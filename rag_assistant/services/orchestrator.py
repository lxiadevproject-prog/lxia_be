import time
import logging
from typing import Optional, Dict, Any, List

from ..models import ChatSession, ChatMessage
from .crisis_detector import CrisisDetector
from .vector_search import search_similar_chunks
from .ai_providers import get_llm_service, BaseLLMService

logger = logging.getLogger(__name__)


class RAGOrchestrator:
    """
    Orquestador principal del ciclo conversacional y motor RAG de Alexia.
    Ejecuta el flujo secuencial:
    1. Regla de Prioridad Cero: Detección de crisis (autolesión, suicidio, violencia física).
    2. Recuperación Vectorial (Retrieval): Búsqueda de fragmentos documentales activos.
    3. Generación Aumentada (Augmented Generation): LLM con prompt afirmativo y citas.
    4. Persistencia y Auditoría: Registro de sesión, métricas de Alexia y citas.
    """

    def __init__(self, llm_service: Optional[BaseLLMService] = None):
        self.llm_service = llm_service or get_llm_service()

    def process_query(
        self,
        user_query: str,
        session: Optional[ChatSession] = None,
        top_k: int = 4
    ) -> Dict[str, Any]:
        """
        Procesa una consulta de usuario dentro de una sesión activa.
        Retorna el diccionario estructurado de respuesta para la API.
        """
        start_time = time.time()
        query_text = (user_query or '').strip()

        # ====================================================================
        # PASO 1: PRIORIDAD CERO - DETECCIÓN DE CRISIS (RF-RAG-09)
        # ====================================================================
        crisis_result = CrisisDetector.evaluate(query_text)
        if crisis_result:
            logger.warning(
                f"Alerta de crisis detectada [{crisis_result['crisis_category']}]: "
                f"activador '{crisis_result['matched_trigger']}'"
            )

            if session:
                # Registrar mensaje del usuario
                ChatMessage.objects.create(
                    session=session,
                    role='USER',
                    content=query_text
                )
                # Registrar respuesta de emergencia inmediata
                ChatMessage.objects.create(
                    session=session,
                    role='ASSISTANT',
                    content=crisis_result['content'],
                    citations=[],
                    is_crisis_detected=True,
                    metadata={
                        'suggested_expression': crisis_result['suggested_expression'],
                        'tts_clean_text': crisis_result['tts_clean_text'],
                        'crisis_category': crisis_result['crisis_category'],
                        'matched_trigger': crisis_result['matched_trigger'],
                        'emergency_hotlines': crisis_result['emergency_hotlines'],
                        'latency_ms': int((time.time() - start_time) * 1000)
                    }
                )
                session.save(update_fields=['updated_at'])

            return crisis_result

        # ====================================================================
        # PASO 2: RECUPERACIÓN VECTORIAL (RETRIEVAL)
        # ====================================================================
        similar_matches = search_similar_chunks(query_text, top_k=top_k)
        context_chunks = [chunk for chunk, _ in similar_matches]

        # ====================================================================
        # PASO 3: ORQUESTACIÓN CON LLM Y GENERACIÓN
        # ====================================================================
        chat_history: List[Dict[str, str]] = []
        if session:
            # Obtener los últimos 4 mensajes previos para contexto de conversación
            recent_msgs = session.messages.order_by('-created_at')[:4]
            chat_history = [
                {'role': m.role.lower(), 'content': m.content}
                for m in reversed(recent_msgs)
            ]

        llm_output = self.llm_service.generate_response(
            user_query=query_text,
            context_chunks=context_chunks,
            chat_history=chat_history
        )

        total_latency = int((time.time() - start_time) * 1000)

        # ====================================================================
        # PASO 4: PERSISTENCIA Y REGISTRO EN BASE DE DATOS
        # ====================================================================
        if session:
            # Guardar mensaje del usuario
            ChatMessage.objects.create(
                session=session,
                role='USER',
                content=query_text
            )
            # Guardar respuesta del asistente
            ChatMessage.objects.create(
                session=session,
                role='ASSISTANT',
                content=llm_output['content'],
                citations=llm_output['citations'],
                is_crisis_detected=False,
                metadata={
                    'suggested_expression': llm_output.get('suggested_expression', 'INFORMATIVE'),
                    'tts_clean_text': llm_output.get('tts_clean_text', ''),
                    'latency_ms': total_latency,
                    'chunks_retrieved': len(context_chunks)
                }
            )
            session.save(update_fields=['updated_at'])

        return {
            "is_crisis": False,
            "content": llm_output['content'],
            "citations": llm_output['citations'],
            "suggested_expression": llm_output.get('suggested_expression', 'INFORMATIVE'),
            "tts_clean_text": llm_output.get('tts_clean_text', ''),
            "latency_ms": total_latency
        }
