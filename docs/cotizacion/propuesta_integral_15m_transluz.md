# 📑 PROPUESTA TÉCNICA Y ECONÓMICA INTEGRAL
## Plataforma TransLúcidas: Portal de Autocuidado, Asistente Conversacional RAG y Agente Virtual Encarnado 3D (Alexia)

---

* **Destinatario:** Fundación TransLúcidas — Equipo de Investigación y Dirección de Proyecto  
  *(Atención: David Herrera y Comité Técnico)*
* **Modalidad de Contratación:** Llave en Mano / Solución Integral Unificada (Módulos 1, 2 y 3)
* **Fecha de Emisión:** 23 de Octubre de 2026
* **Vigencia de la Oferta:** 30 días calendario
* **Inversión Total Consolidada:** **$15.000.000 COP** *(Referencia: $3.750 USD)*
* **Prototipo Funcional en Vivo:**  
  • **Frontend Web & Avatar:** [https://lxia-fe.netlify.app](https://lxia-fe.netlify.app)  
  • **Backend API & Swagger:** [https://lxia-be.onrender.com/api/docs/](https://lxia-be.onrender.com/api/docs/)  
  • **Base de Datos Vectorial:** PostgreSQL 17 + `pgvector` en Supabase (Documentos oficiales ya indexados)

---

## 1. Resumen Ejecutivo y Justificación de la Solución Unificada

La presente propuesta responde de forma exhaustiva a los requerimientos del **Documento Preliminar de Software v0.1 (Módulos 1, 2 y 3)** y a las prioridades estratégicas manifestadas por el equipo de investigación en torno a la **identidad, calidez humana, empatía y sensibilidad cultural** de la plataforma.

### El Riesgo de Fragmentar el Desarrollo vs. La Solución Integral
Contratar el desarrollo dividiendo los Módulos 1 y 2 (Portal y Cerebro RAG) con un proveedor y el Módulo 3 (Avatar 3D y Voz) con otro genera **graves riesgos de viabilidad técnica y sobrecostos operativos**:
1. **El "Infierno de Integración":** El Avatar 3D no puede operar de forma aislada; depende segundo a segundo de los tiempos de respuesta del motor RAG, la detección de crisis y los metadatos emocionales. Si se presentan latencias altas o desajustes de visemas en los celulares de las usuarias, dos proveedores independientes terminarán culpándose mutuamente.
2. **Dilución de Garantías y Retrasos:** Los cronogramas se desalinean y la Fundación queda atrapada en reuniones de coordinación técnica improductivas.
3. **Nuestra Ventaja Insuperable:** Al asumir la **responsabilidad técnica integral**, ofrecemos un único interlocutor (*Single Point of Contact*), un solo SLA de garantía y la tranquilidad de que el núcleo del backend, las leyes indexadas y la interfaz web **ya están desarrollados, probados y desplegados en producción**.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        ARQUITECTURA MULTIMODAL INTEGRAL ALEXIA                         │
│                                                                                        │
│  1. OÍDO (ASR Comunitario)         2. CEREBRO & ÉTICA (RAG)     3. VOZ (Síntesis)      │
│  ┌─────────────────────────┐       ┌─────────────────────────┐  ┌────────────────────┐ │
│  │ OpenAI Whisper Large-v3 │ ───►  │ Orquestador RAG Django  │ ──► Azure AI Speech   │ │
│  │ sobre API Groq (<0.4 s) │       │ + pgvector Supabase     │  │ Neural (Uniforme,  │ │
│  │ Tolerancia a jerga trans│       │ + Filtro Crisis Cero    │  │ cálida + Visemas)  │ │
│  └─────────────────────────┘       └─────────────────────────┘  └─────────┬──────────┘ │
│                                                 │                         │            │
│                                                 ▼                         ▼            │
│                                    ┌─────────────────────────────────────────────────┐ │
│                                    │ 4. CUERPO & EXPRESIÓN (WebGL Three.js)          │ │
│                                    │ Avatar 3D .GLB (<5 MB Draco) + 15 Visemas Oculus│ │
│                                    │ + 52 Blendshapes ARKit + Co-diseño Comunitario  │ │
│                                    └─────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Especificación Técnica por Componente

### A. Voz de Alexia y Reconocimiento de Acentos Comunitarios
* **Síntesis Neuronal Personalizada (TTS):** Se integra **Azure AI Speech Neural**. Se descarta la voz genérica del navegador para garantizar una voz femenina, empática, uniforme y consistente en cualquier marca de dispositivo móvil (Android, iOS o PC), con modulación de velocidad y tono adaptada al perfil comunitario.
* **Sincronización Labial Precisa (Lip-Sync):** Azure Speech emite en una única llamada el flujo de audio comprimido junto con los identificadores de **visemas temporizados (15 visemas de Oculus)**, permitiendo que la boca del modelo 3D articule con exactitud fonética sin sobrecargar la CPU del teléfono.
* **Reconocimiento del Habla (ASR):** Se implementa **OpenAI Whisper Large-v3** ejecutado sobre infraestructura de ultra-baja latencia (Groq API). Esto garantiza una transcripción en menos de 500 ms con alta tolerancia a modismos, regionalismos colombianos y jerga propia de las personas trans y de género diverso.

### B. Modelado 3D, Identidad Trans y Co-diseño
* **Estándar Gráfico WebGL:** Basado en `Three.js` y la librería especializada `TalkingHead`, ejecutado 100% en el cliente web sin requerir servidores GPU costosos de streaming de video.
* **Optimización Extrema para Móviles (RNF-02):** Modelo 3D en formato `.GLB` optimizado a menos de 5 MB mediante compresión geométrica Draco y texturas KTX2, con almacenamiento en caché local tras la primera descarga.
* **Identidad y Expresión Emocional:** 
  - Esqueleto compatible con Mixamo para posturas corporales naturales y de escucha activa.
  - 52 *Blendshapes* faciales estándar ARKit para transiciones emocionales (empática, acogedora, informativa, neutral).
  - **Proceso de Co-diseño:** Hasta 3 sesiones de revisión con el equipo de investigación y lideresas comunitarias para validar vestimenta, rasgos físicos, peinado y gesticulación representativa.

### C. Cerebro RAG, Salvaguardas Éticas y Portal CMS
* **Protocolo de Prioridad Cero (Crisis Vital):** Interceptor estricto antes de cualquier llamada a LLM que detecta ideación suicida, autolesión o violencia física, desplegando de inmediato la tarjeta de emergencia con líneas telefónicas gratuitas verificadas (Línea 106, Línea 123, Línea Púrpura).
* **Búsqueda Vectorial con Cero Alucinaciones:** Base de datos PostgreSQL con extensión `pgvector` en Supabase. Las respuestas se sintetizan exclusivamente a partir de documentos verificados (Decretos notariales, guías del Ministerio de Salud, rutas EPS) e incluyen citas bibliográficas con página y sección.
* **Detector de Cortesía (*Small-Talk*):** Interceptor conversacional que brinda una bienvenida cálida e institucional ante saludos cotidianos (*"Hola"*, *"Buenos días"*), orientando al usuario sin fallas de búsqueda documental.
* **Portal Web y CMS:** Sitio web móvil PWA (Vue 3.5 + Vite) con catálogo temático de recursos, visor de artículos y panel administrativo con control de acceso basado en roles (Superadmin, Investigador, Gestor de Contenido).

---

## 3. Presupuesto Integral Ajustado: $15.000.000 COP

Para ajustarse estrictamente a la capacidad presupuestal del proyecto y permitir la contratación de la solución completa con un único proveedor de confianza, se consolida una **tarifa paquete integral cerrada de $15.000.000 COP**, distribuida de la siguiente manera:

| Fase / Módulo | Alcance y Entregables Específicos | Horas Est. | Duración | Subtotal (COP) | Ref. (USD) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Fase 1: Arquitectura, Especificación & Seguridad Ética** | • Documento de arquitectura técnica e interoperabilidad multimodal.<br>• Modelo relacional y vectorial en PostgreSQL (`pgvector`).<br>• Protocolo ético de crisis (RF-RAG-09) y flujos de no revictimización. | 20 h | 1 semana | **$1.500.000** | $375 |
| **Fase 2 (Módulo 1): Portal Web de Autocuidado & Panel CMS** | • Portal web público responsivo PWA para móviles (bajo consumo).<br>• Catálogo temático de guías descargables y artículos de autocuidado.<br>• Panel administrativo CMS con autenticación y roles RBAC.<br>• Métricas de lectura y descargas anónimas agregadas. | 45 h | 2 semanas | **$4.000.000** | $1.000 |
| **Fase 3 (Módulo 2): Asistente RAG & Inteligencia Documental** | • Pipeline de extracción de texto, fragmentación y embeddings vectoriales.<br>• Interfaz web de Chat con sesiones anónimas (respeto a la privacidad).<br>• **Módulo de Prioridad Cero:** Tarjeta visual de crisis y líneas 106/123.<br>• Sistema de citas bibliográficas desplegables por página y sección.<br>• Interceptor inteligente de saludos y cortesía (*small-talk*). | 50 h | 2 semanas | **$4.500.000** | $1.125 |
| **Fase 4 (Módulo 3): Avatar Alexia 3D, Voz Neuronal & Co-Diseño** | • Integración de **Azure AI Speech Neural** (voz uniforme + visemas).<br>• Integración de **OpenAI Whisper (Groq)** para acentos y jergas trans.<br>• Personaje 3D `.GLB` optimizado (<5 MB) en WebGL Three.js / TalkingHead.<br>• Sincronización labial fonética (15 visemas Oculus) y 52 blendshapes ARKit.<br>• **Acompañamiento en 3 sesiones de co-diseño y validación comunitaria**. | 55 h | 2.5 semanas | **$3.500.000** | $875 |
| **Fase 5: Integración, Pruebas Piloto, Producción & Garantía** | • Pruebas integrales de estrés en dispositivos móviles Android e iOS.<br>• Despliegue en producción cloud de alta disponibilidad.<br>• Entrega de código fuente documentado, Swagger OpenAPI y manual técnico.<br>• **Garantía técnica de 60 días calendario y soporte de estabilización**. | 25 h | 1 semana | **$1.500.000** | $375 |
| **TOTAL GENERAL CONSOLIDADO** | **Solución Completa Llave en Mano (Módulos 1, 2 y 3)** | **195 h** | **7 a 8 semanas** | **$15.000.000** | **$3.750** |

---

## 4. Costos Operativos Recurrentes Estimados (Cero Sorpresas)

Dimensionado para la fase piloto y validación con la comunidad (hasta 50 usuarios concurrentes y más de 1.500 consultas de voz mensuales):

| Servicio | Proveedor / Tecnología | Costo Mensual Estimado | Justificación |
| :--- | :--- | :---: | :--- |
| **Alojamiento Web & CDN** | Netlify | **$0 USD** | Cubierto por capa gratuita (tráfico estático y SPA global). |
| **Backend API Docker** | Render | **$0 a $7 USD** | Capa gratuita disponible para piloto; $7 USD/mes en plan productivo continuo sin suspensión. |
| **Base de Datos & Vectores** | Supabase (PostgreSQL + pgvector) | **$0 USD** | Tier gratuito incluye 500 MB y hasta 50.000 vectores (más que suficiente para toda la legislación colombiana). |
| **Síntesis de Voz Neuronal & Visemas** | Azure AI Speech (`F0 Free Tier`) | **$0 USD** | **500.000 caracteres gratis cada mes de forma permanente** (~1.250 a 1.500 respuestas de voz de Alexia al mes). Superada la cuota: solo $0.016 USD por cada 1.000 caracteres. |
| **Reconocimiento de Voz (ASR)** | Groq Whisper Large-v3 | **$0 a $2 USD** | Tarifa ultra-económica ($0.0005 USD por minuto de audio transcrito). |
| **TOTAL RECURRENTE ESTIMADO** | — | **$0 a $9 USD / mes**<br>*(~$0 a $38.000 COP / mes)* | Costo operativo prácticamente nulo para la Fundación durante todo el desarrollo y pilotaje. |

---

## 5. Cronograma de Trabajo y Plan de Hitos

El proyecto se ejecutará en un período estimado de **7 a 8 semanas**, organizado en sprints con entregables tangibles verificables:

```
Semana 1-2: [Sprint 1] Arquitectura, Especificación de API y Salvaguardas Éticas.
Semana 3-4: [Sprint 2] Portal Web Móvil, Catálogo de Autocuidado y Panel CMS con Roles.
Semana 5-6: [Sprint 3] Motor RAG, Ingesta de Documentos, pgvector y Tarjeta de Crisis.
Semana 6-7: [Sprint 4] Avatar 3D WebGL, Azure Neural Speech, Whisper y Rondas de Co-diseño.
Semana 8:   [Sprint 5] Pruebas Piloto en Móviles, Despliegue en Producción y Entrega Final.
```

### Esquema de Pagos por Hitos de Entrega:
* **Hito 1 (30% — $4.500.000 COP):** Acta de inicio, entrega de documento de arquitectura y despliegue del entorno base de desarrollo.
* **Hito 2 (35% — $5.250.000 COP):** Entrega funcional de los Módulos 1 y 2 (Portal web, CMS administrativo operativo y Chat RAG con detector de crisis y citas verificadas).
* **Hito 3 (35% — $5.250.000 COP):** Entrega final del Módulo 3 (Avatar Alexia 3D con voz de Azure, visemas sincronizados, integración Whisper y co-diseño comunitario), despliegue en producción y acta de cierre.

---

## 6. Cuadro Comparativo: ¿Por qué esta propuesta es la mejor decisión?

| Criterio de Evaluación | Propuesta Fragmentada (Dos Proveedores) | Nuestra Propuesta Integral ($15M COP) |
| :--- | :--- | :--- |
| **Responsabilidad Contractual** | Dos contratos separados; riesgo de culpas mutuas ante fallas de integración. | **Un único responsable (*Single SLA*)**: Garantía total de punta a punta. |
| **Estado de Avance Actual** | Promesas en PDF; cero líneas de código ejecutadas. | **Prototipo real ya desplegado y navegable en Netlify, Render y Supabase.** |
| **Voz y Acentos Comunitarios** | Dependencia de sincronización externa no probada. | **Azure Neural Speech + Whisper en Groq nativamente acoplados al orquestador RAG.** |
| **Identidad 3D y Validación** | Cotización subvalorada con alto riesgo de abandono. | **Avatar 3D WebGL profesional (<5 MB Draco) con 3 sesiones de co-diseño comunitario.** |
| **Protección contra Crisis** | No contemplada en la propuesta del Módulo 3. | **Protocolo Prioridad Cero activo (Líneas 106/123/Púrpura en tiempo real).** |
| **Inversión Económica Total** | Módulo 3 aislado (~$4.1M a $5.8M) + Módulos 1 y 2 (~$14.8M) = **~$19M a $20M COP**. | **Tarifa paquete cerrado de $15.000.000 COP por TODO el proyecto.** |

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
