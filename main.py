from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="API Lycée François 1er")

# Modèle de données attendu par l'API
class ActionLog(BaseModel):
    outil: str      # ex: "Reset_ACL"
    poste: str      # ex: "Prof-104"
    action: str     # ex: "Réinitialisation MDP"
    statut: str     # ex: "Succès"

@app.get("/")
def read_root():
    return {"message": "API TICE en ligne et prête à recevoir des requêtes !"}

@app.post("/api/historique")
def log_action(log: ActionLog):
    # Pour l'instant, on l'affiche juste dans la console du serveur.
    # Plus tard, on insérera ces données dans la base PostgreSQL !
    print(f"[{log.poste}] {log.outil} - {log.action} : {log.statut}")
    
    return {"status": "success", "message": "Action enregistrée dans l'historique"}