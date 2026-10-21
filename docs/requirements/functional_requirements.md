# Requerimientos Funcionales - LXIA Backend (`lxia_be`)

> **Proyecto**: Plataforma TransLúcidas (Portal de autocuidado, asistente conversacional con IA y agente virtual encarnado Alexia)  
> **Componente**: Backend Principal y Columna Vertebral (`lxia_be`)  
> **Fuente de extracción**: *Documento preliminar de requerimientos de software (Versión 0.1)*

---

## 1. Alcance del Backend en la Arquitectura Global
El backend `lxia_be` se concibe como el núcleo central e interoperable que da soporte a los tres módulos de la plataforma y canales externos:
1. **Portal Web de Información y Autocuidado**: Entrega y gestión de contenidos.
2. **Asistente Conversacional con IA (RAG)**: Motor de ingesta documental, búsqueda semántica y generación de respuestas.
3. **Agente Conversacional Virtual Encarnado (Alexia)**: Proveedor del servicio conversacional y metadatos de respuesta.
4. **Canales de Mensajería (WhatsApp / Messenger)**: Webhooks y orquestación de mensajes.
5. **Panel Administrativo**: Gestión de contenidos, base de conocimiento y métricas.

---

## 2. Módulo de Autenticación, Usuarios y Control de Acceso (RBAC)

* **RF-AUTH-01: Autenticación Administrativa**: El sistema debe proveer autenticación segura mediante tokens para usuarios autorizados (Administradores de contenidos y Equipo de investigación).
* **RF-AUTH-02: Control de Acceso Basado en Roles (RBAC)**:
  * **Administradores de Contenido**: Permisos para crear, editar, publicar y retirar artículos y recursos del portal.
  * **Equipo de Investigación**: Permisos para gestionar fuentes de conocimiento del RAG, auditar métricas y configurar parámetros de seguridad.
  * **Usuarios Finales (Personas trans y cuidadores)**: Acceso público anónimo a consultas sin forzar registro previo (salvaguardando la privacidad).

---

## 3. Módulo de Gestión y Entrega de Contenidos (Soporte al Portal Web)
*(Derivado de M1-RF-02, M1-RF-03, M1-RF-04, M1-RF-06)*

* **RF-CNT-01: API de Consulta de Contenidos**: Proveer endpoints públicos para que el portal web consulte artículos, guías de autocuidado y recursos informativos organizados por secciones y categorías.
* **RF-CNT-02: Gestión de Recursos Multimedia y Descargables**: Permitir el registro y entrega de metadatos de recursos en diversos formatos (textos enriquecidos, imágenes, enlaces externos y documentos descargables como PDFs).
* **RF-CNT-03: CMS / Gestión Administrativa de Contenidos**: Proveer endpoints protegidos para que los administradores puedan crear, editar, categorizar, publicar y retirar contenidos sin necesidad de alterar el código fuente ni desplegar la aplicación.
* **RF-CNT-04: Respuestas Ligeras y Adaptadas a Conectividad Limitada**: Optimizar las respuestas JSON y la entrega de recursos para minimizar el consumo de datos móviles en conexiones inestables.

---

## 4. Módulo Asistente Conversacional y Motor RAG (Retrieval-Augmented Generation)
*(Derivado de M2-RF-01 a M2-RF-10, Sección 4.2 y Sección 5)*

### A. Gestión de Conocimiento (Knowledge Base)
* **RF-RAG-01: Ingesta y Procesamiento de Documentos**: Procedimiento y endpoints administrativos para cargar documentos (talleres de autocuidado, guías educativas, etc.).
* **RF-RAG-02: Extracción, Fragmentación (Chunking) e Indexación**: El backend debe extraer texto de los documentos, dividirlo en fragmentos semánticos, generar embeddings vectoriales y almacenarlos en la base de datos vectorial para su rápida recuperación.
* **RF-RAG-03: Actualización y Retiro de Fuentes**: Capacidad de actualizar, re-indexar o dar de baja documentos de la base de conocimiento sin reiniciar ni reconstruir la aplicación.

### B. Consulta y Generación
* **RF-RAG-04: Endpoint de Conversación en Lenguaje Natural**: Endpoint que recibe consultas en texto formuladas en español por el usuario y retorna respuestas comprensibles y contextualizadas.
* **RF-RAG-05: Recuperación Documental Contextual (Retrieval)**: Búsqueda y recuperación de los fragmentos más relevantes de la base de conocimiento frente a la consulta del usuario.
* **RF-RAG-06: Generación Fundamentada (Generation)**: Orquestación con el modelo de lenguaje (LLM) condicionando la respuesta estrictamente a los fragmentos recuperados para evitar alucinaciones.
* **RF-RAG-07: Trazabilidad y Referencias**: Capacidad de adjuntar en la respuesta los títulos, citas o enlaces de los documentos que sustentaron la respuesta (cuando aplique).
* **RF-RAG-08: Manejo de Consultas No Resueltas**: Cuando la base de conocimiento no contenga evidencia suficiente, el sistema debe informar explícitamente su limitación en lugar de especular.

### C. Salvaguardas, Ética y Moderación
* **RF-RAG-09: Detección de Situaciones de Crisis / Violencia**: Detección de mensajes relacionados con emergencias de salud, crisis emocionales o violencia, activando respuestas de derivación a líneas o recursos institucionales de apoyo humano.
* **RF-RAG-10: Filtros de Lenguaje Inclusivo y No Discriminatorio**: Mecanismos de prompt engineering y validación para garantizar un estilo respetuoso, sensible a la diversidad de género y libre de sesgos o estigmas.
* **RF-RAG-11: Transparencia de IA**: Notificación en los metadatos de respuesta indicando que la interacción es generada por un sistema de IA y no reemplaza asesoría médica o legal.

---

## 5. Módulo de Servicios para el Agente Encarnado (Alexia)
*(Derivado de M3-RF-02, M3-RF-09, M3-RF-10)*

* **RF-ALX-01: API Conversacional para Alexia**: Endpoint dedicado o compartido que Alexia consume para obtener las respuestas generadas por el motor conversacional.
* **RF-ALX-02: Metadatos para Expresividad y Voz**: Entrega de respuestas estructuradas (texto limpio para síntesis de voz TTS, marcas de énfasis o sugerencias de estado emocional/expresivo para el avatar si el modelo las provee).
* **RF-ALX-03: Alternativa Textual**: Garantizar que todas las respuestas emitidas a Alexia tengan versión puramente textual para usuarios sin capacidad de audio o con bajo ancho de banda.

---

## 6. Módulo de Integración con Canales de Mensajería (WhatsApp / Messenger)
*(Derivado de M2-RF-07, Sección 5.1)*

* **RF-MSG-01: Webhook Receptor de Mensajería**: Endpoints para recibir eventos y mensajes entrantes de las APIs de WhatsApp Business / Meta Messenger.
* **RF-MSG-02: Normalización y Orquestación**: Transformar los mensajes entrantes de mensajería al formato interno del motor conversacional RAG y despachar la respuesta al usuario mediante la API del canal correspondiente.
* **RF-MSG-03: Formato Conciso para Mensajería**: Optimizar las respuestas para que sean concisas y legibles en aplicaciones de chat móvil.

---

## 7. Módulo de Observabilidad, Métricas y Privacidad
*(Derivado de M2-RF-09, RNF-06, RNF-08, Sección 7)*

* **RF-OBS-01: Métricas de Uso Técnico**: Registro de indicadores agregados (tiempos de respuesta, volumen de consultas por período, tasas de éxito/fallo del RAG, tasa de consultas no resueltas).
* **RF-OBS-02: Minimización y Privacidad de Datos**: No asociar las consultas conversacionales con identidades personales reales ni almacenar datos sensibles no indispensables.
* **RF-OBS-03: Políticas de Retención y Purga**: Mecanismos automáticos o manuales para purgar registros de conversaciones y evitar almacenamiento indefinido de interacciones.

---

## 8. Principios de Arquitectura Técnica del Backend
*(Derivado de la Sección 5.2)*
* **API RESTful**: Endpoints estructurados con estándares HTTP, serialización y validación estricta con Django REST Framework.
* **Desacoplamiento de Proveedores**: Abstracción en la capa de servicios para que los modelos de embeddings, LLMs o servicios externos de IA puedan ser sustituidos sin rehacer la lógica central.
* **Manejo Controlado de Errores y Timeouts**: Resiliencia frente a caídas o demoras de APIs externas de IA o servicios de mensajería.
* **Documentación Viva**: Esquema OpenAPI 3.0 generado automáticamente mediante `drf-spectacular` accesible en `/api/docs/`.
