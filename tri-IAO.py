"""
================================================================================
  AKIR-IAO v18 — Application Streamlit complète (fichier unique)
  Développeur exclusif : Ismail Ibn-Daifa
  Référence clinique   : FRENCH Triage SFMU V1.1 — Juin 2018
  Pharmacologie        : BCFI — Répertoire Commenté des Médicaments — Belgique
  Localisation         : Hainaut, Wallonie, Belgique
  RGPD                 : Aucun nom ni prénom collecté — UUID anonyme uniquement

Modules intégrés dans ce fichier unique :
  [1] core_logic     — Constantes, scores cliniques, moteur triage FRENCH V1.1
  [2] pharma_engine  — Protocoles BCFI (antalgiques, antidotes, urgences)
  [3] ui_components  — Composants UI hospitaliers (#004A99, iPhone WebApp)
  [4] main           — Point d'entrée Streamlit (9 onglets, SBAR, RGPD UUID)
================================================================================
"""

# Imports
from __future__ import annotations
from typing import Optional
from datetime import datetime
import streamlit as st
import uuid
import json
import os


# ==============================================================================
# [1] CONSTANTES ET MOTEUR CLINIQUE
# ==============================================================================



# ==============================================================================
# CONSTANTES CLINIQUES
# ==============================================================================

LABELS_TRI: dict[str, str] = {
    "M":  "TRI M  —  IMMÉDIAT",
    "1":  "TRI 1  —  URGENCE EXTRÊME",
    "2":  "TRI 2  —  TRÈS URGENT",
    "3A": "TRI 3A —  URGENT",
    "3B": "TRI 3B —  URGENT DIFFÉRÉ",
    "4":  "TRI 4  —  MOINS URGENT",
    "5":  "TRI 5  —  NON URGENT",
}

SECTEURS_TRI: dict[str, str] = {
    "M":  "Déchocage — Prise en charge immédiate",
    "1":  "Déchocage — Prise en charge immédiate",
    "2":  "Salle de soins aigus — Médecin disponible en moins de 20 min",
    "3A": "Salle de soins aigus — Médecin disponible en moins de 30 min",
    "3B": "Polyclinique urgences — Médecin disponible en moins de 1 h",
    "4":  "Consultation urgences — Médecin disponible en moins de 2 h",
    "5":  "Salle d'attente — Réorientation médecin généraliste possible",
}

DELAIS_TRI: dict[str, int] = {
    "M": 5, "1": 5, "2": 15, "3A": 30, "3B": 60, "4": 120, "5": 999
}

# Seuils glycémiques — standard belge (mg/dl)
# Facteur de conversion : 1 mmol/l = 18 mg/dl
GLYCEMIE: dict[str, int] = {
    "hypoglycemie_severe":   54,   # < 3,0 mmol/l
    "hypoglycemie_moderee":  70,   # < 3,9 mmol/l
    "hyperglycemie_seuil":  180,   # > 10,0 mmol/l
    "hyperglycemie_severe":  360,  # > 20,0 mmol/l
}

# Seuils vitaux pédiatriques — PDF SFMU V1.1 p.5 + PALS
# Structure : (FC_min, FC_max, PAS_min)
SEUILS_PEDIATRIQUES: dict[str, tuple[int, int, int]] = {
    "0_1m":  (100, 180, 60),
    "1_6m":  (100, 160, 70),
    "6_24m": (80,  150, 75),
    "1_10a": (70,  140, 70),
}

LISTE_ATCD: list[str] = [
    "HTA",
    "Diabète de type 1",
    "Diabète de type 2",
    "Tabagisme actif",
    "Dyslipidémie",
    "ATCD familial coronarien",
    "Insuffisance cardiaque chronique",
    "BPCO",
    "Anticoagulants / AOD",
    "Grossesse en cours",
    "Immunodépression",
    "Néoplasie évolutive",
    "Épilepsie",
    "Insuffisance rénale chronique",
    "Ulcère gastro-duodénal",
    "Insuffisance hépatique",
    "Déficit en vitamine B12",
    "Drépanocytose / hémoglobinopathie",
    "Chimiothérapie en cours",
    "IMAO (inhibiteurs MAO)",
    "Antidépresseurs sérotoninergiques (ISRS / IRSNA)",
]

CFS_NIVEAUX: dict[int, str] = {
    1: "Très en forme — actif, énergique, motivé",
    2: "En forme — sans maladie active",
    3: "Bien portant — maladie bien contrôlée",
    4: "Vulnérabilité — ralenti, fatigable",
    5: "Fragilité légère — dépendant pour AIVQ",
    6: "Fragilité modérée — aide nécessaire pour sorties",
    7: "Fragilité sévère — totalement dépendant pour soins",
    8: "Fragilité très sévère — fin de vie proche",
    9: "Maladie terminale — espérance de vie < 6 mois",
}

# Ordonnancement ordinal pour le kappa pondéré
ORD_NIV: dict[str, int] = {"M": 0, "1": 1, "2": 2, "3A": 3, "3B": 4, "4": 5, "5": 6}


# ==============================================================================
# SCORES CLINIQUES
# ==============================================================================

def calculer_news2(
    fr: float,
    spo2: float,
    o2_supp: bool,
    temp: float,
    pas: float,
    fc: float,
    gcs: int,
    bpco: bool = False,
) -> tuple[int, list[str]]:
    """
    National Early Warning Score 2 — version belge SFMU 2018.

    Deux échelles SpO2 :
      - Échelle 1 (standard)  : cible >= 95 %
      - Échelle 2 (BPCO)      : cible 88-92 % — déclenche si patient BPCO connu

    Référence : Royal College of Physicians, NEWS2, 2017.
    Retourne : (score: int, avertissements: list[str])
    """
    warns: list[str] = []
    score = 0

    # Fréquence respiratoire
    if   fr <= 8:              score += 3; warns.append(f"FR {fr} /min ≤ 8 — détresse respiratoire")
    elif fr <= 11:             score += 1
    elif fr <= 20:             score += 0
    elif fr <= 24:             score += 2
    else:                      score += 3; warns.append(f"FR {fr} /min ≥ 25 — tachypnée sévère")

    # SpO2 — échelle adaptée BPCO
    if bpco:
        # Échelle 2 : cible 88-92 %
        if   spo2 <= 83:       score += 3; warns.append(f"SpO2 {spo2} % — hypoxémie critique (BPCO)")
        elif spo2 <= 85:       score += 2
        elif spo2 <= 87:       score += 1
        elif spo2 <= 92:       score += 0   # zone cible BPCO
        elif spo2 <= 94:       score += 0
        elif spo2 <= 96:       score += 1   # hyperoxie relative déconseillée en BPCO
        else:                  score += 2; warns.append(f"SpO2 {spo2} % — hyperoxie en contexte BPCO")
    else:
        # Échelle 1 standard
        if   spo2 <= 91:       score += 3; warns.append(f"SpO2 {spo2} % ≤ 91 % — hypoxémie sévère")
        elif spo2 <= 93:       score += 2
        elif spo2 <= 95:       score += 1
        else:                  score += 0

    # Oxygène supplémentaire
    if o2_supp:
        score += 2
        warns.append("O2 supplémentaire en cours — +2 pts NEWS2")

    # Température
    if   temp <= 35.0:         score += 3; warns.append(f"T° {temp} °C — hypothermie")
    elif temp <= 36.0:         score += 1
    elif temp <= 38.0:         score += 0
    elif temp <= 39.0:         score += 1
    else:                      score += 2; warns.append(f"T° {temp} °C — hyperthermie")

    # Pression artérielle systolique
    if   pas <= 90:            score += 3; warns.append(f"PAS {pas} mmHg — état de choc")
    elif pas <= 100:           score += 2
    elif pas <= 110:           score += 1
    elif pas <= 219:           score += 0
    else:                      score += 3; warns.append(f"PAS {pas} mmHg — HTA hypertensive")

    # Fréquence cardiaque
    if   fc <= 40:             score += 3; warns.append(f"FC {fc} bpm — bradycardie sévère")
    elif fc <= 50:             score += 1
    elif fc <= 90:             score += 0
    elif fc <= 110:            score += 1
    elif fc <= 130:            score += 2
    else:                      score += 3; warns.append(f"FC {fc} bpm — tachycardie sévère")

    # Glasgow Coma Scale
    if   gcs == 15:            score += 0
    elif gcs >= 13:            score += 3; warns.append(f"GCS {gcs}/15 — altération de conscience")
    else:                      score += 3; warns.append(f"GCS {gcs}/15 — altération majeure de conscience")

    return score, warns


def niveau_news2(score: int) -> tuple[str, str]:
    """
    Interprétation du score NEWS2 avec code CSS associé.
    Retourne : (label: str, css_class: str)
    """
    if   score == 0:           return "NEWS2 : 0 — Risque faible",           "news2-nul"
    elif score <= 4:           return f"NEWS2 : {score} — Risque faible",    "news2-bas"
    elif score <= 6:           return f"NEWS2 : {score} — Risque modéré",    "news2-moy"
    elif score <= 8:           return f"NEWS2 : {score} — Risque élevé",     "news2-haut"
    else:                      return f"NEWS2 : {score} — RISQUE CRITIQUE",  "news2-crit"


def calculer_gcs(y: int, v: int, m: int) -> tuple[int, list[str]]:
    """
    Glasgow Coma Scale — Teasdale & Jennett, Lancet 1974.
    Y (ouverture yeux) : 1-4 | V (réponse verbale) : 1-5 | M (réponse motrice) : 1-6.
    Retourne : (score: int, avertissements: list[str])
    """
    try:
        return max(3, min(15, int(y) + int(v) + int(m))), []
    except (TypeError, ValueError) as exc:
        return 15, [f"Erreur calcul GCS : {exc}"]


def calculer_qsofa(fr: float, gcs: int, pas: float) -> tuple[int, list[str], list[str]]:
    """
    Score qSOFA — détection rapide du sepsis à l'IAO.
    3 critères, 1 point chacun. Score ≥ 2 : sepsis probable.
    Référence : Singer et al., JAMA 2016.
    Retourne : (score: int, criteres_positifs: list[str], avertissements: list[str])
    """
    try:
        positifs: list[str] = []
        warns: list[str] = []
        s = 0
        if fr is None:
            warns.append("qSOFA incomplet : FR manquante")
        elif fr >= 22:
            s += 1
            positifs.append(f"FR ≥ 22 /min (valeur : {fr} /min)")
        if gcs is None:
            warns.append("qSOFA incomplet : GCS manquant")
        elif gcs < 15:
            s += 1
            positifs.append(f"Altération de conscience — GCS {gcs}/15")
        if pas is None:
            warns.append("qSOFA incomplet : PAS manquante")
        elif pas <= 100:
            s += 1
            positifs.append(f"PAS ≤ 100 mmHg (valeur : {pas} mmHg)")
        return s, positifs, warns
    except (TypeError, ValueError) as exc:
        return 0, [], [f"Erreur calcul qSOFA : {exc}"]


def calculer_timi(
    age: float,
    nb_frcv: int,
    stenose_50: bool,
    aspirine_7j: bool,
    troponine_pos: bool,
    deviation_st: bool,
    crises_24h: int,
) -> tuple[int, list[str]]:
    """
    Score TIMI — risque d'événements cardiovasculaires à 14 jours (NSTEMI/AOMI).
    Score 0-2 : faible | 3-4 : intermédiaire | 5-7 : élevé.
    Référence : Antman et al., JAMA 2000.
    Retourne : (score: int, avertissements: list[str])
    """
    try:
        s = (
            int(age >= 65)
            + int(nb_frcv >= 3)
            + int(bool(stenose_50))
            + int(bool(aspirine_7j))
            + int(bool(troponine_pos))
            + int(bool(deviation_st))
            + int(crises_24h >= 2)
        )
        return s, []
    except (TypeError, ValueError) as exc:
        return 0, [f"Erreur calcul TIMI : {exc}"]


def evaluer_fast(
    paralysie_faciale: bool,
    deficit_moteur: bool,
    trouble_langage: bool,
    debut_brutal: bool,
) -> tuple[int, str, bool]:
    """
    Score FAST / BE-FAST — détection rapide AVC.
    F=Face | A=Arm | S=Speech | T=Time.
    Retourne : (score: int, interpretation: str, alerte_stroke: bool)
    """
    s = (
        int(bool(paralysie_faciale))
        + int(bool(deficit_moteur))
        + int(bool(trouble_langage))
        + int(bool(debut_brutal))
    )
    if s >= 2:
        return s, f"FAST positif ({s}/4) — Suspicion AVC — Activation filière Stroke immédiate", True
    if s == 1:
        return s, f"FAST partiel ({s}/4) — Évaluation neurologique urgente", False
    return s, "FAST négatif — AVC moins probable", False


def calculer_algoplus(
    visage: bool,
    regard: bool,
    plaintes: bool,
    attitude_corpo: bool,
    comportement: bool,
) -> tuple[int, str, str, list[str]]:
    """
    Score Algoplus — douleur chez le patient âgé non communicant.
    5 items comportementaux (0/1). Score ≥ 2 : douleur probable.
    Référence : Bercovitch et al., Pain 2006 — validation SFGG.
    Retourne : (score: int, interpretation: str, css: str, avertissements: list[str])
    """
    try:
        s = (
            int(bool(visage))
            + int(bool(regard))
            + int(bool(plaintes))
            + int(bool(attitude_corpo))
            + int(bool(comportement))
        )
        if s >= 4:
            interp, css = "Douleur intense — antalgique IV urgent", "sv-haut"
        elif s >= 2:
            interp, css = "Douleur probable — antalgique à initier", "sv-moy"
        else:
            interp, css = "Douleur peu probable ou absente", "sv-bas"
        return s, interp, css, []
    except (TypeError, ValueError) as exc:
        return 0, "Erreur de calcul", "sv-bas", [f"Erreur Algoplus : {exc}"]


def evaluer_cfs(score_cfs: int) -> tuple[str, str, bool]:
    """
    Clinical Frailty Scale — évaluation de la fragilité du patient âgé.
    Score 1-9. CFS ≥ 5 : envisager remontée du niveau de triage.
    Référence : Rockwood et al., CMAJ 2005.
    Retourne : (label: str, css: str, remontee_triage: bool)
    """
    if score_cfs <= 3:   return "Robuste",       "sv-bas",  False
    if score_cfs <= 4:   return "Vulnérable",    "sv-moy",  False
    if score_cfs <= 6:   return "Fragile",        "sv-moy",  True
    if score_cfs <= 8:   return "Très fragile",  "sv-haut", True
    return "Terminal",   "sv-haut", True


def calculer_silverman(
    balt: int, tirage: int, retraction: int, ailes_nez: int, geignement: int
) -> tuple[int, list[str]]:
    """
    Score de Silverman — détresse respiratoire néonatale.
    5 items de 0 à 2. Score ≤ 2 : normal | 3-4 : modéré | ≥ 5 : sévère.
    Référence : Silverman & Andersen, Pediatrics 1956.
    """
    try:
        return min(10, balt + tirage + retraction + ailes_nez + geignement), []
    except (TypeError, ValueError) as exc:
        return 0, [f"Erreur Silverman : {exc}"]


def calculer_malinas(
    parite: int, duree_travail: int, duree_contrac: int, intervalle: int, poche: int
) -> tuple[int, list[str]]:
    """
    Score de Malinas — décision de transport vers maternité.
    Score ≥ 8 : accouchement imminent, transport contre-indiqué.
    """
    try:
        return min(10, parite + duree_travail + duree_contrac + intervalle + poche), []
    except (TypeError, ValueError) as exc:
        return 0, [f"Erreur Malinas : {exc}"]


def calculer_brulure(surface_pct: float, age_pat: float) -> tuple[float, float, str, list[str]]:
    """
    Surface corporelle brûlée — règle des 9 de Wallace.
    Formule de Baux : pronostic mortalité = âge + SCB (%).
    """
    try:
        scb  = max(0.0, min(100.0, float(surface_pct)))
        baux = float(age_pat) + scb
        if   baux > 120: pronostic = "Pronostic vital très réservé (Baux > 120)"
        elif baux > 100: pronostic = "Pronostic sévère (Baux 100-120)"
        elif baux > 80:  pronostic = "Pronostic réservé (Baux 80-100)"
        else:            pronostic = "Pronostic favorable (Baux < 80)"
        return scb, baux, pronostic, []
    except (TypeError, ValueError) as exc:
        return 0.0, 0.0, "Erreur", [f"Erreur calcul brûlure : {exc}"]


# ==============================================================================
# CALCULS SPÉCIFIQUES
# ==============================================================================

def seuils_pediatriques(age_annees: float) -> tuple[int, int, int]:
    """
    Retourne (FC_min, FC_max, PAS_min) selon la tranche d'âge.
    Formule PAS pour 1-10 ans : 70 + âge × 2.
    """
    if age_annees < 1 / 12:
        return SEUILS_PEDIATRIQUES["0_1m"]
    elif age_annees < 0.5:
        return SEUILS_PEDIATRIQUES["1_6m"]
    elif age_annees <= 2:
        return SEUILS_PEDIATRIQUES["6_24m"]
    elif age_annees <= 10:
        fc_min, fc_max = SEUILS_PEDIATRIQUES["1_10a"][:2]
        return fc_min, fc_max, int(70 + age_annees * 2)
    return 60, 120, 80


def calculer_shock_index(fc: float, pas: float) -> float:
    """Shock Index = FC / PAS. SI ≥ 1,0 : état de choc débutant probable."""
    if pas and pas > 0:
        return round(fc / pas, 2)
    return 0.0


def calculer_sipa(fc: float, age_annees: float) -> tuple[float, str]:
    """
    Shock Index Pédiatrique Ajusté à l'Âge (SIPA).
    Seuils : 0-1 an: >2,2 | 1-4 ans: >2,0 | 4-7 ans: >1,8 | 7-12 ans: >1,7.
    Référence : Acker et al., J Pediatr Surg 2015.
    Retourne : (valeur_sipa: float, interpretation: str)
    """
    # SIPA utilise FC / (FC_max_normal × facteur_âge) mais la forme simplifiée
    # la plus utilisée en urgence pédiatrique est :
    sipa = round(fc / max(1.0, float(age_annees + 1) * 15 + 70), 2)
    if age_annees <= 1:
        seuil = 2.2
    elif age_annees <= 4:
        seuil = 2.0
    elif age_annees <= 7:
        seuil = 1.8
    else:
        seuil = 1.7

    if sipa > seuil:
        return sipa, f"SIPA {sipa} > {seuil} — Choc pédiatrique probable — Tri 1"
    return sipa, f"SIPA {sipa} ≤ {seuil} — Hémodynamique pédiatrique préservée"


def mgdl_vers_mmol(mgdl: float) -> float:
    """Conversion glycémie mg/dl → mmol/l (facteur 18,016)."""
    return round(mgdl / 18.016, 1)


def mmol_vers_mgdl(mmol: float) -> float:
    """Conversion glycémie mmol/l → mg/dl (facteur 18,016)."""
    return round(mmol * 18.016, 0)


def calculer_debit_perfusion(volume_ml: float, duree_h: float) -> dict:
    """
    Calcul du débit de perfusion en ml/h, gouttes/min et microgouttes/min.
    Facteur : 1 ml = 20 gouttes macrogouttes | 1 ml = 60 microgouttes.
    """
    try:
        if duree_h <= 0:
            return {"erreur": "Durée invalide (> 0 requis)"}
        debit_ml_h   = round(volume_ml / duree_h, 1)
        gouttes_min  = round(debit_ml_h * 20 / 60, 1)
        ugouttes_min = round(debit_ml_h * 60 / 60, 1)
        return {
            "debit_ml_h":       debit_ml_h,
            "gouttes_min":      gouttes_min,
            "microgouttes_min": ugouttes_min,
            "reference":        "Calcul standard — 1 ml = 20 gouttes (macrogouttes)",
        }
    except (TypeError, ValueError) as exc:
        return {"erreur": f"Erreur calcul débit : {exc}"}


# ==============================================================================
# MOTEUR DE TRIAGE FRENCH V1.1
# ==============================================================================

def french_triage(
    motif: str,
    details: dict,
    fc: float,
    pas: float,
    spo2: float,
    fr: float,
    gcs: int,
    temp: float,
    age: float,
    news2: int,
    glycemie_mgdl: Optional[float] = None,
) -> tuple[str, str, str]:
    """
    Algorithme de triage FRENCH Triage SFMU V1.1 (2018).

    Toutes les glycémies sont en mg/dl (standard belge).
    Les valeurs manquantes sont remplacées par des valeurs physiologiques par défaut.

    Retourne : (niveau: str, justification: str, reference: str)
    Niveaux   : "M" | "1" | "2" | "3A" | "3B" | "4" | "5"
    """
    # Sécurisation des entrées
    fc    = fc    if fc    is not None else 80
    pas   = pas   if pas   is not None else 120
    spo2  = spo2  if spo2  is not None else 98
    fr    = fr    if fr    is not None else 16
    gcs   = gcs   if gcs   is not None else 15
    temp  = temp  if temp  is not None else 37.0
    news2 = news2 or 0
    if details is None:
        details = {}

    try:
        # ----------------------------------------------------------------
        # CRITÈRES TRANSVERSAUX (priorité absolue, ordre décroissant)
        # ----------------------------------------------------------------

        # NEWS2 ≥ 9 — engagement vital quel que soit le motif
        if news2 >= 9:
            return (
                "M",
                f"NEWS2 {news2} ≥ 9 — engagement vital immédiat.",
                "NEWS2 — Tri M (RFC 2017)",
            )

        # Purpura fulminans — Tri 1 absolu quel que soit le motif
        if details.get("purpura"):
            return (
                "1",
                "PURPURA FULMINANS — Ceftriaxone 2 g IV IMMÉDIAT — ne pas attendre le bilan.",
                "SPILF / SFP — Purpura fulminans 2017",
            )

        # ----------------------------------------------------------------
        # ARRÊT CARDIO-RESPIRATOIRE
        # ----------------------------------------------------------------
        if motif == "Arrêt cardio-respiratoire":
            return "1", "Arrêt cardio-respiratoire confirmé.", "FRENCH — Tri 1"

        # ----------------------------------------------------------------
        # CARDIO-CIRCULATOIRE
        # ----------------------------------------------------------------
        if motif == "Hypotension artérielle":
            if pas <= 70:
                return "1", f"PAS {pas} mmHg ≤ 70 mmHg — collapsus.", "FRENCH — Tri 1"
            if pas <= 90 or (pas <= 100 and fc > 100):
                return "2", f"PAS {pas} mmHg — état de choc débutant.", "FRENCH — Tri 2"
            if pas <= 100:
                return "3B", f"PAS {pas} mmHg — valeur limite.", "FRENCH — Tri 3B"
            return "4", "Pression artérielle dans les valeurs normales.", "FRENCH — Tri 4"

        if motif == "Douleur thoracique / SCA":
            ecg = details.get("ecg", "Normal")
            douleur = details.get("douleur_type", "Atypique")
            if ecg == "Anormal typique SCA" or douleur == "Typique persistante/intense":
                return "1", "SCA avec ECG anormal ou douleur typique — filière STEMI.", "FRENCH — Tri 1"
            if fc >= 120 or spo2 < 94:
                return "2", "Douleur thoracique avec instabilité hémodynamique.", "FRENCH — Tri 2"
            if douleur == "Type coronaire" or details.get("frcv_count", 0) >= 2:
                return "2", "Douleur coronaire probable avec FRCV multiples.", "FRENCH — Tri 2"
            if ecg == "Anormal non typique":
                return "2", "Douleur thoracique avec ECG non typique.", "FRENCH — Tri 2"
            return "3A", "Douleur thoracique atypique, stable.", "FRENCH — Tri 3A"

        if motif in ("Tachycardie / tachyarythmie", "Bradycardie / bradyarythmie", "Palpitations"):
            if fc >= 180 or fc <= 30:
                return "1", f"FC {fc} bpm — arythmie extrême.", "FRENCH — Tri 1"
            if fc >= 150 or fc <= 40:
                return "2", f"FC {fc} bpm — arythmie sévère.", "FRENCH — Tri 2"
            if details.get("mauvaise_tolérance") or details.get("malaise"):
                return "2", "Arythmie avec mauvaise tolérance clinique.", "FRENCH — Tri 2"
            return "3B", f"FC {fc} bpm — arythmie bien tolérée.", "FRENCH — Tri 3B"

        if motif == "Hypertension artérielle":
            if pas >= 220:
                return "2", f"PAS {pas} mmHg ≥ 220 mmHg — urgence hypertensive.", "FRENCH — Tri 2"
            if details.get("sf_associés") or (pas >= 180 and fc > 100):
                return "2", "HTA avec signes fonctionnels associés.", "FRENCH — Tri 2"
            if pas >= 180:
                return "3B", f"PAS {pas} mmHg — HTA sévère sans signe fonctionnel.", "FRENCH — Tri 3B"
            return "4", f"PAS {pas} mmHg — HTA modérée.", "FRENCH — Tri 4"

        if motif == "Allergie / anaphylaxie":
            if spo2 < 94 or pas < 90 or gcs < 15:
                return "1", "Anaphylaxie avec collapsus ou détresse respiratoire.", "FRENCH — Tri 1"
            if details.get("dyspnee") or details.get("urticaire_generalise"):
                return "2", "Réaction allergique généralisée avec signes systémiques.", "FRENCH — Tri 2"
            return "3B", "Réaction allergique localisée sans signe de gravité.", "FRENCH — Tri 3B"

        # ----------------------------------------------------------------
        # NEUROLOGIE
        # ----------------------------------------------------------------
        if motif == "AVC / Déficit neurologique":
            delai = details.get("délai_heures", 99)
            if delai <= 4.5:
                return "1", f"AVC suspecté — délai {delai} h ≤ 4h30 — filière Stroke.", "FRENCH — Tri 1"
            if details.get("déficit_progressif") or gcs < 15:
                return "2", "Déficit neurologique progressif ou altération de conscience.", "FRENCH — Tri 2"
            return "2", "Déficit neurologique — bilan urgent.", "FRENCH — Tri 2"

        if motif == "Traumatisme crânien":
            if gcs <= 8:
                return "1", f"TC grave — GCS {gcs}/15.", "FRENCH — Tri 1"
            if gcs <= 12 or details.get("aod_avk"):
                return "2", f"TC avec GCS {gcs}/15 ou anticoagulant — TDM urgent.", "FRENCH — Tri 2"
            if details.get("perte_conscience") or details.get("amnésie"):
                return "3A", "TC avec perte de conscience ou amnésie.", "FRENCH — Tri 3A"
            return "4", "TC bénin sans signe de gravité.", "FRENCH — Tri 4"

        if motif == "Altération de conscience / Coma":
            gl = glycemie_mgdl or details.get("glycemie_mgdl", 0)
            if gl and gl < GLYCEMIE["hypoglycemie_severe"]:
                return (
                    "2",
                    f"Hypoglycémie {gl} mg/dl ({mgdl_vers_mmol(gl)} mmol/l) — Glucose 30 % IV IMMÉDIAT.",
                    "FRENCH — Tri 2",
                )
            if gcs <= 8:
                return "1", f"Coma profond — GCS {gcs}/15.", "FRENCH — Tri 1"
            if gcs <= 13:
                return "2", f"Altération de conscience — GCS {gcs}/15.", "FRENCH — Tri 2"
            return "2", "Altération légère de conscience — évaluation urgente.", "FRENCH — Tri 2"

        if motif == "État de mal épileptique / Convulsions":
            if details.get("crises_multiples"):
                return "2", "Crises multiples ou état de mal épileptique.", "FRENCH — Tri 2"
            if details.get("confusion_post_critique"):
                return "2", "Confusion post-critique persistante.", "FRENCH — Tri 2"
            return "3B", "Convulsion avec récupération neurologique complète.", "FRENCH — Tri 3B"

        if motif == "Céphalée":
            if details.get("brutal") or details.get("plus_forte_vie"):
                return "1", "Céphalée foudroyante — suspicion HSA.", "FRENCH — Tri 1"
            if details.get("raideur_nuque") or details.get("fievre_cephalee"):
                return "2", "Céphalée avec signes méningés ou fièvre.", "FRENCH — Tri 2"
            if details.get("deficit_asso"):
                return "2", "Céphalée avec déficit neurologique associé.", "FRENCH — Tri 2"
            return "3B", "Céphalée sans signe de gravité.", "FRENCH — Tri 3B"

        if motif == "Syndrome confusionnel":
            if gcs < 13 or details.get("agitation"):
                return "2", "Confusion avec agitation ou altération du GCS.", "FRENCH — Tri 2"
            return "3A", "Syndrome confusionnel — évaluation médicale urgente.", "FRENCH — Tri 3A"

        if motif == "Malaise":
            gl = glycemie_mgdl or details.get("glycemie_mgdl", 0)
            if gl and gl < GLYCEMIE["hypoglycemie_severe"]:
                return (
                    "2",
                    f"Malaise avec hypoglycémie {gl} mg/dl.",
                    "FRENCH — Tri 2",
                )
            if news2 >= 2 or details.get("anomalie_vitaux"):
                return "2", "Malaise avec anomalie des paramètres vitaux.", "FRENCH — Tri 2"
            return "3B", "Malaise récupéré sans anomalie vitale.", "FRENCH — Tri 3B"

        # ----------------------------------------------------------------
        # RESPIRATOIRE
        # ----------------------------------------------------------------
        if motif in ("Dyspnée / insuffisance respiratoire", "Dyspnée / insuffisance cardiaque"):
            bpco = "BPCO" in details.get("atcd", [])
            cible_spo2 = 92 if bpco else 95
            if spo2 < (88 if bpco else 91) or fr >= 40:
                return "1", (
                    f"Détresse respiratoire — SpO2 {spo2} % "
                    f"({'cible BPCO 88-92 %' if bpco else 'cible standard 94+ %'}), FR {fr} /min."
                ), "FRENCH — Tri 1"
            if spo2 < cible_spo2 or fr >= 30 or not details.get("parole_ok", True):
                return "2", f"Dyspnée sévère — SpO2 {spo2} %, FR {fr} /min.", "FRENCH — Tri 2"
            if details.get("orthopnee") or details.get("tirage"):
                return "2", "Dyspnée avec orthopnée ou tirage intercostal.", "FRENCH — Tri 2"
            return "3B", f"Dyspnée modérée — SpO2 {spo2} %, FR {fr} /min.", "FRENCH — Tri 3B"

        # ----------------------------------------------------------------
        # DIGESTIF
        # ----------------------------------------------------------------
        if motif == "Douleur abdominale":
            si = calculer_shock_index(fc, pas)
            if pas < 90 or si >= 1.0:
                return "2", f"Douleur abdominale avec choc (SI {si}).", "FRENCH — Tri 2"
            if details.get("grossesse") or details.get("geu_suspecte"):
                return "2", "Douleur abdominale sur grossesse — GEU à éliminer.", "FRENCH — Tri 2"
            if details.get("defense") or details.get("contracture"):
                return "2", "Abdomen chirurgical probable.", "FRENCH — Tri 2"
            if details.get("mauvaise_tolérance"):
                return "3A", "Douleur abdominale avec mauvaise tolérance.", "FRENCH — Tri 3A"
            return "3B", "Douleur abdominale tolérée.", "FRENCH — Tri 3B"

        # ----------------------------------------------------------------
        # INFECTIOLOGIE
        # ----------------------------------------------------------------
        if motif == "Fièvre":
            si = calculer_shock_index(fc, pas)
            if details.get("purpura"):
                return "1", "Fièvre avec purpura non effaçable — Ceftriaxone 2 g IV IMMÉDIAT.", "FRENCH — Tri 1"
            if temp >= 40 or temp <= 35.2 or details.get("confusion"):
                return "2", f"Fièvre avec critère de gravité (T° {temp} °C).", "FRENCH — Tri 2"
            if details.get("mauvaise_tolérance") or pas < 100 or si >= 1.0:
                return "3B", f"Fièvre avec mauvaise tolérance (SI {si}).", "FRENCH — Tri 3B"
            return "5", "Fièvre bien tolérée.", "FRENCH — Tri 5"

        # ----------------------------------------------------------------
        # PÉDIATRIE
        # ----------------------------------------------------------------
        if motif == "Pédiatrie - Fièvre ≤ 3 mois":
            return (
                "2",
                "Fièvre chez nourrisson ≤ 3 mois — évaluation médicale urgente systématique.",
                "FRENCH Pédiatrie — Tri 2",
            )

        # ----------------------------------------------------------------
        # TRAUMATOLOGIE
        # ----------------------------------------------------------------
        if motif in (
            "Traumatisme du thorax / abdomen / rachis cervical",
            "Traumatisme du bassin / hanche / fémur",
        ):
            if details.get("pénétrant") or details.get("cinetique") == "Haute":
                return "1", "Traumatisme pénétrant ou haute cinétique.", "FRENCH — Tri 1"
            si = calculer_shock_index(fc, pas)
            if si >= 1.0 or spo2 < 94:
                return "2", f"Traumatisme avec signes hémodynamiques (SI {si}).", "FRENCH — Tri 2"
            return "2", "Traumatisme thoracique/abdominal/rachidien — évaluation urgente.", "FRENCH — Tri 2"

        if motif == "Traumatisme d'un membre / épaule":
            if details.get("ischemie"):
                return "1", "Traumatisme avec ischémie distale.", "FRENCH — Tri 1"
            if details.get("impotence_totale") and details.get("déformation"):
                return "2", "Fracture déplacée avec impotence totale.", "FRENCH — Tri 2"
            if details.get("impotence_totale"):
                return "3A", "Impotence fonctionnelle totale.", "FRENCH — Tri 3A"
            if details.get("déformation"):
                return "3A", "Déformation visible.", "FRENCH — Tri 3A"
            if details.get("impotence_modérée"):
                return "4", "Impotence fonctionnelle modérée.", "FRENCH — Tri 4"
            return "4", "Traumatisme de membre sans signe de gravité.", "FRENCH — Tri 4"

        # ----------------------------------------------------------------
        # PEAU
        # ----------------------------------------------------------------
        if motif == "Pétéchie / Purpura":
            if details.get("non_effacable"):
                return (
                    "1",
                    "Purpura non effaçable = purpura fulminans potentiel — Ceftriaxone 2 g IV IMMÉDIAT.",
                    "SPILF / SFP — Purpura fulminans 2017",
                )
            if temp >= 38.0 or details.get("mauvaise_tolérance"):
                return "2", "Purpura avec fièvre — suspicion purpura fulminans.", "FRENCH — Tri 2"
            return "3B", "Pétéchies / purpura effaçable — bilan hémostase.", "FRENCH — Tri 3B"

        if motif == "Écchymose / Hématome spontané":
            return "3B", "Hématome spontané — bilan hémostase.", "FRENCH — Tri 3B"

        # ----------------------------------------------------------------
        # GYNÉCOLOGIE / OBSTÉTRIQUE
        # ----------------------------------------------------------------
        if motif == "Accouchement imminent":
            return "M", "Accouchement imminent.", "FRENCH — Tri M"

        if motif in (
            "Complication de grossesse (1er / 2ème trimestre)",
            "Complication de grossesse (3ème trimestre)",
        ):
            return "3A", "Complication de grossesse — surveillance urgente.", "FRENCH — Tri 3A"

        if motif == "Ménorragie / Métrorragie":
            if details.get("grossesse") or details.get("abondante"):
                return "2", "Métrorragie abondante ou sur grossesse connue.", "FRENCH — Tri 2"
            return "3B", "Saignement génital modéré.", "FRENCH — Tri 3B"

        # ----------------------------------------------------------------
        # MÉTABOLIQUE
        # ----------------------------------------------------------------
        if motif == "Hypoglycémie":
            gl = glycemie_mgdl or details.get("glycemie_mgdl", 0)
            if gl and gl < GLYCEMIE["hypoglycemie_severe"]:
                return (
                    "2",
                    f"Hypoglycémie sévère {gl} mg/dl ({mgdl_vers_mmol(gl)} mmol/l) — Glucose 30 % IV.",
                    "FRENCH — Tri 2",
                )
            if gcs < 15:
                return "2", f"Hypoglycémie avec GCS {gcs}/15.", "FRENCH — Tri 2"
            if gl and gl < GLYCEMIE["hypoglycemie_moderee"]:
                return "3A", f"Hypoglycémie modérée {gl} mg/dl.", "FRENCH — Tri 3A"
            return "3B", "Hypoglycémie légère tolérée.", "FRENCH — Tri 3B"

        if motif == "Hyperglycémie / Cétoacidose diabétique":
            gl = glycemie_mgdl or details.get("glycemie_mgdl", 0)
            if details.get("cetose_élevée") or gcs < 15:
                return "2", "Cétoacidose diabétique ou trouble de conscience.", "FRENCH — Tri 2"
            if gl and gl >= GLYCEMIE["hyperglycemie_severe"]:
                return "3B", f"Hyperglycémie sévère {gl} mg/dl.", "FRENCH — Tri 3B"
            return "4", "Hyperglycémie modérée bien tolérée.", "FRENCH — Tri 4"

        # ----------------------------------------------------------------
        # DIVERS / RENOUVELLEMENT
        # ----------------------------------------------------------------
        if motif in ("Renouvellement ordonnance", "Examen administratif / Certificat"):
            return "5", "Consultation non urgente.", "FRENCH — Tri 5"

        # ----------------------------------------------------------------
        # FALLBACK — motif non reconnu
        # ----------------------------------------------------------------
        if news2 >= 7:
            return "2", f"NEWS2 {news2} ≥ 7 — risque clinique élevé.", "NEWS2 — Tri 2"
        if news2 >= 5:
            return "3A", f"NEWS2 {news2} ≥ 5 — réévaluation rapide.", "NEWS2 — Tri 3A"
        return "3B", f"Motif '{motif}' — évaluation clinique standard.", "FRENCH — Tri 3B"

    except Exception as exc:
        return "2", f"Erreur moteur de triage : {exc}", "Erreur — Tri 2 par sécurité"


# ==============================================================================
# COHÉRENCE ET SBAR
# ==============================================================================

def verifier_coherence(
    fc: float, pas: float, spo2: float, fr: float, gcs: int,
    temp: float, eva: int, motif: str, atcd: list, details: dict,
    news2: int, glycemie_mgdl: Optional[float] = None,
) -> tuple[list[str], list[str], list[str]]:
    """
    Vérification de la cohérence clinique des paramètres saisis.
    Détecte les interactions médicamenteuses et les incohérences physiologiques.
    Retourne : (alertes_danger: list, alertes_attention: list, infos: list)
    """
    danger: list[str] = []
    attention: list[str] = []
    infos: list[str] = []

    sous_ac = "Anticoagulants / AOD" in atcd

    # Interactions médicamenteuses critiques
    if "IMAO (inhibiteurs MAO)" in atcd:
        danger.append(
            "IMAO DÉTECTÉS — Tramadol CONTRE-INDIQUÉ (syndrome sérotoninergique fatal). "
            "Informer le médecin prescripteur avant toute antalgie."
        )
    if "Antidépresseurs sérotoninergiques (ISRS / IRSNA)" in atcd:
        attention.append(
            "ISRS / IRSNA — Interaction majeure avec Tramadol. Préférer Dipidolor ou Morphine."
        )

    # Hypoglycémie critique
    gl = glycemie_mgdl or (details.get("glycemie_mgdl") if details else None)
    if gl:
        if gl < GLYCEMIE["hypoglycemie_severe"]:
            danger.append(
                f"HYPOGLYCÉMIE SÉVÈRE : {gl} mg/dl ({mgdl_vers_mmol(gl)} mmol/l) "
                "— Glucose 30 % 50 ml IV immédiat."
            )
        elif gl < GLYCEMIE["hypoglycemie_moderee"]:
            attention.append(f"Hypoglycémie modérée : {gl} mg/dl — corriger avant antalgique.")

    # Paramètres vitaux critiques
    si = calculer_shock_index(fc, pas)
    if si >= 1.0:
        danger.append(f"Shock Index = {si} ≥ 1,0 — état de choc probable.")
    if spo2 < 90:
        danger.append(f"SpO2 {spo2} % — hypoxémie sévère — oxygénothérapie urgente.")
    if fr >= 30:
        attention.append(f"FR {fr} /min — tachypnée significative.")
    if fc >= 150 or fc <= 40:
        danger.append(f"FC {fc} bpm — arythmie critique.")

    # Anticoagulants + traumatisme crânien
    if sous_ac and "Traumatisme crânien" in motif:
        danger.append("TC sous AOD / AVK — TDM cérébral urgent, risque d'hématome différé.")

    return danger, attention, infos


def generer_sbar(
    age: float,
    motif: str,
    cat: str,
    atcd: list,
    allergies: str,
    o2_supp: bool,
    temp: float,
    fc: float,
    pas: float,
    spo2: float,
    fr: float,
    gcs: int,
    eva: int,
    news2: int,
    niveau: str,
    justif: str,
    critere: str,
    code_operateur: str = "IAO",
    glycemie_mgdl: Optional[float] = None,
) -> str:
    """
    Génère un rapport SBAR (Situation-Background-Assessment-Recommendation)
    au format DPI-Ready pour transmission médicale.
    Compatible avec les systèmes de Dossier Patient Informatisé belges.
    """
    heure = datetime.now().strftime("%d/%m/%Y %H:%M")
    atcd_str = ", ".join(atcd) if atcd else "Aucun antécédent notable"
    gl_str = (
        f"{glycemie_mgdl} mg/dl ({mgdl_vers_mmol(glycemie_mgdl)} mmol/l)"
        if glycemie_mgdl else "Non mesurée"
    )
    o2_str = "O2 supplémentaire en cours" if o2_supp else "Air ambiant"

    sbar = f"""═══════════════════════════════════════════════════════════════
RAPPORT DE TRIAGE IAO — FORMAT SBAR — AKIR-IAO v17.1
Opérateur IAO : {code_operateur}  |  {heure}
Référentiel   : FRENCH Triage SFMU V1.1 — Wallonie, Belgique
═══════════════════════════════════════════════════════════════

[S] SITUATION
─────────────
Patient de {int(age)} ans | Motif de recours : {motif} | Catégorie : {cat}
Niveau de triage attribué : {LABELS_TRI.get(niveau, niveau)}
Secteur de prise en charge : {SECTEURS_TRI.get(niveau, "")}
Critère de triage : {critere}

[B] BACKGROUND
──────────────
Antécédents   : {atcd_str}
Allergies     : {allergies or "Aucune allergie connue"}

[A] ASSESSMENT
──────────────
Paramètres vitaux à l'IAO :
  FC     : {fc} bpm
  PAS    : {pas} mmHg
  SpO2   : {spo2} %  ({o2_str})
  FR     : {fr} /min
  T°     : {temp} °C
  GCS    : {gcs} / 15
  EVA    : {eva} / 10
  NEWS2  : {news2} pts
  Glycémie capillaire : {gl_str}

Justification clinique : {justif}

[R] RECOMMENDATION
──────────────────
Orientation     : {SECTEURS_TRI.get(niveau, niveau)}
Délai maximum   : {DELAIS_TRI.get(niveau, "?")} minutes
Remarques IAO   : [À compléter par l'opérateur]

═══════════════════════════════════════════════════════════════
AVERTISSEMENT MÉDICO-LÉGAL
Ce document est un support d'aide à la décision clinique.
Il ne se substitue pas au jugement clinique du médecin responsable.
AR 18/06/1990 modifié — Responsabilité infirmière — Hainaut, Belgique.
═══════════════════════════════════════════════════════════════"""
    return sbar


# ==============================================================================
# [2] PHARMACOLOGIE BCFI
# ==============================================================================



# ==============================================================================
# CONSTANTES PHARMACOLOGIQUES
# ==============================================================================

# Seuils glycémiques pour activation/désactivation des protocoles glucose
GLYCEMIE_HYPOGLYCEMIE_SEVERE  = 54   # mg/dl — < 3,0 mmol/l
GLYCEMIE_HYPOGLYCEMIE_MODEREE = 70   # mg/dl — < 3,9 mmol/l

# Contre-indications AINS partagées
_CI_AINS_MOTIFS = [
    "Ulcère gastro-duodénal",
    "Insuffisance rénale chronique",
    "Insuffisance hépatique",
    "Grossesse en cours",
    "Chimiothérapie en cours",
]


# ==============================================================================
# HELPERS INTERNES
# ==============================================================================

def _verifier_ci_ains(atcd: list[str]) -> list[str]:
    """Retourne la liste des contre-indications AINS actives pour ce patient."""
    return [ci for ci in _CI_AINS_MOTIFS if ci in atcd]


def _arrondir_dose(dose: float, pas: float = 0.5) -> float:
    """Arrondit la dose au plus proche multiple de `pas` (défaut : 0,5 mg)."""
    return round(round(dose / pas) * pas, 3)


# ==============================================================================
# ANTALGIQUES DE PALIER I
# ==============================================================================

def dose_paracetamol_iv(poids_kg: float) -> tuple[Optional[dict], Optional[str]]:
    """
    Paracétamol IV — palier I.
    ≥ 50 kg : dose fixe 1 g IV (perfusion 15 min) toutes les 6 h.
    < 50 kg : 15 mg/kg IV, maximum 1 g par dose, toutes les 6 h.
    Dose maximale journalière : 4 g / 24 h (60 mg/kg/j si < 50 kg).
    Référence : BCFI — Paracétamol — RCP Belgique.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide (> 0 requis)"
        if poids_kg >= 50:
            dose_g   = 1.0
            volume   = "100 ml NaCl 0,9 % ou G5 % — perfusion IV sur 15 min"
            note_age = ""
        else:
            dose_g   = min(round(15 * poids_kg / 1000, 2), 1.0)
            volume   = f"{dose_g * 1000:.0f} mg dans 100 ml NaCl 0,9 % — perfusion IV sur 15 min"
            note_age = f"Dose poids-dépendante : 15 mg/kg = {dose_g * 1000:.0f} mg pour {poids_kg} kg"
        return {
            "dose_g":      dose_g,
            "dose_mg":     dose_g * 1000,
            "volume":      volume,
            "frequence":   "Toutes les 6 h (maximum 4 g / 24 h)",
            "note":        note_age,
            "reference":   "BCFI — Paracétamol IV — RCP Belgique",
        }, None
    except (TypeError, ValueError) as exc:
        return None, f"Erreur dose paracétamol : {exc}"


# ==============================================================================
# ANTALGIQUES DE PALIER II — AINS
# ==============================================================================

def dose_ketorolac_iv(poids_kg: float, atcd: list[str]) -> tuple[Optional[dict], Optional[str]]:
    """
    Kétorolac (Taradyl) IV — AINS palier II.
    Dose standard : 30 mg IV lent (< 15 s). Durée maximale : 5 jours.
    Contre-indications absolues : ulcère, IRC, grossesse, chimiothérapie.
    Référence : BCFI — Kétorolac trométhamine — RCP Belgique.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"
        ci = _verifier_ci_ains(atcd)
        if ci:
            return None, f"CONTRE-INDIQUÉ : {', '.join(ci)}"
        # Sujet âgé ≥ 65 ans : dose réduite 15 mg IV
        dose_mg = 15.0 if poids_kg < 50 else 30.0
        return {
            "dose_mg":   dose_mg,
            "admin":     "IV lent sur 15 secondes minimum",
            "frequence": "Toutes les 6 h — maximum 5 jours",
            "note":      "Dose 15 mg si < 50 kg ou insuffisance rénale légère",
            "reference": "BCFI — Kétorolac trométhamine (Taradyl) — RCP Belgique",
        }, None
    except (TypeError, ValueError) as exc:
        return None, f"Erreur dose kétorolac : {exc}"


def dose_diclofenac_im(poids_kg: float, atcd: list[str]) -> tuple[Optional[dict], Optional[str]]:
    """
    Diclofénac (Voltaren) IM — AINS palier II.
    Dose standard : 75 mg IM profond dans le quadrant supéro-externe fessier.
    Maximum 2 injections / 24 h, durée maximale 2 jours.
    Référence : BCFI — Diclofénac — RCP Belgique.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"
        ci = _verifier_ci_ains(atcd)
        if ci:
            return None, f"CONTRE-INDIQUÉ : {', '.join(ci)}"
        return {
            "dose_mg":   75.0,
            "admin":     "IM profond — quadrant supéro-externe de la fesse",
            "frequence": "Maximum 2 × 75 mg / 24 h — durée maximale 2 jours",
            "note":      "Ne pas administrer IV ni SC",
            "reference": "BCFI — Diclofénac sodique (Voltaren) — RCP Belgique",
        }, None
    except (TypeError, ValueError) as exc:
        return None, f"Erreur dose diclofénac : {exc}"


# ==============================================================================
# ANTALGIQUES DE PALIER II — OPIOÏDES FAIBLES
# ==============================================================================

def dose_tramadol_iv(
    poids_kg: float,
    atcd: list[str],
    age_patient: float,
) -> tuple[Optional[dict], Optional[str]]:
    """
    Tramadol IV — opioïde faible palier II.
    Dose standard : 100 mg IV dilué dans 100 ml NaCl, perfusion sur 30 min.
    Contre-indications absolues : épilepsie, IMAO (syndrome sérotoninergique fatal).
    Interaction majeure : ISRS / IRSNA.
    Référence : BCFI — Tramadol chlorhydrate — RCP Belgique.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"

        alertes: list[str] = []
        ci: list[str] = []

        # Contre-indication absolue : épilepsie
        if "Épilepsie" in atcd:
            alertes.append(
                "CONTRE-INDIQUÉ ABSOLU : Tramadol abaisse le seuil épileptogène — "
                "risque de convulsions."
            )
        # Contre-indication absolue : IMAO — syndrome sérotoninergique potentiellement fatal
        if "IMAO (inhibiteurs MAO)" in atcd:
            alertes.append(
                "CONTRE-INDICATION ABSOLUE : Tramadol + IMAO — "
                "SYNDROME SÉROTONINERGIQUE FATAL. "
                "Délai minimum 14 jours après arrêt IMAO irréversible."
            )
        # Interaction majeure : ISRS / IRSNA
        if "Antidépresseurs sérotoninergiques (ISRS / IRSNA)" in atcd:
            alertes.append(
                "INTERACTION MAJEURE : Tramadol + ISRS/IRSNA — syndrome sérotoninergique. "
                "Évaluer le rapport bénéfice/risque — envisager Piritramide ou Morphine."
            )
        # Grossesse
        if "Grossesse en cours" in atcd:
            ci.append("Grossesse (1er trimestre CONTRE-INDIQUÉ)")

        if ci:
            return None, f"Contre-indication : {', '.join(ci)}"

        dose_mg = 100.0 if poids_kg >= 50 else round(1.5 * poids_kg, 0)
        note_age = "Dose standard" if age_patient < 75 else "Réduire à 50 mg si > 75 ans"

        return {
            "dose_mg":    dose_mg,
            "admin":      f"{dose_mg:.0f} mg dilués dans 100 ml NaCl 0,9 % — IV sur 30 min",
            "frequence":  "Toutes les 6 h (maximum 400 mg / 24 h)",
            "alertes":    alertes,
            "note":       note_age,
            "reference":  "BCFI — Tramadol chlorhydrate — RCP Belgique",
        }, None
    except (TypeError, ValueError) as exc:
        return None, f"Erreur dose tramadol : {exc}"


# ==============================================================================
# ANTALGIQUES DE PALIER III — OPIOÏDES FORTS
# ==============================================================================

def dose_piritramide_iv(
    poids_kg: float,
    age_patient: float,
    atcd: list[str],
) -> tuple[Optional[dict], Optional[str]]:
    """
    Piritramide (Dipidolor) IV — opioïde fort — titration pure.
    Protocole SFAR 2010 : bolus 0,03-0,05 mg/kg IV sur 1-2 min.
    Maximum par bolus : 3 mg (6 mg si > 70 kg, sauf sujet âgé).
    Réduction 50 % si âge ≥ 70 ans, IRC ou insuffisance hépatique.
    Référence : BCFI — Piritramide (Dipidolor) — RCP Belgique.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"

        reduction = (
            age_patient >= 70
            or "Insuffisance rénale chronique" in atcd
            or "Insuffisance hépatique" in atcd
        )
        facteur = 0.5 if reduction else 1.0

        d_min = round(0.03 * poids_kg * facteur, 2)
        d_max = round(0.05 * poids_kg * facteur, 2)
        plafond = (3.0 if poids_kg < 70 else 6.0) * facteur
        d_min = min(d_min, plafond)
        d_max = min(d_max, plafond)

        note_reduction = (
            "DOSE RÉDUITE 50 % — âge ≥ 70 ans, IRC ou insuffisance hépatique"
            if reduction else ""
        )

        return {
            "bolus_min": d_min,
            "bolus_max": d_max,
            "plafond":   plafond,
            "admin":     f"IV lent sur 1-2 min. Répéter si EVA > 3 après 10-15 min.",
            "objectif":  "EVA ≤ 3",
            "note":      note_reduction,
            "antidote":  "Naloxone 0,4 mg IV en cas de dépression respiratoire (SpO2 < 90 % ou FR < 10 /min)",
            "reference": "BCFI — Piritramide (Dipidolor) — SFAR 2010 — RCP Belgique",
        }, None
    except (TypeError, ValueError) as exc:
        return None, f"Erreur dose piritramide : {exc}"


def dose_morphine_iv(
    poids_kg: float,
    age_patient: float,
) -> tuple[Optional[dict], Optional[str]]:
    """
    Morphine IV — opioïde fort de référence.
    Dose initiale : 0,05-0,1 mg/kg IV (maximum 5 mg par bolus).
    Réduction 50 % si âge ≥ 70 ans.
    Référence : BCFI — Morphine chlorhydrate — Protocoles urgences Belgique.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"
        reduction = age_patient >= 70
        facteur = 0.5 if reduction else 1.0
        d_min = min(round(0.05 * poids_kg * facteur, 1), 2.5)
        d_max = min(round(0.10 * poids_kg * facteur, 1), 5.0)
        return {
            "bolus_min": d_min,
            "bolus_max": d_max,
            "admin":     "IV lent sur 2-3 min. Titration par paliers de 2 mg toutes les 5-10 min.",
            "objectif":  "EVA ≤ 3",
            "note":      "Dose réduite 50 % si âge ≥ 70 ans" if reduction else "",
            "antidote":  "Naloxone 0,4 mg IV en cas de dépression respiratoire",
            "reference": "BCFI — Morphine chlorhydrate — RCP Belgique",
        }, None
    except (TypeError, ValueError) as exc:
        return None, f"Erreur dose morphine : {exc}"


# ==============================================================================
# ANTIDOTES ET URGENCES
# ==============================================================================

def dose_naloxone(
    poids_kg: float,
    age_patient: float,
    dependance_opioides: bool = False,
) -> tuple[Optional[dict], Optional[str]]:
    """
    Naloxone IV — antidote des opioïdes (Dipidolor, Morphine, Tramadol).
    Indication : SpO2 < 90 % ou FR < 10 /min ou sédation excessive sous opioïde.

    Adulte sans dépendance   : 0,4 mg IV, répéter toutes les 2-3 min (max 10 mg).
    Enfant < 18 ans          : 0,01 mg/kg IV (max 0,4 mg par bolus).
    Dépendance aux opioïdes  : titration douce 0,04 mg IV par paliers de 2 min.

    Référence : BCFI — Naloxone chlorhydrate (Narcan) — RCP Belgique.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"
        alertes: list[str] = []

        if dependance_opioides:
            dose_bolus = 0.04
            admin = "0,04 mg IV par paliers de 2 min — titration douce (éviter le sevrage brutal)"
            note  = (
                "DÉPENDANCE AUX OPIOÏDES — objectif : ventilation adéquate, "
                "PAS la levée totale de l'analgésie"
            )
            alertes.append(
                "Risque de syndrome de sevrage aigu et de douleur rebond si surdosage en Naloxone"
            )
        elif age_patient < 18:
            dose_bolus = min(round(0.01 * poids_kg, 3), 0.4)
            admin = (
                f"{dose_bolus} mg IV direct (0,01 mg/kg), "
                "répéter toutes les 2-3 min si besoin"
            )
            note = f"Dose pédiatrique : 0,01 mg/kg — {dose_bolus} mg pour {poids_kg} kg"
        else:
            dose_bolus = 0.4
            admin = "0,4 mg IV direct — répéter toutes les 2-3 min si besoin (max 10 mg total)"
            note  = "Absence de réponse après 10 mg : reconsidérer le diagnostic"

        return {
            "dose_bolus":   dose_bolus,
            "admin":        admin,
            "note":         note,
            "alertes":      alertes,
            "surveillance": (
                "Monitorage SpO2 + FR + conscience continus — "
                "demi-vie courte (30-90 min) : surveiller la réapparition "
                "de la dépression respiratoire"
            ),
            "reference": "BCFI — Naloxone chlorhydrate (Narcan) — RCP Belgique",
        }, None
    except (TypeError, ValueError) as exc:
        return None, f"Erreur dose Naloxone : {exc}"


def dose_adrenaline_anaphylaxie(poids_kg: float) -> tuple[Optional[dict], Optional[str]]:
    """
    Adrénaline IM — choc anaphylactique.
    Adulte ≥ 30 kg : 0,5 mg IM (0,5 ml solution 1 mg/ml).
    Enfant < 30 kg : 0,01 mg/kg IM, maximum 0,5 mg.
    Site d'injection : face antéro-latérale de la cuisse.
    Référence : BCFI — Adrénaline Sterop 1 mg/ml — Lignes directrices anaphylaxie 2023.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"
        if poids_kg >= 30:
            dose_mg = 0.5
            note    = "0,5 ml de la solution à 1 mg/ml (ampoule standard)"
        else:
            dose_mg = min(round(0.01 * poids_kg, 3), 0.5)
            note    = f"0,01 mg/kg → {dose_mg} mg ({round(dose_mg * 1000):.0f} µg)"
        return {
            "dose_mg":  dose_mg,
            "voie":     "Injection intramusculaire — face antéro-latérale de la cuisse",
            "note":     note,
            "répéter":  "Répéter à 5-15 min si absence d'amélioration hémodynamique",
            "moniteur": "Monitorage continu : FC, PA, SpO2 post-injection",
            "reference": "BCFI — Adrénaline Sterop 1 mg/ml — Lignes directrices anaphylaxie 2023",
        }, None
    except (TypeError, ValueError) as exc:
        return None, f"Erreur dose adrénaline : {exc}"


def dose_glucose_hypoglycemie(
    poids_kg: float,
    voie: str = "IV",
    glycemie_mgdl: Optional[float] = None,
) -> tuple[Optional[dict], Optional[str]]:
    """
    Correction d'hypoglycémie — protocoles BCFI Belgique.

    Sécurité : si glycémie non mesurée (None), le protocole n'est pas activé.
    Cette règle de sécurité évite l'administration de glucose sans confirmation.

    Voie IV : Glucose 30 % (Glucosie) : 0,3 g/kg, maximum 50 ml IV lent.
    Voie IM : Glucagon GlucaGen HypoKit : 1 mg IM / SC si accès veineux impossible.

    Référence : BCFI — Glucose 30 % / Glucagon — RCP Belgique.
    """
    try:
        # Sécurité dynamique : désactiver si glycémie non mesurée
        if glycemie_mgdl is None:
            return None, (
                "Glycémie capillaire non mesurée — "
                "protocole glucose désactivé par sécurité. "
                "Mesurer la glycémie avant toute administration."
            )
        if poids_kg <= 0:
            return None, "Poids invalide"

        if voie == "IV":
            dose_g   = min(round(0.3 * poids_kg, 1), 15.0)
            dose_ml  = round(dose_g / 0.3, 0)
            return {
                "dose_g":   dose_g,
                "dose_ml":  dose_ml,
                "volume":   f"{dose_ml:.0f} ml de Glucose 30 % (Glucosie) IV lent sur 5 min",
                "controle": "Glycémie capillaire de contrôle à 15 min",
                "reference": "BCFI — Glucose 30 % (Glucosie) — RCP Belgique",
            }, None
        else:
            return {
                "dose":      "1 mg de Glucagon",
                "admin":     "IM ou SC — si accès veineux impossible",
                "note":      "Inefficace en cas d'hypoglycémie prolongée ou hépatopathie",
                "controle":  "Glycémie de contrôle à 20 min",
                "reference": "BCFI — Glucagon (GlucaGen HypoKit) — RCP Belgique",
            }, None
    except (TypeError, ValueError) as exc:
        return None, f"Erreur dose glucose : {exc}"


def infos_meopa(age_patient: float, atcd: list[str]) -> dict:
    """
    MEOPA (Kalinox) — mélange O2 / N2O 50/50.
    Indication : analgésie non invasive pour actes douloureux courts.
    AMM adulte et enfant ≥ 1 an.
    Référence : BCFI — MEOPA (Kalinox) — RCP Belgique.
    """
    ci_abs = [
        "Pneumothorax ou pneumopéricarde",
        "Embolie gazeuse",
        "Traumatisme crânien avec altération de conscience",
        "Occlusion intestinale",
        "Déficit en vitamine B12",
    ]
    ci_pat = [ci for ci in ci_abs if ci in atcd]

    return {
        "age_min_amm":  "1 an",
        "admin":        "Inhalation spontanée via masque facial avec valve anti-retour",
        "duree_max":    "15 min par session — ventilation de la pièce obligatoire après usage",
        "surveillance": "SpO2, FC, état de conscience. Arrêt si désaturation ou agitation.",
        "ci_absolues":  ci_abs,
        "ci_patient":   ci_pat,
        "reference":    "BCFI — MEOPA (Kalinox) — RCP Belgique",
    }


def dose_ceftriaxone_iv(
    poids_kg: float,
    age_patient: float,
    indication: str = "Purpura fulminans / Méningite",
) -> tuple[Optional[dict], Optional[str]]:
    """
    Ceftriaxone IV / IM — urgence infectieuse (purpura fulminans, méningite).
    Adulte   : 2 g IV ou IM (si voie IV impossible) — dose unique initiale.
    Enfant   : 50-100 mg/kg (max 2 g) — dose unique initiale.
    Référence : BCFI — Ceftriaxone — Recommandations SPILF 2017.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"
        if age_patient < 18:
            dose_g = min(round(0.1 * poids_kg, 1), 2.0)
            note   = f"100 mg/kg = {dose_g * 1000:.0f} mg pour {poids_kg} kg (max 2 g)"
        else:
            dose_g = 2.0
            note   = "Dose adulte standard : 2 g — ne pas attendre le médecin si purpura fulminans"
        return {
            "dose_g":    dose_g,
            "dose_mg":   dose_g * 1000,
            "admin":     "IV direct sur 3-5 min ou IM si VVP impossible",
            "note":      note,
            "indication": indication,
            "reference":  "BCFI — Ceftriaxone — SPILF / SFP Purpura fulminans 2017",
        }, None
    except (TypeError, ValueError) as exc:
        return None, f"Erreur dose ceftriaxone : {exc}"


# ==============================================================================
# PROTOCOLE ANTALGIQUE BASÉ SUR L'EVA
# ==============================================================================

def protocole_antalgique_eva(
    eva: int,
    poids_kg: float,
    age_patient: float,
    atcd: list[str],
    glycemie_mgdl: Optional[float] = None,
) -> dict:
    """
    Recommandation de palier antalgique basée sur l'EVA et le profil patient.
    Suit l'échelle OMS adaptée aux urgences belges.
    Intègre les contre-indications AINS et interactions opioïdes.

    EVA 0-3   : Palier I — Paracétamol IV
    EVA 4-6   : Palier II — AINS (si pas de CI) ou Tramadol
    EVA 7-10  : Palier III — Opioïde fort (Dipidolor ou Morphine)
    """
    alertes_globales: list[str] = []
    imao    = "IMAO (inhibiteurs MAO)" in atcd
    isrs    = "Antidépresseurs sérotoninergiques (ISRS / IRSNA)" in atcd
    ci_ains = _verifier_ci_ains(atcd)

    if imao:
        alertes_globales.append(
            "IMAO ACTIF — Tramadol CONTRE-INDIQUÉ (syndrome sérotoninergique fatal). "
            "Utiliser Paracétamol IV ou Dipidolor avec avis médical."
        )
    if isrs:
        alertes_globales.append(
            "ISRS / IRSNA — Tramadol déconseillé. Préférer Dipidolor ou Morphine."
        )

    recommandations: list[dict] = []

    if eva <= 3:
        res, err = dose_paracetamol_iv(poids_kg)
        if res:
            recommandations.append({"palier": "I", "medicament": "Paracétamol IV", **res})

    elif eva <= 6:
        # Paracétamol systématiquement en association
        res_para, _ = dose_paracetamol_iv(poids_kg)
        if res_para:
            recommandations.append({"palier": "I", "medicament": "Paracétamol IV (association)", **res_para})
        # AINS si pas de CI et pas de chimiothérapie
        if not ci_ains:
            res_ains, err_ains = dose_ketorolac_iv(poids_kg, atcd)
            if res_ains:
                recommandations.append({"palier": "II", "medicament": "Kétorolac (Taradyl) IV", **res_ains})
        # Tramadol si pas de CI absolue
        if not imao and "Épilepsie" not in atcd:
            res_tram, err_tram = dose_tramadol_iv(poids_kg, atcd, age_patient)
            if res_tram:
                recommandations.append({"palier": "II", "medicament": "Tramadol IV", **res_tram})

    else:
        # EVA 7-10 : opioïde fort
        res_para, _ = dose_paracetamol_iv(poids_kg)
        if res_para:
            recommandations.append({"palier": "I", "medicament": "Paracétamol IV (association)", **res_para})
        res_dip, err_dip = dose_piritramide_iv(poids_kg, age_patient, atcd)
        if res_dip:
            recommandations.append({"palier": "III", "medicament": "Piritramide (Dipidolor) IV — titration", **res_dip})
        else:
            # Fallback : Morphine
            res_mor, _ = dose_morphine_iv(poids_kg, age_patient)
            if res_mor:
                recommandations.append({"palier": "III", "medicament": "Morphine IV", **res_mor})

    return {
        "eva":              eva,
        "alertes_globales": alertes_globales,
        "recommandations":  recommandations,
        "objectif":         "EVA ≤ 3 en 30 min",
        "reevaluation":     "EVA à réévaluer 30 min après administration",
    }


# ==============================================================================
# [3] COMPOSANTS UI
# ==============================================================================



# ==============================================================================
# FEUILLE DE STYLE PRINCIPALE
# ==============================================================================

CSS_PRINCIPAL = """
<style>
/* ----------------------------------------------------------------
   POLICE & IMPORTS
---------------------------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap');

/* ----------------------------------------------------------------
   VARIABLES HOSPITALIÈRES — PALETTE #004A99
   Contraste WCAG AA minimum garanti pour environnement lumineux
---------------------------------------------------------------- */
:root {
    --bleu-hop:      #004A99;   /* bleu hospitalier principal */
    --bleu-clair:    #1A69B8;
    --bleu-pale:     #E8F1FB;
    --rouge-crit:    #C62828;   /* urgence critique */
    --rouge-pale:    #FDECEA;
    --orange-alerte: #E65100;
    --orange-pale:   #FFF3E0;
    --vert-ok:       #1B5E20;
    --vert-pale:     #E8F5E9;
    --violet-tri:    #4A148C;
    --violet-pale:   #F3E5F5;
    --fond:          #F4F6F9;   /* fond gris hospitalier */
    --fond-carte:    #FFFFFF;
    --fond-input:    #F8FAFC;
    --bord:          #C5CDD6;
    --bord-focus:    #004A99;
    --txt-principal: #0D1B2A;   /* contraste élevé sur blanc */
    --txt-secondaire:#2C3E50;
    --txt-aide:      #546E7A;
    --txt-blanc:     #FFFFFF;
    --ombre:         0 2px 8px rgba(0,74,153,0.12);
    --ombre-hov:     0 4px 16px rgba(0,74,153,0.22);
}

/* ----------------------------------------------------------------
   BASE
---------------------------------------------------------------- */
html, body, [class*="st-"] {
    font-family: 'IBM Plex Sans', system-ui, -apple-system, sans-serif;
    font-size: 15px;
    color: var(--txt-principal);
    background-color: var(--fond);
    -webkit-font-smoothing: antialiased;
}

/* ----------------------------------------------------------------
   EN-TÊTE APPLICATION
---------------------------------------------------------------- */
.app-header {
    background: linear-gradient(135deg, var(--bleu-hop) 0%, var(--bleu-clair) 100%);
    border-radius: 10px;
    padding: 18px 24px;
    margin-bottom: 20px;
    box-shadow: var(--ombre);
}
.app-titre {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.0rem;
    font-weight: 600;
    color: var(--txt-blanc);
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.app-sous {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.82);
    margin-top: 4px;
}

/* ----------------------------------------------------------------
   SECTION SEPARATOR
---------------------------------------------------------------- */
.sec {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--bleu-hop);
    border-bottom: 2px solid var(--bleu-hop);
    padding-bottom: 5px;
    margin: 18px 0 10px 0;
}

/* ----------------------------------------------------------------
   CARTES GÉNÉRIQUES
---------------------------------------------------------------- */
.carte {
    background: var(--fond-carte);
    border: 1px solid var(--bord);
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 12px;
    box-shadow: var(--ombre);
}

/* ----------------------------------------------------------------
   NIVEAUX DE TRIAGE — couleurs haute visibilité
---------------------------------------------------------------- */
.tri-carte {
    border-radius: 10px;
    padding: 20px 24px;
    margin: 12px 0;
    text-align: center;
    box-shadow: var(--ombre-hov);
}
.tri-niveau {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.tri-detail {
    font-size: 0.82rem;
    margin-top: 6px;
    line-height: 1.5;
}

/* Couleurs par niveau */
.tri-M  { background: #1A0030; color: #E040FB; border: 2px solid #CE93D8; }
.tri-1  { background: #7F0000; color: #FFCDD2; border: 2px solid #EF9A9A; }
.tri-2  { background: #BF360C; color: #FFE0B2; border: 2px solid #FFCC80; }
.tri-3A { background: #0D47A1; color: #BBDEFB; border: 2px solid #90CAF9; }
.tri-3B { background: #01579B; color: #E3F2FD; border: 2px solid #81D4FA; }
.tri-4  { background: #1B5E20; color: #C8E6C9; border: 2px solid #A5D6A7; }
.tri-5  { background: #37474F; color: #ECEFF1; border: 2px solid #B0BEC5; }

/* Badge niveau inline */
.badge-tri {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 4px;
    letter-spacing: 0.06em;
}

/* ----------------------------------------------------------------
   NEWS2
---------------------------------------------------------------- */
.news2-val {
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 700;
    font-size: 1.2rem;
    padding: 8px 16px;
    border-radius: 6px;
    display: inline-block;
}
.news2-nul  { background: #E8F5E9; color: var(--vert-ok);       border: 1px solid #A5D6A7; }
.news2-bas  { background: #E8F5E9; color: var(--vert-ok);       border: 1px solid #A5D6A7; }
.news2-moy  { background: var(--orange-pale); color: var(--orange-alerte); border: 1px solid #FFCC80; }
.news2-haut { background: var(--rouge-pale);  color: var(--rouge-crit);    border: 1px solid #EF9A9A; }
.news2-crit { background: #7F0000; color: #FFCDD2; border: 2px solid #EF9A9A; }

/* ----------------------------------------------------------------
   ALERTES CLINIQUES
---------------------------------------------------------------- */
.al-crit {
    background: var(--rouge-pale);
    border-left: 5px solid var(--rouge-crit);
    border-radius: 4px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.84rem;
    color: var(--rouge-crit);
    font-weight: 600;
}
.al-warn {
    background: var(--orange-pale);
    border-left: 5px solid var(--orange-alerte);
    border-radius: 4px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.84rem;
    color: var(--orange-alerte);
}
.al-ok {
    background: var(--vert-pale);
    border-left: 5px solid var(--vert-ok);
    border-radius: 4px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.84rem;
    color: var(--vert-ok);
}
.al-info {
    background: var(--bleu-pale);
    border-left: 5px solid var(--bleu-hop);
    border-radius: 4px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.84rem;
    color: var(--bleu-hop);
}

/* ----------------------------------------------------------------
   BANNIÈRE PURPURA FULMINANS
---------------------------------------------------------------- */
.banniere-crit {
    background: var(--rouge-crit);
    border-radius: 8px;
    padding: 16px 20px;
    margin: 10px 0;
    animation: pulse-alerte 1.5s ease-in-out infinite;
}
.banniere-crit-titre {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.0rem;
    font-weight: 700;
    color: #FFCDD2;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.banniere-crit-detail {
    font-size: 0.84rem;
    color: #FFECEC;
    line-height: 1.6;
}
@keyframes pulse-alerte {
    0%   { box-shadow: 0 0 0 0 rgba(198, 40, 40, 0.5); }
    70%  { box-shadow: 0 0 0 10px rgba(198, 40, 40, 0); }
    100% { box-shadow: 0 0 0 0 rgba(198, 40, 40, 0); }
}

/* ----------------------------------------------------------------
   DOSES PHARMACOLOGIQUES
---------------------------------------------------------------- */
.dose-carte {
    background: var(--fond-carte);
    border: 1px solid var(--bord);
    border-left: 5px solid var(--bleu-hop);
    border-radius: 6px;
    padding: 14px 18px;
    margin: 8px 0;
    box-shadow: var(--ombre);
    font-size: 0.84rem;
    line-height: 1.7;
    color: var(--txt-secondaire);
}
.dose-titre {
    font-weight: 700;
    font-size: 0.9rem;
    color: var(--bleu-hop);
    margin-bottom: 4px;
}
.dose-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--txt-principal);
    margin: 6px 0;
}

/* ----------------------------------------------------------------
   CONSTANTES VITALES — BADGES
---------------------------------------------------------------- */
.bv {
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 700;
    font-size: 0.9rem;
    padding: 3px 10px;
    border-radius: 4px;
    display: inline-block;
    margin: 2px;
}
.bv-n { background: var(--vert-pale);    color: var(--vert-ok);      border: 1px solid #A5D6A7; }
.bv-w { background: var(--orange-pale);  color: var(--orange-alerte); border: 1px solid #FFCC80; }
.bv-c { background: var(--rouge-pale);   color: var(--rouge-crit);   border: 1px solid #EF9A9A; }
.bv-o { background: var(--bleu-pale);    color: var(--bleu-hop);     border: 1px solid #90CAF9; }

/* ----------------------------------------------------------------
   SCORES DE TRIAGE (sv = score-valeur)
---------------------------------------------------------------- */
.sv-haut { color: var(--rouge-crit); font-weight: 700; }
.sv-moy  { color: var(--orange-alerte); font-weight: 700; }
.sv-bas  { color: var(--vert-ok); }

/* ----------------------------------------------------------------
   BARRE DE PROGRESSION — DÉLAIS
---------------------------------------------------------------- */
.prog-fond { background: #E0E7EF; border-radius: 4px; height: 8px; margin: 6px 0; }
.prog-fill { border-radius: 4px; height: 8px; transition: width 0.4s ease; }

/* ----------------------------------------------------------------
   HISTORIQUE PATIENTS
---------------------------------------------------------------- */
.hist-ligne {
    border-radius: 5px;
    padding: 10px 14px;
    margin: 4px 0;
    font-size: 0.82rem;
    border-left: 4px solid var(--bord);
    background: var(--fond-carte);
    color: var(--txt-secondaire);
}
.hist-M  { border-left-color: #CE93D8; background: #F3E5F5; }
.hist-1  { border-left-color: #EF9A9A; background: #FFEBEE; }
.hist-2  { border-left-color: #FFCC80; background: #FFF8E1; }
.hist-3A { border-left-color: #90CAF9; background: #E3F2FD; }
.hist-3B { border-left-color: #81D4FA; background: #E1F5FE; }
.hist-4  { border-left-color: #A5D6A7; background: #F1F8E9; }
.hist-5  { border-left-color: var(--bord); background: var(--fond); }

/* ----------------------------------------------------------------
   RÉÉVALUATIONS
---------------------------------------------------------------- */
.reeval-ligne   { border-radius:4px;padding:8px 14px;margin:3px 0;font-size:0.82rem; }
.reeval-aggrav  { background:#FFEBEE;border-left:4px solid var(--rouge-crit);color:var(--rouge-crit); }
.reeval-amelio  { background:var(--vert-pale);border-left:4px solid var(--vert-ok);color:var(--vert-ok); }
.reeval-stable  { background:var(--bleu-pale);border-left:4px solid var(--bleu-hop);color:var(--bleu-hop); }
.td-h { color:var(--rouge-crit);font-weight:700; }
.td-b { color:var(--vert-ok);font-weight:700; }
.td-e { color:var(--txt-aide); }

/* ----------------------------------------------------------------
   DISCLAIMER
---------------------------------------------------------------- */
.disclaimer {
    background: #FAFAFA;
    border: 1px solid var(--bord);
    border-top: 3px solid var(--bleu-hop);
    border-radius: 6px;
    padding: 14px 18px;
    margin-top: 28px;
    font-size: 0.68rem;
    color: var(--txt-aide);
    line-height: 1.8;
}
.disclaimer-sig {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--bleu-hop);
    border-top: 1px solid var(--bord);
    padding-top: 8px;
    margin-top: 8px;
}

/* ----------------------------------------------------------------
   BOUTONS — GRANDE TAILLE (iPhone one-hand friendly)
---------------------------------------------------------------- */
.stButton > button {
    min-height: 48px;
    font-size: 0.92rem;
    font-weight: 600;
    border-radius: 6px;
}

/* ----------------------------------------------------------------
   CHRONO IAO
---------------------------------------------------------------- */
.chrono {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.0rem;
    font-weight: 700;
    text-align: center;
}
.chrono-lbl {
    font-size: 0.62rem;
    color: var(--txt-aide);
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 0.12em;
}

/* ----------------------------------------------------------------
   RESPONSIVE iPhone — viewport étroit
---------------------------------------------------------------- */
@media (max-width: 768px) {
    .tri-niveau            { font-size: 1.2rem; }
    .news2-val             { font-size: 1.0rem; }
    .dose-val              { font-size: 1.1rem; }
    .chrono                { font-size: 1.6rem; }
    .stButton > button     { min-height: 52px !important; font-size: 1.0rem !important; }
    .stNumberInput input   { font-size: 1.1rem !important; min-height: 44px !important; }
    .stSelectbox select    { font-size: 1.0rem !important; min-height: 44px !important; }
    .app-titre             { font-size: 0.88rem; }
}
</style>
"""

# Meta tag iPhone WebApp — apple-touch-icon + status bar
META_IPHONE = """
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="AKIR-IAO">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<link rel="apple-touch-icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='22' fill='%23004A99'/%3E%3Ctext y='.9em' font-size='80' x='10'%3E%2B%3C/text%3E%3C/svg%3E">
"""


# ==============================================================================
# FONCTIONS DE RENDU UI
# ==============================================================================

def injecter_css() -> None:
    """Injecte la feuille de style principale et les meta tags iPhone."""
    st.markdown(CSS_PRINCIPAL, unsafe_allow_html=True)
    st.markdown(f"<head>{META_IPHONE}</head>", unsafe_allow_html=True)


def ui_entete(version: str = "v17.1") -> None:
    """Affiche l'en-tête institutionnel de l'application."""
    st.markdown(
        f'<div class="app-header">'
        f'<div class="app-titre">AKIR-IAO — Aide au Triage Infirmier {version}</div>'
        f'<div class="app-sous">'
        f'FRENCH Triage SFMU V1.1  |  Hainaut, Wallonie, Belgique  |  '
        f'Ismail Ibn-Daifa  |  RGPD — Aucun nom stocké'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def ui_sec(titre: str) -> None:
    """Séparateur de section avec style hospitalier."""
    st.markdown(f'<div class="sec">{titre}</div>', unsafe_allow_html=True)


def ui_alerte(msg: str, niveau: str = "crit") -> None:
    """
    Affiche une alerte clinique.
    Niveaux : "crit" (rouge) | "warn" (orange) | "ok" (vert) | "info" (bleu)
    """
    css = {"crit": "al-crit", "warn": "al-warn", "ok": "al-ok", "info": "al-info"}
    st.markdown(
        f'<div class="{css.get(niveau, "al-info")}">{msg}</div>',
        unsafe_allow_html=True,
    )


def ui_banniere_purpura(details: dict) -> None:
    """
    Bannière critique purpura fulminans — Tri 1 transversal.
    Déclenche une animation de pulsation rouge pour attirer l'attention.
    Référence : SPILF / SFP — Purpura fulminans 2017.
    """
    if details and details.get("purpura"):
        st.markdown(
            '<div class="banniere-crit">'
            '<div class="banniere-crit-titre">'
            'PURPURA FULMINANS — TRI 1 IMMEDIAT'
            '</div>'
            '<div class="banniere-crit-detail">'
            'Ceftriaxone 2 g IV (ou IM si VVP impossible) — NE PAS ATTENDRE le bilan.<br>'
            'Appel médecin senior immédiat — Transfert déchocage.'
            '</div></div>',
            unsafe_allow_html=True,
        )


def ui_banniere_news2(news2: int) -> None:
    """Bannière critique si NEWS2 >= 7."""
    if news2 >= 9:
        st.markdown(
            '<div class="banniere-crit">'
            '<div class="banniere-crit-titre">'
            f'NEWS2 {news2} — ENGAGEMENT VITAL — APPEL MÉDICAL IMMÉDIAT'
            '</div>'
            '<div class="banniere-crit-detail">'
            'Transfert déchocage — Médecin au chevet sans délai.'
            '</div></div>',
            unsafe_allow_html=True,
        )
    elif news2 >= 7:
        ui_alerte(
            f"NEWS2 {news2} >= 7 — Risque critique — Appel médical immédiat.",
            "crit",
        )
    elif news2 >= 5:
        ui_alerte(
            f"NEWS2 {news2} >= 5 — Risque élevé — Réévaluation toutes les 30 min.",
            "warn",
        )


def ui_carte_triage(niveau: str, label: str, secteur: str, justif: str, news2: int) -> None:
    """Affiche la carte de résultat de triage."""
    css = {
        "M": "tri-M", "1": "tri-1", "2": "tri-2",
        "3A": "tri-3A", "3B": "tri-3B", "4": "tri-4", "5": "tri-5",
    }.get(niveau, "tri-5")
    st.markdown(
        f'<div class="tri-carte {css}">'
        f'<div class="tri-niveau">{label}</div>'
        f'<div class="tri-detail">'
        f'NEWS2 {news2}  |  {justif}<br>'
        f'<small>{secteur}</small>'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def ui_constante(label: str, valeur, unite: str = "", niveau: str = "n") -> None:
    """Affiche une constante vitale avec code couleur."""
    css = {"n": "bv-n", "w": "bv-w", "c": "bv-c", "o": "bv-o"}.get(niveau, "bv-n")
    st.markdown(
        f'<span class="bv {css}">{label} : {valeur} {unite}</span>',
        unsafe_allow_html=True,
    )


def ui_dose_carte(
    titre: str,
    valeur: str,
    lignes: list[str],
    reference: str,
    couleur_bord: str = "var(--bleu-hop)",
    alertes: Optional[list[str]] = None,
) -> None:
    """Affiche une carte de dose pharmacologique."""
    if alertes:
        for al in alertes:
            ui_alerte(al, "crit")
    lignes_html = "<br>".join(lignes)
    st.markdown(
        f'<div class="dose-carte" style="border-left-color:{couleur_bord};">'
        f'<div class="dose-titre" style="color:{couleur_bord};">{titre}</div>'
        f'<div class="dose-val">{valeur}</div>'
        f'{lignes_html}<br>'
        f'<small style="color:var(--txt-aide);">{reference}</small>'
        f'</div>',
        unsafe_allow_html=True,
    )


def ui_score_box(
    label: str,
    score: int,
    interpretation: str,
    css_class: str = "sv-bas",
) -> None:
    """Affiche un score clinique avec interprétation."""
    st.markdown(
        f'<div class="carte">'
        f'<div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.12em;'
        f'color:var(--txt-aide);margin-bottom:4px;">{label}</div>'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:1.6rem;font-weight:700;">'
        f'{score}</div>'
        f'<div class="{css_class}" style="font-size:0.82rem;margin-top:4px;">'
        f'{interpretation}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def ui_news2_carte(label: str, css: str) -> None:
    """Affiche le score NEWS2 avec son code couleur."""
    st.markdown(
        f'<span class="news2-val {css}">{label}</span>',
        unsafe_allow_html=True,
    )


def ui_disclaimer() -> None:
    """Affiche le bandeau juridique de non-responsabilité."""
    st.markdown(
        '<div class="disclaimer">'
        'AKIR-IAO est un outil d\'aide à la décision clinique. '
        'Il ne se substitue pas au jugement clinique du médecin responsable de la prise en charge. '
        'Toute décision thérapeutique reste sous la responsabilité exclusive du professionnel de santé. '
        'Les doses affichées sont conformes au BCFI (Répertoire Commenté des Médicaments, Belgique) '
        'et doivent être validées par un médecin prescripteur avant administration.<br>'
        'RGPD : aucun nom ni prénom n\'est collecté. Identifiant UUID anonyme uniquement. '
        'Données stockées localement — aucune transmission à des tiers.<br>'
        '<div class="disclaimer-sig">'
        'AKIR-IAO Project — Ismail Ibn-Daifa — FRENCH Triage SFMU V1.1 — Wallonie, Belgique<br>'
        'AR 18/06/1990 modifié — Responsabilité infirmière — '
        'Hainaut, Wallonie, Belgique'
        '</div></div>',
        unsafe_allow_html=True,
    )


def ui_sbar_rendu(texte_sbar: str) -> None:
    """Affiche le rapport SBAR avec options d'export."""
    st.text_area(
        "Rapport SBAR — DPI-Ready",
        value=texte_sbar,
        height=400,
        key="sbar_display",
    )
    st.download_button(
        label="Télécharger le rapport SBAR (.txt)",
        data=texte_sbar,
        file_name="rapport_sbar_akir.txt",
        mime="text/plain",
        use_container_width=True,
    )


def ui_chrono(secondes: float) -> None:
    """Affiche un chronomètre formaté."""
    m, s = divmod(int(secondes), 60)
    h, m = divmod(m, 60)
    if h > 0:
        texte = f"{h:02d}:{m:02d}:{s:02d}"
    else:
        texte = f"{m:02d}:{s:02d}"
    couleur = (
        "var(--rouge-crit)"   if secondes > 600
        else "var(--orange-alerte)" if secondes > 300
        else "var(--vert-ok)"
    )
    st.markdown(
        f'<div class="chrono" style="color:{couleur};">{texte}</div>'
        f'<div class="chrono-lbl">Temps depuis l\'arrivée</div>',
        unsafe_allow_html=True,
    )


def ui_reeval_ligne(snap: dict, prev: dict, index: int) -> None:
    """
    Affiche une ligne d'historique de réévaluation avec tendance NEWS2.
    snap et prev sont des dicts avec clés : heure, fc, pas, spo2, fr, gcs, temp, niveau, news2.
    """

    ORD = ORD_NIV
    no  = ORD.get(snap.get("niveau", "5"), 5)
    np_ = ORD.get(prev.get("niveau", "5"), 5)

    if   no < np_: css, tend = "reeval-aggrav",  "AGGRAVATION"
    elif no > np_: css, tend = "reeval-amelio",  "AMELIORATION"
    else:          css, tend = "reeval-stable",  "STABLE"

    lbl = "H0" if index == 0 else f"H+{index}"

    def td(old, new, hg=True):
        if   new > old: sym, c = "+", ("td-h" if hg else "td-b")
        elif new < old: sym, c = "-", ("td-b" if hg else "td-h")
        else:           sym, c = "=", "td-e"
        return f'<span class="{c}">{sym}</span>'

    st.markdown(
        f'<div class="reeval-ligne {css}">'
        f'<b>{snap.get("heure","?")} ({lbl})</b>  |  '
        f'Tri {snap.get("niveau","?")}  |  '
        f'NEWS2 {snap.get("news2","?")}  |  '
        f'FC {snap.get("fc","?")} {td(prev.get("fc",80), snap.get("fc",80))}  |  '
        f'PAS {snap.get("pas","?")} {td(prev.get("pas",120), snap.get("pas",120), False)}  |  '
        f'SpO2 {snap.get("spo2","?")} {td(prev.get("spo2",98), snap.get("spo2",98), False)}  |  '
        f'<b>{tend}</b>'
        f'</div>',
        unsafe_allow_html=True,
    )


def ui_barre_progression(pct: float, couleur: str = "var(--bleu-hop)") -> None:
    """Affiche une barre de progression."""
    pct = max(0.0, min(100.0, pct))
    st.markdown(
        f'<div class="prog-fond">'
        f'<div class="prog-fill" style="width:{pct}%;background:{couleur};"></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def ui_glycemie_widget(
    key: str,
    label: str = "Glycémie capillaire (mg/dl)",
    glycemie_critique: int = 54,
    glycemie_moderee: int = 70,
) -> Optional[float]:
    """
    Widget glycémie avec conversion mmol/l automatique.
    Retourne None si la valeur est 0 (non mesurée) — sécurité protocoles glucose.
    Référence seuils : GLYCEMIE dict dans core_logic.py.
    """

    valeur = st.number_input(label, min_value=0, max_value=1500, value=0, step=5, key=key)
    if valeur == 0:
        st.caption("Glycémie non mesurée — saisir 0 si non réalisée.")
        return None

    mmol = mgdl_vers_mmol(valeur)
    st.caption(f"Référence : {mmol} mmol/l")

    if valeur < glycemie_critique:
        ui_alerte(
            f"HYPOGLYCÉMIE SÉVÈRE : {valeur} mg/dl ({mmol} mmol/l) "
            "— Glucose 30 % IV immédiat.",
            "crit",
        )
    elif valeur < glycemie_moderee:
        ui_alerte(f"Hypoglycémie modérée : {valeur} mg/dl ({mmol} mmol/l).", "warn")

    return float(valeur)


def ui_dyspnee_bpco_widget(key_prefix: str = "dysp") -> tuple[bool, bool]:
    """
    Widget dyspnée avec détection BPCO pour adapter la cible SpO2.
    Retourne : (bpco_actif: bool, parole_ok: bool)
    BPCO actif → cible SpO2 88-92 % (Échelle 2 NEWS2)
    Standard   → cible SpO2 ≥ 95 %  (Échelle 1 NEWS2)
    """
    bpco = st.checkbox(
        "Patient BPCO connu ?",
        key=f"{key_prefix}_bpco",
        help="Active l'échelle 2 NEWS2 (cible SpO2 88-92 %) et l'alerte hyperoxie"
    )
    if bpco:
        ui_alerte(
            "BPCO — Cible SpO2 : 88-92 %. "
            "Éviter la normoxie stricte (risque d'hypercapnie). "
            "Échelle 2 NEWS2 activée.",
            "warn",
        )
    parole = st.radio(
        "Peut s'exprimer en phrases complètes ?",
        [True, False],
        format_func=lambda x: "Oui — phrases complètes" if x else "Non — mots isolés ou aphasique",
        horizontal=True,
        key=f"{key_prefix}_parole",
    )
    return bpco, parole


# ==============================================================================
# [4] APPLICATION STREAMLIT
# ==============================================================================


# --- Import modules locaux ---

# ==============================================================================
# CONFIGURATION STREAMLIT
# ==============================================================================

st.set_page_config(
    page_title="AKIR-IAO — Triage Infirmier",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# PERSISTANCE — FICHIERS JSON
# ==============================================================================

REGISTRE_FILE    = "akir_registre_anon.json"
ALERTES_FILE     = "akir_journal_alertes.json"
ANTALGIE_FILE    = "akir_antalgie_log.json"


def _charger_json(filepath: str) -> list:
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _sauvegarder_json(filepath: str, data: list) -> None:
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as exc:
        # Log silencieux — ne jamais planter l'UI sur une erreur de persistance
        _log_erreur(f"Erreur sauvegarde {filepath} : {exc}")


def _log_erreur(msg: str) -> None:
    """Journal d'erreurs technique — ne contient aucune donnée patient."""
    try:
        with open("akir_errors.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def ajouter_registre(donnees: dict) -> str:
    """
    Ajoute un patient au registre anonyme.
    RGPD : 0 identifiant nominal. UUID uniquement.
    """
    uid = str(uuid.uuid4())[:8].upper()
    entree = {
        "uid":              uid,
        "heure":            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "motif":            donnees.get("motif", ""),
        "categorie":        donnees.get("categorie", ""),
        "niveau":           donnees.get("niveau", ""),
        "news2":            donnees.get("news2", 0),
        "fc":               donnees.get("fc"),
        "pas":              donnees.get("pas"),
        "spo2":             donnees.get("spo2"),
        "fr":               donnees.get("fr"),
        "temp":             donnees.get("temp"),
        "gcs":              donnees.get("gcs"),
        "age_groupe":       donnees.get("age_groupe", "adulte"),
        "code_operateur":   donnees.get("code_operateur", "IAO"),
    }
    registre = _charger_json(REGISTRE_FILE)
    registre.insert(0, entree)
    _sauvegarder_json(REGISTRE_FILE, registre[:500])  # Conservation 500 derniers
    return uid


def enregistrer_antalgie(
    uid: str, medicament: str, dose: str, voie: str, eva_avant: int, code_operateur: str = "IAO"
) -> None:
    """Enregistre un acte d'antalgie dans le journal de traçabilité."""
    entree = {
        "uid":            uid,
        "heure":          datetime.now().strftime("%H:%M:%S"),
        "medicament":     medicament,
        "dose":           dose,
        "voie":           voie,
        "eva_avant":      eva_avant,
        "operateur":      code_operateur,
    }
    log = _charger_json(ANTALGIE_FILE)
    log.insert(0, entree)
    _sauvegarder_json(ANTALGIE_FILE, log[:1000])


def enregistrer_alerte(uid: str, news2: int, niveau: str, alertes: list, code_op: str = "IAO") -> None:
    """Enregistre une alerte clinique dans le journal des alertes."""
    entree = {
        "uid":        uid,
        "heure":      datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "news2":      news2,
        "niveau":     niveau,
        "alertes":    alertes,
        "operateur":  code_op,
    }
    journal = _charger_json(ALERTES_FILE)
    journal.insert(0, entree)
    _sauvegarder_json(ALERTES_FILE, journal[:500])


# ==============================================================================
# SESSION STATE — RGPD COMPLIANT
# ==============================================================================

DEFAULTS = {
    # Identité de session — UUID anonyme, jamais de nom
    "session_uid":          lambda: str(uuid.uuid4())[:8].upper(),
    "code_operateur":       "",
    "heure_arrivee":        None,
    "heure_premier_contact": None,
    "derniere_reeval":      None,
    # Patient courant
    "historique":           [],
    "histo_reeval":         [],
    "uid_patient_courant":  None,
    # Antalgie
    "uid_antalgie":         "",
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v() if callable(v) else v


# ==============================================================================
# INITIALISATION UI
# ==============================================================================

injecter_css()
ui_entete("v18")

# ==============================================================================
# SIDEBAR — PARAMÈTRES PATIENT
# ==============================================================================

with st.sidebar:
    ui_sec("Opérateur IAO")
    code_op = st.text_input(
        "Code opérateur (anonyme)",
        value=st.session_state.code_operateur,
        max_chars=10,
        key="sb_code_op",
        placeholder="ex: IAO01",
        help="Code anonyme — ne saisir ni nom ni prénom (RGPD)"
    )
    if code_op:
        st.session_state.code_operateur = code_op.upper()

    ui_sec("Chronomètre patient")
    col_chr1, col_chr2 = st.columns(2)
    if col_chr1.button("Arrivée", use_container_width=True):
        st.session_state.heure_arrivee = datetime.now()
        st.session_state.histo_reeval  = []
        st.session_state.historique    = []
    if col_chr2.button("Contact IAO", use_container_width=True):
        st.session_state.heure_premier_contact = datetime.now()

    if st.session_state.heure_arrivee:
        elapsed = (datetime.now() - st.session_state.heure_arrivee).total_seconds()
        ui_chrono(elapsed)
        st.caption(f"Arrivée : {st.session_state.heure_arrivee.strftime('%H:%M')}")
    else:
        st.info("Cliquer sur 'Arrivée' pour démarrer le chronomètre.")

    ui_sec("Paramètres patient")
    age      = st.number_input("Âge (années)", 0, 120, 45, key="sb_age")
    # Sous-champ mois pour nourrissons (âge = 0)
    if age == 0:
        age_mois = st.number_input("Âge en mois (nourrisson)", 0, 11, 3, key="sb_age_mois")
        age      = round(age_mois / 12.0, 4)
        if age_mois <= 1:
            ui_alerte("Nouveau-né — seuils FC/PAS nouveau-né appliqués.", "warn")
        else:
            ui_alerte(f"Nourrisson {age_mois} mois — seuils pédiatriques appliqués.", "info")

    poids_kg = st.number_input("Poids (kg)", 1, 250, 70, key="sb_poids")

    ui_sec("Antécédents")
    atcd = st.multiselect("Antécédents pertinents", LISTE_ATCD, key="sb_atcd")
    allergies = st.text_input("Allergies connues", key="sb_allergies", placeholder="ex: Pénicilline")
    o2_supp   = st.checkbox("O2 supplémentaire en cours", key="sb_o2")

    ui_sec("Session RGPD")
    st.caption(f"Session : {st.session_state.session_uid}")
    st.caption("Aucun nom collecté — UUID anonyme uniquement.")
    if st.button("Nouvelle session (reset)", use_container_width=True):
        for k, v in DEFAULTS.items():
            st.session_state[k] = v() if callable(v) else v
        st.rerun()


# ==============================================================================
# ONGLETS PRINCIPAUX
# ==============================================================================

ONGLETS = [
    "Tri Rapide",
    "Signes Vitaux",
    "Anamnèse",
    "Triage",
    "Scores",
    "Pharmacie",
    "Réévaluation",
    "Historique",
    "Rapport SBAR",
]
tabs = st.tabs(ONGLETS)
(t_rapide, t_vitaux, t_anamnese, t_triage, t_scores,
 t_pharma, t_reeval, t_histo, t_sbar) = tabs

# Variables partagées (initialisées avec valeurs sécurisées)
temp = fr = fc = pas = spo2 = gcs = news2 = None
motif = cat = ""
details: dict = {}
eva_sc = 0
niveau = justif = critere = ""

# ==============================================================================
# ONGLET 1 — TRI RAPIDE
# ==============================================================================

with t_rapide:
    ui_sec("Constantes vitales — Tri Rapide")
    c1, c2, c3 = st.columns(3)
    temp = c1.number_input("T° (°C)", 30.0, 45.0, 37.0, 0.1, key="r_temp")
    fc   = c2.number_input("FC (bpm)", 20, 220, 80, key="r_fc")
    pas  = c3.number_input("PAS (mmHg)", 40, 260, 120, key="r_pas")
    c4, c5, c6 = st.columns(3)
    spo2 = c4.number_input("SpO2 (%)", 50, 100, 98, key="r_spo2")
    fr   = c5.number_input("FR (/min)", 5, 60, 16, key="r_fr")
    gcs  = c6.number_input("GCS (3-15)", 3, 15, 15, key="r_gcs")

    # Shock Index
    si = calculer_shock_index(fc, pas)
    si_css = "bv-c" if si >= 1.0 else ("bv-w" if si >= 0.8 else "bv-o")
    st.markdown(
        f'Shock Index : <span class="bv {si_css}">{si}</span>',
        unsafe_allow_html=True,
    )

    # NEWS2
    news2, n2_warns = calculer_news2(fr, spo2, o2_supp, temp, pas, fc, gcs, "BPCO" in atcd)
    n2_label, n2_css = niveau_news2(news2)
    for w in n2_warns:
        ui_alerte(w, "warn")
    ui_news2_carte(n2_label, n2_css)

    ui_sec("Motif de recours")
    MOTIFS_RAPIDES = [
        "Douleur thoracique / SCA",
        "Dyspnée / insuffisance respiratoire",
        "AVC / Déficit neurologique",
        "Altération de conscience / Coma",
        "Traumatisme crânien",
        "Hypotension artérielle",
        "Tachycardie / tachyarythmie",
        "Fièvre",
        "Douleur abdominale",
        "Allergie / anaphylaxie",
        "Hypoglycémie",
        "État de mal épileptique / Convulsions",
        "Pédiatrie - Fièvre ≤ 3 mois",
        "Autre motif",
    ]
    motif = st.selectbox("Motif de recours", MOTIFS_RAPIDES, key="r_motif")
    cat   = "Tri rapide"
    eva_sc = int(st.select_slider(
        "EVA (0 = aucune douleur, 10 = maximale)",
        options=[str(i) for i in range(11)], value="0", key="r_eva",
    ))
    details = {"eva": eva_sc, "atcd": atcd}

    # Purpura — checkbox transversale présente aussi en mode Tri Rapide
    details["purpura"] = st.checkbox(
        "Purpura non effaçable à la pression (TEST DU VERRE OBLIGATOIRE)",
        key="r_purpura",
        help="Purpura fulminans — Tri 1 absolu — Ceftriaxone 2 g IV IMMÉDIAT",
    )
    if details.get("purpura"):
        ui_banniere_purpura(details)

    # Glycémie capillaire (désactive les protocoles glucose si vide)
    glycemie_rap = ui_glycemie_widget("r_glyc", label="Glycémie capillaire (mg/dl) — si disponible")
    if glycemie_rap:
        details["glycemie_mgdl"] = glycemie_rap

    # Dyspnée — cible SpO2 BPCO
    if motif == "Dyspnée / insuffisance respiratoire":
        bpco_dysp, parole_ok = ui_dyspnee_bpco_widget("r_dysp")
        details["bpco_dyspnee"] = bpco_dysp
        details["parole_ok"]    = parole_ok
        # Recalculer NEWS2 avec BPCO si coché
        if bpco_dysp:
            news2, n2_warns = calculer_news2(
                fr, spo2, o2_supp, temp, pas, fc, gcs, bpco=True
            )

    if st.button("Calculer le niveau de triage", type="primary", use_container_width=True):
        niv_r, just_r, crit_r = french_triage(
            motif, details, fc, pas, spo2, fr, gcs, temp, age, news2,
            glycemie_mgdl=glycemie_rap,
        )
        ui_banniere_news2(news2)
        ui_banniere_purpura(details)
        ui_carte_triage(niv_r, LABELS_TRI[niv_r], SECTEURS_TRI[niv_r], just_r, news2)

        # Vérification de cohérence
        danger, attention, _ = verifier_coherence(
            fc, pas, spo2, fr, gcs, temp, eva_sc, motif, atcd, details, news2, glycemie_rap
        )
        for d in danger:
            ui_alerte(d, "crit")
        for a in attention:
            ui_alerte(a, "warn")


# ==============================================================================
# ONGLET 2 — SIGNES VITAUX
# ==============================================================================

with t_vitaux:
    ui_sec("Paramètres vitaux complets")
    v1, v2, v3 = st.columns(3)
    temp = v1.number_input("Température (°C)", 30.0, 45.0, 37.0, 0.1, key="v_temp")
    fc   = v1.number_input("FC (bpm)", 20, 220, 80, key="v_fc")
    pas  = v2.number_input("PAS (mmHg)", 40, 260, 120, key="v_pas")
    spo2 = v2.number_input("SpO2 (%)", 50, 100, 98, key="v_spo2")
    fr   = v3.number_input("FR (/min)", 5, 60, 16, key="v_fr")

    ui_sec("Glasgow Coma Scale")
    g1, g2, g3 = st.columns(3)
    gcs_y = g1.selectbox("Ouverture des yeux (Y)", [4, 3, 2, 1],
        format_func=lambda x: {4:"4 — Spontanée",3:"3 — À la demande",
                                2:"2 — À la douleur",1:"1 — Aucune"}[x], key="v_gcs_y")
    gcs_v = g2.selectbox("Réponse verbale (V)", [5, 4, 3, 2, 1],
        format_func=lambda x: {5:"5 — Orientée",4:"4 — Confuse",
                                3:"3 — Mots",2:"2 — Sons",1:"1 — Aucune"}[x], key="v_gcs_v")
    gcs_m = g3.selectbox("Réponse motrice (M)", [6, 5, 4, 3, 2, 1],
        format_func=lambda x: {6:"6 — Obéit",5:"5 — Localise",
                                4:"4 — Évitement",3:"3 — Flexion",
                                2:"2 — Extension",1:"1 — Aucune"}[x], key="v_gcs_m")
    gcs, _ = calculer_gcs(gcs_y, gcs_v, gcs_m)
    st.metric("Score GCS", f"{gcs} / 15")

    ui_sec("Scores de surveillance")
    news2, n2_warns = calculer_news2(fr, spo2, o2_supp, temp, pas, fc, gcs, "BPCO" in atcd)
    n2_label, n2_css = niveau_news2(news2)
    for w in n2_warns:
        ui_alerte(w, "warn")
    ci1, ci2 = st.columns(2)
    with ci1:
        ui_news2_carte(n2_label, n2_css)
    with ci2:
        si = calculer_shock_index(fc, pas)
        si_css = "bv-c" if si >= 1.0 else ("bv-w" if si >= 0.8 else "bv-o")
        st.markdown(f'Shock Index : <span class="bv {si_css}">{si}</span>', unsafe_allow_html=True)

    # SIPA si patient pédiatrique
    if age < 18:
        sipa_val, sipa_interp = calculer_sipa(fc, age)
        ui_alerte(sipa_interp, "crit" if "Choc" in sipa_interp else "info")

    # Bannières de sécurité
    ui_banniere_news2(news2)

    # Interprétation NEWS2 par item
    _interp = {
        0: ("Risque faible",     "news2-bas"),
        5: ("Risque modéré",     "news2-moy"),
        7: ("Risque élevé",      "news2-haut"),
        9: ("Risque critique",   "news2-crit"),
    }
    seuil, (ti, di) = max(
        ((s, v) for s, v in _interp.items() if news2 >= s),
        key=lambda x: x[0],
        default=(0, ("Risque faible", "news2-bas")),
    )
    ci1.markdown(f"**{ti}**  —  {di}")
    ui_disclaimer()


# ==============================================================================
# ONGLET 3 — ANAMNÈSE
# ==============================================================================

with t_anamnese:
    # Sécurisation si onglet signes vitaux non visité
    if temp is None:
        temp = 37.0; fc = 80; pas = 120; spo2 = 98; fr = 16; gcs = 15

    ui_sec("Évaluation de la douleur")
    douleur_eva = st.select_slider(
        "EVA — Intensité douloureuse (0 = aucune, 10 = maximale)",
        options=[str(i) for i in range(11)], value="0", key="an_eva"
    )
    eva_sc = int(douleur_eva)

    ui_sec("Motif de recours principal")
    MOTIFS_PAR_CAT = {
        "Cardio-circulatoire": [
            "Arrêt cardio-respiratoire", "Hypotension artérielle",
            "Douleur thoracique / SCA", "Tachycardie / tachyarythmie",
            "Bradycardie / bradyarythmie", "Palpitations", "Hypertension artérielle",
            "Allergie / anaphylaxie",
        ],
        "Respiratoire": [
            "Dyspnée / insuffisance respiratoire", "Dyspnée / insuffisance cardiaque",
        ],
        "Digestif": [
            "Douleur abdominale", "Vomissements / Diarrhée", "Hématémèse / Rectorragie",
        ],
        "Neurologie": [
            "AVC / Déficit neurologique", "Traumatisme crânien",
            "Altération de conscience / Coma", "Céphalée",
            "État de mal épileptique / Convulsions", "Syndrome confusionnel", "Malaise",
        ],
        "Traumatologie": [
            "Traumatisme du thorax / abdomen / rachis cervical",
            "Traumatisme du bassin / hanche / fémur",
            "Traumatisme d'un membre / épaule",
        ],
        "Infectiologie": ["Fièvre"],
        "Pédiatrie": ["Pédiatrie - Fièvre ≤ 3 mois"],
        "Peau": ["Pétéchie / Purpura", "Écchymose / Hématome spontané", "Érythème étendu / Éruption cutanée"],
        "Gynécologie": [
            "Accouchement imminent",
            "Complication de grossesse (1er / 2ème trimestre)",
            "Complication de grossesse (3ème trimestre)",
            "Ménorragie / Métrorragie",
        ],
        "Métabolique": ["Hypoglycémie", "Hyperglycémie / Cétoacidose diabétique"],
        "Divers": ["Renouvellement ordonnance", "Examen administratif / Certificat"],
    }
    cat   = st.selectbox("Catégorie clinique", list(MOTIFS_PAR_CAT.keys()), key="an_cat")
    motif = st.selectbox("Motif principal", MOTIFS_PAR_CAT[cat], key="an_motif")

    # Purpura transversal — présent sur tous les motifs
    ui_sec("Alerte transversale")
    details["purpura"] = st.checkbox(
        "Purpura non effaçable à la pression (test du verre)",
        key="an_purpura",
        help="Purpura fulminans — Tri 1 absolu — Ceftriaxone 2 g IV IMMÉDIAT",
    )
    if details.get("purpura"):
        ui_banniere_purpura(details)

    # Questions spécifiques par motif
    ui_sec("Questions discriminantes FRENCH")

    if motif == "Douleur thoracique / SCA":
        details["ecg"]           = st.selectbox("ECG", ["Normal", "Anormal typique SCA", "Anormal non typique"])
        details["douleur_type"]  = st.selectbox("Type de douleur", ["Atypique", "Typique persistante/intense", "Type coronaire"])
        frcv_c = st.columns(4)
        frcv_v = [
            frcv_c[0].checkbox("HTA",             key="frcv_hta",  value="HTA" in atcd),
            frcv_c[1].checkbox("Diabète",          key="frcv_diab", value=any("Diabete" in a or "Diabète" in a for a in atcd)),
            frcv_c[2].checkbox("Tabagisme",        key="frcv_tab",  value="Tabagisme actif" in atcd),
            frcv_c[3].checkbox("ATCD coronarien",  key="frcv_atcd"),
        ]
        details["frcv_count"] = sum(frcv_v)

    elif motif == "Dyspnée / insuffisance respiratoire":
        bpco_d, parole_d = ui_dyspnee_bpco_widget("an_dysp")
        details["bpco_dyspnee"] = bpco_d
        details["parole_ok"]    = parole_d
        details["orthopnee"]    = st.checkbox("Orthopnée", key="an_orth")
        details["tirage"]       = st.checkbox("Tirage intercostal / sus-sternal", key="an_tir")

    elif motif == "AVC / Déficit neurologique":
        details["délai_heures"]      = st.number_input("Délai depuis le début des symptômes (h)", 0.0, 72.0, 2.0, 0.5, key="an_delai")
        details["déficit_progressif"] = st.checkbox("Déficit neurologique progressif", key="an_defprog")
        details["fast"]               = st.checkbox("FAST positif (face, bras, langage)", key="an_fast")

    elif motif == "Traumatisme crânien":
        details["gcs_note"]        = gcs
        details["aod_avk"]         = st.checkbox("Sous anticoagulants / AOD", key="an_aod", value="Anticoagulants / AOD" in atcd)
        details["perte_conscience"] = st.checkbox("Perte de conscience initiale", key="an_pc")
        details["amnésie"]          = st.checkbox("Amnésie post-traumatique", key="an_amn")

    elif motif == "Pétéchie / Purpura":
        ui_alerte(
            "TEST DU VERRE OBLIGATOIRE — appuyer un verre transparent sur les taches. "
            "Si elles ne s'effacent PAS = purpura vasculaire = urgence absolue.", "warn"
        )
        details["non_effacable"]     = st.checkbox("Purpura NON effaçable au verre", key="an_noneff")
        details["etendu"]            = st.checkbox("Purpura étendu (plusieurs régions)", key="an_etendu")
        details["mauvaise_tolérance"] = st.checkbox("Mauvaise tolérance clinique", key="an_tol_peau")
        if details.get("non_effacable"):
            ui_banniere_purpura({"purpura": True})

    elif motif == "Fièvre":
        details["confusion"]          = st.checkbox("Confusion / altération de l'état mental", key="an_conf_fiev")
        details["mauvaise_tolérance"] = st.checkbox("Mauvaise tolérance clinique", key="an_tol_fiev")

    elif motif == "Hypoglycémie":
        glycemie_an = ui_glycemie_widget("an_glyc_hypo")
        if glycemie_an:
            details["glycemie_mgdl"] = glycemie_an

    elif motif == "Hyperglycémie / Cétoacidose diabétique":
        glycemie_hyper = ui_glycemie_widget("an_glyc_hyper")
        if glycemie_hyper:
            details["glycemie_mgdl"] = glycemie_hyper
        details["cetose_élevée"] = st.checkbox("Cétose élevée / cétoacidose confirmée", key="an_ceto")

    elif motif == "Altération de conscience / Coma":
        glycemie_coma = ui_glycemie_widget(
            "an_glyc_coma",
            label="Glycémie capillaire (mg/dl) — SYSTÉMATIQUE avant tout autre examen"
        )
        if glycemie_coma:
            details["glycemie_mgdl"] = glycemie_coma

    elif motif == "État de mal épileptique / Convulsions":
        details["crises_multiples"]         = st.checkbox("Crises multiples ou crise en cours", key="an_cris")
        details["confusion_post_critique"]  = st.checkbox("Confusion post-critique persistante", key="an_conf_cris")
        glycemie_conv = ui_glycemie_widget("an_glyc_conv", label="Glycémie capillaire (mg/dl) — cause curable")
        if glycemie_conv:
            details["glycemie_mgdl"] = glycemie_conv

    details["eva"] = eva_sc
    details["atcd"] = atcd


# ==============================================================================
# ONGLET 4 — TRIAGE
# ==============================================================================

with t_triage:
    if temp is None:
        temp = 37.0; fc = 80; pas = 120; spo2 = 98; fr = 16; gcs = 15
    if not motif:
        motif = "Fièvre"; cat = "Infectiologie"

    bpco_triage = "BPCO" in atcd or details.get("bpco_dyspnee", False)
    news2, n2_warns = calculer_news2(fr, spo2, o2_supp, temp, pas, fc, gcs, bpco_triage)
    for w in n2_warns:
        ui_alerte(w, "warn")

    gl_triage = details.get("glycemie_mgdl")
    niveau, justif, critere = french_triage(
        motif, details, fc, pas, spo2, fr, gcs, temp, age, news2, glycemie_mgdl=gl_triage
    )

    # Bannières de sécurité
    ui_banniere_news2(news2)
    ui_banniere_purpura(details)

    # Alerte réévaluation en retard
    if st.session_state.derniere_reeval:
        mins = (datetime.now() - st.session_state.derniere_reeval).total_seconds() / 60
        if mins > DELAIS_TRI.get(niveau, 60):
            ui_alerte(
                f"Réévaluation en retard : {int(mins)} min écoulées — "
                f"délai maximum {DELAIS_TRI[niveau]} min pour {LABELS_TRI[niveau]}",
                "crit"
            )

    # Résultat de triage
    ui_carte_triage(niveau, LABELS_TRI[niveau], SECTEURS_TRI[niveau], justif, news2)
    st.caption(f"Critère de triage : {critere}")

    # Vérification de cohérence
    danger, attention, _ = verifier_coherence(
        fc, pas, spo2, fr, gcs, temp, details.get("eva", 0),
        motif, atcd, details, news2, gl_triage
    )
    for d in danger:
        ui_alerte(d, "crit")
        enregistrer_alerte(
            st.session_state.uid_patient_courant or "ANON",
            news2, niveau, [d], st.session_state.code_operateur
        )
    for a in attention:
        ui_alerte(a, "warn")

    # Délai IAO
    if st.session_state.heure_arrivee and st.session_state.heure_premier_contact:
        delai_sec = (st.session_state.heure_premier_contact - st.session_state.heure_arrivee).total_seconds()
        delai_min = int(delai_sec / 60)
        cible_min = 10 if niveau in ("M", "1", "2") else 30
        delai_type = "crit" if delai_min >= cible_min else "ok"
        ui_alerte(
            f"Délai IAO : {delai_min} min — cible {cible_min} min pour {LABELS_TRI[niveau]} — "
            f"{'DÉPASSÉ' if delai_min >= cible_min else 'Dans les délais'}",
            delai_type
        )

    # Enregistrement
    if st.button("Enregistrer ce patient", use_container_width=True, type="primary"):
        age_groupe = "nourrisson" if age < 1 else ("enfant" if age < 18 else "adulte")
        uid = ajouter_registre({
            "motif": motif, "categorie": cat, "niveau": niveau,
            "news2": news2, "fc": fc, "pas": pas, "spo2": spo2,
            "fr": fr, "temp": temp, "gcs": gcs,
            "age_groupe": age_groupe,
            "code_operateur": st.session_state.code_operateur,
        })
        st.session_state.uid_patient_courant = uid
        st.session_state.histo_reeval = []
        st.session_state.derniere_reeval = datetime.now()
        st.session_state.historique.insert(0, {
            "uid": uid, "heure": datetime.now().strftime("%H:%M"),
            "motif": motif, "niveau": niveau, "news2": news2,
        })
        st.success(f"Patient enregistré — UID : {uid} — Tri {niveau}")

    ui_disclaimer()


# ==============================================================================
# ONGLET 5 — SCORES CLINIQUES
# ==============================================================================

with t_scores:
    ui_sec("qSOFA — Détection sepsis")
    qs, qpos, qw = calculer_qsofa(fr, gcs, pas)
    for w in qw:
        ui_alerte(w, "warn")
    interp_qs = "Sepsis probable — évaluation urgente" if qs >= 2 else "qSOFA faible — sepsis moins probable"
    ui_score_box("qSOFA", qs, interp_qs, "sv-haut" if qs >= 2 else "sv-bas")
    if qpos:
        for p in qpos:
            st.caption(f"  + {p}")

    ui_sec("FAST — Détection AVC")
    f1, f2, f3, f4 = st.columns(4)
    fast_face  = f1.checkbox("Face (paralysie faciale)",   key="fast_f")
    fast_bras  = f2.checkbox("Bras (déficit moteur)",      key="fast_a")
    fast_lang  = f3.checkbox("Langage (trouble aphasique)",key="fast_s")
    fast_debut = f4.checkbox("Début brutal",               key="fast_t")
    fs, fi, fa = evaluer_fast(fast_face, fast_bras, fast_lang, fast_debut)
    ui_score_box("FAST", fs, fi, "sv-haut" if fa else "sv-bas")

    ui_sec("TIMI — Risque SCA sans sus-décalage ST")
    t1, t2 = st.columns(2)
    t_age65    = t1.checkbox("Âge ≥ 65 ans",         key="ti_age",   value=age >= 65)
    t_frcv3    = t1.checkbox("≥ 3 FRCV",              key="ti_frcv")
    t_sten50   = t1.checkbox("Sténose coronaire ≥ 50 %", key="ti_sten")
    t_aspi7    = t2.checkbox("Aspirine dans les 7 j", key="ti_aspi")
    t_trop     = t2.checkbox("Troponine positive",    key="ti_trop")
    t_dst      = t2.checkbox("Déviation ST",          key="ti_dst")
    t_cris24   = t2.checkbox("≥ 2 crises en 24 h",   key="ti_cris")
    timi_sc, _ = calculer_timi(age, int(t_frcv3)*3, t_sten50, t_aspi7, t_trop, t_dst, int(t_cris24)*2)
    timi_interp = "Risque élevé" if timi_sc >= 5 else ("Risque intermédiaire" if timi_sc >= 3 else "Risque faible")
    ui_score_box("TIMI", timi_sc, timi_interp, "sv-haut" if timi_sc >= 5 else ("sv-moy" if timi_sc >= 3 else "sv-bas"))

    ui_sec("Algoplus — Douleur patient âgé non communicant")
    al1, al2, al3, al4, al5 = st.columns(5)
    alg_f  = al1.checkbox("Visage",         key="alg_f")
    alg_r  = al2.checkbox("Regard",         key="alg_r")
    alg_p  = al3.checkbox("Plaintes",       key="alg_p")
    alg_ac = al4.checkbox("Corps",          key="alg_ac")
    alg_co = al5.checkbox("Comportement",   key="alg_co")
    alg_sc, alg_int, alg_css, _ = calculer_algoplus(alg_f, alg_r, alg_p, alg_ac, alg_co)
    ui_score_box("Algoplus", alg_sc, alg_int, alg_css)

    ui_sec("Clinical Frailty Scale — Fragilité gériatrique")
    cfs_sc = st.slider("Score CFS (1-9)", 1, 9, 3, key="cfs_sc")
    st.caption(CFS_NIVEAUX.get(cfs_sc, ""))
    cfs_lab, cfs_css, cfs_rem = evaluer_cfs(cfs_sc)
    ui_score_box("CFS", cfs_sc, cfs_lab, cfs_css)
    if cfs_rem:
        ui_alerte("CFS ≥ 5 — Envisager une remontée du niveau de triage.", "warn")


# ==============================================================================
# ONGLET 6 — PHARMACIE
# ==============================================================================

with t_pharma:
    ui_sec("Antalgie basée sur l'EVA")
    eva_ph = st.slider("EVA actuelle", 0, 10, details.get("eva", 0), key="ph_eva")
    proto = protocole_antalgique_eva(eva_ph, poids_kg, age, atcd, details.get("glycemie_mgdl"))
    for al in proto["alertes_globales"]:
        ui_alerte(al, "crit")
    for rec in proto["recommandations"]:
        couleur = {"I": "#1B5E20", "II": "#E65100", "III": "#C62828"}.get(rec.get("palier","I"), "#004A99")
        lignes = [
            rec.get("admin", ""),
            rec.get("frequence", ""),
            rec.get("note", ""),
        ]
        ui_dose_carte(
            titre=f"Palier {rec.get('palier','?')} — {rec.get('medicament','')}",
            valeur=f"{rec.get('dose_g', rec.get('dose_mg','?'))} "
                   f"{'g' if 'dose_g' in rec else 'mg'}",
            lignes=[l for l in lignes if l],
            reference=rec.get("reference", "BCFI — Belgique"),
            couleur_bord=couleur,
            alertes=rec.get("alertes"),
        )

    ui_sec("Adrénaline IM — Choc anaphylactique")
    a_res, a_err = dose_adrenaline_anaphylaxie(poids_kg)
    if a_err:
        ui_alerte(a_err, "warn")
    else:
        ui_dose_carte(
            titre="Adrénaline IM (Sterop 1 mg/ml)",
            valeur=f"{a_res['dose_mg']} mg IM",
            lignes=[a_res["voie"], a_res["note"], a_res["répéter"], a_res["moniteur"]],
            reference=a_res["reference"],
            couleur_bord="var(--rouge-crit)",
        )

    ui_sec("Naloxone IV — Antidote opioïdes")
    dep_op = st.checkbox("Patient dépendant aux opioïdes (titration douce)", key="ph_dep")
    gl_ph  = details.get("glycemie_mgdl")
    nal_res, nal_err = dose_naloxone(poids_kg, age, dependance_opioides=dep_op)
    if nal_err:
        ui_alerte(nal_err, "warn")
    else:
        for al in nal_res.get("alertes", []):
            ui_alerte(al, "warn")
        ui_dose_carte(
            titre="Naloxone IV (Narcan)",
            valeur=f"{nal_res['dose_bolus']} mg / bolus",
            lignes=[nal_res["admin"], nal_res["note"], nal_res["surveillance"]],
            reference=nal_res["reference"],
            couleur_bord="#6A1B9A",
        )

    ui_sec("Glucose 30 % — Correction hypoglycémie")
    # Sécurité : désactivé si glycémie non mesurée
    g_res, g_err = dose_glucose_hypoglycemie(poids_kg, "IV", glycemie_mgdl=gl_ph)
    if g_err:
        ui_alerte(g_err, "warn")
    else:
        ui_dose_carte(
            titre="Glucose 30 % IV (Glucosie)",
            valeur=f"{g_res['dose_g']} g",
            lignes=[g_res["volume"], g_res["controle"]],
            reference=g_res["reference"],
        )

    ui_sec("Ceftriaxone IV — Urgence infectieuse")
    cef_res, cef_err = dose_ceftriaxone_iv(poids_kg, age)
    if cef_err:
        ui_alerte(cef_err, "warn")
    else:
        ui_dose_carte(
            titre="Ceftriaxone IV (Purpura fulminans / Méningite)",
            valeur=f"{cef_res['dose_g']} g IV",
            lignes=[cef_res["admin"], cef_res["note"], cef_res["indication"]],
            reference=cef_res["reference"],
            couleur_bord="var(--rouge-crit)",
        )

    ui_disclaimer()


# ==============================================================================
# ONGLET 7 — RÉÉVALUATION
# ==============================================================================

with t_reeval:
    ui_sec("Nouvelle réévaluation")
    if st.session_state.heure_arrivee and st.session_state.heure_premier_contact:
        delai_sec = (
            st.session_state.heure_premier_contact - st.session_state.heure_arrivee
        ).total_seconds()
        cible_m = 10 if niveau in ("M","1","2") else 30
        ui_alerte(
            f"Délai IAO : {int(delai_sec/60)} min — cible {cible_m} min",
            "ok" if delai_sec/60 < cible_m else "crit"
        )

    rr1, rr2, rr3 = st.columns(3)
    re_temp = rr1.number_input("T° (°C)", 30.0, 45.0, 37.0, 0.1, key="re_temp")
    re_fc   = rr1.number_input("FC (bpm)", 20, 220, 80, key="re_fc")
    re_pas  = rr2.number_input("PAS (mmHg)", 40, 260, 120, key="re_pas")
    re_spo2 = rr2.number_input("SpO2 (%)", 50, 100, 98, key="re_spo2")
    re_fr   = rr3.number_input("FR (/min)", 5, 60, 16, key="re_fr")
    re_gcs  = rr3.number_input("GCS (3-15)", 3, 15, 15, key="re_gcs")

    re_news2, _ = calculer_news2(re_fr, re_spo2, o2_supp, re_temp, re_pas, re_fc, re_gcs, "BPCO" in atcd)
    re_lbl, re_css = niveau_news2(re_news2)
    re_niv, re_just, _ = french_triage(motif or "Fièvre", details, re_fc, re_pas, re_spo2, re_fr, re_gcs, re_temp, age, re_news2)

    rc1, rc2 = st.columns(2)
    rc1.markdown(f'<span class="news2-val {re_css}">{re_lbl}</span>', unsafe_allow_html=True)
    rc2.info(f"Triage recalculé : **{LABELS_TRI[re_niv]}**")

    ui_banniere_news2(re_news2)

    # NEWS2 tendance — courbe barres
    if st.button("Enregistrer cette réévaluation", use_container_width=True):
        st.session_state.histo_reeval.append({
            "heure": datetime.now().strftime("%H:%M"),
            "fc": re_fc, "pas": re_pas, "spo2": re_spo2,
            "fr": re_fr, "gcs": re_gcs, "temp": re_temp,
            "niveau": re_niv, "news2": re_news2,
        })
        st.session_state.derniere_reeval = datetime.now()
        st.success(f"Réévaluation enregistrée — {datetime.now().strftime('%H:%M')} — Tri {re_niv}")

    ui_sec("Historique des réévaluations")
    if not st.session_state.histo_reeval:
        st.info("Aucune réévaluation enregistrée pour ce patient.")
    else:
        # Courbe NEWS2
        news2_vals = [s.get("news2", 0) for s in st.session_state.histo_reeval]
        max_n2 = max(news2_vals) if news2_vals else 1
        for i, (h, n2) in enumerate(
            zip([s["heure"] for s in st.session_state.histo_reeval], news2_vals)
        ):
            pct = round(n2 / max(max_n2, 1) * 100, 0)
            bar_col = "#C62828" if n2 >= 7 else ("#E65100" if n2 >= 5 else "#1B5E20")
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:10px;margin:3px 0;">'
                f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:.75rem;'
                f'width:64px;flex-shrink:0;">{h} (H+{i})</span>'
                f'<div style="flex:1;background:#E0E7EF;border-radius:3px;height:16px;">'
                f'<div style="background:{bar_col};width:{max(pct,4)}%;height:16px;border-radius:3px;"></div>'
                f'</div>'
                f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:.75rem;'
                f'width:24px;text-align:right;font-weight:700;">{n2}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Lignes détaillées
        for i, snap in enumerate(st.session_state.histo_reeval):
            prev = st.session_state.histo_reeval[i - 1] if i > 0 else snap
            ui_reeval_ligne(snap, prev, i)

        if len(st.session_state.histo_reeval) >= 2:
            first = st.session_state.histo_reeval[0]
            last  = st.session_state.histo_reeval[-1]
            st.markdown(
                f"**Bilan :** {len(st.session_state.histo_reeval)} réévaluations — "
                f"NEWS2 : {first.get('news2','?')} → {last.get('news2','?')} — "
                f"Tri : {first['niveau']} → {last['niveau']}"
            )


# ==============================================================================
# ONGLET 8 — HISTORIQUE
# ==============================================================================

with t_histo:
    if not st.session_state.historique:
        st.info("Aucun patient enregistré dans cette session.")
    else:
        st.metric("Patients triés cette session", len(st.session_state.historique))
        for p in st.session_state.historique:
            css_hist = {
                "M": "hist-M", "1": "hist-1", "2": "hist-2",
                "3A": "hist-3A", "3B": "hist-3B", "4": "hist-4", "5": "hist-5",
            }.get(p.get("niveau","5"), "hist-5")
            st.markdown(
                f'<div class="hist-ligne {css_hist}">'
                f'<b>{p.get("heure","?")} — UID : {p.get("uid","?")}</b>  |  '
                f'{p.get("motif","?")}  |  {LABELS_TRI.get(p.get("niveau","5"),"?")}  |  '
                f'NEWS2 {p.get("news2","?")}'
                f'</div>',
                unsafe_allow_html=True,
            )


# ==============================================================================
# ONGLET 9 — RAPPORT SBAR
# ==============================================================================

with t_sbar:
    ui_sec("Génération du rapport SBAR — Format DPI-Ready")
    sbar_op = st.text_input(
        "Code opérateur (pour le rapport)",
        value=st.session_state.code_operateur or "IAO",
        key="sbar_op",
    )
    if st.button("Générer le rapport SBAR", use_container_width=True, type="primary"):
        if not motif:
            ui_alerte("Veuillez d'abord sélectionner un motif de recours.", "warn")
        else:
            rapport = generer_sbar(
                age=age, motif=motif, cat=cat, atcd=atcd,
                allergies=allergies, o2_supp=o2_supp,
                temp=temp or 37.0, fc=fc or 80, pas=pas or 120,
                spo2=spo2 or 98, fr=fr or 16, gcs=gcs or 15,
                eva=details.get("eva", 0), news2=news2 or 0,
                niveau=niveau or "3B", justif=justif or "Non calculé",
                critere=critere or "", code_operateur=sbar_op,
                glycemie_mgdl=details.get("glycemie_mgdl"),
            )
            ui_sbar_rendu(rapport)

    ui_disclaimer()