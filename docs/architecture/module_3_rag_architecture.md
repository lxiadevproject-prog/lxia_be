# 🧠 Arquitectura y Plan Detallado – Módulo 3: Motor RAG y Asistente Conversacional

> **Proyecto:** Plataforma TransLúcidas  
> **Componente:** Backend Principal (`lxia_be`)  
> **Módulo:** 3 – Asistente Conversacional, Base de Conocimiento y Motor RAG  
> **Requisitos asociados:** RF-RAG-01 a RF-RAG-11, RF-ALX-01 a RF-ALX-03, RF-OBS-01 a RF-OBS-03  
> **Estrategia de Almacenamiento:** Arquitectura Delegada en la Nube (*Direct Upload* a Firebase Storage)  
> **Extensibilidad:** Preparado para integración Plug-and-Play con **Firebase Cloud Functions**

---

## 1. Visión General y Principio de Servidor Ligero

El **Módulo 3** implementa la inteligencia conversacional central de la plataforma TransLúcidas y el backend del agente virtual encarnado **Alexia**.

### ⚡ Principio de Eficiencia en Render:
Para mantener el servidor en Render lo más liviano posible y reducir al mínimo el consumo de ancho de banda y memoria RAM:
1. **Delegación de Binarios:** Los archivos pesados (PDFs, guías, manuales) se suben **directamente desde el cliente/frontend hacia Firebase Storage**. Render **NO** recibe archivos binarios multipart de 20 MB por HTTP.
2. **Backend 100% JSON:** El backend de Render solo recibe un payload JSON ligero (~300 bytes) con los metadatos del documento y la URL generada por Firebase.
3. **Indexación Efímera en Memoria:** Durante la indexación, el backend lee el archivo desde la red interna de alta velocidad de Google Cloud en un flujo temporal (`io.BytesIO`), extrae el texto, genera los fragmentos (*chunks*), calcula embeddings y descarta los bytes inmediatamente de la RAM.
4. **Preparación Plug-and-Play para Cloud Functions:** Diseñado desde el inicio con un webhook y pipeline desacoplado para que, en el futuro, una Cloud Function en Firebase pueda extraer el texto de forma serverless y entregarlo directamente a Django sin consumir un solo ciclo de CPU en Render.
5. **Consultas RAG de Alta Velocidad:** Las preguntas de los usuarios y de Alexia se responden consultando **únicamente PostgreSQL** (en < 10 ms), sin tocar Firebase Storage durante las conversaciones.

---

## 2. Diagrama de Flujo: Modos Autónomo y Cloud Function

```
[Computadora del Investigador / Frontend]
      │
      │ 1. Sube el archivo binario pesado (PDF de 15 MB) DIRECTAMENTE
      │    utilizando el SDK de Firebase Storage (con barra de progreso nativa)
      ▼
┌────────────────────────────────────────┐
│  Firebase Storage (Google Cloud)       │
│  - Absorbe los 15 MB de ancho de banda │
│  - Genera la URL pública y storage path│
└──────┬──────────────────────────┬──────┘
       │                          │
       │ (Modo Actual Autónomo)   │ (Modo Futuro Serverless: Cloud Function)
       ▼                          ▼
┌────────────────────────┐  ┌────────────────────────────────────────┐
│ Render recibe JSON     │  │ Firebase Cloud Function (onFinalize)   │
│ POST /documents/       │  │ - Extrae texto en los servidores de GCP│
│ y cuando se indexa,    │  │ - Envía texto limpio vía Webhook:      │
│ lee bytes en memoria   │  │   POST /webhook/document-extracted/    │
└──────┬─────────────────┘  └──────────────────┬─────────────────────┘
       │                                       │
       └───────────────────┬───────────────────┘
                           │
                           ▼
┌────────────────────────────────────────┐
│  DocumentIngestionService (Django)     │
│  - Chunking semántico (~500 chars)     │
│  - Generación de Embeddings vectoriales│
└──────────────────┬─────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────┐
│  PostgreSQL (lxia_db)                  │
│  Guarda KnowledgeChunk + Vectores      │
└──────────────────┬─────────────────────┘
                   │
   ┌───────────────┴────────────────┐
   │  Consulta RAG del Usuario      │
   │  (Chat / Alexia)               │
   ▼                                ▼
┌────────────────────────────────────────┐
│ 1. Detector de Emergencias / Crisis    │
│    ¿Ideación suicida o violencia?      ├─(SÍ)─► Emite Tarjeta de Ayuda Inmediata
└──────────────────┬─────────────────────┘        + Líneas de Vida (106, Púrpura)
                   │ (NO)
                   ▼
┌────────────────────────────────────────┐
│ 2. Búsqueda Vectorial en PostgreSQL    │
│    (Similitud Coseno en milisegundos)  │
└──────────────────┬─────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────┐
│ 3. Orquestación Grounded LLM           │
│    - Prompt afirmativo y sin sesgos    │
│    - Citas y trazabilidad de fuentes   │
│    - Metadatos fonéticos para Alexia   │
└────────────────────────────────────────┘
```

---

## 3. Arquitectura de Modelos de Datos (`rag_assistant`)

### A. Base de Conocimiento (Knowledge Base)

1. **`KnowledgeDocument`**:
   * `title`: Título del documento (ej. *"Guía Nacional de Atención Integral a Personas Trans"*).
   * `slug`: Identificador URL amigable único.
   * `description`: Resumen del documento.
   * `document_type`: `GUIDE`, `PROTOCOL`, `LEGAL`, `WORKSHOP`, `FAQ`.
   * `file_url`: URL pública o firmada del archivo alojado en **Firebase Storage**.
   * `storage_path`: Ruta del objeto en el bucket (ej. `knowledge_docs/guia_salud.pdf`).
   * `file_size_bytes`: Tamaño del archivo en bytes (informado por el cliente).
   * `ingestion_source`: Origen de la ingesta:
     * `MANUAL_TEXT` (Texto directo / FAQ)
     * `FIREBASE_DIRECT` (Subido a Firebase y procesado por Django)
     * `CLOUD_FUNCTION_WEBHOOK` (Extraído por Firebase Cloud Function)
   * `file`: Opcional para entornos de desarrollo local sin Firebase configurado.
   * `raw_text`: Texto íntegro extraído tras la indexación.
   * `status`: `PENDING` (pendiente de indexar), `EXTRACTING`, `INDEXED` (activo en RAG), `FAILED`, `ARCHIVED`.
   * `chunks_count`: Número de fragmentos generados.
   * `uploaded_by`: Relación con el usuario investigador que cargó la fuente.
   * `created_at`, `updated_at`.

2. **`KnowledgeChunk`**:
   * `document`: Relación con el documento padre (`CASCADE`).
   * `chunk_index`: Índice de orden en el documento.
   * `content`: Texto del fragmento (tamaño óptimo ~500 caracteres con 100 caracteres de solapamiento/*overlap*).
   * `embedding`: Vector numérico (*array de floats*). Compatible con almacenamiento nativo portable en PostgreSQL.
   * `token_count`: Cantidad de tokens estimados.
   * `metadata`: JSON con número de página, capítulo y referencias para citación.
   * `created_at`.

### B. Conversaciones y Auditoría Anónima (RF-OBS-02)

3. **`ChatSession`**:
   * `session_id`: UUID único auto-generado por el cliente o servidor.
   * `channel`: `PORTAL_WEB`, `ALEXIA_AVATAR`, `WHATSAPP`, `TEST_PANEL`.
   * `is_anonymous`: `True` por defecto para salvaguardar la privacidad de las personas usuarias.
   * `created_at`, `updated_at`.

4. **`ChatMessage`**:
   * `session`: Relación a la sesión activa (`CASCADE`).
   * `role`: `USER`, `ASSISTANT`, `SYSTEM`.
   * `content`: Mensaje en texto.
   * `citations`: JSON con lista de documentos, páginas y extractos que fundamentan la respuesta.
   * `is_crisis_detected`: Bandera de alerta si el motor identificó riesgo inminente.
   * `metadata`: Metadatos de Alexia (expresión facial sugerida, texto limpio para síntesis de voz TTS, latencia en ms).
   * `created_at`.

---

## 4. Servicios y Lógica de Negocio

### A. Pipeline de Ingesta Desacoplado (`DocumentIngestionService`)
Diseñado para admitir tanto la extracción local de Django como la extracción serverless vía Cloud Function:
* **`index_from_file_bytes(document, file_bytes)`**: Lee el archivo en memoria efímera (`pypdf`), extrae el texto por páginas y delega en el indexador de chunks.
* **`index_from_extracted_text(document, raw_text, pages=None)`**: **Método directo que invoca la Cloud Function a través del webhook**. Recibe el texto ya limpio, genera fragmentos semánticos con overlap, calcula los embeddings con el proveedor configurado y persiste en `KnowledgeChunk`.

### B. Capa de Embeddings y LLM Desacoplada (Factory Pattern)
* **`BaseEmbeddingService`**: Interfaz abstracta con implementaciones:
  * `GeminiEmbeddingService` (ej. `text-embedding-004`).
  * `OpenAIEmbeddingService` (ej. `text-embedding-3-small`).
  * `MockEmbeddingService`: Implementación determinista local para que **toda la suite de pruebas unitarias corra sin costo, sin consumir cuotas de red y de forma 100% offline**.
* **`BaseLLMService`**: Interfaz abstracta para orquestar la generación:
  * Genera respuestas en español, empáticas, fundamentadas estrictamente en el contexto recuperado.
  * Si la evidencia es insuficiente, admite la limitación y ofrece alternativas institucionales (**RF-RAG-08**).

### C. Detector de Crisis y Emergencias (RF-RAG-09)
* **Regla de Prioridad Cero**: Antes de invocar al LLM o consultar vectores, el motor analiza patrones de alerta crítica:
  * Ideación suicida o autolesión.
  * Violencia física inmediata o abuso.
  * Emergencia médica aguda.
* **Respuesta de derivación inmediata**: Entrega una tarjeta de recursos humanos verificados (*Línea 106, Línea Púrpura, Línea Diversa, Línea 123*) con `is_crisis: true`.

### D. Metadatos Específicos para el Avatar Alexia (RF-ALX-01 a 03)
* Retorna `tts_clean_text` (sin marcas Markdown ni asteriscos para que la síntesis de voz suene fluida y natural).
* Retorna `suggested_expression`: `EMPATHETIC`, `NEUTRAL`, `INFORMATIVE`, `SUPPORTIVE`.

### E. Transparencia Ética (RF-RAG-11)
* Toda respuesta emitida incluye el aviso legal y ético:
  > *"Alexia es un asistente conversacional basado en inteligencia artificial y no reemplaza el acompañamiento médico, psicológico o legal profesional."*

---

## 5. Matriz de Endpoints

| Método | Endpoint | Formato | Rol / Acceso | Propósito |
| :---: | :--- | :---: | :---: | :--- |
| **POST** | `/api/v1/chat/message/` | JSON | Público / Anónimo | Enviar consulta en lenguaje natural y recibir respuesta RAG con citas |
| **GET** | `/api/v1/chat/history/{session_id}/` | JSON | Público / Sesión | Consultar historial reciente de la sesión activa |
| **POST** | `/api/v1/alexia/interact/` | JSON | Público / Avatar | Endpoint dedicado con metadatos fonéticos y expresivos para Alexia |
| **GET** | `/api/v1/knowledge/documents/` | JSON | `RESEARCHER` / `SUPERADMIN` | Listar fuentes de conocimiento registradas |
| **POST** | `/api/v1/knowledge/documents/` | **JSON** | `RESEARCHER` / `SUPERADMIN` | **Registrar documento con URL de Firebase (0 MB ancho de banda en Render)** |
| **POST** | `/api/v1/knowledge/documents/{id}/index/` | JSON | `RESEARCHER` / `SUPERADMIN` | Disparar proceso de extracción, chunking y vectorización |
| **POST** | `/api/v1/knowledge/test-search/` | JSON | `RESEARCHER` / `SUPERADMIN` | Probar búsqueda vectorial en vivo y auditar puntuaciones de similitud |
| **POST** | `/api/v1/knowledge/webhook/document-extracted/` | **JSON** | **Webhook Secret** | **Receptor seguro para Firebase Cloud Functions futuras** |
| **DELETE** | `/api/v1/knowledge/documents/{id}/` | JSON | `RESEARCHER` / `SUPERADMIN` | Dar de baja un documento y purgar sus vectores |

---

## 6. Fases de Implementación

1. **Fase 1: Estructura y Modelos de Datos**
   * Creación de la app `rag_assistant` y registro en `INSTALLED_APPS`.
   * Modelos `KnowledgeDocument`, `KnowledgeChunk`, `ChatSession` y `ChatMessage` con campos `ingestion_source`, `file_url`, `storage_path` y `raw_text`.
   * Migraciones en PostgreSQL y configuración en Django Admin.
2. **Fase 2: Motor de Ingesta, Chunking y Embeddings (Desacoplados)**
   * `DocumentIngestionService` con métodos `index_from_extracted_text` (para Cloud Function) y `index_from_file_bytes`.
   * Algoritmo de fragmentación semántica con overlap.
   * Servicio de embeddings y búsqueda por similitud de coseno.
   * Factory pattern con soporte para `Mock` (tests), `Gemini` y `OpenAI`.
3. **Fase 3: Detector de Crisis y Prompt Engineering Ético**
   * Motor de reglas y palabras clave de alta sensibilidad para detección de emergencias.
   * Prompt de sistema con perspectiva de diversidad de género y lenguaje afirmativo.
4. **Fase 4: Endpoints de Chat, Alexia, Knowledge Base y Webhook**
   * ViewSets y serializadores JSON para `/api/v1/chat/`, `/api/v1/alexia/`, `/api/v1/knowledge/` y el webhook seguro para Cloud Functions.
5. **Fase 5: Pruebas Unitarias e Integrales**
   * Suite de pruebas cubriendo indexación autónoma, webhook de Cloud Function, búsqueda vectorial, detección de crisis, respuestas RAG y citas.
6. **Fase 6: Integración en Postman y Accesos Directos**
   * Nuevas carpetas en Postman para el Módulo 3.
   * Actualización del índice en `docs/urls.md`.
