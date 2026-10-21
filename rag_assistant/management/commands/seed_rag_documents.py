import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rag_assistant.models import KnowledgeDocument
from rag_assistant.services.ingestion import DocumentIngestionService

logger = logging.getLogger(__name__)
User = get_user_model()

SEED_DOCUMENTS = [
    {
        "title": "Decreto 1227 de 2015 - Trámite Notarial de Corrección del Componente Sexo en Colombia",
        "description": "Normativa oficial para la corrección del componente sexo en el registro civil de nacimiento y cédula de ciudadanía ante notaría en Colombia.",
        "document_type": "LEGAL",
        "ingestion_source": "MANUAL_TEXT",
        "raw_text": (
            "DECRETO 1227 DE 2015 - TRÁMITE NOTARIAL DE CORRECCIÓN DEL COMPONENTE SEXO EN EL REGISTRO CIVIL\n\n"
            "1. OBJETO Y MARCO DE APLICACIÓN\n"
            "El Decreto 1227 del 4 de junio de 2015, expedido por el Ministerio de Justicia y del Derecho de Colombia, "
            "reglamenta el trámite notarial para la corrección del componente sexo en el Registro Civil de Nacimiento y "
            "en la Cédula de Ciudadanía. Este decreto garantiza el derecho fundamental a la identidad de género, la personalidad "
            "jurídica y el libre desarrollo de la personalidad sin necesidad de intermediación judicial ni patologización.\n\n"
            "2. REQUISITOS ANTE CUALQUIER NOTARÍA DEL PAÍS\n"
            "La persona solicitante, mayor de edad, puede acudir ante cualquier notaría del territorio nacional (no es necesario "
            "que sea la notaría donde fue registrada originalmente). Para iniciar el trámite debe presentar únicamente:\n"
            "a) Copia simple del Registro Civil de Nacimiento.\n"
            "b) Copia de la Cédula de Ciudadanía vigente.\n"
            "c) Declaración escrita bajo la gravedad de juramento en la que se exprese la voluntad libre de corregir el componente "
            "sexo para que coincida con su vivencia interna e identidad de género construida.\n\n"
            "3. PROHIBICIÓN EXPRESA DE EXÁMENES MÉDICOS O PSIQUIÁTRICOS\n"
            "El Decreto 1227 de 2015 prohíbe categóricamente exigir dictámenes médicos, pruebas periciales, exámenes psiquiátricos, "
            "certificados de disforia de género o comprobantes de cirugías de reasignación genital o tratamientos hormonales previos. "
            "El trámite es un acto declarativo y voluntario basado exclusivamente en la autodeterminación de la persona.\n\n"
            "4. PLAZO DE EXPEDICIÓN Y ESCRITURA PÚBLICA\n"
            "Una vez radicada la solicitud completa, el notario o notaria tiene un plazo máximo legal de cinco (5) días hábiles para "
            "expedir la correspondiente Escritura Pública de corrección. Con la escritura otorgada, se expide el nuevo registro "
            "civil corregido y la notaría envía la comunicación oficial a la Registraduría Nacional del Estado Civil para la expedición "
            "del duplicado de la cédula de ciudadanía corregida.\n\n"
            "5. TARIFAS Y COSTOS NOTARIALES\n"
            "El otorgamiento de la escritura pública causa únicamente los derechos notariales estándar fijados por la Superintendencia "
            "de Notariado y Registro para los actos sin cuantía. Está terminantemente prohibido cobrar recargos o tarifas extraordinarias "
            "por tratarse de un trámite de identidad de género.\n\n"
            "6. EFECTOS JURÍDICOS Y RECONOCIMIENTO EN EL SISTEMA DE SALUD Y ENTIDADES\n"
            "Una vez corregido el documento, las Entidades Promotoras de Salud (EPS), fondos de pensiones, instituciones educativas, "
            "bancos y entidades públicas y privadas tienen la obligación legal inmediata de actualizar sus registros y bases de datos "
            "con el nombre y componente sexo rectificado, garantizando el respeto al nombre identitario y la dignidad de la persona."
        )
    },
    {
        "title": "Guía de Rutas de Atención en Salud Integral y Terapia de Afirmación de Género",
        "description": "Rutas de acceso a terapia de reemplazo hormonal (TRH), acompañamiento psicosocial y derechos en el Plan de Beneficios en Salud (PBS).",
        "document_type": "GUIDE",
        "ingestion_source": "MANUAL_TEXT",
        "raw_text": (
            "GUÍA DE ACCESO A SALUD INTEGRAL Y TERAPIA DE AFIRMACIÓN DE GÉNERO EN COLOMBIA\n\n"
            "1. DERECHO A LA SALUD INTEGRAL DE PERSONAS TRANS\n"
            "De acuerdo con la jurisprudencia de la Corte Constitucional (Sentencias T-771 de 2013, T-918 de 2012 y T-063 de 2015), "
            "todas las personas transgénero, no binarias y de género diverso tienen derecho a recibir atención integral y afirmativa "
            "en el Sistema General de Seguridad Social en Salud (SGSSS) sin dilaciones injustificadas ni barreras discriminatorias.\n\n"
            "2. ACCESO A TERAPIA DE REEMPLAZO HORMONAL (TRH)\n"
            "La terapia hormonal de afirmación de género (tanto masculinizante como feminizante) forma parte de los procedimientos "
            "y medicamentos cubiertos por el Plan de Beneficios en Salud (PBS / antes POS). Esto significa que la EPS debe suministrar "
            "los medicamentos hormonales prescritos y cubrir los exámenes de control de laboratorio periódicos.\n\n"
            "3. RUTA DE ACCESO PASO A PASO EN LA EPS\n"
            "Paso 1: Solicitar cita con Medicina General en la IPS primaria asignada, manifestando la necesidad de inicio o continuidad de la TRH.\n"
            "Paso 2: Exigir la remisión a la especialidad de Endocrinología y, si se requiere de forma complementaria y no patologizante, a Psicología.\n"
            "Paso 3: Consulta con Endocrinología para valoración clínica, formulación de perfiles hormonales y prescripción médica personalizada.\n"
            "Paso 4: Reclamar los medicamentos hormonales formulados a través del gestor farmacéutico de la EPS.\n"
            "Paso 5: Controles médicos cada 3 a 6 meses con paraclínicos para monitoreo de niveles hormonales, función hepática y metabólica.\n\n"
            "4. ADVERTENCIA CONTRA LA AUTOMEDICACIÓN\n"
            "La automedicación con hormonas o el uso de sustancias modelantes no absorbibles (biopolímeros, aceites industriales) representa "
            "un riesgo severo de trombosis, daño hepático y complicaciones vitales. Siempre debe contarse con acompañamiento médico calificado.\n\n"
            "5. ATENCIÓN DE EMERGENCIAS Y LÍNEAS DE APOYO EMOCIONAL\n"
            "Si estás experimentando ansiedad, depresión o angustia emocional, cuentas con las líneas de escucha psicológica gratuita:\n"
            "- Línea 106 (Escucha activa y orientación psicosocial las 24 horas, gratuita).\n"
            "- Línea 123 (Emergencias médicas y de seguridad a nivel nacional).\n"
            "- Línea Diversa / Línea Púrpura para orientación especializada en derechos humanos y género."
        )
    },
    {
        "title": "Preguntas Frecuentes y Rutas de Orientación Comunitaria TransLúcidas",
        "description": "Preguntas frecuentes sobre la plataforma, orientación de Alexia y redes de apoyo de la Fundación TransLúcidas.",
        "document_type": "FAQ",
        "ingestion_source": "MANUAL_TEXT",
        "raw_text": (
            "PREGUNTAS FRECUENTES Y RUTAS DE ORIENTACIÓN - FUNDACIÓN TRANSLÚCIDAS\n\n"
            "1. ¿QUÉ ES ALEXIA Y CUÁL ES SU PROPÓSITO?\n"
            "Alexia es un asistente conversacional con inteligencia artificial y arquitectura RAG (Generación Aumentada por Recuperación) "
            "diseñado por la Fundación TransLúcidas. Su propósito es brindar orientación clara, afirmativa y respaldada documentalmente "
            "sobre derechos civiles, trámites legales, salud integral y recursos comunitarios para personas trans y no binarias.\n\n"
            "2. ¿ALEXIA REEMPLAZA EL CONSEJO MÉDICO O LEGAL PROFESIONAL?\n"
            "No. Alexia es una herramienta de orientación y pedagogía social. No emite diagnósticos médicos, no prescribe tratamientos "
            "ni asume representación jurídica. Para trámites complejos o decisiones de salud, se debe acudir siempre a los profesionales "
            "e instituciones competentes.\n\n"
            "3. ¿CÓMO PROTEGE ALEXIA MI PRIVACIDAD?\n"
            "El chat público de Alexia no almacena nombres reales ni direcciones IP de los usuarios anónimos. Las sesiones son temporales "
            "y anónimas por defecto. No solicitamos datos bancarios, contraseñas ni información sensible que pueda comprometer tu seguridad.\n\n"
            "4. ¿DÓNDE ENCUENTRO GUÍAS DE AUTOCUIDADO Y COMUNIDAD?\n"
            "En el menú superior de la plataforma TransLúcidas puedes acceder a las secciones de 'Guías de Autocuidado', 'Recursos', "
            "'Chat con Alexia' y el 'Avatar Interactivo', donde encontrarás materiales descargables, directorios de organizaciones aliadas "
            "y espacios de encuentro seguros."
        )
    }
]


class Command(BaseCommand):
    help = "Registra e indexa documentos institucionales iniciales para el motor RAG de Alexia."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Iniciando indexación de documentos institucionales iniciales..."))

        superadmin = User.objects.filter(is_superuser=True).first()
        service = DocumentIngestionService()
        indexed_count = 0

        for doc_data in SEED_DOCUMENTS:
            title = doc_data["title"]
            doc, created = KnowledgeDocument.objects.get_or_create(
                title=title,
                defaults={
                    "description": doc_data["description"],
                    "document_type": doc_data["document_type"],
                    "ingestion_source": doc_data["ingestion_source"],
                    "raw_text": doc_data["raw_text"],
                    "uploaded_by": superadmin
                }
            )

            action_label = "Creado" if created else "Actualizado"
            self.stdout.write(f"- {action_label}: {title}")

            # Indexar texto
            result = service.index_from_extracted_text(doc, doc_data["raw_text"])
            if result.get("success"):
                chunks = result.get("chunks_count", 0)
                indexed_count += 1
                self.stdout.write(self.style.SUCCESS(f"  [OK] Indexado exitosamente con {chunks} fragmentos vectoriales."))
            else:
                self.stdout.write(self.style.ERROR(f"  [ERROR] Fallo al indexar: {result.get('error')}"))

        self.stdout.write(self.style.SUCCESS(f"\nProceso finalizado: {indexed_count} documentos indexados en el motor RAG."))
