import streamlit as st

# ==========================================
# 1. BASES DE DONNÉES CLINIQUES (FRENCH)
# ==========================================

REFERENTIEL_ADULTE = {
    "Cardio / Thoracique": [
        ("Le patient est-il en arrêt cardio-respiratoire ou choc ?", "TRI 1 (ROUGE)"),
        ("Douleur thoracique constrictive, irradiante ou typique de SCA ?", "TRI 2 (ORANGE)"),
        ("Malaise avec cyanose, déficit neurologique ou durée > qq minutes ?", "TRI 2 (ORANGE)"),
        ("Douleur thoracique atypique mais avec antécédents cardio majeurs ?", "TRI 3A (JAUNE)"),
        ("Palpitations bien tolérées sans douleur ?", "TRI 4 (VERT)")
    ],
    "Neurologie / Psy": [
        ("Coma (Glasgow <= 8) ou convulsion en cours ?", "TRI 1 (ROUGE)"),
        ("Déficit neurologique (moteur, parole, face) apparu depuis MOINS de 4h30 ?", "TRI 2 (ORANGE)"),
        ("Idées suicidaires imminentes ou agitation extrême ?", "TRI 2 (ORANGE)"),
        ("Céphalée inhabituelle, brutale, et d'intensité maximale d'emblée ?", "TRI 3B (JAUNE)"),
        ("Vertiges rotatoires isolés et bien tolérés ?", "TRI 4 (VERT)")
    ],
    "Respiratoire": [
        ("Cyanose, sueurs, ou épuisement respiratoire ?", "TRI 1 (ROUGE)"),
        ("La dyspnée empêche-t-elle de parler en phrases complètes (Tirage) ?", "TRI 2 (ORANGE)"),
        ("Hémoptysie (crachat de sang) de moyenne à grande abondance ?", "TRI 2 (ORANGE)"),
        ("Crise d'asthme avec un DEP <= 200 ?", "TRI 2 (ORANGE)"),
        ("Toux avec fièvre mais respiration calme ?", "TRI 4 (VERT)")
    ]
}

REFERENTIEL_ENFANT = {
    "Respiratoire / Infectieux": [
        ("L'enfant présente-t-il des pauses respiratoires ou une cyanose ?", "TRI 1 (ROUGE)"),
        ("Dyspnée avec sifflement, battement des ailes du nez ou tirage ?", "TRI 2 (ORANGE)"),
        ("Fièvre mal tolérée (enfant geignard, ne sourit plus) ?", "TRI 3A (JAUNE)")
    ],
    "Digestif / Déshydratation": [
        ("Perte de poids >= 10% par rapport au poids habituel ?", "TRI 2 (ORANGE)"),
        ("Enfant très hypotonique (mou) ou refus total de boire ?", "TRI 2 (ORANGE)"),
        ("Perte de poids entre 5% et 9% ?", "TRI 3B (JAUNE)")
    ]
}

# ==========================================
# 2. LOGIQUE DE CALCUL (NEWS2)
# ==========================================

def calculer_score_news2(fr, spo2, temp, pas, fc, gcs_score, oxygen_needed):
    score = 0
    if fr <= 8 or fr >= 25: score += 3
    elif 21 <= fr <= 24: score += 2
    elif 9 <= fr <= 11: score += 1

    if spo2 <= 91: score += 3
    elif 92 <= spo2 <= 93: score += 2
    elif 94 <= spo2 <= 95: score += 1

    if oxygen_needed: score += 2

    if temp <= 35.0: score += 3
    elif temp >= 39.1: score += 2
    elif (35.1 <= temp <= 36.0) or (38.1 <= temp <= 39.0): score += 1

    if pas <= 90 or pas >= 220: score += 3
    elif 91 <= pas <= 100: score += 2
    elif 101 <= pas <= 110: score += 1

    if fc <= 40 or fc >= 131: score += 3
    elif 111 <= fc <= 130: score += 2
    elif (41 <= fc <= 50) or (91 <= fc <= 110): score += 1

    if gcs_score < 15: score += 3
    return score

# ==========================================
# 3. INTERFACE STREAMLIT
# ==========================================

st.set_page_config(page_title="IAO FRENCH & NEWS2", layout="wide")

st.title("🏥 Assistant IAO - FRENCH V1.2 & NEWS2")
st.sidebar.header("📋 Profil Patient")
type_p = st.sidebar.radio("Type", ["Adulte", "Enfant (<= 2 ans)"])

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Constantes Vitales")
    temp = st.number_input("Température (°C)", 25.0, 45.0, 37.0, 0.1)
    fc = st.number_input("Fréquence Cardiaque (bpm)", 20, 250, 80)
    spo2 = st.slider("Saturation SpO2 (%)", 0, 100, 98)
    fr = st.number_input("Fréquence Respiratoire (m/min)", 5, 60, 16)
    
    if type_p == "Adulte":
        pas = st.number_input("PAS (Tension mmHg)", 50, 250, 120)
        gcs = st.slider("Score de Glasgow", 3, 15, 15)
        o2 = st.checkbox("Le patient est sous oxygène ?")
    else:
        age_mois = st.number_input("Âge (en mois)", 0, 24, 12)
        gcs = st.slider("Score de Glasgow (Enfant)", 3, 15, 15)
        pas, o2 = 100, False

# --- CALCULS ET LOGIQUE ---
news2 = 0
decision_finale = "TRI 4/5 (STABLE)"
couleur = "#27ae60" # Vert par défaut

if type_p == "Adulte":
    news2 = calculer_score_news2(fr, spo2, temp, pas, fc, gcs, o2)

# Évaluation Gravité Constantes
if type_p == "Enfant (<= 2 ans)":
    if spo2 < 86 or gcs <= 8 or fc <= 60:
        decision_finale, couleur = "TRI 1 (ROUGE) : DÉTRESSE VITALE", "#c0392b"
    elif (age_mois <= 3 and temp >= 38.0) or fc >= 180 or temp >= 40.5:
        decision_finale, couleur = "TRI 2 (ORANGE) : ALERTE SEPSIS/CRITIQUE", "#e67e22"
else:
    if spo2 < 86 or gcs <= 8 or pas <= 70 or fc >= 180 or fc <= 40 or temp <= 32:
        decision_finale, couleur = "TRI 1 (ROUGE) : URGENCE VITALE", "#c0392b"
    elif pas <= 90 or (pas <= 100 and fc > 100) or (86 <= spo2 <= 90) or fc >= 130 or temp >= 40 or news2 >= 5:
        decision_finale, couleur = "TRI 2 (ORANGE) : URGENCE MAJEURE", "#e67e22"

with col2:
    st.subheader("🔍 Analyse par Motif")
    dico = REFERENTIEL_ADULTE if type_p == "Adulte" else REFERENTIEL_ENFANT
    cat = st.selectbox("Sélectionnez la catégorie", list(dico.keys()))
    
    questions = dico[cat]
    for q, res in questions:
        if st.checkbox(q):
            decision_finale = res
            if "ROUGE" in res: couleur = "#c0392b"
            elif "ORANGE" in res: couleur = "#e67e22"
            elif "JAUNE" in res: couleur = "#f1c40f"
            break

# --- AFFICHAGE DU RÉSULTAT FINAL ---
st.markdown("---")
st.markdown(f"""
    <div style="background-color:{couleur}; padding:30px; border-radius:15px; text-align:center; color:white;">
        <h1 style="margin:0;">{decision_finale}</h1>
        {"<h3>SCORE NEWS2 : " + str(news2) + " / 20</h3>" if type_p == "Adulte" else ""}
    </div>
    """, unsafe_allow_html=True)

if type_p == "Adulte" and news2 >= 5:
    st.error("⚠️ Alerte NEWS2 : Risque de dégradation élevé. Monitoring rapproché nécessaire.")s
    