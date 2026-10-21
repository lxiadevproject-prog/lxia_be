# Documentación del Proyecto LXIA Backend

Este directorio centraliza toda la documentación técnica, arquitectónica y funcional del proyecto LXIA.

---

## 🚀 Estado de Avance de Módulos

| Módulo | Descripción | Estado | Pruebas Unitarias | Documentación |
| :--- | :--- | :---: | :---: | :--- |
| **Módulo 1** | Autenticación, Usuarios y RBAC (Superadmin, Investigador, Gestor) | **100% Completo** | 8/8 superadas | [urls.md](urls.md) |
| **Módulo 2** | Gestión de Contenidos (CMS, Portal Web, Recursos, Métricas de Vistas) | **100% Completo** | 9/9 superadas | [urls.md](urls.md) |
| **Módulo 3** | Asistente Conversacional RAG, Avatar Alexia, Base de Conocimiento y Webhooks | **100% Completo** | 10/10 superadas | [module_3_rag_architecture.md](architecture/module_3_rag_architecture.md) |
| **Total Global** | **Suite completa de pruebas de regresión del backend** | **100% Operativo** | **27/27 superadas** | [urls.md](urls.md) |

---

## Estructura de Carpetas

```
docs/
├── architecture/         # Documentos de arquitectura, decisiones técnicas (ADRs), esquemas de DB
│   └── module_3_rag_architecture.md  # Arquitectura detallada del Motor RAG, Alexia y Webhooks
├── diagrams/             # Diagramas en SVG, PNG, Draw.io o PDF (casos de uso, ER, arquitectura)
├── requirements/         # Requisitos funcionales y no funcionales, historias de usuario
├── urls.md               # Accesos con un solo clic a Swagger UI, Django Admin, ReDoc y endpoints
└── README.md             # Índice y guía general de documentación
```

---

## Secciones Principales

### 1. Arquitectura y Decisiones Técnicas (`architecture/`)
* [Arquitectura y Plan del Módulo 3: Motor RAG y Asistente Conversacional](architecture/module_3_rag_architecture.md)
  * Integración ligera con Firebase Storage (0 MB de ancho de banda en Render).
  * Webhook serverless para futuras Firebase Cloud Functions en GCP.
  * Vectorización y similitud de coseno en PostgreSQL sin dependencias binarias externas.
  * Regla de Prioridad Cero: Detección de crisis y derivación a líneas de ayuda verificadas en Colombia.
  * Soporte específico para el Avatar Alexia (metadatos fonéticos y expresiones).

### 2. Accesos Rápidos y Colección Postman (`urls.md`)
* [Enlaces Directos Local y Remoto](urls.md) — Accesos directos a Swagger UI, Django Admin, ReDoc y endpoints de los Módulos 1, 2 y 3.
* **Postman Collection:** `LXIA - Backend API (Módulos 1, 2 y 3)` sincronizada con 7 carpetas y entornos `local` y `remoto`.
