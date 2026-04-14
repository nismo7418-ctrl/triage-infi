"""
╔══════════════════════════════════════════════════════════════════════════╗
║              AKIR-IAO PROJECT — v13.0 ELITE EDITION                    ║
║              Développeur exclusif : Ismaïl Ibn-Daïfa                   ║
║              Outil d'aide au triage IAO — FRENCH Triage SFMU V1.1      ║
║              Conformité RGPD : Aucune donnée nominative stockée         ║
╚══════════════════════════════════════════════════════════════════════════╝

Modules :
    - moteur_scores    : Calculs NEWS2, TIMI, Silverman, GCS, Brûlures, etc.
    - moteur_triage    : Algorithme FRENCH Triage SFMU V1.1
    - moteur_sbar      : Génération transmission SBAR DPI-Ready
    - moteur_perfusion : Calculateur débit ml/h et doses de charge
    - alertes          : Cohérence clinique et alertes sécurité
    - ui_composants    : Rendu Streamlit (bandeaux, prescriptions, scores)
"""

import streamlit as st
from datetime import datetime
import json
import os
import uuid

# --- CONFIGURATION ------------------------------------------------------------
st.set_page_config(
    page_title="AKIR-IAO Project",
    page_icon="⚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# RGPD : SYSTÈME DE PERSISTANCE ANONYME (pas de nom/prénom stocké)
# Les patients sont identifiés par un UID anonyme uniquement.
# =============================================================================
PATIENT_DB_FILE = "akir_registry_anon.json"


def load_patient_db():
    """Charge la base de données patients anonymes depuis le fichier JSON local."""
    if os.path.exists(PATIENT_DB_FILE):
        try:
            with open(PATIENT_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_patient_db(patients):
    """Sauvegarde la base de données anonymes dans le fichier JSON local."""
    try:
        with open(PATIENT_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(patients, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def add_patient_to_db(patient_data):
    """Ajoute un patient anonyme à la base. Aucun nom/prénom n'est stocké (RGPD)."""
    db = load_patient_db()
    # RGPD : suppression des données nominatives avant stockage
    patient_data.pop("nom", None)
    patient_data.pop("prenom", None)
    patient_data["uid"] = str(uuid.uuid4())[:8].upper()
    patient_data["saved_at"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    patient_data["saved_date"] = datetime.now().strftime("%Y-%m-%d")
    db.insert(0, patient_data)
    save_patient_db(db)
    return patient_data["uid"]


def delete_patient_from_db(uid):
    """Supprime un patient de la base par son UID anonyme."""
    db = load_patient_db()
    db = [p for p in db if p.get("uid") != uid]
    save_patient_db(db)


def search_patients(query):
    """Recherche dans la base par motif, âge, niveau de tri, date (pas de nom)."""
    db = load_patient_db()
    if not query:
        return db
    q = query.lower().strip()
    results = []
    for p in db:
        # RGPD : recherche uniquement sur les données cliniques anonymes
        searchable = f"{p.get('motif','')} {p.get('age','')} {p.get('niveau','')} {p.get('cat','')} {p.get('saved_at','')}".lower()
        if q in searchable:
            results.append(p)
    return results


# --- CSS CYBERPUNK/MÉDICAL — Optimisé iPhone (one-hand friendly) -------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

/* ── VARIABLES COULEUR ── */
:root {
  --bg-dark:     #0a0f1e;
  --bg-panel:    #0f172a;
  --bg-card:     #020617;
  --border:      #1e3a5f;
  --accent-cyan: #38bdf8;
  --accent-red:  #ef4444;
  --accent-neo:  #ff2255;
  --text-main:   #e2e8f0;
  --text-muted:  #64748b;
  --text-soft:   #94a3b8;
}

html,body,[class*="css"]{font-family:'IBM Plex Sans',sans-serif;}
.stApp{background:var(--bg-dark);color:var(--text-main);}
[data-testid='stSidebar']{background:var(--bg-panel);border-right:1px solid var(--border);}

/* ── SECTION HEADERS ── */
.section-header{
  font-family:'IBM Plex Mono',monospace;color:var(--accent-cyan);font-weight:600;
  font-size:0.75rem;letter-spacing:0.12em;text-transform:uppercase;
  border-bottom:1px solid var(--border);padding-bottom:6px;margin:16px 0 12px 0;
}

/* ── TRIAGE BOXES ── */
.triage-box{border-radius:12px;padding:28px;text-align:center;font-family:'IBM Plex Mono',monospace;margin-bottom:16px;}
.box-M{background:linear-gradient(135deg,#1a0030,#3b0764);border:2px solid #a855f7;}
.box-1{background:linear-gradient(135deg,#450a0a,#7f1d1d);border:2px solid var(--accent-red);}
.box-2{background:linear-gradient(135deg,#431407,#7c2d12);border:2px solid #f97316;}
.box-3A{background:linear-gradient(135deg,#3b1a00,#78350f);border:2px solid #f59e0b;}
.box-3B{background:linear-gradient(135deg,#422006,#713f12);border:2px solid #eab308;}
.box-4{background:linear-gradient(135deg,#052e16,#14532d);border:2px solid #22c55e;}
.box-5{background:linear-gradient(135deg,#0c1a2e,#1e3a5f);border:2px solid #3b82f6;}

@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}
.box-M,.box-1{animation:pulse 1s infinite;}

/* ── NEWS2 BADGES ── */
.news2-badge{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:1.6rem;font-weight:600;padding:6px 18px;border-radius:8px;margin-bottom:4px;}
.news2-low{background:#14532d;color:#86efac;}
.news2-med{background:#713f12;color:#fde68a;}
.news2-high{background:#7f1d1d;color:#fca5a5;}
.news2-crit{background:#4c0519;color:#f9a8d4;animation:pulse 1s infinite;}

/* ── VITAL BADGES ── */
.vital-alert{font-family:'IBM Plex Mono',monospace;font-size:0.65rem;padding:2px 6px;border-radius:4px;margin-left:6px;vertical-align:middle;}
.vital-warn{background:#422006;color:#fbbf24;}
.vital-crit{background:#450a0a;color:#f87171;}
.vital-ok{background:#052e16;color:#4ade80;}

/* ── ALERTE CRITIQUE NEWS2 >= 7 : BANNIÈRE ROUGE CLIGNOTANTE ── */
.critical-alert-banner{
  background:linear-gradient(90deg,#7f0000,#c00020,#7f0000);
  border:3px solid var(--accent-neo);
  border-radius:14px;padding:22px 28px;margin:14px 0;
  text-align:center;
  animation:pulse 0.7s infinite;
  box-shadow:0 0 24px rgba(255,34,85,0.6);
}
.critical-alert-title{
  font-family:'IBM Plex Mono',monospace;font-size:1.25rem;font-weight:700;
  color:#fff;letter-spacing:0.08em;text-shadow:0 0 10px var(--accent-neo);
}
.critical-alert-sub{font-size:0.92rem;color:#fecaca;margin-top:8px;font-weight:600;}

/* ── DANGER / WARNING BANNERS ── */
.danger-banner{background:linear-gradient(90deg,#7f1d1d,#991b1b);border:2px solid var(--accent-red);border-radius:12px;padding:18px 22px;margin:12px 0;text-align:center;animation:pulse 0.8s infinite;}
.danger-banner-title{font-family:'IBM Plex Mono',monospace;font-size:1.1rem;font-weight:700;color:#fca5a5;letter-spacing:0.05em;}
.danger-banner-detail{font-size:0.88rem;color:#fecaca;margin-top:6px;}
.warning-banner{background:linear-gradient(90deg,#78350f,#92400e);border:2px solid #f59e0b;border-radius:12px;padding:14px 20px;margin:10px 0;text-align:center;}
.warning-banner-title{font-family:'IBM Plex Mono',monospace;font-size:0.95rem;font-weight:600;color:#fde68a;}
.warning-banner-detail{font-size:0.82rem;color:#fef3c7;margin-top:4px;}

/* ── PROTOCOLE ANTICIPÉ (Douleur thoracique, etc.) ── */
.protocole-anticipe{
  background:#0c1a30;border:2px solid #1d4ed8;border-left:6px solid #3b82f6;
  border-radius:12px;padding:18px 22px;margin:12px 0;
}
.protocole-anticipe-title{font-family:'IBM Plex Mono',monospace;font-size:0.82rem;color:#60a5fa;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:12px;font-weight:700;}
.protocole-item{font-size:0.88rem;color:#e2e8f0;padding:5px 0;display:flex;align-items:flex-start;gap:10px;}
.protocole-item::before{content:"☐";color:#60a5fa;font-size:0.9rem;flex-shrink:0;}
.protocole-urgent::before{content:"⚡";color:#f59e0b;}

/* ── INFO-BULLES SCORES ── */
.infobulles-score{background:#0f172a;border:1px solid var(--border);border-left:4px solid var(--accent-cyan);border-radius:8px;padding:12px 16px;font-size:0.82rem;color:#93c5fd;line-height:1.6;margin:8px 0;}

/* ── PRESCRIPTIONS ANTICIPÉES ── */
.rx-card{background:#0c1a30;border:1px solid #1e40af;border-left:5px solid #3b82f6;border-radius:10px;padding:16px 20px;margin:10px 0;}
.rx-title{font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#60a5fa;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:10px;}
.rx-item{font-size:0.85rem;color:#e2e8f0;padding:4px 0;display:flex;align-items:flex-start;gap:8px;}
.rx-item::before{content:"☐";color:#60a5fa;font-size:0.9rem;flex-shrink:0;}
.rx-item-urgent::before{content:"⚡";color:#f59e0b;}
.rx-cat{font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#94a3b8;letter-spacing:0.1em;text-transform:uppercase;margin:10px 0 4px 0;padding-top:6px;border-top:1px solid var(--border);}

/* ── SBAR DPI-READY ── */
.sbar-block{background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:18px;font-family:'IBM Plex Mono',monospace;font-size:0.82rem;line-height:1.8;white-space:pre-wrap;color:#cbd5e1;}
.sbar-section{font-family:'IBM Plex Mono',monospace;font-weight:700;font-size:0.9rem;color:var(--accent-cyan);margin-top:10px;}

/* ── CALCULATEUR PERFUSION ── */
.perfusion-card{background:#0f172a;border:1px solid var(--border);border-radius:12px;padding:20px;margin:10px 0;}
.perfusion-result{font-family:'IBM Plex Mono',monospace;font-size:2rem;font-weight:700;color:var(--accent-cyan);text-align:center;margin:10px 0;}
.perfusion-label{font-size:0.75rem;color:var(--text-muted);text-align:center;text-transform:uppercase;letter-spacing:0.1em;}
.dose-card{background:#020617;border:1px solid #1e3a5f;border-left:4px solid #22c55e;border-radius:8px;padding:14px 18px;margin:8px 0;font-size:0.85rem;color:#cbd5e1;}
.dose-title{font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#4ade80;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;}

/* ── SCORES ── */
.score-result{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:1.8rem;font-weight:600;padding:8px 22px;border-radius:8px;margin:8px 0 4px 0;}
.score-low{background:#052e16;color:#86efac;border:1px solid #16a34a;}
.score-med{background:#422006;color:#fde68a;border:1px solid #ca8a04;}
.score-high{background:#450a0a;color:#fca5a5;border:1px solid #dc2626;}
.score-info{background:#0c1a2e;color:#93c5fd;border:1px solid #2563eb;}
.score-interp{font-size:0.85rem;color:#94a3b8;margin-top:6px;line-height:1.6;font-style:italic;}
.score-title{font-family:'IBM Plex Mono',monospace;font-size:0.7rem;font-weight:600;letter-spacing:0.14em;text-transform:uppercase;color:var(--accent-cyan);border-bottom:1px solid var(--border);padding-bottom:6px;margin-bottom:14px;}
.score-row{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--border);padding:5px 0;font-size:0.85rem;}
.score-row:last-child{border-bottom:none;}
.score-row-label{color:#94a3b8;}
.score-row-val{font-family:'IBM Plex Mono',monospace;color:#e2e8f0;font-weight:600;}

/* ── ALERTES ── */
.alert-danger{background:#450a0a;border:1px solid var(--accent-red);border-left:5px solid var(--accent-red);border-radius:8px;padding:14px 16px;margin:8px 0;color:#fca5a5;font-weight:600;font-size:0.9rem;animation:pulse 1.2s infinite;}
.alert-warning{background:#422006;border:1px solid #f97316;border-left:5px solid #f97316;border-radius:8px;padding:12px 16px;margin:6px 0;color:#fdba74;font-size:0.88rem;}
.alert-info{background:#0c1a2e;border:1px solid #3b82f6;border-left:5px solid #3b82f6;border-radius:8px;padding:10px 14px;margin:6px 0;color:#93c5fd;font-size:0.85rem;}

/* ── HISTORIQUE ── */
.hist-row{background:var(--bg-panel);border:1px solid var(--border);border-radius:8px;padding:10px 14px;margin-bottom:6px;font-size:0.85rem;}
.hist-M{border-left:4px solid #a855f7;}.hist-1{border-left:4px solid var(--accent-red);}
.hist-2{border-left:4px solid #f97316;}.hist-3A{border-left:4px solid #f59e0b;}
.hist-3B{border-left:4px solid #eab308;}.hist-4{border-left:4px solid #22c55e;}
.hist-5{border-left:4px solid #3b82f6;}

/* ── CHRONOMÈTRE ── */
.chrono{font-family:'IBM Plex Mono',monospace;font-size:2.2rem;font-weight:600;color:var(--accent-cyan);text-align:center;letter-spacing:0.05em;}
.chrono-label{font-size:0.7rem;color:var(--text-muted);text-align:center;letter-spacing:0.1em;text-transform:uppercase;}

/* ── REGISTRE ── */
.reg-card{background:var(--bg-panel);border:1px solid var(--border);border-radius:12px;padding:18px 20px;margin-bottom:10px;transition:all 0.2s;}
.reg-card:hover{border-color:var(--accent-cyan);background:#0c1528;}
.reg-card-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;}
.reg-card-title{font-family:'IBM Plex Mono',monospace;font-size:1rem;font-weight:600;color:#e2e8f0;}
.reg-card-date{font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:var(--text-muted);}
.reg-card-body{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:6px 16px;font-size:0.82rem;}
.reg-field{display:flex;flex-direction:column;}
.reg-field-label{font-size:0.68rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.08em;}
.reg-field-value{color:#cbd5e1;font-family:'IBM Plex Mono',monospace;}
.reg-badge{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:0.78rem;font-weight:600;padding:3px 10px;border-radius:6px;margin-right:6px;}
.reg-badge-M{background:#3b0764;color:#d8b4fe;}.reg-badge-1{background:#7f1d1d;color:#fca5a5;}
.reg-badge-2{background:#7c2d12;color:#fdba74;}.reg-badge-3A{background:#78350f;color:#fde68a;}
.reg-badge-3B{background:#713f12;color:#fde68a;}.reg-badge-4{background:#14532d;color:#86efac;}
.reg-badge-5{background:#1e3a5f;color:#93c5fd;}
.reg-stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px;margin-bottom:20px;}
.reg-stat-card{background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:16px;text-align:center;}
.reg-stat-num{font-family:'IBM Plex Mono',monospace;font-size:1.8rem;font-weight:600;color:var(--accent-cyan);}
.reg-stat-label{font-size:0.72rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.1em;margin-top:4px;}
.reg-empty{text-align:center;padding:60px 20px;color:#475569;}
.reg-empty-icon{font-size:3rem;margin-bottom:12px;opacity:0.4;}

/* ── RÉÉVALUATION ── */
.reeval-row{background:var(--bg-panel);border:1px solid var(--border);border-radius:8px;padding:10px 14px;margin-bottom:6px;font-size:0.83rem;}
.reeval-better{border-left:4px solid #22c55e;}
.reeval-same{border-left:4px solid #3b82f6;}
.reeval-worse{border-left:4px solid var(--accent-red);}
.trend-up{color:#4ade80;}.trend-down{color:#f87171;}.trend-same{color:#94a3b8;}

/* ── FICHE TRI ── */
.fiche-tri{background:white;color:#1e293b;border-radius:10px;padding:20px;font-family:'IBM Plex Sans',sans-serif;}
.fiche-header{border-bottom:3px solid #0f172a;padding-bottom:10px;margin-bottom:12px;}
.fiche-title{font-size:1.1rem;font-weight:700;color:#0f172a;}
.fiche-row{display:flex;justify-content:space-between;font-size:0.82rem;padding:3px 0;border-bottom:1px solid #e2e8f0;}
.fiche-section{font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#64748b;margin:10px 0 4px 0;}
.fiche-niveau{text-align:center;padding:10px;border-radius:8px;font-weight:700;font-size:1.2rem;margin:10px 0;}
.fiche-M,.fiche-1{background:#fee2e2;color:#7f1d1d;}
.fiche-2{background:#ffedd5;color:#7c2d12;}
.fiche-3A,.fiche-3B{background:#fef9c3;color:#713f12;}
.fiche-4{background:#dcfce7;color:#14532d;}
.fiche-5{background:#dbeafe;color:#1e3a8a;}

/* ── DISCLAIMER RGPD ── */
.disclaimer-rgpd{
  background:var(--bg-card);border:1px solid #334155;border-radius:8px;
  padding:14px 18px;margin-top:24px;font-size:0.7rem;color:#64748b;line-height:1.7;font-style:italic;
}
.disclaimer-title{font-family:'IBM Plex Mono',monospace;font-size:0.65rem;font-weight:600;color:#475569;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;}
.akir-signature{color:var(--accent-cyan);font-weight:700;font-size:0.88rem;font-family:'IBM Plex Mono',monospace;border-top:1px solid var(--border);padding-top:8px;margin-top:8px;}

/* ── TRI RAPIDE ── */
.tri-rapide-box{background:var(--bg-card);border:2px solid var(--accent-cyan);border-radius:14px;padding:24px;margin-bottom:16px;}
.tri-rapide-title{font-family:'IBM Plex Mono',monospace;color:var(--accent-cyan);font-size:0.8rem;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:12px;}

/* ── QUESTION GUIDÉE ── */
.question-guidee{background:var(--bg-panel);border:1px solid var(--border);border-left:4px solid var(--accent-cyan);border-radius:8px;padding:12px 16px;margin:6px 0;font-size:0.9rem;}

/* ── LEGAL SIDEBAR ── */
.legal-text{font-size:0.72rem;color:#475569;font-style:italic;margin-top:8px;}
.signature{color:var(--accent-cyan);font-weight:600;font-size:0.85rem;border-top:1px solid var(--border);padding-top:10px;margin-top:12px;}

/* ── MOBILE RESPONSIVE (iPhone) ── */
@media (max-width: 768px) {
  .triage-box{padding:18px;}
  .fiche-tri{padding:14px;}
  .reg-card-body{grid-template-columns:repeat(2,1fr);}
  .sbar-block{font-size:0.75rem;padding:12px;}
  .critical-alert-title{font-size:1rem;}
  .news2-badge{font-size:1.2rem;}
  /* Gros boutons one-hand friendly */
  .stButton>button{min-height:52px;font-size:1rem;}
  .stNumberInput input{font-size:1.1rem;}
}
</style>
""", unsafe_allow_html=True)


# --- SESSION STATE ------------------------------------------------------------
defaults = {
    'patient_history': [],
    'arrival_time': None,
    'sbar_text': "",
    'last_reeval': None,
    'reeval_history': [],
    'mode': 'complet',
    'gcs_y_score': 4,
    'gcs_v_score': 5,
    'gcs_m_score': 6,
    'confirm_delete': None,
    'detail_patient_uid': None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# =============================================================================
# CONSTANTES
# =============================================================================
TRI_LABELS = {
    "M": "TRI M - IMMEDIAT", "1": "TRI 1 - URGENCE EXTREME",
    "2": "TRI 2 - TRES URGENT", "3A": "TRI 3A - URGENT",
    "3B": "TRI 3B - URGENT DIFFERE", "4": "TRI 4 - MOINS URGENT",
    "5": "TRI 5 - NON URGENT",
}
TRI_SECTORS = {
    "M": "Déchocage - Réanimation immédiate",
    "1": "Déchocage - Prise en charge immédiate",
    "2": "Salle de soins aigus - Médecin < 20 min",
    "3A": "Salle de soins aigus - Médecin < 30 min",
    "3B": "Polyclinique urgences - Médecin < 1h",
    "4": "Consultation urgences - Médecin < 2h",
    "5": "Salle d'attente - Consultation / réorientation MG",
}
TRI_DELAIS   = {"M": 5, "1": 5, "2": 15, "3A": 30, "3B": 60, "4": 120, "5": 999}
TRI_BOX_CSS  = {"M": "box-M", "1": "box-1", "2": "box-2", "3A": "box-3A", "3B": "box-3B", "4": "box-4", "5": "box-5"}
TRI_HIST_CSS = {"M": "hist-M", "1": "hist-1", "2": "hist-2", "3A": "hist-3A", "3B": "hist-3B", "4": "hist-4", "5": "hist-5"}
TRI_EMOJI    = {"M": "🟣", "1": "🔴", "2": "🟠", "3A": "🟡", "3B": "🟡", "4": "🟢", "5": "🔵"}

# Questions discriminantes FRENCH par motif
QUESTIONS_GUIDEES = {
    "Douleur thoracique / SCA": [
        ("ECG réalisé ?", "ecg_fait", "bool"),
        ("ECG anormal ?", "ecg_anormal", "bool"),
        ("Douleur typique (rétrosternale, constrictive, irradiation bras/mâchoire) ?", "douleur_typique", "bool"),
        ("Durée > 20 min ?", "duree_longue", "bool"),
    ],
    "Dyspnée / insuffisance respiratoire": [
        ("Peut parler en phrases complètes ?", "parole_ok", "bool"),
        ("Tirage / sibilants audibles ?", "tirage", "bool"),
        ("Orthopnée (dort assis) ?", "orthopnee", "bool"),
    ],
    "AVC / Déficit neurologique": [
        ("Déficit moteur ou facial ?", "deficit_moteur", "bool"),
        ("Aphasie / trouble langage ?", "aphasie", "bool"),
        ("Heure exacte début symptômes connue ?", "heure_debut_connue", "bool"),
        ("Délai < 4h30 ?", "delai_ok", "bool"),
    ],
    "Traumatisme crânien": [
        ("Perte de connaissance ?", "pdc", "bool"),
        ("Vomissements répétés ?", "vomissements_repetes", "bool"),
        ("Sous anticoagulants / AOD ?", "aod_avk", "bool"),
        ("GCS < 15 ?", "gcs_alt", "bool"),
    ],
    "Douleur abdominale": [
        ("Défense / contracture ?", "defense", "bool"),
        ("Fièvre associée ?", "fievre_assoc", "bool"),
        ("Dernier transit normal ?", "transit_ok", "bool"),
    ],
    "Fièvre": [
        ("T > 40°C ou < 35.2°C ?", "temp_extreme", "bool"),
        ("Confusion / purpura ?", "confusion", "bool"),
        ("Hypotension / Shock Index >= 1 ?", "hypotension", "bool"),
    ],
    "Céphalée": [
        ("Céphalée inhabituelle (1er épisode) ?", "inhabituelle", "bool"),
        ("Début brutal (coup de tonnerre) ?", "brutale", "bool"),
        ("Fièvre ou raideur nuque ?", "fievre_assoc", "bool"),
    ],
    "Douleur lombaire / colique néphrétique": [
        ("Douleur intense / agitation ?", "intense", "bool"),
        ("Fièvre associée ?", "fievre_assoc", "bool"),
        ("Anurie / rétention ?", "anurie", "bool"),
    ],
    "Hypertension artérielle": [
        ("PAS >= 180 mmHg ?", "hta_severe", "bool"),
        ("Céphalée / trouble visuel / douleur thoracique ?", "sf_associes", "bool"),
    ],
    "Allergie / anaphylaxie": [
        ("Dyspnée / stridor ?", "dyspnee", "bool"),
        ("Chute tension / malaise ?", "mauvaise_tolerance", "bool"),
        ("Urticaire généralisé ?", "urticaire", "bool"),
    ],
}

# Prescriptions anticipées IAO par motif
PRESCRIPTIONS_ANTICIPEES = {
    "Douleur thoracique / SCA": {
        "Gestes immédiats": [
            "ECG 12 dérivations IMMEDIAT (< 10 min de l'arrivée)",
            "Voie veineuse périphérique (VVP) 18G minimum",
            "Monitoring cardiorespiratoire continu (scope)",
            "Aspirine 250 mg PO/IV sauf allergie documentée",
            "Position semi-assise, O2 si SpO2 < 95%",
        ],
        "Bilan biologique": [
            "Troponine Hs T0 (puis T1h ou T3h selon protocole)",
            "Hémogramme complet + plaquettes",
            "Ionogramme, créatinine, urée",
            "TP / TCA / INR si AOD/AVK",
            "D-Dimères si suspicion EP concomitante",
            "NT-proBNP si signes d'insuffisance cardiaque",
        ],
        "Imagerie": [
            "RX thorax face (lit si instable)",
        ],
        "Rappels critiques": [
            "Répéter ECG à 30 min si premier normal et douleur persistante",
            "NE PAS faire manger le patient (potentiel coro urgente)",
            "Alerter cardiologue si sus-décalage ST (STEMI = salle cath < 90 min)",
        ],
    },
    "Dyspnée / insuffisance respiratoire": {
        "Gestes immédiats": [
            "Position semi-assise (Fowler)",
            "O2 - objectif SpO2 > 94% (88-92% si BPCO connu)",
            "VVP 18G minimum",
            "Monitoring SpO2 continue + FR",
        ],
        "Bilan biologique": [
            "Gazométrie artérielle (ou veineuse si instable)",
            "Hémogramme complet",
            "D-Dimères si suspicion EP",
            "NT-proBNP si suspicion IC",
            "CRP + PCT si contexte infectieux",
        ],
        "Imagerie": [
            "RX thorax face debout",
            "Échographie pulmonaire (POCUS) si disponible",
        ],
        "Rappels critiques": [
            "Préparer kit IOT (intubation) si FR > 35 ou SpO2 < 85% sous O2",
            "Aérosol bêta2-mimétiques si bronchospasme",
        ],
    },
    "AVC / Déficit neurologique": {
        "Gestes immédiats": [
            "ALERTE FILIÈRE STROKE IMMÉDIATE",
            "Glycémie capillaire (CI thrombolyse si < 0.6 ou > 22 mmol/L)",
            "VVP 18G bras NON parétique",
            "NE PAS faire baisser la TA sauf si PAS > 220 mmHg",
            "À jeun strict",
        ],
        "Bilan biologique": [
            "Hémogramme + plaquettes URGENT",
            "TP / TCA / INR / fibrinogène (CI thrombolyse si anomalie)",
            "Ionogramme, créatinine",
            "Troponine (FA possible)",
        ],
        "Imagerie": [
            "TDM cérébral sans injection URGENT (< 25 min door-to-CT)",
            "Angio-TDM TSA si thrombectomie envisagée",
        ],
        "Rappels critiques": [
            "Heure exacte début symptômes = information VITALE",
            "Objectif door-to-needle < 60 min pour thrombolyse",
            "CI thrombolyse : AOD < 48h, chirurgie < 14j, AVC < 3 mois",
            "Activer neuroradiologue si occlusion gros vaisseau",
        ],
    },
    "Traumatisme crânien": {
        "Gestes immédiats": [
            "Monitoring neurologique : GCS + pupilles toutes les 15 min",
            "VVP si GCS < 15 ou AOD/AVK",
            "Collier cervical si mécanisme à risque",
            "À jeun (potentiel bloc)",
        ],
        "Bilan biologique": [
            "Hémogramme + TP/INR si AOD/AVK",
            "Groupe ABO / Rh / RAI si GCS <= 8",
        ],
        "Imagerie": [
            "TDM cérébral si critères SFMU/NICE : PDC, vomissements, AOD, GCS < 15",
        ],
        "Rappels critiques": [
            "Surveillance minimum 4h si TC bénin sans indication TDM",
            "Fiche de conseil remise au patient sortant",
            "AOD/AVK = TDM SYSTÉMATIQUE même si GCS 15",
        ],
    },
    "Douleur abdominale": {
        "Gestes immédiats": [
            "VVP si défense / douleur sévère",
            "À jeun si suspicion chirurgicale",
            "Antalgique IV : Paracétamol 1g ou Néfopam si EVA > 5",
        ],
        "Bilan biologique": [
            "Hémogramme, CRP",
            "Lipase (pancréas)",
            "Bilan hépatique (ASAT, ALAT, GGT, bilirubine)",
            "Bêta-hCG chez toute femme en âge de procréer",
            "Ionogramme, créatinine",
            "BU + ECBU si signes urinaires",
        ],
        "Imagerie": [
            "Échographie abdominale (ou TDM si péritonite / urgence chirurgicale)",
        ],
        "Rappels critiques": [
            "Toucher rectal si suspicion appendicite / rectorragie",
            "Penser : grossesse extra-utérine chez toute femme en âge de procréer",
        ],
    },
    "Fièvre": {
        "Gestes immédiats": [
            "VVP",
            "Paracétamol 1g IV si T > 38.5 et mauvaise tolérance",
        ],
        "Bilan biologique": [
            "Hémocultures x2 AVANT toute antibiothérapie",
            "Hémogramme, CRP, PCT",
            "Ionogramme, créatinine",
            "Lactates (sepsis ?)",
            "BU + ECBU",
        ],
        "Rappels critiques": [
            "Purpura fulminans = Ceftriaxone 2g IV IMMÉDIATEMENT (ne pas attendre le bilan)",
            "Antibiotiques < 1h si sepsis / choc septique",
            "Rechercher porte d'entrée infectieuse systématiquement",
        ],
    },
    "Allergie / anaphylaxie": {
        "Gestes immédiats": [
            "ADRÉNALINE 0.5 mg IM (face antérolatérale cuisse) si anaphylaxie",
            "Remplissage NaCl 0.9% 500 mL en débit libre si choc",
            "Position Trendelenburg si hypotension",
            "O2 haut débit si dyspnée / désaturation",
            "Antihistaminique IV (Polaramine 5 mg)",
            "Corticoïdes IV (Méthylprednisolone 1 mg/kg)",
        ],
        "Rappels critiques": [
            "Répéter adrénaline à 5 min si pas d'amélioration",
            "Surveillance 6h minimum (risque de réaction biphasique)",
            "Tryptase à prélever dans les 2h post-réaction",
        ],
    },
    "Intoxication médicamenteuse": {
        "Gestes immédiats": [
            "VVP",
            "ECG 12 dérivations (toxiques cardiotropes ?)",
            "Monitoring continu",
        ],
        "Bilan biologique": [
            "Paracétamolémie SYSTÉMATIQUE",
            "Éthanolémie",
            "Screening toxicologique urinaire + sanguin",
            "Ionogramme, créatinine, bilan hépatique",
            "Gazométrie (acidose ?)",
        ],
        "Rappels critiques": [
            "Centre Antipoisons Belgique : 070 245 245",
            "N-Acétylcystéine si intoxication paracétamol selon nomogramme Rumack-Matthew",
            "Charbon activé si ingestion < 1h et patient conscient (sauf CI)",
            "Évaluation psychiatrique OBLIGATOIRE si intention suicidaire",
        ],
    },
    "Intoxication non médicamenteuse": {
        "Gestes immédiats": [
            "VVP",
            "ECG 12 dérivations",
            "Monitoring continu",
            "Identifier le toxique (emballage, témoin, odeur)",
        ],
        "Bilan biologique": [
            "Screening toxicologique",
            "Ionogramme, créatinine",
            "Gazométrie artérielle",
            "Bilan hépatique",
        ],
        "Rappels critiques": [
            "Centre Antipoisons Belgique : 070 245 245",
            "NE PAS faire vomir (produits caustiques, moussants, pétroliers)",
        ],
    },
    "Convulsions": {
        "Gestes immédiats": [
            "Protection des voies aériennes - PLS si crise en cours",
            "O2 au masque haute concentration",
            "VVP",
            "Glycémie capillaire IMMÉDIATE",
            "Diazépam 10 mg IV ou Midazolam 10 mg IM si crise > 5 min",
        ],
        "Bilan biologique": [
            "Hémogramme, ionogramme (Ca, Mg, Na)",
            "Glycémie",
            "Dosage antiépileptiques si traitement connu",
        ],
        "Rappels critiques": [
            "Chronométrer la durée de la crise",
            "État de mal = crise > 5 min ou 2 crises sans récupération",
            "TDM cérébral si premier épisode ou contexte traumatique",
        ],
    },
    "Accouchement imminent": {
        "Gestes immédiats": [
            "Appel SMUR / équipe obstétricale IMMÉDIAT",
            "Préparer kit accouchement inopiné",
            "Monitoring fœtal si disponible",
            "VVP gros calibre (16G)",
            "Position gynécologique / décubitus latéral gauche",
        ],
        "Rappels critiques": [
            "NE PAS TRANSPORTER si Malinas >= 8",
            "Préparer : clamps ombilicaux, draps chauds, aspirateur mucosités",
            "Ocytocine 5 UI IV lent APRÈS délivrance (prévention HPP)",
        ],
    },
    "Idée / comportement suicidaire": {
        "Gestes immédiats": [
            "Mise en sécurité du patient (retirer objets dangereux)",
            "Surveillance constante (1 soignant dédié)",
            "VVP si intoxication associée",
            "Environnement calme, porte fermée",
        ],
        "Rappels critiques": [
            "Évaluation psychiatrique OBLIGATOIRE avant toute sortie",
            "Rechercher intoxication médicamenteuse associée",
            "Évaluer le risque suicidaire (RUD : Risque, Urgence, Dangerosité)",
            "Contacter la personne de confiance / famille si accord patient",
        ],
    },
    "Hypoglycémie": {
        "Gestes immédiats": [
            "Glycémie capillaire IMMÉDIATE",
            "Si conscient : resucrage PO (15-20g sucres rapides)",
            "Si inconscient : Glucose 30% 50 mL IV en bolus",
            "Si pas d'accès IV : Glucagon 1 mg IM/SC",
        ],
        "Rappels critiques": [
            "Contrôler glycémie à 15 min post-resucrage",
            "Rechercher la cause : saut de repas, surdosage insuline, sulfamides",
            "Surveillance prolongée si sulfamides (risque récidive)",
        ],
    },
}


# =============================================================================
# ███  MODULE : MOTEUR SCORES  ███
# Chaque fonction encapsule un calcul de score dans un bloc sécurisé.
# =============================================================================

def compute_news2(fr, spo2, supp_o2, temp, pas, fc, gcs, bpco):
    """
    Calcule le score NEWS2 (National Early Warning Score 2).
    Chaque paramètre reçoit un score partiel selon les seuils cliniques officiels.
    Retourne (score_int, warnings_list).

    Référence : Royal College of Physicians, NEWS2 2017.
    Barème BPCO utilise l'échelle SpO2 adaptée (objectif 88-92%).
    """
    warnings = []
    try:
        s = 0

        # Fréquence respiratoire
        if fr is None:
            warnings.append("⚠️ Score NEWS2 incomplet : Fréquence respiratoire manquante")
            return 0, warnings
        s += 3 if fr <= 8 else (1 if fr <= 11 else (0 if fr <= 20 else (2 if fr <= 24 else 3)))

        # SpO2 — deux échelles selon BPCO
        if spo2 is None:
            warnings.append("⚠️ Score NEWS2 incomplet : SpO2 manquante")
            return 0, warnings
        if not bpco:
            s += 3 if spo2 <= 91 else (2 if spo2 <= 93 else (1 if spo2 <= 95 else 0))
        else:
            # Échelle 2 pour BPCO (objectif 88-92%)
            s += (3 if spo2 <= 83 else (2 if spo2 <= 85 else (1 if spo2 <= 87 else
                  (0 if spo2 <= 92 else (1 if spo2 <= 94 else (2 if spo2 <= 96 else 3))))))

        # Oxygène supplémentaire
        if supp_o2:
            s += 2

        # Température
        if temp is None:
            warnings.append("⚠️ Score NEWS2 incomplet : Température manquante")
            return 0, warnings
        s += 3 if temp <= 35.0 else (1 if temp <= 36.0 else (0 if temp <= 38.0 else (1 if temp <= 39.0 else 2)))

        # Pression artérielle systolique
        if pas is None:
            warnings.append("⚠️ Score NEWS2 incomplet : TA manquante")
            return 0, warnings
        s += 3 if pas <= 90 else (2 if pas <= 100 else (1 if pas <= 110 else (0 if pas <= 219 else 3)))

        # Fréquence cardiaque
        if fc is None:
            warnings.append("⚠️ Score NEWS2 incomplet : FC manquante")
            return 0, warnings
        s += 3 if fc <= 40 else (1 if fc <= 50 else (0 if fc <= 90 else (1 if fc <= 110 else (2 if fc <= 130 else 3))))

        # Glasgow
        if gcs is None:
            warnings.append("⚠️ Score NEWS2 incomplet : GCS manquant")
            return 0, warnings
        if gcs < 15:
            s += 3

        return s, warnings

    except (TypeError, ValueError) as e:
        return 0, [f"⚠️ Erreur calcul NEWS2 : {e}"]


def news2_level(score):
    """Retourne (label, css_class) pour un score NEWS2 donné."""
    if score == 0:  return "Faible (0)", "news2-low"
    if score <= 4:  return f"Faible ({score})", "news2-low"
    if score <= 6:  return f"Modéré ({score})", "news2-med"
    if score <= 8:  return f"Élevé ({score})", "news2-high"
    return f"CRITIQUE ({score})", "news2-crit"


def compute_score_timi(age, facteurs_risque_cv, angine_severe, utilisation_aspirine,
                       biomarqueurs, deviation_st, crises_24h):
    """
    Calcule le score TIMI (Thrombolysis In Myocardial Infarction) pour les SCA-ST-.
    Indique le risque de mortalité/IDM/revascularisation à 14 jours.

    Référence : Antman et al., JAMA 2000.
    """
    try:
        s = 0
        if age >= 65: s += 1
        if facteurs_risque_cv >= 3: s += 1
        if angine_severe: s += 1  # Sténose connue >= 50%
        if utilisation_aspirine: s += 1  # Utilisation aspirine dans les 7j = paradoxal
        if biomarqueurs: s += 1  # Troponine élevée
        if deviation_st: s += 1  # Déviation ST >= 0.5 mm
        if crises_24h >= 2: s += 1  # >= 2 crises angineuses en 24h
        return s, []
    except (TypeError, ValueError) as e:
        return 0, [f"⚠️ Erreur calcul TIMI : {e}"]


def compute_score_silverman(balancement_th, tirage_intercostal, retraction_sus_sternale,
                            aile_nez, geignement):
    """
    Calcule le score de Silverman pour la détresse respiratoire néonatale.
    Chaque item est côté 0 (absent), 1 (modéré) ou 2 (intense).
    Score maximal = 10 (détresse sévère).

    Référence : Silverman & Andersen, Pediatrics 1956.
    """
    try:
        s = balancement_th + tirage_intercostal + retraction_sus_sternale + aile_nez + geignement
        return min(s, 10), []
    except (TypeError, ValueError) as e:
        return 0, [f"⚠️ Erreur calcul Silverman : {e}"]


def compute_score_gcs(y, v, m):
    """
    Calcule le Glasgow Coma Scale à partir des sous-scores Y (yeux), V (verbal), M (moteur).
    Score de 3 (coma profond) à 15 (état de conscience normal).

    Référence : Teasdale & Jennett, Lancet 1974.
    """
    try:
        total = int(y) + int(v) + int(m)
        return max(3, min(15, total)), []
    except (TypeError, ValueError) as e:
        return 15, [f"⚠️ Erreur calcul GCS : {e}"]


def compute_score_malinas(parite, duree_travail, duree_contractions,
                          intervalle_contractions, poche_eaux):
    """
    Calcule le score de Malinas pour décider du transport en maternité.
    Score >= 8 : transport contre-indiqué, accouchement imminent.

    Référence : Malinas & Favier — Obstétrique pratique.
    """
    try:
        s = parite + duree_travail + duree_contractions + intervalle_contractions + poche_eaux
        return min(s, 10), []
    except (TypeError, ValueError) as e:
        return 0, [f"⚠️ Erreur calcul Malinas : {e}"]


def compute_score_brulure(surface_corporelle_pct, age_patient, profondeur):
    """
    Calcule la Surface Corporelle Brûlée (SCB) et le pronostic selon la règle des 9 de Wallace.
    Formule de Baux (âge + SCB) pour estimer le pronostic de mortalité.

    Référence : Wallace, Lancet 1951 ; Baux, 1961.
    """
    try:
        scb = max(0, min(100, surface_corporelle_pct))
        baux = age_patient + scb
        # Pronostic Baux : > 100 = pronostic sévère, > 120 = quasi-létal
        if baux > 120:   pronostic = "Pronostic vital très réservé (Baux > 120)"
        elif baux > 100: pronostic = "Pronostic sévère (Baux 100-120)"
        elif baux > 80:  pronostic = "Pronostic réservé (Baux 80-100)"
        else:            pronostic = "Pronostic favorable (Baux < 80)"
        return scb, baux, pronostic, []
    except (TypeError, ValueError) as e:
        return 0, 0, "Erreur calcul", [f"⚠️ Erreur score brûlure : {e}"]


# =============================================================================
# ███  MODULE : MOTEUR PERFUSION  ███
# Calculateur de débit et doses de charge courantes.
# =============================================================================

def calcul_debit_perfusion(volume_ml, duree_heures):
    """
    Calcule le débit de perfusion en ml/h.
    Formule : Débit = Volume (ml) / Durée (h)

    En cas de valeurs manquantes ou nulles, retourne un message d'erreur métier.
    """
    try:
        if duree_heures <= 0:
            return None, "⚠️ Durée de perfusion invalide (doit être > 0)"
        if volume_ml <= 0:
            return None, "⚠️ Volume de perfusion invalide (doit être > 0)"
        debit = round(volume_ml / duree_heures, 1)
        return debit, None
    except (TypeError, ValueError) as e:
        return None, f"⚠️ Erreur calcul débit : {e}"


def calcul_dose_paracetamol(poids_kg):
    """
    Calcule la dose de charge de Paracétamol selon le poids du patient.
    Dose adulte : 15 mg/kg IV en 15 min (max 1g chez l'adulte).
    Dose pédiatrique : 15 mg/kg IV (max 60 mg/kg/j).

    Référence : RCP Paracétamol IV — Belgique 2024.
    """
    try:
        if poids_kg <= 0:
            return None, "⚠️ Poids invalide"
        dose_mg = round(15 * poids_kg, 0)
        dose_g  = round(dose_mg / 1000, 2)
        # Plafonner à 1g chez l'adulte (> 50 kg)
        if poids_kg >= 50:
            dose_mg = 1000
            dose_g  = 1.0
        return {"dose_mg": dose_mg, "dose_g": dose_g, "debit_15min": f"Perfuser en 15 min"}, None
    except (TypeError, ValueError) as e:
        return None, f"⚠️ Erreur calcul Paracétamol : {e}"


def calcul_dose_midazolam(poids_kg):
    """
    Calcule la dose de Midazolam pour sédation procédurale.
    Dose adulte : 0.05-0.1 mg/kg IV titré. Max 5 mg.
    """
    try:
        if poids_kg <= 0:
            return None, "⚠️ Poids invalide"
        dose_min = round(0.05 * poids_kg, 1)
        dose_max = round(0.1 * poids_kg, 1)
        # Plafonner
        dose_min = min(dose_min, 2.5)
        dose_max = min(dose_max, 5.0)
        return {"dose_min_mg": dose_min, "dose_max_mg": dose_max, "note": "Titrer par paliers de 1mg IV lent"}, None
    except (TypeError, ValueError) as e:
        return None, f"⚠️ Erreur calcul Midazolam : {e}"


def calcul_dose_nefopam(poids_kg):
    """
    Calcule la dose de Néfopam (Acupan) pour antalgie.
    Dose standard : 20 mg IV en 15 min (pas d'adaptation au poids en routine).
    CI : épilepsie, rétention urinaire, glaucome.
    """
    try:
        return {"dose_mg": 20, "note": "20 mg IV dilué dans 100mL NaCl 0.9%, perfuser en 15 min. CI : épilepsie, glaucome, rétention urinaire."}, None
    except Exception as e:
        return None, f"⚠️ Erreur calcul Néfopam : {e}"


# =============================================================================
# ███  MODULE : MOTEUR TRIAGE — FRENCH TRIAGE SFMU V1.1  ███
# Algorithme de triage structuré par motif de recours.
# =============================================================================

def french_triage(motif, details, fc, pas, spo2, fr, gcs, temp, age, news2_score):
    """
    Détermine le niveau de triage FRENCH selon le motif et les paramètres vitaux.
    Retourne (niveau_str, justification_str, critere_reference_str).

    Référence : Société Française de Médecine d'Urgence (SFMU) — FRENCH Triage V1.1, 2018.
    Adaptation SIAMU Belgique.
    """
    try:
        # Sécurité : valeurs par défaut si données manquantes
        fc   = fc   if fc   is not None else 80
        pas  = pas  if pas  is not None else 120
        spo2 = spo2 if spo2 is not None else 98
        fr   = fr   if fr   is not None else 16
        gcs  = gcs  if gcs  is not None else 15
        temp = temp if temp is not None else 37.0
        news2_score = news2_score if news2_score is not None else 0

        # Critère transversal NEWS2 : engagement vital immédiat si >= 9
        if news2_score >= 9:
            return "M", "NEWS2 >= 9 : engagement vital immédiat.", "NEWS2 Tri M"

        if motif == "Arrêt cardiorespiratoire":
            return "M", "ACR.", "FRENCH Tri M"

        if motif == "Hypotension artérielle":
            if pas <= 70: return "1", f"PAS <= 70 ({pas}).", "FRENCH Tri 1"
            if pas <= 90 or (pas <= 100 and fc > 100): return "2", "PAS basse ou choc débutant.", "FRENCH Tri 2"
            if 90 < pas <= 100: return "3B", "PAS limite.", "FRENCH Tri 3B"
            return "4", "TA dans les normes.", "FRENCH Tri 4"

        if motif == "Douleur thoracique / SCA":
            ecg   = details.get("ecg", "Normal")
            dt    = details.get("douleur_type", "Atypique")
            co    = details.get("comorbidites_coronaires", False)
            dtyp  = details.get("douleur_typique", False)
            # Facteurs de risque cardiovasculaires : si >= 2 avec douleur thoracique -> remonter tri
            frcv_count = details.get("frcv_count", 0)
            if ecg == "Anormal typique SCA" or details.get("ecg_anormal", False):
                return "1", "ECG typique SCA.", "FRENCH Tri 1"
            if ecg == "Anormal non typique" or dt == "Typique persistante/intense" or (dtyp and details.get("duree_longue", False)):
                return "2", "Douleur typique persistante ou ECG douteux.", "FRENCH Tri 2"
            # Remontée automatique si >= 2 FRCV avec douleur thoracique
            if frcv_count >= 2:
                return "3A", f"Douleur thoracique + {frcv_count} facteurs de risque CV.", "FRENCH Tri 3A (FRCV ≥ 2)"
            if co: return "3A", "Comorbidités coronaires.", "FRENCH Tri 3A"
            if dtyp or dt == "Type coronaire": return "3B", "Douleur type coronaire.", "FRENCH Tri 3B"
            return "4", "ECG normal, douleur atypique.", "FRENCH Tri 4"

        if motif == "Tachycardie / tachyarythmie":
            if fc >= 180: return "1", "FC >= 180.", "FRENCH Tri 1"
            if fc >= 130: return "2", "FC >= 130.", "FRENCH Tri 2"
            if fc > 110:  return "3B", "FC > 110.", "FRENCH Tri 3B"
            return "4", "Épisode résolutif.", "FRENCH Tri 4"

        if motif == "Bradycardie / bradyarythmie":
            mt = details.get("mauvaise_tolerance", False)
            if fc <= 40: return "1", "FC <= 40.", "FRENCH Tri 1"
            if fc <= 50 and mt: return "2", "FC 40-50 + mauvaise tolérance.", "FRENCH Tri 2"
            if fc <= 50: return "3B", "FC 40-50 bien tolérée.", "FRENCH Tri 3B"
            return "4", "Bradycardie tolérée.", "FRENCH Tri 4"

        if motif == "Hypertension artérielle":
            sf = details.get("sf_associes", False)
            if pas >= 220 or (pas >= 180 and sf): return "2", f"PAS >= 220 ou >= 180 + SF.", "FRENCH Tri 2"
            if pas >= 180: return "3B", "PAS >= 180 sans SF.", "FRENCH Tri 3B"
            return "4", "PAS < 180.", "FRENCH Tri 4"

        if motif == "Dyspnée / insuffisance respiratoire":
            if fr >= 40 or spo2 < 86: return "1", "Détresse respiratoire.", "FRENCH Tri 1"
            if not details.get("parole_ok", True) or details.get("tirage") or details.get("orthopnee") or (30 <= fr < 40) or (86 <= spo2 <= 90):
                return "2", "Dyspnée à la parole / tirage.", "FRENCH Tri 2"
            return "3B", "Dyspnée modérée stable.", "FRENCH Tri 3B"

        if motif == "Palpitations":
            if fc >= 180: return "2", "FC >= 180.", "FRENCH Tri 2"
            if fc >= 130: return "2", "FC >= 130.", "FRENCH Tri 2"
            if details.get("malaise") or fc > 110: return "3B", "Malaise / FC > 110.", "FRENCH Tri 3B"
            return "4", "Palpitations isolées.", "FRENCH Tri 4"

        if motif == "Asthme / aggravation BPCO":
            dep = details.get("dep", 999)
            if fr >= 40 or spo2 < 86: return "1", "Détresse respiratoire.", "FRENCH Tri 1"
            if dep <= 200 or not details.get("parole_ok", True) or details.get("tirage"):
                return "2", "DEP <= 200 / dyspnée parole.", "FRENCH Tri 2"
            if dep >= 300: return "4", "DEP >= 300.", "FRENCH Tri 4"
            return "3B", "Asthme modéré.", "FRENCH Tri 3B"

        if motif == "AVC / Déficit neurologique":
            dh = details.get("delai_heures", 999)
            ok = details.get("delai_ok", False)
            if dh <= 4.5 or ok: return "1", "Déficit < 4h30 - filière Stroke / thrombolyse.", "FRENCH Tri 1"
            if dh >= 24: return "3B", "Déficit > 24h.", "FRENCH Tri 3B"
            return "2", "Déficit neurologique aigu.", "FRENCH Tri 2"

        if motif == "Altération de conscience / Coma":
            if gcs <= 8:  return "1", f"GCS {gcs} - coma.", "FRENCH Tri 1"
            if gcs <= 13: return "2", f"GCS {gcs} - altération modérée.", "FRENCH Tri 2"
            return "3B", "Altération légère.", "FRENCH Tri 3B"

        if motif == "Convulsions":
            if details.get("crises_multiples") or details.get("en_cours") or details.get("confusion_post_critique") or temp >= 38.5:
                return "2", "Crise en cours / multiple / confusion.", "FRENCH Tri 2"
            return "3B", "Récupération complète.", "FRENCH Tri 3B"

        if motif == "Céphalée":
            if details.get("inhabituelle") or details.get("brutale") or details.get("fievre_assoc") or temp >= 38.5:
                return "2", "Céphalée inhabituelle / brutale / fébrile.", "FRENCH Tri 2"
            return "3B", "Migraine connue.", "FRENCH Tri 3B"

        if motif == "Vertiges / trouble de l'équilibre":
            if details.get("signes_neuro") or details.get("cephalee_brutale"):
                return "2", "Signes neuro.", "FRENCH Tri 2"
            return "5", "Troubles stables.", "FRENCH Tri 5"

        if motif == "Confusion / désorientation":
            if temp >= 38.5: return "2", "Confusion + fièvre.", "FRENCH Tri 2"
            return "3B", "Confusion afébrile.", "FRENCH Tri 3B"

        if motif == "Hématémèse / vomissement de sang":
            if details.get("abondante"): return "2", "Hématémèse abondante.", "FRENCH Tri 2"
            return "3B", "Striures de sang.", "FRENCH Tri 3B"

        if motif == "Rectorragie / méléna":
            if details.get("abondante"): return "2", "Rectorragie abondante.", "FRENCH Tri 2"
            return "3B", "Selles souillées.", "FRENCH Tri 3B"

        if motif == "Douleur abdominale":
            if details.get("defense") or details.get("contracture") or details.get("mauvaise_tolerance"):
                return "2", "Défense / contracture.", "FRENCH Tri 2"
            if details.get("regressive"): return "5", "Douleur régressive.", "FRENCH Tri 5"
            return "3B", "Douleur modérée.", "FRENCH Tri 3B"

        if motif == "Douleur lombaire / colique néphrétique":
            if details.get("intense"): return "2", "Douleur intense.", "FRENCH Tri 2"
            if details.get("regressive"): return "5", "Douleur régressive.", "FRENCH Tri 5"
            return "3B", "Douleur modérée.", "FRENCH Tri 3B"

        if motif == "Rétention d'urine / anurie":
            return "2", "Rétention urinaire.", "FRENCH Tri 2"

        if motif == "Douleur testiculaire / torsion":
            if details.get("intense") or details.get("suspicion_torsion"):
                return "2", "Torsion suspectée.", "FRENCH Tri 2"
            return "3B", "Avis spécialiste de garde.", "FRENCH Tri 3B"

        if motif == "Hématurie":
            if details.get("abondante_active"): return "2", "Hématurie abondante.", "FRENCH Tri 2"
            return "3B", "Hématurie modérée.", "FRENCH Tri 3B"

        if motif == "Traumatisme avec amputation":
            return "M", "Amputation.", "FRENCH Tri M"

        if motif == "Traumatisme abdomen / thorax / cervical":
            if details.get("penetrant"): return "1", "Pénétrant.", "FRENCH Tri 1"
            if details.get("cinetique") == "Haute": return "2", "Haute vélocité.", "FRENCH Tri 2"
            if details.get("mauvaise_tolerance"): return "3B", "Faible vélocité + mauvaise tolérance.", "FRENCH Tri 3B"
            return "4", "Bonne tolérance.", "FRENCH Tri 4"

        if motif == "Traumatisme crânien":
            if gcs <= 8: return "1", f"TC coma GCS {gcs}.", "FRENCH Tri 1"
            if gcs <= 13 or details.get("deficit_neuro") or details.get("convulsion") or details.get("aod_avk") or details.get("vomissements_repetes"):
                return "2", "GCS 9-13 / déficit / AVK / vomissements.", "FRENCH Tri 2"
            if details.get("pdc") or details.get("plaie") or details.get("hematome"):
                return "3B", "PDC / plaie.", "FRENCH Tri 3B"
            return "5", "TC sans signe gravité.", "FRENCH Tri 5"

        if motif == "Brûlure":
            if details.get("etendue") or details.get("main_visage"):
                return "2", "Étendue / main / visage.", "FRENCH Tri 2"
            if age <= 2: return "3A", "Enfant <= 24 mois.", "FRENCH Tri 3A"
            return "3B", "Brûlure limitée.", "FRENCH Tri 3B"

        if motif == "Traumatisme bassin / hanche / fémur / rachis":
            if details.get("cinetique") == "Haute": return "2", "Haute vélocité.", "FRENCH Tri 2"
            if details.get("mauvaise_tolerance"): return "3B", "Mauvaise tolérance.", "FRENCH Tri 3B"
            return "4", "Bonne tolérance.", "FRENCH Tri 4"

        if motif == "Traumatisme membre / épaule":
            if details.get("ischemie") or details.get("cinetique") == "Haute":
                return "2", "Ischémie / haute vélocité.", "FRENCH Tri 2"
            if details.get("impotence_totale") or details.get("deformation"):
                return "3B", "Impotence totale.", "FRENCH Tri 3B"
            if details.get("impotence_moderee"): return "4", "Impotence modérée.", "FRENCH Tri 4"
            return "5", "Ni impotence ni déformation.", "FRENCH Tri 5"

        if motif == "Plaie":
            if details.get("delabrant") or details.get("saignement_actif"):
                return "2", "Délabrante / saignement.", "FRENCH Tri 2"
            if details.get("large_complexe") or details.get("main"):
                return "3B", "Large / main.", "FRENCH Tri 3B"
            if details.get("superficielle"): return "4", "Superficielle.", "FRENCH Tri 4"
            return "5", "Excoriation.", "FRENCH Tri 5"

        if motif == "Électrisation":
            if details.get("pdc") or details.get("foudre"): return "2", "PDC / foudre.", "FRENCH Tri 2"
            if details.get("haute_tension"): return "3B", "Haute tension.", "FRENCH Tri 3B"
            return "4", "Courant domestique.", "FRENCH Tri 4"

        if motif == "Agression sexuelle / sévices":
            return "1", "Agression sexuelle.", "FRENCH Tri 1"

        if motif == "Idée / comportement suicidaire":
            return "1", "Comportement suicidaire.", "FRENCH Tri 1"

        if motif == "Troubles du comportement / psychiatrie":
            if details.get("agitation") or details.get("violence"):
                return "2", "Agitation/violence.", "FRENCH Tri 2"
            return "4", "Consultation psychiatrique.", "FRENCH Tri 4"

        if motif in ["Intoxication médicamenteuse", "Intoxication non médicamenteuse"]:
            if details.get("mauvaise_tolerance") or details.get("intention_suicidaire") or details.get("cardiotropes"):
                return "2", "Mauvaise tolérance / suicidaire.", "FRENCH Tri 2"
            return "3B", "Avis spécialiste de garde.", "FRENCH Tri 3B"

        if motif == "Fièvre":
            if temp >= 40 or temp <= 35.2 or details.get("confusion") or details.get("purpura") or details.get("temp_extreme"):
                return "2", "Fièvre sévère ou signes graves.", "FRENCH Tri 2"
            if details.get("mauvaise_tolerance") or details.get("hypotension") or pas < 100:
                return "3B", "Mauvaise tolérance.", "FRENCH Tri 3B"
            return "5", "Fièvre tolérée.", "FRENCH Tri 5"

        if motif == "Accouchement imminent":
            return "M", "Accouchement imminent.", "FRENCH Tri M"

        if motif in ["Problème de grossesse (1er/2ème trimestre)", "Problème de grossesse (3ème trimestre)"]:
            return "3A", "Grossesse - surveillance urgente.", "FRENCH Tri 3A"

        if motif == "Méno-métrorragie":
            if details.get("grossesse") or details.get("abondante"):
                return "2", "Grossesse / abondante.", "FRENCH Tri 2"
            return "3B", "Modérée.", "FRENCH Tri 3B"

        if motif == "Hyperglycémie":
            gl = details.get("glycemie", 0)
            if details.get("cetose_elevee") or gcs < 15:
                return "2", "Cétose / trouble conscience.", "FRENCH Tri 2"
            if gl >= 20 or details.get("cetose_positive"):
                return "3B", f"Glycémie >= 20 ({gl}).", "FRENCH Tri 3B"
            return "4", "Hyperglycémie modérée.", "FRENCH Tri 4"

        if motif == "Hypoglycémie":
            if gcs <= 8:  return "1", f"Coma hypoglycémique GCS {gcs}.", "FRENCH Tri 1"
            if gcs <= 13 or details.get("mauvaise_tolerance"):
                return "2", "Mauvaise tolérance.", "FRENCH Tri 2"
            return "3B", "Hypoglycémie modérée.", "FRENCH Tri 3B"

        if motif == "Hypothermie":
            if temp <= 32: return "1", f"Hypothermie sévère T {temp}.", "FRENCH Tri 1"
            if temp <= 35.2: return "2", "Hypothermie modérée.", "FRENCH Tri 2"
            return "3B", "Hypothermie légère.", "FRENCH Tri 3B"

        if motif == "Coup de chaleur / insolation":
            if gcs <= 8: return "1", "Coup chaleur + coma.", "FRENCH Tri 1"
            if temp >= 40: return "2", f"T >= 40°C ({temp}).", "FRENCH Tri 2"
            return "3B", "Coup chaleur léger.", "FRENCH Tri 3B"

        if motif == "Allergie / anaphylaxie":
            if details.get("dyspnee") or details.get("mauvaise_tolerance"):
                return "2", "Anaphylaxie sévère.", "FRENCH Tri 2"
            return "4", "Réaction légère.", "FRENCH Tri 4"

        if motif == "Épistaxis":
            if details.get("abondant_actif"): return "2", "Abondant actif.", "FRENCH Tri 2"
            if details.get("abondant_resolutif"): return "3B", "Abondant résolutif.", "FRENCH Tri 3B"
            return "5", "Peu abondant.", "FRENCH Tri 5"

        if motif in ["Corps étranger / brûlure oculaire", "Trouble visuel / cécité"]:
            if details.get("intense") or details.get("chimique") or details.get("brutal"):
                return "2", "Urgence ophtalmologique.", "FRENCH Tri 2"
            return "3B", "Avis spécialiste de garde.", "FRENCH Tri 3B"

        # Fallback générique sur NEWS2 et EVA
        eva = details.get("eva", 0)
        if news2_score >= 5 or gcs < 15: return "2", f"NEWS2={news2_score} GCS={gcs}.", "NEWS2/GCS"
        if news2_score >= 1 or eva >= 7:  return "3B", f"EVA={eva} NEWS2={news2_score}.", "NEWS2/EVA"
        if eva >= 4: return "4", f"EVA {eva}/10.", "EVA"
        return "5", "Non urgent.", "Défaut"

    except (TypeError, ValueError) as e:
        # Sécurité : ne jamais laisser crasher le moteur de triage
        return "3B", f"Erreur évaluation ({e}) - triage par défaut conservateur.", "Erreur — Vérifier les paramètres"


# =============================================================================
# ███  MODULE : ALERTES SÉCURITÉ  ███
# Vérification de cohérence clinique et détection d'incompatibilités.
# =============================================================================

def check_coherence(fc, pas, spo2, fr, gcs, temp, s_eva, motif, atcd, details, news2_score):
    """
    Vérifie la cohérence clinique des paramètres saisis.
    Retourne (danger_list, warning_list, info_list).
    Signale les incompatibilités qui pourraient indiquer une erreur de saisie.
    """
    danger, warning, info = [], [], []
    try:
        # Incohérences de saisie
        if s_eva == 0 and fc > 110:
            warning.append("Incohérence : EVA 0 mais FC > 110 — évaluer douleur ou autre cause")
        if gcs == 15 and spo2 < 88:
            warning.append("Incohérence : GCS 15 mais SpO2 < 88% — vérifier capteur")

        # Situations à haut risque
        if "Anticoagulants / AOD" in atcd and "crânien" in motif.lower():
            danger.append("DANGER : TC sous anticoagulants — TDM cérébral URGENT — risque hématome x10")
        if "Anticoagulants / AOD" in atcd and ("AVC" in motif or "neurologique" in motif.lower()):
            danger.append("DANGER : AVC suspect sous AOD — CONTRE-INDICATION thrombolyse — neuro IMMÉDIAT")
        if "allergie" in motif.lower() and details.get("dyspnee"):
            danger.append("ANAPHYLAXIE SÉVÈRE : Adrénaline 0.5 mg IM immédiatement")
        if details.get("mal_score", 0) >= 8 or motif == "Accouchement imminent":
            danger.append("NE PAS TRANSPORTER : Malinas >= 8 — protocole accouchement inopiné")
        if news2_score >= 5 and temp >= 38.5:
            danger.append("SEPSIS GRAVE : NEWS2 >= 5 + fièvre — hémocultures + antibiotiques dans l'heure")
        if pas is not None and pas > 0 and pas < 90 and fc > 100:
            si = round(fc / pas, 1)
            danger.append(f"CHOC probable : Shock Index {si} (FC {fc}/PAS {pas}) — 2 VVP + remplissage NaCl 0.9%")
        if spo2 < 85 or fr >= 40:
            danger.append(f"DÉTRESSE RESPIRATOIRE : SpO2 {spo2}% FR {fr} — O2 haut débit + préparer IOT")
        if gcs <= 8:
            danger.append(f"COMA GCS {gcs} : Protection VA — PLS — intubation à évaluer (REA)")
        if temp <= 32:
            danger.append(f"HYPOTHERMIE SÉVÈRE T {temp}°C : réchauffement actif — risque FV")
        if temp >= 41:
            danger.append(f"HYPERTHERMIE MALIGNE T {temp}°C : refroidissement immédiat")
        if "Immunodépression" in atcd and temp >= 38.5:
            warning.append("NEUTROPÉNIE FÉBRILE possible : Hémogramme urgent + antibiotiques sans attendre")

    except (TypeError, ValueError):
        warning.append("Erreur lors de la vérification de cohérence — vérifier les paramètres saisis")
    return danger, warning, info


# =============================================================================
# ███  MODULE : MOTEUR SBAR — DPI-READY  ███
# Génère une transmission SBAR structurée, prête pour copier-coller en DPI.
# Aucun nom/prénom stocké (RGPD) — identité remplacée par un code anonyme.
# =============================================================================

def generate_sbar(age, motif, cat, atcd, allergies, supp_o2, temp, fc, pas, spo2, fr, gcs,
                  news2, news2_label, eva, eva_echelle, p_pqrst, q_pqrst, r_pqrst, t_onset,
                  details, niveau, tri_label, justif, critere_ref, sector,
                  gcs_y=4, gcs_v=5, gcs_m=6, code_anon="ANON"):
    """
    Génère une transmission SBAR professionnelle et structurée.
    Format DPI-Ready : copier-coller propre dans le dossier patient.

    Structure :
        [S] Situation — contexte immédiat
        [B] Background — antécédents et contexte clinique
        [A] Assessment — évaluation objective des paramètres
        [R] Recommendation — orientation et actes immédiats

    RGPD : Aucun nom/prénom dans le SBAR. Utilisation d'un code anonyme.
    """
    now_str   = datetime.now().strftime("%d/%m/%Y à %H:%M")
    date_str  = datetime.now().strftime("%d/%m/%Y")
    heure_str = datetime.now().strftime("%H:%M")
    atcd_str  = ", ".join(atcd) if atcd else "aucun antécédent notable"
    all_str   = allergies if allergies and allergies != "RAS" else "aucune allergie connue"

    # Conscience
    if gcs == 15: conscience = "conscient et orienté"
    elif gcs >= 13: conscience = f"conscience altérée GCS {gcs} (Y{gcs_y}V{gcs_v}M{gcs_m})"
    elif gcs >= 9:  conscience = f"obnubilé GCS {gcs} (Y{gcs_y}V{gcs_v}M{gcs_m})"
    else:           conscience = f"COMA GCS {gcs} (Y{gcs_y}V{gcs_v}M{gcs_m})"

    # Anomalies vitaux
    anomalies = []
    if temp > 38 or temp < 36: anomalies.append(f"T {temp}°C")
    if fc > 100:  anomalies.append(f"tachycardie {fc} bpm")
    if fc < 60:   anomalies.append(f"bradycardie {fc} bpm")
    if pas < 90:  anomalies.append(f"hypotension {pas} mmHg")
    if pas > 180: anomalies.append(f"HTA {pas} mmHg")
    if spo2 < 94: anomalies.append(f"désaturation {spo2}%")
    if fr > 20:   anomalies.append(f"tachypnée {fr}/min")
    vitaux_txt = "dans les normes" if not anomalies else "ANOMALIES : " + ", ".join(anomalies)

    shock_index = round(fc / pas, 2) if pas and pas > 0 else 0

    # Prescriptions anticipées dans le SBAR (4 premiers gestes)
    rx_txt = ""
    rx = PRESCRIPTIONS_ANTICIPEES.get(motif)
    if rx and rx.get("Gestes immédiats"):
        rx_items = rx["Gestes immédiats"][:4]
        rx_txt = "\n  Prescriptions anticipées IAO :\n" + "\n".join([f"    ☐ {item}" for item in rx_items])

    # Recommandation selon niveau
    if niveau in ['M', '1']:
        reco = "DEMANDE PRISE EN CHARGE IMMÉDIATE EN DÉCHOCAGE."
    elif niveau == '2':
        reco = "Demande évaluation médicale urgente < 20 min."
    elif niveau == '3A':
        reco = "Évaluation dans les 30 min — salle de soins aigus."
    elif niveau == '3B':
        reco = "Évaluation dans l'heure — polyclinique urgences."
    elif niveau == '4':
        reco = "Évaluation dans les 2h — consultation urgences."
    else:
        reco = "Consultation non urgente / réorientation MG."

    return f"""╔══════════════════════════════════════════════════════════╗
║  TRANSMISSION SBAR — AKIR-IAO Project v13.0             ║
║  Service des Urgences                                    ║
║  {date_str} — {heure_str}                                      ║
╚══════════════════════════════════════════════════════════╝

━━━ [S] SITUATION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Code anonyme  : {code_anon}
  Âge           : {age} ans
  Admission     : {now_str}
  Motif         : {motif} ({cat})
  Douleur       : {eva}/10 ({eva_echelle})
  Conscience    : {conscience}
  ► NIVEAU TRI  : {tri_label}

━━━ [B] BACKGROUND ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ATCD          : {atcd_str}
  Allergies     : {all_str}
  O2 à l'admission : {'OUI' if supp_o2 else 'non'}

━━━ [A] ASSESSMENT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Constantes :
    T° {temp}°C | FC {fc} bpm | PAS {pas} mmHg
    SpO2 {spo2}% | FR {fr}/min | GCS {gcs}/15
  Shock Index   : {shock_index}
  Bilan vitaux  : {vitaux_txt}

  NEWS2         : {news2} ({news2_label})

  PQRST :
    P — Provoqué/Pallié : {p_pqrst or 'non précisé'}
    Q — Qualité/Type    : {q_pqrst}
    R — Région/Irrad.   : {r_pqrst or 'non précisé'}
    S — Sévérité        : {eva}/10 ({eva_echelle})
    T — Temps/Durée     : {t_onset or 'non précisé'}

  Justification triage : {justif}
  Référence FRENCH     : {critere_ref}

━━━ [R] RECOMMENDATION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Orientation : {sector}
  ► {reco}
{rx_txt}

──────────────────────────────────────────────────────────
  Signé : Ismaïl Ibn-Daïfa — AKIR-IAO Project v13.0
  Réf. FRENCH Triage SFMU V1.1 — Adaptation SIAMU Belgique
  RGPD : Aucun nom patient dans ce document
──────────────────────────────────────────────────────────
"""


# =============================================================================
# ███  MODULE : BILANS SUGGÉRÉS  ███
# =============================================================================

def suggest_bilan(motif, details, fc, pas, spo2, fr, gcs, temp, age, atcd, news2_score, niveau):
    """Génère les bilans recommandés selon le motif et la gravité du tableau clinique."""
    b = {"Biologie": [], "Imagerie": [], "ECG / Monitoring": [], "Gestes immédiats": [], "Avis spécialiste": []}
    try:
        if niveau in ["M", "1", "2"]:
            b["Biologie"] += ["Hémogramme complet + plaquettes", "Ionogramme, créatinine", "Glycémie", "Groupe RAI"]
            b["ECG / Monitoring"] += ["Monitoring cardiorespiratoire continu", "SpO2 continue", "VVP (gros calibre)"]
        if "thoracique" in motif.lower() or "SCA" in motif:
            b["Biologie"] += ["Troponine Hs T0 et T1h", "D-Dimères si EP", "NT-proBNP si IC"]
            b["ECG / Monitoring"] += ["ECG 12 dérivations URGENT", "Répéter ECG à 30 min"]
            b["Imagerie"] += ["RX thorax face"]
            b["Gestes immédiats"] += ["Aspirine 250 mg si SCA non CI", "O2 si SpO2 < 95%"]
            if "Anticoagulants / AOD" in atcd:
                b["Gestes immédiats"] += ["ATTENTION anticoagulants — adapter HBPM/héparine"]
        if "AVC" in motif or "neurologique" in motif.lower():
            b["Biologie"] += ["Hémogramme + coagulation (TP, TCA, fibrinogène)", "Glycémie"]
            b["Imagerie"] += ["TDM cérébral sans injection URGENT", "IRM si disponible"]
            b["Avis spécialiste"] += ["Neurologue vasculaire urgent"]
            b["Gestes immédiats"] += ["ALERTE FILIÈRE STROKE — door-to-needle < 60 min"]
        if "dyspnée" in motif.lower() or "respiratoire" in motif.lower():
            b["Biologie"] += ["Gazométrie artérielle", "D-Dimères si EP"]
            b["Imagerie"] += ["RX thorax", "Échographie pulmonaire si dispo"]
            b["Gestes immédiats"] += ["O2 — objectif SpO2 > 94%", "Position semi-assise (Fowler)"]
        if "traumatisme" in motif.lower() and niveau in ["M", "1", "2"]:
            b["Biologie"] += ["Bilan pré-transfusionnel (groupe, Rh, RAI, Coombs)", "Lactates"]
            b["Imagerie"] += ["CT-scanner corps entier si polytrauma", "Échographie FAST"]
            b["Gestes immédiats"] += ["Compression directe hémorragie + garrot si membre", "2 VVP + remplissage NaCl 0.9%"]
        if "fièvre" in motif.lower() or (temp >= 38.5 and news2_score >= 3):
            b["Biologie"] += ["Hémocultures x2 AVANT antibiotiques", "Lactates", "CRP, PCT, hémogramme"]
            b["Gestes immédiats"] += ["Hémocultures AVANT antibiothérapie", "Antibiotiques large spectre si sepsis grave"]
        if "allergie" in motif.lower():
            b["Gestes immédiats"] += ["ADRÉNALINE 0.5 mg IM", "Antihistaminique + corticoïdes IV", "Remplissage NaCl 0.9%"]
        if "hypoglycémie" in motif.lower():
            b["Gestes immédiats"] += ["Glycémie capillaire IMMÉDIATE", "Glucose 30% 50mL IV si inconscient", "Glucagon 1mg IM/SC si pas d'accès"]
        if "intoxication" in motif.lower():
            b["Biologie"] += ["Screening toxicologique urinaire + sanguin", "Paracétamol + éthanol systématiques"]
            b["ECG / Monitoring"] += ["ECG — toxiques cardiotropes"]
            b["Avis spécialiste"] += ["Centre Antipoisons (070 245 245)"]
    except (TypeError, ValueError):
        pass
    return {k: v for k, v in b.items() if v}


# =============================================================================
# ███  MODULE : BADGES ET COMPOSANTS UI  ███
# =============================================================================

def vital_badge(val, lw, lc, hw, hc, u=""):
    """Retourne un badge HTML coloré pour les alertes des signes vitaux."""
    try:
        if val <= lc or val >= hc: return f'<span class="vital-alert vital-crit">! {val}{u}</span>'
        if val <= lw or val >= hw: return f'<span class="vital-alert vital-warn">~ {val}{u}</span>'
        return f'<span class="vital-alert vital-ok">ok</span>'
    except (TypeError, ValueError):
        return '<span class="vital-alert vital-warn">?</span>'


def score_badge_custom(label, css_class):
    """Retourne un badge HTML pour l'affichage d'un score générique."""
    return f'<div class="score-result {css_class}">{label}</div>'


# =============================================================================
# ███  MODULE : RENDU COMPOSANTS STREAMLIT  ███
# Séparation stricte entre logique (moteur) et affichage (Streamlit).
# =============================================================================

def render_news2_critical_alert(news2_score):
    """
    Affiche la bannière rouge clignotante si NEWS2 >= 7.
    Sécurité clinique critique : alerte visuelle majeure inamovible.
    """
    if news2_score >= 7:
        st.markdown(
            f'<div class="critical-alert-banner">'
            f'<div class="critical-alert-title">🚨 ALERTE CRITIQUE — NEWS2 = {news2_score}</div>'
            f'<div class="critical-alert-sub">Appel médical immédiat requis — Transfert déchocage IMMÉDIAT — Médecin senior</div>'
            f'</div>',
            unsafe_allow_html=True
        )


def render_danger_banners(news2_score, sil_score, niveau, fc, pas, spo2, fr, gcs, temp):
    """Affiche les bandeaux d'alerte colorés selon les paramètres vitaux."""
    banners = []

    # Bannière critique NEWS2 >= 7 (priorité absolue)
    if news2_score >= 7:
        render_news2_critical_alert(news2_score)
    elif news2_score >= 5:
        banners.append(
            f'<div class="warning-banner">'
            f'<div class="warning-banner-title">△ ALERTE — NEWS2 = {news2_score}</div>'
            f'<div class="warning-banner-detail">Évaluation médicale urgente requise dans les 30 minutes</div>'
            f'</div>'
        )

    # Silverman néonatal
    if sil_score is not None and sil_score >= 5:
        banners.append(
            f'<div class="danger-banner">'
            f'<div class="danger-banner-title">⚠ DÉTRESSE NÉONATALE — Silverman = {sil_score}/10</div>'
            f'<div class="danger-banner-detail">Appel pédiatre / néonatologiste IMMÉDIAT — Préparer réanimation néonatale</div>'
            f'</div>'
        )

    # Choc hémodynamique
    if pas and pas > 0 and fc / pas >= 1.0:
        si = round(fc / pas, 1)
        banners.append(
            f'<div class="danger-banner">'
            f'<div class="danger-banner-title">⚠ CHOC — Shock Index = {si}</div>'
            f'<div class="danger-banner-detail">FC {fc} / PAS {pas} — 2 VVP gros calibre + remplissage NaCl 0.9%</div>'
            f'</div>'
        )

    # Détresse respiratoire sévère
    if spo2 < 85 or fr >= 40:
        banners.append(
            f'<div class="danger-banner">'
            f'<div class="danger-banner-title">⚠ DÉTRESSE RESPIRATOIRE — SpO2 {spo2}% / FR {fr}</div>'
            f'<div class="danger-banner-detail">O2 haut débit immédiat — Préparer IOT si échec</div>'
            f'</div>'
        )

    # Coma
    if gcs <= 8:
        banners.append(
            f'<div class="danger-banner">'
            f'<div class="danger-banner-title">⚠ COMA — GCS {gcs}/15</div>'
            f'<div class="danger-banner-detail">Protection voies aériennes — PLS — Évaluer intubation</div>'
            f'</div>'
        )

    for b in banners:
        st.markdown(b, unsafe_allow_html=True)
    return len(banners) > 0


def render_protocole_anticipe_douleur_thoracique(frcv_count, details):
    """
    Affiche le protocole anticipé spécifique à la douleur thoracique.
    Si >= 2 FRCV cochés, suggère une remontée du niveau de tri.
    """
    st.markdown(
        '<div class="protocole-anticipe">'
        '<div class="protocole-anticipe-title">⚠ PROTOCOLE ANTICIPÉ — Douleur Thoracique / SCA</div>'
        '<div class="protocole-item protocole-urgent">ECG immédiat (< 10 min de l\'arrivée)</div>'
        '<div class="protocole-item protocole-urgent">Pose VVP 18G minimum</div>'
        '<div class="protocole-item protocole-urgent">Bilan bio : Troponine Hs T0, D-Dimères, NFS</div>'
        '<div class="protocole-item">Monitoring scope continu</div>'
        '<div class="protocole-item">Aspirine 250 mg PO/IV sauf CI</div>'
        '</div>',
        unsafe_allow_html=True
    )
    if frcv_count >= 2:
        st.markdown(
            f'<div class="alert-danger">⬆ REMONTÉE TRI SUGGÉRÉE : {frcv_count} facteurs de risque CV cochés avec douleur thoracique — Considérer Tri 3A minimum</div>',
            unsafe_allow_html=True
        )


def render_prescriptions_anticipees(motif):
    """Affiche les prescriptions anticipées IAO pour le motif sélectionné."""
    rx = PRESCRIPTIONS_ANTICIPEES.get(motif)
    if not rx:
        return
    st.markdown('<div class="section-header">Prescriptions anticipées IAO</div>', unsafe_allow_html=True)
    cols = st.columns(min(len(rx), 3))
    for i, (category, items) in enumerate(rx.items()):
        col = cols[i % len(cols)]
        is_urgent = category in ["Gestes immédiats", "Rappels critiques"]
        items_html = ""
        for item in items:
            item_class = "rx-item-urgent" if is_urgent else "rx-item"
            items_html += f'<div class="{item_class}">{item}</div>'
        col.markdown(
            f'<div class="rx-card">'
            f'<div class="rx-title">{category}</div>'
            f'{items_html}'
            f'</div>',
            unsafe_allow_html=True
        )


def render_infobulles_news2():
    """Affiche les critères officiels de calcul du score NEWS2."""
    st.markdown(
        '<div class="infobulles-score">'
        '<b>ℹ Score NEWS2 — Critères officiels (Royal College of Physicians, 2017)</b><br>'
        '• FR : 0 pt (12-20) | 1 pt (9-11 ou 21-24) | 2 pt (25+) | 3 pt (≤8)<br>'
        '• SpO2 (sans BPCO) : 0 pt (≥96%) | 1 pt (94-95%) | 2 pt (92-93%) | 3 pt (≤91%)<br>'
        '• O2 supplémentaire : +2 pts<br>'
        '• Température : 0 pt (36.1-38.0) | 1 pt (35.1-36.0 ou 38.1-39.0) | 2 pt (≥39.1) | 3 pt (≤35.0)<br>'
        '• PAS : 0 pt (111-219) | 1 pt (101-110) | 2 pt (91-100) | 3 pt (≤90 ou ≥220)<br>'
        '• FC : 0 pt (51-90) | 1 pt (41-50 ou 91-110) | 2 pt (111-130) | 3 pt (≤40 ou ≥131)<br>'
        '• Conscience : 0 pt (A — alerte) | 3 pts (GCS < 15)<br>'
        '<b>Seuils d\'alerte :</b> 1-4 = faible | 5-6 = modéré | 7-8 = élevé | ≥9 = critique'
        '</div>',
        unsafe_allow_html=True
    )


def render_infobulles_timi():
    """Affiche les critères officiels du score TIMI pour SCA-ST-."""
    st.markdown(
        '<div class="infobulles-score">'
        '<b>ℹ Score TIMI — Risque SCA-ST- (Antman et al., JAMA 2000)</b><br>'
        '• 1 pt : Âge ≥ 65 ans<br>'
        '• 1 pt : ≥ 3 facteurs de risque coronarien (HTA, tabac, diabète, ATCD fam., dyslipidémie)<br>'
        '• 1 pt : Sténose coronaire connue ≥ 50%<br>'
        '• 1 pt : Déviation ST ≥ 0.5 mm à l\'ECG<br>'
        '• 1 pt : ≥ 2 crises angor en 24h<br>'
        '• 1 pt : Utilisation aspirine dans les 7 derniers jours<br>'
        '• 1 pt : Biomarqueurs cardiaques élevés (Troponine+)<br>'
        '<b>Risque :</b> 0-2 = faible | 3-4 = intermédiaire | 5-7 = élevé'
        '</div>',
        unsafe_allow_html=True
    )


def render_disclaimer():
    """Affiche le disclaimer juridique RGPD obligatoire en bas de page."""
    st.markdown(
        '<div class="disclaimer-rgpd">'
        '<div class="disclaimer-title">⚖ Avertissement juridique, clinique & RGPD</div>'
        'AKIR-IAO Project est un outil d\'aide à la décision clinique destiné aux infirmier(e)s '
        'agréé(e)s exerçant en service d\'accueil des urgences (SAU). Il ne se substitue en aucun cas au '
        'jugement clinique du professionnel de santé ni à l\'examen médical. Les niveaux de triage proposés '
        'sont fondés sur la grille FRENCH Triage (SFMU V1.1, 2018) et doivent être validés par l\'IAO '
        'en fonction du contexte clinique. Les prescriptions anticipées sont des rappels et ne constituent '
        'pas des prescriptions médicales : elles doivent être validées par le médecin responsable. '
        'L\'utilisation de cet outil engage la responsabilité de l\'utilisateur. '
        'En cas de doute, toujours sur-trier et demander un avis médical.'
        '<div class="akir-signature">'
        '⚕ AKIR-IAO Project — par Ismaïl Ibn-Daïfa<br>'
        'Outil d\'aide à la décision | Conformité RGPD : Aucune donnée patient n\'est stockée sur serveur.'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


def render_fiche_tri(age, motif, niveau, tri_label, sector, temp, fc, pas, spo2, fr, gcs,
                     news2, news2_label, eva, atcd, allergies, arrivee_str, details, code_anon="ANON"):
    """Génère le HTML de la fiche de tri (affichage en mode impression)."""
    atcd_str = ", ".join(atcd) if atcd else "RAS"
    all_str  = allergies if allergies != "RAS" else "Aucune connue"
    return f"""
<div class="fiche-tri">
  <div class="fiche-header">
    <div class="fiche-title">FICHE DE TRI — AKIR-IAO Project v13.0</div>
    <div style="font-size:0.75rem;color:#64748b;">{arrivee_str}</div>
  </div>
  <div class="fiche-niveau fiche-{niveau}">{TRI_EMOJI.get(niveau, '')} {tri_label}</div>
  <div class="fiche-section">PATIENT (ANONYME)</div>
  <div class="fiche-row"><span>Code</span><span><b>{code_anon}</b></span></div>
  <div class="fiche-row"><span>Âge</span><span>{age} ans</span></div>
  <div class="fiche-row"><span>Motif</span><span><b>{motif}</b></span></div>
  <div class="fiche-row"><span>Allergies</span><span style="color:#dc2626;font-weight:600">{all_str}</span></div>
  <div class="fiche-row"><span>ATCD</span><span>{atcd_str}</span></div>
  <div class="fiche-section">CONSTANTES</div>
  <div class="fiche-row"><span>T°</span><span>{temp} °C</span></div>
  <div class="fiche-row"><span>FC</span><span>{fc} bpm</span></div>
  <div class="fiche-row"><span>PAS</span><span>{pas} mmHg</span></div>
  <div class="fiche-row"><span>SpO2</span><span>{spo2} %</span></div>
  <div class="fiche-row"><span>FR</span><span>{fr} resp/min</span></div>
  <div class="fiche-row"><span>GCS</span><span>{gcs}/15</span></div>
  <div class="fiche-row"><span>NEWS2</span><span>{news2} — {news2_label}</span></div>
  <div class="fiche-row"><span>EVA/FLACC</span><span>{eva}/10</span></div>
  <div class="fiche-section">ORIENTATION</div>
  <div class="fiche-row"><span>Secteur</span><span><b>{sector}</b></span></div>
  <div style="font-size:0.7rem;color:#94a3b8;margin-top:10px;text-align:center;">
    FRENCH Triage — AKIR-IAO Project — Ismaïl Ibn-Daïfa — RGPD : données anonymes
  </div>
</div>
"""


# =============================================================================
# ÉCHELLE DOULEUR ADAPTÉE À L'ÂGE
# =============================================================================

def echelle_douleur(age_patient):
    """Retourne (score, echelle_nom, interpretation, css_class) selon l'âge du patient."""
    if age_patient < 3:
        st.markdown("**Échelle FLACC** *(< 3 ans — observation comportementale)*")
        items = {
            "Visage (grimace, froncement)":    ["0 - Aucune expression", "1 - Grimace occasionnelle", "2 - Froncement permanent"],
            "Jambes (agitation)":              ["0 - Position normale", "1 - Gênées, agitées", "2 - Crispées / ruades"],
            "Activité (position corps)":       ["0 - Allongé, calme", "1 - Se tortille / arquée", "2 - Rigide / convulsive"],
            "Pleurs":                          ["0 - Pas de pleurs", "1 - Gémissements", "2 - Pleurs continus"],
            "Consolabilité":                   ["0 - Calme facilement", "1 - Difficile à calmer", "2 - Inconsolable"],
        }
        total = 0
        ca, cb = st.columns(2)
        for i, (lbl, opts) in enumerate(items.items()):
            col = ca if i < 3 else cb
            v = col.selectbox(lbl, opts, key=f"flacc_{i}")
            total += int(v[0])
        if total <= 2:   interp, css = "Douleur légère / absente", "score-low"
        elif total <= 6: interp, css = "Douleur modérée — antalgiques niveau 1 OMS", "score-med"
        else:            interp, css = "Douleur sévère — antalgiques IV urgents", "score-high"
        return total, "FLACC", interp, css
    elif age_patient < 8:
        st.markdown("**Échelle des visages Wong-Baker** *(3-8 ans)*")
        st.caption("Montrer les visages et demander : *Quel visage montre comment tu te sens ?*")
        faces = {
            "0 - Très heureux, pas de douleur": 0,
            "2 - Un peu de douleur": 2,
            "4 - Douleur un peu plus forte": 4,
            "6 - Douleur encore plus forte": 6,
            "8 - Beaucoup de douleur": 8,
            "10 - Douleur insupportable": 10,
        }
        choix = st.selectbox("Visage choisi par l'enfant", list(faces.keys()), key="wong_baker")
        score = faces[choix]
        if score <= 2:  interp, css = "Douleur légère", "score-low"
        elif score <= 6: interp, css = "Douleur modérée", "score-med"
        else:            interp, css = "Douleur sévère", "score-high"
        return score, "Wong-Baker", interp, css
    else:
        st.markdown("**Échelle Visuelle Analogique (EVA)** *(≥ 8 ans)*")
        eva_options = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        c1, c2 = st.columns([3, 1])
        with c1:
            score_str = st.select_slider(
                "Douleur de 0 (aucune) à 10 (maximale)",
                options=eva_options,
                value="0",
                key="eva_std"
            )
        score = int(score_str)
        emoji_map = {0: "😌", 1: "🙂", 2: "🙂", 3: "😐", 4: "😐", 5: "😟", 6: "😟", 7: "😣", 8: "😣", 9: "😫", 10: "😭"}
        with c2:
            st.markdown(f"### {emoji_map.get(score, '😐')} {score}/10")
        if score <= 3:   interp, css = "Douleur légère — niveau 1 OMS", "score-low"
        elif score <= 6: interp, css = "Douleur modérée — niveau 1-2 OMS", "score-med"
        else:            interp, css = "Douleur sévère — niveau 2-3 OMS ou IV", "score-high"
        return score, "EVA", interp, css


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown("## ⚕ AKIR-IAO Project")
    st.caption("v13.0 Elite Edition — FRENCH Triage SFMU V1.1")

    st.markdown('<div class="section-header">Mode</div>', unsafe_allow_html=True)
    mode = st.radio("Interface", ["Tri Rapide (< 2 min)", "Complet"], horizontal=True, label_visibility="collapsed")
    st.session_state.mode = "rapide" if "Rapide" in mode else "complet"

    st.markdown('<div class="section-header">Chronomètre</div>', unsafe_allow_html=True)
    ca, cb = st.columns(2)
    if ca.button("Démarrer", use_container_width=True):
        st.session_state.arrival_time = datetime.now()
        st.session_state.last_reeval  = datetime.now()
        st.session_state.reeval_history = []
    if cb.button("Reset", use_container_width=True):
        st.session_state.arrival_time = None
        st.session_state.last_reeval  = None
        st.session_state.reeval_history = []

    if st.session_state.arrival_time:
        elapsed = datetime.now() - st.session_state.arrival_time
        m, s = divmod(int(elapsed.total_seconds()), 60)
        h, m = divmod(m, 60)
        st.markdown(f'<div class="chrono">{h:02d}:{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chrono-label">Arrivée {st.session_state.arrival_time.strftime("%H:%M")}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="chrono">--:--:--</div>', unsafe_allow_html=True)
        st.markdown('<div class="chrono-label">En attente</div>', unsafe_allow_html=True)

    # RGPD : Pas de champ nom/prénom — identité anonyme uniquement
    st.markdown('<div class="section-header">Patient (Anonyme — RGPD)</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-info">🔒 RGPD : Aucun nom/prénom collecté. Identité remplacée par un code anonyme.</div>', unsafe_allow_html=True)
    age      = st.number_input("Âge", 0, 120, 45)
    atcd     = st.multiselect("Antécédents / Facteurs de risque", [
        "HTA", "Diabète", "Tabac", "Dyslipidémie", "ATCD familial coronarien",
        "Insuffisance Cardiaque", "BPCO",
        "Anticoagulants / AOD", "Grossesse", "Immunodépression", "Néoplasie"
    ])
    allergies = st.text_input("Allergies", "RAS")
    supp_o2   = st.checkbox("O2 supplémentaire à l'admission")

    db_count = len(load_patient_db())
    st.markdown(f'<div class="section-header">Registre : {db_count} patient(s)</div>', unsafe_allow_html=True)

    st.markdown('<div class="legal-text">FRENCH Triage (adapt. SIAMU Belgique) — Réf. SFMU V1.1</div>', unsafe_allow_html=True)
    st.markdown('<div class="signature">⚕ Ismaïl Ibn-Daïfa<br>Développeur — AKIR-IAO Project</div>', unsafe_allow_html=True)


# =============================================================================
# TABS PRINCIPAUX
# =============================================================================
if st.session_state.mode == "rapide":
    tabs = st.tabs(["⚡ Tri Rapide", "🔄 Réévaluation", "📋 Historique", "🗃️ Registre", "💊 Perfusion"])
    t_rapide, t_reeval, t_history, t_registre, t_perfusion = tabs
    t_complet = t_scores = None
else:
    tabs = st.tabs([
        "📊 Signes Vitaux", "🔍 Anamnèse", "⚖️ Triage & SBAR",
        "🧮 Scores", "💊 Perfusion", "🔄 Réévaluation",
        f"📋 Historique ({len(st.session_state.patient_history)})", "🗃️ Registre"
    ])
    t_vitals, t_anamnesis, t_decision, t_scores, t_perfusion, t_reeval, t_history, t_registre = tabs
    t_rapide = None

# Valeurs par défaut des constantes (remplies dans les tabs)
temp = fc = pas = spo2 = fr = gcs = None


# =============================================================================
# ⚡ MODE TRI RAPIDE
# =============================================================================
if st.session_state.mode == "rapide":
    with t_rapide:
        st.markdown('<div class="tri-rapide-title">TRI RAPIDE — Saisie optimisée < 2 minutes</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">1. Constantes vitales</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        temp = c1.number_input("T° (°C)", 30.0, 45.0, 37.0, 0.1, key="r_temp")
        fc   = c2.number_input("FC (bpm)", 20, 220, 80, key="r_fc")
        pas  = c3.number_input("PAS (mmHg)", 40, 260, 120, key="r_pas")
        c4, c5, c6 = st.columns(3)
        spo2 = c4.number_input("SpO2 %", 50, 100, 98, key="r_spo2")
        fr   = c5.number_input("FR (/min)", 5, 60, 16, key="r_fr")
        gcs  = c6.number_input("GCS", 3, 15, 15, key="r_gcs")

        si = round(fc / pas, 2) if pas > 0 else 0
        si_css = "vital-crit" if si >= 1.0 else ("vital-warn" if si >= 0.8 else "vital-ok")
        st.markdown(f'Shock Index : <span class="vital-alert {si_css}">{si}</span>', unsafe_allow_html=True)

        bpco_flag = "BPCO" in atcd
        news2, news2_warnings = compute_news2(fr, spo2, supp_o2, temp, pas, fc, gcs, bpco_flag)
        news2_label, news2_class = news2_level(news2)

        # Avertissements données manquantes
        for w in news2_warnings:
            st.markdown(f'<div class="alert-warning">{w}</div>', unsafe_allow_html=True)

        cn, ci = st.columns([1, 2])
        cn.markdown(f'<div class="news2-badge {news2_class}">{news2_label}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">2. Motif principal</div>', unsafe_allow_html=True)
        MOTIFS_RAPIDES = [
            "Douleur thoracique / SCA", "Dyspnée / insuffisance respiratoire",
            "AVC / Déficit neurologique", "Altération de conscience / Coma",
            "Traumatisme crânien", "Hypotension artérielle", "Tachycardie / tachyarythmie",
            "Fièvre", "Douleur abdominale", "Allergie / anaphylaxie",
            "Hypoglycémie", "Convulsions", "Autres"
        ]
        motif = st.selectbox("Motif de recours", MOTIFS_RAPIDES, key="r_motif")
        cat   = "RAPIDE"

        # EVA rapide
        eva_score = st.select_slider("EVA", options=[str(i) for i in range(11)], value="0", key="r_eva")
        eva_score = int(eva_score)
        eva_echelle = "EVA"

        details = {"eva": eva_score}

        # Protocole anticipé douleur thoracique avec FRCV
        if motif == "Douleur thoracique / SCA":
            st.markdown('<div class="section-header">Facteurs de risque cardiovasculaires</div>', unsafe_allow_html=True)
            frcv_cols = st.columns(4)
            frcv_hta     = frcv_cols[0].checkbox("HTA", key="r_frcv_hta")
            frcv_diab    = frcv_cols[1].checkbox("Diabète", key="r_frcv_diab")
            frcv_tabac   = frcv_cols[2].checkbox("Tabac", key="r_frcv_tabac")
            frcv_atcd    = frcv_cols[3].checkbox("ATCD coronarien", key="r_frcv_atcd")
            frcv_count   = sum([frcv_hta, frcv_diab, frcv_tabac, frcv_atcd,
                                "HTA" in atcd, "Diabète" in atcd, "Tabac" in atcd, "ATCD familial coronarien" in atcd])
            details["frcv_count"] = frcv_count
            render_protocole_anticipe_douleur_thoracique(frcv_count, details)

        if st.button("⚡ CALCULER LE TRI", type="primary", use_container_width=True):
            niveau, justif, critere_ref = french_triage(motif, details, fc, pas, spo2, fr, gcs, temp, age, news2)
            tri_label = TRI_LABELS[niveau]
            sector    = TRI_SECTORS[niveau]
            emoji     = TRI_EMOJI[niveau]

            render_danger_banners(news2, None, niveau, fc, pas, spo2, fr, gcs, temp)

            st.markdown(
                f'<div class="triage-box {TRI_BOX_CSS[niveau]}">'
                f'<div style="font-size:1.8rem;font-weight:600">{emoji} {tri_label}</div>'
                f'<div style="font-size:0.85rem;margin-top:8px;opacity:.85">NEWS2 {news2} | EVA {eva_score}/10</div>'
                f'<div style="font-size:0.82rem;margin-top:8px;font-style:italic">{justif}</div>'
                f'</div>', unsafe_allow_html=True
            )
            st.info(f"**Orientation :** {sector}")

            # SBAR généré automatiquement
            code_anon = f"PT-{datetime.now().strftime('%H%M%S')}"
            sbar = generate_sbar(
                age, motif, cat, atcd, allergies, supp_o2, temp, fc, pas, spo2, fr, gcs,
                news2, news2_label, eva_score, eva_echelle,
                "", "Non précisé", "", "",
                details, niveau, tri_label, justif, critere_ref, sector,
                code_anon=code_anon
            )
            st.session_state.sbar_text = sbar

            # Historique session
            snap_hist = {
                "heure": datetime.now().strftime("%H:%M"), "age": age, "motif": motif,
                "cat": cat, "eva": eva_score, "news2": news2, "niveau": niveau,
                "temp": temp, "fc": fc, "pas": pas, "spo2": spo2, "fr": fr, "gcs": gcs,
                "atcd": atcd, "allergies": allergies, "sbar": sbar, "alertes_danger": 0,
            }
            st.session_state.patient_history.insert(0, snap_hist)

        if st.session_state.sbar_text:
            st.markdown('<div class="section-header">Transmission SBAR — DPI-Ready</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sbar-block">{st.session_state.sbar_text}</div>', unsafe_allow_html=True)
            st.download_button(
                "📋 Télécharger SBAR (.txt)",
                data=st.session_state.sbar_text,
                file_name=f"SBAR_AKIR_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True,
            )

        render_disclaimer()


# =============================================================================
# MODE COMPLET — TABS
# =============================================================================
else:
    # ── TAB 1 : SIGNES VITAUX ────────────────────────────────────────────────
    with t_vitals:
        st.markdown('<div class="section-header">Constantes vitales</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        temp = c1.number_input("Température (°C)", 30.0, 45.0, 37.0, 0.1)
        fc   = c1.number_input("FC (bpm)", 20, 220, 80)
        pas  = c2.number_input("PAS Systolique (mmHg)", 40, 260, 120)
        spo2 = c2.number_input("SpO2 (%)", 50, 100, 98)
        fr   = c3.number_input("FR (resp/min)", 5, 60, 16)
        gcs  = c3.number_input("Glasgow (3-15)", 3, 15, 15)

        st.markdown('<div class="section-header">Alertes & Shock Index</div>', unsafe_allow_html=True)
        a1, a2, a3, a4, a5 = st.columns(5)
        a1.markdown(f"**T°** {vital_badge(temp, 36, 35, 38, 40.5, '°C')}", unsafe_allow_html=True)
        a2.markdown(f"**FC** {vital_badge(fc, 50, 40, 100, 130, '')}", unsafe_allow_html=True)
        a3.markdown(f"**PAS** {vital_badge(pas, 100, 90, 180, 220, '')}", unsafe_allow_html=True)
        a4.markdown(f"**SpO2** {vital_badge(spo2, 94, 90, 100, 100, '%')}", unsafe_allow_html=True)
        a5.markdown(f"**FR** {vital_badge(fr, 12, 8, 20, 25, '')}", unsafe_allow_html=True)
        si = round(fc / pas, 2) if pas > 0 else 0
        si_css = "vital-crit" if si >= 1.0 else ("vital-warn" if si >= 0.8 else "vital-ok")
        st.markdown(f'**Shock Index** : <span class="vital-alert {si_css}">{si}</span>{"  ⚠ CHOC probable" if si >= 1 else ""}', unsafe_allow_html=True)

        bpco_flag = "BPCO" in atcd
        news2, news2_warnings = compute_news2(fr, spo2, supp_o2, temp, pas, fc, gcs, bpco_flag)
        news2_label, news2_class = news2_level(news2)

        st.markdown('<div class="section-header">Score NEWS2</div>', unsafe_allow_html=True)

        # Info-bulle NEWS2
        with st.expander("ℹ Critères officiels NEWS2 — cliquer pour afficher"):
            render_infobulles_news2()

        for w in news2_warnings:
            st.markdown(f'<div class="alert-warning">{w}</div>', unsafe_allow_html=True)

        cn, ci = st.columns([1, 2])
        cn.markdown(f'<div class="news2-badge {news2_class}">{news2_label}</div>', unsafe_allow_html=True)
        interp_map = {
            "news2-low":  ("Standard", "Réévaluation >= 12h."),
            "news2-med":  ("Rapprochée", "Réévaluation 1h."),
            "news2-high": ("Urgente", "Évaluation médicale immédiate."),
            "news2-crit": ("URGENCE ABSOLUE", "Transfert déchocage immédiat."),
        }
        ti, di = interp_map[news2_class]
        ci.markdown(f"**{ti}**")
        ci.markdown(di)

        render_danger_banners(news2, None, None, fc, pas, spo2, fr, gcs, temp)

    # ── TAB 2 : ANAMNÈSE ─────────────────────────────────────────────────────
    with t_anamnesis:
        if temp is None: temp = 37.0
        if fc   is None: fc   = 80
        if pas  is None: pas  = 120
        if spo2 is None: spo2 = 98
        if fr   is None: fr   = 16
        if gcs  is None: gcs  = 15

        st.markdown('<div class="section-header">Évaluation de la douleur (adaptée à l\'âge)</div>', unsafe_allow_html=True)
        eva_score, eva_echelle, eva_interp, eva_css = echelle_douleur(age)
        st.markdown(f'<div class="score-result {eva_css}">{eva_score}/10 ({eva_echelle})</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="score-interp">→ {eva_interp}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">PQRST</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            p_pqrst = st.text_input("P — Provoqué / Pallié par", placeholder="Repos, effort...")
            q_pqrst = st.selectbox("Q — Qualité / Type", ["Sourd", "Étau", "Brûlure", "Coup de poignard", "Électrique", "Tension", "Pesanteur", "Crampe"])
            r_pqrst = st.text_input("R — Région / Irradiation", placeholder="Bras, mâchoire, dos...")
        with c2:
            t_onset = st.text_input("T — Temps", placeholder="Depuis 30 min, brutal...")

        st.markdown('<div class="section-header">Motif & Questions guidées FRENCH</div>', unsafe_allow_html=True)
        MOTIFS_DICT = {
            "CARDIO-CIRCULATOIRE": ["Arrêt cardiorespiratoire", "Hypotension artérielle", "Douleur thoracique / SCA",
                                    "Tachycardie / tachyarythmie", "Bradycardie / bradyarythmie",
                                    "Hypertension artérielle", "Dyspnée / insuffisance respiratoire", "Palpitations"],
            "RESPIRATOIRE": ["Asthme / aggravation BPCO", "Hémoptysie", "Corps étranger voies aériennes"],
            "NEUROLOGIE": ["AVC / Déficit neurologique", "Altération de conscience / Coma", "Convulsions",
                           "Céphalée", "Vertiges / trouble de l'équilibre", "Confusion / désorientation"],
            "TRAUMATOLOGIE": ["Traumatisme avec amputation", "Traumatisme abdomen / thorax / cervical",
                              "Traumatisme crânien", "Brûlure",
                              "Traumatisme bassin / hanche / fémur / rachis",
                              "Traumatisme membre / épaule", "Plaie", "Électrisation", "Agression sexuelle / sévices"],
            "ABDOMINAL": ["Hématémèse / vomissement de sang", "Rectorragie / méléna", "Douleur abdominale"],
            "GÉNITO-URINAIRE": ["Douleur lombaire / colique néphrétique", "Rétention d'urine / anurie",
                                "Douleur testiculaire / torsion", "Hématurie"],
            "GYNÉCO-OBSTÉTRIQUE": ["Accouchement imminent", "Problème de grossesse (1er/2ème trimestre)",
                                   "Problème de grossesse (3ème trimestre)", "Méno-métrorragie"],
            "PSYCHIATRIE / INTOXICATION": ["Idée / comportement suicidaire", "Troubles du comportement / psychiatrie",
                                           "Intoxication médicamenteuse", "Intoxication non médicamenteuse"],
            "INFECTIOLOGIE": ["Fièvre"],
            "DIVERS MÉTABOLIQUES": ["Hyperglycémie", "Hypoglycémie", "Hypothermie",
                                    "Coup de chaleur / insolation", "Allergie / anaphylaxie"],
            "ORL / OPHTALMO": ["Épistaxis", "Corps étranger / brûlure oculaire", "Trouble visuel / cécité"],
        }
        cat   = st.selectbox("Catégorie", list(MOTIFS_DICT.keys()))
        motif = st.selectbox("Motif de recours", MOTIFS_DICT[cat])

        score_hints = {
            "Douleur thoracique / SCA": "ℹ Score TIMI recommandé (onglet Scores)",
            "Accouchement imminent": "ℹ Score Malinas recommandé (onglet Scores)",
            "Brûlure": "ℹ Score Brûlure + Baux recommandé (onglet Scores)",
            "Altération de conscience / Coma": "ℹ Glasgow détaillé recommandé (onglet Scores)",
        }
        if motif in score_hints:
            st.markdown(f'<div class="alert-info">💡 {score_hints[motif]}</div>', unsafe_allow_html=True)

        # Protocole anticipé douleur thoracique avec FRCV + comorbidités
        if motif == "Douleur thoracique / SCA":
            st.markdown('<div class="section-header">Facteurs de risque cardiovasculaires (FRCV)</div>', unsafe_allow_html=True)
            st.caption("⚠ Si ≥ 2 FRCV cochés avec douleur thoracique, le niveau de tri sera automatiquement remonté.")
            frcv_cols = st.columns(4)
            frcv_hta     = frcv_cols[0].checkbox("HTA", key="c_frcv_hta", value="HTA" in atcd)
            frcv_diab    = frcv_cols[1].checkbox("Diabète", key="c_frcv_diab", value="Diabète" in atcd)
            frcv_tabac   = frcv_cols[2].checkbox("Tabac", key="c_frcv_tabac", value="Tabac" in atcd)
            frcv_atcd    = frcv_cols[3].checkbox("ATCD coronarien", key="c_frcv_atcd")
            frcv_dyslipi = st.checkbox("Dyslipidémie", key="c_frcv_dyslipi", value="Dyslipidémie" in atcd)
            frcv_count   = sum([frcv_hta, frcv_diab, frcv_tabac, frcv_atcd, frcv_dyslipi])

        # Prescriptions anticipées automatiques selon motif
        render_prescriptions_anticipees(motif)

        details = {"eva": eva_score}
        if motif == "Douleur thoracique / SCA":
            details["frcv_count"] = frcv_count
            render_protocole_anticipe_douleur_thoracique(frcv_count, details)

        questions = QUESTIONS_GUIDEES.get(motif, [])
        if questions:
            st.markdown("**Questions discriminantes automatiques :**")
            cq1, cq2 = st.columns(2)
            for i, (label, key, typ) in enumerate(questions):
                col = cq1 if i % 2 == 0 else cq2
                details[key] = col.checkbox(label, key=f"qg_c_{key}")

        # Questions spécifiques par motif
        if motif == "Douleur thoracique / SCA":
            details['ecg']                    = st.selectbox("ECG", ["Normal", "Anormal typique SCA", "Anormal non typique"])
            details['douleur_type']           = st.selectbox("Type douleur", ["Atypique", "Typique persistante/intense", "Type coronaire"])
            details['comorbidites_coronaires'] = st.checkbox("Comorbidités coronaires connues")
        elif motif == "Dyspnée / insuffisance respiratoire":
            details['parole_ok'] = st.radio("Parler en phrases complètes ?", [True, False], format_func=lambda x: "Oui" if x else "Non", horizontal=True)
            c1a, c1b = st.columns(2)
            details['orthopnee'] = c1a.checkbox("Orthopnée")
            details['tirage']    = c1b.checkbox("Tirage intercostal")
        elif motif == "AVC / Déficit neurologique":
            details['delai_heures'] = st.number_input("Délai depuis début (heures)", 0.0, 72.0, 2.0, 0.5)
        elif motif == "Traumatisme crânien":
            c1a, c1b = st.columns(2)
            details['pdc']               = c1a.checkbox("PDC initiale")
            details['vomissements_repetes'] = c1a.checkbox("Vomissements répétés")
            details['aod_avk']           = c1b.checkbox("AOD / AVK")
            details['deficit_neuro']     = c1b.checkbox("Déficit neuro")
        elif motif == "Douleur abdominale":
            c1a, c1b = st.columns(2)
            details['defense']    = c1a.checkbox("Défense abdominale")
            details['contracture'] = c1a.checkbox("Contracture")
            details['regressive'] = c1b.checkbox("Douleur régressive")
            details['mauvaise_tolerance'] = c1b.checkbox("Mauvaise tolérance")
        elif motif == "Fièvre":
            c1a, c1b = st.columns(2)
            details['confusion']          = c1a.checkbox("Confusion")
            details['purpura']            = c1a.checkbox("Purpura")
            details['mauvaise_tolerance'] = c1b.checkbox("Mauvaise tolérance")
        elif motif == "Allergie / anaphylaxie":
            details['dyspnee']            = st.checkbox("Dyspnée / œdème laryngé")
            details['mauvaise_tolerance'] = st.checkbox("Mauvaise tolérance (chute TA)")
        elif motif in ["Intoxication médicamenteuse", "Intoxication non médicamenteuse"]:
            details['mauvaise_tolerance']  = st.checkbox("Mauvaise tolérance")
            details['intention_suicidaire'] = st.checkbox("Intention suicidaire")
            details['cardiotropes']        = st.checkbox("Toxiques cardiotropes")
        elif motif == "Brûlure":
            details['etendue']     = st.checkbox("Étendue > 10% SCT")
            details['main_visage'] = st.checkbox("Main / visage / périnée")
        elif motif in ["Hématémèse / vomissement de sang", "Rectorragie / méléna"]:
            details['abondante'] = st.checkbox("Saignement abondant")
        elif motif == "Plaie":
            details['saignement_actif'] = st.checkbox("Saignement actif")
            details['delabrant']        = st.checkbox("Plaie délabrante")
            details['main']             = st.checkbox("Localisation main")
            details['superficielle']    = st.checkbox("Superficielle")
        elif motif == "Méno-métrorragie":
            details['grossesse'] = st.checkbox("Grossesse connue / suspectée")
            details['abondante'] = st.checkbox("Saignement abondant")
        elif motif in ["Douleur lombaire / colique néphrétique", "Hématurie", "Douleur testiculaire / torsion"]:
            details['intense']           = st.checkbox("Douleur intense")
            details['regressive']        = st.checkbox("Douleur régressive")
            details['suspicion_torsion'] = st.checkbox("Suspicion torsion") if "testiculaire" in motif else False
            details['abondante_active']  = st.checkbox("Saignement actif") if "Hématurie" in motif else False
        elif motif == "Hyperglycémie":
            details['glycemie']        = st.number_input("Glycémie mmol/L", 0.0, 60.0, 8.0, 0.5)
            details['cetose_elevee']   = st.checkbox("Cétose élevée")
            details['cetose_positive'] = st.checkbox("Cétose positive")
        elif motif == "Hypoglycémie":
            details['mauvaise_tolerance'] = st.checkbox("Mauvaise tolérance")
        elif motif == "Troubles du comportement / psychiatrie":
            details['agitation']      = st.checkbox("Agitation / violence")
            details['hallucinations'] = st.checkbox("Hallucinations")
        elif motif in ["Tachycardie / tachyarythmie", "Bradycardie / bradyarythmie", "Palpitations"]:
            details['mauvaise_tolerance'] = st.checkbox("Mauvaise tolérance hémodynamique")
            details['malaise']            = st.checkbox("Malaise associé")
        elif motif == "Hypertension artérielle":
            details['sf_associes'] = st.checkbox("SF associés (céphalée, trouble visuel, douleur thoracique)")
        elif motif in ["Traumatisme abdomen / thorax / cervical", "Traumatisme bassin / hanche / fémur / rachis", "Traumatisme membre / épaule"]:
            details['cinetique']          = st.selectbox("Cinétique", ["Faible", "Haute"])
            details['mauvaise_tolerance'] = st.checkbox("Mauvaise tolérance")
            details['penetrant']          = st.checkbox("Pénétrant") if "abdomen" in motif else False
            if "membre" in motif.lower() or "épaule" in motif.lower():
                details['impotence_totale']   = st.checkbox("Impotence totale")
                details['deformation']         = st.checkbox("Déformation")
                details['impotence_moderee']   = st.checkbox("Impotence modérée")
                details['ischemie']            = st.checkbox("Ischémie distale")
        elif motif == "Épistaxis":
            details['abondant_actif']     = st.checkbox("Abondant actif")
            details['abondant_resolutif'] = st.checkbox("Abondant résolutif")
        elif motif in ["Corps étranger / brûlure oculaire", "Trouble visuel / cécité"]:
            details['chimique'] = st.checkbox("Brûlure chimique")
            details['intense']  = st.checkbox("Douleur intense")
            details['brutal']   = st.checkbox("Début brutal")
        elif motif == "Convulsions":
            details['crises_multiples']        = st.checkbox("Crises multiples / en cours")
            details['confusion_post_critique'] = st.checkbox("Confusion post-critique")
        elif motif == "Céphalée":
            details['inhabituelle'] = st.checkbox("Inhabituelle / 1er épisode")
            details['brutale']      = st.checkbox("Début brutal")
            details['fievre_assoc'] = st.checkbox("Fièvre associée")
        elif motif == "Électrisation":
            details['pdc']           = st.checkbox("PDC")
            details['foudre']        = st.checkbox("Foudroiement")
            details['haute_tension'] = st.checkbox("Haute tension")

    # ── TAB 3 : TRIAGE & SBAR ────────────────────────────────────────────────
    with t_decision:
        if temp is None: temp = 37.0; fc = 80; pas = 120; spo2 = 98; fr = 16; gcs = 15
        bpco_flag = "BPCO" in atcd
        news2, news2_warnings = compute_news2(fr, spo2, supp_o2, temp, pas, fc, gcs, bpco_flag)
        news2_label, news2_class = news2_level(news2)

        # Vérification des variables d'anamnèse (si tab 2 non visité)
        if 'motif' not in dir() or motif is None: motif = "Fièvre"
        if 'details' not in dir() or details is None: details = {}
        if 'eva_score' not in dir(): eva_score = 0; eva_echelle = "EVA"
        if 'cat' not in dir(): cat = "INFECTIOLOGIE"
        if 'p_pqrst' not in dir(): p_pqrst = ""; q_pqrst = "Non précisé"; r_pqrst = ""; t_onset = ""

        for w in news2_warnings:
            st.markdown(f'<div class="alert-warning">{w}</div>', unsafe_allow_html=True)

        niveau, justif, critere_ref = french_triage(motif, details, fc, pas, spo2, fr, gcs, temp, age, news2)
        tri_label = TRI_LABELS[niveau]
        sector    = TRI_SECTORS[niveau]
        emoji     = TRI_EMOJI[niveau]

        # Bannières d'alerte AVANT le résultat
        render_danger_banners(news2, None, niveau, fc, pas, spo2, fr, gcs, temp)

        # Alerte réévaluation en retard
        if st.session_state.last_reeval:
            since_min = (datetime.now() - st.session_state.last_reeval).total_seconds() / 60
            if since_min > TRI_DELAIS.get(niveau, 60):
                st.markdown(
                    f'<div class="alert-danger">⏱ RÉÉVALUATION EN RETARD : {int(since_min)} min écoulées — max {TRI_DELAIS[niveau]} min pour Tri {niveau}</div>',
                    unsafe_allow_html=True
                )

        st.markdown(
            f'<div class="triage-box {TRI_BOX_CSS[niveau]}">'
            f'<div style="font-size:1.8rem;font-weight:600">{emoji} {tri_label}</div>'
            f'<div style="font-size:0.85rem;margin-top:8px;opacity:.85">NEWS2 {news2} | Douleur {details.get("eva", 0)}/10</div>'
            f'<div style="font-size:0.82rem;margin-top:8px;font-style:italic">{justif}</div>'
            f'</div>', unsafe_allow_html=True
        )
        st.info(f"**Orientation :** {sector}")
        st.caption(f"Réf. FRENCH Triage — AKIR-IAO : {critere_ref}")

        st.markdown('<div class="section-header">Alertes sécurité clinique</div>', unsafe_allow_html=True)
        alertes_d, alertes_w, _ = check_coherence(fc, pas, spo2, fr, gcs, temp, details.get("eva", 0), motif, atcd, details, news2)
        for a in alertes_d: st.markdown(f'<div class="alert-danger">⚠ {a}</div>', unsafe_allow_html=True)
        for a in alertes_w: st.markdown(f'<div class="alert-warning">△ {a}</div>', unsafe_allow_html=True)
        if not alertes_d and not alertes_w:
            st.markdown('<div class="alert-info">✓ Aucune incohérence détectée.</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">Bilans recommandés</div>', unsafe_allow_html=True)
        bilans = suggest_bilan(motif, details, fc, pas, spo2, fr, gcs, temp, age, atcd, news2, niveau)
        if bilans:
            cols_b = st.columns(min(len(bilans), 3))
            for i, (bname, bitems) in enumerate(bilans.items()):
                col = cols_b[i % len(cols_b)]
                items_html = "".join([f'<div class="bilan-item">{it}</div>' for it in bitems])
                col.markdown(
                    f'<div style="background:#0f172a;border:1px solid #1e3a5f;border-radius:10px;padding:14px 18px;margin:8px 0;">'
                    f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#38bdf8;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;">{bname}</div>'
                    f'{items_html}</div>',
                    unsafe_allow_html=True
                )

        st.markdown('<div class="section-header">Transmission SBAR — DPI-Ready</div>', unsafe_allow_html=True)
        code_anon = f"PT-{datetime.now().strftime('%H%M%S')}"

        if st.button("📋 Générer SBAR DPI-Ready", type="primary", use_container_width=True):
            sbar = generate_sbar(
                age, motif, cat, atcd, allergies, supp_o2, temp, fc, pas, spo2, fr, gcs,
                news2, news2_label, details.get("eva", 0), eva_echelle if 'eva_echelle' in dir() else "EVA",
                p_pqrst, q_pqrst, r_pqrst, t_onset,
                details, niveau, tri_label, justif, critere_ref, sector,
                gcs_y=st.session_state.gcs_y_score,
                gcs_v=st.session_state.gcs_v_score,
                gcs_m=st.session_state.gcs_m_score,
                code_anon=code_anon
            )
            st.session_state.sbar_text = sbar

            # Sauvegarder dans l'historique de session
            snap_hist = {
                "heure": datetime.now().strftime("%H:%M"), "age": age, "motif": motif,
                "cat": cat, "eva": details.get("eva", 0), "news2": news2, "niveau": niveau,
                "temp": temp, "fc": fc, "pas": pas, "spo2": spo2, "fr": fr, "gcs": gcs,
                "atcd": atcd, "allergies": allergies, "sbar": sbar,
                "alertes_danger": len(alertes_d),
            }
            st.session_state.patient_history.insert(0, snap_hist)
            st.success("SBAR généré et enregistré dans l'historique.")

        if st.session_state.sbar_text:
            st.markdown(f'<div class="sbar-block">{st.session_state.sbar_text}</div>', unsafe_allow_html=True)
            c_dl1, c_dl2 = st.columns(2)
            c_dl1.download_button(
                "📋 Télécharger SBAR (.txt)",
                data=st.session_state.sbar_text,
                file_name=f"SBAR_AKIR_{datetime.now().strftime('%Y%m%d_%H%M')}_Tri{niveau}.txt",
                mime="text/plain",
                use_container_width=True,
            )
            if c_dl2.button("💾 Sauvegarder au registre (anonyme)", use_container_width=True):
                data_to_save = {
                    "age": age, "motif": motif, "cat": cat, "niveau": niveau,
                    "news2": news2, "eva": details.get("eva", 0),
                    "temp": temp, "fc": fc, "pas": pas, "spo2": spo2, "fr": fr, "gcs": gcs,
                    "allergies": allergies, "sbar": st.session_state.sbar_text,
                }
                uid = add_patient_to_db(data_to_save)
                st.success(f"✓ Enregistré dans le registre anonyme (ID : {uid})")

        render_disclaimer()

    # ── TAB 4 : SCORES COMPLÉMENTAIRES ───────────────────────────────────────
    with t_scores:
        if temp is None: temp = 37.0; fc = 80; pas = 120; spo2 = 98; fr = 16; gcs = 15
        bpco_flag = "BPCO" in atcd
        news2, _ = compute_news2(fr, spo2, supp_o2, temp, pas, fc, gcs, bpco_flag)

        s1, s2 = st.columns(2)

        # ── GCS DÉTAILLÉ ──
        with s1:
            st.markdown('<div class="score-title">Glasgow Coma Scale (GCS)</div>', unsafe_allow_html=True)
            with st.expander("ℹ Critères GCS"):
                st.markdown("**Yeux (Y):** 4=spontané | 3=à la voix | 2=à la douleur | 1=absent")
                st.markdown("**Verbal (V):** 5=orienté | 4=confus | 3=mots | 2=sons | 1=absent")
                st.markdown("**Moteur (M):** 6=obéit | 5=localise | 4=évitement | 3=flexion | 2=extension | 1=absent")
            gy = st.select_slider("Yeux (Y)", options=[1, 2, 3, 4], value=4, key="gcs_y")
            gv = st.select_slider("Verbal (V)", options=[1, 2, 3, 4, 5], value=5, key="gcs_v")
            gm = st.select_slider("Moteur (M)", options=[1, 2, 3, 4, 5, 6], value=6, key="gcs_m")
            st.session_state.gcs_y_score = gy
            st.session_state.gcs_v_score = gv
            st.session_state.gcs_m_score = gm
            gcs_calc, gcs_errs = compute_score_gcs(gy, gv, gm)
            for e in gcs_errs: st.warning(e)
            if gcs_calc <= 8: gcss, gcsi = "score-high", "Coma — protection VA urgente"
            elif gcs_calc <= 13: gcss, gcsi = "score-med", "Altération modérée"
            elif gcs_calc == 14: gcss, gcsi = "score-med", "Altération légère"
            else: gcss, gcsi = "score-low", "Éveillé et orienté"
            st.markdown(score_badge_custom(f"GCS {gcs_calc}/15", gcss), unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">→ {gcsi}</div>', unsafe_allow_html=True)

        # ── TIMI ──
        with s2:
            st.markdown('<div class="score-title">Score TIMI — SCA-ST-</div>', unsafe_allow_html=True)
            with st.expander("ℹ Critères TIMI"):
                render_infobulles_timi()
            t_age_65  = st.checkbox("Âge ≥ 65 ans", key="timi_age")
            t_frcv    = st.number_input("Nombre FRCV", 0, 5, 0, key="timi_frcv")
            t_ang_sev = st.checkbox("Sténose coronaire connue ≥ 50%", key="timi_ang")
            t_aspi    = st.checkbox("Aspirine dans les 7 derniers jours", key="timi_aspi")
            t_bio     = st.checkbox("Biomarqueurs élevés (Troponine+)", key="timi_bio")
            t_st      = st.checkbox("Déviation ST ≥ 0.5 mm", key="timi_st")
            t_crises  = st.number_input("Crises angineuses en 24h", 0, 10, 0, key="timi_crises")
            timi_score, timi_errs = compute_score_timi(age, t_frcv, t_ang_sev, t_aspi, t_bio, t_st, t_crises)
            for e in timi_errs: st.warning(e)
            if timi_score <= 2: tcss, tint = "score-low", "Risque faible (<10%)"
            elif timi_score <= 4: tcss, tint = "score-med", "Risque intermédiaire (10-20%)"
            else: tcss, tint = "score-high", "Risque élevé (>20%) — Cardiologie URGENTE"
            st.markdown(score_badge_custom(f"TIMI {timi_score}/7", tcss), unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">→ {tint}</div>', unsafe_allow_html=True)

        s3, s4 = st.columns(2)

        # ── SILVERMAN ──
        with s3:
            st.markdown('<div class="score-title">Score de Silverman — Détresse Néonatale</div>', unsafe_allow_html=True)
            with st.expander("ℹ Critères Silverman"):
                st.markdown("0 = absent | 1 = modéré | 2 = intense. Score max = 10.")
                st.markdown("< 3 = normal | 3-4 = détresse légère | ≥ 5 = détresse sévère → Pédiatre URGENT")
            opts_sil = [0, 1, 2]
            sil_bt  = st.select_slider("Balancement thoraco-abdominal", options=opts_sil, key="sil_bt")
            sil_ti  = st.select_slider("Tirage intercostal", options=opts_sil, key="sil_ti")
            sil_rss = st.select_slider("Rétraction sus-sternale", options=opts_sil, key="sil_rss")
            sil_an  = st.select_slider("Battement aile du nez", options=opts_sil, key="sil_an")
            sil_gei = st.select_slider("Geignement expiratoire", options=opts_sil, key="sil_gei")
            sil_score, sil_errs = compute_score_silverman(sil_bt, sil_ti, sil_rss, sil_an, sil_gei)
            for e in sil_errs: st.warning(e)
            if sil_score <= 2: scss, sint = "score-low", "Normal — pas de détresse"
            elif sil_score <= 4: scss, sint = "score-med", "Détresse légère — surveillance rapprochée"
            else: scss, sint = "score-high", "DÉTRESSE SÉVÈRE — Pédiatre immédiat"
            render_danger_banners(news2, sil_score, None, fc, pas, spo2, fr, gcs, temp)
            st.markdown(score_badge_custom(f"Silverman {sil_score}/10", scss), unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">→ {sint}</div>', unsafe_allow_html=True)

        # ── MALINAS + BRÛLURE ──
        with s4:
            st.markdown('<div class="score-title">Score de Malinas — Transport Obstétrical</div>', unsafe_allow_html=True)
            with st.expander("ℹ Critères Malinas"):
                st.markdown("0-2 pts / item. Score ≥ 8 = NE PAS TRANSPORTER (accouchement imminent).")
            mal_par = st.select_slider("Parité (0=nullipare,1=multi,2=multi≥3)", options=[0, 1, 2], key="mal_par")
            mal_dur = st.select_slider("Durée travail (0=<3h, 1=3-5h, 2=>5h)", options=[0, 1, 2], key="mal_dur")
            mal_con = st.select_slider("Durée contractions (0=<1min, 1=1min, 2=>1min)", options=[0, 1, 2], key="mal_con")
            mal_int = st.select_slider("Intervalle contrac. (0=>5min, 1=3-5min, 2=<3min)", options=[0, 1, 2], key="mal_int")
            mal_poc = st.select_slider("Poche des eaux (0=intacte, 1=rompue<1h, 2=rompue>1h)", options=[0, 1, 2], key="mal_poc")
            mal_score, mal_errs = compute_score_malinas(mal_par, mal_dur, mal_con, mal_int, mal_poc)
            for e in mal_errs: st.warning(e)
            if mal_score <= 5: mcss, mint = "score-low", "Transport possible"
            elif mal_score <= 7: mcss, mint = "score-med", "Transport sous surveillance médicale"
            else: mcss, mint = "score-high", "NE PAS TRANSPORTER — Accouchement imminent"
            st.markdown(score_badge_custom(f"Malinas {mal_score}/10", mcss), unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">→ {mint}</div>', unsafe_allow_html=True)

        # ── BRÛLURE ──
        st.markdown('<div class="score-title">Brûlures — Règle des 9 + Formule de Baux</div>', unsafe_allow_html=True)
        with st.expander("ℹ Règle des 9 de Wallace + Baux"):
            st.markdown("**Règle des 9 :** Tête=9%, Tronc ant=18%, Tronc post=18%, Bras=9%×2, Jambe=18%×2, Périnée=1%")
            st.markdown("**Baux :** Âge + SCB(%) → pronostic mortalité. > 100 = sévère. > 120 = quasi-létal.")
        sb1, sb2 = st.columns(2)
        scb_pct = sb1.number_input("SCB estimée (%)", 0, 100, 10, key="scb_pct")
        profondeur = sb2.selectbox("Profondeur", ["1er degré", "2ème degré superficiel", "2ème degré profond", "3ème degré"])
        scb, baux, pronostic, burn_errs = compute_score_brulure(scb_pct, age, profondeur)
        for e in burn_errs: st.warning(e)
        if baux < 80: bcss = "score-low"
        elif baux < 100: bcss = "score-med"
        else: bcss = "score-high"
        st.markdown(score_badge_custom(f"SCB {scb}% — Baux {baux}", bcss), unsafe_allow_html=True)
        st.markdown(f'<div class="score-interp">→ {profondeur} | {pronostic}</div>', unsafe_allow_html=True)

        # Récapitulatif scores
        st.markdown('<div class="section-header">Récapitulatif</div>', unsafe_allow_html=True)
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("TIMI", f"{timi_score}/7")
        r2.metric("Silverman", f"{sil_score}/10")
        r3.metric("GCS calculé", f"{gcs_calc}/15")
        r4.metric("Malinas", f"{mal_score}/10")

    # ── TAB 5 : CALCULATEUR PERFUSION ────────────────────────────────────────
    with t_perfusion:
        st.markdown("### 💊 Calculateur de Perfusion & Doses de Charge")
        st.caption("Module d'aide au calcul. Les doses doivent être validées par le médecin responsable.")

        # Poids patient (nécessaire pour doses kg-dépendantes)
        poids_kg = st.number_input("Poids du patient (kg)", 1.0, 200.0, 70.0, 0.5, key="perf_poids")

        st.markdown('<div class="section-header">Débit de Perfusion — Formule V/T</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="infobulles-score">'
            'ℹ <b>Formule :</b> Débit (ml/h) = Volume (ml) ÷ Durée (h)<br>'
            'Exemple : 500 mL en 4h = 125 ml/h'
            '</div>',
            unsafe_allow_html=True
        )
        p1, p2 = st.columns(2)
        vol_ml   = p1.number_input("Volume à perfuser (ml)", 1, 5000, 500, 50, key="perf_vol")
        duree_h  = p2.number_input("Durée de perfusion (h)", 0.25, 24.0, 4.0, 0.25, key="perf_dur")

        debit, debit_err = calcul_debit_perfusion(vol_ml, duree_h)
        if debit_err:
            st.markdown(f'<div class="alert-warning">{debit_err}</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="perfusion-card">'
                f'<div class="perfusion-result">{debit} ml/h</div>'
                f'<div class="perfusion-label">Débit calculé pour {vol_ml} ml en {duree_h}h</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            # Calcul des gouttes/min si nécessaire
            gttes_min = round(debit / 3, 1)  # Facteur 20 gouttes/mL standard
            st.caption(f"≈ {gttes_min} gouttes/min (facteur goutte standard 20 gtt/mL)")

        st.markdown('<div class="section-header">Doses de Charge Courantes</div>', unsafe_allow_html=True)

        d1, d2, d3 = st.columns(3)

        # Paracétamol
        with d1:
            parac, parac_err = calcul_dose_paracetamol(poids_kg)
            if parac_err:
                st.markdown(f'<div class="alert-warning">{parac_err}</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div class="dose-card">'
                    f'<div class="dose-title">💊 Paracétamol IV</div>'
                    f'<b>{parac["dose_g"]} g</b> ({parac["dose_mg"]} mg)<br>'
                    f'{parac["debit_15min"]}<br>'
                    f'<small style="color:#64748b;">Max 4g/24h adulte</small>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        # Néfopam
        with d2:
            nef, nef_err = calcul_dose_nefopam(poids_kg)
            if nef_err:
                st.markdown(f'<div class="alert-warning">{nef_err}</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div class="dose-card">'
                    f'<div class="dose-title">💊 Néfopam (Acupan) IV</div>'
                    f'<b>{nef["dose_mg"]} mg</b><br>'
                    f'<small style="color:#64748b;">{nef["note"]}</small>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        # Midazolam
        with d3:
            mida, mida_err = calcul_dose_midazolam(poids_kg)
            if mida_err:
                st.markdown(f'<div class="alert-warning">{mida_err}</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div class="dose-card">'
                    f'<div class="dose-title">💊 Midazolam IV (sédation)</div>'
                    f'<b>{mida["dose_min_mg"]}–{mida["dose_max_mg"]} mg</b><br>'
                    f'<small style="color:#64748b;">{mida["note"]}</small>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        # Adrénaline anaphylaxie
        st.markdown('<div class="section-header">Adrénaline — Anaphylaxie</div>', unsafe_allow_html=True)
        dose_adre = 0.5 if poids_kg >= 30 else round(0.01 * poids_kg, 2)
        st.markdown(
            f'<div class="dose-card">'
            f'<div class="dose-title">⚡ Adrénaline IM — Anaphylaxie</div>'
            f'<b>{dose_adre} mg IM</b> (face antérolatérale cuisse)<br>'
            f'Adulte ≥ 30 kg : 0.5 mg | Enfant : 0.01 mg/kg<br>'
            f'<small style="color:#64748b;">Répéter à 5 min si pas d\'amélioration. Ampoule 1 mg/mL.</small>'
            f'</div>',
            unsafe_allow_html=True
        )

        render_disclaimer()


# =============================================================================
# RÉÉVALUATION STRUCTURÉE (commune aux deux modes)
# =============================================================================
with t_reeval:
    st.markdown("### 🔄 Réévaluations Structurées")
    st.caption("Chaque réévaluation est comparée à la précédente. Tendance automatique.")

    st.markdown('<div class="section-header">Nouvelle réévaluation</div>', unsafe_allow_html=True)
    cr1, cr2, cr3 = st.columns(3)
    re_temp = cr1.number_input("T° (°C)", 30.0, 45.0, 37.0, 0.1, key="re_temp")
    re_fc   = cr1.number_input("FC (bpm)", 20, 220, 80, key="re_fc")
    re_pas  = cr2.number_input("PAS (mmHg)", 40, 260, 120, key="re_pas")
    re_spo2 = cr2.number_input("SpO2 (%)", 50, 100, 98, key="re_spo2")
    re_fr   = cr3.number_input("FR (/min)", 5, 60, 16, key="re_fr")
    re_gcs  = cr3.number_input("GCS", 3, 15, 15, key="re_gcs")

    re_news2, re_warnings = compute_news2(re_fr, re_spo2, supp_o2, re_temp, re_pas, re_fc, re_gcs, "BPCO" in atcd)
    re_label, re_css = news2_level(re_news2)

    for w in re_warnings:
        st.markdown(f'<div class="alert-warning">{w}</div>', unsafe_allow_html=True)

    re_motif = "Fièvre"
    if st.session_state.patient_history:
        re_motif = st.session_state.patient_history[-1].get("motif", "Fièvre")
    re_niveau, re_justif, re_ref = french_triage(re_motif, {}, re_fc, re_pas, re_spo2, re_fr, re_gcs, re_temp, age, re_news2)

    col_re1, col_re2 = st.columns(2)
    col_re1.markdown(f'<div class="news2-badge {re_css}">{re_label}</div>', unsafe_allow_html=True)
    col_re2.info(f"Triage recalculé : **{TRI_EMOJI[re_niveau]} {TRI_LABELS[re_niveau]}**")

    render_danger_banners(re_news2, None, re_niveau, re_fc, re_pas, re_spo2, re_fr, re_gcs, re_temp)

    if st.button("Enregistrer cette réévaluation", use_container_width=True):
        snap = {
            "heure": datetime.now().strftime("%H:%M"),
            "fc": re_fc, "pas": re_pas, "spo2": re_spo2,
            "fr": re_fr, "gcs": re_gcs, "temp": re_temp,
            "niveau": re_niveau, "news2": re_news2,
        }
        st.session_state.reeval_history.append(snap)
        st.session_state.last_reeval = datetime.now()
        st.success(f"Réévaluation enregistrée à {snap['heure']} — Tri {re_niveau}")

    st.markdown('<div class="section-header">Historique des réévaluations</div>', unsafe_allow_html=True)

    if len(st.session_state.reeval_history) < 1:
        st.info("Aucune réévaluation enregistrée. Enregistrez d'abord un patient.")
    else:
        history = st.session_state.reeval_history

        def trend(old, new, higher_is_worse=True):
            if new > old:
                sym = "↑" if higher_is_worse else "↓"
                css = "trend-down" if higher_is_worse else "trend-up"
            elif new < old:
                sym = "↓" if higher_is_worse else "↑"
                css = "trend-up" if higher_is_worse else "trend-down"
            else:
                sym, css = "=", "trend-same"
            return f'<span class="{css}">{sym}</span>'

        for i, snap in enumerate(history):
            prev = history[i - 1] if i > 0 else snap
            niveau_order = {"M": 0, "1": 1, "2": 2, "3A": 3, "3B": 4, "4": 5, "5": 6}
            no = niveau_order.get(snap['niveau'], 3)
            np_ = niveau_order.get(prev['niveau'], 3)
            if no > np_:   row_css, tendance = "reeval-better", "AMÉLIORATION"
            elif no < np_: row_css, tendance = "reeval-worse", "AGGRAVATION"
            else:          row_css, tendance = "reeval-same", "STABLE"

            label = "H0" if i == 0 else f"H+{i}"
            st.markdown(
                f'<div class="reeval-row {row_css}">'
                f'<b>{snap["heure"]}</b> ({label}) | '
                f'Tri {TRI_EMOJI.get(snap["niveau"], "")}{snap["niveau"]} | '
                f'NEWS2 {snap.get("news2", "?")} | '
                f'FC {snap["fc"]} {trend(prev["fc"], snap["fc"])} | '
                f'PAS {snap["pas"]} {trend(prev["pas"], snap["pas"], False)} | '
                f'SpO2 {snap["spo2"]} {trend(prev["spo2"], snap["spo2"], False)} | '
                f'GCS {snap["gcs"]} {trend(prev["gcs"], snap["gcs"], False)} | '
                f'<b>{tendance}</b>'
                f'</div>',
                unsafe_allow_html=True
            )

        if len(history) >= 2:
            first = history[0]; last = history[-1]
            st.markdown(
                f"**Bilan global :** {len(history)} réévaluations | "
                f"NEWS2 initial {first.get('news2', '?')} → {last.get('news2', '?')} | "
                f"Tri {first['niveau']} → {last['niveau']}"
            )

        if st.button("Effacer réévaluations"):
            st.session_state.reeval_history = []
            st.rerun()


# =============================================================================
# HISTORIQUE SESSION
# =============================================================================
with t_history:
    if not st.session_state.patient_history:
        st.info("Aucun patient enregistré dans cette session.")
    else:
        st.markdown(f"**{len(st.session_state.patient_history)} patient(s) cette session**")
        for i, pat in enumerate(reversed(st.session_state.patient_history), 1):
            css = TRI_HIST_CSS.get(pat['niveau'], 'hist-4')
            em  = TRI_EMOJI.get(pat['niveau'], '')
            tag = " ⚠ ALERTES" if pat.get('alertes_danger', 0) > 0 else ""
            st.markdown(
                f'<div class="hist-row {css}">'
                f'<b>{pat["heure"]}</b> | {pat["age"]} ans | <b>{pat["motif"]}</b> | '
                f'EVA {pat["eva"]}/10 | NEWS2 {pat["news2"]} | {em} Tri {pat["niveau"]}{tag}'
                f'</div>', unsafe_allow_html=True
            )
            with st.expander(f"SBAR — Patient #{len(st.session_state.patient_history) - i + 1}"):
                st.markdown(f'<div class="sbar-block">{pat["sbar"]}</div>', unsafe_allow_html=True)
                st.download_button(
                    "📋 Télécharger SBAR",
                    data=pat["sbar"],
                    file_name=f"SBAR_{pat['heure'].replace(':', 'h')}_Tri{pat['niveau']}.txt",
                    mime="text/plain",
                    key=f"dl_{i}"
                )
        if st.button("Effacer l'historique de session"):
            st.session_state.patient_history = []
            st.rerun()


# =============================================================================
# REGISTRE PATIENTS — STOCKAGE ANONYME PERSISTENT
# =============================================================================
with t_registre:
    st.markdown("### 🗃️ Registre Patients — Données anonymes persistantes")
    st.markdown(
        '<div class="alert-info">🔒 <b>RGPD :</b> Ce registre ne contient aucun nom ni prénom. '
        'Chaque patient est identifié par un code anonyme unique généré automatiquement. '
        'Les données sont stockées localement sur ce poste uniquement.</div>',
        unsafe_allow_html=True
    )

    db = load_patient_db()

    if db:
        niveaux_count = {}
        for p in db:
            n = p.get("niveau", "?")
            niveaux_count[n] = niveaux_count.get(n, 0) + 1
        today_count = sum(1 for p in db if p.get("saved_date") == datetime.now().strftime("%Y-%m-%d"))

        cols_stat = st.columns(5)
        cols_stat[0].markdown(f'<div class="reg-stat-card"><div class="reg-stat-num">{len(db)}</div><div class="reg-stat-label">Total</div></div>', unsafe_allow_html=True)
        cols_stat[1].markdown(f'<div class="reg-stat-card"><div class="reg-stat-num">{today_count}</div><div class="reg-stat-label">Aujourd\'hui</div></div>', unsafe_allow_html=True)
        urgent_count = sum(v for k, v in niveaux_count.items() if k in ["M", "1", "2"])
        cols_stat[2].markdown(f'<div class="reg-stat-card"><div class="reg-stat-num" style="color:#f87171">{urgent_count}</div><div class="reg-stat-label">Tri M/1/2</div></div>', unsafe_allow_html=True)
        moderate_count = sum(v for k, v in niveaux_count.items() if k in ["3A", "3B"])
        cols_stat[3].markdown(f'<div class="reg-stat-card"><div class="reg-stat-num" style="color:#fbbf24">{moderate_count}</div><div class="reg-stat-label">Tri 3A/3B</div></div>', unsafe_allow_html=True)
        low_count = sum(v for k, v in niveaux_count.items() if k in ["4", "5"])
        cols_stat[4].markdown(f'<div class="reg-stat-card"><div class="reg-stat-num" style="color:#4ade80">{low_count}</div><div class="reg-stat-label">Tri 4/5</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">Recherche & Filtres</div>', unsafe_allow_html=True)
    col_search, col_filter, col_actions = st.columns([3, 2, 2])
    search_query = col_search.text_input("🔍 Rechercher (motif, âge, niveau...)", placeholder="ex: SCA, 45 ans, Tri 2...", key="reg_search", label_visibility="collapsed")
    filter_niveau = col_filter.selectbox("Filtrer par niveau", ["Tous", "M", "1", "2", "3A", "3B", "4", "5"], key="reg_filter")

    filtered_db = search_patients(search_query) if search_query else db
    if filter_niveau != "Tous":
        filtered_db = [p for p in filtered_db if p.get("niveau") == filter_niveau]

    if col_actions.button("📥 Exporter tout (JSON)", use_container_width=True) and db:
        export_data = json.dumps(db, ensure_ascii=False, indent=2)
        st.download_button(
            "Télécharger registre anonyme",
            data=export_data,
            file_name=f"AKIR_registre_anon_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            key="export_json"
        )

    st.markdown(f'<div class="section-header">Patients ({len(filtered_db)} résultat{"s" if len(filtered_db) != 1 else ""})</div>', unsafe_allow_html=True)

    if not filtered_db:
        st.markdown(
            '<div class="reg-empty">'
            '<div class="reg-empty-icon">🗃️</div>'
            '<div>Aucun patient dans le registre.<br>Utilisez le bouton "Sauvegarder au registre" après un triage.</div>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        for idx, pat in enumerate(filtered_db):
            uid = pat.get("uid", "?")
            niv = pat.get("niveau", "?")
            em  = TRI_EMOJI.get(niv, "")

            st.markdown(
                f'<div class="reg-card">'
                f'<div class="reg-card-header">'
                f'  <div class="reg-card-title">Code : {uid} — {pat.get("age", "?")} ans</div>'
                f'  <div class="reg-card-date">{pat.get("saved_at", "")}</div>'
                f'</div>'
                f'<div style="margin-bottom:8px;">'
                f'  <span class="reg-badge reg-badge-{niv}">{em} Tri {niv}</span>'
                f'  <span style="font-size:0.82rem;color:#94a3b8;">{pat.get("motif", "")} ({pat.get("cat", "")})</span>'
                f'</div>'
                f'<div class="reg-card-body">'
                f'  <div class="reg-field"><span class="reg-field-label">T°</span><span class="reg-field-value">{pat.get("temp", "")} °C</span></div>'
                f'  <div class="reg-field"><span class="reg-field-label">FC</span><span class="reg-field-value">{pat.get("fc", "")} bpm</span></div>'
                f'  <div class="reg-field"><span class="reg-field-label">PAS</span><span class="reg-field-value">{pat.get("pas", "")} mmHg</span></div>'
                f'  <div class="reg-field"><span class="reg-field-label">SpO2</span><span class="reg-field-value">{pat.get("spo2", "")} %</span></div>'
                f'  <div class="reg-field"><span class="reg-field-label">GCS</span><span class="reg-field-value">{pat.get("gcs", "")}/15</span></div>'
                f'  <div class="reg-field"><span class="reg-field-label">NEWS2</span><span class="reg-field-value">{pat.get("news2", "")}</span></div>'
                f'  <div class="reg-field"><span class="reg-field-label">EVA</span><span class="reg-field-value">{pat.get("eva", "")}/10</span></div>'
                f'  <div class="reg-field"><span class="reg-field-label">Allergies</span><span class="reg-field-value">{pat.get("allergies", "RAS")}</span></div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

            col_d1, col_d2, col_d3 = st.columns([3, 1, 1])
            with col_d1:
                with st.expander(f"📄 SBAR complet — {uid}"):
                    sbar_txt = pat.get("sbar", "Pas de SBAR généré.")
                    st.markdown(f'<div class="sbar-block">{sbar_txt}</div>', unsafe_allow_html=True)
                    st.download_button(
                        "📋 Télécharger SBAR",
                        data=sbar_txt,
                        file_name=f"SBAR_AKIR_{uid}_{niv}.txt",
                        mime="text/plain",
                        key=f"dl_reg_{uid}_{idx}"
                    )

            if col_d3.button(f"🗑️ Supprimer", key=f"del_{uid}_{idx}", use_container_width=True):
                st.session_state.confirm_delete = uid

            if st.session_state.confirm_delete == uid:
                st.warning(f"⚠️ Confirmer la suppression du patient **{uid}** ?")
                col_conf1, col_conf2, _ = st.columns([1, 1, 3])
                if col_conf1.button("✅ Oui, supprimer", key=f"conf_del_{uid}_{idx}", type="primary"):
                    delete_patient_from_db(uid)
                    st.session_state.confirm_delete = None
                    st.success(f"Patient {uid} supprimé du registre.")
                    st.rerun()
                if col_conf2.button("❌ Annuler", key=f"cancel_del_{uid}_{idx}"):
                    st.session_state.confirm_delete = None
                    st.rerun()

    if db:
        st.markdown("---")
        st.markdown('<div class="section-header">Administration</div>', unsafe_allow_html=True)
        with st.expander("⚠️ Zone dangereuse — Purge complète du registre"):
            st.warning("Cette action supprimera **tous** les patients du registre de manière irréversible.")
            if st.button("🗑️ PURGER TOUT LE REGISTRE", type="primary", key="purge_all"):
                save_patient_db([])
                st.session_state.confirm_delete = None
                st.success("Registre vidé.")
                st.rerun()

    render_disclaimer()