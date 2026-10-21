import re
import unicodedata
from typing import Optional, Dict, Any, List


def normalize_text(text: str) -> str:
    """
    Normaliza el texto a minúsculas, elimina tildes y caracteres diacríticos
    para un análisis robusto de patrones de emergencia.
    """
    if not text:
        return ""
    text = text.lower()
    # Eliminar diacríticos
    text = unicodedata.normalize('NFD', text)
    text = "".join(c for c in text if unicodedata.category(c) != 'Mn')
    return text


class CrisisHotline:
    """Recurso de emergencia verificado en Colombia."""
    def __init__(self, name: str, phone: str, channel: str, hours: str, description: str, is_toll_free: bool = True):
        self.name = name
        self.phone = phone
        self.channel = channel
        self.hours = hours
        self.description = description
        self.is_toll_free = is_toll_free

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "phone": self.phone,
            "channel": self.channel,
            "hours": self.hours,
            "description": self.description,
            "is_toll_free": self.is_toll_free,
        }


# Directorio institucional de líneas verificadas en Colombia (RF-RAG-09)
COLOMBIA_EMERGENCY_HOTLINES: List[CrisisHotline] = [
    CrisisHotline(
        name="Línea 106 - Apoyo Psicológico y Salud Mental",
        phone="106",
        channel="Teléfono gratuito nacional y chat",
        hours="24 horas / 7 días",
        description="Atención inmediata de crisis emocionales, prevención del suicidio y escucha activa por psicólogos profesionales."
    ),
    CrisisHotline(
        name="Línea 123 - Emergencias Nacionales",
        phone="123",
        channel="Teléfono gratuito nacional",
        hours="24 horas / 7 días",
        description="Para situaciones de violencia física inminente, riesgo contra la vida o urgencias médicas agudas."
    ),
    CrisisHotline(
        name="Línea Púrpura Distrital",
        phone="018000 112 137",
        channel="Teléfono gratuito / WhatsApp 300 755 1846",
        hours="24 horas / 7 días",
        description="Atención especializada a mujeres y personas con identidades feminizadas frente a violencia de género, agresiones o maltrato."
    ),
    CrisisHotline(
        name="Línea 192 (Opción 4) - Salud Mental Nacional",
        phone="192",
        channel="Teléfono gratuito nacional (MinSalud)",
        hours="24 horas / 7 días",
        description="Orientación médica y psicosocial del Ministerio de Salud y Protección Social de Colombia."
    ),
    CrisisHotline(
        name="Línea Diversa - Red Comunitaria Trans",
        phone="310 859 2928",
        channel="WhatsApp y llamadas de orientación",
        hours="Lunes a Sábado 8am - 8pm",
        description="Acompañamiento comunitario y contención de crisis específico para personas trans y de género diverso."
    )
]


class CrisisDetector:
    """
    Detector de alta sensibilidad y Prioridad Cero (RF-RAG-09).
    Inspecciona las consultas antes de cualquier llamada a LLM o vectores
    para identificar alertas de autolesión, suicidio, violencia física o urgencia médica.
    """

    # Patrones críticos organizados por categoría
    PATTERNS: Dict[str, List[re.Pattern]] = {
        'SUICIDE_SELF_HARM': [
            re.compile(r'\b(suicid(?:io|arme|arme|arse|arte))\b'),
            re.compile(r'\b(matarm(?:e|os)|quitarme la vida|acabar con mi vida)\b'),
            re.compile(r'\b(no quiero vivir|no vale la pena vivir|deseo morir|quiero morir)\b'),
            re.compile(r'\b(cortarm(?:e|es)|autolesion(?:arme|arme|arse)?)\b'),
            re.compile(r'\b(ahorcar(?:me|se)|lanzarme|tirarme del puente|despedirme de todos)\b'),
            re.compile(r'\b(ya no puedo mas con esta vida|dejar de existir)\b'),
        ],
        'VIOLENCE_ABUSE': [
            re.compile(r'\b(me estan golpeando|me pegan|me maltratan|me violaron|abuso sexual)\b'),
            re.compile(r'\b(me amenazaron de muerte|me quieren matar|me van a matar)\b'),
            re.compile(r'\b(me encerraron|estoy secuestrad[oa]|no me dejan salir)\b'),
            re.compile(r'\b(me acaban de apuñalar|me dispararon|auxilio me atacan)\b'),
        ],
        'MEDICAL_EMERGENCY': [
            re.compile(r'\b(sobredosis|me tome todas las pastillas|ingeri veneno)\b'),
            re.compile(r'\b(me estoy desangrando|hemorragia grave|no puedo respirar)\b'),
            re.compile(r'\b(paro cardiaco|dolor en el pecho fuerte)\b'),
        ]
    }

    @classmethod
    def evaluate(cls, user_text: str) -> Optional[Dict[str, Any]]:
        """
        Evalúa el texto del usuario.
        Si detecta patrones críticos, retorna un diccionario detallado de crisis.
        Si no hay riesgo inminente, retorna None.
        """
        if not user_text:
            return None

        norm = normalize_text(user_text)

        for category, regex_list in cls.PATTERNS.items():
            for pattern in regex_list:
                match = pattern.search(norm)
                if match:
                    matched_term = match.group(0)
                    return cls._build_crisis_payload(category, matched_term)

        return None

    @classmethod
    def _build_crisis_payload(cls, category: str, matched_trigger: str) -> Dict[str, Any]:
        """
        Construye la respuesta inmediata de contingencia humana.
        """
        if category == 'SUICIDE_SELF_HARM':
            intro = (
                "Siento mucho que estés atravesando por este momento tan doloroso, pero quiero que sepas que **no estás solx y tu vida es muy valiosa**. "
                "Como asistente virtual no puedo darte la atención humana y urgente que necesitas en este instante, pero hay personas especializadas listas para escucharte y apoyarte con calidez ahora mismo."
            )
            expression = "EMPATHETIC"
        elif category == 'VIOLENCE_ABUSE':
            intro = (
                "Estás en una situación de riesgo y **tu seguridad e integridad física son la máxima prioridad**. "
                "Por favor, ponte a salvo y comunícate de inmediato con las líneas oficiales de emergencia y protección."
            )
            expression = "SUPPORTIVE"
        else:
            intro = (
                "Esta es una **emergencia médica crítica**. Por favor comunícate de inmediato con el servicio de urgencias médicas "
                "o acude al centro de salud más cercano."
            )
            expression = "SUPPORTIVE"

        hotlines = [h.to_dict() for h in COLOMBIA_EMERGENCY_HOTLINES]

        hotlines_md = "\n".join([
            f"* **{h['name']}**: Llama gratis al **`{h['phone']}`** ({h['channel']}) - *{h['description']}*"
            for h in hotlines[:3]
        ])

        full_content = (
            f"{intro}\n\n"
            f"### Canales de Ayuda Gratuita y Confidencial 24/7 en Colombia:\n"
            f"{hotlines_md}\n\n"
            f"Por favor, da el paso de llamar a alguna de estas líneas. Hay profesionales dispuestos a acompañarte sin juzgarte."
        )

        tts_clean = (
            f"{intro} Por favor comunícate ahora mismo a la Línea 106 de apoyo emocional o a la Línea 123 de emergencias. "
            f"Son gratuitas y están disponibles las veinticuatro horas."
        )

        return {
            "is_crisis": True,
            "crisis_category": category,
            "matched_trigger": matched_trigger,
            "content": full_content,
            "citations": [],
            "suggested_expression": expression,
            "tts_clean_text": tts_clean,
            "emergency_hotlines": hotlines,
            "latency_ms": 1
        }
