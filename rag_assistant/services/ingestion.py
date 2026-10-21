import io
import re
import logging
from typing import List, Dict, Any, Optional, Tuple

import requests
from pypdf import PdfReader
from django.db import transaction

from ..models import KnowledgeDocument, KnowledgeChunk
from .ai_providers import get_embedding_service, BaseEmbeddingService

logger = logging.getLogger(__name__)


class TextSplitter:
    """
    Algoritmo de fragmentación semántica para documentos RAG.
    Divide el texto respetando párrafos y oraciones con solapamiento (overlap)
    para no perder el contexto temático entre fragmentos contiguos.
    """
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str, page: int = 1) -> List[Dict[str, Any]]:
        if not text or not text.strip():
            return []

        # Normalizar espacios
        cleaned = re.sub(r'[ \t]+', ' ', text).strip()
        chunks = []
        start = 0
        text_len = len(cleaned)

        while start < text_len:
            end = start + self.chunk_size
            if end >= text_len:
                chunk_str = cleaned[start:text_len].strip()
                if chunk_str:
                    chunks.append({
                        "content": chunk_str,
                        "metadata": {"page": page, "char_start": start, "char_end": text_len}
                    })
                break

            # Intentar cortar en fin de párrafo o de oración
            cutoff = -1
            candidate = cleaned[start:end]
            
            for delimiter in ['\n\n', '\n', '. ', '; ', ', ', ' ']:
                pos = candidate.rfind(delimiter)
                if pos > self.chunk_size * 0.5:
                    cutoff = pos + len(delimiter)
                    break

            if cutoff == -1:
                cutoff = self.chunk_size

            chunk_str = cleaned[start:start + cutoff].strip()
            if chunk_str:
                chunks.append({
                    "content": chunk_str,
                    "metadata": {"page": page, "char_start": start, "char_end": start + cutoff}
                })

            start += max(1, cutoff - self.chunk_overlap)

        return chunks


class DocumentIngestionService:
    """
    Servicio de extracción, fragmentación e indexación de fuentes documentales.
    Diseñado con arquitectura desacoplada para admitir:
    1. Ingesta local de PDFs en memoria efímera sin saturar el disco.
    2. Subidas a Firebase Storage (0 MB de ancho de banda consumido por el cliente en Render).
    3. Ingesta externa por Webhook de Firebase Cloud Functions.
    """
    def __init__(self, embedding_service: Optional[BaseEmbeddingService] = None):
        self.embedding_service = embedding_service or get_embedding_service()
        self.splitter = TextSplitter(chunk_size=500, chunk_overlap=100)

    @staticmethod
    def extract_text_from_pdf_stream(stream: io.BytesIO) -> List[Tuple[int, str]]:
        """
        Lee el contenido de un archivo PDF directamente en memoria efímera
        usando pypdf sin escribir archivos temporales en disco.
        Retorna lista de tuplas: [(número_página, texto_página), ...]
        """
        reader = PdfReader(stream)
        pages_content = []
        for idx, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages_content.append((idx, page_text.strip()))
        return pages_content

    @transaction.atomic
    def index_from_extracted_text(
        self,
        document: KnowledgeDocument,
        raw_text: str,
        pages_data: Optional[List[Tuple[int, str]]] = None
    ) -> Dict[str, Any]:
        """
        Método directo que procesa texto ya extraído.
        Invocable directamente por el Webhook de Firebase Cloud Functions
        o para textos directos y FAQs.
        """
        document.status = 'EXTRACTING'
        document.error_message = ''
        document.save(update_fields=['status', 'error_message'])

        try:
            # 1. Purgar fragmentos previos si se trata de una re-indexación
            document.chunks.all().delete()

            # 2. Generar fragmentos
            extracted_chunks: List[Dict[str, Any]] = []

            if pages_data and len(pages_data) > 0:
                for page_num, page_text in pages_data:
                    page_chunks = self.splitter.split_text(page_text, page=page_num)
                    extracted_chunks.extend(page_chunks)
            else:
                extracted_chunks = self.splitter.split_text(raw_text, page=1)

            if not extracted_chunks:
                raise ValueError("No se pudo extraer texto procesable del documento.")

            # 3. Vectorizar fragmentos con el proveedor configurado
            texts_to_embed = [c['content'] for c in extracted_chunks]
            embeddings = self.embedding_service.generate_embeddings_batch(texts_to_embed)

            # 4. Guardar fragmentos
            chunk_objects = []
            for idx, (chunk_data, emb) in enumerate(zip(extracted_chunks, embeddings)):
                content = chunk_data['content']
                approx_tokens = max(1, len(content) // 4)
                meta = chunk_data.get('metadata', {})
                meta['document_title'] = document.title
                meta['source'] = document.storage_path or document.file_url or 'Manual'

                chunk_objects.append(KnowledgeChunk(
                    document=document,
                    chunk_index=idx,
                    content=content,
                    embedding=emb,
                    token_count=approx_tokens,
                    metadata=meta
                ))

            KnowledgeChunk.objects.bulk_create(chunk_objects)

            # 5. Actualizar estado del documento
            document.raw_text = raw_text
            document.chunks_count = len(chunk_objects)
            document.status = 'INDEXED'
            document.error_message = ''
            document.save(update_fields=['raw_text', 'chunks_count', 'status', 'error_message', 'ingestion_source', 'updated_at'])

            logger.info(f"Documento '{document.title}' indexado exitosamente con {len(chunk_objects)} fragmentos.")
            return {
                "success": True,
                "document_id": document.id,
                "chunks_count": len(chunk_objects),
                "status": document.status
            }

        except Exception as e:
            logger.error(f"Error indexando texto del documento '{document.title}': {e}", exc_info=True)
            document.status = 'FAILED'
            document.error_message = str(e)
            document.save(update_fields=['status', 'error_message', 'updated_at'])
            return {
                "success": False,
                "document_id": document.id,
                "error": str(e),
                "status": document.status
            }

    def index_from_file_bytes(self, document: KnowledgeDocument, file_bytes: bytes) -> Dict[str, Any]:
        """
        Extrae el texto de un buffer de bytes PDF en memoria y procede a indexar.
        """
        stream = io.BytesIO(file_bytes)
        pages_data = self.extract_text_from_pdf_stream(stream)
        full_text = "\n\n".join([f"--- Página {p} ---\n{t}" for p, t in pages_data])
        return self.index_from_extracted_text(document, full_text, pages_data)

    def index_document(self, document: KnowledgeDocument) -> Dict[str, Any]:
        """
        Orquestador principal de ingesta:
        - Si tiene texto directo o FAQ, procesa el texto.
        - Si tiene file_url (Firebase Storage), descarga en stream a memoria efímera y procesa.
        - Si tiene archivo local subido (desarrollo), lo lee y procesa.
        """
        # Caso 1: Texto manual cargado previamente
        if document.ingestion_source == 'MANUAL_TEXT' and document.raw_text:
            return self.index_from_extracted_text(document, document.raw_text)

        # Caso 2: URL de Firebase Storage
        if document.file_url:
            try:
                document.status = 'EXTRACTING'
                document.save(update_fields=['status'])
                resp = requests.get(document.file_url, stream=True, timeout=30)
                if resp.status_code != 200:
                    raise ValueError(f"No fue posible descargar el archivo de Firebase (HTTP {resp.status_code})")
                return self.index_from_file_bytes(document, resp.content)
            except Exception as e:
                document.status = 'FAILED'
                document.error_message = f"Error al descargar desde Firebase: {str(e)}"
                document.save(update_fields=['status', 'error_message'])
                return {"success": False, "error": str(e), "document_id": document.id}

        # Caso 3: Archivo local (desarrollo / panel admin)
        if document.file:
            try:
                document.status = 'EXTRACTING'
                document.save(update_fields=['status'])
                with document.file.open('rb') as f:
                    file_bytes = f.read()
                return self.index_from_file_bytes(document, file_bytes)
            except Exception as e:
                document.status = 'FAILED'
                document.error_message = f"Error al leer archivo local: {str(e)}"
                document.save(update_fields=['status', 'error_message'])
                return {"success": False, "error": str(e), "document_id": document.id}

        # Caso 4: Si no hay archivo ni URL pero hay raw_text
        if document.raw_text:
            return self.index_from_extracted_text(document, document.raw_text)

        document.status = 'FAILED'
        document.error_message = "El documento no cuenta con archivo, URL ni texto para procesar."
        document.save(update_fields=['status', 'error_message'])
        return {"success": False, "error": document.error_message, "document_id": document.id}
