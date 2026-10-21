import re
import time
import unicodedata
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

DISCLAIMER_TEXT = (
    "Nota ética: Alexia es un asistente conversacional basado en inteligencia artificial y "
    "no reemplaza el acompañamiento médico, psicológico o legal profesional."
)

# Vocabulario de cortesía y saludos cotidianos
GREETING_TOKENS = {
    'hola', 'buenas', 'buen', 'buenos', 'dia', 'dias', 'tarde', 'tardes',
    'noche', 'noches', 'alexia', 'saludos', 'saludo', 'hey', 'hi', 'hello',
    'que', 'tal', 'como', 'estas', 'te', 'va', 'encuentras', 'quien', 'eres',
    'tu', 'haces', 'puedes', 'hacer', 'presentate', 'ayudar', 'asistente',
    'amiga', 'por', 'favor', 'bienvenida', 'bienvenido', 'gracias'
}

# Palabras clave temáticas sustantivas (si contiene alguna, NO es un simple saludo, es una consulta RAG)
SUBSTANTIVE_KEYWORDS = {
    'requisito', 'requisitos', 'notaria', 'notarias', 'notarial', 'tramite', 'tramites',
    'sexo', 'genero', 'cedula', 'hormona', 'hormonas', 'hormonal', 'salud', 'denuncia',
    'denunciar', 'derecho', 'derechos', 'ley', 'decreto', '1227', 'registro', 'civil',
    'costo', 'costos', 'precio', 'eps', 'tutela', 'violencia', 'discriminacion',
    'psicologo', 'psicologia', 'medico', 'medica', 'cirugia', 'cirugias', 'nombre',
    'cambio', 'documento', 'documentos', 'cita', 'formulario'
}

WELCOME_MESSAGE = (
    "¡Hola! Te doy una cálida bienvenida a **TransLúcidas**. Soy **Alexia**, tu asistente "
    "virtual de orientación comunitaria y derechos.\n\n"
    "Estoy aquí para brindarte información verificada y acompañamiento en:\n"
    "- **Derechos y trámites de identidad de género** (como la corrección del componente sexo ante notaría bajo el Decreto 1227 de 2015).\n"
    "- **Rutas de acceso a salud integral** (terapia de afirmación hormonal, acompañamiento psicosocial y cobertura en EPS).\n"
    "- **Guías de autocuidado, redes de apoyo y recursos comunitarios**.\n\n"
    "¿En qué tema te gustaría profundizar hoy o qué pregunta deseas consultar?"
)

TTS_CLEAN_WELCOME = (
    "Hola, te doy una cálida bienvenida a TransLúcidas. Soy Alexia, tu asistente virtual de "
    "orientación comunitaria. Estoy aquí para acompañarte con información sobre derechos, "
    "salud integral y recursos de autocuidado. ¿En qué te puedo orientar hoy?"
)


class GreetingDetector:
    """
    Detector de saludos de cortesía y preguntas introductorias (Small-talk).
    Permite a Alexia responder de forma humana, empática e institucional
    sin activar una búsqueda vectorial documental fallida cuando el usuario
    solo inicia la conversación con 'Hola', 'Buenos días' o '¿Quién eres?'.
    """

    @staticmethod
    def normalize_text(text: str) -> str:
        """Convierte a minúsculas, elimina tildes y caracteres no alfanuméricos."""
        text = text.lower()
        nfkd = unicodedata.normalize('NFKD', text)
        no_accents = ''.join([c for c in nfkd if not unicodedata.combining(c)])
        cleaned = re.sub(r'[^a-z0-9\s]', ' ', no_accents)
        return re.sub(r'\s+', ' ', cleaned).strip()

    @classmethod
    def is_greeting(cls, query_text: str) -> bool:
        """
        Determina si el mensaje del usuario es exclusivamente un saludo o cortesía.
        Si incluye preguntas o temas sustantivos (ej. 'Hola, ¿cómo cambio mi cédula?'),
        retorna False para que sea procesado por el motor RAG.
        """
        if not query_text or not query_text.strip():
            return False

        normalized = cls.normalize_text(query_text)
        tokens = normalized.split()

        if not tokens:
            return False

        # Si supera 15 palabras, es probable que contenga una narración o consulta específica
        if len(tokens) > 15:
            return False

        # Si contiene palabras sustantivas clave, no es solo cortesía
        for token in tokens:
            if token in SUBSTANTIVE_KEYWORDS:
                return False

        # Verificar si todos o casi todos los tokens pertenecen al vocabulario de saludo
        matched_tokens = [t for t in tokens if t in GREETING_TOKENS]
        # Permitir conectores comunes (a, de, en, me, etc.)
        allowed_fillers = {'a', 'el', 'la', 'los', 'las', 'un', 'una', 'en', 'para', 'de', 'me', 'y', 'o', 'mi'}
        
        valid_count = sum(1 for t in tokens if t in GREETING_TOKENS or t in allowed_fillers)
        return (valid_count / len(tokens)) >= 0.75

    @classmethod
    def evaluate(cls, query_text: str) -> Optional[Dict[str, Any]]:
        """
        Si la consulta es un saludo, retorna el diccionario de respuesta formateado.
        Si no, retorna None.
        """
        if not cls.is_greeting(query_text):
            return None

        content = f"{WELCOME_MESSAGE}\n\n---\n*{DISCLAIMER_TEXT}*"

        return {
            "is_crisis": False,
            "is_greeting": True,
            "content": content,
            "citations": [],
            "suggested_expression": "EMPATHETIC",
            "tts_clean_text": TTS_CLEAN_WELCOME,
        }
