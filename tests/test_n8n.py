import requests

url = "http://localhost:5678/webhook/ask"  
question = input("Pose ta question : ")

response = requests.post(url, json={"question": question})

if response.status_code == 200:
    print("✅ Réponse :", response.json()["answer"])
else:
    print("❌ Erreur :", response.status_code, response.text)
