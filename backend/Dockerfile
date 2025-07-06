FROM python:3.10-slim

# ✅ MÉTADONNÉES
LABEL maintainer="myself"
LABEL version="1.0.0"
LABEL description="Backend RAG with Langchain, ChromaDB et Ollama"

# ✅ VARIABLES D'ENVIRONNEMENT
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONPATH=/app

# ✅ VARIABLES RAG PAR DÉFAUT
# ENV OLLAMA_MODEL=llama3.2:1b
ENV OLLAMA_API=http://ollama:11434
ENV CHUNK_SIZE=1000
ENV CHUNK_OVERLAP=200
ENV RETRIEVAL_K=5
ENV PERSIST_DIR=shared_data/chroma_db
ENV EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# ✅ DÉPENDANCES SYSTÈME
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# ✅ PROD > CRÉER UTILISATEUR NON-ROOT
#RUN groupadd -r appuser && useradd -r -g appuser appuser

# ✅ CRÉER RÉPERTOIRE DE TRAVAIL
WORKDIR /app

# ✅ COPIER ET INSTALLER LES DÉPENDANCES
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
# prod > RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

# Téléchargement du modèle d'embeddings
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# ✅ COPIER LE CODE
COPY . .

# ✅ PROD > CRÉER LES DOSSIERS NÉCESSAIRES
#RUN mkdir -p shared_data/chroma_db && \
#    chown -R appuser:appuser /app

# ✅ PROD > PASSER À L'UTILISATEUR NON-ROOT
# USER appuser

# ✅ HEALTH CHECK
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--access-log", "--log-level", "info"]
