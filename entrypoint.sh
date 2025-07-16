#!/bin/bash
set -e

echo "🔄 Running database migrations..."
python manage.py migrate

echo "🚀 Starting Streamlit app..."
exec poetry run streamlit run app/ui/app_streamlit.py --server.port=8501 --server.address=0.0.0.0