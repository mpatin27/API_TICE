from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from datetime import datetime
from typing import Optional, Dict
import secrets

DATABASE_URL = "postgresql+psycopg2://admin_tice:PatinM_LPOFrancois1er_2026!@db:5432/bdd_tice"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class LogDB(Base):
    __tablename__ = "historique"
    id = Column(Integer, primary_key=True, index=True)
    date_action = Column(DateTime, default=datetime.now)
    outil = Column(String, index=True)
    poste = Column(String, index=True)
    action = Column(String)
    statut = Column(String)
    details = Column(JSON, nullable=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Serveur Central TICE")
security = HTTPBasic()

# --- SYSTÈME DE SÉCURITÉ ---
def verifier_admin(credentials: HTTPBasicCredentials = Depends(security)):
    # Tes identifiants d'accès (à modifier selon tes préférences)
    bon_utilisateur = secrets.compare_digest(credentials.username, "admin")
    bon_mot_de_passe = secrets.compare_digest(credentials.password, "Tice2026!")
    
    if not (bon_utilisateur and bon_mot_de_passe):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

class ActionLog(BaseModel):
    outil: str
    poste: str
    action: str
    statut: str
    details: Optional[Dict] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROUTES PUBLIQUES ---

@app.get("/")
def read_root():
    return {"message": "Serveur TICE en ligne"}

# Les utilitaires locaux postent ici sans mot de passe
@app.post("/api/historique")
def log_action(log: ActionLog, db: Session = Depends(get_db)):
    nouveau_log = LogDB(outil=log.outil, poste=log.poste, action=log.action, statut=log.statut, details=log.details)
    db.add(nouveau_log)
    db.commit()
    db.refresh(nouveau_log)
    return {"status": "success", "id": nouveau_log.id}

# --- ROUTES PROTÉGÉES (Nécessitent la connexion) ---

@app.get("/api/historique")
def lire_historique(db: Session = Depends(get_db), admin: str = Depends(verifier_admin)):
    return db.query(LogDB).order_by(LogDB.date_action.desc()).limit(100).all()

@app.delete("/api/historique/{log_id}")
def supprimer_log(log_id: int, db: Session = Depends(get_db), admin: str = Depends(verifier_admin)):
    log = db.query(LogDB).filter(LogDB.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log introuvable")
    db.delete(log)
    db.commit()
    return {"status": "success"}

@app.get("/dashboard")
def afficher_dashboard(admin: str = Depends(verifier_admin)):
    return FileResponse("static/index.html")