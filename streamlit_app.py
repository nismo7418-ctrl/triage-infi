import streamlit as st
from datetime import datetime

# --- CONFIGURATION ------------------------------------------------------------
st.set_page_config(
    page_title="IAO Expert Pro v9.0 -- FRENCH Triage SFMU + Scores",
    page_icon="⚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THEME --------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
.stApp { background-color: #0a0f1e; color: #e2e8f0; }
[data-testid='stSidebar'] { background-color: #0f172a; border-right: 1px solid #1e3a5f; }

.section-header {
    font-family: 'IBM Plex Mono', monospace;
    color: #38bdf8; font-weight: 600; font-size: 0.75rem;
    letter-spacing: 0.12em; text-transform: uppercase;
    border-bottom: 1px solid #1e3a5f;
    padding-bottom: 6px; margin: 16px 0 12px 0;
}

/* FRENCH Triage level badges */
.tri-badge {
    display:inline-block; font-family:'IBM Plex Mono',monospace;
    font-size:1.6rem; font-weight:600; padding:10px 24px;
    border-radius:8px; margin-bottom:6px;
}
.tri-M  { background:#1a0030; color:#e879f9; border:2px solid #a855f7; animation: pulse 0.8s infinite; }
.tri-1  { background:#450a0a; color:#fca5a5; border:2px solid #ef4444; animation: pulse 1s infinite; }
.tri-2  { background:#431407; color:#fdba74; border:2px solid #f97316; }
.tri-3A { background:#3b1a00; color:#fde68a; border:2px solid #f59e0b; }
.tri-3B { background:#422006; color:#fef08a; border:2px solid #eab308; }
.tri-4  { background:#052e16; color:#86efac; border:2px solid #22c55e; }
.tri-5  { background:#0c1a2e; color:#93c5fd; border:2px solid #3b82f6; }

@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.55} }

.triage-box {
    border-radius:12px; padding:28px; text-align:center;
    font-family:'IBM Plex Mono',monospace; margin-bottom:16px;
}
.box-M  { background:linear-gradient(135deg,#1a0030,#3b0764); border:2px solid #a855f7; }
.box-1  { background:linear-gradient(135deg,#450a0a,#7f1d1d); border:2px solid #ef4444; }
.box-2  { background:linear-gradient(135deg,#431407,#7c2d12); border:2px solid #f97316; }
.box-3A { background:linear-gradient(135deg,#3b1a00,#78350f); border:2px solid #f59e0b; }
.box-3B { background:linear-gradient(135deg,#422006,#713f12); border:2px solid #eab308; }
.box-4  { background:linear-gradient(135deg,#052e16,#14532d); border:2px solid #22c55e; }
.box-5  { background:linear-gradient(135deg,#0c1a2e,#1e3a5f); border:2px solid #3b82f6; }

.news2-badge {
    display:inline-block; font-family:'IBM Plex Mono',monospace;
    font-size:1.8rem; font-weight:600; padding:8px 20px; border-radius:8px; margin-bottom:6px;
}
.news2-low  { background:#14532d; color:#86efac; }
.news2-med  { background:#713f12; color:#fde68a; }
.news2-high { background:#7f1d1d; color:#fca5a5; }
.news2-crit { background:#4c0519; color:#f9a8d4; animation: pulse 1s infinite; }

.vital-alert {
    font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
    padding:2px 6px; border-radius:4px; margin-left:6px; vertical-align:middle;
}
.vital-warn { background:#422006; color:#fbbf24; }
.vital-crit { background:#450a0a; color:#f87171; }
.vital-ok   { background:#052e16; color:#4ade80; }

.hist-row {
    background:#0f172a; border:1px solid #1e3a5f; border-radius:8px;
    padding:10px 14px; margin-bottom:6px; font-size:0.85rem;
}
.hist-M  { border-left:4px solid #a855f7; }
.hist-1  { border-left:4px solid #ef4444; }
.hist-2  { border-left:4px solid #f97316; }
.hist-3A { border-left:4px solid #f59e0b; }
.hist-3B { border-left:4px solid #eab308; }
.hist-4  { border-left:4px solid #22c55e; }
.hist-5  { border-left:4px solid #3b82f6; }

.chrono {
    font-family:'IBM Plex Mono',monospace; font-size:2.4rem; font-weight:600;
    color:#38bdf8; text-align:center; letter-spacing:0.05em;
}
.chrono-label { font-size:0.7rem; color:#64748b; text-align:center; letter-spacing:0.1em; text-transform:uppercase; }

.sbar-block {
    background:#020617; border:1px solid #1e3a5f; border-radius:10px; padding:18px;
    font-family:'IBM Plex Mono',monospace; font-size:0.82rem; line-height:1.8;
    white-space:pre-wrap; color:#cbd5e1;
}
.legal-text { font-size:0.72rem; color:#475569; font-style:italic; margin-top:8px; }
.signature  { color:#38bdf8; font-weight:600; font-size:0.85rem; border-top:1px solid #1e3a5f; padding-top:10px; margin-top:12px; }

.french-ref {
    background:#0f172a; border:1px solid #1e3a5f; border-left:4px solid #38bdf8;
    border-radius:6px; padding:10px 14px; font-size:0.8rem; color:#94a3b8;
    margin-top:10px; font-family:'IBM Plex Mono',monospace;
}

/* -- SCORING TAB -- */
.score-card {
    background:#0f172a; border:1px solid #1e3a5f; border-radius:12px;
    padding:20px; margin-bottom:16px;
}
.score-title {
    font-family:'IBM Plex Mono',monospace; font-size:0.7rem; font-weight:600;
    letter-spacing:0.14em; text-transform:uppercase; color:#38bdf8;
    border-bottom:1px solid #1e3a5f; padding-bottom:6px; margin-bottom:14px;
}
.score-result {
    display:inline-block; font-family:'IBM Plex Mono',monospace;
    font-size:2rem; font-weight:600; padding:8px 22px;
    border-radius:8px; margin:10px 0 4px 0;
}
.score-low    { background:#052e16; color:#86efac; border:1px solid #16a34a; }
.score-med    { background:#422006; color:#fde68a; border:1px solid #ca8a04; }
.score-high   { background:#450a0a; color:#fca5a5; border:1px solid #dc2626; }
.score-info   { background:#0c1a2e; color:#93c5fd; border:1px solid #2563eb; }
.score-interp {
    font-size:0.85rem; color:#94a3b8; margin-top:6px; line-height:1.6;
    font-style:italic;
}
.score-row {
    display:flex; justify-content:space-between; align-items:center;
    border-bottom:1px solid #1e3a5f; padding:5px 0; font-size:0.85rem;
}
.score-row:last-child { border-bottom:none; }
.score-row-label { color:#94a3b8; }
.score-row-val   { font-family:'IBM Plex Mono',monospace; color:#e2e8f0; font-weight:600; }
.criterion-ok  { color:#4ade80; }
.criterion-no  { color:#475569; }
</style>
""", unsafe_allow_html=True)


# --- SESSION STATE ------------------------------------------------------------
if 'patient_history' not in st.session_state:
    st.session_state.patient_history = []
if 'arrival_time' not in st.session_state:
    st.session_state.arrival_time = None
if 'sbar_text' not in st.session_state:
    st.session_state.sbar_text = ""


# ===============================================================================
# FRENCH TRIAGE SFMU -- MOTEURS DE DÉCISION (V1.1 Juin 2018)
# Niveaux : M (immédiat), 1, 2, 3A, 3B, 4, 5
# ===============================================================================

TRI_LABELS = {
    "M":  "TRI M -- IMMÉDIAT (Réanimation)",
    "1":  "TRI 1 -- URGENCE EXTRÊME",
    "2":  "TRI 2 -- TRÈS URGENT",
    "3A": "TRI 3A -- URGENT",
    "3B": "TRI 3B -- URGENT DIFFÉRÉ",
    "4":  "TRI 4 -- MOINS URGENT",
    "5":  "TRI 5 -- NON URGENT",
}

TRI_SECTORS = {
    "M":  "SAUV -- Salle d'Urgences Vitales (réanimation immédiate)",
    "1":  "SAUV -- Prise en charge immédiate",
    "2":  "Secteur Lourd -- Médecin dans les 20 min",
    "3A": "Secteur Lourd -- Médecin dans les 30 min",
    "3B": "Secteur Intermédiaire -- Médecin dans l'heure",
    "4":  "Secteur Ambulatoire -- Médecin dans les 2h",
    "5":  "Zone d'attente -- Consultation ou réorientation",
}

TRI_BOX_CSS = {
    "M": "box-M", "1": "box-1", "2": "box-2",
    "3A": "box-3A", "3B": "box-3B", "4": "box-4", "5": "box-5",
}

TRI_HIST_CSS = {
    "M": "hist-M", "1": "hist-1", "2": "hist-2",
    "3A": "hist-3A", "3B": "hist-3B", "4": "hist-4", "5": "hist-5",
}

TRI_EMOJI = {
    "M": "🟣", "1": "🔴", "2": "🟠", "3A": "🟡", "3B": "🟡", "4": "🟢", "5": "🔵",
}


def french_triage(motif, details, fc, pas, spo2, fr, gcs, temp, age, news2_score):
    """
    Moteur de triage FRENCH (SFMU V1.1 2018).
    Retourne (niveau: str, justification: str, critere_ref: str)
    """

    # -- Sécurité globale NEWS2 ----------------------------------------------
    if news2_score >= 9:
        return "M", "Score NEWS2 ≥ 9 : engagement vital immédiat.", "NEWS2 ≥ 9 → Tri M"

    # ==========================================================================
    # CARDIO-CIRCULATOIRE
    # ==========================================================================
    if motif == "Arrêt cardiorespiratoire":
        return "M", "Arrêt cardiorespiratoire -- réanimation immédiate.", "FRENCH Cardio · Tri M"

    if motif == "Hypotension artérielle":
        if pas <= 70:
            return "1", f"PAS ≤ 70 mmHg ({pas} mmHg) -- choc.", "FRENCH Cardio · Tri 1 : PAS ≤ 70"
        if pas <= 90 or (pas <= 100 and fc > 100):
            return "2", f"PAS ≤ 90 mmHg ou PAS ≤ 100 + FC > 100 ({pas}/{fc}).", "FRENCH Cardio · Tri 2"
        if 90 < pas <= 100 and fc <= 100:
            return "3B", f"PAS {pas} mmHg, FC ≤ 100.", "FRENCH Cardio · Tri 3B"
        return "4", "Tension dans les limites.", "FRENCH Cardio · Tri 4"

    if motif == "Douleur thoracique / SCA":
        ecg = details.get("ecg", "Normal")
        douleur_type = details.get("douleur_type", "Atypique")
        comorbidites = details.get("comorbidites_coronaires", False)
        if ecg == "Anormal typique SCA":
            return "1", "ECG anormal typique de SCA -- activation filière coronaire.", "FRENCH Cardio · Tri 1"
        if ecg == "Anormal non typique" or (ecg == "Normal" and douleur_type == "Typique persistante/intense"):
            return "2", "ECG anormal non typique ou douleur typique persistante/intense.", "FRENCH Cardio · Tri 2"
        if ecg == "Normal" and comorbidites:
            return "3A", "ECG normal mais comorbidités coronaires (ATCD, FdR).", "FRENCH Cardio · Tri 3A"
        if ecg == "Normal" and douleur_type == "Type coronaire":
            return "3B", "ECG normal, douleur de type coronaire.", "FRENCH Cardio · Tri 3B"
        return "4", "ECG normal, douleur atypique.", "FRENCH Cardio · Tri 4"

    if motif == "Tachycardie / tachyarythmie":
        if fc >= 180:
            return "1", f"FC ≥ 180 bpm ({fc}).", "FRENCH Cardio · Tri 1"
        if fc >= 130:
            return "2", f"FC ≥ 130 bpm ({fc}).", "FRENCH Cardio · Tri 2"
        if fc > 110:
            return "3B", f"FC > 110 bpm ({fc}).", "FRENCH Cardio · Tri 3B"
        return "4", "Épisode résolutif / FC ≤ 110.", "FRENCH Cardio · Tri 4"

    if motif == "Bradycardie / bradyarythmie":
        mauvaise_tolerance = details.get("mauvaise_tolerance", False)
        if fc <= 40:
            return "1", f"FC ≤ 40 bpm ({fc}).", "FRENCH Cardio · Tri 1"
        if 40 < fc <= 50 and mauvaise_tolerance:
            return "2", f"FC 40–50 avec mauvaise tolérance ({fc}).", "FRENCH Cardio · Tri 2"
        if 40 < fc <= 50 and not mauvaise_tolerance:
            return "3B", f"FC 40–50 sans mauvaise tolérance ({fc}).", "FRENCH Cardio · Tri 3B"
        return "4", "Bradycardie bien tolérée.", "FRENCH Cardio · Tri 4"

    if motif == "Hypertension artérielle":
        sf_associes = details.get("sf_associes", False)
        if pas >= 220 or (pas >= 180 and sf_associes):
            return "2", f"PAS ≥ 220 ou ≥ 180 + SF ({pas} mmHg).", "FRENCH Cardio · Tri 2"
        if pas >= 180 and not sf_associes:
            return "3B", f"PAS ≥ 180 sans SF ({pas} mmHg).", "FRENCH Cardio · Tri 3B"
        return "4", f"PAS < 180 mmHg ({pas}).", "FRENCH Cardio · Tri 4"

    if motif == "Dyspnée / insuffisance respiratoire":
        if fr >= 40 or spo2 < 86:
            return "1", f"Détresse respiratoire -- FR {fr} cpm / SpO2 {spo2}%.", "FRENCH Cardio · Tri 1"
        if details.get("parole") == "Mots isolés" or details.get("tirage") or details.get("orthopnee") or (30 <= fr < 40) or (86 <= spo2 <= 90):
            return "2", "Dyspnée à la parole / tirage / orthopnée ou FR 30-40 / SpO2 86-90%.", "FRENCH Cardio · Tri 2"
        if fr < 30 and spo2 > 90:
            return "3B", "Dyspnée modérée, FR < 30, SpO2 > 90%.", "FRENCH Cardio · Tri 3B"
        return "4", "Dyspnée légère, paramètres stables.", "FRENCH Cardio · Tri 4"

    if motif == "Palpitations":
        malaise_assoc = details.get("malaise", False)
        if fc >= 180:
            return "2", f"Palpitations + FC ≥ 180 ({fc}).", "FRENCH Cardio · Tri 2"
        if fc >= 130:
            return "2", f"Palpitations + FC ≥ 130 ({fc}).", "FRENCH Cardio · Tri 2"
        if malaise_assoc or fc > 110:
            return "3B", "Palpitations + malaise ou FC > 110.", "FRENCH Cardio · Tri 3B"
        return "4", "Palpitations isolées, FC ≤ 110.", "FRENCH Cardio · Tri 4"

    # ==========================================================================
    # RESPIRATOIRE
    # ==========================================================================
    if motif == "Asthme / aggravation BPCO":
        dep = details.get("dep", 999)
        if fr >= 40 or spo2 < 86:
            return "1", f"Détresse respiratoire -- FR {fr} / SpO2 {spo2}%.", "FRENCH Respi · Tri 1"
        if dep <= 200 or details.get("parole") == "Mots isolés" or details.get("tirage") or details.get("orthopnee"):
            return "2", f"DEP ≤ 200 ou dyspnée à la parole/tirage/orthopnée.", "FRENCH Respi · Tri 2"
        if dep >= 300:
            return "4", f"DEP ≥ 300 l/min, asthme contrôlé.", "FRENCH Respi · Tri 4"
        return "3B", "Asthme modéré stable.", "FRENCH Respi · Tri 3B"

    if motif == "Hémoptysie":
        if fr >= 40 or spo2 < 86:
            return "1", "Détresse respiratoire sur hémoptysie.", "FRENCH Respi · Tri 1"
        if details.get("hemoptysie_abondante") or details.get("repetee"):
            return "2", "Hémoptysie répétée ou abondante.", "FRENCH Respi · Tri 2"
        return "3B", "Hémoptysie modérée.", "FRENCH Respi · Tri 3B"

    if motif == "Corps étranger voies aériennes":
        if fr >= 40 or spo2 < 86:
            return "1", "Détresse respiratoire sur corps étranger.", "FRENCH Respi · Tri 1"
        if details.get("parole") == "Mots isolés" or details.get("tirage"):
            return "2", "Dyspnée à la parole / tirage.", "FRENCH Respi · Tri 2"
        if age <= 2:
            return "3A", "Enfant ≤ 2 ans -- surveillance prioritaire.", "FRENCH Respi · Tri 3A"
        if not details.get("dyspnee"):
            return "3B", "Corps étranger sans dyspnée.", "FRENCH Respi · Tri 3B"
        return "3B", "Corps étranger voies aériennes.", "FRENCH Respi · Tri 3B"

    # ==========================================================================
    # NEUROLOGIE
    # ==========================================================================
    if motif == "AVC / Déficit neurologique":
        delai_h = details.get("delai_heures", 999)
        if delai_h <= 4.5:
            return "1", f"Déficit neurologique aigu ≤ 4h30 -- filière thrombolyse.", "FRENCH Neuro · Tri 1"
        if delai_h >= 24:
            return "3B", "Déficit neurologique > 24h.", "FRENCH Neuro · Tri 3B"
        return "2", "Déficit neurologique, délai > 4h30.", "FRENCH Neuro · Tri 2"

    if motif == "Altération de conscience / Coma":
        if gcs <= 8:
            return "1", f"GCS ≤ 8 ({gcs}) -- coma.", "FRENCH Neuro · Tri 1"
        if 9 <= gcs <= 13:
            return "2", f"GCS 9–13 ({gcs}).", "FRENCH Neuro · Tri 2"
        return "3B", "Altération légère de conscience.", "FRENCH Neuro · Tri 3B"

    if motif == "Convulsions":
        if details.get("crises_multiples") or details.get("en_cours") or details.get("confusion_post_critique") or details.get("deficit_post_critique") or temp >= 38.5:
            return "2", "Crise en cours / multiple / confusion ou fièvre associée.", "FRENCH Neuro · Tri 2"
        return "3B", "Récupération complète post-critique.", "FRENCH Neuro · Tri 3B"

    if motif == "Céphalée":
        if details.get("inhabituelle") or details.get("brutale") or details.get("fievre_assoc") or temp >= 38.5:
            return "2", "Céphalée inhabituelle / brutale / fébrile.", "FRENCH Neuro · Tri 2"
        return "3B", "Céphalée habituelle / migraine connue.", "FRENCH Neuro · Tri 3B"

    if motif == "Vertiges / trouble de l'équilibre":
        if details.get("signes_neuro") or details.get("cephalee_brutale"):
            return "2", "Vertiges + signes neurologiques ou céphalée brutale.", "FRENCH Neuro · Tri 2"
        return "5", "Troubles anciens et stables.", "FRENCH Neuro · Tri 5"

    if motif == "Confusion / désorientation":
        if temp >= 38.5:
            return "2", "Confusion + fièvre.", "FRENCH Neuro · Tri 2"
        return "3B", "Confusion sans fièvre.", "FRENCH Neuro · Tri 3B"

    # ==========================================================================
    # ABDOMINAL
    # ==========================================================================
    if motif == "Hématémèse / vomissement de sang":
        if details.get("abondante"):
            return "2", "Hématémèse abondante.", "FRENCH Abdo · Tri 2"
        return "3B", "Vomissements striés de sang.", "FRENCH Abdo · Tri 3B"

    if motif == "Rectorragie / méléna":
        if details.get("abondante"):
            return "2", "Rectorragie abondante.", "FRENCH Abdo · Tri 2"
        return "3B", "Selles souillées de sang.", "FRENCH Abdo · Tri 3B"

    if motif == "Douleur abdominale":
        if details.get("defense") or details.get("contracture") or details.get("mauvaise_tolerance"):
            return "2", "Douleur sévère et/ou mauvaise tolérance / défense.", "FRENCH Abdo · Tri 2"
        if details.get("regressive") or not details.get("douleur_presente", True):
            return "5", "Douleur régressive / indolore.", "FRENCH Abdo · Tri 5"
        return "3B", "Douleur abdominale modérée.", "FRENCH Abdo · Tri 3B"

    # ==========================================================================
    # GÉNITO-URINAIRE
    # ==========================================================================
    if motif == "Douleur lombaire / colique néphrétique":
        if details.get("intense"):
            return "2", "Douleur lombaire intense.", "FRENCH GU · Tri 2"
        if details.get("regressive"):
            return "5", "Douleur régressive / indolore.", "FRENCH GU · Tri 5"
        return "3B", "Douleur lombaire modérée.", "FRENCH GU · Tri 3B"

    if motif == "Rétention d'urine / anurie":
        return "2", "Rétention d'urine -- douleur intense / agitation.", "FRENCH GU · Tri 2"

    if motif == "Douleur testiculaire / torsion":
        if details.get("intense") or details.get("suspicion_torsion"):
            return "2", "Douleur intense ou suspicion de torsion testiculaire.", "FRENCH GU · Tri 2"
        return "3B", "Avis référent requis.", "FRENCH GU · Tri 3B"

    if motif == "Hématurie":
        if details.get("abondante_active"):
            return "2", "Hématurie -- saignement abondant actif.", "FRENCH GU · Tri 2"
        return "3B", "Hématurie modérée.", "FRENCH GU · Tri 3B"

    # ==========================================================================
    # TRAUMATOLOGIE
    # ==========================================================================
    if motif == "Traumatisme avec amputation":
        return "M", "Amputation traumatique -- prise en charge immédiate.", "FRENCH Trauma · Tri M"

    if motif == "Traumatisme abdomen / thorax / cervical":
        if details.get("penetrant"):
            return "1", "Traumatisme pénétrant.", "FRENCH Trauma · Tri 1"
        if details.get("cinetique") == "Haute" and details.get("mauvaise_tolerance"):
            return "2", "Haute vélocité.", "FRENCH Trauma · Tri 2"
        if details.get("cinetique") == "Faible" and details.get("mauvaise_tolerance"):
            return "3B", "Faible vélocité + mauvaise tolérance.", "FRENCH Trauma · Tri 3B"
        return "4", "Faible vélocité, bonne tolérance / gêne limitée.", "FRENCH Trauma · Tri 4"

    if motif == "Traumatisme crânien":
        if gcs <= 8:
            return "1", f"TC avec coma GCS ≤ 8 ({gcs}).", "FRENCH Trauma · Tri 1"
        if 9 <= gcs <= 13 or details.get("deficit_neuro") or details.get("convulsion") or details.get("aod_avk") or details.get("vomissements_repetes"):
            return "2", "GCS 9–13 / déficit neuro / convulsion / AOD-AVK / vomissements répétés.", "FRENCH Trauma · Tri 2"
        if details.get("pdc") or details.get("plaie") or details.get("hematome"):
            return "3B", "PDC, plaie ou hématome crânien.", "FRENCH Trauma · Tri 3B"
        return "5", "TC sans signe de gravité.", "FRENCH Trauma · Tri 5"

    if motif == "Brûlure":
        if details.get("etendue") or details.get("main_visage"):
            return "2", "Brûlure étendue ou main/visage.", "FRENCH Trauma · Tri 2"
        if age <= 2:
            return "3A", "Enfant ≤ 24 mois, brûlure même peu étendue.", "FRENCH Trauma · Tri 3A"
        return "3B", "Avis référent (MAO, MCO).", "FRENCH Trauma · Tri 3B"

    if motif == "Traumatisme bassin / hanche / fémur / rachis":
        if details.get("cinetique") == "Haute":
            return "2", "Haute vélocité.", "FRENCH Trauma · Tri 2"
        if details.get("mauvaise_tolerance"):
            return "3B", "Faible vélocité + mauvaise tolérance.", "FRENCH Trauma · Tri 3B"
        return "4", "Faible vélocité, bonne tolérance.", "FRENCH Trauma · Tri 4"

    if motif == "Traumatisme membre / épaule":
        if details.get("cinetique") == "Haute" or details.get("ischemie"):
            return "2", "Haute vélocité / ischémie.", "FRENCH Trauma · Tri 2"
        if details.get("impotence_totale") or details.get("deformation"):
            return "3B", "Impotence totale / déformation.", "FRENCH Trauma · Tri 3B"
        if details.get("impotence_moderee") or details.get("petite_deformation"):
            return "4", "Impotence modérée / petite déformation.", "FRENCH Trauma · Tri 4"
        return "5", "Ni impotence, ni déformation.", "FRENCH Trauma · Tri 5"

    if motif == "Plaie":
        if details.get("delabrant") or details.get("saignement_actif"):
            return "2", "Plaie délabrante / saignement actif.", "FRENCH Trauma · Tri 2"
        if details.get("large_complexe") or details.get("main"):
            return "3B", "Plaie large / complexe / main.", "FRENCH Trauma · Tri 3B"
        if details.get("superficielle"):
            return "4", "Plaie superficielle.", "FRENCH Trauma · Tri 4"
        return "5", "Excoriation.", "FRENCH Trauma · Tri 5"

    if motif == "Électrisation":
        if details.get("pdc") or details.get("brulure_grave") or details.get("foudre"):
            return "2", "PDC / brûlure / foudroiement.", "FRENCH Trauma · Tri 2"
        if details.get("haute_tension") or details.get("contact_long"):
            return "3B", "Haute tension / contact prolongé.", "FRENCH Trauma · Tri 3B"
        return "4", "Courant domestique, bonne tolérance.", "FRENCH Trauma · Tri 4"

    if motif == "Agression sexuelle / sévices":
        return "1", "Agression sexuelle -- prise en charge médicale et médico-légale.", "FRENCH Trauma · Tri 1"

    # ==========================================================================
    # NEUROLOGIE -- PSYCHIATRIE
    # ==========================================================================
    if motif == "Idée / comportement suicidaire":
        return "1", "Comportement suicidaire -- évaluation psychiatrique urgente.", "FRENCH Psy · Tri 1"

    if motif == "Troubles du comportement / psychiatrie":
        if details.get("agitation") or details.get("violence") or details.get("hallucinations"):
            return "2", "Agitation / violence / hallucinations.", "FRENCH Psy · Tri 2"
        if age <= 18:
            return "3A", "Enfant / adolescent.", "FRENCH Psy · Tri 3A"
        return "4", "Consultation psychiatrique.", "FRENCH Psy · Tri 4"

    # ==========================================================================
    # INTOXICATIONS
    # ==========================================================================
    if motif == "Intoxication médicamenteuse":
        if details.get("mauvaise_tolerance") or details.get("intention_suicidaire") or details.get("cardiotropes"):
            return "2", "Mauvaise tolérance / intention suicidaire / toxiques cardiotropes.", "FRENCH Intox · Tri 2"
        if age <= 18:
            return "3A", "Enfant.", "FRENCH Intox · Tri 3A"
        return "3B", "Avis référent.", "FRENCH Intox · Tri 3B"

    if motif == "Intoxication non médicamenteuse":
        if details.get("mauvaise_tolerance") or details.get("lesionnels"):
            return "2", "Mauvaise tolérance / toxiques lésionnels.", "FRENCH Intox · Tri 2"
        if age <= 18:
            return "3A", "Enfant.", "FRENCH Intox · Tri 3A"
        return "3B", "Avis référent.", "FRENCH Intox · Tri 3B"

    # ==========================================================================
    # INFECTIOLOGIE / FIÈVRE
    # ==========================================================================
    if motif == "Fièvre":
        if temp >= 40 or temp <= 35.2 or details.get("confusion") or details.get("cephalee") or details.get("purpura"):
            return "2", f"T° {temp}°C ou signes de gravité (confusion/céphalée/purpura).", "FRENCH Infectio · Tri 2"
        if details.get("mauvaise_tolerance") or pas < 100:
            return "3B", "Mauvaise tolérance / hypotension.", "FRENCH Infectio · Tri 3B"
        return "5", "Fièvre bien tolérée.", "FRENCH Infectio · Tri 5"

    # ==========================================================================
    # GYNÉCO-OBSTÉTRIQUE
    # ==========================================================================
    if motif == "Accouchement imminent":
        return "M", "Accouchement imminent ou réalisé -- urgence absolue.", "FRENCH Gynéco · Tri M"

    if motif == "Problème de grossesse (1er/2ème trimestre)":
        return "3A", "Problème de grossesse T1/T2 -- métrorragies / douleur.", "FRENCH Gynéco · Tri 3A"

    if motif == "Problème de grossesse (3ème trimestre)":
        return "3A", "Grossesse T3 -- métrorragies / douleur / HTA / perte de liquide.", "FRENCH Gynéco · Tri 3A"

    if motif == "Méno-métrorragie":
        if details.get("grossesse") or details.get("abondante"):
            return "2", "Grossesse connue/suspectée ou saignement abondant.", "FRENCH Gynéco · Tri 2"
        return "3B", "Métrorragie modérée.", "FRENCH Gynéco · Tri 3B"

    # ==========================================================================
    # DIVERS MÉTABOLIQUES
    # ==========================================================================
    if motif == "Hyperglycémie":
        glyc = details.get("glycemie", 0)
        if details.get("cetose_elevee") or gcs < 15:
            return "2", "Cétose élevée / trouble de conscience.", "FRENCH Divers · Tri 2"
        if glyc >= 20 or details.get("cetose_positive"):
            return "3B", f"Glycémie ≥ 20 mmol/L ou cétose positive ({glyc}).", "FRENCH Divers · Tri 3B"
        return "4", "Hyperglycémie modérée.", "FRENCH Divers · Tri 4"

    if motif == "Hypoglycémie":
        if gcs <= 8:
            return "1", f"Hypoglycémie avec coma GCS {gcs}.", "FRENCH Divers · Tri 1"
        if gcs <= 13 or details.get("mauvaise_tolerance"):
            return "2", "Mauvaise tolérance / GCS 9-13.", "FRENCH Divers · Tri 2"
        return "3B", "Hypoglycémie modérée.", "FRENCH Divers · Tri 3B"

    if motif == "Hypothermie":
        if temp <= 32:
            return "1", f"T° ≤ 32°C ({temp}°C) -- hypothermie sévère.", "FRENCH Divers · Tri 1"
        if temp <= 35.2:
            return "2", f"T° 32–35.2°C ({temp}°C) -- hypothermie modérée.", "FRENCH Divers · Tri 2"
        return "3B", "Hypothermie légère.", "FRENCH Divers · Tri 3B"

    if motif == "Coup de chaleur / insolation":
        if gcs <= 8:
            return "1", f"Coup de chaleur avec coma GCS {gcs}.", "FRENCH Divers · Tri 1"
        if temp >= 40:
            return "2", f"T° ≥ 40°C ({temp}°C) / GCS 9-13.", "FRENCH Divers · Tri 2"
        return "3B", "Coup de chaleur léger.", "FRENCH Divers · Tri 3B"

    if motif == "Allergie / anaphylaxie":
        if details.get("dyspnee") or details.get("obstruction") or details.get("mauvaise_tolerance"):
            return "2", "Dyspnée / risque obstruction / mauvaise tolérance.", "FRENCH Divers · Tri 2"
        return "4", "Réaction allergique légère.", "FRENCH Divers · Tri 4"

    # ==========================================================================
    # ORL / OPHTALMO / PEAU
    # ==========================================================================
    if motif == "Épistaxis":
        if details.get("abondant_actif"):
            return "2", "Épistaxis abondant actif.", "FRENCH ORL · Tri 2"
        if details.get("abondant_resolutif"):
            return "3B", "Épistaxis abondant résolutif.", "FRENCH ORL · Tri 3B"
        return "5", "Épistaxis peu abondant résolutif.", "FRENCH ORL · Tri 5"

    if motif == "Corps étranger / brûlure oculaire":
        if details.get("intense") or details.get("chimique"):
            return "2", "Brûlure chimique / douleur intense.", "FRENCH Ophtalmo · Tri 2"
        return "3B", "Avis référent.", "FRENCH Ophtalmo · Tri 3B"

    if motif == "Trouble visuel / cécité":
        if details.get("brutal"):
            return "2", "Trouble visuel à début brutal.", "FRENCH Ophtalmo · Tri 2"
        return "3B", "Avis référent.", "FRENCH Ophtalmo · Tri 3B"

    # ==========================================================================
    # FALLBACK -- non classé → tri minimum par NEWS2 / EVA
    # ==========================================================================
    eva = details.get("eva", 0)
    if news2_score >= 5 or gcs < 15:
        return "2", f"Paramètres vitaux préoccupants (NEWS2={news2_score}, GCS={gcs}).", "NEWS2/GCS"
    if news2_score >= 1 or eva >= 7:
        return "3B", f"Douleur intense (EVA={eva}) ou NEWS2 anormal ({news2_score}).", "NEWS2/EVA"
    if eva >= 4:
        return "4", f"EVA {eva}/10, paramètres stables.", "EVA"
    return "5", "Motif non urgent, paramètres normaux.", "Défaut"


# --- NEWS2 --------------------------------------------------------------------
def compute_news2(fr, spo2, supp_o2, temp, pas, fc, gcs, bpco):
    s = 0
    s += 3 if fr <= 8 else (1 if fr <= 11 else (0 if fr <= 20 else (2 if fr <= 24 else 3)))
    if not bpco:
        s += 3 if spo2 <= 91 else (2 if spo2 <= 93 else (1 if spo2 <= 95 else 0))
    else:
        s += (3 if spo2 <= 83 else (2 if spo2 <= 85 else (1 if spo2 <= 87 else
              (0 if spo2 <= 92 else (1 if spo2 <= 94 else (2 if spo2 <= 96 else 3))))))
    if supp_o2: s += 2
    s += 3 if temp <= 35.0 else (1 if temp <= 36.0 else (0 if temp <= 38.0 else (1 if temp <= 39.0 else 2)))
    s += 3 if pas <= 90 else (2 if pas <= 100 else (1 if pas <= 110 else (0 if pas <= 219 else 3)))
    s += 3 if fc <= 40 else (1 if fc <= 50 else (0 if fc <= 90 else (1 if fc <= 110 else (2 if fc <= 130 else 3))))
    if gcs < 15: s += 3
    return s


def news2_level(score):
    if score == 0:   return "Faible (0)", "news2-low"
    if score <= 4:   return f"Faible ({score})", "news2-low"
    if score <= 6:   return f"Modéré ({score})", "news2-med"
    if score <= 8:   return f"Élevé ({score})", "news2-high"
    return f"CRITIQUE ({score})", "news2-crit"


def vital_badge(val, lw, lc, hw, hc, u=""):
    if val <= lc or val >= hc:
        return f'<span class="vital-alert vital-crit">⚠ {val}{u}</span>'
    if val <= lw or val >= hw:
        return f'<span class="vital-alert vital-warn">△ {val}{u}</span>'
    return f'<span class="vital-alert vital-ok">✓</span>'


# --- SIDEBAR ------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚕ IAO Expert Pro v9.0")
    st.caption("FRENCH Triage SFMU V1.1 · 2018")

    st.markdown('<div class="section-header">Prise en charge</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    if col_a.button("▶ Démarrer", use_container_width=True):
        st.session_state.arrival_time = datetime.now()
    if col_b.button("✕ Reset", use_container_width=True):
        st.session_state.arrival_time = None

    if st.session_state.arrival_time:
        elapsed = datetime.now() - st.session_state.arrival_time
        mins, secs = divmod(int(elapsed.total_seconds()), 60)
        hrs, mins = divmod(mins, 60)
        st.markdown(f'<div class="chrono">{hrs:02d}:{mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chrono-label">Arrivée {st.session_state.arrival_time.strftime("%H:%M")}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="chrono">--:--:--</div>', unsafe_allow_html=True)
        st.markdown('<div class="chrono-label">En attente</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">Patient & ATCD</div>', unsafe_allow_html=True)
    age      = st.number_input("Âge", 0, 120, 45)
    atcd     = st.multiselect("Facteurs de risque", [
        "HTA","Diabète","Insuffisance Cardiaque","BPCO",
        "Anticoagulants / AOD","Grossesse","Immunodépression","Néoplasie"
    ])
    allergies = st.text_input("Allergies", "RAS")
    supp_o2   = st.checkbox("O₂ supplémentaire en cours")

    st.markdown('<div class="legal-text">FRENCH Triage SFMU V1.1 · Juin 2018<br>Usage professionnel exclusif.</div>', unsafe_allow_html=True)
    st.markdown('<div class="signature">Ismaïl Ibn-Daïfa<br>Infirmier Urgences</div>', unsafe_allow_html=True)


# --- TABS ---------------------------------------------------------------------
t_vitals, t_anamnesis, t_decision, t_scoring, t_history = st.tabs([
    "📊 Signes Vitaux & NEWS2",
    "🔍 Anamnèse & Motif FRENCH",
    "⚖️ Triage & SBAR",
    "🧮 Scores Cliniques",
    f"📋 Historique ({len(st.session_state.patient_history)})"
])


# -- TAB 1 : VITAUX ------------------------------------------------------------
with t_vitals:
    st.markdown('<div class="section-header">Constantes vitales</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    temp = c1.number_input("Température (°C)", 30.0, 45.0, 37.0, 0.1)
    fc   = c1.number_input("FC (bpm)", 20, 220, 80)
    pas  = c2.number_input("Systolique (mmHg)", 40, 260, 120)
    spo2 = c2.slider("SpO2 (%)", 50, 100, 98)
    fr   = c3.number_input("FR (cpm)", 5, 60, 16)
    gcs  = c3.select_slider("Glasgow (GCS)", list(range(3, 16)), 15)

    st.markdown('<div class="section-header">Alertes constantes</div>', unsafe_allow_html=True)
    a1, a2, a3, a4, a5 = st.columns(5)
    a1.markdown(f"**Temp.** {vital_badge(temp,36.0,35.0,38.0,40.5,'°C')}", unsafe_allow_html=True)
    a2.markdown(f"**FC** {vital_badge(fc,50,40,100,130,'')}", unsafe_allow_html=True)
    a3.markdown(f"**PAS** {vital_badge(pas,100,90,180,220,'')}", unsafe_allow_html=True)
    a4.markdown(f"**SpO2** {vital_badge(spo2,94,90,100,100,'%')}", unsafe_allow_html=True)
    a5.markdown(f"**FR** {vital_badge(fr,12,8,20,25,'')}", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Score NEWS2</div>', unsafe_allow_html=True)
    bpco_flag = "BPCO" in atcd
    news2 = compute_news2(fr, spo2, supp_o2, temp, pas, fc, gcs, bpco_flag)
    news2_label, news2_class = news2_level(news2)

    col_n, col_i = st.columns([1, 2])
    with col_n:
        st.markdown(f'<div class="news2-badge {news2_class}">{news2_label}</div>', unsafe_allow_html=True)
    with col_i:
        interp = {
            "news2-low":  ("Surveillance standard", "Réévaluation ≥ toutes les 12h."),
            "news2-med":  ("Surveillance rapprochée", "Réévaluation toutes les 1h. Alerter le médecin si aggravation."),
            "news2-high": ("Réponse urgente", "Évaluation médicale immédiate. Envisager soins continus."),
            "news2-crit": ("RÉPONSE EN URGENCE ABSOLUE", "Transfert immédiat SAUV. Alerte équipe réanimation."),
        }
        t_interp, d_interp = interp[news2_class]
        st.markdown(f"**{t_interp}**")
        st.markdown(d_interp)

    with st.expander("Détail calcul NEWS2"):
        cols = st.columns(7)
        lbl_list = ["FR","SpO2","O₂","Temp.","PAS","FC","Conscience"]
        val_list = [fr, spo2, "Oui" if supp_o2 else "Non", f"{temp}°C", pas, fc, "Alerte" if gcs < 15 else "Normal"]
        for col, lbl, val in zip(cols, lbl_list, val_list):
            col.metric(lbl, val)


# -- TAB 2 : ANAMNÈSE & MOTIF --------------------------------------------------
with t_anamnesis:
    st.markdown('<div class="section-header">Évaluation PQRST</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        p_pqrst = st.text_input("P -- Provoqué / Pallié par", placeholder="Repos, effort, inspiration...")
        q_pqrst = st.selectbox("Q -- Qualité / Type", ["Sourd","Étau","Brûlure","Coup de poignard","Électrique","Tension","Pesanteur","Crampe"])
        r_pqrst = st.text_input("R -- Région / Irradiation", placeholder="Bras, mâchoire, dos...")
    with c2:
        s_eva   = st.slider("S -- Sévérité EVA (0–10)", 0, 10, 0)
        t_onset = st.text_input("T -- Temps (Début & Durée)", placeholder="Depuis 30 min, brutal vs progressif...")

    st.markdown('<div class="section-header">Motif de recours -- FRENCH Triage SFMU</div>', unsafe_allow_html=True)

    # Liste complète des motifs FRENCH
    MOTIFS = {
        "CARDIO-CIRCULATOIRE": [
            "Arrêt cardiorespiratoire","Hypotension artérielle","Douleur thoracique / SCA",
            "Tachycardie / tachyarythmie","Bradycardie / bradyarythmie",
            "Hypertension artérielle","Dyspnée / insuffisance respiratoire","Palpitations",
        ],
        "RESPIRATOIRE": [
            "Asthme / aggravation BPCO","Hémoptysie","Corps étranger voies aériennes",
        ],
        "NEUROLOGIE": [
            "AVC / Déficit neurologique","Altération de conscience / Coma","Convulsions",
            "Céphalée","Vertiges / trouble de l'équilibre","Confusion / désorientation",
        ],
        "TRAUMATOLOGIE": [
            "Traumatisme avec amputation","Traumatisme abdomen / thorax / cervical",
            "Traumatisme crânien","Brûlure","Traumatisme bassin / hanche / fémur / rachis",
            "Traumatisme membre / épaule","Plaie","Électrisation","Agression sexuelle / sévices",
        ],
        "ABDOMINAL": [
            "Hématémèse / vomissement de sang","Rectorragie / méléna","Douleur abdominale",
        ],
        "GÉNITO-URINAIRE": [
            "Douleur lombaire / colique néphrétique","Rétention d'urine / anurie",
            "Douleur testiculaire / torsion","Hématurie",
        ],
        "GYNÉCO-OBSTÉTRIQUE": [
            "Accouchement imminent","Problème de grossesse (1er/2ème trimestre)",
            "Problème de grossesse (3ème trimestre)","Méno-métrorragie",
        ],
        "PSYCHIATRIE / INTOXICATION": [
            "Idée / comportement suicidaire","Troubles du comportement / psychiatrie",
            "Intoxication médicamenteuse","Intoxication non médicamenteuse",
        ],
        "INFECTIOLOGIE": ["Fièvre"],
        "DIVERS MÉTABOLIQUES": [
            "Hyperglycémie","Hypoglycémie","Hypothermie","Coup de chaleur / insolation",
            "Allergie / anaphylaxie",
        ],
        "ORL / OPHTALMO / PEAU": [
            "Épistaxis","Corps étranger / brûlure oculaire","Trouble visuel / cécité",
        ],
    }

    cat = st.selectbox("Catégorie", list(MOTIFS.keys()))
    motif = st.selectbox("Motif de recours", MOTIFS[cat])

    # -- Champs spécifiques selon motif --------------------------------------
    details = {"eva": s_eva, "dyspnee": details_dyspnee if 'details_dyspnee' in dir() else False}
    details = {"eva": s_eva}

    st.markdown('<div class="section-header">Critères spécifiques FRENCH</div>', unsafe_allow_html=True)

    if motif == "Douleur thoracique / SCA":
        details['ecg']                   = st.selectbox("ECG", ["Normal","Anormal typique SCA","Anormal non typique"])
        details['douleur_type']           = st.selectbox("Type de douleur", ["Atypique","Typique persistante/intense","Type coronaire"])
        details['comorbidites_coronaires']= st.checkbox("Comorbidités coronaires (ATCD, FdR)")

    elif motif == "Dyspnée / insuffisance respiratoire":
        details['parole']    = st.radio("Capacité à parler", ["Phrases complètes","Phrases courtes","Mots isolés"], horizontal=True)
        c1a, c1b = st.columns(2)
        details['orthopnee'] = c1a.checkbox("Orthopnée")
        details['tirage']    = c1a.checkbox("Tirage intercostal")
        details['cyanose']   = c1b.checkbox("Cyanose")

    elif motif == "Asthme / aggravation BPCO":
        details['dep']       = st.number_input("DEP (l/min)", 0, 800, 300)
        details['parole']    = st.radio("Capacité à parler", ["Phrases complètes","Phrases courtes","Mots isolés"], horizontal=True)
        details['tirage']    = st.checkbox("Tirage intercostal")
        details['orthopnee'] = st.checkbox("Orthopnée")

    elif motif in ["Tachycardie / tachyarythmie","Bradycardie / bradyarythmie","Palpitations"]:
        details['mauvaise_tolerance'] = st.checkbox("Mauvaise tolérance hémodynamique")
        details['malaise']            = st.checkbox("Malaise associé")

    elif motif == "Hypertension artérielle":
        details['sf_associes'] = st.checkbox("Signes fonctionnels associés (céphalée, trouble visuel, douleur...)")

    elif motif == "AVC / Déficit neurologique":
        details['delai_heures'] = st.number_input("Délai depuis début des symptômes (heures)", 0.0, 72.0, 2.0, 0.5)
        c1a, c1b = st.columns(2)
        details['deficit_moteur']   = c1a.checkbox("Déficit moteur")
        details['aphasie']          = c1a.checkbox("Aphasie")
        details['asymetrie_faciale']= c1b.checkbox("Asymétrie faciale (FAST)")
        details['trouble_marche']   = c1b.checkbox("Trouble de la marche")

    elif motif == "Altération de conscience / Coma":
        pass  # GCS suffit

    elif motif == "Convulsions":
        c1a, c1b = st.columns(2)
        details['crises_multiples']     = c1a.checkbox("Crises multiples")
        details['en_cours']             = c1a.checkbox("Crise en cours")
        details['confusion_post_critique']= c1b.checkbox("Confusion post-critique")
        details['deficit_post_critique'] = c1b.checkbox("Déficit post-critique")

    elif motif == "Céphalée":
        details['inhabituelle'] = st.checkbox("Céphalée inhabituelle (1er épisode, très intense...)")
        details['brutale']      = st.checkbox("Début brutal / en coup de tonnerre")
        details['fievre_assoc'] = st.checkbox("Fièvre associée")

    elif motif == "Vertiges / trouble de l'équilibre":
        details['signes_neuro']    = st.checkbox("Signes neurologiques associés")
        details['cephalee_brutale']= st.checkbox("Céphalée brutale associée")

    elif motif in ["Traumatisme abdomen / thorax / cervical",
                    "Traumatisme bassin / hanche / fémur / rachis",
                    "Traumatisme membre / épaule"]:
        details['cinetique']         = st.selectbox("Cinétique", ["Faible","Haute"])
        details['penetrant']         = st.checkbox("Pénétrant") if "abdomen" in motif else False
        details['mauvaise_tolerance']= st.checkbox("Mauvaise tolérance / déformation")
        if "membre" in motif.lower() or "épaule" in motif.lower():
            details['impotence_totale']   = st.checkbox("Impotence totale")
            details['deformation']        = st.checkbox("Déformation visible")
            details['impotence_moderee']  = st.checkbox("Impotence modérée")
            details['petite_deformation'] = st.checkbox("Petite déformation")
            details['ischemie']           = st.checkbox("Ischémie distale")

    elif motif == "Traumatisme crânien":
        c1a, c1b = st.columns(2)
        details['deficit_neuro']      = c1a.checkbox("Déficit neurologique")
        details['convulsion']         = c1a.checkbox("Convulsion post-TC")
        details['aod_avk']            = c1b.checkbox("AOD / AVK")
        details['vomissements_repetes']= c1b.checkbox("Vomissements répétés")
        details['pdc']                = st.checkbox("Perte de connaissance initiale")
        details['plaie']              = st.checkbox("Plaie crânienne")
        details['hematome']           = st.checkbox("Hématome sous-cutané")

    elif motif == "Brûlure":
        details['etendue']    = st.checkbox("Brûlure étendue (> 10% SCT)")
        details['main_visage']= st.checkbox("Localisation main / visage / périnée")

    elif motif == "Plaie":
        details['delabrant']     = st.checkbox("Plaie délabrante")
        details['saignement_actif']= st.checkbox("Saignement actif")
        details['large_complexe']= st.checkbox("Plaie large / complexe")
        details['main']          = st.checkbox("Localisation main")
        details['superficielle'] = st.checkbox("Plaie superficielle")

    elif motif == "Électrisation":
        details['pdc']         = st.checkbox("Perte de connaissance")
        details['brulure_grave']= st.checkbox("Brûlure associée")
        details['foudre']      = st.checkbox("Foudroiement")
        details['haute_tension']= st.checkbox("Haute tension")
        details['contact_long'] = st.checkbox("Contact prolongé")

    elif motif == "Douleur abdominale":
        c1a, c1b = st.columns(2)
        details['defense']         = c1a.checkbox("Défense abdominale")
        details['contracture']     = c1a.checkbox("Contracture")
        details['mauvaise_tolerance']= c1b.checkbox("Mauvaise tolérance")
        details['regressive']      = c1b.checkbox("Douleur régressive / indolore")
        details['douleur_presente']= True

    elif motif in ["Hématémèse / vomissement de sang","Rectorragie / méléna"]:
        details['abondante'] = st.checkbox("Saignement abondant")

    elif motif in ["Douleur lombaire / colique néphrétique","Douleur testiculaire / torsion","Hématurie"]:
        details['intense']          = st.checkbox("Douleur intense")
        details['regressive']       = st.checkbox("Douleur régressive / indolore")
        details['suspicion_torsion']= st.checkbox("Suspicion torsion") if "testiculaire" in motif else False
        details['abondante_active'] = st.checkbox("Saignement abondant actif") if "Hématurie" in motif else False

    elif motif == "Fièvre":
        c1a, c1b = st.columns(2)
        details['confusion']         = c1a.checkbox("Confusion / altération conscience")
        details['cephalee']          = c1a.checkbox("Céphalée associée")
        details['purpura']           = c1b.checkbox("Purpura")
        details['mauvaise_tolerance']= c1b.checkbox("Mauvaise tolérance générale")

    elif motif == "Hyperglycémie":
        details['glycemie']       = st.number_input("Glycémie (mmol/L)", 0.0, 60.0, 8.0, 0.5)
        details['cetose_elevee']  = st.checkbox("Cétose élevée / trouble de conscience")
        details['cetose_positive']= st.checkbox("Cétose positive")

    elif motif == "Hypoglycémie":
        details['mauvaise_tolerance'] = st.checkbox("Mauvaise tolérance clinique")

    elif motif == "Allergie / anaphylaxie":
        details['dyspnee']          = st.checkbox("Dyspnée / œdème laryngé")
        details['obstruction']      = st.checkbox("Risque d'obstruction")
        details['mauvaise_tolerance']= st.checkbox("Mauvaise tolérance (chute TA, urticaire étendu...)")

    elif motif in ["Intoxication médicamenteuse","Intoxication non médicamenteuse"]:
        c1a, c1b = st.columns(2)
        details['mauvaise_tolerance'] = c1a.checkbox("Mauvaise tolérance clinique")
        details['intention_suicidaire']= c1a.checkbox("Intention suicidaire")
        details['cardiotropes']       = c1b.checkbox("Toxiques cardiotropes / lésionnels")
        details['lesionnels']         = c1b.checkbox("Toxiques lésionnels")

    elif motif == "Troubles du comportement / psychiatrie":
        details['agitation']     = st.checkbox("Agitation / violence")
        details['hallucinations']= st.checkbox("Hallucinations / délire")

    elif motif in ["Épistaxis"]:
        details['abondant_actif']    = st.checkbox("Saignement abondant actif (en cours)")
        details['abondant_resolutif']= st.checkbox("Saignement abondant mais résolutif")

    elif motif in ["Corps étranger / brûlure oculaire"]:
        details['chimique'] = st.checkbox("Brûlure chimique")
        details['intense']  = st.checkbox("Douleur intense")

    elif motif in ["Trouble visuel / cécité"]:
        details['brutal'] = st.checkbox("Début brutal")

    elif motif == "Méno-métrorragie":
        details['grossesse'] = st.checkbox("Grossesse connue / suspectée")
        details['abondante'] = st.checkbox("Saignement abondant")


# -- TAB 3 : TRIAGE & SBAR -----------------------------------------------------
with t_decision:
    # Calcul NEWS2 (re-calcul pour ce tab)
    news2 = compute_news2(fr, spo2, supp_o2, temp, pas, fc, gcs, "BPCO" in atcd)
    news2_label, news2_class = news2_level(news2)

    niveau, justif, critere_ref = french_triage(
        motif, details, fc, pas, spo2, fr, gcs, temp, age, news2
    )

    box_css  = TRI_BOX_CSS[niveau]
    tri_label= TRI_LABELS[niveau]
    sector   = TRI_SECTORS[niveau]
    emoji    = TRI_EMOJI[niveau]

    st.markdown(
        f'<div class="triage-box {box_css}">'
        f'<div style="font-size:1.8rem;font-weight:600">{emoji} {tri_label}</div>'
        f'<div style="font-size:0.9rem;margin-top:8px;opacity:.85">NEWS2 : {news2} · EVA : {s_eva}/10</div>'
        f'<div style="font-size:0.85rem;margin-top:10px;font-style:italic">{justif}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.info(f"**Orientation :** {sector}")

    st.markdown(
        f'<div class="french-ref">📋 Référence FRENCH Triage SFMU V1.1 -- {critere_ref}</div>',
        unsafe_allow_html=True
    )

    # -- SBAR ----------------------------------------------------------------
    st.markdown('<div class="section-header">Transmission SBAR</div>', unsafe_allow_html=True)

    if st.button("📝 Générer la transmission SBAR", use_container_width=True):
        now_str  = datetime.now().strftime("%d/%m/%Y à %H:%M")
        atcd_str = ", ".join(atcd) if atcd else "Aucun ATCD notable"
        detail_str = " | ".join([
            f"{k}: {v}" for k, v in details.items()
            if v and v is not False and v != "" and k != "eva"
        ]) if details else "--"

        sbar = (
            f"==============================================\n"
            f"  TRANSMISSION SBAR -- {now_str}\n"
            f"  IAO Expert Pro v8.0 · FRENCH Triage SFMU V1.1\n"
            f"  Ismaïl Ibn-Daïfa -- Infirmier Urgences\n"
            f"==============================================\n\n"
            f"[S] SITUATION\n"
            f"Patient de {age} ans accueilli pour : {motif} (catégorie : {cat}).\n"
            f"EVA {s_eva}/10. Arrivée le {now_str}.\n\n"
            f"[B] BACKGROUND\n"
            f"ATCD / Terrain : {atcd_str}.\n"
            f"Allergies : {allergies}.\n"
            f"O₂ supplémentaire : {'Oui' if supp_o2 else 'Non'}.\n\n"
            f"[A] ASSESSMENT\n"
            f"Constantes : T° {temp}°C · FC {fc} bpm · PAS {pas} mmHg\n"
            f"             SpO2 {spo2}% · FR {fr} cpm · GCS {gcs}/15.\n"
            f"Score NEWS2 : {news2} ({news2_label}).\n"
            f"PQRST : P={p_pqrst or '--'} · Q={q_pqrst} · R={r_pqrst or '--'}\n"
            f"        S={s_eva}/10 · T={t_onset or '--'}.\n"
            f"Critères spécifiques : {detail_str}.\n\n"
            f"[R] RECOMMENDATION\n"
            f"Triage FRENCH : {tri_label}\n"
            f"Justification  : {justif}\n"
            f"Référence      : {critere_ref}\n"
            f"Orientation    : {sector}\n"
            f"==============================================\n"
            f"Signé : Ismaïl Ibn-Daïfa (IAO) · {now_str}\n"
        )
        st.session_state.sbar_text = sbar
        st.session_state.patient_history.append({
            "heure":   datetime.now().strftime("%H:%M"),
            "age":     age,
            "motif":   motif,
            "cat":     cat,
            "niveau":  niveau,
            "eva":     s_eva,
            "news2":   news2,
            "sbar":    sbar,
        })

    if st.session_state.sbar_text:
        st.markdown(f'<div class="sbar-block">{st.session_state.sbar_text}</div>', unsafe_allow_html=True)
        col_dl, col_cp = st.columns(2)
        col_dl.download_button(
            "⬇ Télécharger (.txt)",
            data=st.session_state.sbar_text,
            file_name=f"SBAR_{datetime.now().strftime('%Y%m%d_%H%M')}_Tri{niveau}.txt",
            mime="text/plain",
            use_container_width=True
        )
        with col_cp:
            st.code(st.session_state.sbar_text[:300] + "…", language=None)


# ==============================================================================
# -- TAB 4 : SCORES CLINIQUES -------------------------------------------------
# ==============================================================================
with t_scoring:

    def score_badge(val, low_max, med_max, label=""):
        if val <= low_max:   css = "score-low"
        elif val <= med_max: css = "score-med"
        else:                css = "score-high"
        return f'<div class="score-result {css}">{val} {label}</div>'

    def score_badge_custom(val, css, label=""):
        return f'<div class="score-result {css}">{val} {label}</div>'

    def row(label, val):
        chk = "criterion-ok" if val else "criterion-no"
        sym = "✓" if val else "○"
        pts = "+1" if val else "+0"
        return (
            f'<div class="score-row">'
            f'<span class="score-row-label {chk}">{sym} {label}</span>'
            f'<span class="score-row-val">{pts}</span>'
            f'</div>'
        )

    st.markdown("### Scores cliniques validés")
    st.caption("Calculateurs interactifs -- résultats automatiques selon les critères cochés.")

    # --------------------------------------------------------------------------
    # SCORE TIMI (SCA / NSTEMI)
    # --------------------------------------------------------------------------
    with st.expander("🫀 Score TIMI -- Risque SCA NSTEMI / Angor instable", expanded=True):
        st.markdown('<div class="score-title">TIMI Risk Score for UA/NSTEMI (Antman 2000)</div>', unsafe_allow_html=True)
        st.caption("Prédit la mortalité à 14 jours : décès, IDM, revascularisation en urgence.")

        ca, cb = st.columns(2)
        with ca:
            t1 = st.checkbox("Âge ≥ 65 ans", key="timi1")
            t2 = st.checkbox("≥ 3 facteurs de risque coronarien (HTA, Diabète, Tabac, Dyslip., ATCD familial)", key="timi2")
            t3 = st.checkbox("Sténose coronarienne connue ≥ 50%", key="timi3")
            t4 = st.checkbox("Déviation du segment ST sur l'ECG d'entrée", key="timi4")
        with cb:
            t5 = st.checkbox("≥ 2 épisodes angineux dans les 24 dernières heures", key="timi5")
            t6 = st.checkbox("Élévation des marqueurs cardiaques (Troponine, CK-MB)", key="timi6")
            t7 = st.checkbox("Aspirine prise dans les 7 derniers jours", key="timi7")

        timi_score = sum([t1, t2, t3, t4, t5, t6, t7])

        if timi_score <= 2:
            timi_risk, timi_css, timi_interp = "Faible", "score-low", "Risque événement 14j : ~5%. Surveillance et bilan biologique."
        elif timi_score <= 4:
            timi_risk, timi_css, timi_interp = "Intermédiaire", "score-med", "Risque événement 14j : ~13–20%. Héparine + coronarographie rapide."
        else:
            timi_risk, timi_css, timi_interp = "Élevé", "score-high", "Risque événement 14j : ~26–41%. Coronarographie urgente < 2h recommandée."

        st.markdown(score_badge_custom(f"{timi_score}/7 -- {timi_risk}", timi_css), unsafe_allow_html=True)
        st.markdown(f'<div class="score-interp">⟶ {timi_interp}</div>', unsafe_allow_html=True)

        rows_html = "".join([
            row("Âge ≥ 65 ans", t1), row("≥ 3 FdR coronariens", t2),
            row("Sténose ≥ 50% connue", t3), row("Déviation ST", t4),
            row("≥ 2 angor/24h", t5), row("Marqueurs cardiaques +", t6),
            row("Aspirine dans les 7j", t7),
        ])
        st.markdown(f'<div style="margin-top:12px">{rows_html}</div>', unsafe_allow_html=True)
        st.info("📌 TIMI > 4 = orientation filière coronaire urgente. Associer ECG, troponine, accès IV.")

    # --------------------------------------------------------------------------
    # SCORE DE SILVERMAN (Détresse respiratoire néonatale)
    # --------------------------------------------------------------------------
    with st.expander("👶 Score de Silverman -- Détresse respiratoire néonatale", expanded=False):
        st.markdown('<div class="score-title">Score de Silverman-Andersen (nouveau-né)</div>', unsafe_allow_html=True)
        st.caption("Évalue la sévérité de la détresse respiratoire du nouveau-né. Score 0 = aucun signe, 10 = détresse maximale.")

        sil_items = {
            "Balancement thoraco-abdominal": ["0 - Synchrone", "1 - Asynchrone léger", "2 - Asynchrone marqué"],
            "Tirage intercostal":            ["0 - Absent", "1 - Discret", "2 - Important"],
            "Creusement xiphoïdien":         ["0 - Absent", "1 - Discret", "2 - Important"],
            "Battement des ailes du nez":    ["0 - Absent", "1 - Discret", "2 - Important"],
            "Geignement expiratoire":        ["0 - Absent", "1 - Audible au stéthoscope", "2 - Audible à l'oreille"],
        }

        sil_vals = {}
        ca2, cb2 = st.columns(2)
        items_list = list(sil_items.items())
        for idx, (label, opts) in enumerate(items_list):
            col = ca2 if idx < 3 else cb2
            val = col.selectbox(label, opts, key=f"sil_{idx}")
            sil_vals[label] = int(val[0])  # digit is always first char

        sil_score = sum(sil_vals.values())

        if sil_score == 0:
            sil_css, sil_interp = "score-info", "Pas de détresse respiratoire."
        elif sil_score <= 3:
            sil_css, sil_interp = "score-low", "Détresse légère. Surveillance rapprochée, O₂ si nécessaire."
        elif sil_score <= 6:
            sil_css, sil_interp = "score-med", "Détresse modérée. Oxygénothérapie, appel pédiatre urgent."
        else:
            sil_css, sil_interp = "score-high", "Détresse sévère. Prise en charge réanimatoire immédiate -- appel SMUR pédiatrique."

        st.markdown(score_badge_custom(f"{sil_score}/10", sil_css), unsafe_allow_html=True)
        st.markdown(f'<div class="score-interp">⟶ {sil_interp}</div>', unsafe_allow_html=True)
        st.info("📌 Score ≥ 4 → appel systématique du pédiatre. Score ≥ 7 → réanimation néonatale.")

    # --------------------------------------------------------------------------
    # GLASGOW INTELLIGENT (avec composantes détaillées)
    # --------------------------------------------------------------------------
    with st.expander("🧠 Glasgow -- Évaluation détaillée (Y / V / M)", expanded=False):
        st.markdown('<div class="score-title">Glasgow Coma Scale -- Détail des 3 composantes</div>', unsafe_allow_html=True)
        st.caption("Évalue le niveau de conscience. Score 15 = conscient. Score ≤ 8 = coma -- intubation à considérer.")

        ca3, cb3, cc3 = st.columns(3)

        with ca3:
            st.markdown("**Ouverture des Yeux (Y)**")
            yeux = st.radio("Yeux", [
                "4 - Spontanée",
                "3 - Au bruit / à la voix",
                "2 - À la douleur",
                "1 - Aucune",
            ], key="gcs_y")
            y_score = int(yeux[0])

        with cb3:
            st.markdown("**Réponse Verbale (V)**")
            verbale = st.radio("Verbale", [
                "5 - Orientée, cohérente",
                "4 - Confuse",
                "3 - Mots inappropriés",
                "2 - Sons incompréhensibles",
                "1 - Aucune",
            ], key="gcs_v")
            v_score = int(verbale[0])

        with cc3:
            st.markdown("**Réponse Motrice (M)**")
            motrice = st.radio("Motrice", [
                "6 - Obéit aux ordres",
                "5 - Localise la douleur",
                "4 - Retrait à la douleur",
                "3 - Flexion anormale (décortication)",
                "2 - Extension (décérébration)",
                "1 - Aucune",
            ], key="gcs_m")
            m_score = int(motrice[0])

        gcs_calc = y_score + v_score + m_score

        if gcs_calc == 15:
            gcs_css, gcs_interp = "score-info", "Conscient, pas d'altération de conscience."
        elif gcs_calc >= 13:
            gcs_css, gcs_interp = "score-low", "Altération légère. Surveillance neurologique rapprochée."
        elif gcs_calc >= 9:
            gcs_css, gcs_interp = "score-med", "Altération modérée. Évaluation médicale urgente, voie aérienne à sécuriser."
        else:
            gcs_css, gcs_interp = "score-high", "COMA -- GCS ≤ 8 : intubation oro-trachéale à discuter en urgence. Tri 1 FRENCH."

        st.markdown(score_badge_custom(f"GCS {gcs_calc}/15  (Y{y_score} V{v_score} M{m_score})", gcs_css), unsafe_allow_html=True)
        st.markdown(f'<div class="score-interp">⟶ {gcs_interp}</div>', unsafe_allow_html=True)

        html_rows = "".join([
            f'<div class="score-row"><span class="score-row-label">Yeux (Y)</span><span class="score-row-val">{y_score}/4</span></div>',
            f'<div class="score-row"><span class="score-row-label">Verbale (V)</span><span class="score-row-val">{v_score}/5</span></div>',
            f'<div class="score-row"><span class="score-row-label">Motrice (M)</span><span class="score-row-val">{m_score}/6</span></div>',
            f'<div class="score-row"><span class="score-row-label"><b>Total GCS</b></span><span class="score-row-val"><b>{gcs_calc}/15</b></span></div>',
        ])
        st.markdown(f'<div style="margin-top:12px">{html_rows}</div>', unsafe_allow_html=True)
        st.info("📌 Documenter systématiquement Y/V/M -- Ex: GCS 12 (Y3 V4 M5). Répéter toutes les 15 min si instable.")

    # --------------------------------------------------------------------------
    # SCORE DE MALINAS (Accouchement imminent)
    # --------------------------------------------------------------------------
    with st.expander("🤰 Score de Malinas -- Accouchement imminent aux urgences", expanded=False):
        st.markdown('<div class="score-title">Score de Malinas -- Pronostic d\'accouchement imminent</div>', unsafe_allow_html=True)
        st.caption("Évalue le risque d'accouchement imminent aux urgences. Score ≥ 10 = accouchement imminent.")

        ca4, cb4 = st.columns(2)
        with ca4:
            parite = ca4.selectbox("Parité", ["0 - Primipare", "1 - Multipare"], key="mal_par")
            duree_trav = ca4.selectbox("Durée du travail", [
                "0 - < 1 heure", "1 - 1 à 3 heures", "2 - > 3 heures"
            ], key="mal_trav")
            duree_cont = ca4.selectbox("Durée des contractions", [
                "0 - < 1 minute", "1 - 1 minute", "2 - > 1 minute"
            ], key="mal_cont")
        with cb4:
            interval = cb4.selectbox("Intervalle entre contractions", [
                "0 - > 5 minutes", "1 - 3 à 5 minutes", "2 - < 3 minutes"
            ], key="mal_int")
            poche = cb4.selectbox("Rupture de la poche des eaux", [
                "0 - Intacte", "1 - Rompue"
            ], key="mal_poche")
            envie_pousser = cb4.selectbox("Envie de pousser", [
                "0 - Absente", "1 - Présente"
            ], key="mal_pousser")

        m_par   = int(parite[0])
        m_trav  = int(duree_trav[0])
        m_cont  = int(duree_cont[0])
        m_int   = int(interval[0])
        m_poche = int(poche[0])
        m_push  = int(envie_pousser[0])
        mal_score = m_par + m_trav + m_cont + m_int + m_poche + m_push

        if mal_score <= 5:
            mal_css, mal_interp = "score-low", "Accouchement non imminent. Transport possible vers maternité."
        elif mal_score <= 7:
            mal_css, mal_interp = "score-med", "Risque modéré. Transport rapide vers maternité en SMUR. Préparer le matériel d'accouchement."
        elif mal_score <= 9:
            mal_css, mal_interp = "score-med", "Risque élevé d'accouchement imminent. Préparer l'accouchement sur place. Appeler sage-femme/obstétricien."
        else:
            mal_css, mal_interp = "score-high", "ACCOUCHEMENT IMMINENT -- Ne pas transporter. Préparer l'accouchement sur place immédiatement. SAUV / Tri M."

        st.markdown(score_badge_custom(f"{mal_score}/10", mal_css), unsafe_allow_html=True)
        st.markdown(f'<div class="score-interp">⟶ {mal_interp}</div>', unsafe_allow_html=True)

        mal_rows = "".join([
            f'<div class="score-row"><span class="score-row-label">Parité</span><span class="score-row-val">{m_par}</span></div>',
            f'<div class="score-row"><span class="score-row-label">Durée du travail</span><span class="score-row-val">{m_trav}</span></div>',
            f'<div class="score-row"><span class="score-row-label">Durée contractions</span><span class="score-row-val">{m_cont}</span></div>',
            f'<div class="score-row"><span class="score-row-label">Intervalle contractions</span><span class="score-row-val">{m_int}</span></div>',
            f'<div class="score-row"><span class="score-row-label">Rupture poche des eaux</span><span class="score-row-val">{m_poche}</span></div>',
            f'<div class="score-row"><span class="score-row-label">Envie de pousser</span><span class="score-row-val">{m_push}</span></div>',
            f'<div class="score-row"><span class="score-row-label"><b>Total Malinas</b></span><span class="score-row-val"><b>{mal_score}/10</b></span></div>',
        ])
        st.markdown(f'<div style="margin-top:12px">{mal_rows}</div>', unsafe_allow_html=True)
        st.info("📌 Score ≥ 10 = ne pas transporter. Activer le protocole d'accouchement inopiné. Score ≥ 8 = SMUR obstétrical.")

    # --------------------------------------------------------------------------
    # SCORE BRÛLURE -- Règle des 9 de Wallace + gravité
    # --------------------------------------------------------------------------
    with st.expander("🔥 Score Brûlure -- Règle des 9 de Wallace + Indice de gravité", expanded=False):
        st.markdown('<div class="score-title">Évaluation des brûlures -- Règle des 9 + Indice de Baux</div>', unsafe_allow_html=True)
        st.caption("Calcule la Surface Corporelle Brûlée (SCB%) et l'indice de gravité (Baux = âge + SCB).")

        age_br = st.number_input("Âge du patient (brûlure)", 0, 120, 45, key="br_age")

        st.markdown("**Surface Corporelle Brûlée (SCB%) -- Règle des 9 de Wallace**")
        ca5, cb5, cc5 = st.columns(3)
        with ca5:
            br_tete    = st.number_input("Tête & cou (%)", 0, 9, 0, key="br_tete")
            br_tx_ant  = st.number_input("Thorax antérieur (%)", 0, 9, 0, key="br_tx_ant")
            br_tx_post = st.number_input("Thorax postérieur (%)", 0, 9, 0, key="br_tx_post")
            br_abdo    = st.number_input("Abdomen antérieur (%)", 0, 9, 0, key="br_abdo")
        with cb5:
            br_ms_d    = st.number_input("Membre supérieur droit (%)", 0, 9, 0, key="br_msd")
            br_ms_g    = st.number_input("Membre supérieur gauche (%)", 0, 9, 0, key="br_msg")
            br_mi_d    = st.number_input("Membre inférieur droit (%)", 0, 18, 0, key="br_mid")
            br_mi_g    = st.number_input("Membre inférieur gauche (%)", 0, 18, 0, key="br_mig")
        with cc5:
            br_perinee = st.number_input("Périnée (%)", 0, 1, 0, key="br_per")
            br_profond = st.selectbox("Profondeur prédominante", [
                "Superficielle (1er degré)",
                "Intermédiaire (2ème degré superficiel)",
                "Profonde (2ème degré profond / 3ème degré)",
            ], key="br_prof")
            br_localisation = st.multiselect("Localisations critiques", [
                "Visage","Mains","Pieds","Périnée","Cou","Plis de flexion","Voies aériennes"
            ], key="br_loc")
            br_inhalation = st.checkbox("Suspicion inhalation de fumées", key="br_inh")

        scb = br_tete + br_tx_ant + br_tx_post + br_abdo + br_ms_d + br_ms_g + br_mi_d + br_mi_g + br_perinee
        scb = min(scb, 100)
        indice_baux = age_br + scb
        indice_baux_rev = age_br + (1.5 * scb) if br_inhalation else indice_baux

        # Gravité
        localisation_critique = len(br_localisation) > 0
        profonde = "Profonde" in br_profond or "3ème" in br_profond

        if scb >= 50 or indice_baux >= 100:
            br_css = "score-high"
            br_sev = "Brûlure CRITIQUE -- Pronostic vital engagé. Centre de brûlés, réanimation immédiate."
        elif scb >= 20 or indice_baux >= 60 or (profonde and scb >= 10) or br_inhalation:
            br_css = "score-high"
            br_sev = "Brûlure GRAVE -- Hospitalisation en centre spécialisé brûlés, remplissage vasculaire."
        elif scb >= 10 or localisation_critique or profonde:
            br_css = "score-med"
            br_sev = "Brûlure MODÉRÉE -- Hospitalisation, surveillance, avis chirurgical plasticien."
        elif scb >= 1:
            br_css = "score-low"
            br_sev = "Brûlure LÉGÈRE -- Prise en charge ambulatoire possible si < 10% SCB, pas de localisation critique."
        else:
            br_css = "score-info"
            br_sev = "Aucune surface renseignée."

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown(score_badge_custom(f"SCB : {scb}%", br_css), unsafe_allow_html=True)
        with col_r2:
            st.markdown(score_badge_custom(f"Baux : {indice_baux}", br_css), unsafe_allow_html=True)

        st.markdown(f'<div class="score-interp">⟶ {br_sev}</div>', unsafe_allow_html=True)
        if br_inhalation:
            st.warning(f"⚠ Inhalation suspectée : Indice de Baux révisé = **{indice_baux_rev:.0f}** (×1.5 sur SCB). Mortalité aggravée.")

        br_rows = "".join([
            f'<div class="score-row"><span class="score-row-label">Surface brûlée totale</span><span class="score-row-val">{scb}%</span></div>',
            f'<div class="score-row"><span class="score-row-label">Âge</span><span class="score-row-val">{age_br} ans</span></div>',
            f'<div class="score-row"><span class="score-row-label">Indice de Baux (âge + SCB)</span><span class="score-row-val">{indice_baux}</span></div>',
            f'<div class="score-row"><span class="score-row-label">Profondeur</span><span class="score-row-val">{br_profond[:20]}</span></div>',
            f'<div class="score-row"><span class="score-row-label">Localisations critiques</span><span class="score-row-val">{", ".join(br_localisation) if br_localisation else "Aucune"}</span></div>',
            f'<div class="score-row"><span class="score-row-label">Inhalation de fumées</span><span class="score-row-val">{"Oui ⚠" if br_inhalation else "Non"}</span></div>',
        ])
        st.markdown(f'<div style="margin-top:12px">{br_rows}</div>', unsafe_allow_html=True)

        # Formule de Parkland
        if scb > 0:
            parkland = 4 * 70 * scb  # 4 mL × poids estimé 70kg × SCB
            st.info(
                f"📌 **Formule de Parkland (poids 70 kg estimé) :** {parkland} mL de Ringer Lactate / 24h "
                f"-- dont {parkland//2} mL dans les 8 premières heures, {parkland//2} mL dans les 16h suivantes. "
                f"Adapter au poids réel du patient."
            )

    # --------------------------------------------------------------------------
    # SCORE BATT (Blast And Trauma Triage)
    # --------------------------------------------------------------------------
    with st.expander("💥 Score BATT -- Blast And Trauma Triage", expanded=False):
        st.markdown('<div class="score-title">Score BATT -- Triage des victimes d\'explosion / traumatismes multiples</div>', unsafe_allow_html=True)
        st.caption(
            "Outil de triage rapide pour les victimes d'explosion ou de traumatisme balistique. "
            "Évalue la survie probable et oriente la priorité de prise en charge en situation de médecine de catastrophe."
        )

        ca6, cb6 = st.columns(2)
        with ca6:
            st.markdown("**Paramètres physiologiques**")
            batt_gcs   = st.select_slider("GCS (victimologie)", list(range(3, 16)), 15, key="batt_gcs")
            batt_pas   = st.number_input("PAS (mmHg)", 0, 300, 120, key="batt_pas")
            batt_fr    = st.number_input("FR (cpm)", 0, 60, 16, key="batt_fr")
            batt_spo2  = st.slider("SpO2 (%)", 50, 100, 98, key="batt_spo2")

        with cb6:
            st.markdown("**Lésions anatomiques**")
            batt_amputation   = st.checkbox("Amputation traumatique (membre)", key="batt_amp")
            batt_thorax       = st.checkbox("Traumatisme thoracique ouvert / volet costal", key="batt_thor")
            batt_abdo         = st.checkbox("Éviscération / laparotomie en urgence", key="batt_abdo")
            batt_crane        = st.checkbox("Traumatisme crânien ouvert / substance cérébrale visible", key="batt_crane")
            batt_crush        = st.checkbox("Syndrome d'écrasement (crush syndrome)", key="batt_crush")
            batt_burns        = st.checkbox("Brûlures > 60% SCB ou inhalation massive", key="batt_burns")
            batt_airways      = st.checkbox("Obstruction des voies aériennes non levée", key="batt_airways")

        # Calcul BATT
        batt_physio_ok = (batt_gcs >= 10 and batt_pas >= 90 and 10 <= batt_fr <= 29 and batt_spo2 >= 90)
        batt_lethal    = batt_crane or batt_burns  # lésions dépassées

        nb_lesions_graves = sum([batt_amputation, batt_thorax, batt_abdo, batt_crush, batt_airways])

        # Logique BATT simplifiée
        if batt_lethal and not batt_physio_ok:
            batt_cat = "T4 -- DÉPASSÉ"
            batt_css = "score-high"
            batt_color = "#7f1d1d"
            batt_interp = (
                "Lésion létale + instabilité physiologique. En médecine de catastrophe : "
                "patient classé T4 (dépassé). Soins palliatifs, priorité aux autres victimes."
            )
        elif not batt_physio_ok and nb_lesions_graves >= 2:
            batt_cat = "T1 -- EXTRÊME URGENCE"
            batt_css = "score-high"
            batt_color = "#7f1d1d"
            batt_interp = "Instabilité physiologique + lésions multiples graves. Prise en charge immédiate -- SAUV."
        elif not batt_physio_ok or nb_lesions_graves >= 1:
            batt_cat = "T1 -- URGENCE ABSOLUE"
            batt_css = "score-high"
            batt_color = "#7c2d12"
            batt_interp = "Instabilité ou lésion grave unique. Prise en charge urgente -- déchocage."
        elif batt_physio_ok and nb_lesions_graves == 0 and not batt_lethal:
            batt_cat = "T3 -- URGENCE DIFFÉRÉE"
            batt_css = "score-low"
            batt_color = "#052e16"
            batt_interp = "Paramètres stables, pas de lésion immédiatement vitale. Surveillance et bilan complet."
        else:
            batt_cat = "T2 -- URGENCE RELATIVE"
            batt_css = "score-med"
            batt_color = "#422006"
            batt_interp = "Paramètres limites ou lésion grave contrôlée. Surveillance rapprochée, réévaluation fréquente."

        st.markdown(score_badge_custom(batt_cat, batt_css), unsafe_allow_html=True)
        st.markdown(f'<div class="score-interp">⟶ {batt_interp}</div>', unsafe_allow_html=True)

        batt_rows = "".join([
            f'<div class="score-row"><span class="score-row-label">GCS</span><span class="score-row-val">{batt_gcs}/15</span></div>',
            f'<div class="score-row"><span class="score-row-label">PAS</span><span class="score-row-val">{batt_pas} mmHg</span></div>',
            f'<div class="score-row"><span class="score-row-label">FR</span><span class="score-row-val">{batt_fr} cpm</span></div>',
            f'<div class="score-row"><span class="score-row-label">SpO2</span><span class="score-row-val">{batt_spo2}%</span></div>',
            f'<div class="score-row"><span class="score-row-label">Lésions graves</span><span class="score-row-val">{nb_lesions_graves} / 5</span></div>',
            f'<div class="score-row"><span class="score-row-label">Lésion potentiellement létale</span><span class="score-row-val">{"Oui ⚠" if batt_lethal else "Non"}</span></div>',
            f'<div class="score-row"><span class="score-row-label">Physiologie stable</span><span class="score-row-val">{"Oui ✓" if batt_physio_ok else "NON ✗"}</span></div>',
        ])
        st.markdown(f'<div style="margin-top:12px">{batt_rows}</div>', unsafe_allow_html=True)

        st.info(
            "📌 En situation de catastrophe (plan ORSAN / plan rouge) : "
            "T1 = prise en charge immédiate · T2 = différée · T3 = attente · T4 = dépassé (soins palliatifs). "
            "Réévaluer systématiquement après chaque geste."
        )

    # Récapitulatif scores calculés
    st.markdown('<div class="section-header">Récapitulatif des scores calculés</div>', unsafe_allow_html=True)
    recap_data = {
        "Score TIMI": f"{timi_score}/7 -- {timi_risk}",
        "Score Silverman": f"{sil_score}/10",
        "Glasgow calculé": f"{gcs_calc}/15 (Y{y_score} V{v_score} M{m_score})",
        "Score Malinas": f"{mal_score}/10",
        "Surface brûlée (SCB)": f"{scb}% -- Baux {indice_baux}",
        "BATT": batt_cat,
    }
    rc1, rc2, rc3 = st.columns(3)
    for i, (k, v) in enumerate(recap_data.items()):
        col = [rc1, rc2, rc3][i % 3]
        col.metric(k, v)


# -- TAB 5 : HISTORIQUE --------------------------------------------------------
with t_history:
    if not st.session_state.patient_history:
        st.info("Aucun patient enregistré. Générez un SBAR pour alimenter l'historique.")
    else:
        st.markdown(f"**{len(st.session_state.patient_history)} patient(s) pris en charge cette session**")

        emoji_map = TRI_EMOJI
        for i, pat in enumerate(reversed(st.session_state.patient_history), 1):
            css = TRI_HIST_CSS.get(pat['niveau'], 'hist-4')
            em  = emoji_map.get(pat['niveau'], '⚪')
            st.markdown(
                f'<div class="hist-row {css}">'
                f'<b>{pat["heure"]}</b> · {pat["age"]} ans · <b>{pat["motif"]}</b> · '
                f'EVA {pat["eva"]}/10 · NEWS2 {pat["news2"]} · {em} Tri {pat["niveau"]}'
                f'</div>',
                unsafe_allow_html=True
            )
            with st.expander(f"SBAR -- Patient #{len(st.session_state.patient_history) - i + 1}"):
                st.markdown(f'<div class="sbar-block">{pat["sbar"]}</div>', unsafe_allow_html=True)
                st.download_button(
                    "⬇ Télécharger ce SBAR",
                    data=pat["sbar"],
                    file_name=f"SBAR_{pat['heure'].replace(':','h')}_Tri{pat['niveau']}.txt",
                    mime="text/plain",
                    key=f"dl_hist_{i}"
                )

        if st.button("🗑 Effacer l'historique de session"):
            st.session_state.patient_history = []
            st.rerun()