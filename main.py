from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from datetime import datetime
from fastapi.responses import FileResponse

# 1. Configuration de la connexion à PostgreSQL
DATABASE_URL = "postgresql+psycopg2://admin_tice:PatinM_LPOFrancois1er_2026!@db:5432/bdd_tice"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Définition de la structure de la table "historique" en BDD
class LogDB(Base):
    __tablename__ = "historique"
    id = Column(Integer, primary_key=True, index=True)
    date_action = Column(DateTime, default=datetime.now)
    outil = Column(String, index=True)
    poste = Column(String, index=True)
    action = Column(String)
    statut = Column(String)

# 3. Création automatique de la table au démarrage si elle n'existe pas
Base.metadata.create_all(bind=engine)

# 4. Initialisation de l'API
app = FastAPI(title="API Lycée François 1er")

# Modèle des données reçues par la requête
class ActionLog(BaseModel):
    outil: str
    poste: str
    action: str
    statut: str

# Fonction pour ouvrir et fermer proprement la connexion à chaque requête
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "API TICE en ligne et connectée à PostgreSQL ! Au travail !"}

@app.post("/api/historique")
def log_action(log: ActionLog, db: Session = Depends(get_db)):
    # Création de la ligne à insérer
    nouveau_log = LogDB(
        outil=log.outil,
        poste=log.poste,
        action=log.action,
        statut=log.statut
    )
    
    # Sauvegarde dans la base de données
    db.add(nouveau_log)
    db.commit()
    db.refresh(nouveau_log) # Pour récupérer l'ID auto-généré
    
    print(f"Log enregistré en BDD avec l'ID : {nouveau_log.id}")
    return {"status": "success", "message": "Action sauvegardée en BDD", "id": nouveau_log.id}

@app.get("/api/historique")
def lire_historique(db: Session = Depends(get_db)):
    # Récupère les 50 derniers logs par ordre décroissant
    logs = db.query(LogDB).order_by(LogDB.date_action.desc()).limit(50).all()
    return logs

@app.get("/dashboard")
def afficher_dashboard():
    return FileResponse("static/index.html")