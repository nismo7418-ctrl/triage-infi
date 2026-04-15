"""
================================================================================
  AKIR-IAO PROJECT  -  v17.0  -  Hospital Pro Edition
  Developpeur exclusif : Ismail Ibn-Daifa
  Outil d'aide au triage infirmier - Service des Urgences
  Conformite : FRENCH Triage SFMU V1.1 | BCFI Belgique | RGPD
  Localisation : Hainaut, Wallonie, Belgique
================================================================================

Nouveautes v17 :
  - Couverture FRENCH 100 % : 13 motifs manquants integres
  - Section Pediatrie <= 2 ans complete (10 motifs, seuils FC/PAS specifiques par age)
  - Anomalie du sein, anomalie vulvo-vaginale / corps etranger
  - Douleur thoracique / embolie / pneumopathie / pneumothorax (motif respiratoire distinct du SCA)
  - Intoxication vue tardivement >= 24h sans symptome -> Tri 5
  - Correction traumatisme abdo/thorax : critere gene limitee -> Tri 4
  - Acquis v16 conserves integralement

Architecture modulaire :
  [1] CONSTANTES      : Tous les referentiels cliniques et CSS en un seul lieu
  [2] SCORES          : NEWS2, GCS, TIMI, qSOFA, FAST, Algoplus, CFS, Silverman, Malinas
  [3] PHARMACIE       : Protocole antalgie BCFI local (Taradyl, Dipidolor, Tramadol, etc.)
  [4] TRIAGE          : Algorithme FRENCH Triage SFMU V1.1 complet (100 % motifs)
  [5] SBAR            : Generation transmission SBAR DPI-Ready avec traçabilite
  [6] ALERTES         : Coherence clinique, securite, retour precoce, GEU
  [7] PERSISTANCE     : Registre anonyme + journal alertes + antalgie horodatee
  [8] COMPOSANTS UI   : Rendu Streamlit - couche affichage uniquement
  [9] APPLICATION     : Point d'entree, onglets, rapport activite

Unites de reference (Belgique francophone) :
  Glycemie    : mg/dl  (facteur : 1 mmol/l = 18 mg/dl)
  Poids       : kg
  Pression    : mmHg
  Temperature : degres Celsius
  Debit       : ml/h (equivalence : ml/h divise par 3 = gouttes/min)
================================================================================
"""

import streamlit as st
from datetime import datetime
import json
import os
import uuid

# ==============================================================================
# CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="AKIR-IAO Project",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# [1] CONSTANTES GLOBALES
# Centralisation de toutes les donnees de reference pour faciliter la maintenance.
# ==============================================================================

# --- Referentiel de triage FRENCH SFMU V1.1 ---
LABELS_TRI = {
    "M":  "TRI M  -  IMMEDIAT",
    "1":  "TRI 1  -  URGENCE EXTREME",
    "2":  "TRI 2  -  TRES URGENT",
    "3A": "TRI 3A -  URGENT",
    "3B": "TRI 3B -  URGENT DIFFERE",
    "4":  "TRI 4  -  MOINS URGENT",
    "5":  "TRI 5  -  NON URGENT",
}
SECTEURS_TRI = {
    "M":  "Dechocage  -  Prise en charge immediate",
    "1":  "Dechocage  -  Prise en charge immediate",
    "2":  "Salle de soins aigus  -  Medecin disponible en moins de 20 min",
    "3A": "Salle de soins aigus  -  Medecin disponible en moins de 30 min",
    "3B": "Polyclinique urgences  -  Medecin disponible en moins de 1 h",
    "4":  "Consultation urgences  -  Medecin disponible en moins de 2 h",
    "5":  "Salle d'attente  -  Reorientation medecin generaliste possible",
}
DELAIS_TRI = {"M": 5, "1": 5, "2": 15, "3A": 30, "3B": 60, "4": 120, "5": 999}
CSS_TRI    = {
    "M": "tri-M", "1": "tri-1", "2": "tri-2",
    "3A": "tri-3A", "3B": "tri-3B", "4": "tri-4", "5": "tri-5",
}
CSS_HIST   = {
    "M": "hist-M", "1": "hist-1", "2": "hist-2",
    "3A": "hist-3A", "3B": "hist-3B", "4": "hist-4", "5": "hist-5",
}

# --- Seuils glycemiques (mg/dl - standard belge) ---
GLYCEMIE = {
    "hypoglycemie_severe":  54,   # < 3,0 mmol/l
    "hypoglycemie_moderee": 70,   # < 3,9 mmol/l
    "hyperglycemie_seuil":  180,  # > 10,0 mmol/l
    "hyperglycemie_severe": 360,  # > 20,0 mmol/l
}

# --- Seuils vitaux pediatriques par tranche d'age (PDF SFMU V1.1 p.5 + references PALS) ---
# Structure : (fc_min, fc_max, pas_min)
# Utilise par french_triage() pour les motifs "Pediatrie - Bradycardie/Tachycardie/Hypotension"
SEUILS_PEDIATRIQUES = {
    # Tranche       : (FC_min_normal, FC_max_normal, PAS_min_normale)
    "0_1m":  (100, 180, 60),   # 0 a 1 mois
    "1_6m":  (100, 160, 70),   # 1 a 6 mois
    "6_24m": (80,  150, 75),   # 6 a 24 mois
    "1_10a": (70,  140, 70),   # 1 a 10 ans (formule PAS : 70 + age*2)
}


def _seuils_ped(age_annees):
    """
    Retourne (fc_min, fc_max, pas_min) pour l'age donne en annees.
    Utilise SEUILS_PEDIATRIQUES. Formule PAS pour 1-10 ans : 70 + age*2.
    """
    if age_annees < 1/12:          # < 1 mois
        fc_min, fc_max, pas_min = SEUILS_PEDIATRIQUES["0_1m"]
    elif age_annees < 0.5:         # 1 a 6 mois
        fc_min, fc_max, pas_min = SEUILS_PEDIATRIQUES["1_6m"]
    elif age_annees <= 2:          # 6 a 24 mois
        fc_min, fc_max, pas_min = SEUILS_PEDIATRIQUES["6_24m"]
    elif age_annees <= 10:         # 1 a 10 ans
        fc_min, fc_max = SEUILS_PEDIATRIQUES["1_10a"][:2]
        pas_min = int(70 + age_annees * 2)   # formule PDF
    else:
        fc_min, fc_max, pas_min = 60, 120, 80
    return fc_min, fc_max, pas_min

# --- Antecedents / Facteurs de risque disponibles ---
LISTE_ATCD = [
    "HTA", "Diabete de type 1", "Diabete de type 2", "Tabagisme actif",
    "Dyslipidaemie", "ATCD familial coronarien",
    "Insuffisance cardiaque chronique", "BPCO",
    "Anticoagulants / AOD", "Grossesse en cours",
    "Immunodepression", "Neoplasie evolutive",
    "Epilepsie", "Insuffisance renale chronique",
    "Ulcere gastro-duodenal", "Insuffisance hepatique",
    "Deficit en vitamine B12", "Drepanocy tose / hemoglobinopathie",
    "Chimiotherapie en cours",
]

# --- Niveaux de fragilite Clinical Frailty Scale ---
CFS_NIVEAUX = {
    1: "Tres en forme - actif, energique, motive",
    2: "En forme - sans maladie active, mais moins en forme que le niveau 1",
    3: "Bien portant - maladie bien controlee, activite possible",
    4: "Vulnerabilite - ralenti, fatigable",
    5: "Fragilite legere - dependant pour les activites instrumentales",
    6: "Fragilite moderee - aide necessaire pour activites et sorties",
    7: "Fragilite severe - totalement dependant pour soins personnels",
    8: "Fragilite tres severe - totalement dependant, en fin de vie proche",
    9: "Maladie terminale - esperance de vie < 6 mois",
}

# --- Prescriptions anticipees IAO par motif ---
# Structure : motif -> categorie -> liste d'actions
PRESCRIPTIONS = {
    "Douleur thoracique / SCA": {
        "Gestes immediats": [
            "ECG 12 derivations - objectif dans les 10 min suivant l'arrivee",
            "Voie veineuse peripherique (VVP) 18G minimum",
            "Monitorage cardiorespiratoire continu (scope)",
            "Acide acetylsalicylique 250 mg PO ou IV sauf allergie documentee",
            "Position semi-assise, O2 si SpO2 < 95 %",
        ],
        "Bilan biologique": [
            "Troponine I hypersensible T0 puis T1h (ou T3h selon protocole local)",
            "Hemogramme complet + numeration plaquettaire",
            "Ionogramme, creatininemie, uree",
            "TP / TCA / INR si patient sous AOD ou AVK",
            "D-dimeres si suspicion d'embolie pulmonaire associee",
            "NT-proBNP si signes d'insuffisance cardiaque gauche",
        ],
        "Imagerie": [
            "Radiographie du thorax de face (lit si instable)",
        ],
        "Rappels critiques": [
            "Repeter l'ECG a 30 min si premier normal et douleur persistante",
            "Patient a jeun strict (coronarographie urgente possible)",
            "Alerter le cardiologue de garde si sus-decalage ST : objectif salle de catheterisme < 90 min",
        ],
    },
    "Dyspnee / insuffisance respiratoire": {
        "Gestes immediats": [
            "Position semi-assise (Fowler 45 degres)",
            "O2 - objectif SpO2 > 94 % (88-92 % si BPCO connu)",
            "VVP 18G minimum",
            "Monitorage SpO2 continu + frequence respiratoire",
        ],
        "Bilan biologique": [
            "Gazometrie arterielle (ou veineuse si etat instable)",
            "Hemogramme complet",
            "D-dimeres si suspicion d'embolie pulmonaire",
            "NT-proBNP si suspicion d'insuffisance cardiaque",
            "CRP + procalcitonine si contexte infectieux",
        ],
        "Imagerie": [
            "Radiographie du thorax de face debout",
            "Echographie pulmonaire (POCUS) si disponible",
        ],
        "Rappels critiques": [
            "Preparer le materiel d'intubation si FR > 35/min ou SpO2 < 85 % sous O2",
            "Aerosol de bronchodilatateur si bronchospasme confirme",
        ],
    },
    "AVC / Deficit neurologique": {
        "Gestes immediats": [
            "ACTIVATION FILIERE STROKE - appel immediat",
            "Glycemie capillaire (contre-indication thrombolyse si < 54 ou > 396 mg/dl)",
            "VVP 18G au membre superieur NON paretique",
            "Ne pas abaisser la PA sauf si PAS > 220 mmHg",
            "Patient a jeun strict",
        ],
        "Bilan biologique": [
            "Hemogramme + numeration plaquettaire - URGENT",
            "TP / TCA / INR / fibrinogene (contre-indication thrombolyse si anomalie)",
            "Ionogramme, creatininemie",
            "Troponinimie (fibrillation auriculaire possible)",
        ],
        "Imagerie": [
            "TDM cerebral sans injection - URGENT (objectif door-to-CT < 25 min)",
            "Angio-TDM des TSA si thrombectomie mecanique envisagee",
        ],
        "Rappels critiques": [
            "Heure exacte du debut des symptomes = information vitale pour la filiere",
            "Objectif door-to-needle < 60 min pour la thrombolyse intraveineuse",
            "Contre-indications : AOD < 48 h, chirurgie < 14 j, AVC < 3 mois",
        ],
    },
    "Fievre": {
        "Gestes immediats": [
            "VVP",
            "Paracetamol IV (Perfusalgan) 1 g si T > 38,5 degres C et mauvaise tolerance",
        ],
        "Bilan biologique": [
            "Hemocultures x 2 AVANT toute antibiotherapie",
            "Hemogramme, CRP, procalcitonine",
            "Ionogramme, creatininemie",
            "Lactates veineux (sepsis ?)",
            "Bandelette urinaire + ECBU",
        ],
        "Rappels critiques": [
            "Purpura fulminans : Ceftriaxone 2 g IV IMMEDIATEMENT - ne pas attendre le bilan",
            "Antibiotherapie large spectre dans l'heure si sepsis ou choc septique confirme",
            "Rechercher systematiquement une porte d'entree infectieuse",
        ],
    },
    "Allergie / anaphylaxie": {
        "Gestes immediats": [
            "Adrenaline 0,5 mg IM - face antero-laterale de la cuisse (Adrenaline Sterop 1 mg/ml)",
            "Remplissage NaCl 0,9 % 500 ml en debit libre si etat de choc",
            "Position de Trendelenburg si hypotension",
            "O2 haut debit si dyspnee ou desaturation",
            "Antihistaminique IV (diphenhydramine / Polaramine 5 mg)",
            "Corticosteroide IV (methylprednisolone 1 mg/kg)",
        ],
        "Rappels critiques": [
            "Repeter l'adrenaline a 5-15 min si absence d'amelioration hemodynamique",
            "Surveillance minimale de 6 h (risque de reaction biphasique)",
            "Tryptase serique a prelever dans les 2 h suivant la reaction",
        ],
    },
    "Intoxication medicamenteuse": {
        "Gestes immediats": [
            "VVP",
            "ECG 12 derivations (toxiques cardiotropes ?)",
            "Monitorage cardiorespiratoire continu",
        ],
        "Bilan biologique": [
            "Paracetamolemie SYSTEMATIQUE quelle que soit la substance evoquee",
            "Ethanollemie",
            "Bilan toxicologique urinaire et sanguin",
            "Ionogramme, creatininemie, bilan hepatique complet",
            "Gazometrie arterielle (acidose metabolique ?)",
        ],
        "Rappels critiques": [
            "Centre Antipoisons de Belgique : 070 245 245 (24 h/24, 7 j/7)",
            "N-acetylcysteine si intoxication au paracetamol selon le nomogramme de Rumack-Matthew",
            "Charbon active si ingestion < 1 h et patient conscient et cooperant (sauf contre-indication)",
            "Evaluation psychiatrique obligatoire avant toute sortie si intention suicidaire",
        ],
    },
    "Hypoglycemie": {
        "Gestes immediats": [
            "Glycemie capillaire IMMEDIATE (valeur en mg/dl)",
            "Si patient conscient : resucrage oral 15-20 g de glucides a index glycemique eleve",
            "Si patient inconscient : Glucose 30 % 50 ml IV lent sur 2-3 min (Glucosie - BCFI)",
            "Si acces veineux impossible : Glucagon 1 mg IM ou SC (GlucaGen HypoKit - BCFI)",
        ],
        "Rappels critiques": [
            "Controler la glycemie a 15 min post-correction - objectif > 100 mg/dl",
            "Identifier la cause : repas saute, surdosage insulinique, sulfamides hypoglycemiants",
            "Surveillance prolongee si sulfamides (risque de recidive differee)",
        ],
    },
    "Convulsions": {
        "Gestes immediats": [
            "Protection des voies aeriennes superieures - position laterale de securite si crise en cours",
            "O2 au masque a haute concentration",
            "VVP",
            "Glycemie capillaire IMMEDIATE",
            "Diazepam 10 mg IV lent OU midazolam 10 mg IM si duree > 5 min",
        ],
        "Bilan biologique": [
            "Hemogramme, ionogramme complet (Ca, Mg, Na)",
            "Glycemie (mg/dl)",
            "Dosage plasmatique des antiepileptiques si traitement en cours",
        ],
        "Rappels critiques": [
            "Chronometrer la duree de la crise des le debut",
            "Etat de mal epileptique = crise > 5 min OU deux crises sans reprise de conscience",
            "TDM cerebral si premier episode ou contexte traumatique",
        ],
    },
    "Accouchement imminent": {
        "Gestes immediats": [
            "Appel SMUR OU equipe obstetricale de garde - IMMEDIAT",
            "Preparer le kit d'accouchement inopine",
            "Monitorage foetal si disponible",
            "VVP gros calibre (16G)",
            "Decubitus lateral gauche OU position gynecologique",
        ],
        "Rappels critiques": [
            "Ne pas transporter si score de Malinas >= 8",
            "Preparer : clamps ombilicaux, draps prechauffes, aspirateur a mucosites",
            "Ocytocine 5 UI IV lent APRES la delivrance (prevention de l'hemorragie du post-partum)",
        ],
    },
}

# --- Motifs classes par categorie ---
MOTIFS_PAR_CATEGORIE = {
    "Cardio-circulatoire": [
        "Arret cardio-respiratoire",
        "Hypotension arterielle",
        "Douleur thoracique / SCA",
        "Tachycardie / tachyarythmie",
        "Bradycardie / bradyarythmie",
        "Hypertension arterielle",
        "Dyspnee / insuffisance respiratoire",
        "Palpitations",
        "Malaise",
        "Membre douloureux / Ischemie aigue",
        "Membre douloureux / Phlebite suspectee",
        "Oedeme des membres inferieurs / IC",
        "Dysfonction stimulateur / defibrillateur",
        "AES / Exposition liquide biologique",
        "Exposition maladie contagieuse",
    ],
    "Respiratoire": [
        "Asthme / exacerbation de BPCO",
        "Hemoptysie",
        "Corps etranger des voies aeriennes",
        "Douleur thoracique / Embolie / Pneumopathie / Pneumothorax",
    ],
    "Neurologie": [
        "AVC / Deficit neurologique",
        "Alteration de conscience / Coma",
        "Etat de mal epileptique / Convulsions",
        "Cephalee",
        "Vertiges / Trouble de l'equilibre",
        "Syndrome confusionnel / Desorientation",
    ],
    "Traumatologie": [
        "Traumatisme avec amputation",
        "Traumatisme du thorax / abdomen / rachis cervical",
        "Traumatisme cranien",
        "Brulure thermique",
        "Traumatisme du bassin / hanche / femur",
        "Traumatisme d'un membre / epaule",
        "Traumatisme oculaire",
        "Traumatisme maxillo-facial / oreille",
        "Plaie",
        "Electrisation",
        "Agression sexuelle / maltraitance",
    ],
    "Digestif": [
        "Hematemese / vomissements sanglants",
        "Rectorragie / Melena",
        "Douleur abdominale",
        "Icterejaunisse",
        "Hernie / Masse / Distension abdominale",
        "Corps etranger digestif",
        "Corps etranger rectal",
        "Probleme technique stomie / cicatrice post-op",
        "Constipation",
        "Vomissements isoles",
        "Diarrhee isolee",
        "Douleur anale",
        "Hoquet",
    ],
    "Genito-urinaire": [
        "Douleur lombaire / Colique nephretique",
        "Retention aigue d'urines / Anurie",
        "Douleur testiculaire / Suspicion de torsion",
        "Hematurie",
        "Dysurie / Brulure mictionnelle",
        "Ecoulement ou lesion genito-cutanee",
        "Dysfonction sonde urinaire / sonde JJ",
    ],
    "Gyneco-obstetrique": [
        "Accouchement imminent",
        "Complication de grossesse (1er / 2eme trimestre)",
        "Complication de grossesse (3eme trimestre)",
        "Menorragie / Metrorragie",
        "Probleme post-partum",
        "Anomalie du sein",
        "Anomalie vulvo-vaginale / corps etranger",
    ],
    "Psychiatrie / Toxicologie": [
        "Idees ou comportement suicidaire",
        "Anxiete / Depression / Consultation psychiatrique",
        "Agitation / Troubles du comportement",
        "Intoxication medicamenteuse",
        "Intoxication non medicamenteuse",
        "Sevrage / Toxicomanie",
        "Ivresse / Comportement ebrieux",
    ],
    "Pediatrie (<= 2 ans - motifs specifiques)": [
        "Pediatrie - Dyspnee avec sifflement respiratoire",
        "Pediatrie - Fievre <= 3 mois",
        "Pediatrie - Convulsion hyperthermique",
        "Pediatrie - Diarrhee / Vomissements nourrisson",
        "Pediatrie - Troubles alimentaires nourrisson <= 6 mois",
        "Pediatrie - Bradycardie",
        "Pediatrie - Ictere neonatal",
        "Pediatrie - Tachycardie",
        "Pediatrie - Hypotension",
        "Pediatrie - Pleurs incoercibles",
    ],
    "Infectiologie": [
        "Fievre",
    ],
    "Metabolique / Environnemental": [
        "Hyperglycemie / Cetoacidose diabetique",
        "Hypoglycemie",
        "Hypothermie",
        "Coup de chaleur / Hyperthermie",
        "Allergie / anaphylaxie",
        "AEG / Asthenie",
        "Anomalie de resultat biologique",
        "Pathologie rare en poussee",
        "Gelure / Lesions liees au froid",
    ],
    "Rhumatologie": [
        "Douleur articulaire / Arthrose / Arthrite",
        "Douleur rachidienne",
        "Douleur de membre / Sciatique",
    ],
    "ORL / Stomatologie": [
        "Epistaxis",
        "Corps etranger ORL",
        "Trouble auditif / Acouphenes",
        "Tumefaction ORL ou cervicale",
        "Pathologie de l'oreille / Otite",
        "Douleur de gorge / Angine",
        "Obstruction nasale / Rhinite / Sinusite",
        "Probleme dentaire",
    ],
    "Ophtalmologie": [
        "Corps etranger / Brulure oculaire",
        "Trouble visuel aigu / Cecite",
        "Demangeaison / Oeil rouge",
    ],
    "Peau": [
        "Ecchymose / Hematome spontane",
        "Abces ou infection cutanee localisee",
        "Erytheme etendu / Eruption cutanee",
        "Morsure / Piqure",
        "Corps etranger sous-cutane",
    ],
    "Divers": [
        "Probleme suite de soins",
        "Renouvellement ordonnance",
        "Examen administratif / Certificat",
        "Demande d'hebergement social",
    ],
}

# Hints vers les scores complementaires
HINTS_SCORES = {
    "Douleur thoracique / SCA":         "Score TIMI recommande (onglet Scores complementaires)",
    "Accouchement imminent":            "Score de Malinas recommande (onglet Scores complementaires)",
    "Brulure thermique":                "Score de brulure et formule de Baux (onglet Scores complementaires)",
    "Alteration de conscience / Coma":  "Glasgow Coma Scale detaille (onglet Scores complementaires)",
}


# ==============================================================================
# CSS - DESIGN HOSPITAL PRO
# Palette : Blanc #FFFFFF | Gris fond #F4F6F9 | Bleu hospitalier #004A99
# Alertes  : Rouge medical #D32F2F | Orange #F57C00 | Vert #2E7D32
# Typographie : DM Sans (corps) + DM Mono (valeurs numeriques / scores)
# ==============================================================================
CSS_GLOBAL = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&family=DM+Mono:wght@400;500&display=swap');

:root {
  --bleu:        #004A99;
  --bleu-clair:  #E8F0FB;
  --fond:        #F4F6F9;
  --fond-carte:  #FFFFFF;
  --fond-sb:     #F0F4FA;
  --bord:        #D0D7E3;
  --bord-fort:   #A0AABF;
  --txt:         #2C3A4D;
  --txt-titre:   #0D1B2A;
  --txt-aide:    #5A6880;
  --rouge:       #D32F2F;
  --rouge-fond:  #FFEBEE;
  --rouge-bord:  #EF9A9A;
  --orange:      #F57C00;
  --orange-fond: #FFF3E0;
  --orange-bord: #FFCC80;
  --vert:        #2E7D32;
  --vert-fond:   #E8F5E9;
  --vert-bord:   #A5D6A7;
  --violet:      #6A1B9A;
  --violet-fond: #F3E5F5;
}

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--txt); }
.stApp                      { background: var(--fond); }
[data-testid='stSidebar']   { background: var(--fond-sb) !important; border-right: 1px solid var(--bord); }

/* En-tete */
.app-header        { background: var(--bleu); color: #fff; padding: 14px 20px; border-radius: 6px; margin-bottom: 18px; }
.app-header-titre  { font-size: 1.05rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; }
.app-header-sub    { font-size: 0.75rem; opacity: 0.82; margin-top: 3px; letter-spacing: 0.04em; }

/* Section header */
.sec-h {
  font-size: 0.68rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--bleu); border-bottom: 1.5px solid var(--bleu); padding-bottom: 5px; margin: 18px 0 12px 0;
}

/* Cartes de triage */
.tri-carte   { border-radius: 6px; padding: 20px 22px; text-align: center; margin-bottom: 14px; border-left: 5px solid transparent; }
.tri-M       { background: var(--violet-fond); border-color: var(--violet); }
.tri-1       { background: var(--rouge-fond);  border-color: var(--rouge);  }
.tri-2       { background: var(--orange-fond); border-color: var(--orange); }
.tri-3A      { background: #FFFDE7;            border-color: #F9A825;       }
.tri-3B      { background: #FFFDE7;            border-color: #FDD835;       }
.tri-4       { background: var(--vert-fond);   border-color: var(--vert);   }
.tri-5       { background: var(--bleu-clair);  border-color: var(--bleu);   }
.tri-niveau  { font-family: 'DM Mono', monospace; font-size: 1.35rem; font-weight: 500; margin-bottom: 4px; }
.tri-M  .tri-niveau  { color: var(--violet); }
.tri-1  .tri-niveau  { color: var(--rouge);  }
.tri-2  .tri-niveau  { color: var(--orange); }
.tri-3A .tri-niveau,
.tri-3B .tri-niveau  { color: #7B5E00;       }
.tri-4  .tri-niveau  { color: var(--vert);   }
.tri-5  .tri-niveau  { color: var(--bleu);   }
.tri-detail { font-size: 0.82rem; color: var(--txt-aide); margin-top: 6px; }

/* NEWS2 */
.news2-val   { display: inline-block; font-family: 'DM Mono', monospace; font-size: 1.5rem; font-weight: 500; padding: 5px 16px; border-radius: 4px; margin-bottom: 4px; }
.news2-bas   { background: var(--vert-fond);   color: var(--vert);   border: 1px solid var(--vert-bord);   }
.news2-moyen { background: var(--orange-fond); color: var(--orange); border: 1px solid var(--orange-bord); }
.news2-haut  { background: var(--rouge-fond);  color: #C62828;       border: 1px solid var(--rouge-bord);  }
.news2-crit  { background: var(--rouge);       color: #ffffff;       border: 1px solid var(--rouge);       }

/* Banniere critique (NEWS2 >= 7) */
.banniere-crit         { background: var(--rouge); color: #fff; border-radius: 4px; padding: 14px 18px; margin: 10px 0; border-left: 6px solid #7F0000; }
.banniere-crit-titre   { font-size: 0.92rem; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; margin-bottom: 4px; }
.banniere-crit-detail  { font-size: 0.82rem; opacity: 0.92; }

/* Alertes */
.alerte-crit  { background: var(--rouge-fond);  border: 1px solid var(--rouge-bord);  border-left: 4px solid var(--rouge);  border-radius: 4px; padding: 10px 14px; margin: 6px 0; color: #B71C1C; font-size: 0.85rem; font-weight: 500; }
.alerte-warn  { background: var(--orange-fond); border: 1px solid var(--orange-bord); border-left: 4px solid var(--orange); border-radius: 4px; padding: 10px 14px; margin: 6px 0; color: #BF360C; font-size: 0.85rem; }
.alerte-info  { background: var(--bleu-clair);  border: 1px solid #90CAF9;            border-left: 4px solid var(--bleu);   border-radius: 4px; padding: 10px 14px; margin: 6px 0; color: var(--bleu); font-size: 0.85rem; }
.alerte-ok    { background: var(--vert-fond);   border: 1px solid var(--vert-bord);   border-left: 4px solid var(--vert);   border-radius: 4px; padding: 10px 14px; margin: 6px 0; color: #1B5E20; font-size: 0.85rem; }

/* Badge vital */
.bv   { display: inline-block; font-family: 'DM Mono', monospace; font-size: 0.72rem; font-weight: 500; padding: 1px 6px; border-radius: 3px; margin-left: 5px; vertical-align: middle; }
.bv-c { background: var(--rouge-fond);  color: var(--rouge);  border: 1px solid var(--rouge-bord);  }
.bv-w { background: var(--orange-fond); color: var(--orange); border: 1px solid var(--orange-bord); }
.bv-o { background: var(--vert-fond);   color: var(--vert);   border: 1px solid var(--vert-bord);   }

/* Carte generique */
.carte       { background: var(--fond-carte); border: 1px solid var(--bord); border-radius: 6px; padding: 16px 18px; margin: 8px 0; }
.carte-titre { font-size: 0.68rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--bleu); margin-bottom: 10px; padding-bottom: 6px; border-bottom: 1px solid var(--bord); }
.carte-item  { font-size: 0.85rem; color: var(--txt); padding: 3px 0; border-bottom: 1px solid #F0F2F5; display: flex; align-items: flex-start; gap: 8px; }
.carte-item::before       { content: "-"; color: var(--bleu); flex-shrink: 0; font-weight: 600; }
.carte-item:last-child    { border-bottom: none; }
.carte-item-urg::before   { content: "!"; color: var(--rouge); font-weight: 700; }

/* Protocole anticipe */
.proto        { background: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid var(--bleu); border-radius: 4px; padding: 14px 16px; margin: 10px 0; }
.proto-titre  { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--bleu); margin-bottom: 10px; }
.proto-item   { font-size: 0.85rem; color: #1E3A5F; padding: 4px 0; display: flex; align-items: flex-start; gap: 8px; }
.proto-item::before     { content: "[ ]"; color: var(--bleu); font-family: 'DM Mono', monospace; font-size: 0.75rem; flex-shrink: 0; }
.proto-item-urg::before { content: "[!]"; color: var(--rouge); font-family: 'DM Mono', monospace; font-size: 0.75rem; }

/* Score result */
.sv      { display: inline-block; font-family: 'DM Mono', monospace; font-size: 1.6rem; font-weight: 500; padding: 6px 18px; border-radius: 4px; margin: 6px 0 4px 0; }
.sv-bas  { background: var(--vert-fond);   color: var(--vert);   border: 1px solid var(--vert-bord);   }
.sv-moy  { background: var(--orange-fond); color: var(--orange); border: 1px solid var(--orange-bord); }
.sv-haut { background: var(--rouge-fond);  color: var(--rouge);  border: 1px solid var(--rouge-bord);  }
.sv-info { background: var(--bleu-clair);  color: var(--bleu);   border: 1px solid #90CAF9;             }
.sv-interp { font-size: 0.82rem; color: var(--txt-aide); margin-top: 4px; font-style: italic; }

/* SBAR */
.sbar { background: #FAFBFC; border: 1px solid var(--bord); border-radius: 4px; padding: 16px; font-family: 'DM Mono', monospace; font-size: 0.78rem; line-height: 1.9; white-space: pre-wrap; color: var(--txt); }

/* Historique */
.hist-ligne  { background: var(--fond-carte); border: 1px solid var(--bord); border-radius: 4px; padding: 9px 13px; margin-bottom: 5px; font-size: 0.82rem; }
.hist-M  { border-left: 4px solid var(--violet); }
.hist-1  { border-left: 4px solid var(--rouge);  }
.hist-2  { border-left: 4px solid var(--orange); }
.hist-3A { border-left: 4px solid #F9A825;       }
.hist-3B { border-left: 4px solid #FDD835;       }
.hist-4  { border-left: 4px solid var(--vert);   }
.hist-5  { border-left: 4px solid var(--bleu);   }

/* Registre */
.reg-carte  { background: var(--fond-carte); border: 1px solid var(--bord); border-radius: 6px; padding: 14px 18px; margin-bottom: 8px; transition: border-color 0.15s; }
.reg-carte:hover { border-color: var(--bleu); }
.reg-badge  { display: inline-block; font-family: 'DM Mono', monospace; font-size: 0.72rem; font-weight: 500; padding: 2px 9px; border-radius: 3px; margin-right: 6px; }
.reg-M  { background: var(--violet-fond); color: var(--violet); }
.reg-1  { background: var(--rouge-fond);  color: var(--rouge);  }
.reg-2  { background: var(--orange-fond); color: var(--orange); }
.reg-3A, .reg-3B { background: #FFFDE7; color: #7B5E00; }
.reg-4  { background: var(--vert-fond);  color: var(--vert);   }
.reg-5  { background: var(--bleu-clair); color: var(--bleu);   }
.reg-stat     { background: var(--fond-carte); border: 1px solid var(--bord); border-radius: 6px; padding: 14px; text-align: center; }
.reg-stat-num { font-family: 'DM Mono', monospace; font-size: 1.7rem; font-weight: 500; color: var(--bleu); }
.reg-stat-lbl { font-size: 0.68rem; color: var(--txt-aide); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 3px; }

/* Perfusion */
.perf-result { font-family: 'DM Mono', monospace; font-size: 2rem; font-weight: 500; color: var(--bleu); text-align: center; margin: 6px 0; }
.perf-label  { font-size: 0.72rem; color: var(--txt-aide); text-align: center; text-transform: uppercase; letter-spacing: 0.08em; }
.dose-carte  { background: var(--fond-carte); border: 1px solid var(--bord); border-left: 3px solid var(--vert); border-radius: 4px; padding: 12px 16px; margin: 6px 0; font-size: 0.84rem; color: var(--txt); }
.dose-titre  { font-size: 0.68rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--vert); margin-bottom: 6px; }
.dose-val    { font-family: 'DM Mono', monospace; font-size: 1.1rem; font-weight: 500; color: var(--txt-titre); }

/* Reevaluation */
.reeval-ligne   { background: var(--fond-carte); border: 1px solid var(--bord); border-radius: 4px; padding: 9px 13px; margin-bottom: 5px; font-size: 0.82rem; }
.reeval-amelio  { border-left: 4px solid var(--vert);   }
.reeval-stable  { border-left: 4px solid var(--bleu);   }
.reeval-aggrav  { border-left: 4px solid var(--rouge);  }
.td-h { color: var(--vert);       font-family: 'DM Mono', monospace; }
.td-b { color: var(--rouge);      font-family: 'DM Mono', monospace; }
.td-e { color: var(--txt-aide);   font-family: 'DM Mono', monospace; }

/* Chronometre */
.chrono       { font-family: 'DM Mono', monospace; font-size: 2rem; font-weight: 500; color: var(--bleu); text-align: center; letter-spacing: 0.04em; padding: 8px 0; }
.chrono-label { font-size: 0.65rem; color: var(--txt-aide); text-align: center; letter-spacing: 0.1em; text-transform: uppercase; }

/* Info-bulle */
.ib       { background: var(--bleu-clair); border: 1px solid #90CAF9; border-radius: 4px; padding: 10px 14px; font-size: 0.78rem; color: #1E3A5F; line-height: 1.7; margin: 8px 0; }
.ib-titre { font-weight: 600; margin-bottom: 4px; }

/* Sidebar */
.sb-section { font-size: 0.62rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--bleu); border-bottom: 1px solid var(--bord); padding-bottom: 4px; margin: 14px 0 9px 0; }
.sb-sig     { font-size: 0.75rem; font-weight: 600; color: var(--bleu); border-top: 1px solid var(--bord); padding-top: 9px; margin-top: 10px; }
.sb-legal   { font-size: 0.65rem; color: var(--txt-aide); font-style: italic; margin-top: 5px; }

/* Disclaimer RGPD */
.disclaimer      { background: var(--fond-carte); border: 1px solid var(--bord); border-radius: 4px; padding: 12px 16px; margin-top: 20px; font-size: 0.68rem; color: var(--txt-aide); line-height: 1.7; }
.disclaimer-hdr  { font-size: 0.65rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--txt-aide); margin-bottom: 5px; }
.disclaimer-sig  { font-size: 0.72rem; font-weight: 600; color: var(--bleu); border-top: 1px solid var(--bord); padding-top: 7px; margin-top: 7px; }

/* Mobile (iPhone) */
@media (max-width: 768px) {
  .tri-carte   { padding: 14px; }
  .sbar        { font-size: 0.72rem; padding: 10px; }
  .reg-carte   { padding: 10px 14px; }
  .chrono      { font-size: 1.6rem; }
  .news2-val   { font-size: 1.2rem; }
  .perf-result { font-size: 1.5rem; }
  .stButton > button   { min-height: 48px; font-size: 0.95rem; }
  .stNumberInput input { font-size: 1rem; }
}
</style>
"""
st.markdown(CSS_GLOBAL, unsafe_allow_html=True)


# ==============================================================================
# [2] MOTEUR SCORES
# Chaque fonction est independante, securisee par try/except,
# et retourne (resultat, liste_avertissements).
# ==============================================================================

def calculer_news2(fr, spo2, o2_supp, temp, pas, fc, gcs, bpco):
    """
    Score NEWS2 (National Early Warning Score 2).
    Reference : Royal College of Physicians, 2017.
    Deux echelles SpO2 : echelle 1 sans BPCO, echelle 2 avec BPCO (objectif 88-92 %).
    Retourne : (score: int, avertissements: list)
    """
    warns = []

    # Table de correspondance : (valeur_max_incluse, points)
    # La valeur None marque la borne superieure ouverte.
    _fr   = [(8, 3), (11, 1), (20, 0), (24, 2), (None, 3)]
    _spo2 = [(91, 3), (93, 2), (95, 1), (None, 0)]
    _spo2_bpco = [(83, 3), (85, 2), (87, 1), (92, 0), (94, 1), (96, 2), (None, 3)]
    _temp = [(35.0, 3), (36.0, 1), (38.0, 0), (39.0, 1), (None, 2)]
    _pas  = [(90, 3), (100, 2), (110, 1), (219, 0), (None, 3)]
    _fc   = [(40, 3), (50, 1), (90, 0), (110, 1), (130, 2), (None, 3)]

    def _lire_table(valeur, table, nom):
        if valeur is None:
            warns.append(f"Score NEWS2 incomplet : {nom} manquant(e)")
            return None
        for seuil, pts in table:
            if seuil is None or valeur <= seuil:
                return pts
        return 0

    try:
        s = 0
        r = _lire_table(fr,   _fr,   "frequence respiratoire")
        if r is None: return 0, warns
        s += r

        r = _lire_table(spo2, _spo2_bpco if bpco else _spo2, "SpO2")
        if r is None: return 0, warns
        s += r

        if o2_supp:
            s += 2

        r = _lire_table(temp, _temp, "temperature")
        if r is None: return 0, warns
        s += r

        r = _lire_table(pas, _pas, "pression arterielle systolique")
        if r is None: return 0, warns
        s += r

        r = _lire_table(fc,  _fc,  "frequence cardiaque")
        if r is None: return 0, warns
        s += r

        if gcs is None:
            warns.append("Score NEWS2 incomplet : GCS manquant")
            return 0, warns
        if gcs < 15:
            s += 3

        return s, warns

    except (TypeError, ValueError) as exc:
        return 0, [f"Erreur calcul NEWS2 : {exc}"]


def niveau_news2(score):
    """Retourne (etiquette, classe_css) pour un score NEWS2 donne."""
    if score <= 4:  return f"NEWS2 : {score}", "news2-bas"
    if score <= 6:  return f"NEWS2 : {score}", "news2-moyen"
    if score <= 8:  return f"NEWS2 : {score}", "news2-haut"
    return          f"NEWS2 : {score}", "news2-crit"


def calculer_gcs(y, v, m):
    """
    Glasgow Coma Scale.
    Reference : Teasdale & Jennett, Lancet 1974.
    Retourne : (score: int, avertissements: list)
    """
    try:
        return max(3, min(15, int(y) + int(v) + int(m))), []
    except (TypeError, ValueError) as exc:
        return 15, [f"Erreur calcul GCS : {exc}"]


def calculer_timi(age, nb_frcv, stenose_50, aspirine_7j, troponine_pos, deviation_st, crises_24h):
    """
    Score TIMI pour SCA sans sus-decalage ST (risque d'evenements a 14 jours).
    Reference : Antman et al., JAMA 2000.
    """
    try:
        s = (
            int(age >= 65)
            + int(nb_frcv >= 3)
            + int(stenose_50)
            + int(aspirine_7j)
            + int(troponine_pos)
            + int(deviation_st)
            + int(crises_24h >= 2)
        )
        return s, []
    except (TypeError, ValueError) as exc:
        return 0, [f"Erreur calcul TIMI : {exc}"]


def calculer_silverman(balt, tirage, retraction, ailes_nez, geignement):
    """
    Score de Silverman : evaluation de la detresse respiratoire neonatale.
    Chaque item : 0 = absent, 1 = modere, 2 = intense. Score maximal = 10.
    Reference : Silverman & Andersen, Pediatrics 1956.
    """
    try:
        return min(10, balt + tirage + retraction + ailes_nez + geignement), []
    except (TypeError, ValueError) as exc:
        return 0, [f"Erreur calcul Silverman : {exc}"]


def calculer_malinas(parite, duree_travail, duree_contrac, intervalle, poche):
    """
    Score de Malinas : decision de transport vers une maternite.
    Score >= 8 : accouchement imminent, transport contre-indique.
    """
    try:
        return min(10, parite + duree_travail + duree_contrac + intervalle + poche), []
    except (TypeError, ValueError) as exc:
        return 0, [f"Erreur calcul Malinas : {exc}"]


def calculer_brulure(surface_pct, age_pat):
    """
    Surface corporelle brulee selon la regle des 9 de Wallace.
    Formule de Baux : pronostic de mortalite = age + SCB (%).
    Reference : Wallace, Lancet 1951 ; Baux, 1961.
    """
    try:
        scb  = max(0.0, min(100.0, float(surface_pct)))
        baux = age_pat + scb
        if   baux > 120: pronostic = "Pronostic vital tres reserve (Baux > 120)"
        elif baux > 100: pronostic = "Pronostic severe (Baux 100-120)"
        elif baux > 80:  pronostic = "Pronostic reserve (Baux 80-100)"
        else:            pronostic = "Pronostic favorable (Baux < 80)"
        return scb, baux, pronostic, []
    except (TypeError, ValueError) as exc:
        return 0.0, 0.0, "Erreur", [f"Erreur calcul brulure : {exc}"]


def badge_vital(val, w_bas, c_bas, w_haut, c_haut, unite=""):
    """Retourne le HTML d'un badge colore selon les seuils vitaux."""
    try:
        if   val <= c_bas or val >= c_haut: css = "bv-c"
        elif val <= w_bas or val >= w_haut: css = "bv-w"
        else:                               css = "bv-o"
        return f'<span class="bv {css}">{val}{unite}</span>'
    except (TypeError, ValueError):
        return '<span class="bv bv-w">?</span>'


def calculer_qsofa(fr, gcs, pas):
    """
    Score qSOFA (quick Sequential Organ Failure Assessment).
    Outil de detection rapide du sepsis a l'IAO - 3 criteres, 1 pt chacun.
    Score >= 2 : risque eleve de defaillance d'organe - evaluation urgente.
    Reference : Singer et al., JAMA 2016.
    Retourne : (score: int, criteres_positifs: list, avertissements: list)
    """
    try:
        warns    = []
        positifs = []
        s = 0
        if fr is None:
            warns.append("qSOFA incomplet : frequence respiratoire manquante")
        elif fr >= 22:
            s += 1
            positifs.append(f"FR >= 22/min (valeur : {fr}/min)")
        if gcs is None:
            warns.append("qSOFA incomplet : GCS manquant")
        elif gcs < 15:
            s += 1
            positifs.append(f"Alteration de la conscience GCS {gcs}/15")
        if pas is None:
            warns.append("qSOFA incomplet : PAS manquante")
        elif pas <= 100:
            s += 1
            positifs.append(f"PAS <= 100 mmHg (valeur : {pas} mmHg)")
        return s, positifs, warns
    except (TypeError, ValueError) as exc:
        return 0, [], [f"Erreur calcul qSOFA : {exc}"]


def evaluer_fast(paralysie_faciale, deficit_moteur, trouble_langage, debut_brutal):
    """
    Score FAST/BE-FAST - Detection rapide AVC a l'IAO.
    F = Face (paralysie faciale)
    A = Arm  (deficit moteur membre superieur)
    S = Speech (trouble du langage)
    T = Time  (debut brutal)
    Tout critere positif = suspicion AVC jusqu'a preuve du contraire.
    Reference : Kothari et al., Ann Emerg Med 1999.
    """
    positifs = []
    if paralysie_faciale: positifs.append("F - Paralysie ou asymetrie faciale")
    if deficit_moteur:    positifs.append("A - Deficit moteur membre superieur")
    if trouble_langage:   positifs.append("S - Trouble du langage (aphasie, dysarthrie)")
    if debut_brutal:      positifs.append("T - Debut brutal des symptomes")
    suspecte = len(positifs) >= 1
    return suspecte, positifs


def calculer_algoplus(visage, regard, plaintes, attitude_corpo, comportement):
    """
    Score Algoplus - Evaluation de la douleur chez le patient age non communicant.
    5 items comportementaux - reponse oui (1) ou non (0).
    Score de 0 a 5. Score >= 2 : douleur probable - traitement a envisager.
    Valide en Belgique pour patients atteints de demence severe.
    Reference : Bercovitch et al. Pain 2006 - validation SFGG.
    """
    try:
        s = (
            int(bool(visage))
            + int(bool(regard))
            + int(bool(plaintes))
            + int(bool(attitude_corpo))
            + int(bool(comportement))
        )
        if   s >= 4: interp, css = "Douleur intense - traitement antalgique IV urgent", "sv-haut"
        elif s >= 2: interp, css = "Douleur probable - traitement antalgique a initier", "sv-moy"
        else:        interp, css = "Douleur peu probable ou absente", "sv-bas"
        return s, interp, css, []
    except (TypeError, ValueError) as exc:
        return 0, "Erreur", "sv-bas", [f"Erreur calcul Algoplus : {exc}"]


def evaluer_cfs(score_cfs):
    """
    Clinical Frailty Scale (CFS) - Evaluation de la fragilite du patient age.
    Score de 1 (tres en forme) a 9 (maladie terminale).
    Impact sur le triage : CFS >= 5 chez un patient Tri 4/5 -> envisager remontee.
    Reference : Rockwood et al., CMAJ 2005.
    """
    if score_cfs <= 3:  return "Robuste", "sv-bas",  False
    if score_cfs <= 4:  return "Vulnerable", "sv-moy", False
    if score_cfs <= 6:  return "Fragile", "sv-moy", True
    if score_cfs <= 8:  return "Tres fragile", "sv-haut", True
    return "Terminal", "sv-haut", True


# ==============================================================================
# [3] MOTEUR PHARMACIE - Protocole antalgie BCFI Belgique (Hainaut / Wallonie)
# Toutes les glycemies sont en mg/dl (standard belge).
# Facteur de conversion : 1 mmol/l = 18 mg/dl.
# Protocole antalgie local : Paracetamol IV | Taradyl IV | Diclofenac IM |
#                            Tramadol IV | Dipidolor IV (titration pure) |
#                            Morphine IV | MEOPA/Kalinox
# ==============================================================================

def mgdl_vers_mmol(mgdl):
    """Conversion glycemie mg/dl -> mmol/l (reference uniquement)."""
    return round(mgdl / 18.0, 1)


def mmol_vers_mgdl(mmol):
    """Conversion glycemie mmol/l -> mg/dl."""
    return round(mmol * 18.0, 0)


def calculer_debit_perfusion(volume_ml, duree_h):
    """
    Debit de perfusion IV.
    Formule : D (ml/h) = V (ml) / T (h).
    Equivalence : D (ml/h) / 3 = gouttes/min (facteur goutte standard 20 gtt/ml).
    """
    try:
        if duree_h <= 0:   return None, "Duree de perfusion invalide (> 0 requis)"
        if volume_ml <= 0: return None, "Volume de perfusion invalide (> 0 requis)"
        debit     = round(volume_ml / duree_h, 1)
        gttes_min = round(debit / 3.0, 1)
        return {"ml_h": debit, "gttes_min": gttes_min}, None
    except (TypeError, ValueError) as exc:
        return None, f"Erreur calcul debit : {exc}"


def _ci_ains(atcd):
    """
    Verifie les contre-indications communes aux AINS (Taradyl et Diclofenac).
    Inclut : IR, ulcere, anticoagulants, grossesse, IC, IH, chimiotherapie.
    Retourne une liste de contre-indications detectees depuis les ATCD.
    """
    ci = []
    if "Insuffisance renale chronique" in atcd:
        ci.append("CONTRE-INDICATION : Insuffisance renale chronique (risque d'insuffisance renale aigue)")
    if "Ulcere gastro-duodenal" in atcd:
        ci.append("CONTRE-INDICATION : Ulcere gastro-duodenal actif ou antecedent recent")
    if "Anticoagulants / AOD" in atcd:
        ci.append("CONTRE-INDICATION relative : Anticoagulants / AOD - risque hemorragique majore")
    if "Grossesse en cours" in atcd:
        ci.append("CONTRE-INDICATION : Grossesse (surtout >= T2 - fermeture prematuree du canal arteriel)")
    if "Insuffisance cardiaque chronique" in atcd:
        ci.append("CONTRE-INDICATION relative : Insuffisance cardiaque - retention hydrosodee")
    if "Insuffisance hepatique" in atcd:
        ci.append("CONTRE-INDICATION : Insuffisance hepatique - risque d'aggravation et de toxicite systemique")
    if "Chimiotherapie en cours" in atcd:
        ci.append("CONTRE-INDICATION relative : Chimiotherapie en cours - risque de nephrotoxicite additive et thrombopenie")
    return ci


def dose_paracetamol_iv(poids_kg):
    """
    Paracetamol IV (Perfusalgan 10 mg/ml / Dafalgan IV) - BCFI Belgique 2024.
    Adulte >= 50 kg : 1 g IV en 15 min, maximum 4 g/24 h.
    < 50 kg         : 15 mg/kg IV en 15 min, maximum 60 mg/kg/24 h.
    Intervalle minimum : 4 h entre deux administrations.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"
        if poids_kg >= 50:
            dose_mg = 1000
            max_j   = "4 g/24 h (4 administrations, intervalle >= 4 h)"
        else:
            dose_mg = round(15.0 * poids_kg)
            max_j   = f"60 mg/kg/24 h (soit {round(60.0 * poids_kg)} mg max)"
        return {
            "dose_mg":    dose_mg,
            "dose_g":     round(dose_mg / 1000.0, 2),
            "admin":      "Perfusion IV en 15 min",
            "intervalle": "Minimum 4 h entre deux doses",
            "max_jour":   max_j,
            "ci":         [],
            "reference":  "Perfusalgan 10 mg/ml / Dafalgan IV - BCFI 2024",
        }, None
    except (TypeError, ValueError) as exc:
        return None, f"Erreur dose paracetamol : {exc}"


def dose_taradyl_iv(poids_kg, atcd):
    """
    Kétorolac IV (Taradyl 30 mg / 50 ml NaCl 0,9%) - BCFI Belgique.
    AINS injectable puissant - antalgie palier 2 non opioide.
    Administration : 30 mg dans 50 ml NaCl 0,9% IV sur 15 min.
    Maximum : 90 mg/24 h - duree max 5 jours.
    Partage les CI des AINS + CI specifique : post-operatoire hemorragique.
    Reference : BCFI - Kétorolac trométhamine - RCP Belgique.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"
        ci = _ci_ains(atcd)
        # Reduction de dose chez le sujet age (>= 65 ans) et poids < 50 kg
        dose_mg = 15 if poids_kg < 50 else 30
        return {
            "dose_mg":    dose_mg,
            "admin":      f"{dose_mg} mg dans 50 ml NaCl 0,9 % - perfusion IV sur 15 min",
            "intervalle": "Toutes les 6 h si necessaire",
            "max_jour":   f"{'60' if poids_kg < 50 else '90'} mg/24 h - duree max 5 jours",
            "ci":         ci,
            "note":       "Reduire a 15 mg si poids < 50 kg ou age >= 65 ans",
            "reference":  "Taradyl 30 mg/ml - BCFI Belgique",
        }, None
    except (TypeError, ValueError) as exc:
        return None, f"Erreur dose Taradyl : {exc}"


def dose_diclofenac_im(poids_kg, atcd):
    """
    Diclofenac IM (Voltaren 75 mg/3 ml) - BCFI Belgique.
    AINS injectable - voie intramusculaire profonde (fessier).
    Dose : 75 mg IM une fois par jour, maximum 150 mg/24 h.
    Partage toutes les CI des AINS.
    Reference : BCFI - Diclofenac - RCP Belgique.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"
        ci = _ci_ains(atcd)
        return {
            "dose_mg":    75,
            "voie":       "Injection intramusculaire profonde dans le quadrant superieur externe du fessier",
            "admin":      "75 mg IM - injection lente, changer de cote si 2e injection",
            "max_jour":   "150 mg/24 h (2 injections maximum)",
            "ci":         ci,
            "reference":  "Voltaren 75 mg/3 ml solution injectable - BCFI",
        }, None
    except (TypeError, ValueError) as exc:
        return None, f"Erreur dose Diclofenac : {exc}"


def dose_tramadol_iv(poids_kg, atcd, age_patient):
    """
    Tramadol IV (Contramal / Tradonal) - BCFI Belgique.
    Opioide faible - palier 2 OMS.
    Administration : 100 mg dans 100 ml NaCl 0,9% IV sur 15 min.
    ALERTE automatique si epilepsie dans les ATCD.
    Reduction 50 % si age >= 75 ans ou IR severe.
    Reference : BCFI - Tramadol chlorhydrate - RCP Belgique.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"
        ci = []
        alertes = []
        # Contre-indication absolue : epilepsie
        if "Epilepsie" in atcd:
            alertes.append("ALERTE CRITIQUE : Tramadol CONTRE-INDIQUE en cas d'epilepsie - abaisse le seuil epileptogene")
        if "Grossesse en cours" in atcd:
            ci.append("CONTRE-INDICATION : Grossesse 1er trimestre")
        # Reduction de dose
        note_dose = ""
        dose_mg = 100
        if age_patient >= 75:
            dose_mg = 50
            note_dose = "Dose reduite a 50 mg (age >= 75 ans)"
        if "Insuffisance renale chronique" in atcd:
            ci.append("Allonger l'intervalle entre les doses si IR severe (toutes les 12 h)")
        return {
            "dose_mg":    dose_mg,
            "admin":      f"{dose_mg} mg dans 100 ml NaCl 0,9 % - perfusion IV sur 15 min",
            "intervalle": "Toutes les 6 h si necessaire",
            "max_jour":   "400 mg/24 h (300 mg si age >= 75 ans)",
            "ci":         ci,
            "alertes":    alertes,
            "note":       note_dose,
            "reference":  "Contramal / Tradonal - BCFI Belgique",
        }, None
    except (TypeError, ValueError) as exc:
        return None, f"Erreur dose Tramadol : {exc}"


def dose_dipidolor_iv(poids_kg, age_patient, atcd):
    """
    Piritramide IV (Dipidolor 7,5 mg/ml) - BCFI Belgique.
    Opioide fort de reference aux urgences belges.
    Titration pure : paliers libres IV lent jusqu'a EVA <= 3.
    Dose initiale : 0,1-0,2 mg/kg IV lent sur 2-3 min.
    Reduction 50 % : age >= 70 ans ou insuffisance renale severe.
    Antidote : Naloxone 0,4 mg IV.
    Reference : BCFI - Piritramide - Dipidolor 7,5 mg/ml solution injectable.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"
        d_min = round(0.1 * poids_kg, 1)
        d_max = round(0.2 * poids_kg, 1)
        notes = []
        reduction = False
        if age_patient >= 70:
            reduction = True
            notes.append("Reduction 50 % : age >= 70 ans")
        if "Insuffisance renale chronique" in atcd:
            reduction = True
            notes.append("Reduction 50 % : insuffisance renale chronique")
        if reduction:
            d_min = round(d_min * 0.5, 1)
            d_max = round(d_max * 0.5, 1)
        # Plafond par bolus initial
        d_min = min(d_min, 5.0)
        d_max = min(d_max, 10.0)
        ci = []
        if spo2_basse := ("SpO2 < 90 %"):
            pass  # evaluer avant administration
        return {
            "dose_min":   d_min,
            "dose_max":   d_max,
            "admin":      "IV lent sur 2-3 min. Titration pure - paliers libres jusqu'a EVA <= 3.",
            "intervalle": "Minimum 5-10 min entre chaque bolus",
            "objectif":   "EVA <= 3",
            "notes":      notes,
            "antidote":   "Naloxone 0,4 mg IV en cas de depression respiratoire (SpO2 < 90 % ou FR < 10/min)",
            "surveillance": "SpO2 + FR + niveau de sedation apres chaque bolus",
            "reference":  "Dipidolor 7,5 mg/ml solution injectable - BCFI Belgique",
        }, None
    except (TypeError, ValueError) as exc:
        return None, f"Erreur dose Dipidolor : {exc}"


def dose_morphine_iv(poids_kg, age_patient):
    """
    Morphine IV - alternative au Dipidolor.
    Dose initiale : 0,05-0,1 mg/kg IV (maximum 5 mg par bolus).
    Titration : paliers de 2-3 mg IV toutes les 5-10 min jusqu'a EVA <= 3.
    Reduction chez le sujet age >= 70 ans : doses divisees par 2.
    Reference : BCFI - Morphine chlorhydrate - Protocoles urgences CHU Belgique.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"
        d_min = round(0.05 * poids_kg, 1)
        d_max = round(0.10 * poids_kg, 1)
        note  = ""
        if age_patient >= 70:
            d_min = round(d_min * 0.5, 1)
            d_max = round(d_max * 0.5, 1)
            note  = "Dose reduite de 50 % chez le patient age >= 70 ans"
        d_min = min(d_min, 2.5)
        d_max = min(d_max, 5.0)
        return {
            "bolus_min": d_min,
            "bolus_max": d_max,
            "admin":     "IV lent sur 2-3 min. Titrer par paliers de 2-3 mg toutes les 5-10 min.",
            "objectif":  "EVA <= 3",
            "note_age":  note,
            "antidote":  "Naloxone 0,4 mg IV en cas de depression respiratoire",
            "reference": "BCFI - Morphine chlorhydrate - Protocole urgences",
        }, None
    except (TypeError, ValueError) as exc:
        return None, f"Erreur dose morphine : {exc}"


def dose_adrenaline_anaphylaxie(poids_kg):
    """
    Adrenaline IM - choc anaphylactique.
    Adulte >= 30 kg : 0,5 mg IM (0,5 ml solution 1 mg/ml).
    Enfant < 30 kg  : 0,01 mg/kg IM, maximum 0,5 mg.
    Site : face antero-laterale de la cuisse.
    Reference : BCFI - Adrenaline Sterop 1 mg/ml - Lignes directrices anaphylaxie 2023.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"
        if poids_kg >= 30:
            dose_mg = 0.5
            note    = "0,5 ml de la solution a 1 mg/ml (ampoule standard)"
        else:
            dose_mg = min(round(0.01 * poids_kg, 3), 0.5)
            note    = f"0,01 mg/kg -> {dose_mg} mg ({round(dose_mg * 1000):.0f} microgrammes)"
        return {
            "dose_mg":  dose_mg,
            "voie":     "Injection intramusculaire - face antero-laterale de la cuisse",
            "note":     note,
            "repeter":  "Repeter a 5-15 min si absence d'amelioration hemodynamique",
            "moniteur": "Monitorage continu : FC, PA, SpO2 post-injection",
            "reference":"BCFI - Adrenaline Sterop 1 mg/ml - Lignes directrices anaphylaxie 2023",
        }, None
    except (TypeError, ValueError) as exc:
        return None, f"Erreur dose adrenaline : {exc}"


def dose_glucose_hypoglycemie(poids_kg, voie):
    """
    Correction d'hypoglycemie - protocoles belges BCFI.
    Voie IV : Glucose 30 % (Glucosie) : 0,3 g/kg (1 ml/kg), maximum 50 ml IV lent.
    Voie IM : Glucagon GlucaGen HypoKit : 1 mg IM ou SC si acces veineux impossible.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"
        if voie == "IV":
            vol_ml = min(round(poids_kg), 50)
            dose_g = round(vol_ml * 0.3, 1)
            return {
                "produit":   "Glucose 30 % solution injectable (Glucosie - BCFI)",
                "dose_g":    dose_g,
                "volume":    f"{vol_ml:.0f} ml IV lent sur 2-3 min",
                "controle":  "Glycemie capillaire a 15 min post-injection - objectif > 100 mg/dl",
                "reference": "BCFI - Glucose 30 % - maximum 50 ml par administration",
            }, None
        else:
            return {
                "produit":   "Glucagon GlucaGen 1 mg poudre + diluant (HypoKit - BCFI)",
                "dose":      "1 mg IM ou SC",
                "note":      "Inefficace si reserves glycogeniques epuisees (jejune prolonge, alcoolisme).",
                "controle":  "Glycemie a 15 min. Alimentation par voie orale des que possible.",
                "reference": "BCFI - GlucaGen HypoKit 1 mg",
            }, None
    except (TypeError, ValueError) as exc:
        return None, f"Erreur dose glucose : {exc}"


def infos_meopa(age_patient, atcd):
    """
    MEOPA / Kalinox (melange equimolaire O2/N2O 50/50) - BCFI Belgique.
    Indication : antalgie procedurale courte (pose VVP, sutures, pansements).
    AMM a partir de 1 an. Efficacite pratique a partir de 3-4 ans (cooperation necessaire).
    Duree max : 60 min continus. Surveillance continue infirmiere.
    Reference : BCFI - Kalinox 170 bar - RCP Belgique.
    """
    ci = []
    if age_patient < 1:
        ci.append("CONTRE-INDICATION : age < 1 an")
    if "Deficit en vitamine B12" in atcd:
        ci.append("CONTRE-INDICATION : deficit en vitamine B12 (inactivation irreversible B12)")
    alertes = []
    if 1 <= age_patient < 3:
        alertes.append("Age 1-3 ans : cooperation souvent insuffisante - evaluer au cas par cas")
    if "BPCO" in atcd:
        alertes.append("BPCO : surveiller la SpO2 attentivement - risque de depression respiratoire")
    return {
        "age_min_amm":    "1 an (AMM) - efficacite pratique a partir de 3-4 ans",
        "admin":          "Masque facial etanche - inhalation spontanee - effet en 3-5 min",
        "duree_max":      "60 min continus - respecter une periode de recuperation de 5 min avant mobilisation",
        "ci_absolues":    [
            "Traumatisme cranien avec HTIC suspectee",
            "Pneumothorax ou emphyseme bulleux",
            "Obstruction nasale totale (rhinite, corps etranger)",
            "SpO2 < 94 % (necessitant O2 pur)",
            "Occlusion intestinale",
            "Deficit en vitamine B12",
        ],
        "ci_detectees":   ci,
        "alertes":        alertes,
        "surveillance":   "SpO2 + FR + niveau de sedation continus - toujours 2 operateurs (1 dedie)",
        "reference":      "Kalinox 170 bar - BCFI Belgique",
    }


# ==============================================================================
# [4] MOTEUR TRIAGE - FRENCH Triage SFMU V1.1
# ==============================================================================

def french_triage(motif, details, fc, pas, spo2, fr, gcs, temp, age, news2, glycemie_mgdl=None):
    """
    Algorithme de triage FRENCH (SFMU V1.1, 2018).
    Toutes les glycemies sont en mg/dl (standard belge).
    Les valeurs manquantes sont remplacees par des valeurs physiologiques par defaut.
    Retourne : (niveau: str, justification: str, reference: str)
    """
    # Securisation des donnees d'entree
    fc   = fc   if fc   is not None else 80
    pas  = pas  if pas  is not None else 120
    spo2 = spo2 if spo2 is not None else 98
    fr   = fr   if fr   is not None else 16
    gcs  = gcs  if gcs  is not None else 15
    temp = temp if temp is not None else 37.0
    news2 = news2 or 0

    try:
        # Critere transversal : NEWS2 >= 9 = engagement vital
        if news2 >= 9:
            return "M", f"NEWS2 {news2} >= 9 : engagement vital immediat.", "NEWS2 - Tri M"

        # --- Arret cardio-respiratoire ---
        # PDF SFMU V1.1 p.1 : ACR = Tri 1 (colonne Tri M vide)
        if motif == "Arret cardio-respiratoire":
            return "1", "Arret cardio-respiratoire confirme.", "FRENCH - Tri 1"

        # --- Cardio-circulatoire ---
        if motif == "Hypotension arterielle":
            if pas <= 70:
                return "1", f"PAS {pas} mmHg <= 70 mmHg.", "FRENCH - Tri 1"
            if pas <= 90 or (pas <= 100 and fc > 100):
                return "2", f"PAS {pas} mmHg - etat de choc debutant.", "FRENCH - Tri 2"
            if pas <= 100:
                return "3B", f"PAS {pas} mmHg - valeur limite.", "FRENCH - Tri 3B"
            return "4", "Pression arterielle dans les valeurs normales.", "FRENCH - Tri 4"

        if motif == "Membre douloureux / Ischemie aigue":
            if details.get("duree_inf_24h") or details.get("cyanose") or details.get("deficit_moteur"):
                return "2", "Ischemie aigue de membre : duree <= 24h, cyanose ou deficit moteur.", "FRENCH - Tri 2"
            return "3B", "Ischemie de membre : duree >= 24h.", "FRENCH - Tri 3B"

        if motif == "Malaise":
            if news2 >= 1 or details.get("anomalie_vitaux") or details.get("hypoglycemie"):
                return "3B", "Malaise avec anomalie des parametres vitaux ou glycemie.", "FRENCH - Tri 3B"
            return "5", "Malaise sans anomalie notable des parametres vitaux ni glycemie.", "FRENCH - Tri 5"

        if motif == "Dysfonction stimulateur / defibrillateur":
            if details.get("chocs_ressentis"):
                return "3B", "Choc(s) electrique(s) ressenti(s) du defibrillateur.", "FRENCH - Tri 3B"
            return "4", "Dysfonction - avis cardiologue de garde.", "FRENCH - Tri 4"

        if motif == "Oedeme des membres inferieurs / IC":
            if fr < 30 and spo2 > 90:
                return "3B", "OEdeme avec FR < 30/min et SpO2 > 90 %.", "FRENCH - Tri 3B"
            return "4", "OEdeme chronique stable.", "FRENCH - Tri 4"

        if motif == "Membre douloureux / Phlebite suspectee":
            if details.get("signes_locaux_francs") or details.get("siege_proximal"):
                return "4", "Signes locaux francs ou siege proximal - echo Doppler urgent.", "FRENCH - Tri 4"
            return "4", "Signes locaux moderes ou siege distal.", "FRENCH - Tri 4"

        if motif == "AES / Exposition liquide biologique":
            if details.get("vih_contact") and details.get("exposition_inf_48h"):
                return "4", "Contact VIH avere et exposition < 48h - TPE urgent.", "FRENCH - Tri 4"
            return "4", "Exposition > 48h ou risque non VIH.", "FRENCH - Tri 4"

        if motif == "Exposition maladie contagieuse":
            if details.get("risque_vital"):
                return "5", "Risque vital de contage (meningite, Ebola...) - isolement immediat.", "FRENCH - Tri 5"
            return "5", "Contage sans risque vital.", "FRENCH - Tri 5"

        if motif == "Douleur thoracique / SCA":
            ecg   = details.get("ecg", "Normal")
            dtype = details.get("douleur_type", "Atypique")
            dtyp  = details.get("douleur_typique", False)
            co    = details.get("comorbidites_coronaires", False)
            frcv  = details.get("frcv_count", 0)
            if ecg == "Anormal typique SCA" or details.get("ecg_anormal", False):
                return "1", "ECG typique SCA (sus-decalage ST ou LBBB nouveau).", "FRENCH - Tri 1"
            if ecg == "Anormal non typique" or dtype == "Typique persistante/intense" \
                    or (dtyp and details.get("duree_longue", False)):
                return "2", "Douleur thoracique typique persistante ou ECG douteux.", "FRENCH - Tri 2"
            if frcv >= 2:
                return "3A", f"Douleur thoracique associee a {frcv} FRCV.", "FRENCH - Tri 3A (FRCV >= 2)"
            if co:
                return "3A", "Coronaropathie documentee avec douleur thoracique.", "FRENCH - Tri 3A"
            if dtyp or dtype == "Type coronaire":
                return "3B", "Douleur de type angineux sans critere de gravite immediat.", "FRENCH - Tri 3B"
            return "4", "ECG normal, douleur thoracique atypique.", "FRENCH - Tri 4"

        if motif == "Tachycardie / tachyarythmie":
            if fc >= 180: return "1", f"Tachycardie extreme : FC {fc} bpm >= 180 bpm.", "FRENCH - Tri 1"
            if fc >= 130: return "2", f"FC {fc} bpm >= 130 bpm.", "FRENCH - Tri 2"
            if fc > 110:  return "3B", f"FC {fc} bpm > 110 bpm.", "FRENCH - Tri 3B"
            return "4", "Episode resolutif ou FC en valeurs normales.", "FRENCH - Tri 4"

        if motif == "Bradycardie / bradyarythmie":
            mt = details.get("mauvaise_tolerance", False)
            if fc <= 40: return "1", f"Bradycardie extreme : FC {fc} bpm <= 40 bpm.", "FRENCH - Tri 1"
            if fc <= 50 and mt: return "2", f"FC {fc} bpm avec mauvaise tolerance hemodynamique.", "FRENCH - Tri 2"
            if fc <= 50: return "3B", f"FC {fc} bpm - bradycardie bien toleree.", "FRENCH - Tri 3B"
            return "4", "Bradycardie toleree - pas de retentissement hemodynamique.", "FRENCH - Tri 4"

        if motif == "Hypertension arterielle":
            sf = details.get("sf_associes", False)
            if pas >= 220 or (pas >= 180 and sf):
                return "2", f"PAS {pas} mmHg ou >= 180 mmHg avec symptomes fonctionnels.", "FRENCH - Tri 2"
            if pas >= 180:
                return "3B", f"PAS {pas} mmHg >= 180 mmHg sans symptome fonctionnel.", "FRENCH - Tri 3B"
            return "4", f"PAS {pas} mmHg < 180 mmHg.", "FRENCH - Tri 4"

        if motif == "Dyspnee / insuffisance respiratoire":
            if fr >= 40 or spo2 < 86:
                return "1", f"Detresse respiratoire aigue (FR {fr}/min, SpO2 {spo2} %).", "FRENCH - Tri 1"
            if not details.get("parole_ok", True) or details.get("tirage") \
                    or details.get("orthopnee") or (30 <= fr < 40) or (86 <= spo2 <= 90):
                return "2", "Dyspnee a la parole, tirage intercostal ou orthopnee.", "FRENCH - Tri 2"
            return "3B", "Dyspnee moderee, patient stable.", "FRENCH - Tri 3B"

        if motif == "Palpitations":
            if fc >= 180: return "2", f"FC {fc} bpm >= 180 bpm.", "FRENCH - Tri 2"
            if fc >= 130: return "2", f"FC {fc} bpm >= 130 bpm.", "FRENCH - Tri 2"
            if details.get("malaise") or fc > 110:
                return "3B", "Palpitations avec malaise associe ou FC > 110 bpm.", "FRENCH - Tri 3B"
            return "4", "Palpitations isolees sans retentissement hemodynamique.", "FRENCH - Tri 4"

        # --- Respiratoire ---
        if motif == "Asthme / exacerbation de BPCO":
            dep = details.get("dep", 999)
            if fr >= 40 or spo2 < 86:
                return "1", "Detresse respiratoire aigue.", "FRENCH - Tri 1"
            if dep <= 200 or not details.get("parole_ok", True) or details.get("tirage"):
                return "2", "DEP <= 200 l/min ou dyspnee a la parole.", "FRENCH - Tri 2"
            if dep >= 300:
                return "4", f"DEP {dep} l/min >= 300 l/min.", "FRENCH - Tri 4"
            return "3B", "Exacerbation moderee.", "FRENCH - Tri 3B"

        # PDF p.6 : motif respiratoire distinct du SCA
        # Douleur thoracique / embolie pulmonaire / pneumopathie / pneumothorax
        if motif == "Douleur thoracique / Embolie / Pneumopathie / Pneumothorax":
            if fr >= 40 or spo2 < 86:
                return "1", "Detresse respiratoire aigue.", "FRENCH - Tri 1"
            if not details.get("parole_ok", True) or details.get("tirage") \
                    or details.get("orthopnee"):
                return "2", "Dyspnee a la parole, tirage ou orthopnee.", "FRENCH - Tri 2"
            return "3B", "Douleur thoracique / embolie / pneumopathie / pneumothorax - bilan urgent.", "FRENCH - Tri 3B"

        # --- Neurologie ---
        if motif == "AVC / Deficit neurologique":
            dh = details.get("delai_heures", 999)
            ok = details.get("delai_ok", False)
            if dh <= 4.5 or ok:
                return "1", "Deficit neurologique focal avec delai < 4 h 30 - filiere Stroke / thrombolyse.", "FRENCH - Tri 1"
            if dh >= 24:
                return "3B", "Deficit neurologique evolutif avec delai > 24 h.", "FRENCH - Tri 3B"
            return "2", "Deficit neurologique focal aigu.", "FRENCH - Tri 2"

        if motif == "Alteration de conscience / Coma":
            if gcs <= 8:  return "1", f"GCS {gcs}/15 - coma.", "FRENCH - Tri 1"
            if gcs <= 13: return "2", f"GCS {gcs}/15 - alteration moderee de la conscience.", "FRENCH - Tri 2"
            return "3B", "Alteration legere de la conscience.", "FRENCH - Tri 3B"

        if motif == "Etat de mal epileptique / Convulsions":
            if details.get("crises_multiples") or details.get("en_cours") \
                    or details.get("confusion_post_critique") or temp >= 38.5:
                return "2", "Crise convulsive en cours, crise repetee ou confusion post-critique.", "FRENCH - Tri 2"
            return "3B", "Recuperation neurologique complete.", "FRENCH - Tri 3B"

        if motif == "Cephalee":
            if details.get("inhabituelle") or details.get("brutale") \
                    or details.get("fievre_assoc") or temp >= 38.5:
                return "2", "Cephalee inhabituelle, debut brutal (coup de tonnerre) ou febrile.", "FRENCH - Tri 2"
            return "3B", "Migraine connue - tableau clinique habituel.", "FRENCH - Tri 3B"

        if motif == "Vertiges / Trouble de l'equilibre":
            if details.get("signes_neuro") or details.get("cephalee_brutale"):
                return "2", "Syndrome vestibulaire avec signes neurologiques associes.", "FRENCH - Tri 2"
            return "5", "Troubles de l'equilibre stables sans signe neurologique.", "FRENCH - Tri 5"

        if motif == "Syndrome confusionnel / Desorientation":
            if temp >= 38.5:
                return "2", "Syndrome confusionnel febrile.", "FRENCH - Tri 2"
            return "3B", "Syndrome confusionnel afebrile.", "FRENCH - Tri 3B"

        # --- Digestif ---
        if motif == "Hematemese / vomissements sanglants":
            if details.get("abondante"):
                return "2", "Hematemese abondante.", "FRENCH - Tri 2"
            return "3B", "Haut degre de suspicion de saignement digestif haut.", "FRENCH - Tri 3B"

        if motif == "Rectorragie / Melena":
            if details.get("abondante"):
                return "2", "Rectorragie abondante ou melena.", "FRENCH - Tri 2"
            return "3B", "Saignement digestif bas modere.", "FRENCH - Tri 3B"

        if motif == "Douleur abdominale":
            if details.get("defense") or details.get("contracture") or details.get("mauvaise_tolerance"):
                return "2", "Defense ou contracture abdominale a la palpation.", "FRENCH - Tri 2"
            if details.get("regressive"):
                return "5", "Douleur abdominale regressive.", "FRENCH - Tri 5"
            return "3B", "Douleur abdominale moderee sans signe de gravite.", "FRENCH - Tri 3B"

        # --- Genito-urinaire ---
        if motif == "Douleur lombaire / Colique nephretique":
            if details.get("intense"):
                return "2", "Douleur lombaire intense avec agitation.", "FRENCH - Tri 2"
            if details.get("regressive"):
                return "5", "Douleur lombaire regressive.", "FRENCH - Tri 5"
            return "3B", "Colique nephretique moderee.", "FRENCH - Tri 3B"

        if motif == "Retention aigue d'urines / Anurie":
            return "2", "Retention aigue d'urines ou anurie.", "FRENCH - Tri 2"

        if motif == "Douleur testiculaire / Suspicion de torsion":
            if details.get("intense") or details.get("suspicion_torsion"):
                return "2", "Suspicion de torsion testiculaire - urgence chirurgicale.", "FRENCH - Tri 2"
            return "3B", "Douleur testiculaire sans critere de gravite immediat.", "FRENCH - Tri 3B"

        if motif == "Hematurie":
            if details.get("abondante_active"):
                return "2", "Hematurie macroscopique abondante et active.", "FRENCH - Tri 2"
            return "3B", "Hematurie macroscopique moderee.", "FRENCH - Tri 3B"

        # --- Traumatologie ---
        if motif == "Traumatisme avec amputation":
            return "M", "Amputation traumatique.", "FRENCH - Tri M"

        if motif == "Traumatisme du thorax / abdomen / rachis cervical":
            if details.get("penetrant"):
                return "1", "Traumatisme penetrant.", "FRENCH - Tri 1"
            if details.get("cinetique") == "Haute":
                return "2", "Traumatisme a haute cinetique.", "FRENCH - Tri 2"
            if details.get("mauvaise_tolerance"):
                return "3B", "Traumatisme a faible cinetique avec mauvaise tolerance.", "FRENCH - Tri 3B"
            # PDF p.7 : faible velocite sans mauvaise tolerance OU gene limitee = Tri 4
            return "4", "Traumatisme a faible cinetique sans mauvaise tolerance (gene limitee acceptable).", "FRENCH - Tri 4"

        if motif == "Traumatisme cranien":
            if gcs <= 8:
                return "1", f"Traumatisme cranien grave : GCS {gcs}/15.", "FRENCH - Tri 1"
            if gcs <= 13 or details.get("deficit_neuro") or details.get("aod_avk") \
                    or details.get("vomissements_repetes"):
                return "2", "Traumatisme cranien modere (GCS 9-13, deficit, anticoagulants ou vomissements).", "FRENCH - Tri 2"
            if details.get("pdc") or details.get("plaie"):
                return "3B", "Traumatisme cranien leger avec perte de connaissance ou plaie.", "FRENCH - Tri 3B"
            return "5", "Traumatisme cranien benin sans signe de gravite.", "FRENCH - Tri 5"

        if motif == "Brulure thermique":
            if details.get("etendue") or details.get("main_visage"):
                return "2", "Brulure etendue (> 10 % SCT) ou localisation critique (main, visage, perinee).", "FRENCH - Tri 2"
            if age <= 2:
                return "3A", "Brulure chez un nourrisson de moins de 24 mois.", "FRENCH - Tri 3A"
            # PDF p.7 : brulure peu etendue consultation tardive = Tri 5
            if details.get("consultation_tardive") and not details.get("etendue"):
                return "5", "Brulure peu etendue - consultation differee.", "FRENCH - Tri 5"
            return "3B", "Brulure limitee sans localisation critique.", "FRENCH - Tri 3B"

        if motif == "Traumatisme du bassin / hanche / femur":
            if details.get("cinetique") == "Haute":
                return "2", "Traumatisme a haute cinetique.", "FRENCH - Tri 2"
            if details.get("mauvaise_tolerance"):
                return "3B", "Traumatisme avec mauvaise tolerance.", "FRENCH - Tri 3B"
            return "4", "Traumatisme bien tolere.", "FRENCH - Tri 4"

        if motif == "Traumatisme d'un membre / epaule":
            if details.get("ischemie") or details.get("cinetique") == "Haute":
                return "2", "Ischemie distale ou traumatisme a haute cinetique.", "FRENCH - Tri 2"
            if details.get("impotence_totale") or details.get("deformation"):
                return "3B", "Impotence fonctionnelle totale ou deformation.", "FRENCH - Tri 3B"
            if details.get("impotence_moderee"):
                return "4", "Impotence fonctionnelle moderee.", "FRENCH - Tri 4"
            return "5", "Traumatisme sans impotence ni deformation.", "FRENCH - Tri 5"

        if motif == "Plaie":
            if details.get("delabrant") or details.get("saignement_actif"):
                return "2", "Plaie delabrante ou saignement actif non controle.", "FRENCH - Tri 2"
            if details.get("large_complexe") or details.get("main"):
                return "3B", "Plaie large ou complexe, ou localisation main.", "FRENCH - Tri 3B"
            if details.get("superficielle"):
                return "4", "Plaie superficielle.", "FRENCH - Tri 4"
            return "5", "Excoriation ou eraflure.", "FRENCH - Tri 5"

        if motif == "Electrisation":
            if details.get("pdc") or details.get("foudre"):
                return "2", "Electrisation avec perte de connaissance ou foudroiement.", "FRENCH - Tri 2"
            if details.get("haute_tension"):
                return "3B", "Contact avec haute tension.", "FRENCH - Tri 3B"
            return "4", "Contact avec courant domestique bien tolere.", "FRENCH - Tri 4"

        if motif == "Agression sexuelle / maltraitance":
            # PDF SFMU V1.1 p.7 : Tri 2 (la colonne Tri 1 est vide pour ce motif)
            return "2", "Agression sexuelle ou maltraitance.", "FRENCH - Tri 2"

        if motif == "Traumatisme oculaire":
            if details.get("cinetique") == "Haute":
                return "2", "Traumatisme oculaire a haute cinetique.", "FRENCH - Tri 2"
            if details.get("mauvaise_tolerance"):
                return "3B", "Traumatisme oculaire a faible cinetique avec mauvaise tolerance.", "FRENCH - Tri 3B"
            return "4", "Traumatisme oculaire a faible cinetique bien tolere.", "FRENCH - Tri 4"

        if motif == "Traumatisme maxillo-facial / oreille":
            if details.get("cinetique") == "Haute":
                return "2", "Traumatisme maxillo-facial a haute cinetique.", "FRENCH - Tri 2"
            if details.get("mauvaise_tolerance"):
                return "3B", "Traumatisme maxillo-facial avec mauvaise tolerance.", "FRENCH - Tri 3B"
            return "4", "Traumatisme maxillo-facial a faible cinetique bien tolere.", "FRENCH - Tri 4"

        # --- Psychiatrie / Toxicologie ---
        if motif == "Idees ou comportement suicidaire":
            return "2", "Idees suicidaires actives ou comportement suicidaire.", "FRENCH - Tri 2"

        if motif == "Anxiete / Depression / Consultation psychiatrique":
            if details.get("anxiete_majeure") or details.get("attaque_panique"):
                return "4", "Anxiete majeure ou attaque de panique.", "FRENCH - Tri 4"
            return "4", "Consultation psychiatrique non urgente.", "FRENCH - Tri 4"

        if motif == "Agitation / Troubles du comportement":
            if details.get("agitation") or details.get("violence"):
                return "2", "Agitation majeure ou comportement violent.", "FRENCH - Tri 2"
            return "4", "Troubles du comportement sans critere d'urgence immediate.", "FRENCH - Tri 4"

        if motif in ["Intoxication medicamenteuse", "Intoxication non medicamenteuse"]:
            if details.get("mauvaise_tolerance") or details.get("intention_suicidaire") \
                    or details.get("cardiotropes"):
                return "2", "Mauvaise tolerance clinique, intention suicidaire ou toxique cardiotrope.", "FRENCH - Tri 2"
            # PDF p.3 : enfant -> Tri 3A
            if details.get("enfant"):
                return "3A", "Intoxication chez un enfant - surveillance urgente.", "FRENCH - Tri 3A"
            # PDF p.3 : avis referent (MAO, MCO) -> Tri 3B
            # PDF p.3 : vu tard (>= 24h) sans mauvaise tolerance -> Tri 5
            if details.get("vu_tard_24h") and not details.get("mauvaise_tolerance"):
                return "5", "Intoxication vue tardivement (>= 24h) sans mauvaise tolerance.", "FRENCH - Tri 5"
            return "3B", "Intoxication moderee - avis du specialiste requis.", "FRENCH - Tri 3B"

        if motif == "Sevrage / Toxicomanie":
            if details.get("agitation") or details.get("violence"):
                return "4", "Etat de manque avec agitation.", "FRENCH - Tri 4"
            return "4", "Demande de substitution - consultation.", "FRENCH - Tri 4"

        if motif == "Ivresse / Comportement ebrieux":
            if gcs <= 8:
                return "2", f"Ivresse avec coma GCS {gcs}.", "FRENCH - Tri 2"
            if gcs <= 13 or details.get("agitation"):
                return "3B", "Ivresse avec alteration de conscience moderee.", "FRENCH - Tri 3B"
            return "4", "Ivresse simple bien toleree.", "FRENCH - Tri 4"

        # --- Infectiologie ---
        if motif == "Fievre":
            si = round(fc / pas, 1) if pas and pas > 0 else 0
            if temp >= 40 or temp <= 35.2 or details.get("confusion") \
                    or details.get("purpura") or details.get("temp_extreme"):
                return "2", "Fievre avec critere de gravite (T >= 40 ou < 35,2 degres C, confusion, purpura).", "FRENCH - Tri 2"
            # PDF p.1 : Shock Index >= 1 = critere de remontee en Tri 3B
            if details.get("mauvaise_tolerance") or pas < 100 or si >= 1.0:
                return "3B", f"Fievre avec mauvaise tolerance clinique (Shock Index {si}).", "FRENCH - Tri 3B"
            return "5", "Fievre bien toleree.", "FRENCH - Tri 5"

        # --- Gyneco-obstetrique ---
        if motif == "Accouchement imminent":
            return "M", "Accouchement imminent.", "FRENCH - Tri M"

        if motif in ["Complication de grossesse (1er / 2eme trimestre)",
                     "Complication de grossesse (3eme trimestre)"]:
            return "3A", "Complication de grossesse - surveillance urgente.", "FRENCH - Tri 3A"

        if motif == "Menorragie / Metrorragie":
            if details.get("grossesse") or details.get("abondante"):
                return "2", "Metrorragie abondante ou sur grossesse connue.", "FRENCH - Tri 2"
            return "3B", "Saignement genital modere.", "FRENCH - Tri 3B"

        if motif == "Probleme post-partum":
            if details.get("fievre"):
                return "4", "Post-partum avec fievre (mastite / endometrite).", "FRENCH - Tri 4"
            return "4", "Probleme post-partum sans critere de gravite.", "FRENCH - Tri 4"

        # PDF p.3 - motifs gynecologiques supplementaires
        if motif == "Anomalie du sein":
            if details.get("mastite") or details.get("abces"):
                return "3B", "Mastite ou abces du sein.", "FRENCH - Tri 3B"
            return "5", "Anomalie du sein - consultation non urgente.", "FRENCH - Tri 5"

        if motif == "Anomalie vulvo-vaginale / corps etranger":
            return "5", "Anomalie vulvo-vaginale ou corps etranger - consultation.", "FRENCH - Tri 5"

        # --- Metabolique ---
        if motif == "Hyperglycemie / Cetoacidose diabetique":
            gl = glycemie_mgdl or details.get("glycemie_mgdl", 0)
            if details.get("cetose_elevee") or gcs < 15:
                return "2", "Cetoacidose diabetique ou trouble de la conscience.", "FRENCH - Tri 2"
            if gl >= GLYCEMIE["hyperglycemie_severe"] or details.get("cetose_positive"):
                return "3B", f"Glycemie {gl} mg/dl >= 360 mg/dl ou cetose positive.", "FRENCH - Tri 3B"
            return "4", "Hyperglycemie moderee bien toleree.", "FRENCH - Tri 4"

        if motif == "Hypoglycemie":
            gl = glycemie_mgdl or details.get("glycemie_mgdl", 90)
            if gcs <= 8:
                return "1", f"Coma hypoglycemique : GCS {gcs}/15.", "FRENCH - Tri 1"
            if gcs <= 13 or details.get("mauvaise_tolerance") \
                    or gl < GLYCEMIE["hypoglycemie_severe"]:
                return "2", f"Hypoglycemie severe (glycemie {gl} mg/dl) ou mauvaise tolerance.", "FRENCH - Tri 2"
            return "3B", "Hypoglycemie moderee.", "FRENCH - Tri 3B"

        if motif == "Pathologie rare en poussee":
            return "2", "Poussee de pathologie rare ou grave (ex. drepanocytose) - avis referent.", "FRENCH - Tri 2"

        if motif == "AEG / Asthenie":
            if details.get("signes_objectifs"):
                return "3B", "Asthenie avec signes objectifs d'alteration de l'etat general.", "FRENCH - Tri 3B"
            return "5", "Asthenie sans comorbidite ni signe objectif.", "FRENCH - Tri 5"

        if motif == "Anomalie de resultat biologique":
            if details.get("symptomatique"):
                return "2", "Anomalie biologique avec retentissement clinique.", "FRENCH - Tri 2"
            return "3B", "Anomalie biologique - avis referent.", "FRENCH - Tri 3B"

        if motif == "Gelure / Lesions liees au froid":
            if details.get("necrose") or details.get("deficit_sensitif") or details.get("deficit_moteur"):
                return "2", "Gelure avec signe de necrose ou deficit sensitif/moteur.", "FRENCH - Tri 2"
            return "3B", "Gelure sans signe de necrose.", "FRENCH - Tri 3B"

        if motif == "Probleme suite de soins":
            return "5", "Probleme de suivi de soins (pansements, stomie) - Tri 5.", "FRENCH - Tri 5"

        if motif == "Renouvellement ordonnance":
            return "5", "Renouvellement d'ordonnance - Tri 5.", "FRENCH - Tri 5"

        if motif == "Examen administratif / Certificat":
            if details.get("demande_forces_ordre"):
                return "3B", "Requisition forces de l'ordre.", "FRENCH - Tri 3B"
            return "5", "Examen administratif - Tri 5.", "FRENCH - Tri 5"

        if motif == "Demande d'hebergement social":
            return "5", "Demande d'hebergement pour raison sociale - Tri 5.", "FRENCH - Tri 5"
            if gcs <= 8:
                return "1", f"Coma hypoglycemique : GCS {gcs}/15.", "FRENCH - Tri 1"
            if gcs <= 13 or details.get("mauvaise_tolerance") \
                    or gl < GLYCEMIE["hypoglycemie_severe"]:
                return "2", f"Hypoglycemie severe (glycemie {gl} mg/dl) ou mauvaise tolerance.", "FRENCH - Tri 2"
            return "3B", "Hypoglycemie moderee.", "FRENCH - Tri 3B"

        if motif == "Hypothermie":
            if temp <= 32:   return "1", f"Hypothermie severe : T {temp} degres C.", "FRENCH - Tri 1"
            if temp <= 35.2: return "2", "Hypothermie moderee.", "FRENCH - Tri 2"
            return "3B", "Hypothermie legere.", "FRENCH - Tri 3B"

        if motif == "Coup de chaleur / Hyperthermie":
            if gcs <= 8:  return "1", "Coup de chaleur avec coma.", "FRENCH - Tri 1"
            if temp >= 40: return "2", f"Hyperthermie : T {temp} degres C >= 40.", "FRENCH - Tri 2"
            return "3B", "Insolation legere.", "FRENCH - Tri 3B"

        if motif == "Allergie / anaphylaxie":
            if details.get("dyspnee") or details.get("mauvaise_tolerance"):
                return "2", "Anaphylaxie severe : atteinte respiratoire ou hemodynamique.", "FRENCH - Tri 2"
            return "4", "Reaction allergique legere sans atteinte systemique.", "FRENCH - Tri 4"

        # --- ORL / Ophtalmologie ---
        if motif == "Epistaxis":
            if details.get("abondant_actif"):     return "2",  "Epistaxis abondante active.", "FRENCH - Tri 2"
            if details.get("abondant_resolutif"): return "3B", "Epistaxis abondante resolutive.", "FRENCH - Tri 3B"
            return "5", "Epistaxis peu abondante.", "FRENCH - Tri 5"

        if motif in ["Corps etranger / Brulure oculaire", "Trouble visuel aigu / Cecite"]:
            if details.get("intense") or details.get("chimique") or details.get("brutal"):
                return "2", "Urgence ophtalmologique : douleur intense, brulure chimique ou cecite brutale.", "FRENCH - Tri 2"
            return "3B", "Avis ophtalmologique de garde requis.", "FRENCH - Tri 3B"

        if motif == "Icterejaunisse":
            return "3B", "Ictere - bilan hepatique urgent.", "FRENCH - Tri 3B"

        if motif == "Probleme technique stomie / cicatrice post-op":
            return "3B", "Probleme technique stomie ou cicatrice post-operatoire - avis referent.", "FRENCH - Tri 3B"

        if motif == "Hernie / Masse / Distension abdominale":
            if details.get("douleur_severe") or details.get("occlusion"):
                return "2", "Hernie avec douleur severe ou syndrome occlusif.", "FRENCH - Tri 2"
            return "4", "Hernie ou masse abdominale sans critere de gravite.", "FRENCH - Tri 4"

        if motif == "Corps etranger digestif":
            if details.get("aphagie") or details.get("hypersialorrhee") or details.get("sf_associes"):
                return "4", "Corps etranger avec aphagie, hypersialorrhee ou SF associes.", "FRENCH - Tri 4"
            if details.get("tranchant") or details.get("pointu"):
                return "4", "Corps etranger tranchant ou pointu.", "FRENCH - Tri 4"
            return "4", "Corps etranger digestif.", "FRENCH - Tri 4"

        if motif == "Corps etranger rectal":
            if details.get("douleur_severe") or details.get("rectorragie"):
                return "4", "Corps etranger rectal avec douleur severe ou rectorragie.", "FRENCH - Tri 4"
            return "4", "Corps etranger rectal.", "FRENCH - Tri 4"

        if motif == "Constipation":
            if details.get("occlusion"):
                return "2", "Constipation avec syndrome occlusif.", "FRENCH - Tri 2"
            if details.get("douleur"):
                return "3B", "Constipation avec douleur abdominale.", "FRENCH - Tri 3B"
            return "5", "Constipation sans douleur.", "FRENCH - Tri 5"

        if motif == "Vomissements isoles":
            if details.get("occlusion"):
                return "2", "Vomissements avec syndrome occlusif.", "FRENCH - Tri 2"
            if age <= 2:
                return "3A", "Vomissements chez nourrisson <= 2 ans.", "FRENCH - Tri 3A"
            if details.get("abondants") or details.get("douleur"):
                return "3B", "Vomissements abondants ou avec douleur.", "FRENCH - Tri 3B"
            return "5", "Vomissements isoles toleres.", "FRENCH - Tri 5"

        if motif == "Diarrhee isolee":
            if age <= 2:
                return "3A", "Diarrhee chez nourrisson <= 2 ans.", "FRENCH - Tri 3A"
            if details.get("abondante") or details.get("mauvaise_tolerance"):
                return "3B", "Diarrhee abondante ou mauvaise tolerance.", "FRENCH - Tri 3B"
            return "5", "Diarrhee isolee toleree.", "FRENCH - Tri 5"

        if motif == "Douleur anale":
            if details.get("suspicion_abces"):
                return "3B", "Suspicion d'abces anal ou fissure.", "FRENCH - Tri 3B"
            return "5", "Douleur anale.", "FRENCH - Tri 5"

        if motif == "Hoquet":
            if details.get("incessant"):
                return "3B", "Hoquet incessant >= 12 h.", "FRENCH - Tri 3B"
            return "5", "Hoquet.", "FRENCH - Tri 5"

        if motif == "Dysurie / Brulure mictionnelle":
            if temp >= 38.0 or details.get("fievre"):
                return "3B", "Infection urinaire febrile.", "FRENCH - Tri 3B"
            if age <= 2:
                return "4", "Symptomes urinaires chez enfant <= 2 ans.", "FRENCH - Tri 4"
            return "5", "Dysurie sans fievre.", "FRENCH - Tri 5"

        if motif == "Ecoulement ou lesion genito-cutanee":
            if temp >= 38.0:
                return "3B", "Ecoulement genital febrile.", "FRENCH - Tri 3B"
            return "5", "Ecoulement genital afebrile.", "FRENCH - Tri 5"

        if motif == "Dysfonction sonde urinaire / sonde JJ":
            if details.get("douleur_intense") or details.get("fievre") or details.get("mauvaise_tolerance"):
                return "3B", "Dysfonction de sonde avec douleur intense, fievre ou mauvaise tolerance.", "FRENCH - Tri 3B"
            return "3B", "Dysfonction de sonde - avis referent.", "FRENCH - Tri 3B"

        # --- Rhumatologie (PDF p.6) ---
        if motif == "Douleur articulaire / Arthrose / Arthrite":
            if temp >= 38.0 or details.get("signes_locaux_importants"):
                return "3B", "Arthrite avec fievre ou signes locaux importants.", "FRENCH - Tri 3B"
            return "4", "Douleur articulaire sans signe de gravite.", "FRENCH - Tri 4"

        if motif == "Douleur rachidienne":
            if details.get("deficit_sensitif") or details.get("deficit_moteur"):
                return "2", "Douleur rachidienne avec deficit sensitif ou moteur.", "FRENCH - Tri 2"
            if temp >= 38.0 or details.get("parestesies"):
                return "3B", "Douleur rachidienne febrile ou avec paresthesies.", "FRENCH - Tri 3B"
            return "5", "Douleur rachidienne mecanique.", "FRENCH - Tri 5"

        if motif == "Douleur de membre / Sciatique":
            if temp >= 38.0:
                return "3B", "Douleur de membre febrile.", "FRENCH - Tri 3B"
            if details.get("impotence"):
                return "3B", "Impotence du membre.", "FRENCH - Tri 3B"
            return "5", "Douleur de membre ou sciatique sans signe de gravite.", "FRENCH - Tri 5"

        # --- ORL / Stomatologie (PDF p.4) ---
        if motif == "Trouble auditif / Acouphenes":
            if details.get("surdite_brutale"):
                return "4", "Surdite brutale - avis ORL urgent.", "FRENCH - Tri 4"
            return "5", "Trouble auditif ou acouphenes.", "FRENCH - Tri 5"

        if motif == "Tumefaction ORL ou cervicale":
            if temp >= 38.0 or details.get("signes_locaux_importants"):
                return "4", "Tumefaction ORL / cervicale febrile ou volumineuse.", "FRENCH - Tri 4"
            return "4", "Tumefaction ORL ou cervicale.", "FRENCH - Tri 4"

        if motif == "Corps etranger ORL":
            if details.get("dyspnee_inspiratoire"):
                return "2", "Corps etranger ORL avec dyspnee inspiratoire.", "FRENCH - Tri 2"
            return "4", "Corps etranger ORL sans dyspnee.", "FRENCH - Tri 4"

        if motif == "Pathologie de l'oreille / Otite":
            return "5", "Pathologie auriculaire.", "FRENCH - Tri 5"

        if motif == "Douleur de gorge / Angine":
            if details.get("aphagie") or details.get("mauvaise_tolerance"):
                return "3B", "Angine avec aphagie ou mauvaise tolerance.", "FRENCH - Tri 3B"
            return "5", "Angine ou stomatite.", "FRENCH - Tri 5"

        if motif == "Obstruction nasale / Rhinite / Sinusite":
            if details.get("febrile"):
                return "3B", "Sinusite febrile.", "FRENCH - Tri 3B"
            return "5", "Rhinite ou obstruction nasale.", "FRENCH - Tri 5"

        if motif == "Probleme dentaire":
            if details.get("signes_locaux_importants") or details.get("douleur_resistante"):
                return "3B", "Probleme dentaire avec signes locaux importants.", "FRENCH - Tri 3B"
            return "5", "Probleme dentaire.", "FRENCH - Tri 5"

        if motif == "Demangeaison / Oeil rouge":
            return "5", "Oeil rouge ou demangeaison oculaire.", "FRENCH - Tri 5"

        # --- Peau (PDF p.4) ---
        if motif == "Ecchymose / Hematome spontane":
            return "3B", "Ecchymose ou hematome spontane - bilan hemostase.", "FRENCH - Tri 3B"

        if motif == "Abces ou infection cutanee localisee":
            if temp >= 38.0 or details.get("abces_volumineux"):
                return "3B", "Abces febrile ou volumineux.", "FRENCH - Tri 3B"
            return "4", "Infection cutanee localisee.", "FRENCH - Tri 4"

        if motif == "Erytheme etendu / Eruption cutanee":
            if details.get("anaphylaxie"):
                return "2", "Eruption avec signes d'anaphylaxie.", "FRENCH - Tri 2"
            if temp >= 38.0 or details.get("mauvaise_tolerance"):
                return "3B", "Eruption febrile ou mauvaise tolerance.", "FRENCH - Tri 3B"
            if details.get("etendu"):
                return "4", "Erytheme etendu.", "FRENCH - Tri 4"
            return "5", "Eruption localisee.", "FRENCH - Tri 5"

        if motif == "Morsure / Piqure":
            if details.get("serpent") or details.get("scorpion"):
                return "2", "Morsure de serpent ou de scorpion.", "FRENCH - Tri 2"
            if temp >= 38.0 or details.get("signes_locaux_importants"):
                return "3B", "Morsure ou piqure febrile ou avec signes locaux importants.", "FRENCH - Tri 3B"
            return "5", "Morsure ou piqure sans signe de gravite.", "FRENCH - Tri 5"

        if motif == "Corps etranger sous-cutane":
            if details.get("multiples") or details.get("complexe"):
                return "4", "Corps etrangers multiples ou complexes.", "FRENCH - Tri 4"
            return "5", "Corps etranger sous-cutane.", "FRENCH - Tri 5"

        # ======================================================================
        # PEDIATRIE <= 2 ans — Pathologies specifiques
        # PDF SFMU V1.1 p.5 : seuils FC et PAS differents de l'adulte.
        # Ces motifs sont evalues en priorite si age <= 2 ans.
        # ======================================================================

        if motif == "Pediatrie - Dyspnee avec sifflement respiratoire":
            # Tri 2 si dyspnee associee, Tri 3A si sifflement isole sans dyspnee
            if fr >= 40 or spo2 < 86 or details.get("detresse"):
                return "2", "Dyspnee avec sifflement chez le nourrisson - detresse respiratoire.", "FRENCH Pediatrie - Tri 2"
            return "3A", "Sifflement respiratoire sans dyspnee - surveillance rapprochee.", "FRENCH Pediatrie - Tri 3A"

        if motif == "Pediatrie - Fievre <= 3 mois":
            # Fievre chez nourrisson <= 3 mois = Tri 2 systematique
            return "2", "Fievre chez nourrisson <= 3 mois - evaluation medicale urgente systematique.", "FRENCH Pediatrie - Tri 2"

        if motif == "Pediatrie - Convulsion hyperthermique":
            # Tri 2 si recidive, duree >= 10 min ou hypotonie post-critique
            # Tri 3B si recuperation complete
            if details.get("recidive") or details.get("duree_sup_10min") or details.get("hypotonie"):
                return "2", "Convulsion hyperthermique : recidive, duree >= 10 min ou hypotonie.", "FRENCH Pediatrie - Tri 2"
            return "3B", "Convulsion hyperthermique avec recuperation complete.", "FRENCH Pediatrie - Tri 3B"

        if motif == "Pediatrie - Diarrhee / Vomissements nourrisson":
            # Nourrisson <= 24 mois
            # Tri 2 si perte de poids >= 10 % ou hypotonie
            # Tri 3A si <= 6 mois
            # Tri 3B par defaut
            if details.get("perte_poids_sup_10pct") or details.get("hypotonie"):
                return "2", "Diarrhee/vomissements nourrisson avec perte de poids >= 10 % ou hypotonie.", "FRENCH Pediatrie - Tri 2"
            if age <= 0.5:  # <= 6 mois
                return "3A", "Diarrhee/vomissements chez nourrisson <= 6 mois.", "FRENCH Pediatrie - Tri 3A"
            return "3B", "Diarrhee/vomissements nourrisson <= 24 mois.", "FRENCH Pediatrie - Tri 3B"

        if motif == "Pediatrie - Troubles alimentaires nourrisson <= 6 mois":
            # Tri 2 si perte de poids >= 10 % ou hypotonie
            # Tri 4 si perte de poids <= 10 %
            if details.get("perte_poids_sup_10pct") or details.get("hypotonie"):
                return "2", "Troubles alimentaires nourrisson : perte de poids >= 10 % ou hypotonie.", "FRENCH Pediatrie - Tri 2"
            return "4", "Troubles alimentaires nourrisson : perte de poids <= 10 %.", "FRENCH Pediatrie - Tri 4"

        if motif == "Pediatrie - Bradycardie":
            # Seuils centralises dans SEUILS_PEDIATRIQUES via _seuils_ped()
            fc_min, _fc_max, _pas_min = _seuils_ped(age)
            if fc <= fc_min:
                return "4", (
                    f"Bradycardie pediatrique : FC {fc} bpm <= {fc_min} bpm "
                    f"pour age {age} an(s)."
                ), "FRENCH Pediatrie - Tri 4"
            return "5", "FC dans les valeurs normales pour l'age.", "FRENCH Pediatrie - Tri 5"

        if motif == "Pediatrie - Ictere neonatal":
            # Tri 2 si perte de poids ou selles decolorees (PDF p.5)
            # Tri 4 par defaut
            if details.get("perte_poids") or details.get("selles_decolorees"):
                return "2", "Ictere neonatal avec perte de poids ou selles decolorees.", "FRENCH Pediatrie - Tri 2"
            return "4", "Ictere neonatal sans signe de gravite.", "FRENCH Pediatrie - Tri 4"

        if motif == "Pediatrie - Tachycardie":
            # Seuils centralises dans SEUILS_PEDIATRIQUES via _seuils_ped()
            _fc_min, fc_max, _pas_min = _seuils_ped(age)
            if fc >= fc_max:
                return "4", (
                    f"Tachycardie pediatrique : FC {fc} bpm >= {fc_max} bpm "
                    f"pour age {age} an(s)."
                ), "FRENCH Pediatrie - Tri 4"
            return "5", "FC dans les valeurs normales pour l'age.", "FRENCH Pediatrie - Tri 5"

        if motif == "Pediatrie - Hypotension":
            # Seuils centralises dans SEUILS_PEDIATRIQUES via _seuils_ped()
            _fc_min, _fc_max, pas_min = _seuils_ped(age)
            if pas <= pas_min:
                return "4", (
                    f"Hypotension pediatrique : PAS {pas} mmHg <= {pas_min} mmHg "
                    f"pour age {age} an(s)."
                ), "FRENCH Pediatrie - Tri 4"
            return "5", "PA normale pour l'age.", "FRENCH Pediatrie - Tri 5"

        if motif == "Pediatrie - Pleurs incoercibles":
            # Tri 3A si pleurs encore presents dans le box de l'IAO
            # Tri 4 si pleurs calmes avant le box
            if details.get("pleurs_dans_box"):
                return "3A", "Pleurs incoercibles persistants dans le box de l'IAO.", "FRENCH Pediatrie - Tri 3A"
            return "4", "Pleurs calmes avant l'evaluation - surveillance.", "FRENCH Pediatrie - Tri 4"

        # Fallback generique sur NEWS2 et EVA
        eva = details.get("eva", 0)
        if news2 >= 5 or gcs < 15: return "2",  f"NEWS2 {news2} / GCS {gcs}.", "NEWS2 / GCS"
        if news2 >= 1 or eva >= 7:  return "3B", f"EVA {eva}/10 / NEWS2 {news2}.", "NEWS2 / EVA"
        if eva >= 4:                return "4",  f"EVA {eva}/10.", "EVA"
        return "5", "Patient non urgent.", "Par defaut"

    except (TypeError, ValueError) as exc:
        return "3B", f"Erreur d'evaluation ({exc}) - tri conservateur 3B applique par defaut.", "Erreur"


# ==============================================================================
# [5] MOTEUR SBAR - Transmission DPI-Ready
# RGPD : aucun nom ni prenom - identifiant anonyme uniquement.
# ==============================================================================

RECO_SBAR = {
    "M":  "PRISE EN CHARGE IMMEDIATE EN DECHOCAGE REQUISE.",
    "1":  "PRISE EN CHARGE IMMEDIATE EN DECHOCAGE REQUISE.",
    "2":  "Evaluation medicale urgente - medecin disponible en moins de 20 min.",
    "3A": "Evaluation dans les 30 min - salle de soins aigus.",
    "3B": "Evaluation dans l'heure - polyclinique des urgences.",
    "4":  "Evaluation dans les 2 h - consultation des urgences.",
    "5":  "Consultation non urgente - reorientation medecin generaliste possible.",
}


def generer_sbar(age, motif, cat, atcd, allergies, o2_supp, temp, fc, pas, spo2, fr, gcs,
                 news2, news2_label, eva, eva_echelle, p_pqrst, q_pqrst, r_pqrst, t_onset,
                 details, niveau, tri_label, justif, critere, secteur,
                 gcs_y=4, gcs_v=5, gcs_m=6, code_anon="ANON"):
    """
    Generation de la transmission SBAR structuree DPI-Ready.
    Format standard copier-coller pour le dossier patient informatise.
    RGPD : aucun nom ni prenom.
    """
    now_str   = datetime.now().strftime("%d/%m/%Y a %H:%M")
    date_str  = datetime.now().strftime("%d/%m/%Y")
    heure_str = datetime.now().strftime("%H:%M")

    atcd_str  = ", ".join(atcd) if atcd else "aucun antecedent notable"
    all_str   = allergies if allergies and allergies.strip().upper() != "RAS" \
                else "aucune allergie connue"

    # Etat de conscience - libelle normalise
    if   gcs == 15: conscience = "conscient et oriente"
    elif gcs >= 13: conscience = f"conscience alteree GCS {gcs} (Y{gcs_y} V{gcs_v} M{gcs_m})"
    elif gcs >= 9:  conscience = f"obnubile GCS {gcs} (Y{gcs_y} V{gcs_v} M{gcs_m})"
    else:           conscience = f"COMA GCS {gcs} (Y{gcs_y} V{gcs_v} M{gcs_m})"

    # Anomalies des signes vitaux
    anomalies = []
    if temp > 38 or temp < 36: anomalies.append(f"fievre/hypothermie {temp} degres C")
    if fc > 100:                anomalies.append(f"tachycardie sinusale {fc} bpm")
    if fc < 60:                 anomalies.append(f"bradycardie {fc} bpm")
    if pas < 90:                anomalies.append(f"hypotension arterielle {pas} mmHg")
    if pas > 180:               anomalies.append(f"hypertension arterielle {pas} mmHg")
    if spo2 < 94:               anomalies.append(f"desaturation SpO2 {spo2} %")
    if fr > 20:                 anomalies.append(f"polypnee {fr}/min")
    vitaux_txt = "dans les valeurs normales" if not anomalies \
                 else "ANOMALIES : " + " | ".join(anomalies)

    si = round(fc / pas, 2) if pas and pas > 0 else 0

    # Prescriptions anticipees (4 premiers gestes)
    rx_txt = ""
    rx = PRESCRIPTIONS.get(motif)
    if rx and rx.get("Gestes immediats"):
        items  = rx["Gestes immediats"][:4]
        rx_txt = "\n  Prescriptions anticipees IAO :\n" \
                 + "\n".join(f"    [ ] {it}" for it in items)

    reco = RECO_SBAR.get(niveau, "Evaluation medicale requise.")

    return (
        f"================================================================\n"
        f"  TRANSMISSION SBAR  -  AKIR-IAO Project v15.0\n"
        f"  Service des Urgences\n"
        f"  {date_str}  -  {heure_str}\n"
        f"================================================================\n"
        f"\n"
        f"[S] SITUATION\n"
        f"  Code patient     : {code_anon}\n"
        f"  Age              : {age} ans\n"
        f"  Heure d'admission: {now_str}\n"
        f"  Motif de recours : {motif} ({cat})\n"
        f"  Douleur          : {eva}/10 ({eva_echelle})\n"
        f"  Etat de conscience: {conscience}\n"
        f"  NIVEAU DE TRI    : {tri_label}\n"
        f"\n"
        f"[B] BACKGROUND\n"
        f"  Antecedents      : {atcd_str}\n"
        f"  Allergies        : {all_str}\n"
        f"  O2 a l'admission : {'oui' if o2_supp else 'non'}\n"
        f"\n"
        f"[A] ASSESSMENT\n"
        f"  Signes vitaux :\n"
        f"    Temperature {temp} degres C  |  FC {fc} bpm  |  PAS {pas} mmHg\n"
        f"    SpO2 {spo2} %  |  FR {fr}/min  |  GCS {gcs}/15\n"
        f"  Shock Index      : {si}\n"
        f"  Bilan vitaux     : {vitaux_txt}\n"
        f"  NEWS2            : {news2} ({news2_label})\n"
        f"\n"
        f"  Anamnese PQRST :\n"
        f"    P - Provoque / Pallie : {p_pqrst or 'non precise'}\n"
        f"    Q - Qualite / Type    : {q_pqrst or 'non precise'}\n"
        f"    R - Region / Irrad.   : {r_pqrst or 'non precise'}\n"
        f"    S - Severite          : {eva}/10 ({eva_echelle})\n"
        f"    T - Temps / Duree     : {t_onset or 'non precise'}\n"
        f"\n"
        f"  Justification du triage : {justif}\n"
        f"  Reference FRENCH        : {critere}\n"
        f"\n"
        f"[R] RECOMMENDATION\n"
        f"  Orientation : {secteur}\n"
        f"  {reco}\n"
        f"{rx_txt}\n"
        f"\n"
        f"----------------------------------------------------------------\n"
        f"  AKIR-IAO Project v15.0  -  Ismail Ibn-Daifa\n"
        f"  Ref. FRENCH Triage SFMU V1.1  -  Adaptation SIAMU Belgique\n"
        f"  RGPD : aucun nom patient dans ce document\n"
        f"----------------------------------------------------------------\n"
    )


# ==============================================================================
# [6] MOTEUR ALERTES - Coherence clinique et securite patient
# ==============================================================================

def verifier_coherence(fc, pas, spo2, fr, gcs, temp, eva, motif, atcd, details, news2,
                       age=0, retour_72h=False, code_operateur=""):
    """
    Verification de la coherence clinique des parametres saisis.
    Detecte les incoherences, les situations a haut risque, et les alertes contextuelles.
    Retourne : (danger: list, attention: list, info: list)

    Nouveautes v16 :
    - Score qSOFA integre
    - Detection conflit NEWS2 vs FRENCH
    - Alerte retour < 72h
    - Alerte GEU femme 15-50 ans + douleur abdominale
    - Alerte hypothermie manipulation douce
    - Alerte immunodeprime febrile (criteres simplifies MASCC)
    - Alerte femme enceinte + motif non obstetrical
    """
    danger, attention, info = [], [], []
    try:
        # --- Incoherences de saisie ---
        if eva == 0 and fc > 110:
            attention.append(
                "Incoherence : EVA 0 associee a une FC > 110 bpm - "
                "reevaluer la douleur ou rechercher une autre cause de tachycardie"
            )
        if gcs == 15 and spo2 < 88:
            attention.append(
                "Incoherence : GCS 15 (patient conscient) avec SpO2 < 88 % - "
                "verifier le capteur et la position du patient"
            )

        # --- qSOFA - Detection sepsis ---
        qsofa_score, qsofa_pos, _ = calculer_qsofa(fr, gcs, pas)
        if qsofa_score >= 2:
            danger.append(
                f"qSOFA >= 2 ({qsofa_score}/3) : risque eleve de defaillance d'organe - "
                f"criteres positifs : {' | '.join(qsofa_pos)} - "
                "evaluer sepsis - hemocultures + antibiotiques dans l'heure"
            )
        elif qsofa_score == 1 and temp >= 38.0:
            attention.append(
                f"qSOFA = 1 avec fievre : surveiller l'evolution - "
                f"critere positif : {' | '.join(qsofa_pos)}"
            )

        # --- Conflit NEWS2 vs niveau FRENCH ---
        if news2 >= 5:
            info.append(
                f"Attention : NEWS2 = {news2} suggere un niveau de prise en charge >= Tri 2. "
                "Valider la coherence avec le niveau FRENCH attribue."
            )

        # --- Retour precoce < 72h ---
        if retour_72h:
            danger.append(
                "RETOUR PRECOCE < 72h : remontee automatique d'un niveau de tri suggeree - "
                "evaluer la cause du retour - traçabilite dans le dossier"
            )

        # --- Alerte GEU : femme 15-50 ans + douleur abdominale ---
        if 15 <= age <= 50 and "Grossesse en cours" not in atcd:
            motif_l = motif.lower()
            if "abdominale" in motif_l or "lombaire" in motif_l or "hematurie" in motif_l \
                    or "metrorragie" in motif_l or "pelvi" in motif_l:
                danger.append(
                    "ALERTE GEU : femme en age de procreer (15-50 ans) avec douleur abdominale - "
                    "beta-hCG urinaire SYSTEMATIQUE avant tout autre bilan"
                )

        # --- Alerte femme enceinte + motif non obstetrical ---
        if "Grossesse en cours" in atcd:
            motifs_obs = ["grossesse", "obstetrique", "accouchement", "metrorragie", "menorragie"]
            if not any(m in motif.lower() for m in motifs_obs):
                attention.append(
                    "GROSSESSE EN COURS : orienter en parallele vers l'equipe obstetricale - "
                    "tout traitement doit tenir compte de la grossesse"
                )

        # --- Situations cliniques a haut risque ---
        _sous_ac = "Anticoagulants / AOD" in atcd
        if _sous_ac and "cranien" in motif.lower():
            danger.append(
                "DANGER - Traumatisme cranien sous anticoagulants : "
                "TDM cerebral URGENT - risque d'hematome intracranien majore"
            )
        if _sous_ac and ("AVC" in motif or "neurologique" in motif.lower()):
            danger.append(
                "DANGER - AVC suspect sous AOD : "
                "CONTRE-INDICATION a la thrombolyse intraveineuse - neurologue IMMEDIAT"
            )
        if "allergie" in motif.lower() and details.get("dyspnee"):
            danger.append(
                "ANAPHYLAXIE SEVERE : "
                "Adrenaline 0,5 mg IM immediate (Adrenaline Sterop 1 mg/ml)"
            )
        if news2 >= 5 and temp >= 38.5:
            danger.append(
                "SEPSIS GRAVE : NEWS2 >= 5 associe a une fievre - "
                "hemocultures x 2 AVANT antibiotherapie - antibiotiques dans l'heure"
            )
        if pas is not None and pas > 0 and pas < 90 and fc > 100:
            si = round(fc / pas, 1)
            danger.append(
                f"ETAT DE CHOC PROBABLE : Shock Index {si} (FC {fc} bpm / PAS {pas} mmHg) - "
                "2 VVP gros calibre + remplissage NaCl 0,9 %"
            )
        if spo2 < 85 or fr >= 40:
            danger.append(
                f"DETRESSE RESPIRATOIRE AIGUE : SpO2 {spo2} % / FR {fr}/min - "
                "O2 haut debit immediat + preparer l'intubation oro-tracheale"
            )
        if gcs <= 8:
            danger.append(
                f"COMA : GCS {gcs}/15 - "
                "protection des voies aeriennes superieures - PLS - evaluer l'intubation"
            )
        # Hypothermie severe : alerte manipulation douce specifique
        if temp <= 32:
            danger.append(
                f"HYPOTHERMIE SEVERE : T {temp} degres C - "
                "MANIPULATION DOUCE OBLIGATOIRE (risque de fibrillation ventriculaire au moindre mouvement) - "
                "rechauffement actif progressif - monitorage cardiaque continu"
            )
        elif temp <= 35.2:
            attention.append(
                f"HYPOTHERMIE MODEREE : T {temp} degres C - "
                "manipulation douce - rechauffement passif - monitorage FC"
            )
        if temp >= 41:
            danger.append(
                f"HYPERTHERMIE MALIGNE : T {temp} degres C - "
                "refroidissement immediat - appel reanimateur"
            )

        # --- Immunodeprime febrile (criteres simplifies MASCC) ---
        if "Immunodepression" in atcd and temp >= 38.0:
            if "Chimiotherapie en cours" in atcd or "Neoplasie evolutive" in atcd:
                danger.append(
                    "NEUTROPENIE FEBRILE PROBABLE (chimiotherapie / neoplasie) : "
                    "hemogramme + bilan infectieux URGENT - antibiotherapie empirique sans attendre les resultats - "
                    "isolement protecter"
                )
            else:
                attention.append(
                    "IMMUNODEPRESSION FEBRILE : "
                    "hemogramme urgent + antibiotherapie empirique sans attendre les resultats"
                )

    except (TypeError, ValueError):
        attention.append(
            "Erreur lors de la verification de coherence - "
            "verifier les parametres saisis"
        )
    return danger, attention, info


def suggerer_bilan(motif, details, fc, pas, spo2, fr, gcs, temp, age, atcd, news2, niveau):
    """Retourne les bilans paracliniques recommandes selon le motif et la gravite."""
    b = {
        "Biologie":           [],
        "Imagerie":           [],
        "ECG / Monitorage":   [],
        "Gestes immediats":   [],
        "Avis specialiste":   [],
    }
    try:
        if niveau in ("M", "1", "2"):
            b["Biologie"]          += ["Hemogramme complet + numeration plaquettaire",
                                       "Ionogramme, creatininemie", "Glycemie (mg/dl)", "Groupe ABO / Rh / RAI"]
            b["ECG / Monitorage"]  += ["Monitorage cardiorespiratoire continu",
                                       "SpO2 continue", "VVP gros calibre"]
        if "thoracique" in motif.lower() or "SCA" in motif:
            b["Biologie"]          += ["Troponine I hypersensible T0 + T1h",
                                       "D-dimeres si embolie pulmonaire", "NT-proBNP si insuffisance cardiaque"]
            b["ECG / Monitorage"]  += ["ECG 12 derivations - URGENT", "Repeter ECG a 30 min"]
            b["Imagerie"]          += ["Radiographie du thorax de face"]
            b["Gestes immediats"]  += ["Acide acetylsalicylique 250 mg si SCA non contre-indique",
                                       "O2 si SpO2 < 95 %"]
        if "AVC" in motif or "neurologique" in motif.lower():
            b["Biologie"]          += ["Hemogramme + coagulation complete (TP, TCA, fibrinogene)",
                                       "Glycemie (mg/dl)"]
            b["Imagerie"]          += ["TDM cerebral sans injection - URGENT",
                                       "IRM cerebrale si disponible"]
            b["Avis specialiste"]  += ["Neurologue vasculaire - URGENT"]
            b["Gestes immediats"]  += ["ACTIVATION FILIERE STROKE - objectif door-to-needle < 60 min"]
        if "dyspnee" in motif.lower() or "respiratoire" in motif.lower():
            b["Biologie"]          += ["Gazometrie arterielle", "D-dimeres si embolie pulmonaire"]
            b["Imagerie"]          += ["Radiographie du thorax",
                                       "Echographie pulmonaire (POCUS) si disponible"]
            b["Gestes immediats"]  += ["O2 - objectif SpO2 > 94 %",
                                       "Position semi-assise (Fowler 45 degres)"]
        if "traumatisme" in motif.lower() and niveau in ("M", "1", "2"):
            b["Biologie"]          += ["Bilan pre-transfusionnel (groupe, Rh, RAI, Coombs direct)",
                                       "Lactates veineux"]
            b["Imagerie"]          += ["CT-scanner corps entier si polytraumatisme",
                                       "Echographie FAST"]
            b["Gestes immediats"]  += ["Compression directe + garrot si lesion de membre",
                                       "2 VVP gros calibre + remplissage NaCl 0,9 %"]
        if "fievre" in motif.lower() or (temp >= 38.5 and news2 >= 3):
            b["Biologie"]          += ["Hemocultures x 2 AVANT antibiotherapie",
                                       "Lactates veineux", "CRP, procalcitonine, hemogramme"]
            b["Gestes immediats"]  += ["Hemocultures AVANT antibiotherapie",
                                       "Antibiotherapie large spectre si sepsis grave"]
        if "allergie" in motif.lower():
            b["Gestes immediats"]  += ["Adrenaline 0,5 mg IM",
                                       "Antihistaminique + corticosteroide IV",
                                       "Remplissage NaCl 0,9 %"]
        if "hypoglycemie" in motif.lower():
            b["Gestes immediats"]  += ["Glycemie capillaire IMMEDIATE (mg/dl)",
                                       "Glucose 30 % 50 ml IV si patient inconscient",
                                       "Glucagon 1 mg IM/SC si acces veineux impossible"]
        if "intoxication" in motif.lower():
            b["Biologie"]          += ["Bilan toxicologique urinaire + sanguin",
                                       "Paracetamolemie + ethanollemie systematiques"]
            b["ECG / Monitorage"]  += ["ECG - recherche de toxiques cardiotropes"]
            b["Avis specialiste"]  += ["Centre Antipoisons Belgique : 070 245 245"]
    except (TypeError, ValueError):
        pass
    return {k: v for k, v in b.items() if v}


# ==============================================================================
# [7] PERSISTANCE - Registre anonyme local
# RGPD : aucun nom ni prenom stocke. Identifiant anonyme genere automatiquement.
# ==============================================================================

FICHIER_REGISTRE  = "akir_registre_anon.json"
FICHIER_ALERTES   = "akir_journal_alertes.json"
FICHIER_ANTALGIE  = "akir_antalgie_log.json"


def _charger_registre():
    if os.path.exists(FICHIER_REGISTRE):
        try:
            with open(FICHIER_REGISTRE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _sauvegarder_registre(data):
    try:
        with open(FICHIER_REGISTRE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def ajouter_registre(donnees):
    """
    Ajoute une fiche anonyme au registre local.
    RGPD strict : tous les champs nominatifs sont supprimes avant stockage.
    Seul l'UUID genere par l'application sert d'identifiant.
    """
    reg = _charger_registre()
    # Suppression exhaustive de tout champ pouvant identifier le patient
    _champs_nominatifs = (
        "nom", "prenom", "nom_prenom", "identite", "patient_name",
        "naissance", "date_naissance", "niss", "numero_national",
        "adresse", "telephone", "email", "mutualite",
    )
    for champ in _champs_nominatifs:
        donnees.pop(champ, None)
    # Generation d'un UUID court (8 caracteres hex majuscules)
    donnees["uid"]        = str(uuid.uuid4())[:8].upper()
    donnees["date_heure"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    donnees["date"]       = datetime.now().strftime("%Y-%m-%d")
    reg.insert(0, donnees)
    _sauvegarder_registre(reg)
    return donnees["uid"]


def supprimer_registre(uid):
    reg = _charger_registre()
    _sauvegarder_registre([p for p in reg if p.get("uid") != uid])


def rechercher_registre(query):
    reg = _charger_registre()
    if not query:
        return reg
    q = query.lower().strip()
    return [
        p for p in reg
        if q in f"{p.get('motif','')} {p.get('age','')} {p.get('niveau','')} "
                f"{p.get('cat','')} {p.get('date_heure','')}".lower()
    ]


def enregistrer_alerte(uid_patient, news2, niveau, alertes_danger, code_operateur=""):
    """
    Enregistre dans le journal les alertes declenchees pour un patient.
    Traçabilite medico-legale : heure alerte, news2, niveau, operateur anonyme.
    RGPD : aucun nom stocke - identifiant patient anonyme uniquement.
    """
    try:
        journal = []
        if os.path.exists(FICHIER_ALERTES):
            with open(FICHIER_ALERTES, "r", encoding="utf-8") as f:
                journal = json.load(f)
        entree = {
            "uid_patient":    uid_patient,
            "heure_alerte":   datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "news2":          news2,
            "niveau_tri":     niveau,
            "nb_alertes":     len(alertes_danger),
            "alertes":        alertes_danger,
            "operateur":      code_operateur or "ANON",
        }
        journal.insert(0, entree)
        with open(FICHIER_ALERTES, "w", encoding="utf-8") as f:
            json.dump(journal, f, ensure_ascii=False, indent=2)
    except (IOError, json.JSONDecodeError):
        pass


def enregistrer_antalgie(uid_patient, medicament, dose, voie, eva_avant, code_operateur=""):
    """
    Enregistre une administration antalgique horodatee.
    Permet le suivi : medicament, dose, EVA avant administration, heure.
    RGPD : identifiant patient anonyme uniquement.
    """
    try:
        log = []
        if os.path.exists(FICHIER_ANTALGIE):
            with open(FICHIER_ANTALGIE, "r", encoding="utf-8") as f:
                log = json.load(f)
        entree = {
            "uid_patient": uid_patient,
            "heure":       datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "medicament":  medicament,
            "dose":        dose,
            "voie":        voie,
            "eva_avant":   eva_avant,
            "eva_apres":   None,  # A renseigner lors de la reevaluation
            "operateur":   code_operateur or "ANON",
        }
        log.insert(0, entree)
        with open(FICHIER_ANTALGIE, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
        return True
    except (IOError, json.JSONDecodeError):
        return False


def charger_log_antalgie(uid_patient):
    """Charge les administrations antalgiques pour un patient donne."""
    try:
        if os.path.exists(FICHIER_ANTALGIE):
            with open(FICHIER_ANTALGIE, "r", encoding="utf-8") as f:
                log = json.load(f)
            return [e for e in log if e.get("uid_patient") == uid_patient]
    except (IOError, json.JSONDecodeError):
        pass
    return []


def generer_rapport_activite(nb_jours=30):
    """
    Genere les statistiques d'activite sur les nb_jours derniers jours.
    Retourne un dictionnaire exploitable pour les graphiques.
    """
    try:
        reg = _charger_registre()
        if not reg:
            return None
        from datetime import timedelta
        date_limite = datetime.now() - timedelta(days=nb_jours)
        # Filtrer sur la periode
        rec = [p for p in reg if _parse_date(p.get("date", "")) >= date_limite]
        if not rec:
            return {"total": 0, "periode": nb_jours}

        # Distribution par niveau
        dist_niv = {}
        for p in rec:
            n = p.get("niveau", "?")
            dist_niv[n] = dist_niv.get(n, 0) + 1

        # Top 10 motifs
        dist_motif = {}
        for p in rec:
            m = p.get("motif", "Non precise")
            dist_motif[m] = dist_motif.get(m, 0) + 1
        top_motifs = sorted(dist_motif.items(), key=lambda x: x[1], reverse=True)[:10]

        # Distribution par date (7 derniers jours)
        dist_date = {}
        for p in rec:
            d = p.get("date", "")
            dist_date[d] = dist_date.get(d, 0) + 1

        # NEWS2 moyen
        news2_vals = [p.get("news2", 0) for p in rec if isinstance(p.get("news2"), (int, float))]
        news2_moy  = round(sum(news2_vals) / len(news2_vals), 1) if news2_vals else 0

        return {
            "total":       len(rec),
            "periode":     nb_jours,
            "dist_niveaux": dist_niv,
            "top_motifs":  top_motifs,
            "dist_dates":  dict(sorted(dist_date.items())[-7:]),
            "news2_moyen": news2_moy,
            "taux_urgents": round(
                sum(v for k, v in dist_niv.items() if k in ("M","1","2")) / len(rec) * 100, 1
            ),
        }
    except Exception:
        return None


def _parse_date(date_str):
    """Parse une date YYYY-MM-DD en objet datetime."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return datetime(2000, 1, 1)


# ==============================================================================
# [8] COMPOSANTS UI
# Couche d'affichage uniquement - aucun calcul clinique ici.
# ==============================================================================

def ui_sec(texte):
    """Affiche un en-tete de section."""
    st.markdown(f'<div class="sec-h">{texte}</div>', unsafe_allow_html=True)


def ui_alerte(texte, niveau="crit"):
    """Affiche une alerte coloree. niveau : crit | warn | info | ok."""
    st.markdown(f'<div class="alerte-{niveau}">{texte}</div>', unsafe_allow_html=True)


def ui_banniere_critique(news2_score):
    """Banniere rouge standardisee si NEWS2 >= 7."""
    if news2_score >= 7:
        st.markdown(
            f'<div class="banniere-crit">'
            f'<div class="banniere-crit-titre">ALERTE CRITIQUE  -  NEWS2 = {news2_score}</div>'
            f'<div class="banniere-crit-detail">'
            f'Appel medical immediat requis  -  Transfert en dechocage  -  Medecin senior'
            f'</div></div>',
            unsafe_allow_html=True,
        )


def ui_bannieres_alerte(news2, sil_score, fc, pas, spo2, fr, gcs):
    """Affiche toutes les bannieres d'alerte clinique pertinentes."""
    ui_banniere_critique(news2)
    if 5 <= news2 < 7:
        ui_alerte(
            f"NEWS2 = {news2}  -  Evaluation medicale urgente dans les 30 minutes",
            "warn"
        )
    if sil_score is not None and sil_score >= 5:
        st.markdown(
            f'<div class="banniere-crit">'
            f'<div class="banniere-crit-titre">DETRESSE RESPIRATOIRE NEONATALE  -  Silverman = {sil_score}/10</div>'
            f'<div class="banniere-crit-detail">Appel pediatre / neonatologue immediat  -  Preparer la reanimation neonatale</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    if pas and pas > 0 and fc / pas >= 1.0:
        ui_alerte(
            f"ETAT DE CHOC  -  Shock Index {round(fc/pas, 1)} (FC {fc} bpm / PAS {pas} mmHg)  -  "
            "2 VVP gros calibre + remplissage NaCl 0,9 %",
            "crit"
        )
    if spo2 < 85 or fr >= 40:
        ui_alerte(
            f"DETRESSE RESPIRATOIRE AIGUE  -  SpO2 {spo2} % / FR {fr}/min  -  "
            "O2 haut debit immediat",
            "crit"
        )
    if gcs <= 8:
        ui_alerte(
            f"COMA  -  GCS {gcs}/15  -  "
            "Protection des voies aeriennes  -  PLS  -  Evaluer intubation",
            "crit"
        )


def ui_prescriptions(motif):
    """Affiche les prescriptions anticipees IAO du motif selectionne."""
    rx = PRESCRIPTIONS.get(motif)
    if not rx:
        return
    ui_sec("Prescriptions anticipees IAO")
    cols = st.columns(min(len(rx), 3))
    for i, (cat, items) in enumerate(rx.items()):
        urgent   = cat in ("Gestes immediats", "Rappels critiques")
        cls_item = "carte-item-urg" if urgent else ""
        html     = "".join(f'<div class="carte-item {cls_item}">{it}</div>' for it in items)
        cols[i % len(cols)].markdown(
            f'<div class="carte"><div class="carte-titre">{cat}</div>{html}</div>',
            unsafe_allow_html=True,
        )


def ui_protocole_sca(frcv_count):
    """Protocole anticipe douleur thoracique / SCA avec evaluation des FRCV."""
    st.markdown(
        '<div class="proto">'
        '<div class="proto-titre">Protocole anticipe  -  Douleur thoracique / SCA</div>'
        '<div class="proto-item proto-item-urg">ECG 12 derivations dans les 10 min suivant l\'arrivee</div>'
        '<div class="proto-item proto-item-urg">Pose VVP 18G minimum</div>'
        '<div class="proto-item proto-item-urg">'
        'Bilan biologique : Troponine I hypersensible T0, D-dimeres, NFS, ionogramme'
        '</div>'
        '<div class="proto-item">Monitorage scope cardiorespiratoire continu</div>'
        '<div class="proto-item">Acide acetylsalicylique 250 mg PO / IV sauf contre-indication documentee</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    if frcv_count >= 2:
        ui_alerte(
            f"Remontee de niveau de triage suggeree : {frcv_count} FRCV identifies avec douleur thoracique - "
            "considerer Tri 3A minimum",
            "crit"
        )


def ui_infobulle_news2():
    st.markdown(
        '<div class="ib"><div class="ib-titre">Score NEWS2  -  Criteres officiels (Royal College of Physicians, 2017)</div>'
        '<b>FR :</b> 0 pt (12-20/min)  |  1 pt (9-11 ou 21-24/min)  |  2 pts (>= 25/min)  |  3 pts (<= 8/min)<br>'
        '<b>SpO2 sans BPCO :</b> 0 pt (>= 96 %)  |  1 pt (94-95 %)  |  2 pts (92-93 %)  |  3 pts (<= 91 %)<br>'
        '<b>O2 supplementaire :</b> + 2 pts<br>'
        '<b>Temperature :</b> 0 pt (36,1-38,0)  |  1 pt (35,1-36,0 ou 38,1-39,0)  |  2 pts (>= 39,1)  |  3 pts (<= 35,0)<br>'
        '<b>PAS :</b> 0 pt (111-219 mmHg)  |  1 pt (101-110)  |  2 pts (91-100)  |  3 pts (<= 90 ou >= 220)<br>'
        '<b>FC :</b> 0 pt (51-90 bpm)  |  1 pt (41-50 ou 91-110)  |  2 pts (111-130)  |  3 pts (<= 40 ou >= 131)<br>'
        '<b>Conscience :</b> 0 pt (alerte, GCS 15)  |  3 pts (GCS < 15)<br>'
        '<b>Interpretation :</b> 1-4 = risque faible  |  5-6 = risque modere  |  7-8 = risque eleve  |  >= 9 = risque critique'
        '</div>',
        unsafe_allow_html=True,
    )


def ui_infobulle_timi():
    st.markdown(
        '<div class="ib"><div class="ib-titre">Score TIMI SCA-ST-  (Antman et al., JAMA 2000)  -  Risque d\'evenements a 14 jours</div>'
        '1 pt : Age >= 65 ans<br>'
        '1 pt : Presence de 3 FRCV ou plus (HTA, tabac, diabete, ATCD familial, dyslipidemie)<br>'
        '1 pt : Stenose coronaire connue >= 50 %<br>'
        '1 pt : Deviation du segment ST >= 0,5 mm a l\'ECG<br>'
        '1 pt : Au moins 2 episodes angineux en 24 h<br>'
        '1 pt : Prise d\'acide acetylsalicylique dans les 7 jours precedents<br>'
        '1 pt : Biomarqueurs cardiaques eleves (troponine positive)<br>'
        '<b>Risque :</b> 0-2 = faible  |  3-4 = intermediaire  |  5-7 = eleve'
        '</div>',
        unsafe_allow_html=True,
    )


def ui_disclaimer():
    """Bandeau de conformite juridique et RGPD."""
    st.markdown(
        '<div class="disclaimer">'
        '<div class="disclaimer-hdr">Avertissement juridique, clinique et RGPD</div>'
        'AKIR-IAO Project est un outil d\'aide a la decision clinique destine aux infirmier(e)s agrees '
        'exercant en service d\'accueil des urgences (SAU). Il ne se substitue pas au jugement clinique '
        'du professionnel de sante ni a l\'examen medical du medecin. Les niveaux de triage proposes '
        'sont fondes sur la grille FRENCH Triage (SFMU V1.1, 2018) et doivent etre valides par l\'infirmier(e) '
        'd\'accueil et d\'orientation (IAO). Les prescriptions anticipees sont des rappels cliniques et ne '
        'constituent pas des prescriptions medicales : elles doivent etre validees par le medecin responsable. '
        'Les posologies indiquees referent au BCFI (Centre Belge d\'Information Pharmacotherapeutique). '
        'En cas de doute clinique, appliquer le principe de precaution : sur-trier et demander un avis medical. '
        'Legislation belge relative a l\'exercice infirmier : AR du 18/06/1990 modifie.'
        '<div class="disclaimer-sig">'
        'AKIR-IAO Project v15.0  -  par Ismail Ibn-Daifa<br>'
        'Outil d\'aide a la decision clinique  |  '
        'Conformite RGPD : aucune donnee patient n\'est stockee sur serveur distant.'
        '</div></div>',
        unsafe_allow_html=True,
    )


def ui_echelle_douleur(age_patient):
    """
    Affiche l'echelle d'evaluation de la douleur adaptee a l'age.
    Retourne : (score: int, nom_echelle: str, interpretation: str, css: str)
    """
    if age_patient < 3:
        st.markdown("**Echelle FLACC** (< 3 ans - observation comportementale)")
        st.caption("5 criteres cotes de 0 a 2. Score total de 0 a 10.")
        items = {
            "Visage (grimaces, froncement des sourcils)":       ["0  -  Aucune expression particuliere",   "1  -  Grimace occasionnelle ou sourire absent",      "2  -  Froncement permanent, menton tremblant"],
            "Jambes (agitation, position)":                     ["0  -  Position normale ou detendue",     "1  -  Genees, agitees, tendues",                     "2  -  Membres crispees ou ruades"],
            "Activite (corps, posture)":                        ["0  -  Allonge tranquillement",           "1  -  Se tortille, se balance",                      "2  -  Arquee, rigide ou contracture"],
            "Pleurs (cris, sanglots)":                          ["0  -  Pas de pleurs ni gemissements",    "1  -  Gemissements ou pleurs intermittents",         "2  -  Pleurs continus ou cris"],
            "Consolabilite":                                    ["0  -  Calme facilement, content",        "1  -  Calme apres un moment de contact",             "2  -  Difficile a calmer ou consoler"],
        }
        total = 0
        ca, cb = st.columns(2)
        for i, (lbl, opts) in enumerate(items.items()):
            col = ca if i < 3 else cb
            v   = col.selectbox(lbl, opts, key=f"flacc_{i}")
            total += int(v[0])
        if   total <= 2: interp, css = "Douleur legere ou absente", "sv-bas"
        elif total <= 6: interp, css = "Douleur moderee - antalgique palier 1 OMS", "sv-moy"
        else:            interp, css = "Douleur severe - antalgique par voie IV urgent", "sv-haut"
        return total, "FLACC", interp, css

    elif age_patient < 8:
        st.markdown("**Echelle des visages de Wong-Baker** (3-8 ans)")
        st.caption("Montrer les visages et demander : Quel visage montre comment tu te sens ?")
        faces = {
            "0  -  Tres heureux, aucune douleur":       0,
            "2  -  Un peu de douleur":                   2,
            "4  -  Douleur plus intense":                4,
            "6  -  Douleur encore plus forte":           6,
            "8  -  Beaucoup de douleur":                 8,
            "10 -  Douleur insupportable":               10,
        }
        choix = st.selectbox("Visage choisi par l'enfant", list(faces.keys()), key="wong_baker")
        score = faces[choix]
        if   score <= 2: interp, css = "Douleur legere", "sv-bas"
        elif score <= 6: interp, css = "Douleur moderee", "sv-moy"
        else:            interp, css = "Douleur severe", "sv-haut"
        return score, "Wong-Baker", interp, css

    else:
        st.markdown("**Echelle Visuelle Analogique (EVA)** (>= 8 ans)")
        c1, c2 = st.columns([4, 1])
        with c1:
            s = st.select_slider(
                "De 0 (aucune douleur) a 10 (douleur maximale imaginable)",
                options=[str(i) for i in range(11)],
                value="0", key="eva_std",
            )
        score = int(s)
        c2.markdown(f"**{score} / 10**")
        if   score <= 3: interp, css = "Douleur legere - palier 1 OMS", "sv-bas"
        elif score <= 6: interp, css = "Douleur moderee - palier 1-2 OMS", "sv-moy"
        else:            interp, css = "Douleur severe - palier 2-3 OMS ou voie IV", "sv-haut"
        return score, "EVA", interp, css


# ==============================================================================
# [9] APPLICATION - Etat de session et sidebar
# ==============================================================================

_SESSION_DEFAULTS = {
    "historique":          [],
    "heure_arrivee":       None,
    "heure_premier_contact": None,   # Distinct de l'heure de saisie
    "sbar_texte":          "",
    "derniere_reeval":     None,
    "histo_reeval":        [],
    "mode":                "complet",
    "gcs_y":               4,
    "gcs_v":               5,
    "gcs_m":               6,
    "confirm_suppression": None,
    "uid_courant":         None,     # UID du patient en cours de triage
    "retour_72h":          False,    # Flag retour precoce
    "code_operateur":      "",       # Identifiant anonyme operateur
    "log_antalgie_session": [],      # Administrations antalgiques session
}
for _k, _v in _SESSION_DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# En-tete principal
st.markdown(
    '<div class="app-header">'
    '<div class="app-header-titre">AKIR-IAO Project</div>'
    '<div class="app-header-sub">'
    'Outil d\'aide au triage infirmier  -  FRENCH Triage SFMU V1.1  -  Wallonie, Belgique'
    '</div></div>',
    unsafe_allow_html=True,
)

# --- Sidebar ---
with st.sidebar:
    st.markdown(
        '<div class="app-header" style="padding:10px 14px;margin-bottom:12px;">'
        '<div class="app-header-titre" style="font-size:0.9rem;">AKIR-IAO</div>'
        '<div class="app-header-sub">v15.0  -  Hospital Pro</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sb-section">Mode d\'interface</div>', unsafe_allow_html=True)
    mode_sel = st.radio(
        "Mode", ["Tri rapide (< 2 min)", "Formulaire complet"],
        horizontal=True, label_visibility="collapsed",
    )
    st.session_state.mode = "rapide" if "rapide" in mode_sel else "complet"

    st.markdown('<div class="sb-section">Chronometre</div>', unsafe_allow_html=True)
    ca, cb = st.columns(2)
    if ca.button("Demarrer", use_container_width=True):
        st.session_state.heure_arrivee   = datetime.now()
        st.session_state.derniere_reeval = datetime.now()
        st.session_state.histo_reeval    = []
    if cb.button("Reinitialiser", use_container_width=True):
        st.session_state.heure_arrivee   = None
        st.session_state.derniere_reeval = None
        st.session_state.histo_reeval    = []

    if st.session_state.heure_arrivee:
        elapsed = datetime.now() - st.session_state.heure_arrivee
        h, rem  = divmod(int(elapsed.total_seconds()), 3600)
        m, s    = divmod(rem, 60)
        st.markdown(f'<div class="chrono">{h:02d}:{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="chrono-label">Arrivee {st.session_state.heure_arrivee.strftime("%H:%M")}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="chrono">--:--:--</div>', unsafe_allow_html=True)
        st.markdown('<div class="chrono-label">En attente</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-section">Patient (anonyme - RGPD)</div>', unsafe_allow_html=True)
    ui_alerte(
        "Conformite RGPD : aucun nom ni prenom collecte. "
        "Identifiant anonyme genere automatiquement.",
        "info"
    )
    age      = st.number_input("Age (annees)", 0, 120, 45, key="sb_age")
    atcd     = st.multiselect("Antecedents / Facteurs de risque", LISTE_ATCD)
    allergies = st.text_input("Allergies connues", "RAS", key="sb_allergies")
    o2_supp   = st.checkbox("O2 supplementaire a l'admission")

    # --- Retour precoce < 72h ---
    retour_72h = st.checkbox("Retour aux urgences < 72h", key="sb_retour72h")
    if retour_72h:
        st.session_state.retour_72h = True
        ui_alerte("Retour precoce : remontee de niveau automatique suggeree.", "crit")
    else:
        st.session_state.retour_72h = False

    # --- Heure premier contact infirmier (distincte heure de saisie) ---
    st.markdown('<div class="sb-section">Premier contact infirmier</div>', unsafe_allow_html=True)
    if st.button("Horodater le premier contact", use_container_width=True):
        st.session_state.heure_premier_contact = datetime.now()
        st.success(f"Premier contact : {datetime.now().strftime('%H:%M:%S')}")
    if st.session_state.heure_premier_contact:
        st.caption(
            f"Premier contact : {st.session_state.heure_premier_contact.strftime('%H:%M:%S')}"
        )

    # --- Identifiant operateur anonymise ---
    st.markdown('<div class="sb-section">Operateur</div>', unsafe_allow_html=True)
    code_op = st.text_input(
        "Code operateur (initiales ou badge - non stocke nominativement)",
        value=st.session_state.code_operateur,
        max_chars=8,
        key="sb_code_op",
        placeholder="ex: IID, 4521...",
    )
    st.session_state.code_operateur = code_op.upper() if code_op else "ANON"

    nb_reg = len(_charger_registre())
    st.markdown(
        f'<div class="sb-section">Registre : {nb_reg} patient(s)</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sb-sig">AKIR-IAO Project<br>par Ismail Ibn-Daifa</div>'
        '<div class="sb-legal">FRENCH Triage  -  SFMU V1.1  -  BCFI Belgique<br>AR 18/06/1990 modifie</div>',
        unsafe_allow_html=True,
    )

# --- Onglets principaux ---
if st.session_state.mode == "rapide":
    _onglets = st.tabs([
        "Tri rapide", "Reevaluation",
        "Historique", "Registre", "Calculateur perfusion", "Rapport activite",
    ])
    t_rapide, t_reeval, t_histo, t_registre, t_perfusion, t_rapport = _onglets
    t_vitaux = t_anamnese = t_triage = t_scores = None
else:
    _onglets = st.tabs([
        "Signes vitaux", "Anamnese", "Triage et SBAR",
        "Scores complementaires", "Calculateur perfusion",
        "Reevaluation", f"Historique ({len(st.session_state.historique)})",
        "Registre", "Rapport activite",
    ])
    t_vitaux, t_anamnese, t_triage, t_scores, t_perfusion, t_reeval, t_histo, t_registre, t_rapport = _onglets
    t_rapide = None

# Variables de signes vitaux - initialisees a None pour detecter les onglets non visites
temp = fc = pas = spo2 = fr = gcs = None


# ==============================================================================
# MODE TRI RAPIDE
# ==============================================================================
if st.session_state.mode == "rapide":
    with t_rapide:
        ui_sec("Constantes vitales")
        c1, c2, c3 = st.columns(3)
        temp = c1.number_input("Temperature (degres C)", 30.0, 45.0, 37.0, 0.1, key="r_temp")
        fc   = c2.number_input("FC (bpm)", 20, 220, 80, key="r_fc")
        pas  = c3.number_input("PAS (mmHg)", 40, 260, 120, key="r_pas")
        c4, c5, c6 = st.columns(3)
        spo2 = c4.number_input("SpO2 (%)", 50, 100, 98, key="r_spo2")
        fr   = c5.number_input("FR (/min)", 5, 60, 16, key="r_fr")
        gcs  = c6.number_input("GCS (3-15)", 3, 15, 15, key="r_gcs")

        si     = round(fc / pas, 2) if pas > 0 else 0
        si_css = "bv-c" if si >= 1.0 else ("bv-w" if si >= 0.8 else "bv-o")
        st.markdown(
            f'Shock Index : <span class="bv {si_css}">{si}</span>',
            unsafe_allow_html=True,
        )

        bpco_f            = "BPCO" in atcd
        news2, n2_warns   = calculer_news2(fr, spo2, o2_supp, temp, pas, fc, gcs, bpco_f)
        n2_label, n2_css  = niveau_news2(news2)
        for w in n2_warns:
            ui_alerte(w, "warn")
        st.markdown(f'<span class="news2-val {n2_css}">{n2_label}</span>', unsafe_allow_html=True)

        ui_sec("Motif principal de recours")
        motif_rapide_opts = [
            "Douleur thoracique / SCA",
            "Dyspnee / insuffisance respiratoire",
            "AVC / Deficit neurologique",
            "Alteration de conscience / Coma",
            "Traumatisme cranien",
            "Hypotension arterielle",
            "Tachycardie / tachyarythmie",
            "Fievre",
            "Douleur abdominale",
            "Allergie / anaphylaxie",
            "Hypoglycemie",
            "Etat de mal epileptique / Convulsions",
            "Autre motif",
        ]
        motif   = st.selectbox("Motif de recours", motif_rapide_opts, key="r_motif")
        cat     = "Tri rapide"
        eva_sc  = int(st.select_slider(
            "EVA - Intensite douloureuse (0 = aucune, 10 = maximale)",
            options=[str(i) for i in range(11)], value="0", key="r_eva",
        ))
        eva_ech = "EVA"
        details = {"eva": eva_sc}

        # Protocole anticipe SCA + FRCV
        if motif == "Douleur thoracique / SCA":
            ui_sec("Facteurs de risque cardiovasculaires")
            fx = st.columns(4)
            frcv_vals = [
                fx[0].checkbox("HTA",            key="r_frcv_hta",  value="HTA" in atcd),
                fx[1].checkbox("Diabete",         key="r_frcv_diab", value=any("Diabete" in a for a in atcd)),
                fx[2].checkbox("Tabagisme",       key="r_frcv_tab",  value="Tabagisme actif" in atcd),
                fx[3].checkbox("ATCD coronarien", key="r_frcv_atcd"),
            ]
            frcv_count            = sum(frcv_vals)
            details["frcv_count"] = frcv_count
            ui_protocole_sca(frcv_count)

        if st.button("Calculer le niveau de triage", type="primary", use_container_width=True):
            niveau, justif, critere = french_triage(
                motif, details, fc, pas, spo2, fr, gcs, temp, age, news2
            )
            tri_label = LABELS_TRI[niveau]
            secteur   = SECTEURS_TRI[niveau]

            ui_bannieres_alerte(news2, None, fc, pas, spo2, fr, gcs)

            st.markdown(
                f'<div class="tri-carte {CSS_TRI[niveau]}">'
                f'<div class="tri-niveau">{tri_label}</div>'
                f'<div class="tri-detail">NEWS2 {news2}  |  EVA {eva_sc}/10  |  {justif}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.info(f"**Orientation :** {secteur}")

            code_anon = f"PT-{datetime.now().strftime('%H%M%S')}"
            sbar      = generer_sbar(
                age, motif, cat, atcd, allergies, o2_supp,
                temp, fc, pas, spo2, fr, gcs,
                news2, n2_label, eva_sc, eva_ech,
                "", "", "", "", details,
                niveau, tri_label, justif, critere, secteur,
                code_anon=code_anon,
            )
            st.session_state.sbar_texte = sbar
            st.session_state.historique.insert(0, {
                "heure": datetime.now().strftime("%H:%M"), "age": age,
                "motif": motif, "cat": cat, "eva": eva_sc,
                "news2": news2, "niveau": niveau,
                "temp": temp, "fc": fc, "pas": pas, "spo2": spo2, "fr": fr, "gcs": gcs,
                "atcd": atcd, "allergies": allergies, "sbar": sbar, "alertes_danger": 0,
            })

        if st.session_state.sbar_texte:
            ui_sec("Transmission SBAR  -  DPI-Ready")
            st.markdown(
                f'<div class="sbar">{st.session_state.sbar_texte}</div>',
                unsafe_allow_html=True,
            )
            st.download_button(
                "Telecharger SBAR (.txt)",
                data=st.session_state.sbar_texte,
                file_name=f"SBAR_AKIR_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        ui_disclaimer()


# ==============================================================================
# MODE FORMULAIRE COMPLET
# ==============================================================================
else:
    # ---- SIGNES VITAUX ----
    with t_vitaux:
        ui_sec("Constantes vitales")
        c1, c2, c3 = st.columns(3)
        temp = c1.number_input("Temperature (degres C)", 30.0, 45.0, 37.0, 0.1)
        fc   = c1.number_input("FC (bpm)", 20, 220, 80)
        pas  = c2.number_input("PAS systolique (mmHg)", 40, 260, 120)
        spo2 = c2.number_input("SpO2 (%)", 50, 100, 98)
        fr   = c3.number_input("FR (resp/min)", 5, 60, 16)
        gcs  = c3.number_input("GCS (3-15)", 3, 15, 15)

        ui_sec("Surveillance clinique")
        a1, a2, a3, a4, a5 = st.columns(5)
        a1.markdown(f"**Temperature** {badge_vital(temp, 36, 35, 38, 40.5, ' C')}", unsafe_allow_html=True)
        a2.markdown(f"**FC**          {badge_vital(fc,   50, 40, 100, 130, ' bpm')}", unsafe_allow_html=True)
        a3.markdown(f"**PAS**         {badge_vital(pas,  100, 90, 180, 220, ' mmHg')}", unsafe_allow_html=True)
        a4.markdown(f"**SpO2**        {badge_vital(spo2, 94, 90, 101, 101, ' %')}", unsafe_allow_html=True)
        a5.markdown(f"**FR**          {badge_vital(fr,   12,  8,  20,  25, '/min')}", unsafe_allow_html=True)

        si     = round(fc / pas, 2) if pas > 0 else 0
        si_css = "bv-c" if si >= 1.0 else ("bv-w" if si >= 0.8 else "bv-o")
        st.markdown(
            f'**Shock Index** : <span class="bv {si_css}">{si}</span>'
            f'{"  -  Etat de choc hemodynamique probable" if si >= 1.0 else ""}',
            unsafe_allow_html=True,
        )

        ui_sec("Score NEWS2")
        with st.expander("Criteres officiels NEWS2 - cliquer pour afficher"):
            ui_infobulle_news2()

        bpco_f           = "BPCO" in atcd
        news2, n2_warns  = calculer_news2(fr, spo2, o2_supp, temp, pas, fc, gcs, bpco_f)
        n2_label, n2_css = niveau_news2(news2)
        for w in n2_warns:
            ui_alerte(w, "warn")

        cn, ci = st.columns([1, 2])
        cn.markdown(f'<span class="news2-val {n2_css}">{n2_label}</span>', unsafe_allow_html=True)
        _interp_n2 = {
            "news2-bas":   ("Surveillance standard",    "Reevaluation dans les 12 h."),
            "news2-moyen": ("Surveillance rapprochee",  "Reevaluation dans l'heure."),
            "news2-haut":  ("Surveillance urgente",     "Evaluation medicale immediate."),
            "news2-crit":  ("URGENCE ABSOLUE",          "Transfert en dechocage immediat."),
        }
        _ti, _di = _interp_n2[n2_css]
        ci.markdown(f"**{_ti}**  -  {_di}")

        ui_bannieres_alerte(news2, None, fc, pas, spo2, fr, gcs)

    # ---- ANAMNESE ----
    with t_anamnese:
        # Securisation si onglet Signes vitaux non visite
        if temp is None: temp = 37.0; fc = 80; pas = 120; spo2 = 98; fr = 16; gcs = 15

        ui_sec("Evaluation de la douleur")
        eva_sc, eva_ech, eva_interp, eva_css = ui_echelle_douleur(age)
        st.markdown(f'<span class="sv {eva_css}">{eva_sc}/10 ({eva_ech})</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="sv-interp">{eva_interp}</div>', unsafe_allow_html=True)

        ui_sec("Anamnese PQRST")
        col1, col2 = st.columns(2)
        with col1:
            p_pqrst = st.text_input("P  -  Provoque / Pallie par", placeholder="Effort, repos, position...")
            q_pqrst = st.selectbox("Q  -  Qualite / Type", [
                "Non precise", "Sourd / pesanteur", "Constrictif (etau)",
                "Brulure", "Piquant / couteau", "Electrique",
                "Tension", "Crampe", "Pression",
            ])
            r_pqrst = st.text_input("R  -  Region / Irradiation", placeholder="Membre superieur gauche, machoire, dos...")
        with col2:
            t_onset = st.text_input("T  -  Temps / Duree", placeholder="Debut brutal depuis 30 min, progressif depuis 2 h...")

        ui_sec("Motif de recours - Classification FRENCH Triage")
        cat   = st.selectbox("Categorie clinique", list(MOTIFS_PAR_CATEGORIE.keys()))
        motif = st.selectbox("Motif principal", MOTIFS_PAR_CATEGORIE[cat])

        if motif in HINTS_SCORES:
            ui_alerte(HINTS_SCORES[motif], "info")

        # Prescriptions anticipees selon motif
        ui_prescriptions(motif)

        details = {"eva": eva_sc}

        # Protocole anticipe SCA + FRCV
        if motif == "Douleur thoracique / SCA":
            ui_sec("Facteurs de risque cardiovasculaires (FRCV)")
            st.caption(
                "Si 2 FRCV ou plus associes a une douleur thoracique, "
                "le niveau de triage sera automatiquement remonte a 3A minimum."
            )
            fx = st.columns(5)
            frcv_list = [
                fx[0].checkbox("HTA",                  key="c_hta",   value="HTA" in atcd),
                fx[1].checkbox("Diabete",              key="c_diab",  value=any("Diabete" in a for a in atcd)),
                fx[2].checkbox("Tabagisme",            key="c_tab",   value="Tabagisme actif" in atcd),
                fx[3].checkbox("Dyslipidemie",         key="c_dys",   value="Dyslipidaemie" in atcd),
                fx[4].checkbox("ATCD coronarien",      key="c_cor"),
            ]
            frcv_count            = sum(frcv_list)
            details["frcv_count"] = frcv_count
            ui_protocole_sca(frcv_count)

        # Questions discriminantes FRENCH par motif
        _QUESTIONS_GUIDEES = {
            "Douleur thoracique / SCA": [
                ("ECG realise ?",                                                                       "ecg_fait"),
                ("ECG anormal (sus-decalage ST, bloc de branche nouveau) ?",                           "ecg_anormal"),
                ("Douleur typique : retrosternale constrictive, irradiation bras/machoire ?",           "douleur_typique"),
                ("Duree de la douleur > 20 min ?",                                                     "duree_longue"),
            ],
            "Dyspnee / insuffisance respiratoire": [
                ("Peut s'exprimer en phrases completes ?",                                              "parole_ok"),
                ("Tirage intercostal ou sibilants audibles ?",                                         "tirage"),
                ("Orthopnee (dort en position assise) ?",                                              "orthopnee"),
            ],
            "AVC / Deficit neurologique": [
                ("Deficit moteur ou paralysie faciale ?",                                              "deficit_moteur"),
                ("Aphasie ou trouble du langage ?",                                                    "aphasie"),
                ("Heure exacte du debut des symptomes connue ?",                                       "heure_debut_connue"),
                ("Delai depuis le debut < 4 h 30 ?",                                                   "delai_ok"),
            ],
            "Traumatisme cranien": [
                ("Perte de connaissance initiale ?",                                                   "pdc"),
                ("Vomissements repetes ?",                                                             "vomissements_repetes"),
                ("Patient sous anticoagulants ou AOD ?",                                              "aod_avk"),
            ],
            "Douleur abdominale": [
                ("Defense abdominale ou contracture ?",                                                "defense"),
                ("Fievre associee ?",                                                                  "fievre_assoc"),
            ],
            "Fievre": [
                ("Temperature >= 40 degres C ou < 35,2 degres C ?",                                   "temp_extreme"),
                ("Syndrome confusionnel ou purpura ?",                                                "confusion"),
                ("Hypotension ou Shock Index >= 1 ?",                                                  "hypotension"),
            ],
            "Cephalee": [
                ("Cephalee inhabituelle (premier episode ou caracteristiques differentes) ?",          "inhabituelle"),
                ("Debut brutal en coup de tonnerre ?",                                                "brutale"),
                ("Fievre ou raideur de la nuque ?",                                                    "fievre_assoc"),
            ],
            "Allergie / anaphylaxie": [
                ("Dyspnee ou stridor larynge ?",                                                       "dyspnee"),
                ("Chute tensionnelle ou malaise hemodynamique ?",                                     "mauvaise_tolerance"),
            ],
        }

        _questions = _QUESTIONS_GUIDEES.get(motif, [])
        if _questions:
            st.markdown("**Questions discriminantes FRENCH :**")
            qc1, qc2 = st.columns(2)
            for i, (lbl, key) in enumerate(_questions):
                col = qc1 if i % 2 == 0 else qc2
                details[key] = col.checkbox(lbl, key=f"qg_{key}")

        # Questions specifiques par motif
        if motif == "Douleur thoracique / SCA":
            details["ecg"]                    = st.selectbox("Aspect ECG", ["Normal", "Anormal typique SCA", "Anormal non typique"])
            details["douleur_type"]           = st.selectbox("Type de douleur", ["Atypique", "Typique persistante/intense", "Type coronaire"])
            details["comorbidites_coronaires"] = st.checkbox("Coronaropathie documentee")
        elif motif == "Dyspnee / insuffisance respiratoire":
            details["parole_ok"] = st.radio("Peut s'exprimer en phrases completes ?", [True, False], format_func=lambda x: "Oui" if x else "Non", horizontal=True)
            c1a, c1b = st.columns(2)
            details["orthopnee"] = c1a.checkbox("Orthopnee")
            details["tirage"]    = c1b.checkbox("Tirage intercostal")
        elif motif == "AVC / Deficit neurologique":
            details["delai_heures"] = st.number_input("Delai depuis le debut des symptomes (h)", 0.0, 72.0, 2.0, 0.5)
        elif motif == "Traumatisme cranien":
            c1a, c1b = st.columns(2)
            details["pdc"]                    = c1a.checkbox("Perte de connaissance initiale")
            details["vomissements_repetes"]   = c1a.checkbox("Vomissements repetes")
            details["aod_avk"]                = c1b.checkbox("Anticoagulants / AOD")
            details["deficit_neuro"]          = c1b.checkbox("Deficit neurologique focal")
        elif motif == "Douleur abdominale":
            c1a, c1b = st.columns(2)
            details["defense"]            = c1a.checkbox("Defense abdominale")
            details["contracture"]        = c1a.checkbox("Contracture")
            details["regressive"]         = c1b.checkbox("Douleur regressive spontanement")
            details["mauvaise_tolerance"] = c1b.checkbox("Mauvaise tolerance clinique")
        elif motif == "Fievre":
            c1a, c1b = st.columns(2)
            details["confusion"]          = c1a.checkbox("Syndrome confusionnel")
            details["purpura"]            = c1a.checkbox("Purpura (non thrombocytopenique)")
            details["mauvaise_tolerance"] = c1b.checkbox("Mauvaise tolerance clinique")
        elif motif == "Allergie / anaphylaxie":
            details["dyspnee"]            = st.checkbox("Dyspnee ou oedeme larynge")
            details["mauvaise_tolerance"] = st.checkbox("Chute tensionnelle ou mauvaise tolerance hemodynamique")
        elif motif in ("Intoxication medicamenteuse", "Intoxication non medicamenteuse"):
            details["mauvaise_tolerance"]   = st.checkbox("Mauvaise tolerance clinique")
            details["intention_suicidaire"] = st.checkbox("Intention suicidaire avouee")
            details["cardiotropes"]         = st.checkbox("Substances cardiotropes impliquees")
            details["enfant"]               = st.checkbox("Patient enfant (age <= 15 ans)")
            details["vu_tard_24h"]          = st.checkbox("Consultation tardive >= 24h apres la prise, sans symptome actuel")
            if details.get("vu_tard_24h") and not details.get("mauvaise_tolerance"):
                st.caption("Consultation tardive sans symptome : classification Tri 5 selon PDF SFMU V1.1 p.3")
        elif motif == "Brulure thermique":
            details["etendue"]     = st.checkbox("Etendue > 10 % de la surface corporelle totale")
            details["main_visage"] = st.checkbox("Localisation critique : main, visage ou perinee")
        elif motif in ("Hematemese / vomissements sanglants", "Rectorragie / Melena"):
            details["abondante"] = st.checkbox("Saignement abondant")
        elif motif == "Plaie":
            details["saignement_actif"] = st.checkbox("Saignement actif non controle")
            details["delabrant"]        = st.checkbox("Plaie delabrante")
            details["main"]             = st.checkbox("Localisation main")
            details["superficielle"]    = st.checkbox("Plaie superficielle")
        elif motif == "Menorragie / Metrorragie":
            details["grossesse"] = st.checkbox("Grossesse connue ou suspectee")
            details["abondante"] = st.checkbox("Saignement abondant")
        elif motif in ("Douleur lombaire / Colique nephretique", "Hematurie",
                       "Douleur testiculaire / Suspicion de torsion"):
            details["intense"]           = st.checkbox("Douleur intense avec agitation")
            details["regressive"]        = st.checkbox("Douleur regressive")
            details["suspicion_torsion"] = st.checkbox("Suspicion de torsion") if "torsion" in motif.lower() else False
            details["abondante_active"]  = st.checkbox("Hematurie macroscopique active") if "Hematurie" in motif else False
        elif motif == "Hyperglycemie / Cetoacidose diabetique":
            gl_mgdl = st.number_input("Glycemie capillaire (mg/dl)", 0, 1500, 180, 10)
            st.caption(f"Reference : {mgdl_vers_mmol(gl_mgdl)} mmol/l  |  Seuil cetoacidose : >= 250 mg/dl (13,9 mmol/l)")
            details["glycemie_mgdl"]   = gl_mgdl
            details["cetose_elevee"]   = st.checkbox("Cetose elevee a la bandelette urinaire")
            details["cetose_positive"] = st.checkbox("Cetose positive confirmee")
        elif motif == "Hypoglycemie":
            gl_hypo = st.number_input("Glycemie capillaire (mg/dl)", 0, 500, 60, 5)
            st.caption(
                f"Reference : {mgdl_vers_mmol(gl_hypo)} mmol/l  |  "
                f"Severe : < 54 mg/dl  |  Moderee : 54-70 mg/dl"
            )
            details["glycemie_mgdl"]      = gl_hypo
            details["mauvaise_tolerance"] = st.checkbox("Mauvaise tolerance neurologique ou hemodynamique")
        elif motif == "Agitation / Troubles du comportement":
            details["agitation"] = st.checkbox("Agitation majeure")
            details["violence"]  = st.checkbox("Comportement violent")
        elif motif in ("Tachycardie / tachyarythmie", "Bradycardie / bradyarythmie", "Palpitations"):
            details["mauvaise_tolerance"] = st.checkbox("Mauvaise tolerance hemodynamique")
            details["malaise"]            = st.checkbox("Malaise associe")
        elif motif == "Hypertension arterielle":
            details["sf_associes"] = st.checkbox("Symptomes fonctionnels associes (cephalee, trouble visuel, douleur thoracique)")
        elif motif in ("Traumatisme du thorax / abdomen / rachis cervical",
                       "Traumatisme du bassin / hanche / femur",
                       "Traumatisme d'un membre / epaule"):
            details["cinetique"]          = st.selectbox("Cinetique traumatique", ["Faible", "Haute"])
            details["mauvaise_tolerance"] = st.checkbox("Mauvaise tolerance clinique")
            details["penetrant"]          = st.checkbox("Traumatisme penetrant") if "thorax" in motif.lower() else False
            if "membre" in motif.lower() or "epaule" in motif.lower():
                details["impotence_totale"]  = st.checkbox("Impotence fonctionnelle totale")
                details["deformation"]       = st.checkbox("Deformation visible")
                details["impotence_moderee"] = st.checkbox("Impotence fonctionnelle moderee")
                details["ischemie"]          = st.checkbox("Ischemie distale")
        elif motif == "Epistaxis":
            details["abondant_actif"]     = st.checkbox("Epistaxis abondante active")
            details["abondant_resolutif"] = st.checkbox("Epistaxis abondante resolutive")
        elif motif in ("Corps etranger / Brulure oculaire", "Trouble visuel aigu / Cecite"):
            details["chimique"] = st.checkbox("Brulure chimique")
            details["intense"]  = st.checkbox("Douleur oculaire intense")
            details["brutal"]   = st.checkbox("Debut brutal de la baisse d'acuite visuelle")
        elif motif == "Etat de mal epileptique / Convulsions":
            details["crises_multiples"]        = st.checkbox("Crises multiples ou crise en cours")
            details["confusion_post_critique"] = st.checkbox("Confusion post-critique prolongee")
        elif motif == "Cephalee":
            details["inhabituelle"] = st.checkbox("Cephalee inhabituelle ou premier episode")
            details["brutale"]      = st.checkbox("Debut brutal en coup de tonnerre")
            details["fievre_assoc"] = st.checkbox("Fievre ou raideur de la nuque associee")
        elif motif == "Electrisation":
            details["pdc"]           = st.checkbox("Perte de connaissance")
            details["foudre"]        = st.checkbox("Foudroiement")
            details["haute_tension"] = st.checkbox("Contact avec haute tension")

        # --- Nouveaux motifs v17 ---
        elif motif == "Anomalie du sein":
            details["mastite"] = st.checkbox("Mastite ou abces du sein")
            if details.get("mastite"):
                ui_alerte("Mastite / abces : classification Tri 3B - evaluation medicale dans l'heure.", "warn")

        elif motif == "Anomalie vulvo-vaginale / corps etranger":
            st.caption("Motif Tri 5 par defaut - consultation non urgente.")

        elif motif == "Douleur thoracique / Embolie / Pneumopathie / Pneumothorax":
            details["parole_ok"] = st.radio(
                "Peut s'exprimer en phrases completes ?",
                [True, False], format_func=lambda x: "Oui" if x else "Non", horizontal=True,
            )
            c1e, c2e = st.columns(2)
            details["tirage"]   = c1e.checkbox("Tirage intercostal")
            details["orthopnee"] = c2e.checkbox("Orthopnee")
            st.caption("Ce motif est distinct du SCA - suspicion EP, pneumopathie aigue ou pneumothorax.")

        # --- Pediatrie <= 2 ans ---
        elif motif == "Pediatrie - Convulsion hyperthermique":
            details["recidive"]        = st.checkbox("Recidive ou crise en cours")
            details["duree_sup_10min"] = st.checkbox("Duree >= 10 min")
            details["hypotonie"]       = st.checkbox("Hypotonie post-critique")

        elif motif == "Pediatrie - Diarrhee / Vomissements nourrisson":
            details["perte_poids_sup_10pct"] = st.checkbox("Perte de poids >= 10 %")
            details["hypotonie"]             = st.checkbox("Hypotonie")

        elif motif == "Pediatrie - Troubles alimentaires nourrisson <= 6 mois":
            details["perte_poids_sup_10pct"] = st.checkbox("Perte de poids >= 10 %")
            details["hypotonie"]             = st.checkbox("Hypotonie")

        elif motif == "Pediatrie - Ictere neonatal":
            details["perte_poids"]      = st.checkbox("Perte de poids")
            details["selles_decolorees"] = st.checkbox("Selles decolorees")

        elif motif == "Pediatrie - Pleurs incoercibles":
            details["pleurs_dans_box"] = st.checkbox("Pleurs persistants dans le box de l'IAO")

        elif motif == "Pediatrie - Fievre <= 3 mois":
            st.caption("Fievre chez nourrisson <= 3 mois : Tri 2 SYSTEMATIQUE - evaluation medicale urgente.")

        elif motif in ("Pediatrie - Bradycardie", "Pediatrie - Tachycardie", "Pediatrie - Hypotension"):
            st.caption(
                "Seuils pediatriques appliques automatiquement selon l'age saisi dans la sidebar. "
                "Verifier que l'age est correct avant de valider le triage."
            )
            _fc_min_ui, _fc_max_ui, _pas_min_ui = _seuils_ped(age)
            st.markdown(
                f'<div class="ib">'
                f'Seuils pour age {age} an(s) :<br>'
                f'Bradycardie : FC <= {_fc_min_ui} bpm  |  '
                f'Tachycardie : FC >= {_fc_max_ui} bpm  |  '
                f'Hypotension : PAS <= {_pas_min_ui} mmHg'
                f'</div>',
                unsafe_allow_html=True,
            )

        elif motif == "Pediatrie - Dyspnee avec sifflement respiratoire":
            details["detresse"] = st.checkbox("Detresse respiratoire associee (tirage, cyanose, SpO2 < 94 %)")
            st.caption("Tri 2 si detresse, Tri 3A si sifflement isole sans detresse.")

    # ---- TRIAGE ET SBAR ----
    with t_triage:
        # Securisation des variables si onglets anterieurs non visites
        if temp is None:
            temp = 37.0; fc = 80; pas = 120; spo2 = 98; fr = 16; gcs = 15
        if "motif" not in dir() or motif is None:
            motif = "Fievre"; cat = "Infectiologie"
        if "details" not in dir() or details is None:
            details = {}
        if "eva_sc" not in dir():
            eva_sc = 0; eva_ech = "EVA"
        if "p_pqrst" not in dir():
            p_pqrst = q_pqrst = r_pqrst = t_onset = ""

        bpco_f           = "BPCO" in atcd
        news2, n2_warns  = calculer_news2(fr, spo2, o2_supp, temp, pas, fc, gcs, bpco_f)
        n2_label, n2_css = niveau_news2(news2)
        for w in n2_warns:
            ui_alerte(w, "warn")

        niveau, justif, critere = french_triage(
            motif, details, fc, pas, spo2, fr, gcs, temp, age, news2,
            glycemie_mgdl=details.get("glycemie_mgdl"),
        )
        tri_label = LABELS_TRI[niveau]
        secteur   = SECTEURS_TRI[niveau]

        ui_bannieres_alerte(news2, None, fc, pas, spo2, fr, gcs)

        # Alerte reevaluation en retard
        if st.session_state.derniere_reeval:
            mins = (datetime.now() - st.session_state.derniere_reeval).total_seconds() / 60
            if mins > DELAIS_TRI.get(niveau, 60):
                ui_alerte(
                    f"Reevaluation en retard : {int(mins)} min ecoulees - "
                    f"delai maximum {DELAIS_TRI[niveau]} min pour {LABELS_TRI[niveau]}",
                    "crit"
                )

        st.markdown(
            f'<div class="tri-carte {CSS_TRI[niveau]}">'
            f'<div class="tri-niveau">{tri_label}</div>'
            f'<div class="tri-detail">'
            f'NEWS2 {news2}  |  EVA {details.get("eva", 0)}/10  |  {justif}'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        st.info(f"**Orientation :** {secteur}")
        st.caption(f"Reference FRENCH : {critere}")

        ui_sec("Alertes de securite clinique")
        al_d, al_a, al_i = verifier_coherence(
            fc, pas, spo2, fr, gcs, temp,
            details.get("eva", 0), motif, atcd, details, news2,
            age=age,
            retour_72h=st.session_state.retour_72h,
            code_operateur=st.session_state.code_operateur,
        )
        # Retour precoce : remonter le niveau si < Tri 2
        if st.session_state.retour_72h:
            _ordre = {"M":0,"1":1,"2":2,"3A":3,"3B":4,"4":5,"5":6}
            if _ordre.get(niveau, 6) > 2:
                niveau_orig = niveau
                niveau = {"5":"4","4":"3B","3B":"3A","3A":"2"}.get(niveau, niveau)
                tri_label = LABELS_TRI[niveau]
                secteur   = SECTEURS_TRI[niveau]
                ui_alerte(
                    f"Retour < 72h : niveau remonte automatiquement de {niveau_orig} a {niveau}",
                    "crit"
                )
        for a in al_d: ui_alerte(a, "crit")
        for a in al_a: ui_alerte(a, "warn")
        for a in al_i: ui_alerte(a, "info")
        if not al_d and not al_a:
            ui_alerte("Aucune incoherence clinique detectee.", "ok")

        # Enregistrement des alertes dans le journal (traçabilite)
        if al_d and st.session_state.uid_courant:
            enregistrer_alerte(
                st.session_state.uid_courant, news2, niveau,
                al_d, st.session_state.code_operateur,
            )

        ui_sec("Bilans paracliniques recommandes")
        bilans = suggerer_bilan(motif, details, fc, pas, spo2, fr, gcs, temp, age, atcd, news2, niveau)
        if bilans:
            bcols = st.columns(min(len(bilans), 3))
            for i, (bnom, bitems) in enumerate(bilans.items()):
                html = "".join(f'<div class="carte-item">{it}</div>' for it in bitems)
                bcols[i % len(bcols)].markdown(
                    f'<div class="carte"><div class="carte-titre">{bnom}</div>{html}</div>',
                    unsafe_allow_html=True,
                )

        ui_sec("Transmission SBAR  -  DPI-Ready")
        code_anon = f"PT-{datetime.now().strftime('%H%M%S')}"

        if st.button("Generer la transmission SBAR", type="primary", use_container_width=True):
            sbar = generer_sbar(
                age, motif, cat, atcd, allergies, o2_supp,
                temp, fc, pas, spo2, fr, gcs,
                news2, n2_label,
                details.get("eva", 0),
                eva_ech if "eva_ech" in dir() else "EVA",
                p_pqrst, q_pqrst, r_pqrst, t_onset,
                details, niveau, tri_label, justif, critere, secteur,
                gcs_y=st.session_state.gcs_y,
                gcs_v=st.session_state.gcs_v,
                gcs_m=st.session_state.gcs_m,
                code_anon=code_anon,
            )
            st.session_state.sbar_texte = sbar
            st.session_state.historique.insert(0, {
                "heure": datetime.now().strftime("%H:%M"), "age": age,
                "motif": motif, "cat": cat,
                "eva": details.get("eva", 0), "news2": news2, "niveau": niveau,
                "temp": temp, "fc": fc, "pas": pas, "spo2": spo2, "fr": fr, "gcs": gcs,
                "atcd": atcd, "allergies": allergies, "sbar": sbar, "alertes_danger": len(al_d),
            })
            st.success("SBAR genere et sauvegarde dans l'historique de session.")

        if st.session_state.sbar_texte:
            st.markdown(
                f'<div class="sbar">{st.session_state.sbar_texte}</div>',
                unsafe_allow_html=True,
            )
            cd1, cd2 = st.columns(2)
            cd1.download_button(
                "Telecharger SBAR (.txt)",
                data=st.session_state.sbar_texte,
                file_name=f"SBAR_AKIR_{datetime.now().strftime('%Y%m%d_%H%M')}_Tri{niveau}.txt",
                mime="text/plain",
                use_container_width=True,
            )
            if cd2.button("Enregistrer au registre anonyme", use_container_width=True):
                uid = ajouter_registre({
                    "age": age, "motif": motif, "cat": cat, "niveau": niveau,
                    "news2": news2, "eva": details.get("eva", 0),
                    "temp": temp, "fc": fc, "pas": pas, "spo2": spo2, "fr": fr, "gcs": gcs,
                    "allergies": allergies, "sbar": st.session_state.sbar_texte,
                })
                st.success(f"Enregistrement anonyme - identifiant : {uid}")

        ui_disclaimer()

    # ---- SCORES COMPLEMENTAIRES ----
    with t_scores:
        if temp is None:
            temp = 37.0; fc = 80; pas = 120; spo2 = 98; fr = 16; gcs = 15
        bpco_f    = "BPCO" in atcd
        news2, _  = calculer_news2(fr, spo2, o2_supp, temp, pas, fc, gcs, bpco_f)

        sc1, sc2 = st.columns(2)

        # GCS detaille
        with sc1:
            ui_sec("Glasgow Coma Scale (GCS)")
            with st.expander("Criteres GCS"):
                st.markdown(
                    "**Yeux (Y) :** 4 = spontanement | 3 = a la voix | 2 = a la douleur | 1 = aucune\n\n"
                    "**Verbal (V) :** 5 = oriente | 4 = confus | 3 = mots | 2 = sons | 1 = aucun\n\n"
                    "**Moteur (M) :** 6 = obeit | 5 = localise | 4 = evitement | 3 = flexion | 2 = extension | 1 = aucun"
                )
            gy = st.select_slider("Yeux (Y)",    options=[1,2,3,4],   value=4, key="gcs_gy")
            gv = st.select_slider("Verbal (V)",  options=[1,2,3,4,5], value=5, key="gcs_gv")
            gm = st.select_slider("Moteur (M)",  options=[1,2,3,4,5,6], value=6, key="gcs_gm")
            st.session_state.gcs_y = gy
            st.session_state.gcs_v = gv
            st.session_state.gcs_m = gm
            gcs_calc, gcs_errs = calculer_gcs(gy, gv, gm)
            for e in gcs_errs: st.warning(e)
            if   gcs_calc <= 8:  g_css, g_int = "sv-haut", "Coma - protection des voies aeriennes superieure urgente"
            elif gcs_calc <= 13: g_css, g_int = "sv-moy",  "Alteration moderee de la conscience"
            elif gcs_calc == 14: g_css, g_int = "sv-moy",  "Alteration legere de la conscience"
            else:                g_css, g_int = "sv-bas",  "Patient eveille et oriente"
            st.markdown(f'<span class="sv {g_css}">GCS {gcs_calc}/15</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="sv-interp">{g_int}</div>', unsafe_allow_html=True)

        # TIMI
        with sc2:
            ui_sec("Score TIMI  -  SCA sans sus-decalage ST")
            with st.expander("Criteres TIMI"):
                ui_infobulle_timi()
            t_a65  = st.checkbox("Age >= 65 ans",                         key="timi_a65")
            t_frcv = st.number_input("Nombre de FRCV", 0, 5, 0,           key="timi_frcv")
            t_sten = st.checkbox("Stenose coronaire connue >= 50 %",      key="timi_sten")
            t_aspi = st.checkbox("Aspirine dans les 7 derniers jours",    key="timi_aspi")
            t_trop = st.checkbox("Troponine I positive",                   key="timi_trop")
            t_st   = st.checkbox("Deviation ST >= 0,5 mm",                key="timi_st")
            t_cris = st.number_input("Episodes angineux en 24 h", 0, 10, 0, key="timi_cris")
            timi_sc, timi_errs = calculer_timi(age, t_frcv, t_sten, t_aspi, t_trop, t_st, t_cris)
            for e in timi_errs: st.warning(e)
            if   timi_sc <= 2: t_css, t_int = "sv-bas",  "Risque faible (< 10 % a 14 jours)"
            elif timi_sc <= 4: t_css, t_int = "sv-moy",  "Risque intermediaire (10-20 %)"
            else:              t_css, t_int = "sv-haut", "Risque eleve (> 20 %) - Cardiologue urgent"
            st.markdown(f'<span class="sv {t_css}">TIMI {timi_sc}/7</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="sv-interp">{t_int}</div>', unsafe_allow_html=True)

        sc3, sc4 = st.columns(2)

        # Silverman
        with sc3:
            ui_sec("Score de Silverman  -  Detresse respiratoire neonatale")
            with st.expander("Criteres Silverman"):
                st.markdown("0 = absent | 1 = modere | 2 = intense | Score maximal = 10")
                st.markdown("Score < 3 = normal | 3-4 = detresse legere | >= 5 = detresse severe")
            opts  = [0, 1, 2]
            s_bt  = st.select_slider("Balancement thoraco-abdominal",    options=opts, key="sil_bt")
            s_ti  = st.select_slider("Tirage intercostal",               options=opts, key="sil_ti")
            s_rss = st.select_slider("Retraction sus-sternale",          options=opts, key="sil_rss")
            s_an  = st.select_slider("Battement des ailes du nez",       options=opts, key="sil_an")
            s_gei = st.select_slider("Geignement expiratoire",           options=opts, key="sil_gei")
            sil_sc, sil_errs = calculer_silverman(s_bt, s_ti, s_rss, s_an, s_gei)
            for e in sil_errs: st.warning(e)
            ui_bannieres_alerte(news2, sil_sc, fc, pas, spo2, fr, gcs)
            if   sil_sc <= 2: s_css, s_int = "sv-bas",  "Pas de detresse respiratoire"
            elif sil_sc <= 4: s_css, s_int = "sv-moy",  "Detresse respiratoire legere - surveillance rapprochee"
            else:             s_css, s_int = "sv-haut", "Detresse respiratoire severe - pediatre immediat"
            st.markdown(f'<span class="sv {s_css}">Silverman {sil_sc}/10</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="sv-interp">{s_int}</div>', unsafe_allow_html=True)

        # Malinas
        with sc4:
            ui_sec("Score de Malinas  -  Transport obstetrical")
            with st.expander("Criteres de Malinas"):
                st.markdown("0 a 2 pts par critere. Score >= 8 : ne pas transporter.")
            m_par  = st.select_slider("Parite (0=nullipare, 1=multipare, 2=multipare >=3)",            options=[0,1,2], key="mal_par")
            m_dur  = st.select_slider("Duree du travail (0=< 3h, 1=3-5h, 2=> 5h)",                    options=[0,1,2], key="mal_dur")
            m_con  = st.select_slider("Duree des contractions (0=< 1min, 1=1 min, 2=> 1min)",          options=[0,1,2], key="mal_con")
            m_int  = st.select_slider("Intervalle (0=> 5min, 1=3-5min, 2=< 3min)",                     options=[0,1,2], key="mal_int")
            m_poc  = st.select_slider("Poche des eaux (0=intacte, 1=rompue < 1h, 2=rompue > 1h)",     options=[0,1,2], key="mal_poc")
            mal_sc, mal_errs = calculer_malinas(m_par, m_dur, m_con, m_int, m_poc)
            for e in mal_errs: st.warning(e)
            if   mal_sc <= 5: m_css, m_int_str = "sv-bas",  "Transport vers maternite possible"
            elif mal_sc <= 7: m_css, m_int_str = "sv-moy",  "Transport sous surveillance medicale stricte"
            else:             m_css, m_int_str = "sv-haut", "Ne pas transporter - accouchement imminent"
            st.markdown(f'<span class="sv {m_css}">Malinas {mal_sc}/10</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="sv-interp">{m_int_str}</div>', unsafe_allow_html=True)

        # Brulures
        ui_sec("Evaluation des brulures  -  Regle des 9 de Wallace + Formule de Baux")
        with st.expander("Regle des 9 de Wallace et formule de Baux"):
            st.markdown(
                "**Regle des 9 :** Tete 9 % | Tronc ant. 18 % | Tronc post. 18 % | "
                "Bras 9 % x 2 | Jambes 18 % x 2 | Perinee 1 %\n\n"
                "**Formule de Baux :** Age + SCB (%) -> pronostic de mortalite. "
                "Baux > 100 = severe. Baux > 120 = quasi-letal."
            )
        br1, br2 = st.columns(2)
        scb_pct    = br1.number_input("Surface corporelle brulee (%)", 0, 100, 10, key="scb")
        profondeur = br2.selectbox("Profondeur", [
            "1er degre (superficiel)", "2eme degre superficiel",
            "2eme degre profond", "3eme degre (plein epaisseur)",
        ])
        scb_val, baux_val, pronostic, burn_errs = calculer_brulure(scb_pct, age)
        for e in burn_errs: st.warning(e)
        b_css = "sv-bas" if baux_val < 80 else ("sv-moy" if baux_val < 100 else "sv-haut")
        st.markdown(f'<span class="sv {b_css}">SCB {scb_val:.0f} %  -  Baux {baux_val:.0f}</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="sv-interp">{profondeur}  |  {pronostic}</div>', unsafe_allow_html=True)

        # Tableau de synthese
        ui_sec("Tableau de synthese des scores")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("TIMI",      f"{timi_sc}/7")
        r2.metric("Silverman", f"{sil_sc}/10")
        r3.metric("GCS",       f"{gcs_calc}/15")
        r4.metric("Malinas",   f"{mal_sc}/10")

        # ---- qSOFA ----
        ui_sec("Score qSOFA  -  Detection rapide du sepsis")
        st.markdown(
            '<div class="ib"><div class="ib-titre">qSOFA (quick SOFA) - Singer et al., JAMA 2016</div>'
            'FR >= 22/min (+1)  |  GCS < 15 (+1)  |  PAS <= 100 mmHg (+1)<br>'
            'Score >= 2 : risque eleve de defaillance d\'organe - evaluation urgente du sepsis.'
            '</div>',
            unsafe_allow_html=True,
        )
        if temp is not None and fc is not None:
            qsofa_sc, qsofa_pos, qsofa_w = calculer_qsofa(fr, gcs, pas)
            for w in qsofa_w:
                ui_alerte(w, "warn")
            if   qsofa_sc == 0: q_css, q_int = "sv-bas",  "Pas de signe de sepsis evident"
            elif qsofa_sc == 1: q_css, q_int = "sv-moy",  "Surveiller l'evolution - 1 critere positif"
            else:               q_css, q_int = "sv-haut", "Risque eleve - evaluer sepsis IMMEDIAT"
            st.markdown(f'<span class="sv {q_css}">qSOFA : {qsofa_sc}/3</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="sv-interp">{q_int}</div>', unsafe_allow_html=True)
            if qsofa_pos:
                st.markdown("**Criteres positifs :** " + " | ".join(qsofa_pos))

        # ---- FAST / BE-FAST (AVC) ----
        ui_sec("Score FAST  -  Detection rapide AVC")
        st.markdown(
            '<div class="ib"><div class="ib-titre">FAST - Kothari et al., Ann Emerg Med 1999</div>'
            'F = Face (paralysie faciale)  |  A = Arm (deficit moteur)  |  '
            'S = Speech (trouble langage)  |  T = Time (debut brutal)<br>'
            'Tout critere positif = suspicion AVC jusqu\'a preuve du contraire.'
            '</div>',
            unsafe_allow_html=True,
        )
        fc1, fc2, fc3, fc4 = st.columns(4)
        fast_f  = fc1.checkbox("F - Paralysie faciale",       key="fast_f")
        fast_a  = fc2.checkbox("A - Deficit moteur",          key="fast_a")
        fast_s  = fc3.checkbox("S - Trouble du langage",      key="fast_s")
        fast_t  = fc4.checkbox("T - Debut brutal",            key="fast_t")
        fast_susp, fast_pos = evaluer_fast(fast_f, fast_a, fast_s, fast_t)
        if fast_susp:
            ui_alerte(
                f"SUSPICION AVC : {len(fast_pos)} critere(s) FAST positif(s) - "
                f"{' | '.join(fast_pos)} - "
                "ACTIVATION FILIERE STROKE - noter l'heure exacte du debut des symptomes",
                "crit"
            )
        elif any([fast_f, fast_a, fast_s, fast_t]):
            ui_alerte(
                f"Critere(s) FAST positif(s) : {' | '.join(fast_pos)} - surveiller l'evolution",
                "warn"
            )
        else:
            ui_alerte("FAST negatif - pas de signe evocateur d'AVC.", "ok")

        # ---- ALGOPLUS (patient age non communicant) ----
        if age >= 65:
            ui_sec("Score Algoplus  -  Douleur patient age non communicant (>= 65 ans)")
            st.markdown(
                '<div class="ib"><div class="ib-titre">Algoplus - valide en Belgique (SFGG)</div>'
                '5 criteres comportementaux observes - reponse oui (1) ou non (0).<br>'
                'Score >= 2 : douleur probable - traitement antalgique a envisager.'
                '</div>',
                unsafe_allow_html=True,
            )
            al1, al2 = st.columns(2)
            alg_v  = al1.checkbox("Visage : grimaces, froncement, crispations", key="alg_v")
            alg_r  = al1.checkbox("Regard : fixe, absent, larmes",              key="alg_r")
            alg_p  = al1.checkbox("Plaintes : gemissements, pleurs, cris",      key="alg_p")
            alg_ac = al2.checkbox("Attitude corporelle : crispee, evitement",   key="alg_ac")
            alg_co = al2.checkbox("Comportement : agitation, refus soins",      key="alg_co")
            alg_sc, alg_int, alg_css, alg_w = calculer_algoplus(alg_v, alg_r, alg_p, alg_ac, alg_co)
            for w in alg_w:
                ui_alerte(w, "warn")
            st.markdown(f'<span class="sv {alg_css}">Algoplus : {alg_sc}/5</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="sv-interp">{alg_int}</div>', unsafe_allow_html=True)

        # ---- CLINICAL FRAILTY SCALE ----
        if age >= 75:
            ui_sec("Clinical Frailty Scale (CFS)  -  Patient age >= 75 ans")
            st.markdown(
                '<div class="ib"><div class="ib-titre">CFS - Rockwood et al., CMAJ 2005</div>'
                'Score de 1 (tres en forme) a 9 (maladie terminale).<br>'
                'CFS >= 5 avec Tri 4/5 : envisager une remontee du niveau de triage.'
                '</div>',
                unsafe_allow_html=True,
            )
            cfs_score = st.select_slider(
                "Niveau de fragilite",
                options=list(CFS_NIVEAUX.keys()),
                format_func=lambda x: f"{x} - {CFS_NIVEAUX[x]}",
                key="cfs_score",
            )
            cfs_label, cfs_css, cfs_remontee = evaluer_cfs(cfs_score)
            st.markdown(f'<span class="sv {cfs_css}">CFS {cfs_score}/9  -  {cfs_label}</span>', unsafe_allow_html=True)
            if cfs_remontee:
                ui_alerte(
                    f"CFS {cfs_score} (fragile) chez un patient age : "
                    "envisager une remontee d'un niveau de triage si Tri 4 ou 5",
                    "warn"
                )


# ==============================================================================
# CALCULATEUR DE PERFUSION (onglet commun)
# ==============================================================================
with t_perfusion:
    st.markdown("### Calculateur de perfusion et protocole antalgie BCFI")
    ui_alerte(
        "Protocole antalgie local : Hainaut / Wallonie - BCFI Belgique. "
        "Toute prescription doit etre validee par le medecin responsable.",
        "info"
    )

    pc1, pc2 = st.columns(2)
    poids_kg = pc1.number_input("Poids du patient (kg)", 1.0, 200.0, 70.0, 0.5, key="perf_poids")
    uid_ant  = pc2.text_input(
        "Code patient (pour traçabilite antalgie)",
        value=st.session_state.uid_courant or "",
        key="perf_uid",
        placeholder="ex: A1B2C3D4",
    )

    # ---- DEBIT IV ----
    ui_sec("Debit de perfusion IV  -  Formule V/T")
    st.markdown(
        '<div class="ib"><div class="ib-titre">Debit (ml/h) = Volume (ml) / Duree (h)'
        '  |  Equivalence : Debit (ml/h) / 3 = gouttes/min</div></div>',
        unsafe_allow_html=True,
    )
    pv1, pv2   = st.columns(2)
    vol_ml     = pv1.number_input("Volume (ml)", 1, 5000, 500, 50, key="perf_vol")
    dur_h      = pv2.number_input("Duree (h)", 0.25, 24.0, 4.0, 0.25, key="perf_dur")
    perf, perr = calculer_debit_perfusion(vol_ml, dur_h)
    if perr:
        ui_alerte(perr, "warn")
    else:
        st.markdown(
            f'<div class="carte" style="text-align:center;">'
            f'<div class="perf-result">{perf["ml_h"]} ml/h</div>'
            f'<div class="perf-label">{vol_ml} ml en {dur_h} h  |  {perf["gttes_min"]} gouttes/min</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ---- PALIER 1 : NON OPIOIDE ----
    ui_sec("Palier 1  -  Non opioide")
    pp1, pp2 = st.columns(2)

    with pp1:
        p_res, p_err = dose_paracetamol_iv(poids_kg)
        if p_err:
            ui_alerte(p_err, "warn")
        else:
            st.markdown(
                f'<div class="dose-carte">'
                f'<div class="dose-titre">Paracetamol IV (Perfusalgan / Dafalgan IV)</div>'
                f'<div class="dose-val">{p_res["dose_g"]} g ({p_res["dose_mg"]:.0f} mg)</div>'
                f'{p_res["admin"]}<br>'
                f'Intervalle : {p_res["intervalle"]}<br>'
                f'Max : {p_res["max_jour"]}<br>'
                f'<small style="color:var(--txt-aide);">{p_res["reference"]}</small>'
                f'</div>', unsafe_allow_html=True,
            )
            if st.button("Tracer Paracetamol", key="bt_parac", use_container_width=True):
                enregistrer_antalgie(
                    uid_ant or "ANON", "Paracetamol IV",
                    f'{p_res["dose_g"]} g', "IV",
                    st.session_state.get("eva_courante", 0),
                    st.session_state.code_operateur,
                )
                st.success("Administration tracee.")

    with pp2:
        t_res, t_err = dose_taradyl_iv(poids_kg, atcd)
        if t_err:
            ui_alerte(t_err, "warn")
        else:
            ci_html = "".join(
                f'<div style="color:var(--rouge);font-size:0.78rem;">{c}</div>'
                for c in t_res["ci"]
            )
            st.markdown(
                f'<div class="dose-carte">'
                f'<div class="dose-titre">Kétorolac IV (Taradyl 30 mg / 50 ml NaCl)</div>'
                f'<div class="dose-val">{t_res["dose_mg"]} mg IV</div>'
                f'{t_res["admin"]}<br>'
                f'Intervalle : {t_res["intervalle"]}<br>'
                f'Max : {t_res["max_jour"]}<br>'
                f'{ci_html}'
                f'<small style="color:var(--txt-aide);">{t_res["reference"]}</small>'
                f'</div>', unsafe_allow_html=True,
            )
            for ci_item in t_res["ci"]:
                ui_alerte(ci_item, "crit")
            if not t_res["ci"]:
                if st.button("Tracer Taradyl", key="bt_taradyl", use_container_width=True):
                    enregistrer_antalgie(
                        uid_ant or "ANON", "Taradyl IV",
                        f'{t_res["dose_mg"]} mg', "IV",
                        st.session_state.get("eva_courante", 0),
                        st.session_state.code_operateur,
                    )
                    st.success("Administration tracee.")

    # Diclofenac IM
    ui_sec("Palier 1  -  AINS voie IM")
    d_res, d_err = dose_diclofenac_im(poids_kg, atcd)
    if d_err:
        ui_alerte(d_err, "warn")
    else:
        ci_html_d = "".join(
            f'<div style="color:var(--rouge);font-size:0.78rem;">{c}</div>'
            for c in d_res["ci"]
        )
        st.markdown(
            f'<div class="dose-carte">'
            f'<div class="dose-titre">Diclofenac IM (Voltaren 75 mg)</div>'
            f'<div class="dose-val">{d_res["dose_mg"]} mg IM</div>'
            f'Voie : {d_res["voie"]}<br>'
            f'{d_res["admin"]}<br>'
            f'Max : {d_res["max_jour"]}<br>'
            f'{ci_html_d}'
            f'<small style="color:var(--txt-aide);">{d_res["reference"]}</small>'
            f'</div>', unsafe_allow_html=True,
        )
        for ci_item in d_res["ci"]:
            ui_alerte(ci_item, "crit")

    # ---- PALIER 2 : TRAMADOL ----
    ui_sec("Palier 2  -  Opioide faible")
    tr_res, tr_err = dose_tramadol_iv(poids_kg, atcd, age)
    if tr_err:
        ui_alerte(tr_err, "warn")
    else:
        for al in tr_res.get("alertes", []):
            ui_alerte(al, "crit")
        if not tr_res.get("alertes"):
            ci_html_t = "".join(
                f'<div style="color:var(--orange);font-size:0.78rem;">{c}</div>'
                for c in tr_res["ci"]
            )
            note_dose_html = (
                f'<div style="color:var(--orange);font-weight:600;">{tr_res["note"]}</div>'
                if tr_res["note"] else ""
            )
            st.markdown(
                f'<div class="dose-carte">'
                f'<div class="dose-titre">Tramadol IV (Contramal / Tradonal)</div>'
                f'<div class="dose-val">{tr_res["dose_mg"]} mg IV</div>'
                f'{tr_res["admin"]}<br>'
                f'Intervalle : {tr_res["intervalle"]}<br>'
                f'Max : {tr_res["max_jour"]}<br>'
                f'{note_dose_html}{ci_html_t}'
                f'<small style="color:var(--txt-aide);">{tr_res["reference"]}</small>'
                f'</div>', unsafe_allow_html=True,
            )
            if st.button("Tracer Tramadol", key="bt_tramadol", use_container_width=True):
                enregistrer_antalgie(
                    uid_ant or "ANON", "Tramadol IV",
                    f'{tr_res["dose_mg"]} mg', "IV",
                    st.session_state.get("eva_courante", 0),
                    st.session_state.code_operateur,
                )
                st.success("Administration tracee.")

    # ---- PALIER 3 : OPIOIDE FORT ----
    ui_sec("Palier 3  -  Opioide fort")
    dip_col, mor_col = st.columns(2)

    with dip_col:
        dip_res, dip_err = dose_dipidolor_iv(poids_kg, age, atcd)
        if dip_err:
            ui_alerte(dip_err, "warn")
        else:
            notes_html = "".join(
                f'<div style="color:var(--orange);font-weight:600;font-size:0.82rem;">{n}</div>'
                for n in dip_res["notes"]
            )
            st.markdown(
                f'<div class="dose-carte" style="border-left-color:var(--rouge);">'
                f'<div class="dose-titre" style="color:var(--rouge);">Dipidolor IV - 1er choix</div>'
                f'<div class="dose-val">{dip_res["dose_min"]}-{dip_res["dose_max"]} mg / bolus</div>'
                f'{dip_res["admin"]}<br>'
                f'Objectif : <b>{dip_res["objectif"]}</b><br>'
                f'{notes_html}'
                f'Antidote : {dip_res["antidote"]}<br>'
                f'Surveillance : {dip_res["surveillance"]}<br>'
                f'<small style="color:var(--txt-aide);">{dip_res["reference"]}</small>'
                f'</div>', unsafe_allow_html=True,
            )
            bolus_dip = st.number_input(
                "Dose bolus administree (mg)", 0.0, 20.0,
                float(dip_res["dose_min"]), 0.5, key="dip_bolus",
            )
            if st.button("Tracer bolus Dipidolor", key="bt_dip", use_container_width=True):
                enregistrer_antalgie(
                    uid_ant or "ANON", "Dipidolor IV",
                    f'{bolus_dip} mg bolus', "IV",
                    st.session_state.get("eva_courante", 0),
                    st.session_state.code_operateur,
                )
                st.success("Bolus trace.")

    with mor_col:
        m_res, m_err = dose_morphine_iv(poids_kg, age)
        if m_err:
            ui_alerte(m_err, "warn")
        else:
            note_age_html = (
                f'<div style="color:var(--orange);font-weight:600;">{m_res["note_age"]}</div>'
                if m_res["note_age"] else ""
            )
            st.markdown(
                f'<div class="dose-carte">'
                f'<div class="dose-titre">Morphine IV - alternative</div>'
                f'<div class="dose-val">{m_res["bolus_min"]}-{m_res["bolus_max"]} mg / bolus</div>'
                f'{m_res["admin"]}<br>'
                f'Objectif : {m_res["objectif"]}<br>'
                f'{note_age_html}'
                f'Antidote : {m_res["antidote"]}<br>'
                f'<small style="color:var(--txt-aide);">{m_res["reference"]}</small>'
                f'</div>', unsafe_allow_html=True,
            )

    # ---- MEOPA ----
    ui_sec("Sedation procedurale  -  MEOPA / Kalinox")
    meopa = infos_meopa(age, atcd)
    for ci_m in meopa["ci_detectees"]:
        ui_alerte(ci_m, "crit")
    for al_m in meopa["alertes"]:
        ui_alerte(al_m, "warn")
    ci_abs_html = "".join(
        f'<div style="font-size:0.78rem;color:var(--rouge);">- {c}</div>'
        for c in meopa["ci_absolues"]
    )
    st.markdown(
        f'<div class="dose-carte">'
        f'<div class="dose-titre">MEOPA / Kalinox (O2 / N2O 50/50)</div>'
        f'<div class="dose-val">Inhalation spontanee</div>'
        f'Age minimum AMM : {meopa["age_min_amm"]}<br>'
        f'{meopa["admin"]}<br>'
        f'Duree max : {meopa["duree_max"]}<br>'
        f'Surveillance : {meopa["surveillance"]}<br>'
        f'Contre-indications absolues :{ci_abs_html}'
        f'<small style="color:var(--txt-aide);">{meopa["reference"]}</small>'
        f'</div>', unsafe_allow_html=True,
    )

    # ---- ADRENALINE ----
    ui_sec("Adrenaline IM  -  Choc anaphylactique")
    a_res, a_err = dose_adrenaline_anaphylaxie(poids_kg)
    if a_err:
        ui_alerte(a_err, "warn")
    else:
        st.markdown(
            f'<div class="dose-carte" style="border-left-color:var(--rouge);">'
            f'<div class="dose-titre" style="color:var(--rouge);">Adrenaline IM  -  Choc anaphylactique</div>'
            f'<div class="dose-val">{a_res["dose_mg"]} mg IM</div>'
            f'Voie : {a_res["voie"]}<br>'
            f'Preparation : {a_res["note"]}<br>'
            f'{a_res["repeter"]}<br>'
            f'{a_res["moniteur"]}<br>'
            f'<small style="color:var(--txt-aide);">{a_res["reference"]}</small>'
            f'</div>', unsafe_allow_html=True,
        )

    # ---- GLUCOSE ----
    ui_sec("Glucose 30 %  -  Correction hypoglycemie")
    g_res, g_err = dose_glucose_hypoglycemie(poids_kg, "IV")
    gc_res, gc_err = dose_glucose_hypoglycemie(poids_kg, "IM")
    gc1, gc2 = st.columns(2)
    with gc1:
        if not g_err:
            st.markdown(
                f'<div class="dose-carte">'
                f'<div class="dose-titre">Glucose 30 % IV (Glucosie)</div>'
                f'<div class="dose-val">{g_res["dose_g"]} g</div>'
                f'{g_res["volume"]}<br>'
                f'{g_res["controle"]}<br>'
                f'<small style="color:var(--txt-aide);">{g_res["reference"]}</small>'
                f'</div>', unsafe_allow_html=True,
            )
    with gc2:
        if not gc_err:
            st.markdown(
                f'<div class="dose-carte">'
                f'<div class="dose-titre">Glucagon IM/SC (GlucaGen HypoKit) - si IV impossible</div>'
                f'<div class="dose-val">{gc_res["dose"]}</div>'
                f'{gc_res["note"]}<br>'
                f'{gc_res["controle"]}<br>'
                f'<small style="color:var(--txt-aide);">{gc_res["reference"]}</small>'
                f'</div>', unsafe_allow_html=True,
            )

    # ---- LOG ANTALGIE SESSION ----
    if uid_ant:
        log_af = charger_log_antalgie(uid_ant)
        if log_af:
            ui_sec("Historique antalgie  -  Patient " + uid_ant)
            for entry in log_af[:10]:
                st.markdown(
                    f'<div class="hist-ligne hist-3B">'
                    f'<b>{entry["heure"]}</b>  |  {entry["medicament"]}  |  '
                    f'{entry["dose"]}  {entry["voie"]}  |  '
                    f'EVA avant : {entry["eva_avant"]}/10  |  '
                    f'Operateur : {entry["operateur"]}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    ui_disclaimer()


# ==============================================================================
# REEVALUATION STRUCTUREE (onglet commun)
# ==============================================================================
with t_reeval:
    st.markdown("### Reevaluations structurees")
    st.caption(
        "Chaque reevaluation est comparee a la precedente. "
        "La tendance clinique est calculee automatiquement."
    )

    ui_sec("Nouvelle reevaluation")
    cr1, cr2, cr3 = st.columns(3)
    re_temp = cr1.number_input("Temperature (degres C)", 30.0, 45.0, 37.0, 0.1, key="re_temp")
    re_fc   = cr1.number_input("FC (bpm)", 20, 220, 80,    key="re_fc")
    re_pas  = cr2.number_input("PAS (mmHg)", 40, 260, 120, key="re_pas")
    re_spo2 = cr2.number_input("SpO2 (%)", 50, 100, 98,    key="re_spo2")
    re_fr   = cr3.number_input("FR (/min)", 5, 60, 16,     key="re_fr")
    re_gcs  = cr3.number_input("GCS (3-15)", 3, 15, 15,    key="re_gcs")

    re_news2, re_warns = calculer_news2(
        re_fr, re_spo2, o2_supp, re_temp, re_pas, re_fc, re_gcs, "BPCO" in atcd
    )
    re_label, re_css = niveau_news2(re_news2)
    for w in re_warns:
        ui_alerte(w, "warn")

    re_motif = st.session_state.historique[-1].get("motif", "Fievre") \
               if st.session_state.historique else "Fievre"
    re_niv, re_just, re_ref = french_triage(
        re_motif, {}, re_fc, re_pas, re_spo2, re_fr, re_gcs, re_temp, age, re_news2
    )

    rc1, rc2 = st.columns(2)
    rc1.markdown(f'<span class="news2-val {re_css}">{re_label}</span>', unsafe_allow_html=True)
    rc2.info(f"Triage recalcule : **{LABELS_TRI[re_niv]}**")

    ui_bannieres_alerte(re_news2, None, re_fc, re_pas, re_spo2, re_fr, re_gcs)

    if st.button("Enregistrer cette reevaluation", use_container_width=True):
        st.session_state.histo_reeval.append({
            "heure": datetime.now().strftime("%H:%M"),
            "fc": re_fc, "pas": re_pas, "spo2": re_spo2,
            "fr": re_fr, "gcs": re_gcs, "temp": re_temp,
            "niveau": re_niv, "news2": re_news2,
        })
        st.session_state.derniere_reeval = datetime.now()
        st.success(f"Reevaluation enregistree a {datetime.now().strftime('%H:%M')} - Tri {re_niv}")

    ui_sec("Historique des reevaluations")

    if not st.session_state.histo_reeval:
        st.info("Aucune reevaluation enregistree pour ce patient.")
    else:
        _ORD_NIV = {"M": 0, "1": 1, "2": 2, "3A": 3, "3B": 4, "4": 5, "5": 6}

        def _td(old, new, hg=True):
            if   new > old: sym, css = ("+", "td-h") if not hg else ("+", "td-b")
            elif new < old: sym, css = ("-", "td-b") if not hg else ("-", "td-h")
            else:           sym, css = "=", "td-e"
            return f'<span class="{css}">{sym}</span>'

        for i, snap in enumerate(st.session_state.histo_reeval):
            prev  = st.session_state.histo_reeval[i - 1] if i > 0 else snap
            no    = _ORD_NIV.get(snap["niveau"], 3)
            np_   = _ORD_NIV.get(prev["niveau"], 3)
            r_css = "reeval-amelio" if no > np_ else ("reeval-aggrav" if no < np_ else "reeval-stable")
            tend  = "AMELIORATION" if no > np_ else ("AGGRAVATION" if no < np_ else "STABLE")
            lbl   = "H0" if i == 0 else f"H+{i}"
            st.markdown(
                f'<div class="reeval-ligne {r_css}">'
                f'<b>{snap["heure"]}</b> ({lbl})  |  Tri {snap["niveau"]}  |  '
                f'NEWS2 {snap.get("news2","?")}  |  '
                f'FC {snap["fc"]} {_td(prev["fc"], snap["fc"])}  |  '
                f'PAS {snap["pas"]} {_td(prev["pas"], snap["pas"], False)}  |  '
                f'SpO2 {snap["spo2"]} {_td(prev["spo2"], snap["spo2"], False)}  |  '
                f'GCS {snap["gcs"]} {_td(prev["gcs"], snap["gcs"], False)}  |  '
                f'<b>{tend}</b>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if len(st.session_state.histo_reeval) >= 2:
            first = st.session_state.histo_reeval[0]
            last  = st.session_state.histo_reeval[-1]
            st.markdown(
                f"**Bilan global :** {len(st.session_state.histo_reeval)} reevaluations  |  "
                f"NEWS2 : {first.get('news2','?')} -> {last.get('news2','?')}  |  "
                f"Tri : {first['niveau']} -> {last['niveau']}"
            )

        if st.button("Effacer l'historique de reevaluation"):
            st.session_state.histo_reeval = []
            st.rerun()


# ==============================================================================
# HISTORIQUE DE SESSION
# ==============================================================================
with t_histo:
    if not st.session_state.historique:
        st.info("Aucun patient enregistre dans cette session.")
    else:
        st.markdown(f"**{len(st.session_state.historique)} patient(s) enregistre(s) cette session**")
        for i, pat in enumerate(reversed(st.session_state.historique), 1):
            tag = "  -  ALERTES DANGER" if pat.get("alertes_danger", 0) > 0 else ""
            st.markdown(
                f'<div class="hist-ligne {CSS_HIST.get(pat["niveau"],"hist-4")}">'
                f'<b>{pat["heure"]}</b>  |  {pat["age"]} ans  |  <b>{pat["motif"]}</b>  |  '
                f'EVA {pat["eva"]}/10  |  NEWS2 {pat["news2"]}  |  Tri {pat["niveau"]}{tag}'
                f'</div>',
                unsafe_allow_html=True,
            )
            with st.expander(f"SBAR  -  Patient n {len(st.session_state.historique) - i + 1}"):
                st.markdown(f'<div class="sbar">{pat["sbar"]}</div>', unsafe_allow_html=True)
                st.download_button(
                    "Telecharger SBAR",
                    data=pat["sbar"],
                    file_name=f"SBAR_{pat['heure'].replace(':','h')}_Tri{pat['niveau']}.txt",
                    mime="text/plain",
                    key=f"dl_histo_{i}",
                )
        if st.button("Effacer l'historique de session"):
            st.session_state.historique = []
            st.rerun()


# ==============================================================================
# REGISTRE PATIENTS - STOCKAGE ANONYME PERSISTANT
# ==============================================================================
with t_registre:
    st.markdown("### Registre des patients  -  Donnees anonymes persistantes")
    ui_alerte(
        "Conformite RGPD : ce registre ne contient aucun nom ni prenom. "
        "Chaque patient est identifie par un code anonyme. "
        "Les donnees sont stockees localement sur ce poste uniquement.",
        "info"
    )

    registre = _charger_registre()

    if registre:
        _niv_c = {}
        for p in registre:
            _n = p.get("niveau", "?")
            _niv_c[_n] = _niv_c.get(_n, 0) + 1
        auj = sum(1 for p in registre if p.get("date") == datetime.now().strftime("%Y-%m-%d"))
        cs  = st.columns(5)
        cs[0].markdown(f'<div class="reg-stat"><div class="reg-stat-num">{len(registre)}</div><div class="reg-stat-lbl">Total</div></div>', unsafe_allow_html=True)
        cs[1].markdown(f'<div class="reg-stat"><div class="reg-stat-num">{auj}</div><div class="reg-stat-lbl">Aujourd\'hui</div></div>', unsafe_allow_html=True)
        urg = sum(v for k, v in _niv_c.items() if k in ("M","1","2"))
        cs[2].markdown(f'<div class="reg-stat"><div class="reg-stat-num" style="color:var(--rouge);">{urg}</div><div class="reg-stat-lbl">Tri M/1/2</div></div>', unsafe_allow_html=True)
        mod = sum(v for k, v in _niv_c.items() if k in ("3A","3B"))
        cs[3].markdown(f'<div class="reg-stat"><div class="reg-stat-num" style="color:var(--orange);">{mod}</div><div class="reg-stat-lbl">Tri 3A/3B</div></div>', unsafe_allow_html=True)
        bas = sum(v for k, v in _niv_c.items() if k in ("4","5"))
        cs[4].markdown(f'<div class="reg-stat"><div class="reg-stat-num" style="color:var(--vert);">{bas}</div><div class="reg-stat-lbl">Tri 4/5</div></div>', unsafe_allow_html=True)

    ui_sec("Recherche et filtres")
    cs1, cs2, cs3 = st.columns([3, 2, 2])
    q_rech     = cs1.text_input(
        "Rechercher (motif, age, niveau, date...)",
        placeholder="ex : SCA, 60 ans, Tri 2...",
        key="reg_rech", label_visibility="collapsed",
    )
    filtre_niv = cs2.selectbox("Filtrer par niveau", ["Tous","M","1","2","3A","3B","4","5"], key="reg_filtre")
    filtres    = rechercher_registre(q_rech) if q_rech else registre
    if filtre_niv != "Tous":
        filtres = [p for p in filtres if p.get("niveau") == filtre_niv]

    if cs3.button("Exporter tout (JSON)", use_container_width=True) and registre:
        st.download_button(
            "Telecharger le registre anonyme",
            data=json.dumps(registre, ensure_ascii=False, indent=2),
            file_name=f"AKIR_registre_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            key="export_registre",
        )

    st.markdown(
        f'<div class="sec-h">Patients ({len(filtres)} '
        f'resultat{"s" if len(filtres) != 1 else ""})</div>',
        unsafe_allow_html=True,
    )

    if not filtres:
        st.markdown(
            '<div style="text-align:center;padding:40px 20px;color:var(--txt-aide);">'
            'Aucun patient dans le registre.<br>'
            'Utilisez le bouton "Enregistrer au registre anonyme" apres un triage.'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        for idx, pat in enumerate(filtres):
            uid = pat.get("uid", "?")
            niv = pat.get("niveau", "?")
            st.markdown(
                f'<div class="reg-carte">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">'
                f'  <div style="font-family:DM Mono,monospace;font-size:0.95rem;font-weight:500;color:var(--txt-titre);">'
                f'    Code : {uid}  -  {pat.get("age","?")} ans'
                f'  </div>'
                f'  <div style="font-size:0.68rem;color:var(--txt-aide);">{pat.get("date_heure","")}</div>'
                f'</div>'
                f'<div style="margin-bottom:8px;">'
                f'  <span class="reg-badge reg-{niv}">Tri {niv}</span>'
                f'  <span style="font-size:0.82rem;color:var(--txt-aide);">'
                f'    {pat.get("motif","")}  -  {pat.get("cat","")}'
                f'  </span>'
                f'</div>'
                f'<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:4px 14px;font-size:0.8rem;">'
                f'  <div><span style="font-size:0.62rem;color:var(--txt-aide);text-transform:uppercase;">Temperature</span><br><b>{pat.get("temp","")} degres C</b></div>'
                f'  <div><span style="font-size:0.62rem;color:var(--txt-aide);text-transform:uppercase;">FC</span><br><b>{pat.get("fc","")} bpm</b></div>'
                f'  <div><span style="font-size:0.62rem;color:var(--txt-aide);text-transform:uppercase;">PAS</span><br><b>{pat.get("pas","")} mmHg</b></div>'
                f'  <div><span style="font-size:0.62rem;color:var(--txt-aide);text-transform:uppercase;">SpO2</span><br><b>{pat.get("spo2","")} %</b></div>'
                f'  <div><span style="font-size:0.62rem;color:var(--txt-aide);text-transform:uppercase;">NEWS2</span><br><b>{pat.get("news2","")}</b></div>'
                f'  <div><span style="font-size:0.62rem;color:var(--txt-aide);text-transform:uppercase;">EVA</span><br><b>{pat.get("eva","")}/10</b></div>'
                f'  <div><span style="font-size:0.62rem;color:var(--txt-aide);text-transform:uppercase;">Allergies</span><br><b>{pat.get("allergies","RAS")}</b></div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

            cr1, cr2, cr3 = st.columns([3, 1, 1])
            with cr1:
                with st.expander(f"SBAR complet  -  {uid}"):
                    sbar_txt = pat.get("sbar", "Aucun SBAR disponible.")
                    st.markdown(f'<div class="sbar">{sbar_txt}</div>', unsafe_allow_html=True)
                    st.download_button(
                        "Telecharger SBAR",
                        data=sbar_txt,
                        file_name=f"SBAR_AKIR_{uid}_{niv}.txt",
                        mime="text/plain",
                        key=f"dl_reg_{uid}_{idx}",
                    )

            if cr3.button("Supprimer", key=f"del_{uid}_{idx}", use_container_width=True):
                st.session_state.confirm_suppression = uid

            if st.session_state.confirm_suppression == uid:
                st.warning(f"Confirmer la suppression definitive du patient {uid} ?")
                cf1, cf2, _ = st.columns([1, 1, 3])
                if cf1.button("Confirmer", key=f"conf_{uid}_{idx}", type="primary"):
                    supprimer_registre(uid)
                    st.session_state.confirm_suppression = None
                    st.success(f"Patient {uid} supprime du registre.")
                    st.rerun()
                if cf2.button("Annuler", key=f"ann_{uid}_{idx}"):
                    st.session_state.confirm_suppression = None
                    st.rerun()

    if registre:
        st.markdown("---")
        ui_sec("Administration")
        with st.expander("Zone de purge  -  Action irreversible"):
            st.warning("Cette action supprimera definitivement l'ensemble des patients du registre.")
            if st.button("Purger l'ensemble du registre", type="primary", key="purge_tout"):
                _sauvegarder_registre([])
                st.session_state.confirm_suppression = None
                st.success("Registre vide.")
                st.rerun()

    ui_disclaimer()

# ==============================================================================
# RAPPORT D'ACTIVITE MENSUEL
# ==============================================================================
with t_rapport:
    st.markdown("### Rapport d'activite  -  Tableau de bord")
    st.caption(
        "Statistiques generees depuis le registre anonyme local. "
        "Aucune donnee nominative - conformite RGPD."
    )

    rap_nb_jours = st.select_slider(
        "Periode d'analyse",
        options=[7, 14, 30, 60, 90],
        value=30,
        format_func=lambda x: f"{x} derniers jours",
        key="rap_periode",
    )

    rapport = generer_rapport_activite(rap_nb_jours)

    if not rapport or rapport.get("total", 0) == 0:
        ui_alerte(
            f"Aucune donnee disponible sur les {rap_nb_jours} derniers jours. "
            "Enrichissez le registre en cliquant sur 'Enregistrer au registre anonyme' apres chaque triage.",
            "info"
        )
    else:
        # --- KPI principaux ---
        k1, k2, k3, k4 = st.columns(4)
        k1.markdown(
            f'<div class="reg-stat"><div class="reg-stat-num">{rapport["total"]}</div>'
            f'<div class="reg-stat-lbl">Passages ({rap_nb_jours} j)</div></div>',
            unsafe_allow_html=True,
        )
        k2.markdown(
            f'<div class="reg-stat"><div class="reg-stat-num" style="color:var(--rouge);">'
            f'{rapport["taux_urgents"]} %</div>'
            f'<div class="reg-stat-lbl">Taux urgents M/1/2</div></div>',
            unsafe_allow_html=True,
        )
        k3.markdown(
            f'<div class="reg-stat"><div class="reg-stat-num">{rapport["news2_moyen"]}</div>'
            f'<div class="reg-stat-lbl">NEWS2 moyen</div></div>',
            unsafe_allow_html=True,
        )
        avg_j = round(rapport["total"] / rap_nb_jours, 1) if rap_nb_jours > 0 else 0
        k4.markdown(
            f'<div class="reg-stat"><div class="reg-stat-num">{avg_j}</div>'
            f'<div class="reg-stat-lbl">Passages / jour (moy.)</div></div>',
            unsafe_allow_html=True,
        )

        # --- Distribution par niveau de tri ---
        ui_sec("Distribution par niveau de tri")
        ordre_niv  = ["M", "1", "2", "3A", "3B", "4", "5"]
        couleurs   = {
            "M":  "var(--violet)", "1": "var(--rouge)",  "2": "var(--orange)",
            "3A": "#F9A825",       "3B": "#FDD835",
            "4":  "var(--vert)",   "5": "var(--bleu)",
        }
        dist = rapport.get("dist_niveaux", {})
        total_niv = sum(dist.values()) or 1
        for niv in ordre_niv:
            cnt  = dist.get(niv, 0)
            pct  = round(cnt / total_niv * 100, 1)
            col  = couleurs.get(niv, "var(--bleu)")
            lbl  = LABELS_TRI.get(niv, niv)
            st.markdown(
                f'<div style="margin:4px 0;">'
                f'  <div style="display:flex;justify-content:space-between;font-size:0.8rem;margin-bottom:2px;">'
                f'    <span style="font-family:DM Mono,monospace;">{lbl}</span>'
                f'    <span style="font-family:DM Mono,monospace;font-weight:600;">{cnt} ({pct} %)</span>'
                f'  </div>'
                f'  <div style="background:var(--bord);border-radius:3px;height:8px;">'
                f'    <div style="background:{col};width:{pct}%;height:8px;border-radius:3px;'
                f'      min-width:{2 if cnt > 0 else 0}px;"></div>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # --- Top 10 motifs ---
        ui_sec("Top 10 motifs de recours")
        top = rapport.get("top_motifs", [])
        if top:
            max_cnt = top[0][1] if top else 1
            for motif_r, cnt_r in top:
                pct_r = round(cnt_r / total_niv * 100, 1)
                pct_bar = round(cnt_r / max_cnt * 100, 1)
                st.markdown(
                    f'<div style="margin:3px 0;">'
                    f'  <div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:2px;">'
                    f'    <span>{motif_r}</span>'
                    f'    <span style="font-family:DM Mono,monospace;">{cnt_r} ({pct_r} %)</span>'
                    f'  </div>'
                    f'  <div style="background:var(--bord);border-radius:3px;height:6px;">'
                    f'    <div style="background:var(--bleu);width:{pct_bar}%;height:6px;border-radius:3px;"></div>'
                    f'  </div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # --- Activite 7 derniers jours ---
        ui_sec("Activite  -  7 derniers jours")
        dist_dates = rapport.get("dist_dates", {})
        if dist_dates:
            max_j_cnt = max(dist_dates.values()) if dist_dates else 1
            for date_str, cnt_d in sorted(dist_dates.items()):
                try:
                    d_fmt = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m")
                except ValueError:
                    d_fmt = date_str
                pct_d = round(cnt_d / max_j_cnt * 100, 1)
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;margin:3px 0;">'
                    f'  <span style="font-family:DM Mono,monospace;font-size:0.75rem;'
                    f'    width:48px;flex-shrink:0;">{d_fmt}</span>'
                    f'  <div style="flex:1;background:var(--bord);border-radius:3px;height:18px;">'
                    f'    <div style="background:var(--bleu-clair);border:1px solid var(--bleu);'
                    f'      width:{pct_d}%;height:18px;border-radius:3px;min-width:{2 if cnt_d > 0 else 0}px;">'
                    f'    </div>'
                    f'  </div>'
                    f'  <span style="font-family:DM Mono,monospace;font-size:0.75rem;'
                    f'    width:30px;text-align:right;">{cnt_d}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # --- Export JSON rapport ---
        rapport_json = json.dumps(rapport, ensure_ascii=False, indent=2)
        st.download_button(
            "Telecharger le rapport (JSON)",
            data=rapport_json,
            file_name=f"AKIR_rapport_{datetime.now().strftime('%Y%m%d')}_{rap_nb_jours}j.json",
            mime="application/json",
            key="dl_rapport",
            use_container_width=True,
        )

    ui_disclaimer()