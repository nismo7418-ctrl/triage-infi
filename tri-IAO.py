import streamlit as st
from datetime import datetime

# --- CONFIGURATION ------------------------------------------------------------
st.set_page_config(
    page_title="IAO Expert Pro v11.0",
    page_icon="⚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

/* ── v11 NOUVEAUTES ── */
/* Mode tri rapide */
.tri-rapide-box{background:#020617;border:2px solid #38bdf8;border-radius:14px;padding:24px;margin-bottom:16px;}
.tri-rapide-title{font-family:'IBM Plex Mono',monospace;color:#38bdf8;font-size:0.8rem;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:12px;}
.question-guidee{background:#0f172a;border:1px solid #1e3a5f;border-left:4px solid #38bdf8;border-radius:8px;padding:12px 16px;margin:6px 0;font-size:0.9rem;}
.question-label{font-size:0.72rem;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px;}

/* Douleur adaptee */
.douleur-badge{display:inline-flex;align-items:center;justify-content:center;
width:52px;height:52px;border-radius:50%;font-size:1.3rem;font-weight:700;
font-family:'IBM Plex Mono',monospace;cursor:pointer;border:2px solid transparent;transition:all 0.15s;}
.douleur-0{background:#052e16;color:#86efac;}
.douleur-1{background:#083344;color:#67e8f9;}
.douleur-2{background:#0c1a2e;color:#93c5fd;}
.douleur-3{background:#1c1917;color:#d6d3d1;}
.douleur-4{background:#1c1917;color:#fbbf24;}
.douleur-5{background:#422006;color:#fb923c;}
.douleur-6{background:#431407;color:#f97316;}
.douleur-7{background:#450a0a;color:#f87171;}
.douleur-8{background:#4c0519;color:#fb7185;}
.douleur-9{background:#4c0519;color:#f43f5e;}
.douleur-10{background:#450a0a;color:#fca5a5;animation:pulse 0.8s infinite;}

/* Fiche de tri */
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

/* Reevaluation */
.reeval-row{background:#0f172a;border:1px solid #1e3a5f;border-radius:8px;padding:10px 14px;margin-bottom:6px;font-size:0.83rem;}
.reeval-better{border-left:4px solid #22c55e;}
.reeval-same{border-left:4px solid #3b82f6;}
.reeval-worse{border-left:4px solid #ef4444;}
.trend-up{color:#4ade80;}
.trend-down{color:#f87171;}
.trend-same{color:#94a3b8;}

.legal-text{font-size:0.72rem;color:#475569;font-style:italic;margin-top:8px;}
.signature{color:#38bdf8;font-weight:600;font-size:0.85rem;border-top:1px solid #1e3a5f;padding-top:10px;margin-top:12px;}
</style>
""", unsafe_allow_html=True)


# --- SESSION STATE ------------------------------------------------------------
defaults = {
    'patient_history': [],
    'arrival_time': None,
    'sbar_text': "",
    'last_reeval': None,
    'reeval_history': [],      # liste de snapshots {heure, fc, pas, spo2, fr, gcs, temp, niveau}
    'mode': 'complet',         # 'rapide' ou 'complet'
    'gcs_y_score': 4,
    'gcs_v_score': 5,
    'gcs_m_score': 6,
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
    "M":"SAUV - Reanimation immediate","1":"SAUV - Prise en charge immediate",
    "2":"Secteur Lourd - Medecin < 20 min","3A":"Secteur Lourd - Medecin < 30 min",
    "3B":"Secteur Intermediaire - Medecin < 1h","4":"Secteur Ambulatoire - Medecin < 2h",
    "5":"Zone d'attente - Consultation / reorientation",
}
TRI_DELAIS = {"M":5,"1":5,"2":15,"3A":30,"3B":60,"4":120,"5":999}
TRI_BOX_CSS  = {"M":"box-M","1":"box-1","2":"box-2","3A":"box-3A","3B":"box-3B","4":"box-4","5":"box-5"}
TRI_HIST_CSS = {"M":"hist-M","1":"hist-1","2":"hist-2","3A":"hist-3A","3B":"hist-3B","4":"hist-4","5":"hist-5"}
TRI_EMOJI    = {"M":"🟣","1":"🔴","2":"🟠","3A":"🟡","3B":"🟡","4":"🟢","5":"🔵"}

# Questions discriminantes par motif (Point 1 - questions guidees en 1 clic)
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
# MOTEUR FRENCH TRIAGE SFMU V1.1
# =============================================================================
def french_triage(motif, details, fc, pas, spo2, fr, gcs, temp, age, news2_score):
    if news2_score >= 9:
        return "M","NEWS2 >= 9 : engagement vital immediat.","NEWS2 Tri M"
    # Cardio
    if motif == "Arret cardiorespiratoire": return "M","ACR.","FRENCH Tri M"
    if motif == "Hypotension arterielle":
        if pas <= 70: return "1",f"PAS <= 70 ({pas}).","FRENCH Tri 1"
        if pas <= 90 or (pas <= 100 and fc > 100): return "2","PAS basse ou choc debutant.","FRENCH Tri 2"
        if 90 < pas <= 100: return "3B","PAS limite.","FRENCH Tri 3B"
        return "4","TA dans les normes.","FRENCH Tri 4"
    if motif == "Douleur thoracique / SCA":
        ecg = details.get("ecg","Normal")
        dt  = details.get("douleur_type","Atypique")
        co  = details.get("comorbidites_coronaires",False)
        dtyp= details.get("douleur_typique",False)
        if ecg=="Anormal typique SCA" or details.get("ecg_anormal",False): return "1","ECG typique SCA.","FRENCH Tri 1"
        if ecg=="Anormal non typique" or dt=="Typique persistante/intense" or (dtyp and details.get("duree_longue",False)):
            return "2","Douleur typique persistante ou ECG douteux.","FRENCH Tri 2"
        if co: return "3A","Comorbidites coronaires.","FRENCH Tri 3A"
        if dtyp or dt=="Type coronaire": return "3B","Douleur type coronaire.","FRENCH Tri 3B"
        return "4","ECG normal, douleur atypique.","FRENCH Tri 4"
    if motif == "Tachycardie / tachyarythmie":
        if fc >= 180: return "1",f"FC >= 180.","FRENCH Tri 1"
        if fc >= 130: return "2",f"FC >= 130.","FRENCH Tri 2"
        if fc > 110:  return "3B",f"FC > 110.","FRENCH Tri 3B"
        return "4","Episode resolutif.","FRENCH Tri 4"
    if motif == "Bradycardie / bradyarythmie":
        mt = details.get("mauvaise_tolerance",False)
        if fc <= 40: return "1",f"FC <= 40.","FRENCH Tri 1"
        if fc <= 50 and mt: return "2","FC 40-50 + mauvaise tolerance.","FRENCH Tri 2"
        if fc <= 50: return "3B","FC 40-50 bien toleree.","FRENCH Tri 3B"
        return "4","Bradycardie toleree.","FRENCH Tri 4"
    if motif == "Hypertension arterielle":
        sf = details.get("sf_associes",False)
        if pas >= 220 or (pas >= 180 and sf): return "2",f"PAS >= 220 ou >= 180 + SF.","FRENCH Tri 2"
        if pas >= 180: return "3B",f"PAS >= 180 sans SF.","FRENCH Tri 3B"
        return "4","PAS < 180.","FRENCH Tri 4"
    if motif == "Dyspnee / insuffisance respiratoire":
        if fr >= 40 or spo2 < 86: return "1","Detresse respiratoire.","FRENCH Tri 1"
        if not details.get("parole_ok",True) or details.get("tirage") or details.get("orthopnee") or (30<=fr<40) or (86<=spo2<=90):
            return "2","Dyspnee a la parole / tirage.","FRENCH Tri 2"
        return "3B","Dyspnee moderee stable.","FRENCH Tri 3B"
    if motif == "Palpitations":
        if fc >= 180: return "2","FC >= 180.","FRENCH Tri 2"
        if fc >= 130: return "2","FC >= 130.","FRENCH Tri 2"
        if details.get("malaise") or fc > 110: return "3B","Malaise / FC > 110.","FRENCH Tri 3B"
        return "4","Palpitations isolees.","FRENCH Tri 4"
    if motif == "Asthme / aggravation BPCO":
        dep = details.get("dep",999)
        if fr >= 40 or spo2 < 86: return "1","Detresse respiratoire.","FRENCH Tri 1"
        if dep <= 200 or not details.get("parole_ok",True) or details.get("tirage"): return "2","DEP <= 200 / dyspnee parole.","FRENCH Tri 2"
        if dep >= 300: return "4","DEP >= 300.","FRENCH Tri 4"
        return "3B","Asthme modere.","FRENCH Tri 3B"
    if motif == "AVC / Deficit neurologique":
        dh = details.get("delai_heures",999)
        ok = details.get("delai_ok",False)
        if dh <= 4.5 or ok: return "1","Deficit < 4h30 - filiere AVC.","FRENCH Tri 1"
        if dh >= 24: return "3B","Deficit > 24h.","FRENCH Tri 3B"
        return "2","Deficit neurologique aigu.","FRENCH Tri 2"
    if motif == "Alteration de conscience / Coma":
        if gcs <= 8:  return "1",f"GCS {gcs} - coma.","FRENCH Tri 1"
        if gcs <= 13: return "2",f"GCS {gcs} - alteration moderee.","FRENCH Tri 2"
        return "3B","Alteration legere.","FRENCH Tri 3B"
    if motif == "Convulsions":
        if details.get("crises_multiples") or details.get("en_cours") or details.get("confusion_post_critique") or temp >= 38.5:
            return "2","Crise en cours / multiple / confusion.","FRENCH Tri 2"
        return "3B","Recuperation complete.","FRENCH Tri 3B"
    if motif == "Cephalee":
        if details.get("inhabituelle") or details.get("brutale") or details.get("fievre_assoc") or temp >= 38.5:
            return "2","Cephalee inhabituelle / brutale / febrile.","FRENCH Tri 2"
        return "3B","Migraine connue.","FRENCH Tri 3B"
    if motif in ["Vertiges / trouble de l'equilibre"]:
        if details.get("signes_neuro") or details.get("cephalee_brutale"): return "2","Signes neuro.","FRENCH Tri 2"
        return "5","Troubles stables.","FRENCH Tri 5"
    if motif == "Confusion / desorientation":
        if temp >= 38.5: return "2","Confusion + fievre.","FRENCH Tri 2"
        return "3B","Confusion afebrile.","FRENCH Tri 3B"
    if motif == "Hematemese / vomissement de sang":
        if details.get("abondante"): return "2","Hematemese abondante.","FRENCH Tri 2"
        return "3B","Striures de sang.","FRENCH Tri 3B"
    if motif == "Rectorragie / melena":
        if details.get("abondante"): return "2","Rectorragie abondante.","FRENCH Tri 2"
        return "3B","Selles souillees.","FRENCH Tri 3B"
    if motif == "Douleur abdominale":
        if details.get("defense") or details.get("contracture") or details.get("mauvaise_tolerance"): return "2","Defense / contracture.","FRENCH Tri 2"
        if details.get("regressive"): return "5","Douleur regressive.","FRENCH Tri 5"
        return "3B","Douleur moderee.","FRENCH Tri 3B"
    if motif == "Douleur lombaire / colique nephretique":
        if details.get("intense"): return "2","Douleur intense.","FRENCH Tri 2"
        if details.get("regressive"): return "5","Douleur regressive.","FRENCH Tri 5"
        return "3B","Douleur moderee.","FRENCH Tri 3B"
    if motif == "Retention d'urine / anurie": return "2","Retention urinaire.","FRENCH Tri 2"
    if motif == "Douleur testiculaire / torsion":
        if details.get("intense") or details.get("suspicion_torsion"): return "2","Torsion suspectee.","FRENCH Tri 2"
        return "3B","Avis referent.","FRENCH Tri 3B"
    if motif == "Hematurie":
        if details.get("abondante_active"): return "2","Hematurie abondante.","FRENCH Tri 2"
        return "3B","Hematurie moderee.","FRENCH Tri 3B"
    if motif == "Traumatisme avec amputation": return "M","Amputation.","FRENCH Tri M"
    if motif == "Traumatisme abdomen / thorax / cervical":
        if details.get("penetrant"): return "1","Penetrant.","FRENCH Tri 1"
        if details.get("cinetique")=="Haute": return "2","Haute velocite.","FRENCH Tri 2"
        if details.get("mauvaise_tolerance"): return "3B","Faible velocite + mauvaise tolerance.","FRENCH Tri 3B"
        return "4","Bonne tolerance.","FRENCH Tri 4"
    if motif == "Traumatisme cranien":
        if gcs <= 8: return "1",f"TC coma GCS {gcs}.","FRENCH Tri 1"
        if gcs <= 13 or details.get("deficit_neuro") or details.get("convulsion") or details.get("aod_avk") or details.get("vomissements_repetes"):
            return "2","GCS 9-13 / deficit / AVK / vomissements.","FRENCH Tri 2"
        if details.get("pdc") or details.get("plaie") or details.get("hematome"): return "3B","PDC / plaie.","FRENCH Tri 3B"
        return "5","TC sans signe gravite.","FRENCH Tri 5"
    if motif == "Brulure":
        if details.get("etendue") or details.get("main_visage"): return "2","Etendue / main / visage.","FRENCH Tri 2"
        if age <= 2: return "3A","Enfant <= 24 mois.","FRENCH Tri 3A"
        return "3B","Brulure limitee.","FRENCH Tri 3B"
    if motif in ["Traumatisme bassin / hanche / femur / rachis"]:
        if details.get("cinetique")=="Haute": return "2","Haute velocite.","FRENCH Tri 2"
        if details.get("mauvaise_tolerance"): return "3B","Mauvaise tolerance.","FRENCH Tri 3B"
        return "4","Bonne tolerance.","FRENCH Tri 4"
    if motif == "Traumatisme membre / epaule":
        if details.get("ischemie") or details.get("cinetique")=="Haute": return "2","Ischemie / haute velocite.","FRENCH Tri 2"
        if details.get("impotence_totale") or details.get("deformation"): return "3B","Impotence totale.","FRENCH Tri 3B"
        if details.get("impotence_moderee"): return "4","Impotence moderee.","FRENCH Tri 4"
        return "5","Ni impotence ni deformation.","FRENCH Tri 5"
    if motif == "Plaie":
        if details.get("delabrant") or details.get("saignement_actif"): return "2","Delabrante / saignement.","FRENCH Tri 2"
        if details.get("large_complexe") or details.get("main"): return "3B","Large / main.","FRENCH Tri 3B"
        if details.get("superficielle"): return "4","Superficielle.","FRENCH Tri 4"
        return "5","Excoriation.","FRENCH Tri 5"
    if motif == "Electrisation":
        if details.get("pdc") or details.get("foudre"): return "2","PDC / foudre.","FRENCH Tri 2"
        if details.get("haute_tension"): return "3B","Haute tension.","FRENCH Tri 3B"
        return "4","Courant domestique.","FRENCH Tri 4"
    if motif == "Agression sexuelle / sevices": return "1","Agression sexuelle.","FRENCH Tri 1"
    if motif == "Idee / comportement suicidaire": return "1","Comportement suicidaire.","FRENCH Tri 1"
    if motif == "Troubles du comportement / psychiatrie":
        if details.get("agitation") or details.get("violence"): return "2","Agitation/violence.","FRENCH Tri 2"
        return "4","Consultation psy.","FRENCH Tri 4"
    if motif in ["Intoxication medicamenteuse","Intoxication non medicamenteuse"]:
        if details.get("mauvaise_tolerance") or details.get("intention_suicidaire") or details.get("cardiotropes"):
            return "2","Mauvaise tolerance / suicidaire.","FRENCH Tri 2"
        return "3B","Avis referent.","FRENCH Tri 3B"
    if motif == "Fievre":
        if temp >= 40 or temp <= 35.2 or details.get("confusion") or details.get("purpura") or details.get("temp_extreme"):
            return "2","Fievre severe ou signes graves.","FRENCH Tri 2"
        if details.get("mauvaise_tolerance") or details.get("hypotension") or pas < 100: return "3B","Mauvaise tolerance.","FRENCH Tri 3B"
        return "5","Fievre toleree.","FRENCH Tri 5"
    if motif == "Accouchement imminent": return "M","Accouchement imminent.","FRENCH Tri M"
    if motif in ["Probleme de grossesse (1er/2eme trimestre)","Probleme de grossesse (3eme trimestre)"]:
        return "3A","Grossesse - surveillance urgente.","FRENCH Tri 3A"
    if motif == "Meno-metrorragie":
        if details.get("grossesse") or details.get("abondante"): return "2","Grossesse / abondante.","FRENCH Tri 2"
        return "3B","Moderee.","FRENCH Tri 3B"
    if motif == "Hyperglycemie":
        gl = details.get("glycemie",0)
        if details.get("cetose_elevee") or gcs < 15: return "2","Cetose / trouble conscience.","FRENCH Tri 2"
        if gl >= 20 or details.get("cetose_positive"): return "3B",f"Glycemie >= 20 ({gl}).","FRENCH Tri 3B"
        return "4","Hyperglycemie moderee.","FRENCH Tri 4"
    if motif == "Hypoglycemie":
        if gcs <= 8: return "1",f"Coma hypoglycemique GCS {gcs}.","FRENCH Tri 1"
        if gcs <= 13 or details.get("mauvaise_tolerance"): return "2","Mauvaise tolerance.","FRENCH Tri 2"
        return "3B","Hypoglycemie moderee.","FRENCH Tri 3B"
    if motif == "Hypothermie":
        if temp <= 32: return "1",f"Hypothermie severe T {temp}.","FRENCH Tri 1"
        if temp <= 35.2: return "2","Hypothermie moderee.","FRENCH Tri 2"
        return "3B","Hypothermie legere.","FRENCH Tri 3B"
    if motif == "Coup de chaleur / insolation":
        if gcs <= 8: return "1","Coup chaleur + coma.","FRENCH Tri 1"
        if temp >= 40: return "2",f"T >= 40C ({temp}).","FRENCH Tri 2"
        return "3B","Coup chaleur leger.","FRENCH Tri 3B"
    if motif == "Allergie / anaphylaxie":
        if details.get("dyspnee") or details.get("mauvaise_tolerance"): return "2","Anaphylaxie severe.","FRENCH Tri 2"
        return "4","Reaction legere.","FRENCH Tri 4"
    if motif == "Epistaxis":
        if details.get("abondant_actif"): return "2","Abondant actif.","FRENCH Tri 2"
        if details.get("abondant_resolutif"): return "3B","Abondant resolutif.","FRENCH Tri 3B"
        return "5","Peu abondant.","FRENCH Tri 5"
    if motif in ["Corps etranger / brulure oculaire","Trouble visuel / cecite"]:
        if details.get("intense") or details.get("chimique") or details.get("brutal"): return "2","Urgence ophtalmologique.","FRENCH Tri 2"
        return "3B","Avis referent.","FRENCH Tri 3B"
    # Fallback
    eva = details.get("eva",0)
    if news2_score >= 5 or gcs < 15: return "2",f"NEWS2={news2_score} GCS={gcs}.","NEWS2/GCS"
    if news2_score >= 1 or eva >= 7:  return "3B",f"EVA={eva} NEWS2={news2_score}.","NEWS2/EVA"
    if eva >= 4: return "4",f"EVA {eva}/10.","EVA"
    return "5","Non urgent.","Defaut"


# =============================================================================
# NEWS2
# =============================================================================
def compute_news2(fr, spo2, supp_o2, temp, pas, fc, gcs, bpco):
    s = 0
    s += 3 if fr<=8 else (1 if fr<=11 else (0 if fr<=20 else (2 if fr<=24 else 3)))
    if not bpco:
        s += 3 if spo2<=91 else (2 if spo2<=93 else (1 if spo2<=95 else 0))
    else:
        s += (3 if spo2<=83 else (2 if spo2<=85 else (1 if spo2<=87 else (0 if spo2<=92 else (1 if spo2<=94 else (2 if spo2<=96 else 3))))))
    if supp_o2: s += 2
    s += 3 if temp<=35.0 else (1 if temp<=36.0 else (0 if temp<=38.0 else (1 if temp<=39.0 else 2)))
    s += 3 if pas<=90 else (2 if pas<=100 else (1 if pas<=110 else (0 if pas<=219 else 3)))
    s += 3 if fc<=40 else (1 if fc<=50 else (0 if fc<=90 else (1 if fc<=110 else (2 if fc<=130 else 3))))
    if gcs < 15: s += 3
    return s

def news2_level(score):
    if score == 0:  return "Faible (0)","news2-low"
    if score <= 4:  return f"Faible ({score})","news2-low"
    if score <= 6:  return f"Modere ({score})","news2-med"
    if score <= 8:  return f"Eleve ({score})","news2-high"
    return f"CRITIQUE ({score})","news2-crit"

def vital_badge(val, lw, lc, hw, hc, u=""):
    if val <= lc or val >= hc: return f'<span class="vital-alert vital-crit">! {val}{u}</span>'
    if val <= lw or val >= hw: return f'<span class="vital-alert vital-warn">~ {val}{u}</span>'
    return f'<span class="vital-alert vital-ok">ok</span>'


# =============================================================================
# POINT 2 : ECHELLE DOULEUR ADAPTEE A L'AGE
# =============================================================================
def echelle_douleur(age_patient):
    """Retourne (score, echelle_utilisee)"""
    if age_patient < 3:
        # FLACC
        st.markdown("**Echelle FLACC** *(< 3 ans — observation comportementale)*")
        items = {
            "Visage (grimace, froncement)":    ["0 - Aucune expression","1 - Grimace occasionnelle","2 - Froncement permanent"],
            "Jambes (agitation)":              ["0 - Position normale","1 - Genees, agitees","2 - Crispees / ruades"],
            "Activite (position corps)":       ["0 - Allong, calme","1 - Se tortille / arquee","2 - Rigide / convulsive"],
            "Pleurs":                          ["0 - Pas de pleurs","1 - Gemissements","2 - Pleurs continus"],
            "Consolabilite":                   ["0 - Calme facilement","1 - Difficile a calmer","2 - Inconsolable"],
        }
        total = 0
        ca, cb = st.columns(2)
        for i, (lbl, opts) in enumerate(items.items()):
            col = ca if i < 3 else cb
            v = col.selectbox(lbl, opts, key=f"flacc_{i}")
            total += int(v[0])
        if total <= 2:   interp, css = "Douleur legere / absente","score-low"
        elif total <= 6: interp, css = "Douleur moderee - antalgiques palier 1","score-med"
        else:             interp, css = "Douleur severe - antalgiques urgents","score-high"
        return total, "FLACC", interp, css

    elif age_patient < 8:
        # Wong-Baker FACES
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
        if score <= 2:  interp, css = "Douleur legere","score-low"
        elif score <= 6: interp, css = "Douleur moderee","score-med"
        else:             interp, css = "Douleur severe","score-high"
        return score, "Wong-Baker", interp, css

    else:
        # EVA / EN standard
        st.markdown("**Echelle Visuelle Analogique (EVA)** *(>= 8 ans)*")
        score = st.slider("Douleur de 0 (aucune) a 10 (maximale)", 0, 10, 0, key="eva_std")
        emoji_map = {0:"😌",1:"🙂",2:"🙂",3:"😐",4:"😐",5:"😟",6:"😟",7:"😣",8:"😣",9:"😫",10:"😭"}
        st.markdown(f"### {emoji_map.get(score,'😐')}  EVA = {score}/10")
        if score <= 3:   interp, css = "Douleur legere - palier 1","score-low"
        elif score <= 6: interp, css = "Douleur moderee - palier 1-2","score-med"
        else:             interp, css = "Douleur severe - palier 2-3 ou IV","score-high"
        return score, "EVA", interp, css


# =============================================================================
# POINT 4 : GENERATION FICHE DE TRI (HTML imprimable)
# =============================================================================
def generate_fiche_tri(age, motif, niveau, tri_label, sector, temp, fc, pas, spo2, fr, gcs,
                        news2, news2_label, eva, atcd, allergies, arrivee_str, details):
    atcd_str = ", ".join(atcd) if atcd else "RAS"
    all_str  = allergies if allergies != "RAS" else "Aucune connue"
    fiche = f"""
<div class="fiche-tri">
  <div class="fiche-header">
    <div class="fiche-title">FICHE DE TRI - IAO Expert Pro v11</div>
    <div style="font-size:0.75rem;color:#64748b;">{arrivee_str}</div>
  </div>
  <div class="fiche-niveau fiche-{niveau}">{TRI_EMOJI.get(niveau,'')} {tri_label}</div>
  <div class="fiche-section">PATIENT</div>
  <div class="fiche-row"><span>Age</span><span>{age} ans</span></div>
  <div class="fiche-row"><span>Motif</span><span><b>{motif}</b></span></div>
  <div class="fiche-row"><span>Allergies</span><span style="color:#dc2626;font-weight:600">{all_str}</span></div>
  <div class="fiche-row"><span>ATCD</span><span>{atcd_str}</span></div>
  <div class="fiche-section">CONSTANTES</div>
  <div class="fiche-row"><span>T°</span><span>{temp} C</span></div>
  <div class="fiche-row"><span>FC</span><span>{fc} bpm</span></div>
  <div class="fiche-row"><span>PAS</span><span>{pas} mmHg</span></div>
  <div class="fiche-row"><span>SpO2</span><span>{spo2} %</span></div>
  <div class="fiche-row"><span>FR</span><span>{fr} cpm</span></div>
  <div class="fiche-row"><span>GCS</span><span>{gcs}/15</span></div>
  <div class="fiche-row"><span>NEWS2</span><span>{news2} - {news2_label}</span></div>
  <div class="fiche-row"><span>EVA/FLACC</span><span>{eva}/10</span></div>
  <div class="fiche-section">ORIENTATION</div>
  <div class="fiche-row"><span>Secteur</span><span><b>{sector}</b></span></div>
  <div style="font-size:0.7rem;color:#94a3b8;margin-top:10px;text-align:center;">
    FRENCH Triage SFMU V1.1 - Ismaile Ibn-Daifa, IAO
  </div>
</div>
"""
    return fiche


# =============================================================================
# ALERTES DE SECURITE
# =============================================================================
def check_coherence(fc, pas, spo2, fr, gcs, temp, s_eva, motif, atcd, details, news2_score):
    danger, warning, info = [], [], []
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
        danger.append("NE PAS TRANSPORTER : Malinas >= 8 - protocole accouchement inopiné")
    if news2_score >= 5 and temp >= 38.5:
        danger.append("SEPSIS GRAVE : NEWS2 >= 5 + fievre - hemocultures + antibiotiques dans l'heure")
    if pas < 90 and fc > 100:
        si = round(fc/pas, 1) if pas > 0 else 0
        danger.append(f"CHOC probable : Shock Index {si} (FC {fc}/PAS {pas}) - 2 VVP + remplissage")
    if spo2 < 85 or fr >= 40:
        danger.append(f"DETRESSE RESPIRATOIRE : SpO2 {spo2}% FR {fr} - O2 haut debit + preparer intubation")
    if gcs <= 8:
        danger.append(f"COMA GCS {gcs} : Protection VA - position laterale - intubation a discuter")
    if temp <= 32:
        danger.append(f"HYPOTHERMIE SEVERE T {temp}C : rechauffement actif - risque FV")
    if temp >= 41:
        danger.append(f"HYPERTHERMIE MALIGNE T {temp}C : refroidissement immediat")
    if "Immunodepression" in atcd and temp >= 38.5:
        warning.append("NEUTROPENIE FEBRILE possible : NFS urgente + antibiotiques sans attendre")
    return danger, warning, info


# =============================================================================
# BILANS SUGGERES
# =============================================================================
def suggest_bilan(motif, details, fc, pas, spo2, fr, gcs, temp, age, atcd, news2_score, niveau):
    b = {"Biologie":[],"Imagerie":[],"ECG / Monitoring":[],"Gestes immediats":[],"Avis specialiste":[]}
    if niveau in ["M","1","2"]:
        b["Biologie"] += ["NFS, plaquettes","Ionogramme, creatinine","Glycemie","Groupe RAI"]
        b["ECG / Monitoring"] += ["Scope cardiorespiratoire","SpO2 continue","VVP calibre"]
    if "thoracique" in motif.lower() or "SCA" in motif:
        b["Biologie"] += ["Troponine Hs T0 et T1h","D-Dimeres si EP","BNP si IC"]
        b["ECG / Monitoring"] += ["ECG 12 derivations URGENT","Repeter ECG a 30 min"]
        b["Imagerie"] += ["Radio thorax face"]
        b["Gestes immediats"] += ["Aspirine 250 mg si SCA non CI","O2 si SpO2 < 95%"]
        if "Anticoagulants / AOD" in atcd:
            b["Gestes immediats"] += ["ATTENTION anticoagulants - adapter heparine"]
    if "AVC" in motif or "neurologique" in motif.lower():
        b["Biologie"] += ["NFS TP TCA fibrinogene","Glycemie (CI thrombolyse si < 0.6 ou > 22)"]
        b["Imagerie"] += ["TDM cerebral sans injection URGENT","IRM si disponible"]
        b["Avis specialiste"] += ["Neurologue vasculaire urgent"]
        b["Gestes immediats"] += ["ALERTE FILIERE AVC - objectif porte-aiguille < 60 min"]
    if "dyspnee" in motif.lower() or "respiratoire" in motif.lower():
        b["Biologie"] += ["Gaz du sang arteriels","D-Dimeres si EP"]
        b["Imagerie"] += ["Radio thorax","Echo pulmonaire si dispo"]
        b["Gestes immediats"] += ["O2 - objectif SpO2 > 94%","Position demi-assise"]
    if "traumatisme" in motif.lower() and niveau in ["M","1","2"]:
        b["Biologie"] += ["Bilan pre-transfusionnel","Lactates"]
        b["Imagerie"] += ["Pan-scanner si polytrauma","Echo-FAST"]
        b["Gestes immediats"] += ["Compression hemorragie externe","2 VVP + remplissage"]
    if "fievre" in motif.lower() or (temp >= 38.5 and news2_score >= 3):
        b["Biologie"] += ["Hemocultures x2 AVANT ATB","Lactates","CRP PCT NFS"]
        b["Gestes immediats"] += ["Hemocultures AVANT antibiotherapie","ATB large spectre si sepsis grave"]
    if "allergie" in motif.lower():
        b["Gestes immediats"] += ["ADRENALINE 0.5 mg IM face anterolaterale cuisse","Antihistaminique + corticoides IV","Remplissage NaCl 0.9%"]
    if "hypoglycemie" in motif.lower():
        b["Gestes immediats"] += ["Glycemie capillaire IMMEDIATE","G30% 50mL IV si inconscient","Glucagon 1mg SC/IM si pas d'acces"]
    if "intoxication" in motif.lower():
        b["Biologie"] += ["Toxicologie urinaire + sanguine","Paracetamol + ethanol systematiques"]
        b["ECG / Monitoring"] += ["ECG - toxiques cardiotropes"]
        b["Avis specialiste"] += ["Centre antipoison"]
    return {k:v for k,v in b.items() if v}


# =============================================================================
# SBAR NARRATIF
# =============================================================================
def generate_sbar(age, motif, cat, atcd, allergies, supp_o2, temp, fc, pas, spo2, fr, gcs,
                  news2, news2_label, eva, eva_echelle, p_pqrst, q_pqrst, r_pqrst, t_onset,
                  details, niveau, tri_label, justif, critere_ref, sector,
                  gcs_y=4, gcs_v=5, gcs_m=6):
    now_str  = datetime.now().strftime("%d/%m/%Y a %H:%M")
    atcd_str = ", ".join(atcd) if atcd else "aucun antecedent"
    all_str  = allergies if allergies and allergies != "RAS" else "aucune allergie connue"
    if gcs == 15: conscience = "conscient et oriente"
    elif gcs >= 13: conscience = f"conscience alteree GCS {gcs} (Y{gcs_y}V{gcs_v}M{gcs_m})"
    elif gcs >= 9:  conscience = f"obnubile GCS {gcs} (Y{gcs_y}V{gcs_v}M{gcs_m})"
    else:           conscience = f"COMA GCS {gcs} (Y{gcs_y}V{gcs_v}M{gcs_m})"
    anomalies = []
    if temp > 38 or temp < 36: anomalies.append(f"T {temp}C")
    if fc > 100:  anomalies.append(f"tachycardie {fc} bpm")
    if fc < 60:   anomalies.append(f"bradycardie {fc} bpm")
    if pas < 90:  anomalies.append(f"hypotension {pas} mmHg")
    if pas > 180: anomalies.append(f"HTA {pas} mmHg")
    if spo2 < 94: anomalies.append(f"desaturation {spo2}%")
    if fr > 20:   anomalies.append(f"polypnee {fr} cpm")
    vitaux_txt = "dans les normes" if not anomalies else "ANOMALIES : " + ", ".join(anomalies)
    return f"""{'='*52}
  TRANSMISSION SBAR - IAO Expert Pro v11.0
  FRENCH Triage SFMU V1.1 | {now_str}
  Ismaile Ibn-Daifa - Infirmier Urgences
{'='*52}

[S] SITUATION
Patient de {age} ans, pris en charge a {now_str}
Motif : {motif} ({cat})
Douleur ({eva_echelle}) : {eva}/10 | {conscience}
Niveau FRENCH : {tri_label}

[B] BACKGROUND
ATCD : {atcd_str}
Allergies : {all_str}
O2 supplementaire a l'admission : {'oui' if supp_o2 else 'non'}

[A] ASSESSMENT
Constantes : T {temp}C | FC {fc} bpm | PAS {pas} mmHg
             SpO2 {spo2}% | FR {fr} cpm | GCS {gcs}/15
Bilan vitaux : {vitaux_txt}
NEWS2 : {news2} ({news2_label})

PQRST :
  P - Provoque/Pallie : {p_pqrst or 'non precise'}
  Q - Qualite/Type    : {q_pqrst}
  R - Region/Irrad.   : {r_pqrst or 'non precise'}
  S - Severite        : {eva}/10 ({eva_echelle})
  T - Temps/Duree     : {t_onset or 'non precise'}

Justification : {justif}
Reference FRENCH : {critere_ref}

[R] RECOMMENDATION
Orientation : {sector}
{'Demande prise en charge IMMEDIATE en SAUV.' if niveau in ['M','1'] else
 'Demande evaluation medicale urgente < 20 min.' if niveau == '2' else
 'Evaluation dans les delais recommandes.'}

{'='*52}
Signe : Ismaile Ibn-Daifa (IAO) | {now_str}
"""


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown("## IAO Expert Pro v11.0")
    st.caption("FRENCH Triage SFMU V1.1")

    # Bascule mode
    st.markdown('<div class="section-header">Mode</div>', unsafe_allow_html=True)
    mode = st.radio("Interface", ["Tri Rapide (< 2 min)","Complet"], horizontal=True, label_visibility="collapsed")
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

    st.markdown('<div class="section-header">Patient & ATCD</div>', unsafe_allow_html=True)
    age       = st.number_input("Age", 0, 120, 45)
    atcd      = st.multiselect("Facteurs de risque", [
        "HTA","Diabete","Insuffisance Cardiaque","BPCO",
        "Anticoagulants / AOD","Grossesse","Immunodepression","Neoplasie"
    ])
    allergies = st.text_input("Allergies", "RAS")
    supp_o2   = st.checkbox("O2 supplementaire")

    st.markdown('<div class="legal-text">FRENCH Triage SFMU V1.1 - Juin 2018<br>Usage professionnel exclusif.</div>', unsafe_allow_html=True)
    st.markdown('<div class="signature">Ismaile Ibn-Daifa<br>Infirmier Urgences</div>', unsafe_allow_html=True)


# =============================================================================
# TABS
# =============================================================================
if st.session_state.mode == "rapide":
    tabs = st.tabs(["⚡ Tri Rapide","🔄 Reevaluation","📋 Historique"])
    t_rapide, t_reeval, t_history = tabs
    t_complet = t_scores = None
else:
    tabs = st.tabs([
        "📊 Signes Vitaux","🔍 Anamnese","⚖️ Triage & SBAR",
        "🧮 Scores","🔄 Reevaluation",f"📋 Historique ({len(st.session_state.patient_history)})"
    ])
    t_vitals, t_anamnesis, t_decision, t_scores, t_reeval, t_history = tabs
    t_rapide = None


# =============================================================================
# CONSTANTES VITALES (communes aux deux modes)
# =============================================================================
# Valeurs par defaut — seront saisies dans chaque tab
temp = fc = pas = spo2 = fr = gcs = None


# =============================================================================
# ⚡ MODE TRI RAPIDE
# =============================================================================
if st.session_state.mode == "rapide":
    with t_rapide:
        st.markdown('<div class="tri-rapide-title">TRI RAPIDE — Saisie optimisee < 2 minutes</div>', unsafe_allow_html=True)

        # Constantes rapides
        st.markdown('<div class="section-header">1. Constantes vitales</div>', unsafe_allow_html=True)
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        temp = c1.number_input("T° (C)", 30.0, 45.0, 37.0, 0.1, key="r_temp")
        fc   = c2.number_input("FC", 20, 220, 80, key="r_fc")
        pas  = c3.number_input("PAS", 40, 260, 120, key="r_pas")
        spo2 = c4.number_input("SpO2%", 50, 100, 98, key="r_spo2")
        fr   = c5.number_input("FR", 5, 60, 16, key="r_fr")
        gcs  = c6.number_input("GCS", 3, 15, 15, key="r_gcs")

        # Shock Index rapide
        si = round(fc/pas, 2) if pas > 0 else 0
        si_css = "vital-crit" if si >= 1.0 else ("vital-warn" if si >= 0.8 else "vital-ok")
        st.markdown(f'Shock Index : <span class="vital-alert {si_css}">{si}</span>', unsafe_allow_html=True)

        # NEWS2 rapide
        bpco_flag = "BPCO" in atcd
        news2 = compute_news2(fr, spo2, supp_o2, temp, pas, fc, gcs, bpco_flag)
        news2_label, news2_class = news2_level(news2)
        st.markdown(f'NEWS2 : <span class="news2-badge {news2_class}">{news2_label}</span>', unsafe_allow_html=True)

        # Motif
        st.markdown('<div class="section-header">2. Motif en 1 clic</div>', unsafe_allow_html=True)
        MOTIFS_FLAT = [
            "Arret cardiorespiratoire","Hypotension arterielle","Douleur thoracique / SCA",
            "Tachycardie / tachyarythmie","Bradycardie / bradyarythmie","Hypertension arterielle",
            "Dyspnee / insuffisance respiratoire","Palpitations","Asthme / aggravation BPCO",
            "AVC / Deficit neurologique","Alteration de conscience / Coma","Convulsions",
            "Cephalee","Vertiges / trouble de l'equilibre","Confusion / desorientation",
            "Traumatisme avec amputation","Traumatisme abdomen / thorax / cervical",
            "Traumatisme cranien","Brulure","Traumatisme bassin / hanche / femur / rachis",
            "Traumatisme membre / epaule","Plaie","Electrisation","Agression sexuelle / sevices",
            "Hematemese / vomissement de sang","Rectorragie / melena","Douleur abdominale",
            "Douleur lombaire / colique nephretique","Retention d'urine / anurie",
            "Douleur testiculaire / torsion","Hematurie",
            "Accouchement imminent","Probleme de grossesse (1er/2eme trimestre)",
            "Probleme de grossesse (3eme trimestre)","Meno-metrorragie",
            "Idee / comportement suicidaire","Troubles du comportement / psychiatrie",
            "Intoxication medicamenteuse","Intoxication non medicamenteuse",
            "Fievre","Hyperglycemie","Hypoglycemie","Hypothermie",
            "Coup de chaleur / insolation","Allergie / anaphylaxie",
            "Epistaxis","Corps etranger / brulure oculaire","Trouble visuel / cecite",
        ]
        motif = st.selectbox("Motif", MOTIFS_FLAT, key="r_motif")

        # POINT 1 : Questions guidees automatiques selon motif
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
            st.caption("Aucune question specifique - motif general.")

        # POINT 2 : Douleur adaptee a l'age
        st.markdown('<div class="section-header">4. Evaluation de la douleur</div>', unsafe_allow_html=True)
        eva_score, eva_echelle, eva_interp, eva_css = echelle_douleur(age)
        details["eva"] = eva_score
        st.markdown(f'<div class="score-result {eva_css}">{eva_score}/10 ({eva_echelle})</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="score-interp">→ {eva_interp}</div>', unsafe_allow_html=True)

        # Calcul triage
        niveau, justif, critere_ref = french_triage(motif, details, fc, pas, spo2, fr, gcs, temp, age, news2)
        tri_label = TRI_LABELS[niveau]
        sector    = TRI_SECTORS[niveau]
        emoji     = TRI_EMOJI[niveau]

        st.markdown('<div class="section-header">5. Resultat</div>', unsafe_allow_html=True)

        # Alerte depassement reevaluation
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

        # Alertes securite
        alertes_d, alertes_w, _ = check_coherence(fc, pas, spo2, fr, gcs, temp, eva_score, motif, atcd, details, news2)
        for a in alertes_d: st.markdown(f'<div class="alert-danger">⚠ {a}</div>', unsafe_allow_html=True)
        for a in alertes_w: st.markdown(f'<div class="alert-warning">△ {a}</div>', unsafe_allow_html=True)

        # POINT 3 : Fiche de tri imprimable
        st.markdown('<div class="section-header">Fiche de tri</div>', unsafe_allow_html=True)
        arrivee_str = st.session_state.arrival_time.strftime("%d/%m/%Y %H:%M") if st.session_state.arrival_time else datetime.now().strftime("%d/%m/%Y %H:%M")
        fiche_html = generate_fiche_tri(age, motif, niveau, tri_label, sector, temp, fc, pas, spo2, fr, gcs, news2, news2_label, eva_score, atcd, allergies, arrivee_str, details)
        st.markdown(fiche_html, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        # Enregistrer dans historique
        if col_a.button("Enregistrer ce patient", use_container_width=True):
            sbar = generate_sbar(age, motif, "Tri Rapide", atcd, allergies, supp_o2,
                                  temp, fc, pas, spo2, fr, gcs, news2, news2_label,
                                  eva_score, eva_echelle, "", "", "", "",
                                  details, niveau, tri_label, justif, critere_ref, sector)
            st.session_state.sbar_text = sbar
            st.session_state.patient_history.append({
                "heure": datetime.now().strftime("%H:%M"),
                "age": age, "motif": motif, "cat": "Tri Rapide",
                "niveau": niveau, "eva": eva_score, "news2": news2,
                "sbar": sbar, "alertes_danger": len(alertes_d),
            })
            # Snapshot réévaluation initial
            st.session_state.reeval_history = [{
                "heure": datetime.now().strftime("%H:%M"),
                "fc": fc, "pas": pas, "spo2": spo2, "fr": fr, "gcs": gcs, "temp": temp, "niveau": niveau,
            }]
            st.success("Patient enregistre.")

        # POINT 5 : Reevaluation 1 touche
        if col_b.button("Reevaluer maintenant", use_container_width=True):
            st.session_state.last_reeval = datetime.now()
            snap = {"heure": datetime.now().strftime("%H:%M"), "fc": fc, "pas": pas,
                    "spo2": spo2, "fr": fr, "gcs": gcs, "temp": temp, "niveau": niveau}
            st.session_state.reeval_history.append(snap)
            st.success(f"Reevaluation enregistree a {snap['heure']} - Tri {niveau}")


# =============================================================================
# MODE COMPLET — TABS
# =============================================================================
else:
    # ── TAB 1 : SIGNES VITAUX ────────────────────────────────────────────────
    with t_vitals:
        st.markdown('<div class="section-header">Constantes vitales</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        temp = c1.number_input("Temperature (C)", 30.0, 45.0, 37.0, 0.1)
        fc   = c1.number_input("FC (bpm)", 20, 220, 80)
        pas  = c2.number_input("Systolique (mmHg)", 40, 260, 120)
        spo2 = c2.slider("SpO2 (%)", 50, 100, 98)
        fr   = c3.number_input("FR (cpm)", 5, 60, 16)
        gcs  = c3.select_slider("Glasgow", list(range(3, 16)), 15)

        st.markdown('<div class="section-header">Alertes & Shock Index</div>', unsafe_allow_html=True)
        a1,a2,a3,a4,a5 = st.columns(5)
        a1.markdown(f"**T°** {vital_badge(temp,36,35,38,40.5,'C')}", unsafe_allow_html=True)
        a2.markdown(f"**FC** {vital_badge(fc,50,40,100,130,'')}", unsafe_allow_html=True)
        a3.markdown(f"**PAS** {vital_badge(pas,100,90,180,220,'')}", unsafe_allow_html=True)
        a4.markdown(f"**SpO2** {vital_badge(spo2,94,90,100,100,'%')}", unsafe_allow_html=True)
        a5.markdown(f"**FR** {vital_badge(fr,12,8,20,25,'')}", unsafe_allow_html=True)
        si = round(fc/pas,2) if pas > 0 else 0
        si_css = "vital-crit" if si >= 1.0 else ("vital-warn" if si >= 0.8 else "vital-ok")
        st.markdown(f'**Shock Index** : <span class="vital-alert {si_css}">{si}</span>{"  CHOC probable" if si >= 1 else ""}', unsafe_allow_html=True)

        bpco_flag = "BPCO" in atcd
        news2 = compute_news2(fr, spo2, supp_o2, temp, pas, fc, gcs, bpco_flag)
        news2_label, news2_class = news2_level(news2)
        st.markdown('<div class="section-header">NEWS2</div>', unsafe_allow_html=True)
        cn, ci = st.columns([1,2])
        cn.markdown(f'<div class="news2-badge {news2_class}">{news2_label}</div>', unsafe_allow_html=True)
        interp_map = {
            "news2-low":("Standard","Reevaluation >= 12h."),
            "news2-med":("Rapprochee","Reevaluation 1h."),
            "news2-high":("Urgente","Evaluation medicale immediate."),
            "news2-crit":("URGENCE ABSOLUE","Transfert SAUV immediat."),
        }
        ti, di = interp_map[news2_class]
        ci.markdown(f"**{ti}**") ; ci.markdown(di)

    # ── TAB 2 : ANAMNESE ─────────────────────────────────────────────────────
    with t_anamnesis:
        # POINT 2 : Douleur adaptee a l'age
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
            q_pqrst = st.selectbox("Q - Qualite / Type", ["Sourd","Etau","Brulure","Coup de poignard","Electrique","Tension","Pesanteur","Crampe"])
            r_pqrst = st.text_input("R - Region / Irradiation", placeholder="Bras, machoire, dos...")
        with c2:
            t_onset = st.text_input("T - Temps", placeholder="Depuis 30 min, brutal...")

        # Motif + questions guidees
        st.markdown('<div class="section-header">Motif & Questions guidees FRENCH</div>', unsafe_allow_html=True)
        MOTIFS_DICT = {
            "CARDIO-CIRCULATOIRE":["Arret cardiorespiratoire","Hypotension arterielle","Douleur thoracique / SCA","Tachycardie / tachyarythmie","Bradycardie / bradyarythmie","Hypertension arterielle","Dyspnee / insuffisance respiratoire","Palpitations"],
            "RESPIRATOIRE":["Asthme / aggravation BPCO","Hemoptysie","Corps etranger voies aeriennes"],
            "NEUROLOGIE":["AVC / Deficit neurologique","Alteration de conscience / Coma","Convulsions","Cephalee","Vertiges / trouble de l'equilibre","Confusion / desorientation"],
            "TRAUMATOLOGIE":["Traumatisme avec amputation","Traumatisme abdomen / thorax / cervical","Traumatisme cranien","Brulure","Traumatisme bassin / hanche / femur / rachis","Traumatisme membre / epaule","Plaie","Electrisation","Agression sexuelle / sevices"],
            "ABDOMINAL":["Hematemese / vomissement de sang","Rectorragie / melena","Douleur abdominale"],
            "GENITO-URINAIRE":["Douleur lombaire / colique nephretique","Retention d'urine / anurie","Douleur testiculaire / torsion","Hematurie"],
            "GYNECO-OBSTETRIQUE":["Accouchement imminent","Probleme de grossesse (1er/2eme trimestre)","Probleme de grossesse (3eme trimestre)","Meno-metrorragie"],
            "PSYCHIATRIE / INTOXICATION":["Idee / comportement suicidaire","Troubles du comportement / psychiatrie","Intoxication medicamenteuse","Intoxication non medicamenteuse"],
            "INFECTIOLOGIE":["Fievre"],
            "DIVERS METABOLIQUES":["Hyperglycemie","Hypoglycemie","Hypothermie","Coup de chaleur / insolation","Allergie / anaphylaxie"],
            "ORL / OPHTALMO":["Epistaxis","Corps etranger / brulure oculaire","Trouble visuel / cecite"],
        }
        cat   = st.selectbox("Categorie", list(MOTIFS_DICT.keys()))
        motif = st.selectbox("Motif de recours", MOTIFS_DICT[cat])

        # Suggestion score
        score_hints = {
            "Douleur thoracique / SCA":"Score TIMI recommande (onglet Scores)",
            "Accouchement imminent":"Score Malinas recommande (onglet Scores)",
            "Brulure":"Score Brulure + Baux recommande (onglet Scores)",
            "Alteration de conscience / Coma":"Glasgow detaille recommande (onglet Scores)",
        }
        if motif in score_hints:
            st.markdown(f'<div class="alert-info">💡 {score_hints[motif]}</div>', unsafe_allow_html=True)

        # POINT 1 : Questions guidees
        details = {"eva": eva_score}
        questions = QUESTIONS_GUIDEES.get(motif, [])
        if questions:
            st.markdown("**Questions discriminantes automatiques :**")
            cq1, cq2 = st.columns(2)
            for i, (label, key, typ) in enumerate(questions):
                col = cq1 if i % 2 == 0 else cq2
                details[key] = col.checkbox(label, key=f"qg_c_{key}")
        # Champs complementaires selon motif
        if motif == "Douleur thoracique / SCA":
            details['ecg']                    = st.selectbox("ECG", ["Normal","Anormal typique SCA","Anormal non typique"])
            details['douleur_type']           = st.selectbox("Type douleur", ["Atypique","Typique persistante/intense","Type coronaire"])
            details['comorbidites_coronaires']= st.checkbox("Comorbidites coronaires")
        elif motif == "Dyspnee / insuffisance respiratoire":
            details['parole_ok'] = st.radio("Parler en phrases completes ?", [True, False], format_func=lambda x: "Oui" if x else "Non", horizontal=True)
            c1a, c1b = st.columns(2)
            details['orthopnee'] = c1a.checkbox("Orthopnee")
            details['tirage']    = c1b.checkbox("Tirage intercostal")
        elif motif == "AVC / Deficit neurologique":
            details['delai_heures'] = st.number_input("Delai depuis debut (heures)", 0.0, 72.0, 2.0, 0.5)
        elif motif == "Traumatisme cranien":
            c1a,c1b = st.columns(2)
            details['pdc']              = c1a.checkbox("PDC initiale")
            details['vomissements_repetes']= c1a.checkbox("Vomissements repetes")
            details['aod_avk']          = c1b.checkbox("AOD / AVK")
            details['deficit_neuro']    = c1b.checkbox("Deficit neuro")
        elif motif == "Douleur abdominale":
            c1a,c1b = st.columns(2)
            details['defense']    = c1a.checkbox("Defense abdominale")
            details['contracture']= c1a.checkbox("Contracture")
            details['regressive'] = c1b.checkbox("Douleur regressive")
            details['mauvaise_tolerance'] = c1b.checkbox("Mauvaise tolerance")
        elif motif == "Fievre":
            c1a,c1b = st.columns(2)
            details['confusion']          = c1a.checkbox("Confusion")
            details['purpura']            = c1a.checkbox("Purpura")
            details['mauvaise_tolerance'] = c1b.checkbox("Mauvaise tolerance")
        elif motif == "Allergie / anaphylaxie":
            details['dyspnee']            = st.checkbox("Dyspnee / oedeme larynge")
            details['mauvaise_tolerance'] = st.checkbox("Mauvaise tolerance (chute TA)")
        elif motif in ["Intoxication medicamenteuse","Intoxication non medicamenteuse"]:
            details['mauvaise_tolerance']  = st.checkbox("Mauvaise tolerance")
            details['intention_suicidaire']= st.checkbox("Intention suicidaire")
            details['cardiotropes']        = st.checkbox("Toxiques cardiotropes")
        elif motif == "Brulure":
            details['etendue']     = st.checkbox("Etendue > 10% SCT")
            details['main_visage'] = st.checkbox("Main / visage / perinee")
        elif motif in ["Hematemese / vomissement de sang","Rectorragie / melena"]:
            details['abondante'] = st.checkbox("Saignement abondant")
        elif motif == "Plaie":
            details['saignement_actif'] = st.checkbox("Saignement actif")
            details['delabrant']        = st.checkbox("Plaie delabrante")
            details['main']             = st.checkbox("Localisation main")
            details['superficielle']    = st.checkbox("Superficielle")
        elif motif == "Meno-metrorragie":
            details['grossesse'] = st.checkbox("Grossesse connue / suspectee")
            details['abondante'] = st.checkbox("Saignement abondant")
        elif motif in ["Douleur lombaire / colique nephretique","Hematurie","Douleur testiculaire / torsion"]:
            details['intense']           = st.checkbox("Douleur intense")
            details['regressive']        = st.checkbox("Douleur regressive")
            details['suspicion_torsion'] = st.checkbox("Suspicion torsion") if "testiculaire" in motif else False
            details['abondante_active']  = st.checkbox("Saignement actif") if "Hematurie" in motif else False
        elif motif in ["Hyperglycemie"]:
            details['glycemie']        = st.number_input("Glycemie mmol/L", 0.0, 60.0, 8.0, 0.5)
            details['cetose_elevee']   = st.checkbox("Cetose elevee")
            details['cetose_positive'] = st.checkbox("Cetose positive")
        elif motif in ["Hypoglycemie"]:
            details['mauvaise_tolerance'] = st.checkbox("Mauvaise tolerance")
        elif motif in ["Troubles du comportement / psychiatrie"]:
            details['agitation']     = st.checkbox("Agitation / violence")
            details['hallucinations']= st.checkbox("Hallucinations")
        elif motif in ["Tachycardie / tachyarythmie","Bradycardie / bradyarythmie","Palpitations"]:
            details['mauvaise_tolerance'] = st.checkbox("Mauvaise tolerance hemodynamique")
            details['malaise']            = st.checkbox("Malaise associe")
        elif motif == "Hypertension arterielle":
            details['sf_associes'] = st.checkbox("SF associes (cephalee, trouble visuel, douleur thoracique)")
        elif motif in ["Traumatisme abdomen / thorax / cervical","Traumatisme bassin / hanche / femur / rachis","Traumatisme membre / epaule"]:
            details['cinetique']          = st.selectbox("Cinetique", ["Faible","Haute"])
            details['mauvaise_tolerance'] = st.checkbox("Mauvaise tolerance")
            details['penetrant']          = st.checkbox("Penetrant") if "abdomen" in motif else False
            if "membre" in motif.lower() or "epaule" in motif.lower():
                details['impotence_totale'] = st.checkbox("Impotence totale")
                details['deformation']      = st.checkbox("Deformation")
                details['impotence_moderee']= st.checkbox("Impotence moderee")
                details['ischemie']         = st.checkbox("Ischemie distale")
        elif motif == "Epistaxis":
            details['abondant_actif']    = st.checkbox("Abondant actif")
            details['abondant_resolutif']= st.checkbox("Abondant resolutif")
        elif motif in ["Corps etranger / brulure oculaire","Trouble visuel / cecite"]:
            details['chimique'] = st.checkbox("Brulure chimique")
            details['intense']  = st.checkbox("Douleur intense")
            details['brutal']   = st.checkbox("Debut brutal")
        elif motif == "Convulsions":
            details['crises_multiples'] = st.checkbox("Crises multiples / en cours")
            details['confusion_post_critique'] = st.checkbox("Confusion post-critique")
        elif motif == "Cephalee":
            details['inhabituelle'] = st.checkbox("Inhabituell / 1er episode")
            details['brutale']      = st.checkbox("Debut brutal")
            details['fievre_assoc'] = st.checkbox("Fievre associee")
        elif motif == "Electrisation":
            details['pdc']          = st.checkbox("PDC")
            details['foudre']       = st.checkbox("Foudroiement")
            details['haute_tension']= st.checkbox("Haute tension")
        else:
            pass  # motif sans champs specifiques

    # ── TAB 3 : TRIAGE & SBAR ────────────────────────────────────────────────
    with t_decision:
        if temp is None: temp=37.0; fc=80; pas=120; spo2=98; fr=16; gcs=15
        bpco_flag = "BPCO" in atcd
        news2 = compute_news2(fr, spo2, supp_o2, temp, pas, fc, gcs, bpco_flag)
        news2_label, news2_class = news2_level(news2)
        if 'motif' not in dir(): motif = "Fievre"
        if 'details' not in dir(): details = {}
        if 'eva_score' not in dir(): eva_score = 0; eva_echelle = "EVA"
        if 'cat' not in dir(): cat = "INFECTIOLOGIE"

        niveau, justif, critere_ref = french_triage(motif, details, fc, pas, spo2, fr, gcs, temp, age, news2)
        tri_label = TRI_LABELS[niveau]; sector = TRI_SECTORS[niveau]; emoji = TRI_EMOJI[niveau]

        # Alerte reevaluation
        if st.session_state.last_reeval:
            since_min = (datetime.now() - st.session_state.last_reeval).total_seconds() / 60
            if since_min > TRI_DELAIS.get(niveau, 60):
                st.markdown(f'<div class="alert-danger">REEVALUATION EN RETARD : {int(since_min)} min ecoulees - max {TRI_DELAIS[niveau]} min pour Tri {niveau}</div>', unsafe_allow_html=True)

        st.markdown(
            f'<div class="triage-box {TRI_BOX_CSS[niveau]}">'
            f'<div style="font-size:1.8rem;font-weight:600">{emoji} {tri_label}</div>'
            f'<div style="font-size:0.85rem;margin-top:8px;opacity:.85">NEWS2 {news2} | Douleur {details.get("eva",0)}/10</div>'
            f'<div style="font-size:0.82rem;margin-top:8px;font-style:italic">{justif}</div>'
            f'</div>', unsafe_allow_html=True
        )
        st.info(f"**Orientation :** {sector}")
        st.markdown(f'<div class="french-ref">Ref. FRENCH Triage SFMU V1.1 : {critere_ref}</div>', unsafe_allow_html=True)

        # Alertes
        st.markdown('<div class="section-header">Alertes securite</div>', unsafe_allow_html=True)
        alertes_d, alertes_w, _ = check_coherence(fc, pas, spo2, fr, gcs, temp, details.get("eva",0), motif, atcd, details, news2)
        for a in alertes_d: st.markdown(f'<div class="alert-danger">⚠ {a}</div>', unsafe_allow_html=True)
        for a in alertes_w: st.markdown(f'<div class="alert-warning">△ {a}</div>', unsafe_allow_html=True)
        if not alertes_d and not alertes_w:
            st.markdown('<div class="alert-info">✓ Aucune incoherence detectee.</div>', unsafe_allow_html=True)

        # Bilans
        st.markdown('<div class="section-header">Bilans recommandes</div>', unsafe_allow_html=True)
        bilans = suggest_bilan(motif, details, fc, pas, spo2, fr, gcs, temp, age, atcd, news2, niveau)
        if bilans:
            cols_b = st.columns(min(len(bilans),3))
            for i, (cat_b, items) in enumerate(bilans.items()):
                col = cols_b[i % len(cols_b)]
                items_html = "".join([f'<div class="bilan-item">{it}</div>' for it in items])
                col.markdown(f'<div class="bilan-card"><div class="bilan-title">{cat_b}</div>{items_html}</div>', unsafe_allow_html=True)

        # Fiche de tri + SBAR
        st.markdown('<div class="section-header">Fiche de tri & SBAR</div>', unsafe_allow_html=True)
        arrivee_str = st.session_state.arrival_time.strftime("%d/%m/%Y %H:%M") if st.session_state.arrival_time else datetime.now().strftime("%d/%m/%Y %H:%M")
        fiche_html = generate_fiche_tri(age, motif, niveau, tri_label, sector, temp, fc, pas, spo2, fr, gcs, news2, news2_label, details.get("eva",0), atcd, allergies, arrivee_str, details)
        st.markdown(fiche_html, unsafe_allow_html=True)

        if st.button("Generer SBAR narratif", use_container_width=True):
            gy = st.session_state.get('gcs_y_score',4)
            gv = st.session_state.get('gcs_v_score',5)
            gm = st.session_state.get('gcs_m_score',6)
            sbar = generate_sbar(age, motif, cat, atcd, allergies, supp_o2,
                                  temp, fc, pas, spo2, fr, gcs, news2, news2_label,
                                  details.get("eva",0), eva_echelle if 'eva_echelle' in dir() else "EVA",
                                  p_pqrst if 'p_pqrst' in dir() else "", q_pqrst if 'q_pqrst' in dir() else "",
                                  r_pqrst if 'r_pqrst' in dir() else "", t_onset if 't_onset' in dir() else "",
                                  details, niveau, tri_label, justif, critere_ref, sector, gy, gv, gm)
            st.session_state.sbar_text = sbar
            st.session_state.patient_history.append({
                "heure": datetime.now().strftime("%H:%M"), "age": age, "motif": motif, "cat": cat,
                "niveau": niveau, "eva": details.get("eva",0), "news2": news2, "sbar": sbar,
                "alertes_danger": len(alertes_d),
            })
            st.session_state.reeval_history = [{"heure": datetime.now().strftime("%H:%M"),
                "fc": fc, "pas": pas, "spo2": spo2, "fr": fr, "gcs": gcs, "temp": temp, "niveau": niveau}]

        if st.session_state.sbar_text:
            st.markdown(f'<div class="sbar-block">{st.session_state.sbar_text}</div>', unsafe_allow_html=True)
            st.download_button("Telecharger SBAR (.txt)", data=st.session_state.sbar_text,
                file_name=f"SBAR_{datetime.now().strftime('%Y%m%d_%H%M')}_Tri{niveau}.txt",
                mime="text/plain", use_container_width=True)

    # ── TAB 4 : SCORES ───────────────────────────────────────────────────────
    with t_scores:
        def score_badge_custom(val, css):
            return f'<div class="score-result {css}">{val}</div>'

        st.markdown("### Scores cliniques valides")

        with st.expander("Score TIMI - SCA NSTEMI", expanded=True):
            st.markdown('<div class="score-title">TIMI Risk Score (Antman 2000)</div>', unsafe_allow_html=True)
            ca, cb = st.columns(2)
            t1=ca.checkbox("Age >= 65 ans",key="timi1"); t2=ca.checkbox(">= 3 FdR coronariens",key="timi2")
            t3=ca.checkbox("Stenose connue >= 50%",key="timi3"); t4=ca.checkbox("Deviation ST ECG",key="timi4")
            t5=cb.checkbox(">= 2 angor/24h",key="timi5"); t6=cb.checkbox("Troponine +",key="timi6")
            t7=cb.checkbox("Aspirine < 7j",key="timi7")
            timi_score=sum([t1,t2,t3,t4,t5,t6,t7])
            if timi_score<=2: tc,ti="score-low","Risque 14j ~5% - surveillance + bilan"
            elif timi_score<=4: tc,ti="score-med","Risque 14j ~13-20% - heparine + coro rapide"
            else: tc,ti="score-high","Risque 14j ~26-41% - coronarographie urgente < 2h"
            st.markdown(score_badge_custom(f"{timi_score}/7", tc), unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">→ {ti}</div>', unsafe_allow_html=True)

        with st.expander("Score de Silverman - Nouveau-ne", expanded=False):
            st.markdown('<div class="score-title">Silverman-Andersen (nouveau-ne)</div>', unsafe_allow_html=True)
            sil_items = {
                "Balancement thoraco-abdominal":["0 - Synchrone","1 - Asynchrone leger","2 - Asynchrone marque"],
                "Tirage intercostal":["0 - Absent","1 - Discret","2 - Important"],
                "Creusement xiphoidien":["0 - Absent","1 - Discret","2 - Important"],
                "Battement ailes du nez":["0 - Absent","1 - Discret","2 - Important"],
                "Geignement expiratoire":["0 - Absent","1 - Audible stethoscope","2 - Audible a l'oreille"],
            }
            sv={}; ca2,cb2=st.columns(2)
            for i,(lbl,opts) in enumerate(sil_items.items()):
                col=ca2 if i<3 else cb2
                v=col.selectbox(lbl,opts,key=f"sil_{i}"); sv[lbl]=int(v[0])
            sil_score=sum(sv.values())
            if sil_score==0: sc,si="score-info","Pas de detresse."
            elif sil_score<=3: sc,si="score-low","Detresse legere."
            elif sil_score<=6: sc,si="score-med","Detresse moderee - pediatre urgent."
            else: sc,si="score-high","Detresse severe - reanimation neonatale."
            st.markdown(score_badge_custom(f"{sil_score}/10", sc), unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">→ {si}</div>', unsafe_allow_html=True)

        with st.expander("Glasgow detaille (Y/V/M)", expanded=False):
            st.markdown('<div class="score-title">Glasgow Coma Scale</div>', unsafe_allow_html=True)
            ca3,cb3,cc3=st.columns(3)
            with ca3:
                st.markdown("**Yeux (Y)**")
                ye=st.radio("Y",["4 - Spontanee","3 - Au bruit","2 - A la douleur","1 - Aucune"],key="gcs_y"); y_s=int(ye[0])
            with cb3:
                st.markdown("**Verbale (V)**")
                ve=st.radio("V",["5 - Orientee","4 - Confuse","3 - Mots inappropries","2 - Sons","1 - Aucune"],key="gcs_v"); v_s=int(ve[0])
            with cc3:
                st.markdown("**Motrice (M)**")
                me=st.radio("M",["6 - Obeit","5 - Localise","4 - Retrait","3 - Flexion","2 - Extension","1 - Aucune"],key="gcs_m"); m_s=int(me[0])
            gcs_calc=y_s+v_s+m_s
            st.session_state['gcs_y_score']=y_s; st.session_state['gcs_v_score']=v_s; st.session_state['gcs_m_score']=m_s
            if gcs_calc==15: gc,gi="score-info","Conscient."
            elif gcs_calc>=13: gc,gi="score-low","Alteration legere."
            elif gcs_calc>=9: gc,gi="score-med","Alteration moderee."
            else: gc,gi="score-high","COMA - protection VA urgente."
            st.markdown(score_badge_custom(f"GCS {gcs_calc}/15 (Y{y_s}V{v_s}M{m_s})", gc), unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">→ {gi}</div>', unsafe_allow_html=True)
            if abs(gcs_calc - gcs) > 1 if gcs else False:
                st.markdown(f'<div class="alert-warning">△ GCS calcule {gcs_calc} != GCS Signes Vitaux {gcs} - mettre a jour</div>', unsafe_allow_html=True)

        with st.expander("Score de Malinas - Accouchement imminent", expanded=False):
            st.markdown('<div class="score-title">Score de Malinas</div>', unsafe_allow_html=True)
            ca4,cb4=st.columns(2)
            with ca4:
                par=ca4.selectbox("Parite",["0 - Primipare","1 - Multipare"],key="mal_par")
                trav=ca4.selectbox("Duree travail",["0 - < 1h","1 - 1 a 3h","2 - > 3h"],key="mal_trav")
                cont=ca4.selectbox("Duree contractions",["0 - < 1min","1 - 1min","2 - > 1min"],key="mal_cont")
            with cb4:
                inter=cb4.selectbox("Intervalle contractions",["0 - > 5min","1 - 3 a 5min","2 - < 3min"],key="mal_int")
                poche=cb4.selectbox("Poche des eaux",["0 - Intacte","1 - Rompue"],key="mal_poche")
                push=cb4.selectbox("Envie de pousser",["0 - Absente","1 - Presente"],key="mal_pousser")
            mal_score=int(par[0])+int(trav[0])+int(cont[0])+int(inter[0])+int(poche[0])+int(push[0])
            if mal_score<=5: mc,mi="score-low","Transport possible."
            elif mal_score<=7: mc,mi="score-med","Transport rapide SMUR."
            elif mal_score<=9: mc,mi="score-med","Preparer accouchement sur place."
            else: mc,mi="score-high","NE PAS TRANSPORTER - accouchement imminent."
            st.markdown(score_badge_custom(f"{mal_score}/10", mc), unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">→ {mi}</div>', unsafe_allow_html=True)
            if mal_score >= 8:
                st.markdown('<div class="alert-danger">NE PAS TRANSPORTER - Activer protocole accouchement inopiné</div>', unsafe_allow_html=True)

        with st.expander("Score Brulure - Regle des 9 + Baux", expanded=False):
            st.markdown('<div class="score-title">Regle des 9 de Wallace + Indice de Baux</div>', unsafe_allow_html=True)
            age_br=st.number_input("Age patient",0,120,age,key="br_age")
            ca5,cb5,cc5=st.columns(3)
            with ca5:
                bt=st.number_input("Tete & cou %",0,9,0,key="br_t"); bta=st.number_input("Thorax ant %",0,9,0,key="br_ta")
                btp=st.number_input("Thorax post %",0,9,0,key="br_tp"); bab=st.number_input("Abdomen %",0,9,0,key="br_ab")
            with cb5:
                bmsd=st.number_input("MS droit %",0,9,0,key="br_msd"); bmsg=st.number_input("MS gauche %",0,9,0,key="br_msg")
                bmid=st.number_input("MI droit %",0,18,0,key="br_mid"); bmig=st.number_input("MI gauche %",0,18,0,key="br_mig")
            with cc5:
                bper=st.number_input("Perinee %",0,1,0,key="br_per")
                bprof=st.selectbox("Profondeur",["Superficielle","Intermediaire","Profonde"],key="br_prof")
                binh=st.checkbox("Inhalation suspectee",key="br_inh")
            scb=min(bt+bta+btp+bab+bmsd+bmsg+bmid+bmig+bper,100)
            baux=age_br+scb; baux_r=age_br+int(1.5*scb) if binh else baux
            profonde="Profonde" in bprof
            if scb>=50 or baux>=100: brc,brs="score-high","CRITIQUE - Centre brules + reanimation."
            elif scb>=20 or (profonde and scb>=10) or binh: brc,brs="score-high","GRAVE - Centre specialise."
            elif scb>=10 or profonde: brc,brs="score-med","MODEREE - Hospitalisation + plasticien."
            elif scb>=1: brc,brs="score-low","LEGERE - Ambulatoire possible."
            else: brc,brs="score-info","Aucune surface renseignee."
            cr1,cr2=st.columns(2)
            cr1.markdown(score_badge_custom(f"SCB {scb}%",brc),unsafe_allow_html=True)
            cr2.markdown(score_badge_custom(f"Baux {baux}",brc),unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">→ {brs}</div>',unsafe_allow_html=True)
            if binh: st.markdown(f'<div class="alert-warning">Baux revise (inhalation) : {baux_r}</div>',unsafe_allow_html=True)
            if scb>0:
                pds=st.number_input("Poids (kg)",10,200,70,key="br_pds")
                pk=4*pds*scb
                st.info(f"Parkland : {pk} mL RL / 24h | {pk//2} mL les 8 premieres heures | {pk//2} mL les 16h suivantes")

        with st.expander("Score BATT - Blast And Trauma Triage", expanded=False):
            st.markdown('<div class="score-title">BATT - Victimes explosion / traumatismes multiples</div>', unsafe_allow_html=True)
            ca6,cb6=st.columns(2)
            with ca6:
                bg=st.select_slider("GCS",list(range(3,16)),15,key="batt_gcs")
                bp=st.number_input("PAS",0,300,120,key="batt_pas")
                bfr=st.number_input("FR",0,60,16,key="batt_fr")
                bs=st.slider("SpO2",50,100,98,key="batt_spo2")
            with cb6:
                ba=st.checkbox("Amputation",key="batt_amp"); bth=st.checkbox("Thorax ouvert",key="batt_thor")
                bad=st.checkbox("Evisceration",key="batt_abdo"); bcr=st.checkbox("TC ouvert",key="batt_crane")
                bcu=st.checkbox("Crush syndrome",key="batt_crush"); bbu=st.checkbox("Brulures > 60%",key="batt_burns")
                bai=st.checkbox("Obstruction VA",key="batt_airways")
            bok=(bg>=10 and bp>=90 and 10<=bfr<=29 and bs>=90)
            blet=bcr or bbu; nbl=sum([ba,bth,bad,bcu,bai])
            if blet and not bok: bcat,bcc,bint="T4 DEPASSE","score-high","Soins palliatifs en catastrophe."
            elif not bok and nbl>=2: bcat,bcc,bint="T1 EXTREME URGENCE","score-high","SAUV immediat."
            elif not bok or nbl>=1: bcat,bcc,bint="T1 URGENCE ABSOLUE","score-high","Dechocage immediat."
            elif bok and nbl==0 and not blet: bcat,bcc,bint="T3 DIFFERE","score-low","Stable - surveillance."
            else: bcat,bcc,bint="T2 URGENCE RELATIVE","score-med","Reevaluation frequente."
            st.markdown(score_badge_custom(bcat,bcc),unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">→ {bint}</div>',unsafe_allow_html=True)

        # Recapitulatif
        st.markdown('<div class="section-header">Recapitulatif</div>', unsafe_allow_html=True)
        r1,r2,r3=st.columns(3)
        r1.metric("TIMI",f"{timi_score}/7"); r2.metric("Silverman",f"{sil_score}/10"); r3.metric("GCS calcule",f"{gcs_calc}/15")
        r1.metric("Malinas",f"{mal_score}/10"); r2.metric("SCB",f"{scb}%"); r3.metric("Baux",f"{baux}")


# =============================================================================
# POINT 5 : REEVALUATION STRUCTUREE (communes aux deux modes)
# =============================================================================
reeval_tab = t_reeval

with reeval_tab:
    st.markdown("### Reevaluations structurees")
    st.caption("Chaque reevaluation est comparee a la precedente. Tendance automatique.")

    # Saisie nouvelle reevaluation
    st.markdown('<div class="section-header">Nouvelle reevaluation</div>', unsafe_allow_html=True)
    cr1, cr2, cr3 = st.columns(3)
    re_temp = cr1.number_input("T° (C)", 30.0, 45.0, 37.0, 0.1, key="re_temp")
    re_fc   = cr1.number_input("FC (bpm)", 20, 220, 80, key="re_fc")
    re_pas  = cr2.number_input("PAS (mmHg)", 40, 260, 120, key="re_pas")
    re_spo2 = cr2.slider("SpO2 (%)", 50, 100, 98, key="re_spo2")
    re_fr   = cr3.number_input("FR (cpm)", 5, 60, 16, key="re_fr")
    re_gcs  = cr3.select_slider("GCS", list(range(3, 16)), 15, key="re_gcs")

    re_news2 = compute_news2(re_fr, re_spo2, supp_o2, re_temp, re_pas, re_fc, re_gcs, "BPCO" in atcd)
    re_label, re_css = news2_level(re_news2)

    re_motif = "Fievre"
    if st.session_state.patient_history:
        re_motif = st.session_state.patient_history[-1].get("motif", "Fievre")
    re_niveau, re_justif, re_ref = french_triage(re_motif, {}, re_fc, re_pas, re_spo2, re_fr, re_gcs, re_temp, age, re_news2)

    col_re1, col_re2 = st.columns(2)
    col_re1.markdown(f'<div class="news2-badge {re_css}">{re_label}</div>', unsafe_allow_html=True)
    col_re2.info(f"Triage recalcule : **{TRI_EMOJI[re_niveau]} {TRI_LABELS[re_niveau]}**")

    if st.button("Enregistrer cette reevaluation", use_container_width=True):
        snap = {
            "heure": datetime.now().strftime("%H:%M"),
            "fc": re_fc, "pas": re_pas, "spo2": re_spo2,
            "fr": re_fr, "gcs": re_gcs, "temp": re_temp,
            "niveau": re_niveau, "news2": re_news2,
        }
        st.session_state.reeval_history.append(snap)
        st.session_state.last_reeval = datetime.now()
        st.success(f"Reevaluation enregistree a {snap['heure']} - Tri {re_niveau}")

    # Affichage historique reevaluations avec tendance
    st.markdown('<div class="section-header">Historique des reevaluations</div>', unsafe_allow_html=True)

    if len(st.session_state.reeval_history) < 1:
        st.info("Aucune reevaluation enregistree. Enregistrez d'abord un patient.")
    else:
        # Tableau comparatif
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
            prev = history[i-1] if i > 0 else snap

            # Determiner si amelioration globale
            niveau_order = {"M":0,"1":1,"2":2,"3A":3,"3B":4,"4":5,"5":6}
            no = niveau_order.get(snap['niveau'],3); np_ = niveau_order.get(prev['niveau'],3)
            if no > np_:      row_css, tendance = "reeval-better", "AMELIORATION"
            elif no < np_:    row_css, tendance = "reeval-worse",  "AGGRAVATION"
            else:              row_css, tendance = "reeval-same",   "STABLE"

            label = f"H0" if i == 0 else f"H+{i}"
            st.markdown(
                f'<div class="reeval-row {row_css}">'
                f'<b>{snap["heure"]}</b> ({label}) | '
                f'Tri {TRI_EMOJI.get(snap["niveau"],"")}{snap["niveau"]} | '
                f'NEWS2 {snap["news2"]} | '
                f'FC {snap["fc"]} {trend(prev["fc"],snap["fc"])} | '
                f'PAS {snap["pas"]} {trend(prev["pas"],snap["pas"],False)} | '
                f'SpO2 {snap["spo2"]} {trend(prev["spo2"],snap["spo2"],False)} | '
                f'GCS {snap["gcs"]} {trend(prev["gcs"],snap["gcs"],False)} | '
                f'<b>{tendance}</b>'
                f'</div>',
                unsafe_allow_html=True
            )

        if len(history) >= 2:
            first = history[0]; last = history[-1]
            st.markdown(f"**Bilan global :** {len(history)} reevaluations | "
                        f"NEWS2 initial {first['news2']} → {last['news2']} | "
                        f"Tri {first['niveau']} → {last['niveau']}")

        if st.button("Effacer reevaluations"):
            st.session_state.reeval_history = []
            st.rerun()


# =============================================================================
# HISTORIQUE
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
            st.markdown(
                f'<div class="hist-row {css}">'
                f'<b>{pat["heure"]}</b> | {pat["age"]} ans | <b>{pat["motif"]}</b> | '
                f'EVA {pat["eva"]}/10 | NEWS2 {pat["news2"]} | {em} Tri {pat["niveau"]}{tag}'
                f'</div>', unsafe_allow_html=True
            )
            with st.expander(f"SBAR - Patient #{len(st.session_state.patient_history)-i+1}"):
                st.markdown(f'<div class="sbar-block">{pat["sbar"]}</div>', unsafe_allow_html=True)
                st.download_button("Telecharger SBAR", data=pat["sbar"],
                    file_name=f"SBAR_{pat['heure'].replace(':','h')}_Tri{pat['niveau']}.txt",
                    mime="text/plain", key=f"dl_{i}")
        if st.button("Effacer l'historique"):
            st.session_state.patient_history = []
            st.rerun()