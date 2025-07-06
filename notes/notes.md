Lancer le projet

mkdir volumes\ollama_data
mkdir volumes\shared_data
mkdir volumes\chroma_db
mkdir volumes\n8n_data

icacls volumes /grant "Tout le monde":F /T


docker-compose build backend
docker-compose up

pour indexer:
docker exec project-backend-1 find /app/shared_data -type f -regex ".*\.\(pdf\|txt\|md\|cs\)$"
docker exec project-backend-1 find /app/shared_data -type f -name "*.pdf" -o -name "*.txt" -o -name "*.md" -o -name "*.cs"

download models
docker exec -it ollama-1 ollama pull llama3:70b
docker exec -it project-ollama-1 ollama pull llama3.2:1b

lister models
docker exec project-ollama-1 ollama list

delete model
docker exec project-ollama-1 ollama rm llama3.2:1b


Accédez à l’interface : http://localhost:8501

Accédez à n8n : http://localhost:5678


# Recherche récursive avec parenthèses (RECOMMANDÉE)
docker exec project-backend-1 find /app/shared_data -type f `( -name "*.pdf" -o -name "*.txt" -o -name "*.md" -o -name "*.cs" `) -ls

# Compter les fichiers
(docker exec project-backend-1 bash -c "find /app/shared_data -type f \( -name '*.pdf' -o -name '*.txt' -o -name '*.md' -o -name '*.cs' \)").Count


 Importer un workflow n8n
Dans n8n, cliquez sur "Import" et collez ce JSON :

{
  "nodes": [
    {
      "parameters": {
        "url": "http://ollama:11434/api/generate",
        "method": "POST",
        "jsonParameters": true,
        "options": {},
        "bodyParametersJson": "{\"model\": \"llama3\", \"prompt\": \"Explique le fonctionnement d'un transformeur\", \"stream\": false}"
      },
      "name": "Appel Ollama",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [450, 300]
    }
  ],
  "connections": {}
}



Conseils d’archivage et maintenance
Archivez régulièrement le dossier shared_data/ (zip ou git)
Ajoutez un script de nettoyage automatique si besoin
Utilisez des volumes Docker pour la persistance



Prochaines étapes possibles
Connexion à Freshdesk via API
Ajout d’un système d’authentification
Déploiement sur Kubernetes





