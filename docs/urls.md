# 🔗 Accesos Directos y URLs del Proyecto LXIA Backend

Este documento contiene los enlaces directos tanto para el entorno **Local** como para el entorno **Remoto (Render)**, permitiendo abrirlos directamente en el navegador con un solo clic.

---

## 💻 1. Ambiente Local (Desarrollo)

> **Base URL:** `http://localhost:8000`  
> *(Asegúrate de que el servidor esté corriendo con `python manage.py runserver`)*

### 🛠️ Administración y Documentación Interactiva
* [Django Admin Panel (Local)](http://localhost:8000/admin/) — Panel administrativo de Django.
* [Swagger UI Docs (Local)](http://localhost:8000/api/docs/) — Interfaz interactiva de Swagger para probar endpoints de Módulos 1, 2 y 3.
* [ReDoc UI Docs (Local)](http://localhost:8000/api/redoc/) — Especificación técnica legible de la API.
* [OpenAPI 3.0 Schema (Local)](http://localhost:8000/api/schema/) — Descarga del esquema OpenAPI en formato YAML/JSON.

### 🔐 Módulo 1: Autenticación y Usuarios
* [API Auth Users List (Local)](http://localhost:8000/api/v1/auth/users/) — Listado y gestión de usuarios (requiere Token Superadmin).
* [API Auth Me (Local)](http://localhost:8000/api/v1/auth/me/) — Perfil del usuario en sesión.
* [API Auth Login (Local)](http://localhost:8000/api/v1/auth/login/) — Endpoint POST para inicio de sesión.
* [API Auth Change Password (Local)](http://localhost:8000/api/v1/auth/change-password/) — Endpoint POST para cambio de contraseña.
* [API Auth Logout (Local)](http://localhost:8000/api/v1/auth/logout/) — Endpoint POST para revocación de sesión.

### 🌐 Módulo 2: Portal Web Público (Autocuidado)
* [API Categorías Activas (Local)](http://localhost:8000/api/v1/content/categories/) — Categorías para el menú del portal.
* [API Artículos Publicados (Local)](http://localhost:8000/api/v1/content/articles/) — Artículos públicos optimizados para redes móviles.
* [API Recursos Descargables (Local)](http://localhost:8000/api/v1/content/resources/) — Directorio de guías, infografías y enlaces.
* [API Etiquetas (Local)](http://localhost:8000/api/v1/content/tags/) — Clasificación transversal de temas.

### ✍️ Módulo 2: CMS Administrativo (Content Manager / Superadmin)
* [API CMS Gestión de Artículos (Local)](http://localhost:8000/api/v1/content/manage/articles/) — CRUD completo de borradores, publicación y archivo.

### 🤖 Módulo 3: Asistente Conversacional & Alexia (Público / Anónimo)
* [API Chat Message (Local)](http://localhost:8000/api/v1/chat/message/) — Endpoint POST para consultas RAG fundamentadas con citas bibliográficas.
* [API Alexia Avatar Interact (Local)](http://localhost:8000/api/v1/alexia/interact/) — Endpoint POST dedicado para el Avatar Alexia (metadatos fonéticos TTS y emociones visuales).

### 📚 Módulo 3: Base de Conocimiento RAG & Webhook Serverless (Investigador / Superadmin)
* [API Documentos de Conocimiento (Local)](http://localhost:8000/api/v1/knowledge/documents/) — Listado y registro de documentos con URL de Firebase (0 MB en Render).
* [API Búsqueda Vectorial de Prueba (Local)](http://localhost:8000/api/v1/knowledge/test-search/) — Endpoint POST para auditar similitud de coseno en vivo.
* [API Webhook Cloud Function (Local)](http://localhost:8000/api/v1/knowledge/webhook/document-extracted/) — Receptor seguro con `X-Webhook-Secret` para Firebase Cloud Functions.

#### 👤 Credenciales Iniciales (Local)
* **Usuario:** `admin`
* **Contraseña:** `AdminPassword2026!`
* **Email:** `admin@lxia.org`

---

## ☁️ 2. Ambiente Remoto (Producción - Render)

> **Base URL:** `https://lxia-be.onrender.com`  
> *(Sujeto al despliegue activo en Render)*

### 🛠️ Administración y Documentación Interactiva
* [Django Admin Panel (Remoto)](https://lxia-be.onrender.com/admin/)
* [Swagger UI Docs (Remoto)](https://lxia-be.onrender.com/api/docs/)
* [ReDoc UI Docs (Remoto)](https://lxia-be.onrender.com/api/redoc/)
* [OpenAPI 3.0 Schema (Remoto)](https://lxia-be.onrender.com/api/schema/)

### 🔐 Módulo 1: Autenticación y Usuarios
* [API Auth Users List (Remoto)](https://lxia-be.onrender.com/api/v1/auth/users/)
* [API Auth Me (Remoto)](https://lxia-be.onrender.com/api/v1/auth/me/)
* [API Auth Login (Remoto)](https://lxia-be.onrender.com/api/v1/auth/login/)
* [API Auth Change Password (Remoto)](https://lxia-be.onrender.com/api/v1/auth/change-password/)
* [API Auth Logout (Remoto)](https://lxia-be.onrender.com/api/v1/auth/logout/)

### 🌐 Módulo 2: Portal Web Público
* [API Categorías Activas (Remoto)](https://lxia-be.onrender.com/api/v1/content/categories/)
* [API Artículos Publicados (Remoto)](https://lxia-be.onrender.com/api/v1/content/articles/)
* [API Recursos Descargables (Remoto)](https://lxia-be.onrender.com/api/v1/content/resources/)
* [API Etiquetas (Remoto)](https://lxia-be.onrender.com/api/v1/content/tags/)

### ✍️ Módulo 2: CMS Administrativo
* [API CMS Gestión de Artículos (Remoto)](https://lxia-be.onrender.com/api/v1/content/manage/articles/)

### 🤖 Módulo 3: Asistente Conversacional & Alexia
* [API Chat Message (Remoto)](https://lxia-be.onrender.com/api/v1/chat/message/)
* [API Alexia Avatar Interact (Remoto)](https://lxia-be.onrender.com/api/v1/alexia/interact/)

### 📚 Módulo 3: Base de Conocimiento RAG & Webhook Serverless
* [API Documentos de Conocimiento (Remoto)](https://lxia-be.onrender.com/api/v1/knowledge/documents/)
* [API Búsqueda Vectorial de Prueba (Remoto)](https://lxia-be.onrender.com/api/v1/knowledge/test-search/)
* [API Webhook Cloud Function (Remoto)](https://lxia-be.onrender.com/api/v1/knowledge/webhook/document-extracted/)

#### 👤 Credenciales Iniciales (Remoto)
* Configuradas vía variables de entorno en el panel de Render:
  * `DJANGO_SUPERUSER_USERNAME`
  * `DJANGO_SUPERUSER_PASSWORD`
  * `DJANGO_SUPERUSER_EMAIL`

---

## 📮 3. Espacio de Trabajo Postman

* **Workspace:** `lxia_be`
* **Colección:** `LXIA - Backend API (Módulos 1, 2 y 3)`
* **Total de Carpetas:** 7
  * `1. Autenticación y Sesiones (Módulo 1)`
  * `2. Gestión de Usuarios y Roles (Módulo 1)`
  * `3. Casos Borde y Seguridad (Módulo 1)`
  * `4. Portal Web - Contenidos Públicos (Módulo 2)`
  * `5. CMS - Administración de Contenidos (Módulo 2)`
  * `6. RAG - Asistente Conversacional & Alexia (Módulo 3)`
  * `7. RAG - Base de Conocimiento & Webhooks (Módulo 3)`
* **Entornos disponibles:**
  * `local` (`base_url: http://localhost:8000`)
  * `remoto` (`base_url: https://lxia-be.onrender.com`)
