# 📑 Propuesta Técnica y Económica Formal: Plataforma TransLúcidas
### Portal de Autocuidado, Asistente Conversacional RAG y Agente Virtual Encarnado (Alexia)

* **Documento Base de Referencia:** `Documento preliminar de requerimientos de software v0.1` ([docs/requirements/Documento preliminar de requerimientos de software.pdf](file:///C:/Users/Lenovo/PycharmProjects/lxia_be/docs/requirements/Documento%20preliminar%20de%20requerimientos%20de%20software.pdf))
* **Destinatario:** Equipo de Investigación del Proyecto TransLúcidas
* **Fecha de Emisión:** 21 de Octubre de 2026
* **Vigencia de la Oferta:** 30 días calendario
* **Moneda:** Pesos Colombianos (COP) — con valores de referencia en Dólares Estadounidenses (USD)

---

## 1. Descripción de la Solución y Enfoque Arquitectural

En cumplimiento de las secciones **1, 4 y 5 del documento de requerimientos**, la solución se concibe como un sistema modular e interoperable, de bajo consumo de datos y culturalmente sensible, conformado por tres módulos funcionales y servicios transversales compartidos:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 CANALES DE USUARIO                                     │
│  ┌──────────────────────┐  ┌───────────────────────┐  ┌─────────────────────────────┐  │
│  │   Portal Web Móvil   │  │    Chat RAG Web &     │  │  Avatar Alexia Interactivo  │  │
│  │   (Bajo consumo/SPA) │  │  Tarjeta de Crisis    │  │   (Voz TTS / Expresiones)   │  │
│  └──────────┬───────────┘  └───────────┬───────────┘  └──────────────┬──────────────┘  │
└─────────────┼──────────────────────────┼─────────────────────────────┼─────────────────┘
              │                          │                             │
              ▼                          ▼                             ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        BACKEND API DESACOPLADO (DJANGO REST)                           │
│  ┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐ │
│  │ Autenticación & Perfil  │  │   Gestión Contenidos    │  │ Orquestador RAG         │ │
│  │     (RBAC Granular)     │  │  (CMS Artículos/Rec)    │  │ (Embeddings & Prompt)   │ │
│  └─────────────────────────┘  └─────────────────────────┘  └────────────┬────────────┘ │
│                                                                         │              │
│  ┌──────────────────────────────────────────────────────────────────────┴────────────┐ │
│  │   PROTOCOLOS DE SEGURIDAD ÉTICA: Detector de Crisis y Líneas de Emergencia Cero    │ │
│  └───────────────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────┬───────────────────────────────────────────────┘
                                         │
                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                           INFRAESTRUCTURA DE DATOS                                     │
│  ┌──────────────────────────────────────────┐  ┌─────────────────────────────────────┐ │
│  │ Base de Datos PostgreSQL + pgvector      │  │ Almacenamiento Serverless           │ │
│  │ (Fragmentos, Citas, Similitud Coseno)    │  │ (Documentos, Guías PDF, Recursos)   │ │
│  └──────────────────────────────────────────┘  └─────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Principios de Arquitectura Cumplidos (Sección 5.2):
1. **Separación lógica estricta:** Backend API (Django 6 / DRF) desacoplado del cliente web (Vue 3.5 / Vite).
2. **Sustituibilidad de proveedores de IA:** Orquestador agnóstico con conmutación dinámica entre OpenAI, Anthropic Claude, Google Gemini y modelos locales.
3. **Privacidad y No Revictimización (RNF-06 y Sección 7):** Sesiones ciudadanas anónimas en `sessionStorage`, minimización de telemetría y exclusión de datos personales en consultas vectoriales.
4. **Diseño para conectividad móvil limitada (Sección 4.2.3):** Cargas diferidas, compresión gzip, estáticos cacheados y cero descarga obligatoria de recursos pesados.

---

## 2. Tecnologías, Modelos y Proveedores Recomendados

| Componente | Tecnologías Recomendadas | Justificación Técnica y Económica |
| :--- | :--- | :--- |
| **Backend API** | Python 3.12+, Django REST Framework, WhiteNoise, Gunicorn | Estabilidad empresarial, ORM seguro contra inyección SQL, soporte nativo para RBAC y documentación OpenAPI 3 automática. |
| **Base de Datos & Vectores** | PostgreSQL 17 + Extensión `pgvector` (Supabase / Render) | Almacenamiento unificado de datos relacionales y embeddings vectoriales de alta dimensionalidad (cero costos de bases vectoriales externas tipo Pinecone). |
| **Frontend Web** | Vue 3.5+, Vite 8, TypeScript, Pinia, `@lucide/vue`, Vanilla CSS | Rendimiento óptimo, bundle ultra ligero (~100 kB gzipped), compatibilidad móvil PWA y total control de accesibilidad (RNF-01, RNF-03). |
| **Modelos de Embeddings** | `text-embedding-3-small` (OpenAI) / Gemini Text Embeddings | Excelente relación precisión semántica/costo ($0.02 USD por millón de tokens). |
| **Modelos LLM (RAG)** | Claude 3.5 Sonnet / GPT-4o-mini / Gemini 1.5 Flash | Razonamiento clínico/legal fundamentado, baja tasa de alucinación y soporte nativo de citas bibliográficas contextuales. |
| **Voz (TTS & ASR)** | Web Speech API (Navegador) + Fallback Whisper API | **Cero costo de transferencia para el usuario móvil** mediante síntesis nativa del navegador; alta precisión fonética sin Markdown. |
| **Infraestructura Cloud** | Netlify (CDN Frontend) + Render (Docker Backend) + Supabase (DB) | Tier gratuito inicial disponible, escalabilidad automática y alta disponibilidad regional (Oregon / US-West). |

---

## 3. Matriz de Cotización Detallada por Fases y Entregables

Con base en la **Sección 9 (Propuesta de implementación por fases)**, la **Sección 8 (Entregables esperados)** y la **Sección 4.3.3 (Niveles de Alexia)** del PDF:

| Fase / Componente | Requerimientos Cubiertos | Entregables Específicos (Sección 8) | Horas Est. | Duración | Valor (COP) | Valor Ref. (USD) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Fase 1: Definición, Diseño Técnico & Arquitectura** | M1, M2, M3, RNF-01 a RNF-10, Sección 7 (Ética) | • Documento de arquitectura técnica.<br>• Modelo de datos, flujos de API y salvaguardas éticas.<br>• Revisión del prototipo Figma y criterios de aceptación. | 32 h | 1.5 sem | $3.200.000 | $800 |
| **Fase 2: Portal Web de Información y Autocuidado & CMS** | M1-RF-01 a M1-RF-07, RNF-01, RNF-02, RNF-05 | • Sitio web público adaptado a móviles (bajo consumo).<br>• Catálogo temático de artículos y descargables.<br>• Panel CMS administrativo con roles RBAC.<br>• Contador atómico de lecturas y descargas. | 48 h | 2.5 sem | $5.800.000 | $1.450 |
| **Fase 3: Asistente Conversacional con IA (RAG)** | M2-RF-01 a M2-RF-10, RNF-04, RNF-06, Sección 7 | • Pipeline de ingestión, chunking y vector search.<br>• Interfaz web de chat con sesiones anónimas.<br>• **Tarjeta de Crisis Prioridad Cero** (Líneas 106/123/Púrpura).<br>• Citas bibliográficas desplegables por página y sección. | 60 h | 3 sem | $7.800.000 | $1.950 |
| **Fase 4: Integración con Canales de Mensajería (Opcional)** | M2-RF-07, Sección 4.2.3 | • Webhook y adaptador para WhatsApp Cloud API / Messenger.<br>• Gestión de sesiones de bajo ancho de banda.<br>• Control de rate limits y políticas de mensajería Meta. | 30 h | 1.5 sem | $3.500.000 | $875 |
| **Fase 5A: Alexia Nivel 1 — Prototipo Funcional (Base)** | M3-RF-01 a M3-RF-04, M3-RF-06, M3-RF-09, M3-RF-10 | • Avatar visible en interfaz web con feedback visual.<br>• Integración directa con servicio RAG (M2).<br>• Entrada de voz (Web Speech Recognition / Micrófono).<br>• Síntesis de voz (TTS) con texto limpio de Markdown.<br>• Expresiones emocionales reactivas y fallback textual. | 36 h | 2 sem | $4.500.000 | $1.125 |
| **Fase 5B: Alexia Nivel 2 — Agente Expresivo (Opcional)** | M3-RF-07, M3-RF-08, Sección 4.3.3 | • Sincronización labial dinámica (lip-sync con visemas).<br>• Repertorio avanzado de gestos y animaciones faciales.<br>• Motor de estados emocionales en tiempo real. | 35 h | 2 sem | $4.200.000 | $1.050 |
| **Fase 5C: Alexia Nivel 3 — Experimental Avanzado (Opcional)** | M3-RF-05, Sección 4.3.3 | • Adaptación ASR a variedades dialectales de la comunidad.<br>• Instrumentación para evaluación científica y aceptación.<br>• Análisis de latencia y sincronización multimodal. | 30 h | 2 sem | $3.800.000 | $950 |
| **Fase 6: Integración, Pruebas, Despliegue & Producción** | Secciones 8 (7-12), 10 (Criterios Aceptación) | • Pruebas automatizadas (unitarias e integración).<br>• Despliegue en producción (Netlify + Render + Supabase).<br>• Manual de despliegue, entrega de código y accesos.<br>• Período de garantía y soporte de estabilización. | 34 h | 1.5 sem | $3.900.000 | $975 |

---

## 4. Opciones de Contratación Modular

El documento preliminar (Sección 12) recomienda explícitamente:
> *"una cotización desglosada que permita contratar inicialmente los componentes prioritarios y decidir la continuidad de las capacidades experimentales de acuerdo con los resultados técnicos, presupuestales y de investigación."*

A continuación se presentan los paquetes de contratación sugeridos:

### 📦 Opción A: Plataforma Esencial (Prioritaria para Validación Piloto)
* **Alcance:** Fase 1 (Arquitectura) + Fase 2 (Portal Web & CMS) + Fase 3 (Asistente RAG & Crisis) + Fase 5A (Alexia Nivel 1) + Fase 6 (Despliegue & Garantía).
* **Duración total:** 8 a 10 semanas.
* **Esfuerzo:** 210 horas de ingeniería senior.
* **Inversión Total:** **$25.200.000 COP** (~$6.300 USD).

### 📦 Opción B: Plataforma Integral con Mensajería & Alexia Nivel 2
* **Alcance:** Opción A + Fase 4 (WhatsApp Cloud API) + Fase 5B (Alexia Agente Expresivo con Lip-Sync).
* **Duración total:** 11 a 13 semanas.
* **Esfuerzo:** 275 horas de ingeniería senior.
* **Inversión Total:** **$32.900.000 COP** (~$8.225 USD).

### 📦 Opción C: Ecosistema Completo de Investigación (Todos los Módulos & Nivel 3)
* **Alcance:** Todas las fases (1, 2, 3, 4, 5A, 5B, 5C y 6).
* **Duración total:** 13 a 15 semanas.
* **Esfuerzo:** 305 horas de ingeniería senior.
* **Inversión Total:** **$36.700.000 COP** (~$9.175 USD).

---

## 5. Estimación de Costos Recurrentes de Operación (RNF-10 y Sección 12)

Estos costos corresponden a servicios de infraestructura, licencias y consumo de APIs de terceros. **Deben ser asumidos directamente por el proyecto o la institución titular**:

| Concepto / Servicio | Proveedor Recomendado | Nivel de Uso Estimado | Costo Estimado Mensual | Costo Estimado Anual |
| :--- | :--- | :--- | :---: | :---: |
| **Hosting Frontend (CDN)** | Netlify | Tráfico web de portal y SPA | $0 COP (Tier Gratuito) | $0 COP |
| **Servicio Backend Web** | Render | Docker Web Service (512 MB - 1 GB RAM) | $0 – $28.000 COP ($0 - $7 USD) | $0 – $336.000 COP |
| **Base de Datos & `pgvector`** | Supabase | PostgreSQL 17 + Vector Search (500 MB) | $0 COP (Tier Gratuito) | $0 COP |
| **Almacenamiento Serverless** | Firebase Storage | Guías, infografías y protocolos (0 - 5 GB) | $0 COP (Tier Gratuito Spark) | $0 COP |
| **Consumo de Modelos IA (RAG)** | OpenAI / Gemini API | ~3.000 a 5.000 consultas/mes | $25.000 – $60.000 COP ($6 - $15 USD) | $300.000 – $720.000 COP |
| **Dominio Personalizado & SSL** | Namecheap / GoDaddy | Dominio institucional `.org` o `.co` | N/A | $55.000 – $90.000 COP |
| **Canal WhatsApp (Si aplica F4)** | Meta Cloud API | Primeras 1.000 conversaciones/mes gratis | $0 – $40.000 COP según volumen | $0 – $480.000 COP |
| **TOTAL ESTIMADO RECURRENTE** | — | **Operación estándar en fase piloto** | **~$25.000 – $128.000 COP/mes** | **~$650.000 – $1.600.000 COP/año** |

---

## 6. Matriz de Riesgos, Supuestos y Dependencias (Sección 12)

| Riesgo Identificado | Nivel | Estrategia de Mitigación / Salvaguarda |
| :--- | :---: | :--- |
| **Latencia o caída de APIs de IA externas** | Medio | Implementación de fallback multi-proveedor (OpenAI ➔ Anthropic ➔ Gemini) y respuestas de contingencia amables preconfiguradas. |
| **Riesgo ético de alucinaciones en temas de salud/legales** | Alto | Inyección estricta de contexto mediante RAG con citas exactas y **Tarjeta de Crisis Prioridad Cero** para transferir de inmediato a líneas humanas oficiales (106, 123, Púrpura). |
| **Acceso desde redes móviles lentas o inestables** | Alto | Interfaz ligera en CSS puro, compresión Gzip, bundle < 100 kB y caché de recursos locales (Sección 4.2.3). |
| **Costos imprevistos de WhatsApp Business** | Medio | Se incluye como fase modular independiente (Fase 4); la web móvil es el canal prioritario garantizado sin costo por mensaje. |
| **Dependencia del equipo investigador para fuentes** | Medio | El CMS y la consola RAG permiten cargar, auditar y retirar documentos en 1 clic sin depender de ajustes en el código fuente. |

---

## 7. Criterios de Aceptación Cumplidos (Sección 10 del PDF)

1. ✅ **Portal Informativo:** Implementa las vistas, navegación y recursos validados en Figma con diseño accesible.
2. ✅ **Asistente RAG Fundamentado:** Responde con base en documentos cargados e indica claramente sus limitaciones cuando no hay información suficiente (M2-RF-10).
3. ✅ **Gestión Dinámica de Documentos:** Ingestión y re-indexación de fuentes sin recompilar ni reiniciar el sistema (M2-RF-08).
4. ✅ **Alexia Multimodal:** Interacción con entrada de voz, síntesis TTS fonética y representación de estados emocionales.
5. ✅ **Interoperabilidad:** APIs documentadas con OpenAPI 3 / Swagger y comunicación fluida entre módulos (Sección 5).
6. ✅ **Seguridad y Privacidad:** Roles RBAC activos, sesiones anónimas y no almacenamiento indebido de datos sensibles (RNF-06).
7. ✅ **Entregables de Ingeniería:** Código fuente completo, tests con 100% de éxito, guías de despliegue y manuales de administración.

---

## 8. Condiciones de Entrega, Garantía y Soporte Posterior

* **Propiedad Intelectual:** El 100% de los derechos patrimoniales sobre el código fuente, bases de datos, scripts y documentación técnica desarrollada pertenecerán exclusivamente al proyecto TransLúcidas y su entidad titular.
* **Período de Garantía Técnica:** **90 días calendario** posteriores a la puesta en marcha para corrección de bugs o inconsistencias funcionales sin costo adicional.
* **Propuesta de Soporte y Mantenimiento Posterior (Opcional):**
  * **Tarifa mensual sugerida:** **$1.800.000 COP/mes**.
  * **Cobertura:** Monitoreo preventivo 24/7, actualización de dependencias, auditoría mensual de embeddings, soporte ante cambios en APIs de IA y backups de bases de datos.

---

## 9. Esquema de Facturación e Hitos de Pago

Para garantizar el flujo de trabajo continuo y la mitigación de riesgos para ambas partes, se propone el siguiente esquema de desembolsos por hitos:

| Hito de Pago | Porcentaje | Entregable Clave Vinculado |
| :---: | :---: | :--- |
| **Hito 1 (Anticipo)** | **35%** | Acta de inicio, documento de arquitectura técnica y configuración del entorno base. |
| **Hito 2 (Entrega Módulo 1 & CMS)** | **30%** | Portal web de autocuidado, catálogo de recursos y panel CMS funcional probado. |
| **Hito 3 (Entrega Módulo 2 & RAG)** | **20%** | Asistente conversacional RAG, base de conocimiento vectorizada y tarjeta de crisis activa. |
| **Hito 4 (Puesta en Marcha Final)** | **15%** | Prototipo de Alexia integrado, despliegue en producción, entrega de manuales y código fuente. |

---

*Propuesta elaborada con los más altos estándares de calidad, accesibilidad y compromiso con la comunidad TransLúcidas.*
