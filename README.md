
### TODO
- remove duplicate
- add freshdesk data
- split qa service
- slipt main (routes)
- .config || .env > edit exe_change.bat
- create install.bat
- fix frontend endpoints/display
- better health check
- list files


### 📋 Prérequis
- Docker Desktop avec WSL2 activé
- Windows 10/11 avec permissions administrateur

## 🔧 Installation Complète

### 1. Création des Dossiers Volumes
```batch
mkdir volumes\ollama_data
mkdir volumes\shared_data\documents
mkdir volumes\shared_data\chroma_db
mkdir volumes\chroma_db
mkdir volumes\n8n_data

icacls volumes /grant "Tout le monde":F /T
```

### 2. ⚠️ Setup Ollama 
```batch
REM Démarrage initial
docker-compose up -d

REM ⚠️ ÉTAPE CRITIQUE : Forcer la synchronisation volume
docker-compose stop ollama
docker rm -f project-ollama-1
rmdir /s /q volumes\ollama_data
mkdir volumes\ollama_data
docker-compose up -d ollama

REM Attendre le démarrage complet
timeout /t 60

REM Télécharger le modèle dans le volume synchronisé
exe_change_ollama_model.bat
```

### 3. ✅ Vérification Obligatoire
```batch
REM Le modèle doit être visible
docker exec project-ollama-1 ollama list

REM Le dossier Windows DOIT contenir des fichiers (pas juste 468 octets)
dir volumes\ollama_data /s

REM Test de persistance
docker-compose restart ollama
timeout /t 30
docker exec project-ollama-1 ollama list
```

### '4'. Build et Démarrage Final
```batch
REM Build backend avec la correction
docker-compose build backend
docker-compose up -d

REM Ajouter un document test
echo "Document de test pour RAG" > volumes\shared_data\test.txt
```

## 📊 Accès aux Services

- **Interface RAG** : http://localhost:8501
- **Backend API** : http://localhost:8000/health
- **Ollama API** : http://localhost:11434/api/tags
- **n8n Workflows** : http://localhost:5678

## 🔍 Tests et Diagnostic

### Test Complet du Système
```batch
REM 1. Santé des services
docker-compose ps

REM 2. Modèle Ollama présent et persistant
docker exec project-ollama-1 ollama list
dir volumes\ollama_data /s

REM 3. Backend accessible
curl http://localhost:8000/health

REM 4. Test question simple
curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d "{\"question\":\"Hello\"}"
```

### Diagnostic si Problème
```batch
REM Logs des services
docker logs project-backend-1
docker logs project-ollama-1
docker logs project-ui-1

REM Vérifier connectivité Ollama depuis backend
docker exec project-backend-1 curl http://ollama:11434/api/tags

REM Vérifier les volumes
docker inspect project-ollama-1 --format="{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}"
```

## 🔧 Développement (Build Safe)

```batch
REM ✅ Build backend seulement (préserve Ollama)
docker-compose build backend
docker-compose up -d backend

REM ✅ Build UI seulement
docker-compose build ui
docker-compose up -d ui

REM ❌ ÉVITER : docker-compose build (rebuild tout)
REM ❌ ÉVITER : docker-compose down (détruit les conteneurs)
```


## 🚨 Problèmes Connus et Solutions

### 1. Volume Ollama vide mais modèle présent
**Symptôme :**
```batch
docker exec project-ollama-1 ollama list  REM → llama3.2:1b présent
dir volumes\ollama_data /s                REM → Seulement 468 octets
```

**Solution :**
```batch
docker-compose stop ollama
docker rm -f project-ollama-1
rmdir /s /q volumes\ollama_data && mkdir volumes\ollama_data
docker-compose up -d ollama
docker exec -it project-ollama-1 ollama pull llama3.2:1b
```

### 2. Backend erreur "Backend not ready"
**Causes possibles :**
- Modèle Ollama non disponible
- Mauvais nom de modèle dans `rag_server.py`
- Aucun document dans `shared_data/`

**Diagnostic :**
```batch
REM Vérifier modèle disponible
docker exec project-ollama-1 ollama list

REM Vérifier connectivité
curl http://localhost:11434/api/tags

REM Vérifier documents
dir volumes\shared_data

REM Logs backend pour erreur détaillée
docker logs project-backend-1
```

### 3. Interface Streamlit ne charge pas
**Vérifications :**
```batch
REM Service UI actif
docker-compose ps ui

REM Logs UI
docker logs project-ui-1

REM Port accessible
curl http://localhost:8501
```

## 🔄 Workflow n8n

Dans n8n (http://localhost:5678), cliquer sur "Import" et coller :

```json
{
  "nodes": [
    {
      "parameters": {
        "url": "http://ollama:11434/api/generate",
        "method": "POST",
        "jsonParameters": true,
        "bodyParametersJson": "{\"model\": \"llama3.2:1b\", \"prompt\": \"{{$json.question}}\", \"stream\": false}"
      },
      "name": "Ollama API",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [450, 300]
    }
  ],
  "connections": {}
}
```

## 📋 Checklist Post-Setup

- [ ] Services actifs : `docker-compose ps`
- [ ] Modèle Ollama : `docker exec project-ollama-1 ollama list` → llama3.2:1b visible
- [ ] Volume persistant : `dir volumes\ollama_data /s` → Contient des fichiers (> 1MB)
- [ ] Backend accessible : `curl http://localhost:8000/health` → status: ok
- [ ] Interface accessible : http://localhost:8501
- [ ] Test persistance : `docker-compose restart ollama` → modèle toujours présent
- [ ] Document test : `echo "Test" > volumes\shared_data\test.txt`

## 📞 Dépannage Avancé

### Reset Complet
```batch
docker-compose down
docker system prune -f
rmdir /s /q volumes
mkdir volumes\ollama_data volumes\shared_data volumes\chroma_db volumes\n8n_data
icacls volumes /grant "Tout le monde":F /T
docker-compose up -d
REM Puis refaire le setup Ollama
```

### Sauvegarde
```batch
REM Sauvegarde complète
xcopy volumes volumes_backup /E /H /Y

REM Sauvegarde modèle seulement
xcopy volumes\ollama_data ollama_backup /E /H /Y
```

## 🚀 Prochaines Étapes

- [ ] **Connexion Freshdesk API** - Intégration tickets support
- [ ] **Authentification** - Système utilisateurs
- [ ] **Monitoring** - Logs et métriques
- [ ] **Déploiement** - Production avec Docker Swarm/Kubernetes
- [ ] **Optimisation** - Cache et performance

## 📈 Maintenance

```batch
REM Nettoyage périodique
docker system prune -f

REM Mise à jour modèles
docker exec project-ollama-1 ollama pull llama3.2:1b

REM Backup automatique (à automatiser)
xcopy volumes volumes_backup_%date% /E /H /Y
```

---

## ⚡ Démarrage Rapide

```batch
REM Setup rapide complet
git clone [votre-repo]
cd project
mkdir volumes\ollama_data volumes\shared_data volumes\chroma_db volumes\n8n_data
icacls volumes /grant "Tout le monde":F /T
docker-compose up -d
docker-compose stop ollama && docker rm -f project-ollama-1
rmdir /s /q volumes\ollama_data && mkdir volumes\ollama_data
docker-compose up -d ollama
timeout /t 60
docker exec -it project-ollama-1 ollama pull llama3.2:1b
docker-compose build backend && docker-compose up -d
echo "Test RAG" > volumes\shared_data\test.txt
echo ✅ Setup terminé - Interface: http://localhost:8501
```