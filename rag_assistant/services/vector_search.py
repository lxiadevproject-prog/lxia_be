import math
from typing import List, Tuple, Optional
from ..models import KnowledgeChunk
from .ai_providers import get_embedding_service, BaseEmbeddingService


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Calcula la similitud de coseno entre dos vectores numéricos:
    sim(A, B) = (A · B) / (||A|| * ||B||)
    Retorna un valor entre -1.0 y 1.0 (o 0.0 si las dimensiones no coinciden).
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return max(-1.0, min(1.0, dot / (norm_a * norm_b)))


def search_similar_chunks(
    query_text: str,
    top_k: int = 4,
    threshold: float = 0.15,
    document_ids: Optional[List[int]] = None,
    embedding_service: Optional[BaseEmbeddingService] = None
) -> List[Tuple[KnowledgeChunk, float]]:
    """
    Busca los fragmentos más relevantes para una consulta en lenguaje natural
    dentro de los documentos con estado 'INDEXED'.
    
    Retorna una lista ordenada de tuplas (KnowledgeChunk, score).
    """
    if not query_text or not query_text.strip():
        return []

    service = embedding_service or get_embedding_service()
    query_vector = service.generate_embedding(query_text.strip())

    chunks_qs = KnowledgeChunk.objects.filter(
        document__status='INDEXED'
    ).select_related('document')

    if document_ids:
        chunks_qs = chunks_qs.filter(document_id__in=document_ids)

    scored_chunks = []
    for chunk in chunks_qs:
        if not chunk.embedding:
            continue
        score = cosine_similarity(query_vector, chunk.embedding)
        if score >= threshold:
            scored_chunks.append((chunk, score))

    # Ordenar por mayor similitud
    scored_chunks.sort(key=lambda x: x[1], reverse=True)

    return scored_chunks[:top_k]
