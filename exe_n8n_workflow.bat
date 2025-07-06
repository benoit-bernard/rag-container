#!/bin/bash
echo "Attente du démarrage de n8n..."
sleep 30

echo "Import du workflow RAG..."
curl -X POST http://localhost:5678/rest/workflows/import \
  -H "Content-Type: application/json" \
  -d @/notes/workflow.json

echo "Activation du workflow..."
curl -X POST http://localhost:5678/rest/workflows/1/activate