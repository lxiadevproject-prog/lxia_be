import re
import math
import time
import hashlib
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

DISCLAIMER_TEXT = (
    "Nota ética: Alexia es un asistente conversacional basado en inteligencia artificial y "
    "no reemplaza el acompañamiento médico, psicológico o legal profesional."
)


# ============================================================================
# INTERFACES Y FACTORY DE EMBEDDINGS
# ============================================================================

class BaseEmbeddingService(ABC):
    """
    Contrato abstracto para proveedores de embeddings vectoriales.
    """
    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """Genera un vector numérico (lista de flotantes) para un texto."""
        pass

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings para múltiples textos en lote."""
        return [self.generate_embedding(t) for t in texts]


SPANISH_STOP_WORDS = {
    'de', 'la', 'el', 'en', 'y', 'a', 'los', 'del', 'las', 'un', 'una', 'unos', 'unas',
    'por', 'para', 'con', 'no', 'si', 'su', 'sus', 'al', 'lo', 'como', 'mas', 'pero', 'que', 'se', 'es'
}


class MockEmbeddingService(BaseEmbeddingService):
    """
    Generador determinista de embeddings locales (dimensión 128).
    Calcula un vector unitario L2 basado en términos significativos sin stop-words.
    Garantiza que el 100% de pruebas unitarias y entornos offline corran sin costo
    y con similitudes semánticas consistentes y reproducibles.
    """
    DIMENSION = 128

    def generate_embedding(self, text: str) -> List[float]:
        if not text:
            vector = [0.0] * self.DIMENSION
            vector[0] = 1.0
            return vector

        vector = [0.0] * self.DIMENSION
        # Normalizar tildes y caracteres especiales
        normalized = text.lower()
        replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n'}
        for orig, rep in replacements.items():
            normalized = normalized.replace(orig, rep)

        cleaned = re.sub(r'[^\w\s]', ' ', normalized)
        tokens = [t for t in cleaned.split() if t not in SPANISH_STOP_WORDS and len(t) > 2]

        if not tokens:
            vector[0] = 1.0
            return vector

        # Acumular pesos por términos y sub-cadenas
        for i, token in enumerate(tokens):
            h1 = int(hashlib.sha256(token.encode('utf-8')).hexdigest(), 16) % self.DIMENSION
            vector[h1] += 2.0
            # Character n-grams (sub-words)
            for j in range(len(token) - 2):
                tri = token[j:j + 3]
                h_tri = int(hashlib.md5(tri.encode('utf-8')).hexdigest(), 16) % self.DIMENSION
                vector[h_tri] += 0.5

            if i + 1 < len(tokens):
                bigram = f"{token}_{tokens[i + 1]}"
                h2 = int(hashlib.sha256(bigram.encode('utf-8')).hexdigest(), 16) % self.DIMENSION
                vector[h2] += 2.5

        # Normalización L2 (norma unitaria)
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            return [round(v / norm, 6) for v in vector]

        vector[0] = 1.0
        return vector


class GeminiEmbeddingService(BaseEmbeddingService):
    """
    Proveedor de embeddings usando Google Gemini API (text-embedding-004).
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'GEMINI_API_KEY', '')
        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent"

    def generate_embedding(self, text: str) -> List[float]:
        if not self.api_key:
            logger.warning("GEMINI_API_KEY no configurada. Fallback a MockEmbeddingService.")
            return MockEmbeddingService().generate_embedding(text)

        url = f"{self.endpoint}?key={self.api_key}"
        payload = {
            "model": "models/text-embedding-004",
            "content": {
                "parts": [{"text": text[:2000]}]
            }
        }
        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                values = data.get('embedding', {}).get('values', [])
                # Normalizar vector
                norm = math.sqrt(sum(v * v for v in values))
                return [v / norm for v in values] if norm > 0 else values
            else:
                logger.error(f"Error en Gemini Embedding: {resp.status_code} {resp.text}")
                return MockEmbeddingService().generate_embedding(text)
        except Exception as e:
            logger.error(f"Excepción en Gemini Embedding: {e}")
            return MockEmbeddingService().generate_embedding(text)


class OpenAIEmbeddingService(BaseEmbeddingService):
    """
    Proveedor de embeddings usando OpenAI API (text-embedding-3-small).
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'OPENAI_API_KEY', '')
        self.endpoint = "https://api.openai.com/v1/embeddings"

    def generate_embedding(self, text: str) -> List[float]:
        if not self.api_key:
            logger.warning("OPENAI_API_KEY no configurada. Fallback a MockEmbeddingService.")
            return MockEmbeddingService().generate_embedding(text)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "text-embedding-3-small",
            "input": text[:4000]
        }
        try:
            resp = requests.post(self.endpoint, headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data['data'][0]['embedding']
            else:
                logger.error(f"Error en OpenAI Embedding: {resp.status_code} {resp.text}")
                return MockEmbeddingService().generate_embedding(text)
        except Exception as e:
            logger.error(f"Excepción en OpenAI Embedding: {e}")
            return MockEmbeddingService().generate_embedding(text)


def get_embedding_service(provider: Optional[str] = None) -> BaseEmbeddingService:
    """
    Factory para instanciar el servicio de embeddings según configuración.
    """
    choice = (provider or getattr(settings, 'RAG_EMBEDDING_PROVIDER', 'mock')).lower()
    if choice == 'gemini':
        return GeminiEmbeddingService()
    elif choice == 'openai':
        return OpenAIEmbeddingService()
    return MockEmbeddingService()


# ============================================================================
# INTERFACES Y FACTORY DE MODELO DE LENGUAJE (LLM)
# ============================================================================

class BaseLLMService(ABC):
    """
    Contrato abstracto para proveedores de LLM generativo (RAG Orquestador).
    """
    @abstractmethod
    def generate_response(
        self,
        user_query: str,
        context_chunks: List[Any],
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Genera una respuesta afirmativa, sin sesgos y fundamentada en fragmentos.
        Retorna diccionario con content, citations, suggested_expression, tts_clean_text, latency_ms.
        """
        pass

    @staticmethod
    def clean_text_for_tts(markdown_text: str) -> str:
        """
        Limpia marcas de formato Markdown, enlaces, viñetas y asteriscos
        para que los motores de síntesis de voz (TTS) del Avatar Alexia
        pronuncien un lenguaje natural y fluido (RF-ALX-02).
        """
        text = re.sub(r'#+\s*', '', markdown_text)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'[\r\n]+', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text


class MockLLMService(BaseLLMService):
    """
    Servicio simulado determinista para pruebas unitarias y entornos sin conexión.
    Sintetiza los fragmentos recuperados en una respuesta estructurada con citas reales.
    """
    def generate_response(
        self,
        user_query: str,
        context_chunks: List[Any],
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        start_time = time.time()

        citations = []
        for chunk in context_chunks:
            meta = chunk.metadata if isinstance(chunk.metadata, dict) else {}
            citations.append({
                "document_id": chunk.document.id,
                "document_title": chunk.document.title,
                "chunk_id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "page": meta.get('page', 1),
                "section": meta.get('section', 'General'),
                "snippet": chunk.content[:150] + "..." if len(chunk.content) > 150 else chunk.content
            })

        if not context_chunks:
            content = (
                "Actualmente no dispongo de información documental verificada en la base de conocimiento "
                "sobre este tema específico. Te sugiero consultar las guías de atención institucionales o "
                "contactar directamente con las redes de apoyo comunitario del portal."
            )
            expression = "INFORMATIVE"
        else:
            doc_titles = list({c['document_title'] for c in citations})
            extracted_points = [f"- {c['snippet']}" for c in citations[:3]]
            summary_points = "\n".join(extracted_points)

            content = (
                f"Con base en la información institucional verificada ({', '.join(doc_titles)}):\n\n"
                f"{summary_points}\n\n"
                f"Si necesitas ampliar algún detalle de esta guía o trámite, con gusto te oriento paso a paso."
            )
            expression = "EMPATHETIC"

        content += f"\n\n---\n*{DISCLAIMER_TEXT}*"

        latency = int((time.time() - start_time) * 1000)
        tts_clean = self.clean_text_for_tts(content)

        return {
            "content": content,
            "citations": citations,
            "suggested_expression": expression,
            "tts_clean_text": tts_clean,
            "latency_ms": latency
        }


class GeminiLLMService(BaseLLMService):
    """
    Proveedor de generación conversacional usando Google Gemini 1.5 Flash.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'GEMINI_API_KEY', '')
        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    def generate_response(
        self,
        user_query: str,
        context_chunks: List[Any],
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            logger.warning("GEMINI_API_KEY no configurada. Fallback a MockLLMService.")
            return MockLLMService().generate_response(user_query, context_chunks, chat_history)

        start_time = time.time()
        citations = []
        context_texts = []
        for chunk in context_chunks:
            meta = chunk.metadata if isinstance(chunk.metadata, dict) else {}
            citations.append({
                "document_id": chunk.document.id,
                "document_title": chunk.document.title,
                "chunk_id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "page": meta.get('page', 1),
                "section": meta.get('section', 'General'),
                "snippet": chunk.content[:150]
            })
            context_texts.append(f"[{chunk.document.title} - Pág {meta.get('page', 1)}]: {chunk.content}")

        context_prompt = "\n\n".join(context_texts)
        system_instruction = (
            "Eres Alexia, una asistente virtual empática, afirmativa y respetuosa de la diversidad de género y derechos humanos. "
            "Responde de forma clara en español. Basa tus respuestas estrictamente en el siguiente contexto documental verificador. "
            "Si el contexto no contiene la respuesta, indícalo con amabilidad sin inventar datos. "
            f"Al final añade siempre: '{DISCLAIMER_TEXT}'"
        )

        user_content = f"Contexto disponible:\n{context_prompt}\n\nPregunta de la persona usuaria:\n{user_query}"

        url = f"{self.endpoint}?key={self.api_key}"
        payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": [{"parts": [{"text": user_content}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 800}
        }

        try:
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                content = data['candidates'][0]['content']['parts'][0]['text']
            else:
                logger.error(f"Error Gemini LLM: {resp.status_code} {resp.text}")
                return MockLLMService().generate_response(user_query, context_chunks, chat_history)
        except Exception as e:
            logger.error(f"Excepción Gemini LLM: {e}")
            return MockLLMService().generate_response(user_query, context_chunks, chat_history)

        latency = int((time.time() - start_time) * 1000)
        return {
            "content": content,
            "citations": citations,
            "suggested_expression": "SUPPORTIVE",
            "tts_clean_text": self.clean_text_for_tts(content),
            "latency_ms": latency
        }


class OpenAILLMService(BaseLLMService):
    """
    Proveedor de generación conversacional usando OpenAI GPT-4o-mini.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'OPENAI_API_KEY', '')
        self.endpoint = "https://api.openai.com/v1/chat/completions"

    def generate_response(
        self,
        user_query: str,
        context_chunks: List[Any],
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            logger.warning("OPENAI_API_KEY no configurada. Fallback a MockLLMService.")
            return MockLLMService().generate_response(user_query, context_chunks, chat_history)

        start_time = time.time()
        citations = []
        context_texts = []
        for chunk in context_chunks:
            meta = chunk.metadata if isinstance(chunk.metadata, dict) else {}
            citations.append({
                "document_id": chunk.document.id,
                "document_title": chunk.document.title,
                "chunk_id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "page": meta.get('page', 1),
                "section": meta.get('section', 'General'),
                "snippet": chunk.content[:150]
            })
            context_texts.append(f"[{chunk.document.title}]: {chunk.content}")

        context_prompt = "\n\n".join(context_texts)
        system_instruction = (
            "Eres Alexia, una asistente virtual empática, respetuosa e informada sobre diversidad y derechos LGBTIQ+. "
            "Responde en español basándote estrictamente en el contexto adjunto. "
            f"Incluye al final: '{DISCLAIMER_TEXT}'"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Contexto:\n{context_prompt}\n\nPregunta:\n{user_query}"}
        ]

        payload = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "temperature": 0.2
        }

        try:
            resp = requests.post(self.endpoint, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                content = data['choices'][0]['message']['content']
            else:
                logger.error(f"Error OpenAI LLM: {resp.status_code} {resp.text}")
                return MockLLMService().generate_response(user_query, context_chunks, chat_history)
        except Exception as e:
            logger.error(f"Excepción OpenAI LLM: {e}")
            return MockLLMService().generate_response(user_query, context_chunks, chat_history)

        latency = int((time.time() - start_time) * 1000)
        return {
            "content": content,
            "citations": citations,
            "suggested_expression": "SUPPORTIVE",
            "tts_clean_text": self.clean_text_for_tts(content),
            "latency_ms": latency
        }


def get_llm_service(provider: Optional[str] = None) -> BaseLLMService:
    """
    Factory para instanciar el servicio LLM configurado.
    """
    choice = (provider or getattr(settings, 'RAG_LLM_PROVIDER', 'mock')).lower()
    if choice == 'gemini':
        return GeminiLLMService()
    elif choice == 'openai':
        return OpenAILLMService()
    return MockLLMService()
