# 📑 PROPUESTA TÉCNICA Y ECONÓMICA INTEGRAL
## Plataforma TransLúcidas: Portal de Autocuidado, Asistente Conversacional RAG y Agente Virtual Encarnado 3D (Alexia)

---

* **Destinatario:** Fundación TransLúcidas — Equipo de Investigación y Dirección de Proyecto  
  *(Atención: David Herrera y Comité Técnico)*
* **Modalidad de Contratación:** Llave en Mano / Solución Integral Unificada (Módulos 1, 2 y 3)
* **Fecha de Emisión:** 23 de Octubre de 2026
* **Vigencia de la Oferta:** 30 días calendario
* **Inversión Total Consolidada:** **$15.000.000 COP** *(Referencia: $3.750 USD)*
* **Estado de Madurez y Prototipo en Vivo:**  
  • **Frontend Web & Avatar:** [https://lxia-fe.netlify.app](https://lxia-fe.netlify.app)  
  • **Backend API & Swagger:** [https://lxia-be.onrender.com/api/docs/](https://lxia-be.onrender.com/api/docs/)  
  • **Base de Datos Vectorial:** PostgreSQL 17 + `pgvector` en Supabase (Documentos oficiales indexados y operativos)

---

## 1. Resumen Ejecutivo y Enfoque de la Solución Integral

La presente propuesta técnica y económica detalla la implementación integral de la **Plataforma TransLúcidas**, dando cumplimiento a los requerimientos funcionales y no funcionales del **Documento Preliminar de Software v0.1** y a las directrices de investigación comunitaria orientadas a la **representación digna, calidez humana, empatía y sensibilidad cultural**.

La solución se concibe como un **ecosistema multimodal cohesionado de tres módulos**, diseñado para brindar acompañamiento continuo, pedagógico y afirmativo a personas trans y no binarias en Colombia:

![Diagrama de Arquitectura Multimodal Integral Plataforma TransLúcidas](arquitectura_transluz.png)

```mermaid
flowchart TD
    %% Estilos Profesionales
    classDef userClass fill:#F3F4F6,stroke:#4B5563,stroke-width:2px,color:#111827;
    classDef m1Class fill:#EFF6FF,stroke:#3B82F6,stroke-width:2px,color:#1E3A8A;
    classDef m3Class fill:#FDF2F8,stroke:#EC4899,stroke-width:2px,color:#831843;
    classDef m2Class fill:#FFFBEB,stroke:#F59E0B,stroke-width:2px,color:#78350F;
    classDef ethicsClass fill:#FEF2F2,stroke:#EF4444,stroke-width:2px,color:#991B1B;
    classDef dataClass fill:#ECFDF5,stroke:#10B981,stroke-width:2px,color:#065F46;

    subgraph SEC_USER ["1. USUARIAS Y CANALES MÓVILES (Android / iOS / Web)"]
        direction LR
        U["👤 Usuaria Comunitaria"]
        MIC["🎤 Micrófono Web"]
        UI["📱 Pantalla / Interfaz PWA"]
        SPK["🔊 Parlante Móvil"]
        U <--> MIC
        U <--> UI
        U <--> SPK
    end
    class U,MIC,UI,SPK userClass;

    subgraph SEC_FRONT ["MÓDULO 1: PORTAL WEB DE AUTOCUIDADO & CMS (Vue 3.5 / Netlify)"]
        direction LR
        PORTAL["📚 Portal de Autocuidado<br/><i>Guías, Directorio y Recursos</i>"]
        CMS["⚙️ Panel Administrativo CMS<br/><i>Roles RBAC (Admin/Investigador/CM)</i>"]
        CHAT_UI["💬 Interfaz Web de Chat<br/><i>Sesión Anónima & Respuestas RAG</i>"]
    end
    class PORTAL,CMS,CHAT_UI m1Class;

    subgraph SEC_M3 ["MÓDULO 3: AGENTE MULTIMODAL ALEXIA (Audio Neuronal & WebGL 3D)"]
        direction LR
        OIDO["👂 OÍDO: OpenAI Whisper Large-v3 (Groq)<br/><i>Transcripción <0.4s tolerante a jerga trans</i>"]
        VOZ["🗣️ VOZ: Azure AI Speech Neural<br/><i>Voz uniforme, cálida + 15 Visemas Oculus</i>"]
        CUERPO["💃 CUERPO: Three.js + TalkingHead (WebGL)<br/><i>Modelo .GLB (<5 MB Draco) + 52 Blendshapes ARKit</i>"]
    end
    class OIDO,VOZ,CUERPO m3Class;

    subgraph SEC_M2 ["MÓDULO 2: CEREBRO RAG & BACKEND API (Django REST / Render)"]
        direction TB
        CRISIS["🚨 PRIORIDAD CERO: Detector de Crisis Vital<br/><i>Líneas Gratuitas de Auxilio 106, 123 y Línea Púrpura</i>"]
        GREET["👋 Interceptor de Cortesía / Small-Talk<br/><i>Bienvenida empática sin error de búsqueda</i>"]
        ORCH["🧠 Orquestador RAG Alexia<br/><i>Control de flujo, prompt afirmativo y citas</i>"]
        LLM["🤖 Proveedor LLM Agnóstico<br/><i>Claude 3.5 Sonnet / GPT-4o-mini / Gemini</i>"]
        INGEST["📄 Pipeline de Ingestión & Chunking<br/><i>Fragmentación semántica con solapamiento</i>"]
    end
    class CRISIS ethicsClass;
    class GREET,ORCH,LLM,INGEST m2Class;

    subgraph SEC_DATA ["INFRAESTRUCTURA DE DATOS & CLOUD STORAGE"]
        direction LR
        SUPABASE["🗄️ Supabase PostgreSQL 17 + pgvector<br/><i>Leyes, Decretos 1227, Guías & Embeddings 128d</i>"]
        STORAGE["☁️ Firebase Storage Bucket<br/><i>Documentos Oficiales PDF y Material Descargable</i>"]
    end
    class SUPABASE,STORAGE dataClass;

    %% Conexiones de Entrada
    MIC -->|Audio de Voz| OIDO
    OIDO -->|Texto Transcrito| ORCH
    UI -->|Texto / Navegación| CHAT_UI
    CHAT_UI -->|Consulta API| ORCH
    CMS -->|Publica Contenido| INGEST
    INGEST -->|Almacena PDF| STORAGE
    INGEST -->|Vectores de Búsqueda| SUPABASE

    %% Flujo RAG Interno
    ORCH -->|1. Evaluar Emergencia| CRISIS
    CRISIS -.->|Si hay riesgo vital| CHAT_UI
    ORCH -->|1.5. Evaluar Saludo| GREET
    GREET -.->|Bienvenida Rápida| CHAT_UI
    ORCH -->|2. Recuperación Vectorial| SUPABASE
    SUPABASE -->|Fragmentos y Citas| ORCH
    ORCH -->|3. Generación Aumentada| LLM
    LLM -->|Texto Fundamentado + Emoción| ORCH

    %% Salida Multimodal
    ORCH -->|Texto Limpio + Emoción| VOZ
    VOZ -->|Audio + 15 Visemas| CUERPO
    CUERPO -->|Renderizado WebGL en tiempo real| UI
    VOZ -->|Flujo de Audio Neuronal| SPK
```


### Ventajas de una Arquitectura Integral Unificada
1. **Coherencia y Rendimiento en Tiempo Real:** La sincronización entre el texto generado, la emoción asignada y los movimientos labiales del avatar ocurre en milisegundos sin fricciones de protocolo.
2. **Responsabilidad Centralizada (*Single Point of Responsibility*):** Un único equipo técnico lidera el diseño, la ingeniería de datos, la experiencia visual y el soporte, garantizando un estándar de calidad homogéneo y cumplimiento de plazos.
3. **Plataforma Pre-construida y Verificable:** La arquitectura de base ya se encuentra desplegada en la nube con pruebas unitarias pasando, base de datos pgvector activa y flujo RAG en funcionamiento.

---

## 2. Detalle Tecnológico por Componente

### A. Módulo 3: Agente Virtual Encarnado (Alexia 3D)

#### 1. Voz Neuronal Personalizada y Uniformidad de Marca (TTS)
* **Proveedor:** **Azure AI Speech Neural** (Voz en español con modulación emocional).
* **Consistencia entre Dispositivos:** Se garantiza una voz cálida, humana y uniforme en cualquier celular (Android o iOS) o computador, sin depender de los motores de síntesis genéricos o robóticos de cada teléfono.
* **Sincronización Labial Precisa (Lip-Sync con Visemas):** Azure Speech entrega en una sola llamada el flujo de audio comprimido junto con los eventos de **15 visemas de Oculus** temporizados en milisegundos, permitiendo que la boca del avatar articule cada fonema con total naturalidad sin recargar el procesador del teléfono móvil.

#### 2. Reconocimiento de Voz y Tolerancia a Jergas Locales (ASR)
* **Proveedor:** **OpenAI Whisper Large-v3** ejecutado sobre infraestructura Groq de alta velocidad.
* **Sensibilidad Dialectal:** Transcripción instantánea (<500 ms) optimizada para reconocer con alta precisión el lenguaje natural, regionalismos colombianos, entonaciones diversas y vocabulario comunitario propio de la población trans y no binaria.

#### 3. Modelado 3D, Identidad y Proceso de Co-diseño
* **Motor Gráfico Web:** `Three.js` y la librería especializada `TalkingHead`, ejecutado en el navegador mediante WebGL ligero sin requerir servidores GPU de streaming de video (evitando costos mensuales de más de $400 USD).
* **Optimización Extrema para Móviles (RNF-02):** Personaje 3D en formato `.GLB` optimizado a menos de 5 MB mediante compresión geométrica Draco y texturas KTX2, almacenado en caché local tras la primera descarga.
* **Gesticulación y Expresión Emocional:**
  - Esqueleto compatible con Mixamo para posturas base naturales, movimientos de respiración y parpadeo autónomo.
  - 52 *Blendshapes* faciales estándar ARKit para transiciones emocionales dinámicas (empática, acogedora, informativa, neutral).
* **Validación Comunitaria:** Hasta tres (3) sesiones guiadas de revisión con el equipo de investigación y lideresas comunitarias para afinar el diseño del personaje (vestimenta, rasgos identitarios, peinado y gesticulación representativa).

---

### B. Módulo 2: Asistente Conversacional RAG e Inteligencia Ética

#### 1. Protocolo de Prioridad Cero (Detección de Crisis Vital)
* **Evaluación Inmediata:** Interceptor previo que analiza cada mensaje buscando activadores de ideación suicida, autolesión o violencia física.
* **Respuesta de Auxilio:** Despliega de inmediato la tarjeta de emergencia con líneas telefónicas gratuitas verificadas (Línea 106 de salud mental, Línea 123 y Línea Púrpura), priorizando la vida sobre cualquier procesamiento de lenguaje natural.

#### 2. Búsqueda Vectorial Documental (Cero Alucinaciones)
* **Base de Conocimiento:** PostgreSQL 17 con extensión `pgvector` en Supabase.
* **Citas Verificables:** Las respuestas se sintetizan a partir de fragmentos documentales activos (Decreto 1227 de 2015 para trámites notariales, guías del Ministerio de Salud, rutas de afirmación hormonal en EPS), incorporando citas con número de página y sección.
* **Interceptor de Cortesía (*Small-Talk*):** Reconoce de forma natural saludos cotidianos (*"Hola"*, *"Buenos días"*, *"¿Quién eres?"*), entregando una bienvenida empática y orientadora sin activar fallas de búsqueda documental.

---

### C. Módulo 1: Portal Web de Información, Autocuidado y CMS

#### 1. Portal Web Público Responsivo (PWA)
* Desarrollado en **Vue 3.5**, **Vite** y **TypeScript**, optimizado para conexiones móviles lentas (bundle ultra-ligero de ~100 kB gzipped).
* Catálogo temático de autocuidado, derechos, salud integral y recursos comunitarios con visor de documentos y descarga directa.

#### 2. Panel Administrativo CMS con Roles RBAC
* Sistema de gestión de contenidos con control de acceso granular:
  - **Superadministrador:** Control total del sistema y auditoría.
  - **Investigador:** Creación, edición e indexación de fuentes documentales para el motor RAG.
  - **Gestor de Contenido:** Publicación de guías, artículos temáticos y categorías del portal.
* Métricas éticas y agregadas de lectura y descargas (sin rastreo de datos personales ni direcciones IP, cumpliendo el principio de privacidad RNF-06).

---

## 3. Presupuesto Integral y Matriz de Entregables: $15.000.000 COP

La propuesta consolida una **tarifa paquete integral cerrada de $15.000.000 COP** *(Referencia: $3.750 USD)* por un esfuerzo total de **195 horas** de ingeniería especializada:

| Fase / Componente | Requerimientos | Entregables Específicos | Horas | Duración | Subtotal (COP) | Ref. (USD) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Fase 1: Arquitectura, Especificación & Seguridad Ética** | M1, M2, M3, RNF-01 a RNF-10, Ética | • Documento formal de arquitectura técnica e interoperabilidad multimodal.<br>• Modelo relacional y vectorial en PostgreSQL (`pgvector`).<br>• Protocolo ético de crisis (RF-RAG-09) y salvaguardas de no revictimización. | 20 h | 1 semana | **$1.500.000** | $375 |
| **Fase 2 (Módulo 1): Portal Web de Autocuidado & Panel CMS** | M1-RF-01 a 07, RNF-01, 02, 05 | • Portal web público responsivo PWA para móviles de bajo consumo.<br>• Catálogo temático de guías descargables y artículos de autocuidado.<br>• Panel administrativo CMS con autenticación y roles RBAC granulares.<br>• Métricas agregadas de lectura y descarga de recursos. | 45 h | 2 semanas | **$4.000.000** | $1.000 |
| **Fase 3 (Módulo 2): Motor RAG Documental & Protocolo de Crisis** | M2-RF-01 a 10, RNF-04, 06 | • Pipeline de extracción, fragmentación semántica y embeddings vectoriales.<br>• Interfaz web de Chat con sesiones anónimas de alta privacidad.<br>• Módulo de Prioridad Cero: Tarjeta visual de crisis y líneas 106/123/Púrpura.<br>• Sistema de citas bibliográficas desplegables por página y sección.<br>• Interceptor inteligente de saludos y bienvenida comunitaria. | 50 h | 2 semanas | **$4.500.000** | $1.125 |
| **Fase 4 (Módulo 3): Avatar Alexia 3D, Voz Neuronal & Co-Diseño** | M3-RF-01 a 10, Sección 4.3.3 | • Integración de **Azure AI Speech Neural** (voz uniforme + visemas Oculus).<br>• Integración de **OpenAI Whisper (Groq)** para acentos y jergas trans.<br>• Personaje 3D `.GLB` optimizado (<5 MB) en WebGL Three.js / TalkingHead.<br>• Sincronización labial fonética (15 visemas) y 52 blendshapes ARKit.<br>• **Acompañamiento en 3 sesiones de co-diseño y validación comunitaria**. | 55 h | 2.5 semanas | **$3.500.000** | $875 |
| **Fase 5: Pruebas Piloto, Despliegue en Producción & Garantía** | Secciones 8 y 10 | • Pruebas integrales de estrés en dispositivos móviles Android e iOS.<br>• Despliegue en producción cloud de alta disponibilidad.<br>• Entrega de código fuente documentado, Swagger OpenAPI y manual técnico.<br>• **Garantía técnica de 60 días calendario y soporte de estabilización**. | 25 h | 1 semana | **$1.500.000** | $375 |
| **TOTAL GENERAL CONSOLIDADO** | **Solución Completa Llave en Mano (Módulos 1, 2 y 3)** | **195 h** | **7 a 8 semanas** | **$15.000.000** | **$3.750** |

---

## 4. Costos Operativos Recurrentes Estimados (Infraestructura)

Dimensionado para la fase piloto y validación con la comunidad (hasta 50 usuarios concurrentes y más de 1.500 consultas de voz mensuales):

| Servicio | Proveedor / Tecnología | Costo Mensual Estimado | Justificación Técnica |
| :--- | :--- | :---: | :--- |
| **Alojamiento Web & CDN** | Netlify | **$0 USD** | Cubierto por la capa gratuita (tráfico estático y distribución SPA global). |
| **Backend API Docker** | Render | **$0 a $7 USD** | Capa gratuita disponible para piloto; $7 USD/mes en plan productivo continuo sin suspensión. |
| **Base de Datos & Vectores** | Supabase (PostgreSQL + pgvector) | **$0 USD** | Tier gratuito incluye 500 MB y hasta 50.000 vectores (suficiente para toda la documentación del proyecto). |
| **Síntesis de Voz Neuronal & Visemas** | Azure AI Speech (`F0 Free Tier`) | **$0 USD** | **500.000 caracteres gratis mensuales permanentes** (~1.250 a 1.500 respuestas de voz al mes). Superada la cuota: $0.016 USD por cada 1.000 caracteres. |
| **Reconocimiento de Voz (ASR)** | Groq Whisper Large-v3 | **$0 a $2 USD** | Tarifa ultra-económica ($0.0005 USD por minuto de audio transcrito). |
| **TOTAL RECURRENTE ESTIMADO** | — | **$0 a $9 USD / mes**<br>*(~$0 a $38.000 COP / mes)* | Costo de infraestructura prácticamente nulo para la Fundación durante todo el desarrollo y pilotaje. |

---

## 5. Cronograma de Trabajo y Plan de Hitos

El proyecto se desarrollará a lo largo de **7 a 8 semanas**, organizado en sprints con entregables tangibles verificables:

```
Semana 1-2: [Sprint 1] Arquitectura, Especificación de API y Salvaguardas Éticas.
Semana 3-4: [Sprint 2] Portal Web Móvil, Catálogo de Autocuidado y Panel CMS con Roles.
Semana 5-6: [Sprint 3] Motor RAG, Ingesta de Documentos, pgvector y Tarjeta de Crisis.
Semana 6-7: [Sprint 4] Avatar 3D WebGL, Azure Neural Speech, Whisper y Rondas de Co-diseño.
Semana 8:   [Sprint 5] Pruebas Piloto en Móviles, Despliegue en Producción y Entrega Final.
```

### Esquema de Pagos por Hitos de Entrega:
* **Hito 1 (30% — $4.500.000 COP):** Firma del acuerdo de inicio, entrega del documento de arquitectura técnica y despliegue del entorno base de desarrollo.
* **Hito 2 (35% — $5.250.000 COP):** Entrega funcional de los Módulos 1 y 2 (Portal web, CMS administrativo operativo y Chat RAG con detector de crisis y citas verificadas).
* **Hito 3 (35% — $5.250.000 COP):** Entrega final del Módulo 3 (Avatar Alexia 3D con voz de Azure, visemas sincronizados, integración Whisper y co-diseño comunitario validado), despliegue en producción y acta de cierre.

---

## 6. Criterios de Calidad, Cumplimiento y Garantías de la Solución

| Dimensión | Compromiso y Estándar de Entrega |
| :--- | :--- |
| **Rendimiento Móvil (RNF-02, RNF-03)** | Bundle web menor a 150 kB gzipped; modelo 3D comprimido a menos de 5 MB; carga funcional en menos de 2.5 segundos en redes móviles 4G. |
| **Privacidad y No Revictimización (RNF-06)** | Sesiones ciudadanas anónimas en `sessionStorage`; cero registro de nombres reales o IPs; telemetría anonimizada. |
| **Calidad Documental Anti-Alucinación** | Respuestas fundamentadas estrictamente en los documentos oficiales indexados; citas visibles con página y sección. |
| **Uniformidad y Empatía de Voz** | Voz neuronal consistente en cualquier marca de dispositivo; reconocimiento preciso de jergas comunitarias con Whisper. |
| **Representación e Identidad** | Personaje 3D construido a partir de rondas de co-diseño con la comunidad; expresiones faciales y corporales de escucha activa. |
| **Soporte y Garantía Post-Entrega** | **Garantía técnica de 60 días calendario** para corrección de bugs o ajustes menores tras la entrega final. |

---

## 7. Aceptación y Formalización

La presente propuesta técnica y económica garantiza a la Fundación TransLúcidas una plataforma moderna, culturalmente sensible, escalable y respaldada por las mejores prácticas de la ingeniería de software actual.

Para formalizar la aceptación de esta propuesta o coordinar la sesión de inicio técnico, quedamos a su entera disposición.

**Por el Equipo de Desarrollo e Ingeniería:**  
*Plataforma TransLúcidas — Proyecto Alexia*  
*Contacto: lxia.dev.project@gmail.com*  
*Repositorios Oficiales:*  
• Backend API: `https://github.com/lxiadevproject-prog/lxia_be`  
• Frontend Web: `https://github.com/lxiadevproject-prog/lxia_fe`
