#!/bin/sh
set -e

echo "📌 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "📌 Aplicando migraciones de base de datos..."
python manage.py migrate --noinput

echo "📌 Inicializando roles y grupos del sistema..."
python manage.py init_roles

echo "📌 Verificando superusuario administrativo..."
python manage.py setup_admin

echo "📌 Indexando documentos de conocimiento RAG iniciales..."
python manage.py seed_rag_documents

echo "🚀 Iniciando servidor Gunicorn en el puerto ${PORT:-8000}..."
exec gunicorn lxia_be.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
