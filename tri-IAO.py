import streamlit as st
from datetime import datetime
import json
import os
import uuid

# --- CONFIGURATION ------------------------------------------------------------
st.set_page_config(
    page_title="IAO Expert Pro v12.0",
    page_icon="⚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# SYSTEME DE PERSISTANCE DES PATIENTS (fichier JSON)
# =============================================================================
PATIENT_DB_FILE = "patients_registry.json"

def load_patient_db():
    """Charge la base de donnees patients depuis le fichier JSON."""
    if os.path.exists(PATIENT_DB_FILE):
        try:
            with open(PATIENT_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_patient_db(patients):
    """Sauvegarde la base de donnees patients dans le fichier JSON."""
    try:
        with open(PATIENT_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(patients, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False

def add_patient_to_db(patient_data):
    """Ajoute un patient a la base de donnees persistante."""
    db = load_patient_db()
    patient_data["uid"] = str(uuid.uuid4())[:8]
    patient_data["saved_at"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    patient_data["saved_date"] = datetime.now().strftime("%Y-%m-%d")
    db.insert(0, patient_data)
    save_patient_db(db)
    return patient_data["uid"]

def delete_patient_from_db(uid):
    """Supprime un patient de la base par son UID."""
    db = load_patient_db()
    db = [p for p in db if p.get("uid") != uid]
    save_patient_db(db)

def search_patients(query):
    """Recherche dans la base de donnees par motif, age, niveau, date..."""
    db = load_patient_db()
    if not query:
        return db
    q = query.lower().strip()
    results = []
    for p in db:
        searchable = f"{p.get('motif','')} {p.get('age','')} {p.get('niveau','')} {p.get('cat','')} {p.get('saved_at','')} {p.get('nom','')} {p.get('prenom','')}".lower()
        if q in searchable:
            results.append(p)
    return results


# --- CSS ----------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
html,body,[class*="css"]{font-family:'IBM Plex Sans',sans-serif;}
.stApp{background:#0a0f1e;color:#e2e8f0;}
[data-testid='stSidebar']{background:#0f172a;border-right:1px solid #1e3a5f;}

.section-header{font-family:'IBM Plex Mono',monospace;color:#38bdf8;font-weight:600;font-size:0.75rem;
letter-spacing:0.12em;text-transform:uppercase;border-bottom:1px solid #1e3a5f;padding-bottom:6px;margin:16px 0 12px 0;}

/* Triage boxes */
.triage-box{border-radius:12px;padding:28px;text-align:center;font-family:'IBM Plex Mono',monospace;margin-bottom:16px;}
.box-M{background:linear-gradient(135deg,#1a0030,#3b0764);border:2px solid #a855f7;}
.box-1{background:linear-gradient(135deg,#450a0a,#7f1d1d);border:2px solid #ef4444;}
.box-2{background:linear-gradient(135deg,#431407,#7c2d12);border:2px solid #f97316;}
.box-3A{background:linear-gradient(135deg,#3b1a00,#78350f);border:2px solid #f59e0b;}
.box-3B{background:linear-gradient(135deg,#422006,#713f12);border:2px solid #eab308;}
.box-4{background:linear-gradient(135deg,#052e16,#14532d);border:2px solid #22c55e;}
.box-5{background:linear-gradient(135deg,#0c1a2e,#1e3a5f);border:2px solid #3b82f6;}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.55}}
.box-M,.box-1{animation:pulse 1s infinite;}

.news2-badge{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:1.6rem;font-weight:600;padding:6px 18px;border-radius:8px;margin-bottom:4px;}
.news2-low{background:#14532d;color:#86efac;}
.news2-med{background:#713f12;color:#fde68a;}
.news2-high{background:#7f1d1d;color:#fca5a5;}
.news2-crit{background:#4c0519;color:#f9a8d4;animation:pulse 1s infinite;}

.vital-alert{font-family:'IBM Plex Mono',monospace;font-size:0.65rem;padding:2px 6px;border-radius:4px;margin-left:6px;vertical-align:middle;}
.vital-warn{background:#422006;color:#fbbf24;}
.vital-crit{background:#450a0a;color:#f87171;}
.vital-ok{background:#052e16;color:#4ade80;}

.hist-row{background:#0f172a;border:1px solid #1e3a5f;border-radius:8px;padding:10px 14px;margin-bottom:6px;font-size:0.85rem;}
.hist-M{border-left:4px solid #a855f7;}.hist-1{border-left:4px solid #ef4444;}
.hist-2{border-left:4px solid #f97316;}.hist-3A{border-left:4px solid #f59e0b;}
.hist-3B{border-left:4px solid #eab308;}.hist-4{border-left:4px solid #22c55e;}
.hist-5{border-left:4px solid #3b82f6;}

.chrono{font-family:'IBM Plex Mono',monospace;font-size:2.2rem;font-weight:600;color:#38bdf8;text-align:center;letter-spacing:0.05em;}
.chrono-label{font-size:0.7rem;color:#64748b;text-align:center;letter-spacing:0.1em;text-transform:uppercase;}

.sbar-block{background:#020617;border:1px solid #1e3a5f;border-radius:10px;padding:18px;
font-family:'IBM Plex Mono',monospace;font-size:0.82rem;line-height:1.8;white-space:pre-wrap;color:#cbd5e1;}
.french-ref{background:#0f172a;border:1px solid #1e3a5f;border-left:4px solid #38bdf8;border-radius:6px;padding:10px 14px;font-size:0.8rem;color:#94a3b8;margin-top:10px;font-family:'IBM Plex Mono',monospace;}

.alert-danger{background:#450a0a;border:1px solid #ef4444;border-left:5px solid #ef4444;border-radius:8px;
padding:14px 16px;margin:8px 0;color:#fca5a5;font-weight:600;font-size:0.9rem;animation:pulse 1.2s infinite;}
.alert-warning{background:#422006;border:1px solid #f97316;border-left:5px solid #f97316;border-radius:8px;padding:12px 16px;margin:6px 0;color:#fdba74;font-size:0.88rem;}
.alert-info{background:#0c1a2e;border:1px solid #3b82f6;border-left:5px solid #3b82f6;border-radius:8px;padding:10px 14px;margin:6px 0;color:#93c5fd;font-size:0.85rem;}

.bilan-card{background:#0f172a;border:1px solid #1e3a5f;border-radius:10px;padding:14px 18px;margin:8px 0;}
.bilan-title{font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#38bdf8;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;}
.bilan-item{font-size:0.85rem;color:#cbd5e1;padding:3px 0;}
.bilan-item::before{content:"→ ";color:#38bdf8;}

.score-result{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:1.8rem;font-weight:600;padding:8px 22px;border-radius:8px;margin:8px 0 4px 0;}
.score-low{background:#052e16;color:#86efac;border:1px solid #16a34a;}
.score-med{background:#422006;color:#fde68a;border:1px solid #ca8a04;}
.score-high{background:#450a0a;color:#fca5a5;border:1px solid #dc2626;}
.score-info{background:#0c1a2e;color:#93c5fd;border:1px solid #2563eb;}
.score-interp{font-size:0.85rem;color:#94a3b8;margin-top:6px;line-height:1.6;font-style:italic;}
.score-title{font-family:'IBM Plex Mono',monospace;font-size:0.7rem;font-weight:600;letter-spacing:0.14em;text-transform:uppercase;color:#38bdf8;border-bottom:1px solid #1e3a5f;padding-bottom:6px;margin-bottom:14px;}
.score-row{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1e3a5f;padding:5px 0;font-size:0.85rem;}
.score-row:last-child{border-bottom:none;}
.score-row-label{color:#94a3b8;}
.score-row-val{font-family:'IBM Plex Mono',monospace;color:#e2e8f0;font-weight:600;}

/* ── v12 NOUVEAUTES ── */
.tri-rapide-box{background:#020617;border:2px solid #38bdf8;border-radius:14px;padding:24px;margin-bottom:16px;}
.tri-rapide-title{font-family:'IBM Plex Mono',monospace;color:#38bdf8;font-size:0.8rem;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:12px;}
.question-guidee{background:#0f172a;border:1px solid #1e3a5f;border-left:4px solid #38bdf8;border-radius:8px;padding:12px 16px;margin:6px 0;font-size:0.9rem;}
.question-label{font-size:0.72rem;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px;}

.douleur-badge{display:inline-flex;align-items:center;justify-content:center;
width:52px;height:52px;border-radius:50%;font-size:1.3rem;font-weight:700;
font-family:'IBM Plex Mono',monospace;cursor:pointer;border:2px solid transparent;transition:all 0.15s;}

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

.reeval-row{background:#0f172a;border:1px solid #1e3a5f;border-radius:8px;padding:10px 14px;margin-bottom:6px;font-size:0.83rem;}
.reeval-better{border-left:4px solid #22c55e;}
.reeval-same{border-left:4px solid #3b82f6;}
.reeval-worse{border-left:4px solid #ef4444;}
.trend-up{color:#4ade80;}
.trend-down{color:#f87171;}
.trend-same{color:#94a3b8;}

.legal-text{font-size:0.72rem;color:#475569;font-style:italic;margin-top:8px;}
.signature{color:#38bdf8;font-weight:600;font-size:0.85rem;border-top:1px solid #1e3a5f;padding-top:10px;margin-top:12px;}

/* ── REGISTRE PATIENTS ── */
.reg-card{background:#0f172a;border:1px solid #1e3a5f;border-radius:12px;padding:18px 20px;margin-bottom:10px;transition:all 0.2s;}
.reg-card:hover{border-color:#38bdf8;background:#0c1528;}
.reg-card-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;}
.reg-card-title{font-family:'IBM Plex Mono',monospace;font-size:1rem;font-weight:600;color:#e2e8f0;}
.reg-card-date{font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#64748b;}
.reg-card-body{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:6px 16px;font-size:0.82rem;}
.reg-field{display:flex;flex-direction:column;}
.reg-field-label{font-size:0.68rem;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;}
.reg-field-value{color:#cbd5e1;font-family:'IBM Plex Mono',monospace;}
.reg-badge{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:0.78rem;font-weight:600;padding:3px 10px;border-radius:6px;margin-right:6px;}
.reg-badge-M{background:#3b0764;color:#d8b4fe;}.reg-badge-1{background:#7f1d1d;color:#fca5a5;}
.reg-badge-2{background:#7c2d12;color:#fdba74;}.reg-badge-3A{background:#78350f;color:#fde68a;}
.reg-badge-3B{background:#713f12;color:#fde68a;}.reg-badge-4{background:#14532d;color:#86efac;}
.reg-badge-5{background:#1e3a5f;color:#93c5fd;}
.reg-stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px;margin-bottom:20px;}
.reg-stat-card{background:#020617;border:1px solid #1e3a5f;border-radius:10px;padding:16px;text-align:center;}
.reg-stat-num{font-family:'IBM Plex Mono',monospace;font-size:1.8rem;font-weight:600;color:#38bdf8;}
.reg-stat-label{font-size:0.72rem;color:#64748b;text-transform:uppercase;letter-spacing:0.1em;margin-top:4px;}
.reg-empty{text-align:center;padding:60px 20px;color:#475569;}
.reg-empty-icon{font-size:3rem;margin-bottom:12px;opacity:0.4;}

/* ── v12 : BANDEAU ALERTE IMMÉDIATE ── */
.danger-banner{background:linear-gradient(90deg,#7f1d1d,#991b1b);border:2px solid #ef4444;border-radius:12px;
padding:18px 22px;margin:12px 0;text-align:center;animation:pulse 0.8s infinite;}
.danger-banner-title{font-family:'IBM Plex Mono',monospace;font-size:1.1rem;font-weight:700;color:#fca5a5;letter-spacing:0.05em;}
.danger-banner-detail{font-size:0.88rem;color:#fecaca;margin-top:6px;}
.warning-banner{background:linear-gradient(90deg,#78350f,#92400e);border:2px solid #f59e0b;border-radius:12px;
padding:14px 20px;margin:10px 0;text-align:center;}
.warning-banner-title{font-family:'IBM Plex Mono',monospace;font-size:0.95rem;font-weight:600;color:#fde68a;}
.warning-banner-detail{font-size:0.82rem;color:#fef3c7;margin-top:4px;}

/* ── v12 : PRESCRIPTIONS ANTICIPÉES ── */
.rx-card{background:#0c1a30;border:1px solid #1e40af;border-left:5px solid #3b82f6;border-radius:10px;padding:16px 20px;margin:10px 0;}
.rx-title{font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#60a5fa;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:10px;}
.rx-item{font-size:0.85rem;color:#e2e8f0;padding:4px 0;display:flex;align-items:flex-start;gap:8px;}
.rx-item::before{content:"☐";color:#60a5fa;font-size:0.9rem;flex-shrink:0;}
.rx-item-urgent::before{content:"⚡";color:#f59e0b;}
.rx-cat{font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#94a3b8;letter-spacing:0.1em;text-transform:uppercase;
margin:10px 0 4px 0;padding-top:6px;border-top:1px solid #1e3a5f;}

/* ── v12 : SBAR AMÉLIORÉ ── */
.sbar-section{font-family:'IBM Plex Mono',monospace;font-weight:700;font-size:0.9rem;color:#38bdf8;margin-top:10px;}
.sbar-line{font-size:0.83rem;color:#cbd5e1;padding:2px 0 2px 12px;border-left:2px solid #1e3a5f;}
.sbar-header{background:#0f172a;border:2px solid #38bdf8;border-radius:10px;padding:16px;text-align:center;margin-bottom:12px;}
.sbar-header-title{font-family:'IBM Plex Mono',monospace;font-size:1rem;font-weight:600;color:#38bdf8;letter-spacing:0.08em;}
.sbar-header-sub{font-size:0.78rem;color:#64748b;margin-top:4px;}

/* ── v12 : DISCLAIMER JURIDIQUE ── */
.disclaimer{background:#020617;border:1px solid #334155;border-radius:8px;padding:14px 18px;margin-top:24px;
font-size:0.7rem;color:#64748b;line-height:1.7;font-style:italic;}
.disclaimer-title{font-family:'IBM Plex Mono',monospace;font-size:0.65rem;font-weight:600;color:#475569;
letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;}

/* ── v12 : MOBILE RESPONSIVE ── */
@media (max-width: 768px) {
    .triage-box{padding:18px;}
    .fiche-tri{padding:14px;}
    .reg-card-body{grid-template-columns:repeat(2,1fr);}
    .sbar-block{font-size:0.75rem;padding:12px;}
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
    "M":"TRI M - IMMEDIAT","1":"TRI 1 - URGENCE EXTREME","2":"TRI 2 - TRES URGENT",
    "3A":"TRI 3A - URGENT","3B":"TRI 3B - URGENT DIFFERE","4":"TRI 4 - MOINS URGENT","5":"TRI 5 - NON URGENT",
}
TRI_SECTORS = {
    "M":"Dechocage - Reanimation immediate","1":"Dechocage - Prise en charge immediate",
    "2":"Salle de soins aigus - Medecin < 20 min","3A":"Salle de soins aigus - Medecin < 30 min",
    "3B":"Polyclinique urgences - Medecin < 1h","4":"Consultation urgences - Medecin < 2h",
    "5":"Salle d'attente - Consultation / reorientation MG",
}
TRI_DELAIS = {"M":5,"1":5,"2":15,"3A":30,"3B":60,"4":120,"5":999}
TRI_BOX_CSS  = {"M":"box-M","1":"box-1","2":"box-2","3A":"box-3A","3B":"box-3B","4":"box-4","5":"box-5"}
TRI_HIST_CSS = {"M":"hist-M","1":"hist-1","2":"hist-2","3A":"hist-3A","3B":"hist-3B","4":"hist-4","5":"hist-5"}
TRI_EMOJI    = {"M":"🟣","1":"🔴","2":"🟠","3A":"🟡","3B":"🟡","4":"🟢","5":"🔵"}

QUESTIONS_GUIDEES = {
    "Douleur thoracique / SCA": [
        ("ECG realise ?", "ecg_fait", "bool"),
        ("ECG anormal ?", "ecg_anormal", "bool"),
        ("Douleur typique (retrosternale, constrictive, irradiation bras/machoire) ?", "douleur_typique", "bool"),
        ("Duree > 20 min ?", "duree_longue", "bool"),
    ],
    "Dyspnee / insuffisance respiratoire": [
        ("Peut parler en phrases completes ?", "parole_ok", "bool"),
        ("Tirage / sibilants audibles ?", "tirage", "bool"),
        ("Orthopnee (dort assis) ?", "orthopnee", "bool"),
    ],
    "AVC / Deficit neurologique": [
        ("Deficit moteur ou facial ?", "deficit_moteur", "bool"),
        ("Aphasie / trouble langage ?", "aphasie", "bool"),
        ("Heure exacte debut symptomes ?", "heure_debut_connue", "bool"),
        ("Delai < 4h30 ?", "delai_ok", "bool"),
    ],
    "Traumatisme cranien": [
        ("Perte de connaissance ?", "pdc", "bool"),
        ("Vomissements repetes ?", "vomissements_repetes", "bool"),
        ("Sous anticoagulants / AOD ?", "aod_avk", "bool"),
        ("GCS < 15 ?", "gcs_alt", "bool"),
    ],
    "Douleur abdominale": [
        ("Defense / contracture ?", "defense", "bool"),
        ("Fievre associee ?", "fievre_assoc", "bool"),
        ("Dernier transit normal ?", "transit_ok", "bool"),
    ],
    "Fievre": [
        ("T > 40C ou < 35.2C ?", "temp_extreme", "bool"),
        ("Confusion / purpura ?", "confusion", "bool"),
        ("Hypotension / Shock Index >= 1 ?", "hypotension", "bool"),
    ],
    "Cephalee": [
        ("Cephalee inhabituelle (1er episode) ?", "inhabituelle", "bool"),
        ("Debut brutal (coup de tonnerre) ?", "brutale", "bool"),
        ("Fievre ou raideur nuque ?", "fievre_assoc", "bool"),
    ],
    "Douleur lombaire / colique nephretique": [
        ("Douleur intense / agitation ?", "intense", "bool"),
        ("Fievre associee ?", "fievre_assoc", "bool"),
        ("Anurie / retention ?", "anurie", "bool"),
    ],
    "Hypertension arterielle": [
        ("PAS >= 180 mmHg ?", "hta_severe", "bool"),
        ("Cephalee / trouble visuel / douleur thoracique ?", "sf_associes", "bool"),
    ],
    "Allergie / anaphylaxie": [
        ("Dyspnee / stridor ?", "dyspnee", "bool"),
        ("Chute tension / malaise ?", "mauvaise_tolerance", "bool"),
        ("Urticaire generalise ?", "urticaire", "bool"),
    ],
}


# =============================================================================
# v12 : PRESCRIPTIONS ANTICIPÉES (Nouveau)
# =============================================================================
PRESCRIPTIONS_ANTICIPEES = {
    "Douleur thoracique / SCA": {
        "Gestes immediats": [
            "ECG 12 derivations IMMEDIAT (< 10 min de l'arrivee)",
            "Voie veineuse peripherique (VVP) 18G minimum",
            "Monitoring cardiorespiratoire continu (scope)",
            "Aspirine 250 mg PO/IV sauf allergie documentee",
            "Position semi-assise, O2 si SpO2 < 95%",
        ],
        "Bilan biologique": [
            "Troponine Hs T0 (puis T1h ou T3h selon protocole)",
            "Hemogramme complet + plaquettes",
            "Ionogramme, creatinine, uree",
            "TP / TCA / INR si AOD/AVK",
            "D-Dimeres si suspicion EP concomitante",
            "NT-proBNP si signes d'insuffisance cardiaque",
        ],
        "Imagerie": [
            "RX thorax face (lit si instable)",
        ],
        "Rappels critiques": [
            "Repeter ECG a 30 min si premier normal et douleur persistante",
            "NE PAS faire manger le patient (potentiel coro urgente)",
            "Alerter cardiologue si sus-decalage ST (STEMI = salle cath < 90 min)",
        ],
    },
    "Dyspnee / insuffisance respiratoire": {
        "Gestes immediats": [
            "Position semi-assise (Fowler)",
            "O2 - objectif SpO2 > 94% (88-92% si BPCO connu)",
            "VVP 18G minimum",
            "Monitoring SpO2 continue + FR",
        ],
        "Bilan biologique": [
            "Gazometrie arterielle (ou veineuse si instable)",
            "Hemogramme complet",
            "D-Dimeres si suspicion EP",
            "NT-proBNP si suspicion IC",
            "CRP + PCT si contexte infectieux",
        ],
        "Imagerie": [
            "RX thorax face debout",
            "Echographie pulmonaire (POCUS) si disponible",
        ],
        "Rappels critiques": [
            "Preparer kit IOT (intubation) si FR > 35 ou SpO2 < 85% sous O2",
            "Aerosol beta2-mimetiques si bronchospasme",
        ],
    },
    "AVC / Deficit neurologique": {
        "Gestes immediats": [
            "ALERTE FILIERE STROKE IMMEDIATE",
            "Glycemie capillaire (CI thrombolyse si < 0.6 ou > 22 mmol/L)",
            "VVP 18G bras NON parétique",
            "NE PAS faire baisser la TA sauf si PAS > 220 mmHg",
            "A jeun strict",
        ],
        "Bilan biologique": [
            "Hemogramme + plaquettes URGENT",
            "TP / TCA / INR / fibrinogene (CI thrombolyse si anomalie)",
            "Ionogramme, creatinine",
            "Troponine (FA possible)",
        ],
        "Imagerie": [
            "TDM cerebral sans injection URGENT (< 25 min door-to-CT)",
            "Angio-TDM TSA si thrombectomie envisagee",
        ],
        "Rappels critiques": [
            "Heure exacte debut symptomes = information VITALE",
            "Objectif door-to-needle < 60 min pour thrombolyse",
            "Contre-indications thrombolyse : AOD < 48h, chirurgie < 14j, AVC < 3 mois",
            "Activer neuroradiologue si occlusion gros vaisseau",
        ],
    },
    "Traumatisme cranien": {
        "Gestes immediats": [
            "Monitoring neurologique : GCS + pupilles toutes les 15 min",
            "VVP si GCS < 15 ou AOD/AVK",
            "Collier cervical si mecanisme a risque",
            "A jeun (potentiel bloc)",
        ],
        "Bilan biologique": [
            "Hemogramme + TP/INR si AOD/AVK",
            "Groupe ABO / Rh / RAI si GCS <= 8",
        ],
        "Imagerie": [
            "TDM cerebral si criteres SFMU/NICE : PDC, vomissements, AOD, GCS < 15",
        ],
        "Rappels critiques": [
            "Surveillance minimum 4h si TC benin sans indication TDM",
            "Fiche de conseil remise au patient sortant",
            "AOD/AVK = TDM SYSTEMATIQUE meme si GCS 15",
        ],
    },
    "Douleur abdominale": {
        "Gestes immediats": [
            "VVP si defense / douleur severe",
            "A jeun si suspicion chirurgicale",
            "Antalgique IV : Paracetamol 1g ou Nefopam si EVA > 5",
        ],
        "Bilan biologique": [
            "Hemogramme, CRP",
            "Lipase (pancreas)",
            "Bilan hepatique (ASAT, ALAT, GGT, bilirubine)",
            "Beta-hCG chez toute femme en age de procreer",
            "Ionogramme, creatinine",
            "BU + ECBU si signes urinaires",
        ],
        "Imagerie": [
            "Echographie abdominale (ou TDM si peritonite / urgence chirurgicale)",
        ],
        "Rappels critiques": [
            "Toucher rectal si suspicion appendicite / rectorragie",
            "Penser : grossesse extra-uterine chez toute femme en age de procreer",
        ],
    },
    "Fievre": {
        "Gestes immediats": [
            "VVP",
            "Paracetamol 1g IV si T > 38.5 et mauvaise tolerance",
        ],
        "Bilan biologique": [
            "Hemocultures x2 AVANT toute antibiotherapie",
            "Hemogramme, CRP, PCT",
            "Ionogramme, creatinine",
            "Lactates (sepsis ?)",
            "BU + ECBU",
        ],
        "Rappels critiques": [
            "Purpura fulminans = Ceftriaxone 2g IV IMMEDIATEMENT (ne pas attendre le bilan)",
            "Antibiotiques < 1h si sepsis / choc septique",
            "Rechercher porte d'entree infectieuse systematiquement",
        ],
    },
    "Allergie / anaphylaxie": {
        "Gestes immediats": [
            "ADRENALINE 0.5 mg IM (face anterolaterale cuisse) si anaphylaxie",
            "Remplissage NaCl 0.9% 500 mL en debit libre si choc",
            "Position Trendelenburg si hypotension",
            "O2 haut debit si dyspnee / desaturation",
            "Antihistaminique IV (Polaramine 5 mg)",
            "Corticoides IV (Methylprednisolone 1 mg/kg)",
        ],
        "Rappels critiques": [
            "Repeter adrenaline a 5 min si pas d'amelioration",
            "Surveillance 6h minimum (risque de reaction biphasique)",
            "Tryptase a prelever dans les 2h post-reaction",
        ],
    },
    "Intoxication medicamenteuse": {
        "Gestes immediats": [
            "VVP",
            "ECG 12 derivations (toxiques cardiotropes ?)",
            "Monitoring continu",
        ],
        "Bilan biologique": [
            "Paracetamolémie SYSTEMATIQUE",
            "Ethanolémie",
            "Screening toxicologique urinaire + sanguin",
            "Ionogramme, creatinine, bilan hepatique",
            "Gazometrie (acidose ?)",
        ],
        "Rappels critiques": [
            "Centre Antipoisons Belgique : 070 245 245",
            "N-Acetylcysteine si intoxication paracetamol selon nomogramme Rumack-Matthew",
            "Charbon active si ingestion < 1h et patient conscient (sauf CI)",
            "Evaluation psychiatrique OBLIGATOIRE si intention suicidaire",
        ],
    },
    "Intoxication non medicamenteuse": {
        "Gestes immediats": [
            "VVP",
            "ECG 12 derivations",
            "Monitoring continu",
            "Identifier le toxique (emballage, temoin, odeur)",
        ],
        "Bilan biologique": [
            "Screening toxicologique",
            "Ionogramme, creatinine",
            "Gazometrie arterielle",
            "Bilan hepatique",
        ],
        "Rappels critiques": [
            "Centre Antipoisons Belgique : 070 245 245",
            "NE PAS faire vomir (produits caustiques, moussants, petroliers)",
        ],
    },
    "Convulsions": {
        "Gestes immediats": [
            "Protection des voies aeriennes - PLS si crise en cours",
            "O2 au masque haute concentration",
            "VVP",
            "Glycemie capillaire IMMEDIATE",
            "Diazepam 10 mg IV ou Midazolam 10 mg IM si crise > 5 min",
        ],
        "Bilan biologique": [
            "Hemogramme, ionogramme (Ca, Mg, Na)",
            "Glycemie",
            "Dosage antiepileptiques si traitement connu",
        ],
        "Rappels critiques": [
            "Chronometrer la duree de la crise",
            "Etat de mal = crise > 5 min ou 2 crises sans recuperation",
            "TDM cerebral si premier episode ou contexte traumatique",
        ],
    },
    "Accouchement imminent": {
        "Gestes immediats": [
            "Appel SMUR / equipe obstetricale IMMEDIAT",
            "Preparer kit accouchement inopiné",
            "Monitoring foetal si disponible",
            "VVP gros calibre (16G)",
            "Position gynecologique / decubitus lateral gauche",
        ],
        "Rappels critiques": [
            "NE PAS TRANSPORTER si Malinas >= 8",
            "Preparer : clamps ombilicaux, draps chauds, aspirateur mucosite",
            "Oxytocine 5 UI IV lent APRES delivrance (prevention HPP)",
        ],
    },
    "Idee / comportement suicidaire": {
        "Gestes immediats": [
            "Mise en securite du patient (retirer objets dangereux)",
            "Surveillance constante (1 soignant dedie)",
            "VVP si intoxication associee",
            "Environnement calme, porte fermee",
        ],
        "Rappels critiques": [
            "Evaluation psychiatrique OBLIGATOIRE avant toute sortie",
            "Rechercher intoxication medicamenteuse associee",
            "Evaluer le risque suicidaire (RUD : Risque, Urgence, Dangerosite)",
            "Contacter la personne de confiance / famille si accord patient",
        ],
    },
    "Hypoglycemie": {
        "Gestes immediats": [
            "Glycemie capillaire IMMEDIATE",
            "Si conscient : resucrage PO (15-20g sucres rapides)",
            "Si inconscient : Glucose 30% 50 mL IV en bolus",
            "Si pas d'acces IV : Glucagon 1 mg IM/SC",
        ],
        "Rappels critiques": [
            "Controler glycemie a 15 min post-resucrage",
            "Rechercher la cause : saut de repas, surdosage insuline, sulfamides",
            "Surveillance prolongee si sulfamides (risque recidive)",
        ],
    },
}


# =============================================================================
# MOTEUR FRENCH TRIAGE SFMU V1.1
# =============================================================================
def french_triage(motif, details, fc, pas, spo2, fr, gcs, temp, age, news2_score):
    """Determine le niveau de triage FRENCH selon le motif et les parametres.
    Retourne (niveau, justification, critere_reference)."""
    try:
        if news2_score >= 9:
            return "M", "NEWS2 >= 9 : engagement vital immediat.", "NEWS2 Tri M"
        if motif == "Arret cardiorespiratoire":
            return "M", "ACR.", "FRENCH Tri M"
        if motif == "Hypotension arterielle":
            if pas <= 70: return "1", f"PAS <= 70 ({pas}).", "FRENCH Tri 1"
            if pas <= 90 or (pas <= 100 and fc > 100): return "2", "PAS basse ou choc debutant.", "FRENCH Tri 2"
            if 90 < pas <= 100: return "3B", "PAS limite.", "FRENCH Tri 3B"
            return "4", "TA dans les normes.", "FRENCH Tri 4"
        if motif == "Douleur thoracique / SCA":
            ecg = details.get("ecg", "Normal")
            dt  = details.get("douleur_type", "Atypique")
            co  = details.get("comorbidites_coronaires", False)
            dtyp = details.get("douleur_typique", False)
            if ecg == "Anormal typique SCA" or details.get("ecg_anormal", False):
                return "1", "ECG typique SCA.", "FRENCH Tri 1"
            if ecg == "Anormal non typique" or dt == "Typique persistante/intense" or (dtyp and details.get("duree_longue", False)):
                return "2", "Douleur typique persistante ou ECG douteux.", "FRENCH Tri 2"
            if co: return "3A", "Comorbidites coronaires.", "FRENCH Tri 3A"
            if dtyp or dt == "Type coronaire": return "3B", "Douleur type coronaire.", "FRENCH Tri 3B"
            return "4", "ECG normal, douleur atypique.", "FRENCH Tri 4"
        if motif == "Tachycardie / tachyarythmie":
            if fc >= 180: return "1", "FC >= 180.", "FRENCH Tri 1"
            if fc >= 130: return "2", "FC >= 130.", "FRENCH Tri 2"
            if fc > 110:  return "3B", "FC > 110.", "FRENCH Tri 3B"
            return "4", "Episode resolutif.", "FRENCH Tri 4"
        if motif == "Bradycardie / bradyarythmie":
            mt = details.get("mauvaise_tolerance", False)
            if fc <= 40: return "1", "FC <= 40.", "FRENCH Tri 1"
            if fc <= 50 and mt: return "2", "FC 40-50 + mauvaise tolerance.", "FRENCH Tri 2"
            if fc <= 50: return "3B", "FC 40-50 bien toleree.", "FRENCH Tri 3B"
            return "4", "Bradycardie toleree.", "FRENCH Tri 4"
        if motif == "Hypertension arterielle":
            sf = details.get("sf_associes", False)
            if pas >= 220 or (pas >= 180 and sf): return "2", f"PAS >= 220 ou >= 180 + SF.", "FRENCH Tri 2"
            if pas >= 180: return "3B", "PAS >= 180 sans SF.", "FRENCH Tri 3B"
            return "4", "PAS < 180.", "FRENCH Tri 4"
        if motif == "Dyspnee / insuffisance respiratoire":
            if fr >= 40 or spo2 < 86: return "1", "Detresse respiratoire.", "FRENCH Tri 1"
            if not details.get("parole_ok", True) or details.get("tirage") or details.get("orthopnee") or (30 <= fr < 40) or (86 <= spo2 <= 90):
                return "2", "Dyspnee a la parole / tirage.", "FRENCH Tri 2"
            return "3B", "Dyspnee moderee stable.", "FRENCH Tri 3B"
        if motif == "Palpitations":
            if fc >= 180: return "2", "FC >= 180.", "FRENCH Tri 2"
            if fc >= 130: return "2", "FC >= 130.", "FRENCH Tri 2"
            if details.get("malaise") or fc > 110: return "3B", "Malaise / FC > 110.", "FRENCH Tri 3B"
            return "4", "Palpitations isolees.", "FRENCH Tri 4"
        if motif == "Asthme / aggravation BPCO":
            dep = details.get("dep", 999)
            if fr >= 40 or spo2 < 86: return "1", "Detresse respiratoire.", "FRENCH Tri 1"
            if dep <= 200 or not details.get("parole_ok", True) or details.get("tirage"):
                return "2", "DEP <= 200 / dyspnee parole.", "FRENCH Tri 2"
            if dep >= 300: return "4", "DEP >= 300.", "FRENCH Tri 4"
            return "3B", "Asthme modere.", "FRENCH Tri 3B"
        if motif == "AVC / Deficit neurologique":
            dh = details.get("delai_heures", 999)
            ok = details.get("delai_ok", False)
            if dh <= 4.5 or ok: return "1", "Deficit < 4h30 - filiere Stroke / thrombolyse.", "FRENCH Tri 1"
            if dh >= 24: return "3B", "Deficit > 24h.", "FRENCH Tri 3B"
            return "2", "Deficit neurologique aigu.", "FRENCH Tri 2"
        if motif == "Alteration de conscience / Coma":
            if gcs <= 8:  return "1", f"GCS {gcs} - coma.", "FRENCH Tri 1"
            if gcs <= 13: return "2", f"GCS {gcs} - alteration moderee.", "FRENCH Tri 2"
            return "3B", "Alteration legere.", "FRENCH Tri 3B"
        if motif == "Convulsions":
            if details.get("crises_multiples") or details.get("en_cours") or details.get("confusion_post_critique") or temp >= 38.5:
                return "2", "Crise en cours / multiple / confusion.", "FRENCH Tri 2"
            return "3B", "Recuperation complete.", "FRENCH Tri 3B"
        if motif == "Cephalee":
            if details.get("inhabituelle") or details.get("brutale") or details.get("fievre_assoc") or temp >= 38.5:
                return "2", "Cephalee inhabituelle / brutale / febrile.", "FRENCH Tri 2"
            return "3B", "Migraine connue.", "FRENCH Tri 3B"
        if motif == "Vertiges / trouble de l'equilibre":
            if details.get("signes_neuro") or details.get("cephalee_brutale"):
                return "2", "Signes neuro.", "FRENCH Tri 2"
            return "5", "Troubles stables.", "FRENCH Tri 5"
        if motif == "Confusion / desorientation":
            if temp >= 38.5: return "2", "Confusion + fievre.", "FRENCH Tri 2"
            return "3B", "Confusion afebrile.", "FRENCH Tri 3B"
        if motif == "Hematemese / vomissement de sang":
            if details.get("abondante"): return "2", "Hematemese abondante.", "FRENCH Tri 2"
            return "3B", "Striures de sang.", "FRENCH Tri 3B"
        if motif == "Rectorragie / melena":
            if details.get("abondante"): return "2", "Rectorragie abondante.", "FRENCH Tri 2"
            return "3B", "Selles souillees.", "FRENCH Tri 3B"
        if motif == "Douleur abdominale":
            if details.get("defense") or details.get("contracture") or details.get("mauvaise_tolerance"):
                return "2", "Defense / contracture.", "FRENCH Tri 2"
            if details.get("regressive"): return "5", "Douleur regressive.", "FRENCH Tri 5"
            return "3B", "Douleur moderee.", "FRENCH Tri 3B"
        if motif == "Douleur lombaire / colique nephretique":
            if details.get("intense"): return "2", "Douleur intense.", "FRENCH Tri 2"
            if details.get("regressive"): return "5", "Douleur regressive.", "FRENCH Tri 5"
            return "3B", "Douleur moderee.", "FRENCH Tri 3B"
        if motif == "Retention d'urine / anurie":
            return "2", "Retention urinaire.", "FRENCH Tri 2"
        if motif == "Douleur testiculaire / torsion":
            if details.get("intense") or details.get("suspicion_torsion"):
                return "2", "Torsion suspectee.", "FRENCH Tri 2"
            return "3B", "Avis specialiste de garde.", "FRENCH Tri 3B"
        if motif == "Hematurie":
            if details.get("abondante_active"): return "2", "Hematurie abondante.", "FRENCH Tri 2"
            return "3B", "Hematurie moderee.", "FRENCH Tri 3B"
        if motif == "Traumatisme avec amputation":
            return "M", "Amputation.", "FRENCH Tri M"
        if motif == "Traumatisme abdomen / thorax / cervical":
            if details.get("penetrant"): return "1", "Penetrant.", "FRENCH Tri 1"
            if details.get("cinetique") == "Haute": return "2", "Haute velocite.", "FRENCH Tri 2"
            if details.get("mauvaise_tolerance"): return "3B", "Faible velocite + mauvaise tolerance.", "FRENCH Tri 3B"
            return "4", "Bonne tolerance.", "FRENCH Tri 4"
        if motif == "Traumatisme cranien":
            if gcs <= 8: return "1", f"TC coma GCS {gcs}.", "FRENCH Tri 1"
            if gcs <= 13 or details.get("deficit_neuro") or details.get("convulsion") or details.get("aod_avk") or details.get("vomissements_repetes"):
                return "2", "GCS 9-13 / deficit / AVK / vomissements.", "FRENCH Tri 2"
            if details.get("pdc") or details.get("plaie") or details.get("hematome"):
                return "3B", "PDC / plaie.", "FRENCH Tri 3B"
            return "5", "TC sans signe gravite.", "FRENCH Tri 5"
        if motif == "Brulure":
            if details.get("etendue") or details.get("main_visage"):
                return "2", "Etendue / main / visage.", "FRENCH Tri 2"
            if age <= 2: return "3A", "Enfant <= 24 mois.", "FRENCH Tri 3A"
            return "3B", "Brulure limitee.", "FRENCH Tri 3B"
        if motif == "Traumatisme bassin / hanche / femur / rachis":
            if details.get("cinetique") == "Haute": return "2", "Haute velocite.", "FRENCH Tri 2"
            if details.get("mauvaise_tolerance"): return "3B", "Mauvaise tolerance.", "FRENCH Tri 3B"
            return "4", "Bonne tolerance.", "FRENCH Tri 4"
        if motif == "Traumatisme membre / epaule":
            if details.get("ischemie") or details.get("cinetique") == "Haute":
                return "2", "Ischemie / haute velocite.", "FRENCH Tri 2"
            if details.get("impotence_totale") or details.get("deformation"):
                return "3B", "Impotence totale.", "FRENCH Tri 3B"
            if details.get("impotence_moderee"): return "4", "Impotence moderee.", "FRENCH Tri 4"
            return "5", "Ni impotence ni deformation.", "FRENCH Tri 5"
        if motif == "Plaie":
            if details.get("delabrant") or details.get("saignement_actif"):
                return "2", "Delabrante / saignement.", "FRENCH Tri 2"
            if details.get("large_complexe") or details.get("main"):
                return "3B", "Large / main.", "FRENCH Tri 3B"
            if details.get("superficielle"): return "4", "Superficielle.", "FRENCH Tri 4"
            return "5", "Excoriation.", "FRENCH Tri 5"
        if motif == "Electrisation":
            if details.get("pdc") or details.get("foudre"): return "2", "PDC / foudre.", "FRENCH Tri 2"
            if details.get("haute_tension"): return "3B", "Haute tension.", "FRENCH Tri 3B"
            return "4", "Courant domestique.", "FRENCH Tri 4"
        if motif == "Agression sexuelle / sevices":
            return "1", "Agression sexuelle.", "FRENCH Tri 1"
        if motif == "Idee / comportement suicidaire":
            return "1", "Comportement suicidaire.", "FRENCH Tri 1"
        if motif == "Troubles du comportement / psychiatrie":
            if details.get("agitation") or details.get("violence"):
                return "2", "Agitation/violence.", "FRENCH Tri 2"
            return "4", "Consultation psychiatrique.", "FRENCH Tri 4"
        if motif in ["Intoxication medicamenteuse", "Intoxication non medicamenteuse"]:
            if details.get("mauvaise_tolerance") or details.get("intention_suicidaire") or details.get("cardiotropes"):
                return "2", "Mauvaise tolerance / suicidaire.", "FRENCH Tri 2"
            return "3B", "Avis specialiste de garde.", "FRENCH Tri 3B"
        if motif == "Fievre":
            if temp >= 40 or temp <= 35.2 or details.get("confusion") or details.get("purpura") or details.get("temp_extreme"):
                return "2", "Fievre severe ou signes graves.", "FRENCH Tri 2"
            if details.get("mauvaise_tolerance") or details.get("hypotension") or pas < 100:
                return "3B", "Mauvaise tolerance.", "FRENCH Tri 3B"
            return "5", "Fievre toleree.", "FRENCH Tri 5"
        if motif == "Accouchement imminent":
            return "M", "Accouchement imminent.", "FRENCH Tri M"
        if motif in ["Probleme de grossesse (1er/2eme trimestre)", "Probleme de grossesse (3eme trimestre)"]:
            return "3A", "Grossesse - surveillance urgente.", "FRENCH Tri 3A"
        if motif == "Meno-metrorragie":
            if details.get("grossesse") or details.get("abondante"):
                return "2", "Grossesse / abondante.", "FRENCH Tri 2"
            return "3B", "Moderee.", "FRENCH Tri 3B"
        if motif == "Hyperglycemie":
            gl = details.get("glycemie", 0)
            if details.get("cetose_elevee") or gcs < 15:
                return "2", "Cetose / trouble conscience.", "FRENCH Tri 2"
            if gl >= 20 or details.get("cetose_positive"):
                return "3B", f"Glycemie >= 20 ({gl}).", "FRENCH Tri 3B"
            return "4", "Hyperglycemie moderee.", "FRENCH Tri 4"
        if motif == "Hypoglycemie":
            if gcs <= 8:  return "1", f"Coma hypoglycemique GCS {gcs}.", "FRENCH Tri 1"
            if gcs <= 13 or details.get("mauvaise_tolerance"):
                return "2", "Mauvaise tolerance.", "FRENCH Tri 2"
            return "3B", "Hypoglycemie moderee.", "FRENCH Tri 3B"
        if motif == "Hypothermie":
            if temp <= 32: return "1", f"Hypothermie severe T {temp}.", "FRENCH Tri 1"
            if temp <= 35.2: return "2", "Hypothermie moderee.", "FRENCH Tri 2"
            return "3B", "Hypothermie legere.", "FRENCH Tri 3B"
        if motif == "Coup de chaleur / insolation":
            if gcs <= 8: return "1", "Coup chaleur + coma.", "FRENCH Tri 1"
            if temp >= 40: return "2", f"T >= 40C ({temp}).", "FRENCH Tri 2"
            return "3B", "Coup chaleur leger.", "FRENCH Tri 3B"
        if motif == "Allergie / anaphylaxie":
            if details.get("dyspnee") or details.get("mauvaise_tolerance"):
                return "2", "Anaphylaxie severe.", "FRENCH Tri 2"
            return "4", "Reaction legere.", "FRENCH Tri 4"
        if motif == "Epistaxis":
            if details.get("abondant_actif"): return "2", "Abondant actif.", "FRENCH Tri 2"
            if details.get("abondant_resolutif"): return "3B", "Abondant resolutif.", "FRENCH Tri 3B"
            return "5", "Peu abondant.", "FRENCH Tri 5"
        if motif in ["Corps etranger / brulure oculaire", "Trouble visuel / cecite"]:
            if details.get("intense") or details.get("chimique") or details.get("brutal"):
                return "2", "Urgence ophtalmologique.", "FRENCH Tri 2"
            return "3B", "Avis specialiste de garde.", "FRENCH Tri 3B"
        # Fallback
        eva = details.get("eva", 0)
        if news2_score >= 5 or gcs < 15: return "2", f"NEWS2={news2_score} GCS={gcs}.", "NEWS2/GCS"
        if news2_score >= 1 or eva >= 7:  return "3B", f"EVA={eva} NEWS2={news2_score}.", "NEWS2/EVA"
        if eva >= 4: return "4", f"EVA {eva}/10.", "EVA"
        return "5", "Non urgent.", "Defaut"
    except (TypeError, ValueError) as e:
        return "3B", f"Erreur evaluation ({e}) - triage par defaut.", "Erreur"


# =============================================================================
# NEWS2
# =============================================================================
def compute_news2(fr, spo2, supp_o2, temp, pas, fc, gcs, bpco):
    """Calcule le score NEWS2 a partir des parametres vitaux."""
    try:
        s = 0
        s += 3 if fr <= 8 else (1 if fr <= 11 else (0 if fr <= 20 else (2 if fr <= 24 else 3)))
        if not bpco:
            s += 3 if spo2 <= 91 else (2 if spo2 <= 93 else (1 if spo2 <= 95 else 0))
        else:
            s += (3 if spo2 <= 83 else (2 if spo2 <= 85 else (1 if spo2 <= 87 else (0 if spo2 <= 92 else (1 if spo2 <= 94 else (2 if spo2 <= 96 else 3))))))
        if supp_o2: s += 2
        s += 3 if temp <= 35.0 else (1 if temp <= 36.0 else (0 if temp <= 38.0 else (1 if temp <= 39.0 else 2)))
        s += 3 if pas <= 90 else (2 if pas <= 100 else (1 if pas <= 110 else (0 if pas <= 219 else 3)))
        s += 3 if fc <= 40 else (1 if fc <= 50 else (0 if fc <= 90 else (1 if fc <= 110 else (2 if fc <= 130 else 3))))
        if gcs < 15: s += 3
        return s
    except (TypeError, ValueError):
        return 0

def news2_level(score):
    """Retourne le label et la classe CSS pour un score NEWS2."""
    if score == 0:  return "Faible (0)", "news2-low"
    if score <= 4:  return f"Faible ({score})", "news2-low"
    if score <= 6:  return f"Modere ({score})", "news2-med"
    if score <= 8:  return f"Eleve ({score})", "news2-high"
    return f"CRITIQUE ({score})", "news2-crit"

def vital_badge(val, lw, lc, hw, hc, u=""):
    """Retourne un badge HTML pour les alertes des signes vitaux."""
    try:
        if val <= lc or val >= hc: return f'<span class="vital-alert vital-crit">! {val}{u}</span>'
        if val <= lw or val >= hw: return f'<span class="vital-alert vital-warn">~ {val}{u}</span>'
        return f'<span class="vital-alert vital-ok">ok</span>'
    except (TypeError, ValueError):
        return '<span class="vital-alert vital-warn">?</span>'


# =============================================================================
# v12 : BANDEAUX D'ALERTE VISUELLE (Securite Clinique)
# =============================================================================
def render_danger_banners(news2_score, sil_score, niveau, fc, pas, spo2, fr, gcs, temp):
    """Affiche les bandeaux de couleur si NEWS2 ou Silverman indiquent un danger immediat."""
    banners = []

    # NEWS2 critique
    if news2_score >= 7:
        banners.append(
            '<div class="danger-banner">'
            f'<div class="danger-banner-title">⚠ DANGER IMMEDIAT — NEWS2 = {news2_score}</div>'
            '<div class="danger-banner-detail">Engagement vital probable — Transfert dechocage IMMEDIAT — Appel medecin senior</div>'
            '</div>'
        )
    elif news2_score >= 5:
        banners.append(
            '<div class="warning-banner">'
            f'<div class="warning-banner-title">△ ALERTE — NEWS2 = {news2_score}</div>'
            '<div class="warning-banner-detail">Evaluation medicale urgente requise dans les 30 minutes</div>'
            '</div>'
        )

    # Silverman (si fourni)
    if sil_score is not None and sil_score >= 5:
        banners.append(
            '<div class="danger-banner">'
            f'<div class="danger-banner-title">⚠ DETRESSE NEONATALE — Silverman = {sil_score}/10</div>'
            '<div class="danger-banner-detail">Appel pediatre / neonatologue IMMEDIAT — Preparer reanimation neonatale</div>'
            '</div>'
        )

    # Choc / instabilite hemodynamique
    if pas > 0 and fc / pas >= 1.0:
        si = round(fc / pas, 1)
        banners.append(
            '<div class="danger-banner">'
            f'<div class="danger-banner-title">⚠ CHOC — Shock Index = {si}</div>'
            '<div class="danger-banner-detail">FC {fc} / PAS {pas} — 2 VVP gros calibre + remplissage NaCl 0.9%</div>'
            '</div>'.format(fc=fc, pas=pas)
        )

    # Detresse respiratoire
    if spo2 < 85 or fr >= 40:
        banners.append(
            '<div class="danger-banner">'
            f'<div class="danger-banner-title">⚠ DETRESSE RESPIRATOIRE — SpO2 {spo2}% / FR {fr}</div>'
            '<div class="danger-banner-detail">O2 haut debit immediat — Preparer IOT si echec</div>'
            '</div>'
        )

    # Coma
    if gcs <= 8:
        banners.append(
            '<div class="danger-banner">'
            f'<div class="danger-banner-title">⚠ COMA — GCS {gcs}/15</div>'
            '<div class="danger-banner-detail">Protection voies aeriennes — PLS — Evaluer intubation</div>'
            '</div>'
        )

    for b in banners:
        st.markdown(b, unsafe_allow_html=True)

    return len(banners) > 0


# =============================================================================
# v12 : AFFICHAGE PRESCRIPTIONS ANTICIPEES
# =============================================================================
def render_prescriptions_anticipees(motif):
    """Affiche les prescriptions anticipees pour un motif donne."""
    rx = PRESCRIPTIONS_ANTICIPEES.get(motif)
    if not rx:
        return
    st.markdown('<div class="section-header">Prescriptions anticipees IAO</div>', unsafe_allow_html=True)
    cols = st.columns(min(len(rx), 3))
    for i, (category, items) in enumerate(rx.items()):
        col = cols[i % len(cols)]
        is_urgent = category in ["Gestes immediats", "Rappels critiques"]
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


# =============================================================================
# ECHELLE DOULEUR ADAPTEE A L'AGE
# =============================================================================
def echelle_douleur(age_patient):
    """Retourne (score, echelle_nom, interpretation, css_class) selon l'age."""
    if age_patient < 3:
        st.markdown("**Echelle FLACC** *(< 3 ans — observation comportementale)*")
        items = {
            "Visage (grimace, froncement)":    ["0 - Aucune expression", "1 - Grimace occasionnelle", "2 - Froncement permanent"],
            "Jambes (agitation)":              ["0 - Position normale", "1 - Genees, agitees", "2 - Crispees / ruades"],
            "Activite (position corps)":       ["0 - Allong, calme", "1 - Se tortille / arquee", "2 - Rigide / convulsive"],
            "Pleurs":                          ["0 - Pas de pleurs", "1 - Gemissements", "2 - Pleurs continus"],
            "Consolabilite":                   ["0 - Calme facilement", "1 - Difficile a calmer", "2 - Inconsolable"],
        }
        total = 0
        ca, cb = st.columns(2)
        for i, (lbl, opts) in enumerate(items.items()):
            col = ca if i < 3 else cb
            v = col.selectbox(lbl, opts, key=f"flacc_{i}")
            total += int(v[0])
        if total <= 2:   interp, css = "Douleur legere / absente", "score-low"
        elif total <= 6: interp, css = "Douleur moderee - antalgiques niveau 1 OMS", "score-med"
        else:            interp, css = "Douleur severe - antalgiques IV urgents", "score-high"
        return total, "FLACC", interp, css
    elif age_patient < 8:
        st.markdown("**Echelle des visages Wong-Baker** *(3-8 ans)*")
        st.caption("Montrer les visages et demander : *Quel visage montre comment tu te sens ?*")
        faces = {
            "0 - Tres heureux, pas de douleur": 0,
            "2 - Un peu de douleur": 2,
            "4 - Douleur un peu plus forte": 4,
            "6 - Douleur encore plus forte": 6,
            "8 - Beaucoup de douleur": 8,
            "10 - Douleur insupportable": 10,
        }
        choix = st.selectbox("Visage choisi par l'enfant", list(faces.keys()), key="wong_baker")
        score = faces[choix]
        if score <= 2:  interp, css = "Douleur legere", "score-low"
        elif score <= 6: interp, css = "Douleur moderee", "score-med"
        else:            interp, css = "Douleur severe", "score-high"
        return score, "Wong-Baker", interp, css
    else:
        st.markdown("**Echelle Visuelle Analogique (EVA)** *(>= 8 ans)*")
        # v12 : Remplacement du slider par des boutons de selection rapide pour mobile
        eva_options = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        c1, c2 = st.columns([3, 1])
        with c1:
            score_str = st.select_slider(
                "Douleur de 0 (aucune) a 10 (maximale)",
                options=eva_options,
                value="0",
                key="eva_std"
            )
        score = int(score_str)
        emoji_map = {0: "😌", 1: "🙂", 2: "🙂", 3: "😐", 4: "😐", 5: "😟", 6: "😟", 7: "😣", 8: "😣", 9: "😫", 10: "😭"}
        with c2:
            st.markdown(f"### {emoji_map.get(score, '😐')} {score}/10")
        if score <= 3:   interp, css = "Douleur legere - niveau 1 OMS", "score-low"
        elif score <= 6: interp, css = "Douleur moderee - niveau 1-2 OMS", "score-med"
        else:            interp, css = "Douleur severe - niveau 2-3 OMS ou IV", "score-high"
        return score, "EVA", interp, css


# =============================================================================
# GENERATION FICHE DE TRI
# =============================================================================
def generate_fiche_tri(age, motif, niveau, tri_label, sector, temp, fc, pas, spo2, fr, gcs,
                        news2, news2_label, eva, atcd, allergies, arrivee_str, details, nom="", prenom=""):
    """Genere le HTML de la fiche de tri imprimable."""
    atcd_str = ", ".join(atcd) if atcd else "RAS"
    all_str  = allergies if allergies != "RAS" else "Aucune connue"
    identite = f"{nom.upper()} {prenom}" if nom or prenom else "NON RENSEIGNE"
    return f"""
<div class="fiche-tri">
  <div class="fiche-header">
    <div class="fiche-title">FICHE DE TRI — IAO Expert Pro v12 | CHR Haute Senne</div>
    <div style="font-size:0.75rem;color:#64748b;">{arrivee_str}</div>
  </div>
  <div class="fiche-niveau fiche-{niveau}">{TRI_EMOJI.get(niveau, '')} {tri_label}</div>
  <div class="fiche-section">PATIENT</div>
  <div class="fiche-row"><span>Identite</span><span><b>{identite}</b></span></div>
  <div class="fiche-row"><span>Age</span><span>{age} ans</span></div>
  <div class="fiche-row"><span>Motif</span><span><b>{motif}</b></span></div>
  <div class="fiche-row"><span>Allergies</span><span style="color:#dc2626;font-weight:600">{all_str}</span></div>
  <div class="fiche-row"><span>ATCD</span><span>{atcd_str}</span></div>
  <div class="fiche-section">CONSTANTES</div>
  <div class="fiche-row"><span>T°</span><span>{temp} C</span></div>
  <div class="fiche-row"><span>FC</span><span>{fc} bpm</span></div>
  <div class="fiche-row"><span>PAS</span><span>{pas} mmHg</span></div>
  <div class="fiche-row"><span>SpO2</span><span>{spo2} %</span></div>
  <div class="fiche-row"><span>FR</span><span>{fr} resp/min</span></div>
  <div class="fiche-row"><span>GCS</span><span>{gcs}/15</span></div>
  <div class="fiche-row"><span>NEWS2</span><span>{news2} - {news2_label}</span></div>
  <div class="fiche-row"><span>EVA/FLACC</span><span>{eva}/10</span></div>
  <div class="fiche-section">ORIENTATION</div>
  <div class="fiche-row"><span>Secteur</span><span><b>{sector}</b></span></div>
  <div style="font-size:0.7rem;color:#94a3b8;margin-top:10px;text-align:center;">
    FRENCH Triage - Adaptation SIAMU Belgique - Ismaïl Ibn-Daïfa, Infirmier SIAMU — CHR Haute Senne
  </div>
</div>
"""


# =============================================================================
# ALERTES DE SECURITE
# =============================================================================
def check_coherence(fc, pas, spo2, fr, gcs, temp, s_eva, motif, atcd, details, news2_score):
    """Verifie la coherence clinique et genere les alertes de securite.
    Retourne (danger_list, warning_list, info_list)."""
    danger, warning, info = [], [], []
    try:
        if s_eva == 0 and fc > 110:
            warning.append("Incoherence : EVA 0 mais FC > 110 - evaluer douleur ou autre cause")
        if gcs == 15 and spo2 < 88:
            warning.append("Incoherence : GCS 15 mais SpO2 < 88% - verifier capteur")
        if "Anticoagulants / AOD" in atcd and "cranien" in motif.lower():
            danger.append("DANGER : TC sous anticoagulants - TDM cerebral URGENT - risque hematome x10")
        if "Anticoagulants / AOD" in atcd and ("AVC" in motif or "neurologique" in motif.lower()):
            danger.append("DANGER : AVC suspect sous AOD - CONTRE-INDICATION thrombolyse - neuro IMMEDIAT")
        if "allergie" in motif.lower() and details.get("dyspnee"):
            danger.append("ANAPHYLAXIE SEVERE : Adrenaline 0.5 mg IM immediatement")
        if details.get("mal_score", 0) >= 8 or motif == "Accouchement imminent":
            danger.append("NE PAS TRANSPORTER : Malinas >= 8 - protocole accouchement inopine")
        if news2_score >= 5 and temp >= 38.5:
            danger.append("SEPSIS GRAVE : NEWS2 >= 5 + fievre - hemocultures + antibiotiques dans l'heure")
        if pas > 0 and pas < 90 and fc > 100:
            si = round(fc / pas, 1)
            danger.append(f"CHOC probable : Shock Index {si} (FC {fc}/PAS {pas}) - 2 VVP + remplissage NaCl 0.9%")
        if spo2 < 85 or fr >= 40:
            danger.append(f"DETRESSE RESPIRATOIRE : SpO2 {spo2}% FR {fr} - O2 haut debit + preparer IOT")
        if gcs <= 8:
            danger.append(f"COMA GCS {gcs} : Protection VA - PLS - intubation a evaluer (REA)")
        if temp <= 32:
            danger.append(f"HYPOTHERMIE SEVERE T {temp}C : rechauffement actif - risque FV")
        if temp >= 41:
            danger.append(f"HYPERTHERMIE MALIGNE T {temp}C : refroidissement immediat")
        if "Immunodepression" in atcd and temp >= 38.5:
            warning.append("NEUTROPENIE FEBRILE possible : Hemogramme urgent + antibiotiques sans attendre")
    except (TypeError, ValueError):
        warning.append("Erreur lors de la verification de coherence - verifier les parametres")
    return danger, warning, info


# =============================================================================
# BILANS SUGGERES
# =============================================================================
def suggest_bilan(motif, details, fc, pas, spo2, fr, gcs, temp, age, atcd, news2_score, niveau):
    """Genere les bilans recommandes selon le motif et la gravite."""
    b = {"Biologie": [], "Imagerie": [], "ECG / Monitoring": [], "Gestes immediats": [], "Avis specialiste": []}
    if niveau in ["M", "1", "2"]:
        b["Biologie"] += ["Hemogramme complet + plaquettes", "Ionogramme, creatinine", "Glycemie", "Groupe RAI"]
        b["ECG / Monitoring"] += ["Monitoring cardiorespiratoire continu", "SpO2 continue", "VVP (gros calibre)"]
    if "thoracique" in motif.lower() or "SCA" in motif:
        b["Biologie"] += ["Troponine Hs T0 et T1h", "D-Dimeres si EP", "NT-proBNP si IC"]
        b["ECG / Monitoring"] += ["ECG 12 derivations URGENT", "Repeter ECG a 30 min"]
        b["Imagerie"] += ["RX thorax face"]
        b["Gestes immediats"] += ["Aspirine 250 mg si SCA non CI", "O2 si SpO2 < 95%"]
        if "Anticoagulants / AOD" in atcd:
            b["Gestes immediats"] += ["ATTENTION anticoagulants - adapter HBPM/heparine"]
    if "AVC" in motif or "neurologique" in motif.lower():
        b["Biologie"] += ["Hemogramme + coagulation (TP, TCA, fibrinogene)", "Glycemie"]
        b["Imagerie"] += ["TDM cerebral sans injection URGENT", "IRM si disponible"]
        b["Avis specialiste"] += ["Neurologue vasculaire urgent"]
        b["Gestes immediats"] += ["ALERTE FILIERE STROKE - door-to-needle < 60 min"]
    if "dyspnee" in motif.lower() or "respiratoire" in motif.lower():
        b["Biologie"] += ["Gazometrie arterielle", "D-Dimeres si EP"]
        b["Imagerie"] += ["RX thorax", "Echographie pulmonaire si dispo"]
        b["Gestes immediats"] += ["O2 - objectif SpO2 > 94%", "Position semi-assise (Fowler)"]
    if "traumatisme" in motif.lower() and niveau in ["M", "1", "2"]:
        b["Biologie"] += ["Bilan pre-transfusionnel (groupe, Rh, RAI, Coombs)", "Lactates"]
        b["Imagerie"] += ["CT-scanner corps entier si polytrauma", "Echographie FAST"]
        b["Gestes immediats"] += ["Compression directe hemorragie + garrot si membre", "2 VVP + remplissage NaCl 0.9%"]
    if "fievre" in motif.lower() or (temp >= 38.5 and news2_score >= 3):
        b["Biologie"] += ["Hemocultures x2 AVANT antibiotiques", "Lactates", "CRP, PCT, hemogramme"]
        b["Gestes immediats"] += ["Hemocultures AVANT antibiotherapie", "Antibiotiques large spectre si sepsis grave"]
    if "allergie" in motif.lower():
        b["Gestes immediats"] += ["ADRENALINE 0.5 mg IM", "Antihistaminique + corticoides IV", "Remplissage NaCl 0.9%"]
    if "hypoglycemie" in motif.lower():
        b["Gestes immediats"] += ["Glycemie capillaire IMMEDIATE", "Glucose 30% 50mL IV si inconscient", "Glucagon 1mg IM/SC si pas d'acces"]
    if "intoxication" in motif.lower():
        b["Biologie"] += ["Screening toxicologique urinaire + sanguin", "Paracetamol + ethanol systematiques"]
        b["ECG / Monitoring"] += ["ECG - toxiques cardiotropes"]
        b["Avis specialiste"] += ["Centre Antipoisons (070 245 245)"]
    return {k: v for k, v in b.items() if v}


# =============================================================================
# v12 : SBAR NARRATIF AMÉLIORÉ
# =============================================================================
def generate_sbar(age, motif, cat, atcd, allergies, supp_o2, temp, fc, pas, spo2, fr, gcs,
                  news2, news2_label, eva, eva_echelle, p_pqrst, q_pqrst, r_pqrst, t_onset,
                  details, niveau, tri_label, justif, critere_ref, sector,
                  gcs_y=4, gcs_v=5, gcs_m=6, nom="", prenom=""):
    """Genere une transmission SBAR professionnelle et structuree."""
    now_str  = datetime.now().strftime("%d/%m/%Y a %H:%M")
    date_str = datetime.now().strftime("%d/%m/%Y")
    heure_str = datetime.now().strftime("%H:%M")
    atcd_str = ", ".join(atcd) if atcd else "aucun antecedent notable"
    all_str  = allergies if allergies and allergies != "RAS" else "aucune allergie connue"
    identite = f"{nom.upper()} {prenom}" if nom or prenom else "Non renseigne"

    if gcs == 15: conscience = "conscient et oriente"
    elif gcs >= 13: conscience = f"conscience alteree GCS {gcs} (Y{gcs_y}V{gcs_v}M{gcs_m})"
    elif gcs >= 9:  conscience = f"obnubile GCS {gcs} (Y{gcs_y}V{gcs_v}M{gcs_m})"
    else:           conscience = f"COMA GCS {gcs} (Y{gcs_y}V{gcs_v}M{gcs_m})"

    anomalies = []
    if temp > 38 or temp < 36: anomalies.append(f"T {temp}°C")
    if fc > 100:  anomalies.append(f"tachycardie {fc} bpm")
    if fc < 60:   anomalies.append(f"bradycardie {fc} bpm")
    if pas < 90:  anomalies.append(f"hypotension {pas} mmHg")
    if pas > 180: anomalies.append(f"HTA {pas} mmHg")
    if spo2 < 94: anomalies.append(f"desaturation {spo2}%")
    if fr > 20:   anomalies.append(f"tachypnee {fr}/min")
    vitaux_txt = "dans les normes" if not anomalies else "ANOMALIES : " + ", ".join(anomalies)

    shock_index = round(fc / pas, 2) if pas > 0 else 0

    # Prescriptions anticipees dans le SBAR
    rx_txt = ""
    rx = PRESCRIPTIONS_ANTICIPEES.get(motif)
    if rx and rx.get("Gestes immediats"):
        rx_items = rx["Gestes immediats"][:4]
        rx_txt = "\n  Prescriptions anticipees IAO :\n" + "\n".join([f"    ☐ {item}" for item in rx_items])

    # Recommandation adaptee au niveau
    if niveau in ['M', '1']:
        reco = "DEMANDE PRISE EN CHARGE IMMEDIATE EN DECHOCAGE."
    elif niveau == '2':
        reco = "Demande evaluation medicale urgente < 20 min."
    elif niveau == '3A':
        reco = "Evaluation dans les 30 min - salle de soins aigus."
    elif niveau == '3B':
        reco = "Evaluation dans l'heure - polyclinique urgences."
    elif niveau == '4':
        reco = "Evaluation dans les 2h - consultation urgences."
    else:
        reco = "Consultation non urgente / reorientation MG."

    return f"""╔══════════════════════════════════════════════════════════╗
║  TRANSMISSION SBAR — IAO Expert Pro v12.0               ║
║  CHR Haute Senne — Service des Urgences                  ║
║  {date_str} — {heure_str}                                      ║
╚══════════════════════════════════════════════════════════╝

━━━ [S] SITUATION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Patient     : {identite}, {age} ans
  Admission   : {now_str}
  Motif       : {motif} ({cat})
  Douleur     : {eva}/10 ({eva_echelle})
  Conscience  : {conscience}
  ► NIVEAU    : {tri_label}

━━━ [B] BACKGROUND ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ATCD        : {atcd_str}
  Allergies   : {all_str}
  O2 a l'admission : {'OUI' if supp_o2 else 'non'}

━━━ [A] ASSESSMENT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Constantes :
    T° {temp}°C | FC {fc} bpm | PAS {pas} mmHg
    SpO2 {spo2}% | FR {fr}/min | GCS {gcs}/15
  Shock Index : {shock_index}
  Bilan vitaux : {vitaux_txt}

  NEWS2 : {news2} ({news2_label})

  PQRST :
    P — Provoque/Pallie : {p_pqrst or 'non precise'}
    Q — Qualite/Type    : {q_pqrst}
    R — Region/Irrad.   : {r_pqrst or 'non precise'}
    S — Severite        : {eva}/10 ({eva_echelle})
    T — Temps/Duree     : {t_onset or 'non precise'}

  Justification triage : {justif}
  Reference FRENCH     : {critere_ref}

━━━ [R] RECOMMENDATION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Orientation : {sector}
  ► {reco}
{rx_txt}

──────────────────────────────────────────────────────────
  Signe : Ismaïl Ibn-Daïfa (Infirmier SIAMU)
  CHR Haute Senne — {now_str}
  Ref. FRENCH Triage SFMU V1.1 — Adaptation SIAMU Belgique
──────────────────────────────────────────────────────────
"""


# =============================================================================
# v12 : DISCLAIMER JURIDIQUE
# =============================================================================
def render_disclaimer():
    """Affiche le disclaimer juridique en bas de page."""
    st.markdown(
        '<div class="disclaimer">'
        '<div class="disclaimer-title">Avertissement juridique et clinique</div>'
        'Cet outil d\'aide au triage est un support a la decision clinique destine aux infirmiers(eres) '
        'agrees exerçant en service d\'accueil des urgences (SAU). Il ne se substitue en aucun cas au '
        'jugement clinique du professionnel de sante ni a l\'examen medical. Les niveaux de triage proposes '
        'sont fondes sur la grille FRENCH Triage (SFMU V1.1, 2018) et doivent etre valides par l\'IAO '
        'en fonction du contexte clinique. Les prescriptions anticipees sont des rappels et ne constituent '
        'pas des prescriptions medicales : elles doivent etre validees par le medecin responsable. '
        'L\'utilisation de cet outil engage la responsabilite de l\'utilisateur. Toute donnee patient '
        'est stockee localement et n\'est pas transmise a des tiers. '
        'Adaptation SIAMU Belgique — Conforme a la legislation belge sur l\'exercice infirmier (AR 18/06/1990). '
        'En cas de doute, toujours sur-trier et demander un avis medical.'
        '</div>',
        unsafe_allow_html=True
    )


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown("## IAO Expert Pro v12.0")
    st.caption("FRENCH Triage — CHR Haute Senne")

    st.markdown('<div class="section-header">Mode</div>', unsafe_allow_html=True)
    mode = st.radio("Interface", ["Tri Rapide (< 2 min)", "Complet"], horizontal=True, label_visibility="collapsed")
    st.session_state.mode = "rapide" if "Rapide" in mode else "complet"

    st.markdown('<div class="section-header">Chronometre</div>', unsafe_allow_html=True)
    ca, cb = st.columns(2)
    if ca.button("Demarrer", use_container_width=True):
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
        st.markdown(f'<div class="chrono-label">Arrivee {st.session_state.arrival_time.strftime("%H:%M")}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="chrono">--:--:--</div>', unsafe_allow_html=True)
        st.markdown('<div class="chrono-label">En attente</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">Identite Patient</div>', unsafe_allow_html=True)
    p_nom    = st.text_input("Nom", "", key="sb_nom", placeholder="NOM")
    p_prenom = st.text_input("Prenom", "", key="sb_prenom", placeholder="Prenom")
    age      = st.number_input("Age", 0, 120, 45)
    atcd     = st.multiselect("Facteurs de risque", [
        "HTA", "Diabete", "Insuffisance Cardiaque", "BPCO",
        "Anticoagulants / AOD", "Grossesse", "Immunodepression", "Neoplasie"
    ])
    allergies = st.text_input("Allergies", "RAS")
    supp_o2   = st.checkbox("O2 supplementaire")

    db_count = len(load_patient_db())
    st.markdown(f'<div class="section-header">Registre : {db_count} patient(s)</div>', unsafe_allow_html=True)

    st.markdown('<div class="legal-text">FRENCH Triage (adapt. SIAMU Belgique) - Ref. SFMU V1.1<br>Usage professionnel exclusif — CHR Haute Senne</div>', unsafe_allow_html=True)
    st.markdown('<div class="signature">Ismaïl Ibn-Daïfa<br>Infirmier SIAMU — Urgences</div>', unsafe_allow_html=True)


# =============================================================================
# TABS
# =============================================================================
if st.session_state.mode == "rapide":
    tabs = st.tabs(["⚡ Tri Rapide", "🔄 Reevaluation", "📋 Historique", "🗃️ Registre Patients"])
    t_rapide, t_reeval, t_history, t_registre = tabs
    t_complet = t_scores = None
else:
    tabs = st.tabs([
        "📊 Signes Vitaux", "🔍 Anamnese", "⚖️ Triage & SBAR",
        "🧮 Scores", "🔄 Reevaluation", f"📋 Historique ({len(st.session_state.patient_history)})", "🗃️ Registre Patients"
    ])
    t_vitals, t_anamnesis, t_decision, t_scores, t_reeval, t_history, t_registre = tabs
    t_rapide = None


# Constantes par defaut
temp = fc = pas = spo2 = fr = gcs = None


# =============================================================================
# ⚡ MODE TRI RAPIDE
# =============================================================================
if st.session_state.mode == "rapide":
    with t_rapide:
        st.markdown('<div class="tri-rapide-title">TRI RAPIDE — Saisie optimisee < 2 minutes</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">1. Constantes vitales</div>', unsafe_allow_html=True)
        # v12 : Layout mobile-friendly 3x2 au lieu de 6 colonnes
        c1, c2, c3 = st.columns(3)
        temp = c1.number_input("T° (C)", 30.0, 45.0, 37.0, 0.1, key="r_temp")
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
        news2 = compute_news2(fr, spo2, supp_o2, temp, pas, fc, gcs, bpco_flag)
        news2_label, news2_class = news2_level(news2)
        st.markdown(f'NEWS2 : <span class="news2-badge {news2_class}">{news2_label}</span>', unsafe_allow_html=True)

        # v12 : Bandeaux d'alerte immediats
        render_danger_banners(news2, None, None, fc, pas, spo2, fr, gcs, temp)

        st.markdown('<div class="section-header">2. Motif en 1 clic</div>', unsafe_allow_html=True)
        MOTIFS_FLAT = [
            "Arret cardiorespiratoire", "Hypotension arterielle", "Douleur thoracique / SCA",
            "Tachycardie / tachyarythmie", "Bradycardie / bradyarythmie", "Hypertension arterielle",
            "Dyspnee / insuffisance respiratoire", "Palpitations", "Asthme / aggravation BPCO",
            "AVC / Deficit neurologique", "Alteration de conscience / Coma", "Convulsions",
            "Cephalee", "Vertiges / trouble de l'equilibre", "Confusion / desorientation",
            "Hematemese / vomissement de sang", "Rectorragie / melena", "Douleur abdominale",
            "Douleur lombaire / colique nephretique", "Retention d'urine / anurie",
            "Douleur testiculaire / torsion", "Hematurie",
            "Traumatisme avec amputation", "Traumatisme abdomen / thorax / cervical",
            "Traumatisme cranien", "Brulure", "Traumatisme bassin / hanche / femur / rachis",
            "Traumatisme membre / epaule", "Plaie", "Electrisation",
            "Agression sexuelle / sevices",
            "Accouchement imminent", "Probleme de grossesse (1er/2eme trimestre)",
            "Probleme de grossesse (3eme trimestre)", "Meno-metrorragie",
            "Idee / comportement suicidaire", "Troubles du comportement / psychiatrie",
            "Intoxication medicamenteuse", "Intoxication non medicamenteuse",
            "Fievre", "Hyperglycemie", "Hypoglycemie", "Hypothermie",
            "Coup de chaleur / insolation", "Allergie / anaphylaxie",
            "Epistaxis", "Corps etranger / brulure oculaire", "Trouble visuel / cecite",
        ]
        motif = st.selectbox("Motif", MOTIFS_FLAT, key="r_motif")

        # v12 : Prescriptions anticipees automatiques
        render_prescriptions_anticipees(motif)

        st.markdown('<div class="section-header">3. Questions cles (auto-selectionnees)</div>', unsafe_allow_html=True)
        details = {"eva": 5}
        questions = QUESTIONS_GUIDEES.get(motif, [])

        if questions:
            cols_q = st.columns(min(len(questions), 2))
            for i, (label, key, typ) in enumerate(questions):
                col = cols_q[i % len(cols_q)]
                col.markdown(f'<div class="question-guidee"><div class="question-label">{label}</div>', unsafe_allow_html=True)
                details[key] = col.checkbox(label, key=f"qg_{key}")
                col.markdown('</div>', unsafe_allow_html=True)
        else:
            st.caption("Aucune question specifique — motif general.")

        st.markdown('<div class="section-header">4. Evaluation de la douleur</div>', unsafe_allow_html=True)
        eva_score, eva_echelle, eva_interp, eva_css = echelle_douleur(age)
        details["eva"] = eva_score
        st.markdown(f'<div class="score-result {eva_css}">{eva_score}/10 ({eva_echelle})</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="score-interp">→ {eva_interp}</div>', unsafe_allow_html=True)

        niveau, justif, critere_ref = french_triage(motif, details, fc, pas, spo2, fr, gcs, temp, age, news2)
        tri_label = TRI_LABELS[niveau]
        sector    = TRI_SECTORS[niveau]
        emoji     = TRI_EMOJI[niveau]

        st.markdown('<div class="section-header">5. Resultat</div>', unsafe_allow_html=True)

        if st.session_state.last_reeval:
            since_min = (datetime.now() - st.session_state.last_reeval).total_seconds() / 60
            if since_min > TRI_DELAIS.get(niveau, 60):
                st.markdown(f'<div class="alert-danger">REEVALUATION EN RETARD : {int(since_min)} min - max {TRI_DELAIS[niveau]} min pour Tri {niveau}</div>', unsafe_allow_html=True)

        st.markdown(
            f'<div class="triage-box {TRI_BOX_CSS[niveau]}">'
            f'<div style="font-size:1.8rem;font-weight:600">{emoji} {tri_label}</div>'
            f'<div style="font-size:0.85rem;margin-top:8px;opacity:.85">NEWS2 {news2} | Douleur {eva_score}/10</div>'
            f'<div style="font-size:0.82rem;margin-top:8px;font-style:italic">{justif}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        alertes_d, alertes_w, _ = check_coherence(fc, pas, spo2, fr, gcs, temp, eva_score, motif, atcd, details, news2)
        for a in alertes_d: st.markdown(f'<div class="alert-danger">⚠ {a}</div>', unsafe_allow_html=True)
        for a in alertes_w: st.markdown(f'<div class="alert-warning">△ {a}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">Fiche de tri</div>', unsafe_allow_html=True)
        arrivee_str = st.session_state.arrival_time.strftime("%d/%m/%Y %H:%M") if st.session_state.arrival_time else datetime.now().strftime("%d/%m/%Y %H:%M")
        fiche_html = generate_fiche_tri(age, motif, niveau, tri_label, sector, temp, fc, pas, spo2, fr, gcs, news2, news2_label, eva_score, atcd, allergies, arrivee_str, details, p_nom, p_prenom)
        st.markdown(fiche_html, unsafe_allow_html=True)

        # v12 : Layout boutons mobile-friendly
        col_a, col_b = st.columns(2)
        if col_a.button("💾 Enregistrer session", use_container_width=True):
            sbar = generate_sbar(age, motif, "Tri Rapide", atcd, allergies, supp_o2,
                                  temp, fc, pas, spo2, fr, gcs, news2, news2_label,
                                  eva_score, eva_echelle, "", "", "", "",
                                  details, niveau, tri_label, justif, critere_ref, sector,
                                  nom=p_nom, prenom=p_prenom)
            st.session_state.sbar_text = sbar
            st.session_state.patient_history.append({
                "heure": datetime.now().strftime("%H:%M"),
                "age": age, "motif": motif, "cat": "Tri Rapide",
                "niveau": niveau, "eva": eva_score, "news2": news2,
                "sbar": sbar, "alertes_danger": len(alertes_d),
                "nom": p_nom, "prenom": p_prenom,
            })
            st.session_state.reeval_history = [{
                "heure": datetime.now().strftime("%H:%M"),
                "fc": fc, "pas": pas, "spo2": spo2, "fr": fr, "gcs": gcs, "temp": temp, "niveau": niveau, "news2": news2,
            }]
            st.success("Patient enregistre dans la session.")

        if col_b.button("🗃️ Sauver au registre", use_container_width=True, type="primary"):
            sbar = generate_sbar(age, motif, "Tri Rapide", atcd, allergies, supp_o2,
                                  temp, fc, pas, spo2, fr, gcs, news2, news2_label,
                                  eva_score, eva_echelle, "", "", "", "",
                                  details, niveau, tri_label, justif, critere_ref, sector,
                                  nom=p_nom, prenom=p_prenom)
            patient_record = {
                "nom": p_nom, "prenom": p_prenom, "age": age,
                "motif": motif, "cat": "Tri Rapide", "niveau": niveau,
                "tri_label": tri_label, "sector": sector,
                "eva": eva_score, "eva_echelle": eva_echelle, "news2": news2, "news2_label": news2_label,
                "temp": temp, "fc": fc, "pas": pas, "spo2": spo2, "fr": fr, "gcs": gcs,
                "atcd": atcd, "allergies": allergies, "supp_o2": supp_o2,
                "justif": justif, "critere_ref": critere_ref,
                "alertes_danger": len(alertes_d), "alertes_warning": len(alertes_w),
                "sbar": sbar, "arrivee": arrivee_str,
            }
            uid = add_patient_to_db(patient_record)
            st.success(f"✅ Patient sauvegarde dans le registre permanent (ID: {uid})")

        if st.button("🔄 Reevaluer maintenant", use_container_width=True):
            st.session_state.last_reeval = datetime.now()
            snap = {"heure": datetime.now().strftime("%H:%M"), "fc": fc, "pas": pas,
                    "spo2": spo2, "fr": fr, "gcs": gcs, "temp": temp, "niveau": niveau, "news2": news2}
            st.session_state.reeval_history.append(snap)
            st.success(f"Reevaluation enregistree a {snap['heure']} — Tri {niveau}")

        # v12 : SBAR affiche automatiquement avec bouton copier
        if st.session_state.sbar_text:
            st.markdown('<div class="section-header">Transmission SBAR</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sbar-block">{st.session_state.sbar_text}</div>', unsafe_allow_html=True)
            st.download_button(
                "📋 Telecharger SBAR (.txt)",
                data=st.session_state.sbar_text,
                file_name=f"SBAR_{datetime.now().strftime('%Y%m%d_%H%M')}_Tri{niveau}.txt",
                mime="text/plain",
                use_container_width=True,
            )

        # v12 : Disclaimer juridique
        render_disclaimer()


# =============================================================================
# MODE COMPLET — TABS
# =============================================================================
else:
    # ── TAB 1 : SIGNES VITAUX ────────────────────────────────────────────────
    with t_vitals:
        st.markdown('<div class="section-header">Constantes vitales</div>', unsafe_allow_html=True)
        # v12 : Layout 3x2 mobile-friendly
        c1, c2, c3 = st.columns(3)
        temp = c1.number_input("Temperature (C)", 30.0, 45.0, 37.0, 0.1)
        fc   = c1.number_input("FC (bpm)", 20, 220, 80)
        pas  = c2.number_input("Systolique (mmHg)", 40, 260, 120)
        spo2 = c2.number_input("SpO2 (%)", 50, 100, 98)
        fr   = c3.number_input("FR (resp/min)", 5, 60, 16)
        # v12 : GCS en number_input au lieu de select_slider pour mobile
        gcs  = c3.number_input("Glasgow (3-15)", 3, 15, 15)

        st.markdown('<div class="section-header">Alertes & Shock Index</div>', unsafe_allow_html=True)
        a1, a2, a3, a4, a5 = st.columns(5)
        a1.markdown(f"**T°** {vital_badge(temp, 36, 35, 38, 40.5, 'C')}", unsafe_allow_html=True)
        a2.markdown(f"**FC** {vital_badge(fc, 50, 40, 100, 130, '')}", unsafe_allow_html=True)
        a3.markdown(f"**PAS** {vital_badge(pas, 100, 90, 180, 220, '')}", unsafe_allow_html=True)
        a4.markdown(f"**SpO2** {vital_badge(spo2, 94, 90, 100, 100, '%')}", unsafe_allow_html=True)
        a5.markdown(f"**FR** {vital_badge(fr, 12, 8, 20, 25, '')}", unsafe_allow_html=True)
        si = round(fc / pas, 2) if pas > 0 else 0
        si_css = "vital-crit" if si >= 1.0 else ("vital-warn" if si >= 0.8 else "vital-ok")
        st.markdown(f'**Shock Index** : <span class="vital-alert {si_css}">{si}</span>{"  CHOC probable" if si >= 1 else ""}', unsafe_allow_html=True)

        bpco_flag = "BPCO" in atcd
        news2 = compute_news2(fr, spo2, supp_o2, temp, pas, fc, gcs, bpco_flag)
        news2_label, news2_class = news2_level(news2)
        st.markdown('<div class="section-header">NEWS2</div>', unsafe_allow_html=True)
        cn, ci = st.columns([1, 2])
        cn.markdown(f'<div class="news2-badge {news2_class}">{news2_label}</div>', unsafe_allow_html=True)
        interp_map = {
            "news2-low": ("Standard", "Reevaluation >= 12h."),
            "news2-med": ("Rapprochee", "Reevaluation 1h."),
            "news2-high": ("Urgente", "Evaluation medicale immediate."),
            "news2-crit": ("URGENCE ABSOLUE", "Transfert dechocage immediat."),
        }
        ti, di = interp_map[news2_class]
        ci.markdown(f"**{ti}**"); ci.markdown(di)

        # v12 : Bandeaux d'alerte immediats
        render_danger_banners(news2, None, None, fc, pas, spo2, fr, gcs, temp)

    # ── TAB 2 : ANAMNESE ─────────────────────────────────────────────────────
    with t_anamnesis:
        st.markdown('<div class="section-header">Evaluation de la douleur (adaptee a l age)</div>', unsafe_allow_html=True)
        if temp is None: temp = 37.0
        if fc   is None: fc   = 80
        if pas  is None: pas  = 120
        if spo2 is None: spo2 = 98
        if fr   is None: fr   = 16
        if gcs  is None: gcs  = 15
        eva_score, eva_echelle, eva_interp, eva_css = echelle_douleur(age)
        st.markdown(f'<div class="score-result {eva_css}">{eva_score}/10 ({eva_echelle})</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="score-interp">→ {eva_interp}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">PQRST</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            p_pqrst = st.text_input("P - Provoque / Pallie par", placeholder="Repos, effort...")
            q_pqrst = st.selectbox("Q - Qualite / Type", ["Sourd", "Etau", "Brulure", "Coup de poignard", "Electrique", "Tension", "Pesanteur", "Crampe"])
            r_pqrst = st.text_input("R - Region / Irradiation", placeholder="Bras, machoire, dos...")
        with c2:
            t_onset = st.text_input("T - Temps", placeholder="Depuis 30 min, brutal...")

        st.markdown('<div class="section-header">Motif & Questions guidees FRENCH</div>', unsafe_allow_html=True)
        MOTIFS_DICT = {
            "CARDIO-CIRCULATOIRE": ["Arret cardiorespiratoire", "Hypotension arterielle", "Douleur thoracique / SCA", "Tachycardie / tachyarythmie", "Bradycardie / bradyarythmie", "Hypertension arterielle", "Dyspnee / insuffisance respiratoire", "Palpitations"],
            "RESPIRATOIRE": ["Asthme / aggravation BPCO", "Hemoptysie", "Corps etranger voies aeriennes"],
            "NEUROLOGIE": ["AVC / Deficit neurologique", "Alteration de conscience / Coma", "Convulsions", "Cephalee", "Vertiges / trouble de l'equilibre", "Confusion / desorientation"],
            "TRAUMATOLOGIE": ["Traumatisme avec amputation", "Traumatisme abdomen / thorax / cervical", "Traumatisme cranien", "Brulure", "Traumatisme bassin / hanche / femur / rachis", "Traumatisme membre / epaule", "Plaie", "Electrisation", "Agression sexuelle / sevices"],
            "ABDOMINAL": ["Hematemese / vomissement de sang", "Rectorragie / melena", "Douleur abdominale"],
            "GENITO-URINAIRE": ["Douleur lombaire / colique nephretique", "Retention d'urine / anurie", "Douleur testiculaire / torsion", "Hematurie"],
            "GYNECO-OBSTETRIQUE": ["Accouchement imminent", "Probleme de grossesse (1er/2eme trimestre)", "Probleme de grossesse (3eme trimestre)", "Meno-metrorragie"],
            "PSYCHIATRIE / INTOXICATION": ["Idee / comportement suicidaire", "Troubles du comportement / psychiatrie", "Intoxication medicamenteuse", "Intoxication non medicamenteuse"],
            "INFECTIOLOGIE": ["Fievre"],
            "DIVERS METABOLIQUES": ["Hyperglycemie", "Hypoglycemie", "Hypothermie", "Coup de chaleur / insolation", "Allergie / anaphylaxie"],
            "ORL / OPHTALMO": ["Epistaxis", "Corps etranger / brulure oculaire", "Trouble visuel / cecite"],
        }
        cat   = st.selectbox("Categorie", list(MOTIFS_DICT.keys()))
        motif = st.selectbox("Motif de recours", MOTIFS_DICT[cat])

        score_hints = {
            "Douleur thoracique / SCA": "Score TIMI recommande (onglet Scores)",
            "Accouchement imminent": "Score Malinas recommande (onglet Scores)",
            "Brulure": "Score Brulure + Baux recommande (onglet Scores)",
            "Alteration de conscience / Coma": "Glasgow detaille recommande (onglet Scores)",
        }
        if motif in score_hints:
            st.markdown(f'<div class="alert-info">💡 {score_hints[motif]}</div>', unsafe_allow_html=True)

        # v12 : Prescriptions anticipees automatiques
        render_prescriptions_anticipees(motif)

        details = {"eva": eva_score}
        questions = QUESTIONS_GUIDEES.get(motif, [])
        if questions:
            st.markdown("**Questions discriminantes automatiques :**")
            cq1, cq2 = st.columns(2)
            for i, (label, key, typ) in enumerate(questions):
                col = cq1 if i % 2 == 0 else cq2
                details[key] = col.checkbox(label, key=f"qg_c_{key}")

        if motif == "Douleur thoracique / SCA":
            details['ecg']                    = st.selectbox("ECG", ["Normal", "Anormal typique SCA", "Anormal non typique"])
            details['douleur_type']           = st.selectbox("Type douleur", ["Atypique", "Typique persistante/intense", "Type coronaire"])
            details['comorbidites_coronaires'] = st.checkbox("Comorbidites coronaires")
        elif motif == "Dyspnee / insuffisance respiratoire":
            details['parole_ok'] = st.radio("Parler en phrases completes ?", [True, False], format_func=lambda x: "Oui" if x else "Non", horizontal=True)
            c1a, c1b = st.columns(2)
            details['orthopnee'] = c1a.checkbox("Orthopnee")
            details['tirage']    = c1b.checkbox("Tirage intercostal")
        elif motif == "AVC / Deficit neurologique":
            details['delai_heures'] = st.number_input("Delai depuis debut (heures)", 0.0, 72.0, 2.0, 0.5)
        elif motif == "Traumatisme cranien":
            c1a, c1b = st.columns(2)
            details['pdc']               = c1a.checkbox("PDC initiale")
            details['vomissements_repetes'] = c1a.checkbox("Vomissements repetes")
            details['aod_avk']           = c1b.checkbox("AOD / AVK")
            details['deficit_neuro']     = c1b.checkbox("Deficit neuro")
        elif motif == "Douleur abdominale":
            c1a, c1b = st.columns(2)
            details['defense']    = c1a.checkbox("Defense abdominale")
            details['contracture'] = c1a.checkbox("Contracture")
            details['regressive'] = c1b.checkbox("Douleur regressive")
            details['mauvaise_tolerance'] = c1b.checkbox("Mauvaise tolerance")
        elif motif == "Fievre":
            c1a, c1b = st.columns(2)
            details['confusion']          = c1a.checkbox("Confusion")
            details['purpura']            = c1a.checkbox("Purpura")
            details['mauvaise_tolerance'] = c1b.checkbox("Mauvaise tolerance")
        elif motif == "Allergie / anaphylaxie":
            details['dyspnee']            = st.checkbox("Dyspnee / oedeme larynge")
            details['mauvaise_tolerance'] = st.checkbox("Mauvaise tolerance (chute TA)")
        elif motif in ["Intoxication medicamenteuse", "Intoxication non medicamenteuse"]:
            details['mauvaise_tolerance']  = st.checkbox("Mauvaise tolerance")
            details['intention_suicidaire'] = st.checkbox("Intention suicidaire")
            details['cardiotropes']        = st.checkbox("Toxiques cardiotropes")
        elif motif == "Brulure":
            details['etendue']     = st.checkbox("Etendue > 10% SCT")
            details['main_visage'] = st.checkbox("Main / visage / perinee")
        elif motif in ["Hematemese / vomissement de sang", "Rectorragie / melena"]:
            details['abondante'] = st.checkbox("Saignement abondant")
        elif motif == "Plaie":
            details['saignement_actif'] = st.checkbox("Saignement actif")
            details['delabrant']        = st.checkbox("Plaie delabrante")
            details['main']             = st.checkbox("Localisation main")
            details['superficielle']    = st.checkbox("Superficielle")
        elif motif == "Meno-metrorragie":
            details['grossesse'] = st.checkbox("Grossesse connue / suspectee")
            details['abondante'] = st.checkbox("Saignement abondant")
        elif motif in ["Douleur lombaire / colique nephretique", "Hematurie", "Douleur testiculaire / torsion"]:
            details['intense']           = st.checkbox("Douleur intense")
            details['regressive']        = st.checkbox("Douleur regressive")
            details['suspicion_torsion'] = st.checkbox("Suspicion torsion") if "testiculaire" in motif else False
            details['abondante_active']  = st.checkbox("Saignement actif") if "Hematurie" in motif else False
        elif motif == "Hyperglycemie":
            details['glycemie']        = st.number_input("Glycemie mmol/L", 0.0, 60.0, 8.0, 0.5)
            details['cetose_elevee']   = st.checkbox("Cetose elevee")
            details['cetose_positive'] = st.checkbox("Cetose positive")
        elif motif == "Hypoglycemie":
            details['mauvaise_tolerance'] = st.checkbox("Mauvaise tolerance")
        elif motif == "Troubles du comportement / psychiatrie":
            details['agitation']      = st.checkbox("Agitation / violence")
            details['hallucinations'] = st.checkbox("Hallucinations")
        elif motif in ["Tachycardie / tachyarythmie", "Bradycardie / bradyarythmie", "Palpitations"]:
            details['mauvaise_tolerance'] = st.checkbox("Mauvaise tolerance hemodynamique")
            details['malaise']            = st.checkbox("Malaise associe")
        elif motif == "Hypertension arterielle":
            details['sf_associes'] = st.checkbox("SF associes (cephalee, trouble visuel, douleur thoracique)")
        elif motif in ["Traumatisme abdomen / thorax / cervical", "Traumatisme bassin / hanche / femur / rachis", "Traumatisme membre / epaule"]:
            details['cinetique']          = st.selectbox("Cinetique", ["Faible", "Haute"])
            details['mauvaise_tolerance'] = st.checkbox("Mauvaise tolerance")
            details['penetrant']          = st.checkbox("Penetrant") if "abdomen" in motif else False
            if "membre" in motif.lower() or "epaule" in motif.lower():
                details['impotence_totale'] = st.checkbox("Impotence totale")
                details['deformation']      = st.checkbox("Deformation")
                details['impotence_moderee'] = st.checkbox("Impotence moderee")
                details['ischemie']         = st.checkbox("Ischemie distale")
        elif motif == "Epistaxis":
            details['abondant_actif']    = st.checkbox("Abondant actif")
            details['abondant_resolutif'] = st.checkbox("Abondant resolutif")
        elif motif in ["Corps etranger / brulure oculaire", "Trouble visuel / cecite"]:
            details['chimique'] = st.checkbox("Brulure chimique")
            details['intense']  = st.checkbox("Douleur intense")
            details['brutal']   = st.checkbox("Debut brutal")
        elif motif == "Convulsions":
            details['crises_multiples'] = st.checkbox("Crises multiples / en cours")
            details['confusion_post_critique'] = st.checkbox("Confusion post-critique")
        elif motif == "Cephalee":
            details['inhabituelle'] = st.checkbox("Inhabituelle / 1er episode")
            details['brutale']      = st.checkbox("Debut brutal")
            details['fievre_assoc'] = st.checkbox("Fievre associee")
        elif motif == "Electrisation":
            details['pdc']           = st.checkbox("PDC")
            details['foudre']        = st.checkbox("Foudroiement")
            details['haute_tension'] = st.checkbox("Haute tension")

    # ── TAB 3 : TRIAGE & SBAR ────────────────────────────────────────────────
    with t_decision:
        if temp is None: temp = 37.0; fc = 80; pas = 120; spo2 = 98; fr = 16; gcs = 15
        bpco_flag = "BPCO" in atcd
        news2 = compute_news2(fr, spo2, supp_o2, temp, pas, fc, gcs, bpco_flag)
        news2_label, news2_class = news2_level(news2)
        if 'motif' not in dir(): motif = "Fievre"
        if 'details' not in dir(): details = {}
        if 'eva_score' not in dir(): eva_score = 0; eva_echelle = "EVA"
        if 'cat' not in dir(): cat = "INFECTIOLOGIE"

        niveau, justif, critere_ref = french_triage(motif, details, fc, pas, spo2, fr, gcs, temp, age, news2)
        tri_label = TRI_LABELS[niveau]; sector = TRI_SECTORS[niveau]; emoji = TRI_EMOJI[niveau]

        # v12 : Bandeaux d'alerte immediats avant le resultat
        render_danger_banners(news2, None, niveau, fc, pas, spo2, fr, gcs, temp)

        if st.session_state.last_reeval:
            since_min = (datetime.now() - st.session_state.last_reeval).total_seconds() / 60
            if since_min > TRI_DELAIS.get(niveau, 60):
                st.markdown(f'<div class="alert-danger">REEVALUATION EN RETARD : {int(since_min)} min ecoulees - max {TRI_DELAIS[niveau]} min pour Tri {niveau}</div>', unsafe_allow_html=True)

        st.markdown(
            f'<div class="triage-box {TRI_BOX_CSS[niveau]}">'
            f'<div style="font-size:1.8rem;font-weight:600">{emoji} {tri_label}</div>'
            f'<div style="font-size:0.85rem;margin-top:8px;opacity:.85">NEWS2 {news2} | Douleur {details.get("eva", 0)}/10</div>'
            f'<div style="font-size:0.82rem;margin-top:8px;font-style:italic">{justif}</div>'
            f'</div>', unsafe_allow_html=True
        )
        st.info(f"**Orientation :** {sector}")
        st.markdown(f'<div class="french-ref">Ref. FRENCH Triage — Adaptation SIAMU Belgique : {critere_ref}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">Alertes securite</div>', unsafe_allow_html=True)
        alertes_d, alertes_w, _ = check_coherence(fc, pas, spo2, fr, gcs, temp, details.get("eva", 0), motif, atcd, details, news2)
        for a in alertes_d: st.markdown(f'<div class="alert-danger">⚠ {a}</div>', unsafe_allow_html=True)
        for a in alertes_w: st.markdown(f'<div class="alert-warning">△ {a}</div>', unsafe_allow_html=True)
        if not alertes_d and not alertes_w:
            st.markdown('<div class="alert-info">✓ Aucune incoherence detectee.</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">Bilans recommandes</div>', unsafe_allow_html=True)
        bilans = suggest_bilan(motif, details, fc, pas, spo2, fr, gcs, temp, age, atcd, news2, niveau)
        if bilans:
            cols_b = st.columns(min(len(bilans), 3))
            for i, (cat_b, items) in enumerate(bilans.items()):
                col = cols_b[i % len(cols_b)]
                items_html = "".join([f'<div class="bilan-item">{it}</div>' for it in items])
                col.markdown(f'<div class="bilan-card"><div class="bilan-title">{cat_b}</div>{items_html}</div>', unsafe_allow_html=True)

        # v12 : Prescriptions anticipees dans le triage
        render_prescriptions_anticipees(motif)

        st.markdown('<div class="section-header">Fiche de tri & SBAR</div>', unsafe_allow_html=True)
        arrivee_str = st.session_state.arrival_time.strftime("%d/%m/%Y %H:%M") if st.session_state.arrival_time else datetime.now().strftime("%d/%m/%Y %H:%M")
        fiche_html = generate_fiche_tri(age, motif, niveau, tri_label, sector, temp, fc, pas, spo2, fr, gcs, news2, news2_label, details.get("eva", 0), atcd, allergies, arrivee_str, details, p_nom, p_prenom)
        st.markdown(fiche_html, unsafe_allow_html=True)

        col_sbar1, col_sbar2 = st.columns(2)

        if col_sbar1.button("Generer SBAR narratif", use_container_width=True):
            gy = st.session_state.get('gcs_y_score', 4)
            gv = st.session_state.get('gcs_v_score', 5)
            gm = st.session_state.get('gcs_m_score', 6)
            sbar = generate_sbar(age, motif, cat, atcd, allergies, supp_o2,
                                  temp, fc, pas, spo2, fr, gcs, news2, news2_label,
                                  details.get("eva", 0), eva_echelle if 'eva_echelle' in dir() else "EVA",
                                  p_pqrst if 'p_pqrst' in dir() else "", q_pqrst if 'q_pqrst' in dir() else "",
                                  r_pqrst if 'r_pqrst' in dir() else "", t_onset if 't_onset' in dir() else "",
                                  details, niveau, tri_label, justif, critere_ref, sector, gy, gv, gm,
                                  nom=p_nom, prenom=p_prenom)
            st.session_state.sbar_text = sbar
            st.session_state.patient_history.append({
                "heure": datetime.now().strftime("%H:%M"), "age": age, "motif": motif, "cat": cat,
                "niveau": niveau, "eva": details.get("eva", 0), "news2": news2, "sbar": sbar,
                "alertes_danger": len(alertes_d), "nom": p_nom, "prenom": p_prenom,
            })
            st.session_state.reeval_history = [{"heure": datetime.now().strftime("%H:%M"),
                "fc": fc, "pas": pas, "spo2": spo2, "fr": fr, "gcs": gcs, "temp": temp, "niveau": niveau, "news2": news2}]

        if col_sbar2.button("🗃️ Sauver au registre", use_container_width=True, type="primary"):
            gy = st.session_state.get('gcs_y_score', 4)
            gv = st.session_state.get('gcs_v_score', 5)
            gm = st.session_state.get('gcs_m_score', 6)
            sbar = generate_sbar(age, motif, cat, atcd, allergies, supp_o2,
                                  temp, fc, pas, spo2, fr, gcs, news2, news2_label,
                                  details.get("eva", 0), eva_echelle if 'eva_echelle' in dir() else "EVA",
                                  p_pqrst if 'p_pqrst' in dir() else "", q_pqrst if 'q_pqrst' in dir() else "",
                                  r_pqrst if 'r_pqrst' in dir() else "", t_onset if 't_onset' in dir() else "",
                                  details, niveau, tri_label, justif, critere_ref, sector, gy, gv, gm,
                                  nom=p_nom, prenom=p_prenom)
            patient_record = {
                "nom": p_nom, "prenom": p_prenom, "age": age,
                "motif": motif, "cat": cat, "niveau": niveau,
                "tri_label": tri_label, "sector": sector,
                "eva": details.get("eva", 0), "eva_echelle": eva_echelle if 'eva_echelle' in dir() else "EVA",
                "news2": news2, "news2_label": news2_label,
                "temp": temp, "fc": fc, "pas": pas, "spo2": spo2, "fr": fr, "gcs": gcs,
                "atcd": atcd, "allergies": allergies, "supp_o2": supp_o2,
                "justif": justif, "critere_ref": critere_ref,
                "alertes_danger": len(alertes_d), "alertes_warning": len(alertes_w),
                "sbar": sbar, "arrivee": arrivee_str,
            }
            uid = add_patient_to_db(patient_record)
            st.success(f"✅ Patient sauvegarde dans le registre permanent (ID: {uid})")

        if st.session_state.sbar_text:
            st.markdown(f'<div class="sbar-block">{st.session_state.sbar_text}</div>', unsafe_allow_html=True)
            st.download_button("📋 Telecharger SBAR (.txt)", data=st.session_state.sbar_text,
                file_name=f"SBAR_{datetime.now().strftime('%Y%m%d_%H%M')}_Tri{niveau}.txt",
                mime="text/plain", use_container_width=True)

        # v12 : Disclaimer juridique
        render_disclaimer()

    # ── TAB 4 : SCORES ───────────────────────────────────────────────────────
    with t_scores:
        def score_badge_custom(val, css):
            return f'<div class="score-result {css}">{val}</div>'

        st.markdown("### Scores cliniques valides")

        with st.expander("Score TIMI — SCA NSTEMI", expanded=True):
            st.markdown('<div class="score-title">TIMI Risk Score (Antman 2000)</div>', unsafe_allow_html=True)
            ca, cb = st.columns(2)
            t1 = ca.checkbox("Age >= 65 ans", key="timi1"); t2 = ca.checkbox(">= 3 FdR coronariens", key="timi2")
            t3 = ca.checkbox("Stenose connue >= 50%", key="timi3"); t4 = ca.checkbox("Deviation ST ECG", key="timi4")
            t5 = cb.checkbox(">= 2 angor/24h", key="timi5"); t6 = cb.checkbox("Troponine +", key="timi6")
            t7 = cb.checkbox("Aspirine < 7j", key="timi7")
            timi_score = sum([t1, t2, t3, t4, t5, t6, t7])
            if timi_score <= 2: tc, ti = "score-low", "Risque 14j ~5% — surveillance + bilan"
            elif timi_score <= 4: tc, ti = "score-med", "Risque 14j ~13-20% — HBPM + coronarographie rapide"
            else: tc, ti = "score-high", "Risque 14j ~26-41% — coronarographie urgente < 2h"
            st.markdown(score_badge_custom(f"{timi_score}/7", tc), unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">→ {ti}</div>', unsafe_allow_html=True)

        with st.expander("Score de Silverman — Nouveau-ne", expanded=False):
            st.markdown('<div class="score-title">Silverman-Andersen (nouveau-ne)</div>', unsafe_allow_html=True)
            sil_items = {
                "Balancement thoraco-abdominal": ["0 - Synchrone", "1 - Asynchrone leger", "2 - Asynchrone marque"],
                "Tirage intercostal": ["0 - Absent", "1 - Discret", "2 - Important"],
                "Creusement xiphoidien": ["0 - Absent", "1 - Discret", "2 - Important"],
                "Battement ailes du nez": ["0 - Absent", "1 - Discret", "2 - Important"],
                "Geignement expiratoire": ["0 - Absent", "1 - Audible stethoscope", "2 - Audible a l'oreille"],
            }
            sv = {}; ca2, cb2 = st.columns(2)
            for i, (lbl, opts) in enumerate(sil_items.items()):
                col = ca2 if i < 3 else cb2
                v = col.selectbox(lbl, opts, key=f"sil_{i}"); sv[lbl] = int(v[0])
            sil_score = sum(sv.values())
            if sil_score == 0: sc, si_txt = "score-info", "Pas de detresse."
            elif sil_score <= 3: sc, si_txt = "score-low", "Detresse legere."
            elif sil_score <= 6: sc, si_txt = "score-med", "Detresse moderee — pediatre urgent."
            else: sc, si_txt = "score-high", "Detresse severe — reanimation neonatale (NIC/NICU)."
            st.markdown(score_badge_custom(f"{sil_score}/10", sc), unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">→ {si_txt}</div>', unsafe_allow_html=True)

            # v12 : Bandeau Silverman si danger
            if sil_score >= 5:
                render_danger_banners(0, sil_score, None, 80, 120, 98, 16, 15, 37)

        with st.expander("Glasgow detaille (Y/V/M)", expanded=False):
            st.markdown('<div class="score-title">Glasgow Coma Scale</div>', unsafe_allow_html=True)
            ca3, cb3, cc3 = st.columns(3)
            with ca3:
                st.markdown("**Yeux (Y)**")
                ye = st.radio("Y", ["4 - Spontanee", "3 - Au bruit", "2 - A la douleur", "1 - Aucune"], key="gcs_y"); y_s = int(ye[0])
            with cb3:
                st.markdown("**Verbale (V)**")
                ve = st.radio("V", ["5 - Orientee", "4 - Confuse", "3 - Mots inappropries", "2 - Sons", "1 - Aucune"], key="gcs_v"); v_s = int(ve[0])
            with cc3:
                st.markdown("**Motrice (M)**")
                me = st.radio("M", ["6 - Obeit", "5 - Localise", "4 - Retrait", "3 - Flexion", "2 - Extension", "1 - Aucune"], key="gcs_m"); m_s = int(me[0])
            gcs_calc = y_s + v_s + m_s
            st.session_state['gcs_y_score'] = y_s; st.session_state['gcs_v_score'] = v_s; st.session_state['gcs_m_score'] = m_s
            if gcs_calc == 15: gc, gi = "score-info", "Conscient."
            elif gcs_calc >= 13: gc, gi = "score-low", "Alteration legere."
            elif gcs_calc >= 9: gc, gi = "score-med", "Alteration moderee."
            else: gc, gi = "score-high", "COMA — protection VA urgente."
            st.markdown(score_badge_custom(f"GCS {gcs_calc}/15 (Y{y_s}V{v_s}M{m_s})", gc), unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">→ {gi}</div>', unsafe_allow_html=True)
            if abs(gcs_calc - gcs) > 1 if gcs else False:
                st.markdown(f'<div class="alert-warning">△ GCS calcule {gcs_calc} != GCS Signes Vitaux {gcs} — mettre a jour</div>', unsafe_allow_html=True)

        with st.expander("Score de Malinas — Accouchement imminent", expanded=False):
            st.markdown('<div class="score-title">Score de Malinas</div>', unsafe_allow_html=True)
            ca4, cb4 = st.columns(2)
            with ca4:
                par = ca4.selectbox("Parite", ["0 - Primipare", "1 - Multipare"], key="mal_par")
                trav = ca4.selectbox("Duree travail", ["0 - < 1h", "1 - 1 a 3h", "2 - > 3h"], key="mal_trav")
                cont = ca4.selectbox("Duree contractions", ["0 - < 1min", "1 - 1min", "2 - > 1min"], key="mal_cont")
            with cb4:
                inter = cb4.selectbox("Intervalle contractions", ["0 - > 5min", "1 - 3 a 5min", "2 - < 3min"], key="mal_int")
                poche = cb4.selectbox("Poche des eaux", ["0 - Intacte", "1 - Rompue"], key="mal_poche")
                push = cb4.selectbox("Envie de pousser", ["0 - Absente", "1 - Presente"], key="mal_pousser")
            mal_score = int(par[0]) + int(trav[0]) + int(cont[0]) + int(inter[0]) + int(poche[0]) + int(push[0])
            if mal_score <= 5: mc, mi = "score-low", "Transport possible."
            elif mal_score <= 7: mc, mi = "score-med", "Transport rapide SMUR/PIT."
            elif mal_score <= 9: mc, mi = "score-med", "Preparer accouchement sur place."
            else: mc, mi = "score-high", "NE PAS TRANSPORTER — accouchement imminent."
            st.markdown(score_badge_custom(f"{mal_score}/10", mc), unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">→ {mi}</div>', unsafe_allow_html=True)
            if mal_score >= 8:
                st.markdown('<div class="alert-danger">NE PAS TRANSPORTER — Activer protocole accouchement inopine</div>', unsafe_allow_html=True)

        with st.expander("Score Brulure — Regle des 9 + Baux", expanded=False):
            st.markdown('<div class="score-title">Regle des 9 de Wallace + Indice de Baux</div>', unsafe_allow_html=True)
            age_br = st.number_input("Age patient", 0, 120, age, key="br_age")
            ca5, cb5, cc5 = st.columns(3)
            with ca5:
                bt = st.number_input("Tete & cou %", 0, 9, 0, key="br_t"); bta = st.number_input("Thorax ant %", 0, 9, 0, key="br_ta")
                btp = st.number_input("Thorax post %", 0, 9, 0, key="br_tp"); bab = st.number_input("Abdomen %", 0, 9, 0, key="br_ab")
            with cb5:
                bmsd = st.number_input("MS droit %", 0, 9, 0, key="br_msd"); bmsg = st.number_input("MS gauche %", 0, 9, 0, key="br_msg")
                bmid = st.number_input("MI droit %", 0, 18, 0, key="br_mid"); bmig = st.number_input("MI gauche %", 0, 18, 0, key="br_mig")
            with cc5:
                bper = st.number_input("Perinee %", 0, 1, 0, key="br_per")
                bprof = st.selectbox("Profondeur", ["Superficielle", "Intermediaire", "Profonde"], key="br_prof")
                binh = st.checkbox("Inhalation suspectee", key="br_inh")
            scb = min(bt + bta + btp + bab + bmsd + bmsg + bmid + bmig + bper, 100)
            baux = age_br + scb; baux_r = age_br + int(1.5 * scb) if binh else baux
            profonde = "Profonde" in bprof
            if scb >= 50 or baux >= 100: brc, brs = "score-high", "CRITIQUE — Centre des Grands Brules + reanimation."
            elif scb >= 20 or (profonde and scb >= 10) or binh: brc, brs = "score-high", "GRAVE — Centre des Grands Brules."
            elif scb >= 10 or profonde: brc, brs = "score-med", "MODEREE — Hospitalisation + chirurgien plasticien."
            elif scb >= 1: brc, brs = "score-low", "LEGERE — Ambulatoire possible."
            else: brc, brs = "score-info", "Aucune surface renseignee."
            cr1, cr2 = st.columns(2)
            cr1.markdown(score_badge_custom(f"SCB {scb}%", brc), unsafe_allow_html=True)
            cr2.markdown(score_badge_custom(f"Baux {baux}", brc), unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">→ {brs}</div>', unsafe_allow_html=True)
            if binh: st.markdown(f'<div class="alert-warning">Baux revise (inhalation) : {baux_r}</div>', unsafe_allow_html=True)
            if scb > 0:
                pds = st.number_input("Poids (kg)", 10, 200, 70, key="br_pds")
                pk = 4 * pds * scb
                st.info(f"Parkland : {pk} mL RL / 24h | {pk // 2} mL les 8 premieres heures | {pk // 2} mL les 16h suivantes")

        with st.expander("Score BATT — Blast And Trauma Triage", expanded=False):
            st.markdown('<div class="score-title">BATT — Victimes explosion / traumatismes multiples</div>', unsafe_allow_html=True)
            ca6, cb6 = st.columns(2)
            with ca6:
                bg = st.number_input("GCS", 3, 15, 15, key="batt_gcs")
                bp = st.number_input("PAS", 0, 300, 120, key="batt_pas")
                bfr = st.number_input("FR", 0, 60, 16, key="batt_fr")
                bs = st.number_input("SpO2", 50, 100, 98, key="batt_spo2")
            with cb6:
                ba = st.checkbox("Amputation", key="batt_amp"); bth = st.checkbox("Thorax ouvert", key="batt_thor")
                bad = st.checkbox("Evisceration", key="batt_abdo"); bcr = st.checkbox("TC ouvert", key="batt_crane")
                bcu = st.checkbox("Crush syndrome", key="batt_crush"); bbu = st.checkbox("Brulures > 60%", key="batt_burns")
                bai = st.checkbox("Obstruction VA", key="batt_airways")
            bok = (bg >= 10 and bp >= 90 and 10 <= bfr <= 29 and bs >= 90)
            blet = bcr or bbu; nbl = sum([ba, bth, bad, bcu, bai])
            if blet and not bok: bcat, bcc, bint = "T4 DEPASSE", "score-high", "Soins palliatifs en catastrophe."
            elif not bok and nbl >= 2: bcat, bcc, bint = "T1 EXTREME URGENCE", "score-high", "Dechocage immediat."
            elif not bok or nbl >= 1: bcat, bcc, bint = "T1 URGENCE ABSOLUE", "score-high", "Dechocage immediat."
            elif bok and nbl == 0 and not blet: bcat, bcc, bint = "T3 DIFFERE", "score-low", "Stable — surveillance."
            else: bcat, bcc, bint = "T2 URGENCE RELATIVE", "score-med", "Reevaluation frequente."
            st.markdown(score_badge_custom(bcat, bcc), unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">→ {bint}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">Recapitulatif</div>', unsafe_allow_html=True)
        r1, r2, r3 = st.columns(3)
        r1.metric("TIMI", f"{timi_score}/7"); r2.metric("Silverman", f"{sil_score}/10"); r3.metric("GCS calcule", f"{gcs_calc}/15")
        r1.metric("Malinas", f"{mal_score}/10"); r2.metric("SCB", f"{scb}%"); r3.metric("Baux", f"{baux}")


# =============================================================================
# REEVALUATION STRUCTUREE (communes aux deux modes)
# =============================================================================
reeval_tab = t_reeval

with reeval_tab:
    st.markdown("### Reevaluations structurees")
    st.caption("Chaque reevaluation est comparee a la precedente. Tendance automatique.")

    st.markdown('<div class="section-header">Nouvelle reevaluation</div>', unsafe_allow_html=True)
    # v12 : Layout 3x2 mobile-friendly
    cr1, cr2, cr3 = st.columns(3)
    re_temp = cr1.number_input("T° (C)", 30.0, 45.0, 37.0, 0.1, key="re_temp")
    re_fc   = cr1.number_input("FC (bpm)", 20, 220, 80, key="re_fc")
    re_pas  = cr2.number_input("PAS (mmHg)", 40, 260, 120, key="re_pas")
    re_spo2 = cr2.number_input("SpO2 (%)", 50, 100, 98, key="re_spo2")
    re_fr   = cr3.number_input("FR (/min)", 5, 60, 16, key="re_fr")
    re_gcs  = cr3.number_input("GCS", 3, 15, 15, key="re_gcs")

    re_news2 = compute_news2(re_fr, re_spo2, supp_o2, re_temp, re_pas, re_fc, re_gcs, "BPCO" in atcd)
    re_label, re_css = news2_level(re_news2)

    re_motif = "Fievre"
    if st.session_state.patient_history:
        re_motif = st.session_state.patient_history[-1].get("motif", "Fievre")
    re_niveau, re_justif, re_ref = french_triage(re_motif, {}, re_fc, re_pas, re_spo2, re_fr, re_gcs, re_temp, age, re_news2)

    col_re1, col_re2 = st.columns(2)
    col_re1.markdown(f'<div class="news2-badge {re_css}">{re_label}</div>', unsafe_allow_html=True)
    col_re2.info(f"Triage recalcule : **{TRI_EMOJI[re_niveau]} {TRI_LABELS[re_niveau]}**")

    # v12 : Bandeaux d'alerte en reevaluation
    render_danger_banners(re_news2, None, re_niveau, re_fc, re_pas, re_spo2, re_fr, re_gcs, re_temp)

    if st.button("Enregistrer cette reevaluation", use_container_width=True):
        snap = {
            "heure": datetime.now().strftime("%H:%M"),
            "fc": re_fc, "pas": re_pas, "spo2": re_spo2,
            "fr": re_fr, "gcs": re_gcs, "temp": re_temp,
            "niveau": re_niveau, "news2": re_news2,
        }
        st.session_state.reeval_history.append(snap)
        st.session_state.last_reeval = datetime.now()
        st.success(f"Reevaluation enregistree a {snap['heure']} — Tri {re_niveau}")

    st.markdown('<div class="section-header">Historique des reevaluations</div>', unsafe_allow_html=True)

    if len(st.session_state.reeval_history) < 1:
        st.info("Aucune reevaluation enregistree. Enregistrez d'abord un patient.")
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
            no = niveau_order.get(snap['niveau'], 3); np_ = niveau_order.get(prev['niveau'], 3)
            if no > np_:      row_css, tendance = "reeval-better", "AMELIORATION"
            elif no < np_:    row_css, tendance = "reeval-worse", "AGGRAVATION"
            else:             row_css, tendance = "reeval-same", "STABLE"

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
            st.markdown(f"**Bilan global :** {len(history)} reevaluations | "
                        f"NEWS2 initial {first.get('news2', '?')} → {last.get('news2', '?')} | "
                        f"Tri {first['niveau']} → {last['niveau']}")

        if st.button("Effacer reevaluations"):
            st.session_state.reeval_history = []
            st.rerun()


# =============================================================================
# HISTORIQUE (session)
# =============================================================================
with t_history:
    if not st.session_state.patient_history:
        st.info("Aucun patient enregistre dans cette session.")
    else:
        st.markdown(f"**{len(st.session_state.patient_history)} patient(s) cette session**")
        for i, pat in enumerate(reversed(st.session_state.patient_history), 1):
            css = TRI_HIST_CSS.get(pat['niveau'], 'hist-4')
            em  = TRI_EMOJI.get(pat['niveau'], '')
            tag = " ⚠ ALERTES" if pat.get('alertes_danger', 0) > 0 else ""
            nom_display = f"{pat.get('nom', '').upper()} {pat.get('prenom', '')}" if pat.get('nom') or pat.get('prenom') else ""
            st.markdown(
                f'<div class="hist-row {css}">'
                f'<b>{pat["heure"]}</b> | {nom_display + " | " if nom_display else ""}{pat["age"]} ans | <b>{pat["motif"]}</b> | '
                f'EVA {pat["eva"]}/10 | NEWS2 {pat["news2"]} | {em} Tri {pat["niveau"]}{tag}'
                f'</div>', unsafe_allow_html=True
            )
            with st.expander(f"SBAR — Patient #{len(st.session_state.patient_history) - i + 1}"):
                st.markdown(f'<div class="sbar-block">{pat["sbar"]}</div>', unsafe_allow_html=True)
                st.download_button("📋 Telecharger SBAR", data=pat["sbar"],
                    file_name=f"SBAR_{pat['heure'].replace(':', 'h')}_Tri{pat['niveau']}.txt",
                    mime="text/plain", key=f"dl_{i}")
        if st.button("Effacer l'historique"):
            st.session_state.patient_history = []
            st.rerun()


# =============================================================================
# 🗃️ REGISTRE PATIENTS — STOCKAGE PERSISTANT
# =============================================================================
with t_registre:
    st.markdown("### 🗃️ Registre Patients — Donnees persistantes")
    st.caption("Les patients sauvegardes ici sont conserves entre les sessions (fichier JSON local).")

    db = load_patient_db()

    # --- Statistiques ---
    if db:
        niveaux_count = {}
        for p in db:
            n = p.get("niveau", "?")
            niveaux_count[n] = niveaux_count.get(n, 0) + 1
        today_count = sum(1 for p in db if p.get("saved_date") == datetime.now().strftime("%Y-%m-%d"))

        st.markdown('<div class="reg-stats">', unsafe_allow_html=True)
        cols_stat = st.columns(5)
        cols_stat[0].markdown(f'<div class="reg-stat-card"><div class="reg-stat-num">{len(db)}</div><div class="reg-stat-label">Total patients</div></div>', unsafe_allow_html=True)
        cols_stat[1].markdown(f'<div class="reg-stat-card"><div class="reg-stat-num">{today_count}</div><div class="reg-stat-label">Aujourd\'hui</div></div>', unsafe_allow_html=True)
        urgent_count = sum(v for k, v in niveaux_count.items() if k in ["M", "1", "2"])
        cols_stat[2].markdown(f'<div class="reg-stat-card"><div class="reg-stat-num" style="color:#f87171">{urgent_count}</div><div class="reg-stat-label">Tri M/1/2</div></div>', unsafe_allow_html=True)
        moderate_count = sum(v for k, v in niveaux_count.items() if k in ["3A", "3B"])
        cols_stat[3].markdown(f'<div class="reg-stat-card"><div class="reg-stat-num" style="color:#fbbf24">{moderate_count}</div><div class="reg-stat-label">Tri 3A/3B</div></div>', unsafe_allow_html=True)
        low_count = sum(v for k, v in niveaux_count.items() if k in ["4", "5"])
        cols_stat[4].markdown(f'<div class="reg-stat-card"><div class="reg-stat-num" style="color:#4ade80">{low_count}</div><div class="reg-stat-label">Tri 4/5</div></div>', unsafe_allow_html=True)

    # --- Recherche & filtres ---
    st.markdown('<div class="section-header">Recherche & Filtres</div>', unsafe_allow_html=True)
    col_search, col_filter, col_actions = st.columns([3, 2, 2])
    search_query = col_search.text_input("🔍 Rechercher", placeholder="Nom, motif, niveau, date...", key="reg_search", label_visibility="collapsed")
    filter_niveau = col_filter.selectbox("Filtrer par niveau", ["Tous", "M", "1", "2", "3A", "3B", "4", "5"], key="reg_filter")

    if search_query:
        filtered_db = search_patients(search_query)
    else:
        filtered_db = db

    if filter_niveau != "Tous":
        filtered_db = [p for p in filtered_db if p.get("niveau") == filter_niveau]

    if col_actions.button("📥 Exporter tout (JSON)", use_container_width=True) and db:
        export_data = json.dumps(db, ensure_ascii=False, indent=2)
        st.download_button(
            "Telecharger registre complet",
            data=export_data,
            file_name=f"registre_patients_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            key="export_json"
        )

    # --- Liste des patients ---
    st.markdown(f'<div class="section-header">Patients ({len(filtered_db)} resultat{"s" if len(filtered_db) != 1 else ""})</div>', unsafe_allow_html=True)

    if not filtered_db:
        st.markdown(
            '<div class="reg-empty">'
            '<div class="reg-empty-icon">🗃️</div>'
            '<div>Aucun patient dans le registre.<br>Utilisez le bouton "Sauver au registre" apres un triage.</div>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        for idx, pat in enumerate(filtered_db):
            uid = pat.get("uid", "?")
            niv = pat.get("niveau", "?")
            nom_display = f"{pat.get('nom', '').upper()} {pat.get('prenom', '')}" if pat.get('nom') or pat.get('prenom') else "ANONYME"
            em = TRI_EMOJI.get(niv, "")

            st.markdown(
                f'<div class="reg-card">'
                f'<div class="reg-card-header">'
                f'  <div class="reg-card-title">{nom_display} — {pat.get("age", "?")} ans</div>'
                f'  <div class="reg-card-date">ID {uid} | {pat.get("saved_at", "")}</div>'
                f'</div>'
                f'<div style="margin-bottom:8px;">'
                f'  <span class="reg-badge reg-badge-{niv}">{em} Tri {niv}</span>'
                f'  <span style="font-size:0.82rem;color:#94a3b8;">{pat.get("motif", "")} ({pat.get("cat", "")})</span>'
                f'</div>'
                f'<div class="reg-card-body">'
                f'  <div class="reg-field"><span class="reg-field-label">T°</span><span class="reg-field-value">{pat.get("temp", "")} C</span></div>'
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
                with st.expander(f"📄 SBAR complet — {nom_display}"):
                    sbar_txt = pat.get("sbar", "Pas de SBAR genere.")
                    st.markdown(f'<div class="sbar-block">{sbar_txt}</div>', unsafe_allow_html=True)
                    st.download_button(
                        "📋 Telecharger SBAR",
                        data=sbar_txt,
                        file_name=f"SBAR_{uid}_{niv}.txt",
                        mime="text/plain",
                        key=f"dl_reg_{uid}_{idx}"
                    )

            if col_d3.button(f"🗑️ Supprimer", key=f"del_{uid}_{idx}", use_container_width=True):
                st.session_state.confirm_delete = uid

            if st.session_state.confirm_delete == uid:
                st.warning(f"⚠️ Confirmer la suppression de **{nom_display}** (ID: {uid}) ?")
                col_conf1, col_conf2, _ = st.columns([1, 1, 3])
                if col_conf1.button("✅ Oui, supprimer", key=f"conf_del_{uid}_{idx}", type="primary"):
                    delete_patient_from_db(uid)
                    st.session_state.confirm_delete = None
                    st.success(f"Patient {uid} supprime du registre.")
                    st.rerun()
                if col_conf2.button("❌ Annuler", key=f"cancel_del_{uid}_{idx}"):
                    st.session_state.confirm_delete = None
                    st.rerun()

    # --- Purge totale ---
    if db:
        st.markdown("---")
        st.markdown('<div class="section-header">Administration</div>', unsafe_allow_html=True)
        with st.expander("⚠️ Zone dangereuse — Purge complete"):
            st.warning("Cette action supprimera **tous** les patients du registre de maniere irreversible.")
            if st.button("🗑️ PURGER TOUT LE REGISTRE", type="primary", key="purge_all"):
                save_patient_db([])
                st.session_state.confirm_delete = None
                st.success("Registre vide.")
                st.rerun()
                