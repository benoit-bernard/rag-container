@echo off
title Changement Modèle Ollama automatique
echo.
echo 🔄 CHANGEMENT DE MODÈLE OLLAMA AUTO
echo ==============================

echo Modèles disponibles:
echo 1. llama3.2:1b (très rapide / proto) - vram: 3 go / ram: 4 go
echo 2. llama3:70b (très lent, très performant) - vram 48-64go / ram : 128 go
echo 3. llama3.1:8b (équilibré) - vram 12go / ram: 16 go
echo 4. Mistral 7b (léger, rapide et bon sur doc technique) - vram: 10gp/ ram 16go / hd 10 go
echo 5. Nous-Hermes 2 (basé sur mistral Doc technique, QA, peu hallucinatoire) - vram: 10gp/ ram 16go /hd 10 go
echo 6. CodeLlama 13b (Analyse fine de code, bon compromis - moyennement lent) - vram 22go / ram: 24-32 gp / hd 20 go
echo 7. Code Llama 34b (Ultra-précis pour code, trop lourd localement)- vram 48-64go / ram: 64+ go
echo 8. deepseek 6.7b (léger et rapide) - VRAM: 12go / RAM: 16go / HD: 8go
echo 9. mistral large (123b) - hd: 250 go / ram 128go+ / multigpu obligatoire / cpu threadripper / xeon
echo 10. Personnalisé (https://ollama.com/library)

echo.
set /p choice="Choisissez un modèle (1-10): "

if "%choice%"=="1" set MODEL=llama3.2:1b
if "%choice%"=="2" set MODEL=llama3:70b
if "%choice%"=="3" set MODEL=llama3.1:8b
if "%choice%"=="4" set MODEL=mistral:7b-instruct
if "%choice%"=="5" set MODEL=nous-hermes2:10.7b
if "%choice%"=="6" set MODEL=codellama:13b-instruct
if "%choice%"=="7" set MODEL=codellama:34b-instruct
if "%choice%"=="8" set MODEL=deepseek-coder:6.7b
if "%choice%"=="9" set MODEL=mistral-large:123b
if "%choice%"=="10" (
    set /p MODEL="Entrez le nom du modèle: "
)

if not defined MODEL (
    echo Choix invalide!
    pause
    exit /b
)

echo.
echo 📝 Vérification/Création du fichier .env...
if not exist .env (
    echo Création du fichier .env...
    echo # Configuration RAG> .env
    echo OLLAMA_MODEL=llama3.2:1b>> .env
    echo OLLAMA_API=http://ollama:11434>> .env
    echo BACKEND_URL=http://backend:8000>> .env
    echo N8N_URL=http://n8n:5678>> .env
    echo CHUNK_SIZE=1000>> .env
    echo CHUNK_OVERLAP=200>> .env
    echo RETRIEVAL_K=5>> .env
    echo PERSIST_DIR=shared_data/chroma_db>> .env
    echo EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2>> .env
)

echo Mise à jour du modèle dans .env...
powershell -Command "(Get-Content .env) -replace 'OLLAMA_MODEL=.*', 'OLLAMA_MODEL=%MODEL%' | Set-Content .env"

echo.
echo 📥 Téléchargement du modèle si nécessaire...
docker exec rag-ollama ollama pull %MODEL%

echo.
echo 🔄 Redémarrage du backend...
docker-compose restart backend

echo.
echo ⏳ Attente de l'initialisation (30s)...
timeout /t 30

echo.
echo 🧪 Test du nouveau modèle...
powershell -Command "try { $r = Invoke-RestMethod -Uri 'http://localhost:8000/config' -TimeoutSec 10; Write-Host 'Modèle actif:' $r.ollama_model } catch { Write-Host 'Erreur test' }"

echo.
echo ✅ Changement terminé!
echo    Modèle: %MODEL%
echo    Interface: http://localhost:8501
echo.
pause