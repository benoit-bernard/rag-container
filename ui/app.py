import os
import streamlit as st
import requests
import time

# ✅ URLs configurables via variables d'environnement
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
N8N_URL = os.getenv("N8N_URL", "http://n8n:5678")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")

st.set_page_config(page_title="RAG Assistant", layout="wide")
st.title("🤖 Assistant IA - Support Technique")

if "history" not in st.session_state:
    st.session_state.history = []

question = st.text_input("Posez votre question technique ici :", "")


# ✅ BOUTON PRINCIPAL POUR QUESTIONS
if st.button("🤖 ask RAG") and question:
    with st.spinner("Traitement en cours..."):
        progress = st.progress(0)
        log = st.empty()
        try:
            st.info(f"Envoi vers RAG: {BACKEND_URL}/ask")
             
            for i in range(5):
                time.sleep(0.3)
                progress.progress((i + 1) * 20)
                log.text(f"Étape {i+1}/5 : traitement en cours...")

            # ✅ Appel au backend RAG
            response = requests.post(
                f"{BACKEND_URL}/ask", 
                json={"question": question}, 
                timeout=120
            )

            st.write(f"**Status Code:** {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "Pas de réponse reçue")
                st.session_state.history.append((question, f"[RAG] {answer}"))
                st.success("✅ Réponse reçue du RAG")
                st.write(f"**Réponse complète:** {answer}")
            else:
                st.error(f"❌ Erreur RAG: {response.status_code}")
                st.error(f"**Response:** {response.text}")
    
        except Exception as e:
            st.error(f"❌ Erreur RAG: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
        finally:
            progress.empty()
            log.empty()

# ✅ BOUTON OPTIONNEL POUR N8N
if st.button("send to n8n") and question:
    try:
        n8n_urls = [
            f"{N8N_URL}/webhook/ask",           # URL standard
            f"{N8N_URL}/webhook-test/ask",      # URL de test
            "http://localhost:5678/webhook/ask", # URL directe (fallback)
        ]
        response = None
        error_messages = []
        
        for url in n8n_urls:
            try:
                st.info(f"Tentative: {url}")
                response = requests.post(url, json={"question": question}, timeout=30)
                if response.status_code == 200:
                    answer = response.json().get("answer", "Pas de réponse reçue")
                    st.session_state.history.append((question, f"[n8n] {answer}"))
                    st.success(f"✅ Réponse reçue de n8n via {url}")
                    break
                else:
                    error_messages.append(f"{url}: {response.status_code}")
            except Exception as e:
                error_messages.append(f"{url}: {str(e)}")
        
        if not response or response.status_code != 200:
            st.error(f"❌ Toutes les tentatives n8n ont échoué:\n" + "\n".join(error_messages))
            
    except Exception as e:
        st.error(f"❌ Erreur générale n8n: {str(e)}")


# Historique
if st.session_state.history:
    st.markdown("---")
    st.subheader("📜 Historique des Conversations")
    for i, item in enumerate(reversed(st.session_state.history)):
        q, a = item
        with st.expander(f"💬 Question {len(st.session_state.history) - i}"):
            st.markdown(f"**🧑 Question :** {q}")
            st.markdown(f"**🤖 Réponse :** {a}")

st.markdown("----")
st.markdown("### 🔄 Maintenance et Debug")

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

with col1:
    if st.button("🔁 Recharger l'index RAG"):
        with st.spinner("Rechargement en cours..."):
            progress = st.progress(0)
            log = st.empty()
            try:
                st.info(f"Envoi vers RAG: {BACKEND_URL}/ask")
                 
                for i in range(5):
                    time.sleep(0.3)
                    progress.progress((i + 1) * 20)
                    log.text(f"Étape {i+1}/5 : traitement en cours...")

                reload_response = requests.post(f"{BACKEND_URL}/reload", timeout=240)

                st.write(f"**Status Code:** {response.status_code}")

                if reload_response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "Pas de réponse reçue")
                    st.session_state.history.append((question, f"[RAG] {answer}"))
                    st.success("✅ Réponse reçue du RAG")
                    st.write(f"**Réponse complète:** {answer}")
                else:
                    st.error(f"❌ Erreur RAG: {response.status_code}")
                    st.error(f"**Response:** {response.text}")
        
            except Exception as e:
                st.error(f"❌ Erreur RAG: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
            finally:
                progress.empty()
                log.empty()

with col2:
    if st.button("📊 Statut des Services"):
        # ✅ Utiliser les noms de services Docker depuis le conteneur
        services = {
            "Backend RAG": f"{BACKEND_URL}/health",
            "n8n": N8N_URL,
            "Ollama": f"{OLLAMA_URL}/api/tags"
        }
        
        for service, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    st.success(f"✅ {service}: OK")
                else:
                    st.warning(f"⚠️ {service}: {response.status_code}")
            except:
                st.error(f"❌ {service}: Inaccessible")

with col3:
    if st.button("🗑️ Vider l'historique"):
        st.session_state.history = []
        st.success("✅ Historique vidé")

with col1:
    if st.button("🔍 Debug2 Backend"):
        try:
            debug_response = requests.get(f"{BACKEND_URL}/debug2", timeout=10)
            if debug_response.status_code == 200:
                debug_data = debug_response.json()
                
                st.subheader("📊 État du Backend")
                st.json(debug_data)
                
                # Affichage formaté
                st.write("**📁 Fichiers trouvés:**")
                if debug_data.get("files_found"):
                    for file_info in debug_data["files_found"]:
                        st.write(f"- {file_info['path']} ({file_info['size']} bytes)")
                else:
                    st.error("❌ Aucun fichier trouvé dans shared_data")
                
                st.write("**🗃️ Index ChromaDB:**")
                if debug_data.get("chroma_db_files"):
                    st.success(f"✅ {len(debug_data['chroma_db_files'])} fichiers d'index")
                else:
                    st.warning("⚠️ Aucun fichier d'index trouvé")
                    
            else:
                st.error(f"❌ Debug failed: {debug_response.status_code}")
        except Exception as e:
            st.error(f"❌ Erreur debug: {str(e)}")

with col4:
    if st.button("🔍 Debug Backend"):
        try:
            debug_response = requests.get(f"{BACKEND_URL}/debug", timeout=10)
            if debug_response.status_code == 200:
                debug_data = debug_response.json()
                
                st.subheader("📊 État du Backend")
                
                # ✅ Affichage formaté des informations importantes
                col_info1, col_info2 = st.columns(2)
                
                with col_info1:
                    st.metric("📁 Fichiers trouvés", debug_data.get("total_files", 0))
                    st.metric("🗃️ QA Chain", "✅ Prêt" if debug_data.get("qa_chain_ready") else "❌ Non prêt")
                
                with col_info2:
                    st.metric("📊 Taille totale", f"{debug_data.get('total_size', 0):,} bytes")
                    st.metric("💾 ChromaDB", "✅ Existe" if debug_data.get("chroma_db_exists") else "❌ Absent")
                
                # Affichage détaillé des fichiers
                if debug_data.get("files_found"):
                    with st.expander("📄 Détails des fichiers"):
                        for file_info in debug_data["files_found"]:
                            if "error" in file_info:
                                st.error(f"❌ {file_info['name']}: {file_info['error']}")
                            else:
                                st.write(f"✅ {file_info['name']} ({file_info['size']:,} bytes)")
                else:
                    st.error("❌ Aucun fichier trouvé dans shared_data")
                
                # JSON complet
                with st.expander("🔍 Debug JSON complet"):
                    st.json(debug_data)
                    
            else:
                st.error(f"❌ Debug failed: {debug_response.status_code}")
        except Exception as e:
            st.error(f"❌ Erreur debug: {str(e)}")

with col2:
    if st.button("🤖 Test Ollama Direct"):
        try:
            test_response = requests.post(f"{BACKEND_URL}/test-simple", timeout=30)
            if test_response.status_code == 200:
                test_data = test_response.json()
                if test_data["status"] == "ok":
                    st.success("✅ Ollama fonctionne")
                    st.write(f"Réponse: {test_data['response']}")
                else:
                    st.error(f"❌ Erreur Ollama: {test_data['error']}")
            else:
                st.error(f"❌ Test Ollama failed: {test_response.status_code}")
        except Exception as e:
            st.error(f"❌ Erreur test Ollama: {str(e)}")

with col6:
    if st.button("📋 Status Fichiers"):
        try:
            files_response = requests.get(f"{BACKEND_URL}/files-status", timeout=10)
            if files_response.status_code == 200:
                files_data = files_response.json()
                
                st.subheader("📁 Status des Fichiers")
                
                col_files1, col_files2 = st.columns(2)
                
                with col_files1:
                    st.metric("📄 Total fichiers", files_data.get("total_files", 0))
                    st.metric("🆕 Nouveaux", len(files_data.get("changes", {}).get("new_files", [])))
                
                with col_files2:
                    st.metric("📝 Modifiés", len(files_data.get("changes", {}).get("modified_files", [])))
                    st.metric("🗑️ Supprimés", len(files_data.get("changes", {}).get("deleted_files", [])))
                
                # Recommandation
                recommendation = files_data.get("recommendation", "unknown")
                if recommendation == "index_up_to_date":
                    st.success("✅ Index à jour")
                elif recommendation == "reindex_needed":
                    st.warning("⚠️ Réindexation recommandée")
                else:
                    st.info(f"ℹ️ Status: {recommendation}")
                
                # Détails des changements
                changes = files_data.get("changes", {})
                if changes.get("new_files") or changes.get("modified_files"):
                    with st.expander("🔄 Détails des changements"):
                        for new_file in changes.get("new_files", []):
                            st.success(f"➕ Nouveau: {new_file['path']}")
                        
                        for mod_file in changes.get("modified_files", []):
                            st.warning(f"📝 Modifié: {mod_file['path']}")
                
            else:
                st.error(f"❌ Status fichiers failed: {files_response.status_code}")
        except Exception as e:
            st.error(f"❌ Erreur status fichiers: {str(e)}")


# Zone de debug
with st.expander("🔍 Debug Information"):
    st.code(f"""
Variables d'environnement:
- BACKEND_URL: {BACKEND_URL}
- N8N_URL: {N8N_URL}
- OLLAMA_URL: {OLLAMA_URL}

Services URLs (depuis conteneur UI):
- Backend RAG: {BACKEND_URL}
- n8n API: {N8N_URL}
- Ollama API: {OLLAMA_URL}

Services URLs (depuis Windows):
- Interface: http://localhost:8501
- Backend: http://localhost:8000
- n8n: http://localhost:5678
- Ollama: http://localhost:11434
    """)



# ✅ FOOTER
st.markdown("---")
st.markdown("*🤖 Assistant IA RAG - Interface Streamlit*")