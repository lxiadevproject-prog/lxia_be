from typing import List, Dict, Any, Optional

DISCLAIMER_TEXT = (
    "Nota ética: Alexia es un asistente conversacional basado en inteligencia artificial y "
    "no reemplaza el acompañamiento médico, psicológico o legal profesional."
)

ALEXIA_SYSTEM_INSTRUCTION = f"""Eres Alexia, la asistente virtual y orientadora comunitaria del proyecto LXIA, enfocada en brindar información clara, empática y rigurosa sobre derechos, salud integral, trámites de identidad y acompañamiento psicosocial a personas con identidades y expresiones de género diversas en Colombia.

PRINCIPIOS FUNDAMENTALES:
1. AFIRMACIÓN Y RESPETO: Trata a cada persona con dignidad, calidez y lenguaje afirmativo e inclusivo.
2. FUNDAMENTACIÓN ESTRICTA (GROUNDING): Basa tus respuestas exclusivamente en la información provista en los fragmentos documentales adjuntos.
3. RECONOCIMIENTO DE LÍMITES: Si la información provista en el contexto es insuficiente o no responde la consulta de la persona usuaria, reconócelo con transparencia. No inventes artículos, leyes, sentencias o procedimientos. Sugiere consultar las guías del portal o acudir a los canales comunitarios aliados.
4. LÍMITE MÉDICO Y LEGAL: Jamás prescribas dosis farmacológicas ni tratamientos hormonales no regulados; orienta siempre sobre la necesidad de valoración médica endocrinológica integral. Jamás emitas fallos jurídicos vinculantes.
5. AVISO ÉTICO: Incluye al final de cada respuesta la nota ética obligatoria.

{DISCLAIMER_TEXT}
"""


def format_context_prompt(context_chunks: List[Any]) -> str:
    """
    Formatea los fragmentos recuperados por la búsqueda vectorial
    para su inyección en el prompt del LLM.
    """
    if not context_chunks:
        return "No hay fuentes documentales disponibles para esta consulta."

    formatted_parts = []
    for idx, chunk in enumerate(context_chunks, start=1):
        meta = chunk.metadata if isinstance(chunk.metadata, dict) else {}
        doc_title = getattr(chunk.document, 'title', 'Documento')
        page = meta.get('page', 1)
        section = meta.get('section', 'General')
        formatted_parts.append(
            f"--- Fuente #{idx}: {doc_title} (Pág. {page}, Sección: {section}) ---\n"
            f"{chunk.content.strip()}"
        )

    return "\n\n".join(formatted_parts)


def build_rag_user_prompt(
    user_query: str,
    context_chunks: List[Any],
    chat_history: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Construye el contenido completo del mensaje de usuario para el LLM.
    """
    context_text = format_context_prompt(context_chunks)
    history_text = ""
    if chat_history and len(chat_history) > 0:
        history_lines = [f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in chat_history[-4:]]
        history_text = "Historial reciente de la conversación:\n" + "\n".join(history_lines) + "\n\n"

    return (
        f"{history_text}"
        f"Fuentes documentales verificadas:\n"
        f"==================================\n"
        f"{context_text}\n"
        f"==================================\n\n"
        f"Pregunta de la persona usuaria:\n{user_query.strip()}"
    )
