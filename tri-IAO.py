"""
================================================================================
  AKIR-IAO PROJECT  -  v14.0  -  Hospital Pro Edition
  Developpeur : Ismail Ibn-Daifa
  Outil d'aide au triage infirmier - Service des Urgences
  Conformite : FRENCH Triage SFMU V1.1  |  BCFI Belgique  |  RGPD
  Localisation : Hainaut, Wallonie, Belgique
================================================================================

Architecture modulaire :
  [1] moteur_scores     : Calculs cliniques encapsules (NEWS2, GCS, TIMI, etc.)
  [2] moteur_pharmacie  : Doses BCFI, calculs debit perfusion, unites belges
  [3] moteur_triage     : Algorithme FRENCH Triage SFMU V1.1
  [4] moteur_sbar       : Generation transmission SBAR DPI-Ready
  [5] moteur_alertes    : Coherence clinique et securite
  [6] persistance       : Registre anonyme local (RGPD)
  [7] ui_composants     : Rendu Streamlit - couche affichage uniquement
  [8] application       : Point d'entree principal

Unites de reference (Belgique) :
  - Glycemie  : mg/dl  (1 mmol/l = 18 mg/dl)
  - Poids     : kg
  - Pression  : mmHg
  - Temperature : degres Celsius
================================================================================
"""

import streamlit as st
from datetime import datetime
import json
import os
import uuid

# ==============================================================================
# CONFIGURATION STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="AKIR-IAO Project",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==============================================================================
# [SECTION CSS] - DESIGN HOSPITAL PRO
# Palette : Blanc #FFFFFF | Gris clair #F8F9FA | Bleu hospitalier #004A99
# Alertes  : Rouge medical #D32F2F | Orange #F57C00 | Vert #2E7D32
# Typographie : DM Sans (corps) + DM Mono (valeurs numeriques/scores)
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ---- VARIABLES COULEURS ---- */
:root {
  --bleu-hosp:     #004A99;
  --bleu-clair:    #E8F0FB;
  --bleu-mid:      #1565C0;
  --fond-page:     #F4F6F9;
  --fond-carte:    #FFFFFF;
  --fond-sidebar:  #F0F4FA;
  --bordure:       #D0D7E3;
  --bordure-forte: #A0AABF;
  --texte-titre:   #0D1B2A;
  --texte-corps:   #2C3A4D;
  --texte-aide:    #5A6880;
  --rouge-crit:    #D32F2F;
  --rouge-fond:    #FFEBEE;
  --rouge-bord:    #EF9A9A;
  --orange-warn:   #F57C00;
  --orange-fond:   #FFF3E0;
  --orange-bord:   #FFCC80;
  --vert-ok:       #2E7D32;
  --vert-fond:     #E8F5E9;
  --vert-bord:     #A5D6A7;
  --violet-m:      #6A1B9A;
  --violet-fond:   #F3E5F5;
}

/* ---- BASE ---- */
html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
  color: var(--texte-corps);
}
.stApp {
  background: var(--fond-page);
}

/* ---- SIDEBAR ---- */
[data-testid='stSidebar'] {
  background: var(--fond-sidebar) !important;
  border-right: 1px solid var(--bordure);
}
[data-testid='stSidebar'] .stMarkdown { color: var(--texte-corps); }

/* ---- EN-TETE APPLICATION ---- */
.app-header {
  background: var(--bleu-hosp);
  color: #FFFFFF;
  padding: 14px 20px;
  border-radius: 6px;
  margin-bottom: 18px;
}
.app-header-title {
  font-size: 1.05rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.app-header-sub {
  font-size: 0.75rem;
  opacity: 0.82;
  margin-top: 3px;
  letter-spacing: 0.04em;
}

/* ---- SECTION HEADERS ---- */
.sec-header {
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--bleu-hosp);
  border-bottom: 1.5px solid var(--bleu-hosp);
  padding-bottom: 5px;
  margin: 18px 0 12px 0;
}

/* ---- CARTES TRIAGE ---- */
.tri-carte {
  border-radius: 6px;
  padding: 20px 22px;
  text-align: center;
  margin-bottom: 14px;
  border-left: 5px solid transparent;
}
.tri-M  { background: var(--violet-fond); border-color: var(--violet-m); }
.tri-1  { background: var(--rouge-fond);  border-color: var(--rouge-crit); }
.tri-2  { background: var(--orange-fond); border-color: var(--orange-warn); }
.tri-3A { background: #FFFDE7;            border-color: #F9A825; }
.tri-3B { background: #FFFDE7;            border-color: #FDD835; }
.tri-4  { background: var(--vert-fond);   border-color: var(--vert-ok); }
.tri-5  { background: var(--bleu-clair);  border-color: var(--bleu-hosp); }

.tri-niveau {
  font-family: 'DM Mono', monospace;
  font-size: 1.35rem;
  font-weight: 500;
  margin-bottom: 4px;
}
.tri-M  .tri-niveau { color: var(--violet-m);   }
.tri-1  .tri-niveau { color: var(--rouge-crit);  }
.tri-2  .tri-niveau { color: var(--orange-warn); }
.tri-3A .tri-niveau, .tri-3B .tri-niveau { color: #7B5E00; }
.tri-4  .tri-niveau { color: var(--vert-ok);     }
.tri-5  .tri-niveau { color: var(--bleu-hosp);   }
.tri-detail { font-size: 0.82rem; color: var(--texte-aide); margin-top: 6px; }

/* ---- SCORE NEWS2 ---- */
.news2-val {
  display: inline-block;
  font-family: 'DM Mono', monospace;
  font-size: 1.5rem;
  font-weight: 500;
  padding: 5px 16px;
  border-radius: 4px;
  margin-bottom: 4px;
}
.news2-bas    { background: var(--vert-fond);   color: var(--vert-ok);     border: 1px solid var(--vert-bord); }
.news2-moyen  { background: var(--orange-fond); color: var(--orange-warn); border: 1px solid var(--orange-bord); }
.news2-haut   { background: var(--rouge-fond);  color: #C62828;            border: 1px solid var(--rouge-bord); }
.news2-crit   { background: var(--rouge-crit);  color: #FFFFFF;            border: 1px solid var(--rouge-crit); }

/* ---- BANNIERE D'ALERTE CRITIQUE (NEWS2 >= 7) ---- */
.banniere-critique {
  background: var(--rouge-crit);
  color: #FFFFFF;
  border-radius: 4px;
  padding: 14px 18px;
  margin: 10px 0;
  border-left: 6px solid #7F0000;
}
.banniere-critique-titre {
  font-size: 0.92rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-bottom: 4px;
}
.banniere-critique-detail { font-size: 0.82rem; opacity: 0.92; }

/* ---- BANNIERE D'ALERTE STANDARD ---- */
.alerte-danger {
  background: var(--rouge-fond);
  border: 1px solid var(--rouge-bord);
  border-left: 4px solid var(--rouge-crit);
  border-radius: 4px;
  padding: 10px 14px;
  margin: 6px 0;
  color: #B71C1C;
  font-size: 0.85rem;
  font-weight: 500;
}
.alerte-attention {
  background: var(--orange-fond);
  border: 1px solid var(--orange-bord);
  border-left: 4px solid var(--orange-warn);
  border-radius: 4px;
  padding: 10px 14px;
  margin: 6px 0;
  color: #BF360C;
  font-size: 0.85rem;
}
.alerte-info {
  background: var(--bleu-clair);
  border: 1px solid #90CAF9;
  border-left: 4px solid var(--bleu-hosp);
  border-radius: 4px;
  padding: 10px 14px;
  margin: 6px 0;
  color: var(--bleu-hosp);
  font-size: 0.85rem;
}
.alerte-ok {
  background: var(--vert-fond);
  border: 1px solid var(--vert-bord);
  border-left: 4px solid var(--vert-ok);
  border-radius: 4px;
  padding: 10px 14px;
  margin: 6px 0;
  color: #1B5E20;
  font-size: 0.85rem;
}

/* ---- BADGE VITAL ---- */
.badge-vital {
  display: inline-block;
  font-family: 'DM Mono', monospace;
  font-size: 0.72rem;
  font-weight: 500;
  padding: 1px 6px;
  border-radius: 3px;
  margin-left: 5px;
  vertical-align: middle;
}
.badge-crit    { background: var(--rouge-fond); color: var(--rouge-crit); border: 1px solid var(--rouge-bord); }
.badge-warn    { background: var(--orange-fond); color: var(--orange-warn); border: 1px solid var(--orange-bord); }
.badge-ok      { background: var(--vert-fond); color: var(--vert-ok); border: 1px solid var(--vert-bord); }

/* ---- CARTE GENERIQUE ---- */
.carte {
  background: var(--fond-carte);
  border: 1px solid var(--bordure);
  border-radius: 6px;
  padding: 16px 18px;
  margin: 8px 0;
}
.carte-titre {
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--bleu-hosp);
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--bordure);
}
.carte-item {
  font-size: 0.85rem;
  color: var(--texte-corps);
  padding: 3px 0;
  border-bottom: 1px solid #F0F2F5;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}
.carte-item::before { content: "-"; color: var(--bleu-hosp); flex-shrink: 0; font-weight: 600; }
.carte-item:last-child { border-bottom: none; }
.carte-item-urgent::before { content: "!"; color: var(--rouge-crit); font-weight: 700; }

/* ---- PROTOCOLE ANTICIPE ---- */
.protocole-card {
  background: #EFF6FF;
  border: 1px solid #BFDBFE;
  border-left: 4px solid var(--bleu-hosp);
  border-radius: 4px;
  padding: 14px 16px;
  margin: 10px 0;
}
.protocole-titre {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--bleu-hosp);
  margin-bottom: 10px;
}
.protocole-item {
  font-size: 0.85rem;
  color: #1E3A5F;
  padding: 4px 0;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}
.protocole-item::before { content: "[ ]"; color: var(--bleu-hosp); font-family: 'DM Mono', monospace; font-size: 0.75rem; flex-shrink: 0; }
.protocole-item-urgent::before { content: "[!]"; color: var(--rouge-crit); font-family: 'DM Mono', monospace; font-size: 0.75rem; }

/* ---- SCORE RESULT ---- */
.score-val {
  display: inline-block;
  font-family: 'DM Mono', monospace;
  font-size: 1.6rem;
  font-weight: 500;
  padding: 6px 18px;
  border-radius: 4px;
  margin: 6px 0 4px 0;
}
.score-bas  { background: var(--vert-fond);   color: var(--vert-ok);   border: 1px solid var(--vert-bord); }
.score-moy  { background: var(--orange-fond); color: var(--orange-warn); border: 1px solid var(--orange-bord); }
.score-haut { background: var(--rouge-fond);  color: var(--rouge-crit); border: 1px solid var(--rouge-bord); }
.score-info { background: var(--bleu-clair);  color: var(--bleu-hosp);  border: 1px solid #90CAF9; }
.score-interp { font-size: 0.82rem; color: var(--texte-aide); margin-top: 4px; font-style: italic; }

/* ---- SBAR ---- */
.sbar-bloc {
  background: #FAFBFC;
  border: 1px solid var(--bordure);
  border-radius: 4px;
  padding: 16px;
  font-family: 'DM Mono', monospace;
  font-size: 0.78rem;
  line-height: 1.9;
  white-space: pre-wrap;
  color: var(--texte-corps);
}

/* ---- HISTORIQUE ---- */
.hist-ligne {
  background: var(--fond-carte);
  border: 1px solid var(--bordure);
  border-radius: 4px;
  padding: 9px 13px;
  margin-bottom: 5px;
  font-size: 0.82rem;
}
.hist-M  { border-left: 4px solid var(--violet-m);  }
.hist-1  { border-left: 4px solid var(--rouge-crit); }
.hist-2  { border-left: 4px solid var(--orange-warn); }
.hist-3A { border-left: 4px solid #F9A825; }
.hist-3B { border-left: 4px solid #FDD835; }
.hist-4  { border-left: 4px solid var(--vert-ok); }
.hist-5  { border-left: 4px solid var(--bleu-hosp); }

/* ---- REGISTRE ---- */
.reg-carte {
  background: var(--fond-carte);
  border: 1px solid var(--bordure);
  border-radius: 6px;
  padding: 14px 18px;
  margin-bottom: 8px;
  transition: border-color 0.15s;
}
.reg-carte:hover { border-color: var(--bleu-hosp); }
.reg-badge {
  display: inline-block;
  font-family: 'DM Mono', monospace;
  font-size: 0.72rem;
  font-weight: 500;
  padding: 2px 9px;
  border-radius: 3px;
  margin-right: 6px;
}
.reg-M  { background: var(--violet-fond); color: var(--violet-m); }
.reg-1  { background: var(--rouge-fond);  color: var(--rouge-crit); }
.reg-2  { background: var(--orange-fond); color: var(--orange-warn); }
.reg-3A, .reg-3B { background: #FFFDE7; color: #7B5E00; }
.reg-4  { background: var(--vert-fond);  color: var(--vert-ok); }
.reg-5  { background: var(--bleu-clair); color: var(--bleu-hosp); }
.reg-stat {
  background: var(--fond-carte);
  border: 1px solid var(--bordure);
  border-radius: 6px;
  padding: 14px;
  text-align: center;
}
.reg-stat-num {
  font-family: 'DM Mono', monospace;
  font-size: 1.7rem;
  font-weight: 500;
  color: var(--bleu-hosp);
}
.reg-stat-label { font-size: 0.68rem; color: var(--texte-aide); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 3px; }

/* ---- PERFUSION ---- */
.perf-result {
  font-family: 'DM Mono', monospace;
  font-size: 2rem;
  font-weight: 500;
  color: var(--bleu-hosp);
  text-align: center;
  margin: 6px 0;
}
.perf-label { font-size: 0.72rem; color: var(--texte-aide); text-align: center; text-transform: uppercase; letter-spacing: 0.08em; }
.dose-carte {
  background: var(--fond-carte);
  border: 1px solid var(--bordure);
  border-left: 3px solid var(--vert-ok);
  border-radius: 4px;
  padding: 12px 16px;
  margin: 6px 0;
  font-size: 0.84rem;
  color: var(--texte-corps);
}
.dose-titre {
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--vert-ok);
  margin-bottom: 6px;
}
.dose-valeur {
  font-family: 'DM Mono', monospace;
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--texte-titre);
}

/* ---- REEVALUATION ---- */
.reeval-ligne {
  background: var(--fond-carte);
  border: 1px solid var(--bordure);
  border-radius: 4px;
  padding: 9px 13px;
  margin-bottom: 5px;
  font-size: 0.82rem;
}
.reeval-amelio { border-left: 4px solid var(--vert-ok); }
.reeval-stable { border-left: 4px solid var(--bleu-hosp); }
.reeval-aggrav { border-left: 4px solid var(--rouge-crit); }
.trend-haut { color: var(--vert-ok); font-family: 'DM Mono', monospace; }
.trend-bas  { color: var(--rouge-crit); font-family: 'DM Mono', monospace; }
.trend-egal { color: var(--texte-aide); font-family: 'DM Mono', monospace; }

/* ---- CHRONOMETRE ---- */
.chrono {
  font-family: 'DM Mono', monospace;
  font-size: 2rem;
  font-weight: 500;
  color: var(--bleu-hosp);
  text-align: center;
  letter-spacing: 0.04em;
  padding: 8px 0;
}
.chrono-label {
  font-size: 0.65rem;
  color: var(--texte-aide);
  text-align: center;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

/* ---- DISCLAIMER RGPD ---- */
.disclaimer {
  background: var(--fond-carte);
  border: 1px solid var(--bordure);
  border-radius: 4px;
  padding: 12px 16px;
  margin-top: 20px;
  font-size: 0.68rem;
  color: var(--texte-aide);
  line-height: 1.7;
}
.disclaimer-titre {
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--texte-aide);
  margin-bottom: 5px;
}
.disclaimer-signature {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--bleu-hosp);
  border-top: 1px solid var(--bordure);
  padding-top: 7px;
  margin-top: 7px;
}

/* ---- INFO-BULLE SCORE ---- */
.infobulle {
  background: var(--bleu-clair);
  border: 1px solid #90CAF9;
  border-radius: 4px;
  padding: 10px 14px;
  font-size: 0.78rem;
  color: #1E3A5F;
  line-height: 1.7;
  margin: 8px 0;
}
.infobulle-titre { font-weight: 600; margin-bottom: 4px; }

/* ---- FICHE TRI ---- */
.fiche-tri {
  background: #FFFFFF;
  color: #1a1a1a;
  border-radius: 6px;
  padding: 18px;
  font-family: 'DM Sans', sans-serif;
  border: 1px solid var(--bordure);
}
.fiche-header { border-bottom: 2px solid var(--bleu-hosp); padding-bottom: 8px; margin-bottom: 10px; }
.fiche-titre  { font-size: 1rem; font-weight: 600; color: var(--bleu-hosp); }
.fiche-row    { display: flex; justify-content: space-between; font-size: 0.8rem; padding: 3px 0; border-bottom: 1px solid #EEF0F3; }
.fiche-section { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--texte-aide); margin: 8px 0 3px 0; }
.fiche-niveau { text-align: center; padding: 8px; border-radius: 4px; font-weight: 700; font-size: 1.1rem; margin: 8px 0; }

/* ---- SIDEBAR ELEMENTS ---- */
.sidebar-section {
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--bleu-hosp);
  border-bottom: 1px solid var(--bordure);
  padding-bottom: 4px;
  margin: 14px 0 9px 0;
}
.sidebar-sig {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--bleu-hosp);
  border-top: 1px solid var(--bordure);
  padding-top: 9px;
  margin-top: 10px;
}
.sidebar-legal { font-size: 0.65rem; color: var(--texte-aide); font-style: italic; margin-top: 5px; }

/* ---- MOBILE (iPhone) ---- */
@media (max-width: 768px) {
  .tri-carte    { padding: 14px; }
  .sbar-bloc    { font-size: 0.72rem; padding: 10px; }
  .reg-carte    { padding: 10px 14px; }
  .chrono       { font-size: 1.6rem; }
  .news2-val    { font-size: 1.2rem; }
  .perf-result  { font-size: 1.5rem; }
  .stButton > button { min-height: 48px; font-size: 0.95rem; }
  .stNumberInput input { font-size: 1rem; }
}
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# [1] MOTEUR SCORES - Calculs cliniques encapsules
# ==============================================================================

def calculer_news2(fr, spo2, o2_supp, temp, pas, fc, gcs, bpco):
    """
    Score NEWS2 (National Early Warning Score 2).
    Reference : Royal College of Physicians, 2017.
    Echelle SpO2 adaptee BPCO : objectif cible 88-92%.
    Retourne : (score_int, liste_avertissements)
    """
    avertissements = []
    try:
        s = 0
        # Frequence respiratoire
        if fr is None:
            avertissements.append("Score NEWS2 incomplet : frequence respiratoire manquante")
            return 0, avertissements
        s += 3 if fr <= 8 else (1 if fr <= 11 else (0 if fr <= 20 else (2 if fr <= 24 else 3)))

        # SpO2 - echelle 1 (sans BPCO) ou echelle 2 (BPCO)
        if spo2 is None:
            avertissements.append("Score NEWS2 incomplet : SpO2 manquante")
            return 0, avertissements
        if not bpco:
            s += 3 if spo2 <= 91 else (2 if spo2 <= 93 else (1 if spo2 <= 95 else 0))
        else:
            s += (3 if spo2 <= 83 else (2 if spo2 <= 85 else (1 if spo2 <= 87 else
                  (0 if spo2 <= 92 else (1 if spo2 <= 94 else (2 if spo2 <= 96 else 3))))))

        # Oxygene supplementaire
        if o2_supp:
            s += 2

        # Temperature
        if temp is None:
            avertissements.append("Score NEWS2 incomplet : temperature manquante")
            return 0, avertissements
        s += 3 if temp <= 35.0 else (1 if temp <= 36.0 else (0 if temp <= 38.0 else (1 if temp <= 39.0 else 2)))

        # Pression arterielle systolique
        if pas is None:
            avertissements.append("Score NEWS2 incomplet : pression arterielle manquante")
            return 0, avertissements
        s += 3 if pas <= 90 else (2 if pas <= 100 else (1 if pas <= 110 else (0 if pas <= 219 else 3)))

        # Frequence cardiaque
        if fc is None:
            avertissements.append("Score NEWS2 incomplet : frequence cardiaque manquante")
            return 0, avertissements
        s += 3 if fc <= 40 else (1 if fc <= 50 else (0 if fc <= 90 else (1 if fc <= 110 else (2 if fc <= 130 else 3))))

        # Conscience
        if gcs is None:
            avertissements.append("Score NEWS2 incomplet : GCS manquant")
            return 0, avertissements
        if gcs < 15:
            s += 3

        return s, avertissements

    except (TypeError, ValueError) as e:
        return 0, [f"Erreur calcul NEWS2 : {e}"]


def niveau_news2(score):
    """Retourne (etiquette, classe_css) pour un score NEWS2."""
    if score <= 4:  return f"NEWS2 : {score}", "news2-bas" if score == 0 else "news2-bas"
    if score <= 6:  return f"NEWS2 : {score}", "news2-moyen"
    if score <= 8:  return f"NEWS2 : {score}", "news2-haut"
    return f"NEWS2 : {score}", "news2-crit"


def calculer_gcs(y, v, m):
    """
    Glasgow Coma Scale.
    Reference : Teasdale & Jennett, Lancet 1974.
    """
    try:
        total = max(3, min(15, int(y) + int(v) + int(m)))
        return total, []
    except (TypeError, ValueError) as e:
        return 15, [f"Erreur calcul GCS : {e}"]


def calculer_timi(age, nb_frcv, stenose_50, aspirine_7j, troponine_pos, deviation_st, crises_24h):
    """
    Score TIMI pour SCA-ST- (risque a 14 jours).
    Reference : Antman et al., JAMA 2000.
    """
    try:
        s = 0
        if age >= 65:      s += 1
        if nb_frcv >= 3:   s += 1
        if stenose_50:     s += 1
        if aspirine_7j:    s += 1
        if troponine_pos:  s += 1
        if deviation_st:   s += 1
        if crises_24h >= 2: s += 1
        return s, []
    except (TypeError, ValueError) as e:
        return 0, [f"Erreur calcul TIMI : {e}"]


def calculer_silverman(balt, tirage, retraction, ailes_nez, geignement):
    """
    Score de Silverman - detresse respiratoire neonatale.
    Reference : Silverman & Andersen, Pediatrics 1956.
    """
    try:
        return min(10, balt + tirage + retraction + ailes_nez + geignement), []
    except (TypeError, ValueError) as e:
        return 0, [f"Erreur calcul Silverman : {e}"]


def calculer_malinas(parite, duree_travail, duree_contrac, intervalle, poche):
    """
    Score de Malinas - transport obstetrical.
    Score >= 8 : accouchement imminent, transport contre-indique.
    """
    try:
        return min(10, parite + duree_travail + duree_contrac + intervalle + poche), []
    except (TypeError, ValueError) as e:
        return 0, [f"Erreur calcul Malinas : {e}"]


def calculer_brulure(surface_pct, age_pat):
    """
    Surface corporelle brulee (regle des 9 de Wallace) et formule de Baux.
    Reference : Wallace, Lancet 1951 ; Baux, 1961.
    """
    try:
        scb = max(0.0, min(100.0, surface_pct))
        baux = age_pat + scb
        if baux > 120:   pronostic = "Pronostic vital tres reserve (Baux > 120)"
        elif baux > 100: pronostic = "Pronostic severe (Baux 100-120)"
        elif baux > 80:  pronostic = "Pronostic reserve (Baux 80-100)"
        else:            pronostic = "Pronostic favorable (Baux < 80)"
        return scb, baux, pronostic, []
    except (TypeError, ValueError) as e:
        return 0.0, 0.0, "Erreur", [f"Erreur calcul brulure : {e}"]


def badge_vital(val, seuil_warn_bas, seuil_crit_bas, seuil_warn_haut, seuil_crit_haut, unite=""):
    """Retourne un badge HTML colore selon les seuils vitaux."""
    try:
        if val <= seuil_crit_bas or val >= seuil_crit_haut:
            return f'<span class="badge-vital badge-crit">{val}{unite}</span>'
        if val <= seuil_warn_bas or val >= seuil_warn_haut:
            return f'<span class="badge-vital badge-warn">{val}{unite}</span>'
        return f'<span class="badge-vital badge-ok">{val}{unite}</span>'
    except (TypeError, ValueError):
        return f'<span class="badge-vital badge-warn">?</span>'


# ==============================================================================
# [2] MOTEUR PHARMACIE - Doses BCFI Belgique, unites belges
# Glycemie : mg/dl (standard belge). Facteur : 1 mmol/l = 18 mg/dl
# ==============================================================================

GLYCEMIE_SEUILS = {
    # Seuils en mg/dl (standard belge)
    "hypoglycemie_severe":  54,   # < 3 mmol/l
    "hypoglycemie_modere":  70,   # < 3.9 mmol/l
    "hyperglycemie_seuil": 180,   # > 10 mmol/l
    "hyperglycemie_severe": 360,  # > 20 mmol/l
    "cetose_risque":        252,  # > 14 mmol/l
}


def mmol_vers_mgdl(valeur_mmol):
    """Convertit une glycemie de mmol/l en mg/dl (standard belge)."""
    return round(valeur_mmol * 18, 0)


def mgdl_vers_mmol(valeur_mgdl):
    """Convertit une glycemie de mg/dl en mmol/l pour reference."""
    return round(valeur_mgdl / 18, 1)


def calculer_debit_perfusion(volume_ml, duree_heures):
    """
    Calcul du debit de perfusion.
    Formule : Debit (ml/h) = Volume (ml) / Duree (h)
    """
    try:
        if duree_heures <= 0:
            return None, "Duree de perfusion invalide (doit etre > 0)"
        if volume_ml <= 0:
            return None, "Volume de perfusion invalide (doit etre > 0)"
        debit = round(volume_ml / duree_heures, 1)
        gttes_min = round(debit / 3, 1)  # 1 ml = 20 gouttes ; debit/3 = gttes/min
        return {"ml_h": debit, "gttes_min": gttes_min}, None
    except (TypeError, ValueError) as e:
        return None, f"Erreur calcul debit : {e}"


def dose_paracetamol_iv(poids_kg):
    """
    Paracetamol IV (Perfusalgan/Dafalgan IV) - BCFI Belgique.
    Adulte (>= 50 kg) : 1 g IV en 15 min, max 4 g/24h.
    Enfant/adulte leger (10-50 kg) : 15 mg/kg IV en 15 min, max 60 mg/kg/24h.
    Intervalle minimum : 4 heures entre chaque administration.
    Reference : RCP Paracetamol IV - BCFI 2024.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"
        if poids_kg >= 50:
            dose_mg = 1000
            max_j   = "4 g/24h (4 administrations)"
        else:
            dose_mg = round(15 * poids_kg, 0)
            max_j   = f"60 mg/kg/24h (max {round(60 * poids_kg, 0)} mg)"
        dose_g = round(dose_mg / 1000, 2)
        return {
            "dose_mg":  dose_mg,
            "dose_g":   dose_g,
            "admin":    "Perfusion IV en 15 minutes",
            "intervalle": "Minimum 4 heures entre deux doses",
            "max_jour": max_j,
            "reference": "Perfusalgan 10 mg/ml / Dafalgan IV - BCFI"
        }, None
    except (TypeError, ValueError) as e:
        return None, f"Erreur dose Paracetamol : {e}"


def dose_morphine_iv(poids_kg, age_patient):
    """
    Morphine IV - Protocole antalgie urgences Belgique francophone.
    Titration : 2-3 mg IV toutes les 5-10 min jusqu'a EVA <= 3.
    Dose initiale : 0.05-0.1 mg/kg IV (max 5 mg par bolus).
    CI relatives : insuffisance respiratoire, hypotension.
    Reference : BCFI - Protocoles antalgie urgences CHU Belgique.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"
        dose_bolus_min = round(0.05 * poids_kg, 1)
        dose_bolus_max = round(0.1 * poids_kg, 1)
        # Reduction systematique chez le sujet age (>= 70 ans)
        note_age = ""
        if age_patient >= 70:
            dose_bolus_min = round(dose_bolus_min * 0.5, 1)
            dose_bolus_max = round(dose_bolus_max * 0.5, 1)
            note_age = "Dose reduite 50% - sujet age >= 70 ans"
        # Plafonnement par bolus
        dose_bolus_min = min(dose_bolus_min, 2.5)
        dose_bolus_max = min(dose_bolus_max, 5.0)
        return {
            "bolus_min":  dose_bolus_min,
            "bolus_max":  dose_bolus_max,
            "admin":      "IV lent sur 2-3 min. Titrer par paliers de 2-3 mg toutes les 5-10 min.",
            "objectif":   "EVA <= 3",
            "note_age":   note_age,
            "antidote":   "Naloxone 0.4 mg IV en cas de depression respiratoire",
            "reference":  "BCFI - Morphine chlorhydrate - Protocole urgences"
        }, None
    except (TypeError, ValueError) as e:
        return None, f"Erreur dose Morphine : {e}"


def dose_adrenaline_anaphylaxie(poids_kg):
    """
    Adrenaline IM - Choc anaphylactique.
    Reference : BCFI - Lignes directrices anaphylaxie Belgique 2023.
    Adulte (>= 30 kg) : 0.5 mg IM (0.5 ml de la solution 1 mg/ml).
    Enfant (< 30 kg)  : 0.01 mg/kg IM, max 0.5 mg.
    Site : face anterolaterale cuisse (travers le vetement si necessaire).
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"
        if poids_kg >= 30:
            dose_mg = 0.5
            note    = "0.5 ml de la solution a 1 mg/ml (ampoule standard)"
        else:
            dose_mg = min(round(0.01 * poids_kg, 3), 0.5)
            note    = f"0.01 mg/kg : {dose_mg} mg ({round(dose_mg * 1000, 0):.0f} microg)"
        return {
            "dose_mg": dose_mg,
            "voie":    "Injection intramusculaire - face anterolaterale de la cuisse",
            "note":    note,
            "repeter": "Repeter a 5-15 min si pas d'amelioration hemodynamique",
            "moniteur": "Monitoring continu FC, TA, SpO2 post-injection",
            "reference": "BCFI - Adrenaline Sterop 1 mg/ml - Lignes directrices anaphylaxie"
        }, None
    except (TypeError, ValueError) as e:
        return None, f"Erreur dose Adrenaline : {e}"


def dose_glucose_hypoglycemie(poids_kg, voie):
    """
    Correction hypoglycemie - protocoles belges.
    Glucose 30% IV : 0.3 g/kg (1 ml/kg de la sol. 30%) - max 50 ml.
    Glucagon SC/IM  : 1 mg si pas d'acces veineux.
    Reference : BCFI - Glucose 30% / Glucagon GlucaGen 1 mg.
    """
    try:
        if poids_kg <= 0:
            return None, "Poids invalide"
        if voie == "IV":
            dose_g  = round(0.3 * poids_kg, 1)
            vol_ml  = round(1 * poids_kg, 0)
            vol_ml  = min(vol_ml, 50)
            dose_g  = round(vol_ml * 0.3, 1)
            return {
                "produit":  "Glucose 30% solution injectable (Glucosie)",
                "dose_g":   dose_g,
                "volume":   f"{vol_ml:.0f} ml IV lent (2-3 min)",
                "controle": "Glycemie capillaire a 15 min post-injection",
                "reference": "BCFI - Glucose 30% - max 50 ml"
            }, None
        else:
            return {
                "produit":  "Glucagon GlucaGen 1 mg poudre (reconstitution avec diluant fourni)",
                "dose":     "1 mg SC ou IM",
                "note":     "Si acces IV impossible. Inefficace si reserves glycogene epuisees (jeune prolonge).",
                "controle": "Glycemie a 15 min. Alimentation PO des que possible.",
                "reference": "BCFI - GlucaGen HypoKit 1 mg"
            }, None
    except (TypeError, ValueError) as e:
        return None, f"Erreur dose Glucose : {e}"


# ==============================================================================
# [3] MOTEUR TRIAGE - FRENCH Triage SFMU V1.1
# ==============================================================================

LABELS_TRI = {
    "M":  "TRI M - IMMEDIAT",
    "1":  "TRI 1 - URGENCE EXTREME",
    "2":  "TRI 2 - TRES URGENT",
    "3A": "TRI 3A - URGENT",
    "3B": "TRI 3B - URGENT DIFFERE",
    "4":  "TRI 4 - MOINS URGENT",
    "5":  "TRI 5 - NON URGENT",
}
SECTEURS_TRI = {
    "M":  "Dechocage - Prise en charge immediate",
    "1":  "Dechocage - Prise en charge immediate",
    "2":  "Salle de soins aigus - Medecin < 20 min",
    "3A": "Salle de soins aigus - Medecin < 30 min",
    "3B": "Polyclinique urgences - Medecin < 1h",
    "4":  "Consultation urgences - Medecin < 2h",
    "5":  "Salle d'attente - Reorientation MG possible",
}
DELAIS_TRI  = {"M": 5, "1": 5, "2": 15, "3A": 30, "3B": 60, "4": 120, "5": 999}
CSS_TRI     = {"M": "tri-M",  "1": "tri-1",  "2": "tri-2",
               "3A": "tri-3A", "3B": "tri-3B", "4": "tri-4", "5": "tri-5"}
CSS_HIST    = {"M": "hist-M",  "1": "hist-1",  "2": "hist-2",
               "3A": "hist-3A", "3B": "hist-3B", "4": "hist-4", "5": "hist-5"}


def french_triage(motif, details, fc, pas, spo2, fr, gcs, temp, age, news2_score, glycemie_mgdl=None):
    """
    Algorithme FRENCH Triage SFMU V1.1.
    Glycemie en mg/dl (standard belge).
    Retourne : (niveau_str, justification_str, critere_ref_str)
    """
    try:
        # Valeurs par defaut si donnees manquantes
        fc   = fc   if fc   is not None else 80
        pas  = pas  if pas  is not None else 120
        spo2 = spo2 if spo2 is not None else 98
        fr   = fr   if fr   is not None else 16
        gcs  = gcs  if gcs  is not None else 15
        temp = temp if temp is not None else 37.0
        news2_score = news2_score or 0

        if news2_score >= 9:
            return "M", "NEWS2 >= 9 : engagement vital immediat.", "NEWS2 - Tri M"

        if motif == "Arret cardiorespiratoire":
            return "M", "ACR confirme.", "FRENCH - Tri M"

        if motif == "Hypotension arterielle":
            if pas <= 70:  return "1", f"PAS {pas} mmHg <= 70.", "FRENCH - Tri 1"
            if pas <= 90 or (pas <= 100 and fc > 100):
                return "2", f"PAS {pas} mmHg - choc debutant.", "FRENCH - Tri 2"
            if 90 < pas <= 100:
                return "3B", f"PAS {pas} mmHg - limite.", "FRENCH - Tri 3B"
            return "4", "TA dans les normes.", "FRENCH - Tri 4"

        if motif == "Douleur thoracique / SCA":
            ecg       = details.get("ecg", "Normal")
            douleur_t = details.get("douleur_type", "Atypique")
            co        = details.get("comorbidites_coronaires", False)
            dtyp      = details.get("douleur_typique", False)
            frcv      = details.get("frcv_count", 0)
            if ecg == "Anormal typique SCA" or details.get("ecg_anormal", False):
                return "1", "ECG typique SCA.", "FRENCH - Tri 1"
            if ecg == "Anormal non typique" or douleur_t == "Typique persistante/intense" or (dtyp and details.get("duree_longue", False)):
                return "2", "Douleur typique persistante ou ECG douteux.", "FRENCH - Tri 2"
            if frcv >= 2:
                return "3A", f"Douleur thoracique + {frcv} FRCV.", "FRENCH - Tri 3A (FRCV >= 2)"
            if co:
                return "3A", "Comorbidites coronaires documentees.", "FRENCH - Tri 3A"
            if dtyp or douleur_t == "Type coronaire":
                return "3B", "Douleur type coronaire.", "FRENCH - Tri 3B"
            return "4", "ECG normal, douleur atypique.", "FRENCH - Tri 4"

        if motif == "Tachycardie / tachyarythmie":
            if fc >= 180: return "1", f"FC {fc} >= 180 bpm.", "FRENCH - Tri 1"
            if fc >= 130: return "2", f"FC {fc} >= 130 bpm.", "FRENCH - Tri 2"
            if fc > 110:  return "3B", f"FC {fc} > 110 bpm.", "FRENCH - Tri 3B"
            return "4", "Episode resolutif.", "FRENCH - Tri 4"

        if motif == "Bradycardie / bradyarythmie":
            mt = details.get("mauvaise_tolerance", False)
            if fc <= 40: return "1", f"FC {fc} <= 40 bpm.", "FRENCH - Tri 1"
            if fc <= 50 and mt: return "2", f"FC {fc} + mauvaise tolerance.", "FRENCH - Tri 2"
            if fc <= 50: return "3B", f"FC {fc} - bien toleree.", "FRENCH - Tri 3B"
            return "4", "Bradycardie toleree.", "FRENCH - Tri 4"

        if motif == "Hypertension arterielle":
            sf = details.get("sf_associes", False)
            if pas >= 220 or (pas >= 180 and sf):
                return "2", f"PAS {pas} mmHg ou SF associes.", "FRENCH - Tri 2"
            if pas >= 180: return "3B", f"PAS {pas} >= 180 sans SF.", "FRENCH - Tri 3B"
            return "4", f"PAS {pas} < 180.", "FRENCH - Tri 4"

        if motif == "Dyspnee / insuffisance respiratoire":
            if fr >= 40 or spo2 < 86:
                return "1", f"Detresse respiratoire (FR {fr}, SpO2 {spo2}%).", "FRENCH - Tri 1"
            if (not details.get("parole_ok", True) or details.get("tirage") or
                    details.get("orthopnee") or (30 <= fr < 40) or (86 <= spo2 <= 90)):
                return "2", "Dyspnee a la parole ou tirage.", "FRENCH - Tri 2"
            return "3B", "Dyspnee moderee stable.", "FRENCH - Tri 3B"

        if motif == "Palpitations":
            if fc >= 180: return "2", f"FC {fc} >= 180.", "FRENCH - Tri 2"
            if fc >= 130: return "2", f"FC {fc} >= 130.", "FRENCH - Tri 2"
            if details.get("malaise") or fc > 110:
                return "3B", "Malaise ou FC > 110.", "FRENCH - Tri 3B"
            return "4", "Palpitations isolees.", "FRENCH - Tri 4"

        if motif == "Asthme / aggravation BPCO":
            dep = details.get("dep", 999)
            if fr >= 40 or spo2 < 86:
                return "1", "Detresse respiratoire.", "FRENCH - Tri 1"
            if dep <= 200 or not details.get("parole_ok", True) or details.get("tirage"):
                return "2", "DEP <= 200 ou dyspnee a la parole.", "FRENCH - Tri 2"
            if dep >= 300:
                return "4", f"DEP {dep} >= 300.", "FRENCH - Tri 4"
            return "3B", "Asthme modere.", "FRENCH - Tri 3B"

        if motif == "AVC / Deficit neurologique":
            dh = details.get("delai_heures", 999)
            ok = details.get("delai_ok", False)
            if dh <= 4.5 or ok:
                return "1", "Deficit < 4h30 - filiere Stroke / thrombolyse.", "FRENCH - Tri 1"
            if dh >= 24: return "3B", "Deficit > 24h.", "FRENCH - Tri 3B"
            return "2", "Deficit neurologique aigu.", "FRENCH - Tri 2"

        if motif == "Alteration de conscience / Coma":
            if gcs <= 8:  return "1", f"GCS {gcs} - coma.", "FRENCH - Tri 1"
            if gcs <= 13: return "2", f"GCS {gcs} - alteration moderee.", "FRENCH - Tri 2"
            return "3B", "Alteration legere.", "FRENCH - Tri 3B"

        if motif == "Convulsions":
            if (details.get("crises_multiples") or details.get("en_cours") or
                    details.get("confusion_post_critique") or temp >= 38.5):
                return "2", "Crise en cours, multiple ou confusion.", "FRENCH - Tri 2"
            return "3B", "Recuperation complete.", "FRENCH - Tri 3B"

        if motif == "Cephalee":
            if (details.get("inhabituelle") or details.get("brutale") or
                    details.get("fievre_assoc") or temp >= 38.5):
                return "2", "Cephalee inhabituelle, brutale ou febrile.", "FRENCH - Tri 2"
            return "3B", "Migraine connue.", "FRENCH - Tri 3B"

        if motif == "Vertiges / trouble de l'equilibre":
            if details.get("signes_neuro") or details.get("cephalee_brutale"):
                return "2", "Signes neurologiques associes.", "FRENCH - Tri 2"
            return "5", "Troubles stables.", "FRENCH - Tri 5"

        if motif == "Confusion / desorientation":
            if temp >= 38.5: return "2", "Confusion et fievre.", "FRENCH - Tri 2"
            return "3B", "Confusion afebrile.", "FRENCH - Tri 3B"

        if motif == "Hematemese / vomissement de sang":
            if details.get("abondante"): return "2", "Hematemese abondante.", "FRENCH - Tri 2"
            return "3B", "Striures de sang.", "FRENCH - Tri 3B"

        if motif == "Rectorragie / melena":
            if details.get("abondante"): return "2", "Rectorragie abondante.", "FRENCH - Tri 2"
            return "3B", "Selles souillees.", "FRENCH - Tri 3B"

        if motif == "Douleur abdominale":
            if (details.get("defense") or details.get("contracture") or
                    details.get("mauvaise_tolerance")):
                return "2", "Defense ou contracture abdominale.", "FRENCH - Tri 2"
            if details.get("regressive"): return "5", "Douleur regressive.", "FRENCH - Tri 5"
            return "3B", "Douleur moderee.", "FRENCH - Tri 3B"

        if motif == "Douleur lombaire / colique nephretique":
            if details.get("intense"): return "2", "Douleur intense.", "FRENCH - Tri 2"
            if details.get("regressive"): return "5", "Douleur regressive.", "FRENCH - Tri 5"
            return "3B", "Douleur moderee.", "FRENCH - Tri 3B"

        if motif == "Retention d'urine / anurie":
            return "2", "Retention urinaire.", "FRENCH - Tri 2"

        if motif == "Douleur testiculaire / torsion":
            if details.get("intense") or details.get("suspicion_torsion"):
                return "2", "Torsion suspectee.", "FRENCH - Tri 2"
            return "3B", "Avis chirurgical de garde.", "FRENCH - Tri 3B"

        if motif == "Hematurie":
            if details.get("abondante_active"): return "2", "Hematurie abondante.", "FRENCH - Tri 2"
            return "3B", "Hematurie moderee.", "FRENCH - Tri 3B"

        if motif == "Traumatisme avec amputation":
            return "M", "Amputation traumatique.", "FRENCH - Tri M"

        if motif == "Traumatisme abdomen / thorax / cervical":
            if details.get("penetrant"): return "1", "Traumatisme penetrant.", "FRENCH - Tri 1"
            if details.get("cinetique") == "Haute": return "2", "Haute velocite.", "FRENCH - Tri 2"
            if details.get("mauvaise_tolerance"): return "3B", "Mauvaise tolerance.", "FRENCH - Tri 3B"
            return "4", "Bonne tolerance.", "FRENCH - Tri 4"

        if motif == "Traumatisme cranien":
            if gcs <= 8: return "1", f"TC - GCS {gcs} - coma.", "FRENCH - Tri 1"
            if (gcs <= 13 or details.get("deficit_neuro") or details.get("aod_avk") or
                    details.get("vomissements_repetes")):
                return "2", "GCS 9-13, deficit, AVK ou vomissements.", "FRENCH - Tri 2"
            if details.get("pdc") or details.get("plaie"):
                return "3B", "PDC ou plaie crane.", "FRENCH - Tri 3B"
            return "5", "TC sans signe de gravite.", "FRENCH - Tri 5"

        if motif == "Brulure":
            if details.get("etendue") or details.get("main_visage"):
                return "2", "Etendue ou localisation main/visage.", "FRENCH - Tri 2"
            if age <= 2: return "3A", "Enfant <= 24 mois.", "FRENCH - Tri 3A"
            return "3B", "Brulure limitee.", "FRENCH - Tri 3B"

        if motif in ["Traumatisme bassin / hanche / femur / rachis"]:
            if details.get("cinetique") == "Haute": return "2", "Haute velocite.", "FRENCH - Tri 2"
            if details.get("mauvaise_tolerance"): return "3B", "Mauvaise tolerance.", "FRENCH - Tri 3B"
            return "4", "Bonne tolerance.", "FRENCH - Tri 4"

        if motif == "Traumatisme membre / epaule":
            if details.get("ischemie") or details.get("cinetique") == "Haute":
                return "2", "Ischemie distale ou haute velocite.", "FRENCH - Tri 2"
            if details.get("impotence_totale") or details.get("deformation"):
                return "3B", "Impotence totale.", "FRENCH - Tri 3B"
            if details.get("impotence_moderee"):
                return "4", "Impotence moderee.", "FRENCH - Tri 4"
            return "5", "Ni impotence ni deformation.", "FRENCH - Tri 5"

        if motif == "Plaie":
            if details.get("delabrant") or details.get("saignement_actif"):
                return "2", "Plaie delabrante ou saignement actif.", "FRENCH - Tri 2"
            if details.get("large_complexe") or details.get("main"):
                return "3B", "Plaie large ou main.", "FRENCH - Tri 3B"
            if details.get("superficielle"): return "4", "Plaie superficielle.", "FRENCH - Tri 4"
            return "5", "Excoriation.", "FRENCH - Tri 5"

        if motif == "Electrisation":
            if details.get("pdc") or details.get("foudre"):
                return "2", "PDC ou foudroiement.", "FRENCH - Tri 2"
            if details.get("haute_tension"):
                return "3B", "Haute tension.", "FRENCH - Tri 3B"
            return "4", "Courant domestique.", "FRENCH - Tri 4"

        if motif == "Agression sexuelle / sevices":
            return "1", "Agression sexuelle.", "FRENCH - Tri 1"

        if motif == "Idee / comportement suicidaire":
            return "1", "Comportement suicidaire.", "FRENCH - Tri 1"

        if motif == "Troubles du comportement / psychiatrie":
            if details.get("agitation") or details.get("violence"):
                return "2", "Agitation ou violence.", "FRENCH - Tri 2"
            return "4", "Consultation psychiatrique.", "FRENCH - Tri 4"

        if motif in ["Intoxication medicamenteuse", "Intoxication non medicamenteuse"]:
            if (details.get("mauvaise_tolerance") or details.get("intention_suicidaire") or
                    details.get("cardiotropes")):
                return "2", "Mauvaise tolerance ou cardiotropes.", "FRENCH - Tri 2"
            return "3B", "Avis specialiste de garde.", "FRENCH - Tri 3B"

        if motif == "Fievre":
            if (temp >= 40 or temp <= 35.2 or details.get("confusion") or
                    details.get("purpura") or details.get("temp_extreme")):
                return "2", "Fievre severe ou signes de gravite.", "FRENCH - Tri 2"
            if details.get("mauvaise_tolerance") or pas < 100:
                return "3B", "Mauvaise tolerance.", "FRENCH - Tri 3B"
            return "5", "Fievre bien toleree.", "FRENCH - Tri 5"

        if motif == "Accouchement imminent":
            return "M", "Accouchement imminent.", "FRENCH - Tri M"

        if motif in ["Probleme de grossesse (1er/2eme T)", "Probleme de grossesse (3eme T)"]:
            return "3A", "Grossesse - surveillance urgente.", "FRENCH - Tri 3A"

        if motif == "Meno-metrorragie":
            if details.get("grossesse") or details.get("abondante"):
                return "2", "Grossesse ou saignement abondant.", "FRENCH - Tri 2"
            return "3B", "Saignement modere.", "FRENCH - Tri 3B"

        if motif == "Hyperglycemie":
            # Glycemie en mg/dl (standard belge)
            gl = glycemie_mgdl if glycemie_mgdl is not None else details.get("glycemie_mgdl", 0)
            if details.get("cetose_elevee") or gcs < 15:
                return "2", "Cetose ou trouble conscience.", "FRENCH - Tri 2"
            if gl >= GLYCEMIE_SEUILS["hyperglycemie_severe"] or details.get("cetose_positive"):
                return "3B", f"Glycemie {gl} mg/dl >= 360.", "FRENCH - Tri 3B"
            return "4", "Hyperglycemie moderee.", "FRENCH - Tri 4"

        if motif == "Hypoglycemie":
            gl = glycemie_mgdl if glycemie_mgdl is not None else details.get("glycemie_mgdl", 90)
            if gcs <= 8:
                return "1", f"Coma hypoglycemique GCS {gcs}.", "FRENCH - Tri 1"
            if gcs <= 13 or details.get("mauvaise_tolerance") or gl < GLYCEMIE_SEUILS["hypoglycemie_severe"]:
                return "2", f"Mauvaise tolerance - glycemie {gl} mg/dl.", "FRENCH - Tri 2"
            return "3B", "Hypoglycemie moderee.", "FRENCH - Tri 3B"

        if motif == "Hypothermie":
            if temp <= 32: return "1", f"Hypothermie severe T {temp}C.", "FRENCH - Tri 1"
            if temp <= 35.2: return "2", "Hypothermie moderee.", "FRENCH - Tri 2"
            return "3B", "Hypothermie legere.", "FRENCH - Tri 3B"

        if motif == "Coup de chaleur / insolation":
            if gcs <= 8: return "1", "Coup de chaleur + coma.", "FRENCH - Tri 1"
            if temp >= 40: return "2", f"T {temp}C >= 40.", "FRENCH - Tri 2"
            return "3B", "Coup de chaleur leger.", "FRENCH - Tri 3B"

        if motif == "Allergie / anaphylaxie":
            if details.get("dyspnee") or details.get("mauvaise_tolerance"):
                return "2", "Anaphylaxie severe.", "FRENCH - Tri 2"
            return "4", "Reaction allergique legere.", "FRENCH - Tri 4"

        if motif == "Epistaxis":
            if details.get("abondant_actif"): return "2", "Epistaxis abondante active.", "FRENCH - Tri 2"
            if details.get("abondant_resolutif"): return "3B", "Epistaxis abondante resolutive.", "FRENCH - Tri 3B"
            return "5", "Epistaxis peu abondante.", "FRENCH - Tri 5"

        if motif in ["Corps etranger / brulure oculaire", "Trouble visuel / cecite"]:
            if details.get("intense") or details.get("chimique") or details.get("brutal"):
                return "2", "Urgence ophtalmologique.", "FRENCH - Tri 2"
            return "3B", "Avis ophtalmologue de garde.", "FRENCH - Tri 3B"

        # Fallback generique
        eva = details.get("eva", 0)
        if news2_score >= 5 or gcs < 15: return "2", f"NEWS2 {news2_score} / GCS {gcs}.", "NEWS2/GCS"
        if news2_score >= 1 or eva >= 7:  return "3B", f"EVA {eva}/10 / NEWS2 {news2_score}.", "NEWS2/EVA"
        if eva >= 4: return "4", f"EVA {eva}/10.", "EVA"
        return "5", "Non urgent.", "Par defaut"

    except (TypeError, ValueError) as e:
        return "3B", f"Erreur evaluation ({e}) - tri par defaut conservateur.", "Erreur - verifier les parametres"


# ==============================================================================
# [4] MOTEUR SBAR - Transmission DPI-Ready
# RGPD : aucun nom/prenom. Code anonyme horodate.
# ==============================================================================

PRESCRIPTIONS_ANTICIPEES = {
    "Douleur thoracique / SCA": {
        "Gestes immediats": [
            "ECG 12 derivations - objectif < 10 min de l'arrivee",
            "Voie veineuse peripherique (VVP) 18G minimum",
            "Monitoring cardiorespiratoire continu",
            "Aspirine 250 mg PO ou IV sauf allergie documentee",
            "Position semi-assise, O2 si SpO2 < 95%",
        ],
        "Bilan biologique": [
            "Troponine Hs T0 puis T1h (ou T3h selon protocole local)",
            "Hemogramme complet + plaquettes",
            "Ionogramme, creatinine, uree",
            "TP / TCA / INR si patient sous AOD ou AVK",
            "D-Dimeres si suspicion embolie pulmonaire concomitante",
            "NT-proBNP si signes d'insuffisance cardiaque",
        ],
        "Imagerie": ["Radiographie thorax face (lit si instable)"],
        "Rappels critiques": [
            "Repeter ECG a 30 min si premier normal et douleur persistante",
            "Patient a jeun - potentiel coronarographie urgente",
            "Alerter cardiologue si sus-decalage ST : salle cath < 90 min",
        ],
    },
    "Dyspnee / insuffisance respiratoire": {
        "Gestes immediats": [
            "Position semi-assise (Fowler 45 degres)",
            "O2 - objectif SpO2 > 94% (88-92% si BPCO connu)",
            "VVP 18G minimum",
            "Monitoring SpO2 continu + frequence respiratoire",
        ],
        "Bilan biologique": [
            "Gazometrie arterielle (ou veineuse si instable)",
            "Hemogramme complet",
            "D-Dimeres si suspicion embolie pulmonaire",
            "NT-proBNP si suspicion insuffisance cardiaque",
            "CRP + PCT si contexte infectieux",
        ],
        "Imagerie": ["Radiographie thorax face debout", "Echographie pulmonaire (POCUS) si disponible"],
        "Rappels critiques": [
            "Preparer materiel intubation si FR > 35 ou SpO2 < 85% sous O2",
            "Aerosol bronchodilatateur si bronchospasme confirme",
        ],
    },
    "AVC / Deficit neurologique": {
        "Gestes immediats": [
            "ALERTE FILIERE STROKE - activation immediate",
            "Glycemie capillaire (CI thrombolyse si < 54 ou > 396 mg/dl)",
            "VVP 18G bras NON paretique",
            "Ne pas faire baisser la TA sauf si PAS > 220 mmHg",
            "Patient a jeun strict",
        ],
        "Bilan biologique": [
            "Hemogramme + plaquettes - URGENT",
            "TP / TCA / INR / fibrinogene (CI thrombolyse si anomalie)",
            "Ionogramme, creatinine",
            "Troponine (FA possible)",
        ],
        "Imagerie": [
            "TDM cerebral sans injection URGENT (< 25 min door-to-CT)",
            "Angio-TDM TSA si thrombectomie envisagee",
        ],
        "Rappels critiques": [
            "Heure exacte debut des symptomes = information vitale pour la filiere",
            "Objectif door-to-needle < 60 min pour thrombolyse",
            "CI thrombolyse : AOD < 48h, chirurgie < 14j, AVC < 3 mois",
        ],
    },
    "Fievre": {
        "Gestes immediats": [
            "VVP",
            "Paracetamol IV (Perfusalgan) 1g si T > 38.5C et mauvaise tolerance",
        ],
        "Bilan biologique": [
            "Hemocultures x2 AVANT toute antibiotherapie",
            "Hemogramme, CRP, procalcitonine",
            "Ionogramme, creatinine",
            "Lactates (sepsis ?)",
            "Bandelette urinaire + ECBU",
        ],
        "Rappels critiques": [
            "Purpura fulminans : Ceftriaxone 2g IV IMMEDIATEMENT - ne pas attendre le bilan",
            "Antibiotiques dans l'heure si sepsis ou choc septique confirme",
            "Recherche systematique d'une porte d'entree infectieuse",
        ],
    },
    "Allergie / anaphylaxie": {
        "Gestes immediats": [
            "Adrenaline 0.5 mg IM - face anterolaterale cuisse (Adrenaline Sterop 1 mg/ml)",
            "Remplissage NaCl 0.9% 500 ml en debit libre si choc",
            "Position Trendelenburg si hypotension",
            "O2 haut debit si dyspnee ou desaturation",
            "Antihistaminique IV (Diphenhydramine / Polaramine 5 mg)",
            "Corticosteroides IV (Methylprednisolone 1 mg/kg)",
        ],
        "Rappels critiques": [
            "Repeter l'adrenaline a 5-15 min si pas d'amelioration",
            "Surveillance minimale 6h (risque de reaction biphasique)",
            "Tryptase serique a prelever dans les 2h post-reaction",
        ],
    },
    "Intoxication medicamenteuse": {
        "Gestes immediats": [
            "VVP",
            "ECG 12 derivations (toxiques cardiotropes ?)",
            "Monitoring cardiorespiratoire continu",
        ],
        "Bilan biologique": [
            "Paracetamol sanguin SYSTEMATIQUE",
            "Ethanolémie",
            "Screening toxicologique urinaire et sanguin",
            "Ionogramme, creatinine, bilan hepatique",
            "Gazometrie (acidose ?)",
        ],
        "Rappels critiques": [
            "Centre Antipoisons Belgique : 070 245 245 (24h/24)",
            "N-Acetylcysteine si intoxication paracetamol selon nomogramme Rumack-Matthew",
            "Charbon active si ingestion < 1h, patient conscient (sauf CI)",
            "Evaluation psychiatrique obligatoire si intention suicidaire",
        ],
    },
    "Hypoglycemie": {
        "Gestes immediats": [
            "Glycemie capillaire IMMEDIATE (mg/dl)",
            "Si conscient : resucrage oral 15-20g glucides rapides",
            "Si inconscient : Glucose 30% 50 ml IV lent (Glucosie - BCFI)",
            "Si acces IV impossible : Glucagon 1 mg IM/SC (GlucaGen HypoKit)",
        ],
        "Rappels critiques": [
            "Controler glycemie a 15 min post-correction - objectif > 100 mg/dl",
            "Identifier la cause : saut de repas, surdosage insuline, sulfamides",
            "Surveillance prolongee si sulfamides hypoglycemiants (risque recidive)",
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
            "Appel SMUR ou equipe obstetricale IMMEDIAT",
            "Preparer kit accouchement inopine",
            "Monitoring foetal si disponible",
            "VVP gros calibre (16G)",
            "Decubitus lateral gauche ou position gynecologique",
        ],
        "Rappels critiques": [
            "Ne pas transporter si Malinas >= 8",
            "Preparer : clamps ombilicaux, draps chauds, aspirateur mucosites",
            "Ocytocine 5 UI IV lent APRES delivrance (prevention HPP)",
        ],
    },
}


def generer_sbar(age, motif, cat, atcd, allergies, o2_supp, temp, fc, pas, spo2, fr, gcs,
                 news2, news2_label, eva, eva_echelle, p_pqrst, q_pqrst, r_pqrst, t_onset,
                 details, niveau, tri_label, justif, critere_ref, secteur,
                 gcs_y=4, gcs_v=5, gcs_m=6, code_anon="ANON"):
    """
    Generation d'une transmission SBAR structuree DPI-Ready.
    RGPD : aucun nom ou prenom - identifiant anonyme uniquement.
    Format : copier-coller direct dans le dossier patient informatise.
    """
    now_str   = datetime.now().strftime("%d/%m/%Y a %H:%M")
    date_str  = datetime.now().strftime("%d/%m/%Y")
    heure_str = datetime.now().strftime("%H:%M")
    atcd_str  = ", ".join(atcd) if atcd else "aucun antecedent signifie"
    all_str   = allergies if allergies and allergies.strip().upper() != "RAS" else "aucune allergie connue"

    # Etat de conscience
    if gcs == 15:    conscience = "conscient et oriente"
    elif gcs >= 13:  conscience = f"conscience alteree GCS {gcs} (Y{gcs_y}V{gcs_v}M{gcs_m})"
    elif gcs >= 9:   conscience = f"obnubile GCS {gcs} (Y{gcs_y}V{gcs_v}M{gcs_m})"
    else:            conscience = f"COMA GCS {gcs} (Y{gcs_y}V{gcs_v}M{gcs_m})"

    # Anomalies vitaux
    anomalies = []
    if temp > 38 or temp < 36:   anomalies.append(f"temperature {temp}C")
    if fc > 100:                  anomalies.append(f"tachycardie {fc} bpm")
    if fc < 60:                   anomalies.append(f"bradycardie {fc} bpm")
    if pas < 90:                  anomalies.append(f"hypotension {pas} mmHg")
    if pas > 180:                 anomalies.append(f"HTA {pas} mmHg")
    if spo2 < 94:                 anomalies.append(f"desaturation SpO2 {spo2}%")
    if fr > 20:                   anomalies.append(f"tachypnee {fr}/min")
    vitaux_txt = "dans les normes" if not anomalies else "ANOMALIES : " + ", ".join(anomalies)

    shock_index = round(fc / pas, 2) if pas and pas > 0 else 0

    # Gestes anticipees IAO (4 premiers)
    rx_txt = ""
    rx = PRESCRIPTIONS_ANTICIPEES.get(motif)
    if rx and rx.get("Gestes immediats"):
        items = rx["Gestes immediats"][:4]
        rx_txt = "\n  Prescriptions anticipees IAO :\n" + "\n".join([f"    [ ] {it}" for it in items])

    # Recommandation selon niveau
    reco_map = {
        "M":  "DEMANDE PRISE EN CHARGE IMMEDIATE EN DECHOCAGE.",
        "1":  "DEMANDE PRISE EN CHARGE IMMEDIATE EN DECHOCAGE.",
        "2":  "Demande evaluation medicale urgente < 20 min.",
        "3A": "Evaluation dans les 30 min - salle de soins aigus.",
        "3B": "Evaluation dans l'heure - polyclinique urgences.",
        "4":  "Evaluation dans les 2h - consultation urgences.",
        "5":  "Consultation non urgente - reorientation MG possible.",
    }
    reco = reco_map.get(niveau, "Evaluation medicale requise.")

    return f"""==============================================================
  TRANSMISSION SBAR - AKIR-IAO Project v14.0
  Service des Urgences
  {date_str} - {heure_str}
==============================================================

[S] SITUATION
  Code patient   : {code_anon}
  Age            : {age} ans
  Admission      : {now_str}
  Motif          : {motif} ({cat})
  Douleur        : {eva}/10 ({eva_echelle})
  Conscience     : {conscience}
  NIVEAU DE TRI  : {tri_label}

[B] BACKGROUND
  Antecedents    : {atcd_str}
  Allergies      : {all_str}
  O2 admission   : {'oui' if o2_supp else 'non'}

[A] ASSESSMENT
  Constantes :
    Temperature {temp}C  |  FC {fc} bpm  |  PAS {pas} mmHg
    SpO2 {spo2}%          |  FR {fr}/min  |  GCS {gcs}/15
  Shock Index    : {shock_index}
  Bilan vitaux   : {vitaux_txt}
  NEWS2          : {news2} ({news2_label})

  PQRST :
    P - Provoque / Pallie : {p_pqrst or 'non precise'}
    Q - Qualite / Type    : {q_pqrst or 'non precise'}
    R - Region / Irrad.   : {r_pqrst or 'non precise'}
    S - Severite          : {eva}/10 ({eva_echelle})
    T - Temps / Duree     : {t_onset or 'non precise'}

  Justification triage : {justif}
  Reference FRENCH     : {critere_ref}

[R] RECOMMENDATION
  Orientation    : {secteur}
  {reco}
{rx_txt}

--------------------------------------------------------------
  AKIR-IAO Project v14.0 - Ismail Ibn-Daifa
  Ref. FRENCH Triage SFMU V1.1 - Adaptation SIAMU Belgique
  RGPD : aucun nom patient dans ce document
--------------------------------------------------------------
"""


# ==============================================================================
# [5] MOTEUR ALERTES - Coherence clinique et securite
# ==============================================================================

def verifier_coherence(fc, pas, spo2, fr, gcs, temp, eva, motif, atcd, details, news2):
    """
    Verification de coherence clinique des parametres saisis.
    Retourne : (liste_danger, liste_attention, liste_info)
    """
    danger, attention, info = [], [], []
    try:
        # Incoherences de saisie
        if eva == 0 and fc > 110:
            attention.append("Incoherence : EVA 0 mais FC > 110 - reevaluer la douleur ou rechercher une autre cause")
        if gcs == 15 and spo2 < 88:
            attention.append("Incoherence : GCS 15 mais SpO2 < 88% - verifier le capteur et la position")

        # Situations a haut risque
        if "Anticoagulants / AOD" in atcd and "cranien" in motif.lower():
            danger.append("DANGER - TC sous anticoagulants : TDM cerebral URGENT - risque d'hematome majore")
        if "Anticoagulants / AOD" in atcd and ("AVC" in motif or "neurologique" in motif.lower()):
            danger.append("DANGER - AVC suspect sous AOD : CONTRE-INDICATION thrombolyse - neurologue IMMEDIAT")
        if "allergie" in motif.lower() and details.get("dyspnee"):
            danger.append("ANAPHYLAXIE SEVERE : Adrenaline 0.5 mg IM immediate (Adrenaline Sterop 1 mg/ml)")
        if news2 >= 5 and temp >= 38.5:
            danger.append("SEPSIS GRAVE : NEWS2 >= 5 + fievre - hemocultures AVANT antibiotiques dans l'heure")
        if pas is not None and pas > 0 and pas < 90 and fc > 100:
            si = round(fc / pas, 1)
            danger.append(f"CHOC PROBABLE : Shock Index {si} (FC {fc} / PAS {pas}) - 2 VVP + remplissage NaCl 0.9%")
        if spo2 < 85 or fr >= 40:
            danger.append(f"DETRESSE RESPIRATOIRE : SpO2 {spo2}% / FR {fr}/min - O2 haut debit + preparer IOT")
        if gcs <= 8:
            danger.append(f"COMA : GCS {gcs}/15 - protection des voies aeriennes - PLS - evaluer intubation")
        if temp <= 32:
            danger.append(f"HYPOTHERMIE SEVERE : T {temp}C - rechauffement actif - risque fibrillation ventriculaire")
        if temp >= 41:
            danger.append(f"HYPERTHERMIE MALIGNE : T {temp}C - refroidissement immediat - appel reanimateur")
        if "Immunodepression" in atcd and temp >= 38.5:
            attention.append("NEUTROPENIE FEBRILE possible : hemogramme urgent + antibiotiques sans attendre les resultats")

    except (TypeError, ValueError):
        attention.append("Erreur verification coherence - verifier les parametres saisis")
    return danger, attention, info


def suggerer_bilan(motif, details, fc, pas, spo2, fr, gcs, temp, age, atcd, news2, niveau):
    """Retourne les bilans recommandes selon motif et gravite."""
    b = {"Biologie": [], "Imagerie": [], "ECG / Monitoring": [], "Gestes immediats": [], "Avis specialiste": []}
    try:
        if niveau in ["M", "1", "2"]:
            b["Biologie"] += ["Hemogramme complet + plaquettes", "Ionogramme, creatinine", "Glycemie (mg/dl)", "Groupe ABO / Rh / RAI"]
            b["ECG / Monitoring"] += ["Monitoring cardiorespiratoire continu", "SpO2 continue", "VVP gros calibre"]
        if "thoracique" in motif.lower() or "SCA" in motif:
            b["Biologie"]       += ["Troponine Hs T0 + T1h", "D-Dimeres si EP", "NT-proBNP si IC"]
            b["ECG / Monitoring"] += ["ECG 12 derivations - URGENT", "Repeter ECG a 30 min"]
            b["Imagerie"]       += ["Radiographie thorax face"]
            b["Gestes immediats"] += ["Aspirine 250 mg si SCA non contre-indique", "O2 si SpO2 < 95%"]
        if "AVC" in motif or "neurologique" in motif.lower():
            b["Biologie"]       += ["Hemogramme + coagulation (TP, TCA, fibrinogene)", "Glycemie (mg/dl)"]
            b["Imagerie"]       += ["TDM cerebral sans injection - URGENT", "IRM si disponible"]
            b["Avis specialiste"] += ["Neurologue vasculaire urgent"]
            b["Gestes immediats"] += ["ALERTE FILIERE STROKE - door-to-needle < 60 min"]
        if "dyspnee" in motif.lower() or "respiratoire" in motif.lower():
            b["Biologie"]       += ["Gazometrie arterielle", "D-Dimeres si EP"]
            b["Imagerie"]       += ["Radiographie thorax", "Echographie pulmonaire si disponible"]
            b["Gestes immediats"] += ["O2 - objectif SpO2 > 94%", "Position semi-assise (Fowler 45)"]
        if "traumatisme" in motif.lower() and niveau in ["M", "1", "2"]:
            b["Biologie"]       += ["Bilan pre-transfusionnel (groupe, Rh, RAI, Coombs)", "Lactates"]
            b["Imagerie"]       += ["CT-scanner corps entier si polytrauma", "Echographie FAST"]
            b["Gestes immediats"] += ["Compression directe + garrot si membre", "2 VVP + remplissage NaCl 0.9%"]
        if "fievre" in motif.lower() or (temp >= 38.5 and news2 >= 3):
            b["Biologie"]       += ["Hemocultures x2 AVANT antibiotiques", "Lactates", "CRP, PCT, hemogramme"]
            b["Gestes immediats"] += ["Hemocultures AVANT antibiotherapie", "Antibiotiques si sepsis grave"]
        if "allergie" in motif.lower():
            b["Gestes immediats"] += ["Adrenaline 0.5 mg IM", "Antihistaminique + corticosteroides IV", "Remplissage NaCl 0.9%"]
        if "hypoglycemie" in motif.lower():
            b["Gestes immediats"] += ["Glycemie capillaire IMMEDIATE (mg/dl)", "Glucose 30% 50 ml IV si inconscient", "Glucagon 1 mg IM/SC si acces IV impossible"]
        if "intoxication" in motif.lower():
            b["Biologie"]       += ["Screening toxicologique urinaire + sanguin", "Paracetamol + ethanol systematiques"]
            b["ECG / Monitoring"] += ["ECG - toxiques cardiotropes"]
            b["Avis specialiste"] += ["Centre Antipoisons Belgique : 070 245 245"]
    except (TypeError, ValueError):
        pass
    return {k: v for k, v in b.items() if v}


# ==============================================================================
# [6] PERSISTANCE - Registre anonyme local (RGPD)
# ==============================================================================

FICHIER_REGISTRE = "akir_registre_anon.json"


def charger_registre():
    """Charge le registre anonyme depuis le fichier JSON local."""
    if os.path.exists(FICHIER_REGISTRE):
        try:
            with open(FICHIER_REGISTRE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def sauvegarder_registre(patients):
    """Sauvegarde le registre anonyme dans le fichier JSON local."""
    try:
        with open(FICHIER_REGISTRE, "w", encoding="utf-8") as f:
            json.dump(patients, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def ajouter_au_registre(donnees):
    """
    Ajoute un patient anonyme au registre.
    RGPD : suppression systematique des donnees nominatives avant stockage.
    """
    registre = charger_registre()
    donnees.pop("nom", None)
    donnees.pop("prenom", None)
    donnees["uid"]        = str(uuid.uuid4())[:8].upper()
    donnees["date_heure"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    donnees["date"]       = datetime.now().strftime("%Y-%m-%d")
    registre.insert(0, donnees)
    sauvegarder_registre(registre)
    return donnees["uid"]


def supprimer_du_registre(uid):
    """Supprime un patient du registre par son UID anonyme."""
    registre = charger_registre()
    registre = [p for p in registre if p.get("uid") != uid]
    sauvegarder_registre(registre)


def rechercher_registre(query):
    """Recherche dans le registre par donnees cliniques anonymes uniquement."""
    registre = charger_registre()
    if not query:
        return registre
    q = query.lower().strip()
    return [p for p in registre
            if q in f"{p.get('motif','')} {p.get('age','')} {p.get('niveau','')} {p.get('cat','')} {p.get('date_heure','')}".lower()]


# ==============================================================================
# [7] UI - Composants Streamlit
# ==============================================================================

def render_banniere_critique(news2_score):
    """
    Banniere d'alerte critique si NEWS2 >= 7.
    Securite clinique : alerte visuelle standardisee, rouge medical D32F2F.
    """
    if news2_score >= 7:
        st.markdown(
            f'<div class="banniere-critique">'
            f'<div class="banniere-critique-titre">ALERTE CRITIQUE - NEWS2 = {news2_score}</div>'
            f'<div class="banniere-critique-detail">Appel medical immediat requis - Transfert dechocage - Medecin senior</div>'
            f'</div>',
            unsafe_allow_html=True
        )


def render_bannieres_alerte(news2, sil_score, fc, pas, spo2, fr, gcs, temp):
    """Affiche les bannieres d'alerte clinique selon les parametres vitaux."""
    render_banniere_critique(news2)

    if 5 <= news2 < 7:
        st.markdown(
            f'<div class="alerte-attention">NEWS2 = {news2} - Evaluation medicale urgente dans les 30 minutes</div>',
            unsafe_allow_html=True
        )
    if sil_score is not None and sil_score >= 5:
        st.markdown(
            f'<div class="banniere-critique">'
            f'<div class="banniere-critique-titre">DETRESSE RESPIRATOIRE NEONATALE - Silverman = {sil_score}/10</div>'
            f'<div class="banniere-critique-detail">Appel pediatre / neonatologue immediat - Preparer reanimation neonatale</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    if pas and pas > 0 and fc / pas >= 1.0:
        si = round(fc / pas, 1)
        st.markdown(
            f'<div class="alerte-danger">CHOC - Shock Index {si} (FC {fc} / PAS {pas} mmHg) - 2 VVP gros calibre + remplissage NaCl 0.9%</div>',
            unsafe_allow_html=True
        )
    if spo2 < 85 or fr >= 40:
        st.markdown(
            f'<div class="alerte-danger">DETRESSE RESPIRATOIRE - SpO2 {spo2}% / FR {fr}/min - O2 haut debit immediat</div>',
            unsafe_allow_html=True
        )
    if gcs <= 8:
        st.markdown(
            f'<div class="alerte-danger">COMA - GCS {gcs}/15 - Protection voies aeriennes - PLS - Evaluer intubation</div>',
            unsafe_allow_html=True
        )


def render_prescriptions(motif):
    """Affiche les prescriptions anticipees IAO pour le motif selectionne."""
    rx = PRESCRIPTIONS_ANTICIPEES.get(motif)
    if not rx:
        return
    st.markdown('<div class="sec-header">Prescriptions anticipees IAO</div>', unsafe_allow_html=True)
    cols = st.columns(min(len(rx), 3))
    for i, (categorie, items) in enumerate(rx.items()):
        col = cols[i % len(cols)]
        is_urgent = categorie in ["Gestes immediats", "Rappels critiques"]
        items_html = "".join([
            f'<div class="carte-item {"carte-item-urgent" if is_urgent else ""}">{it}</div>'
            for it in items
        ])
        col.markdown(
            f'<div class="carte">'
            f'<div class="carte-titre">{categorie}</div>'
            f'{items_html}'
            f'</div>',
            unsafe_allow_html=True
        )


def render_protocole_douleur_thoracique(frcv_count):
    """Affiche le protocole anticipe douleur thoracique / SCA."""
    st.markdown(
        '<div class="protocole-card">'
        '<div class="protocole-titre">Protocole anticipe - Douleur thoracique / SCA</div>'
        '<div class="protocole-item protocole-item-urgent">ECG 12 derivations dans les 10 minutes suivant l\'arrivee</div>'
        '<div class="protocole-item protocole-item-urgent">Pose VVP 18G minimum</div>'
        '<div class="protocole-item protocole-item-urgent">Bilan biologique : Troponine Hs T0, D-Dimeres, NFS, ionogramme</div>'
        '<div class="protocole-item">Monitoring scope cardiorespiratoire continu</div>'
        '<div class="protocole-item">Aspirine 250 mg PO/IV sauf contre-indication documentee</div>'
        '</div>',
        unsafe_allow_html=True
    )
    if frcv_count >= 2:
        st.markdown(
            f'<div class="alerte-danger">Remontee de tri suggeree : {frcv_count} facteurs de risque cardiovasculaires avec douleur thoracique - Considerer Tri 3A minimum</div>',
            unsafe_allow_html=True
        )


def render_infobulle_news2():
    """Info-bulle criteresNEWS2 officiels."""
    st.markdown(
        '<div class="infobulle">'
        '<div class="infobulle-titre">Score NEWS2 - Criteres officiels (Royal College of Physicians, 2017)</div>'
        '<b>FR :</b> 0 pt (12-20) | 1 pt (9-11 ou 21-24) | 2 pt (25+) | 3 pt (8 ou moins)<br>'
        '<b>SpO2 sans BPCO :</b> 0 pt (96%+) | 1 pt (94-95%) | 2 pt (92-93%) | 3 pt (91% ou moins)<br>'
        '<b>O2 supplementaire :</b> +2 pts<br>'
        '<b>Temperature :</b> 0 pt (36.1-38.0) | 1 pt (35.1-36.0 ou 38.1-39.0) | 2 pt (39.1+) | 3 pt (35.0 ou moins)<br>'
        '<b>PAS :</b> 0 pt (111-219) | 1 pt (101-110) | 2 pt (91-100) | 3 pt (90 ou moins / 220+)<br>'
        '<b>FC :</b> 0 pt (51-90) | 1 pt (41-50 ou 91-110) | 2 pt (111-130) | 3 pt (40 ou moins / 131+)<br>'
        '<b>Conscience :</b> 0 pt (alerte GCS 15) | 3 pts (GCS &lt; 15)<br>'
        '<b>Seuils :</b> 1-4 = faible | 5-6 = modere | 7-8 = eleve | 9+ = critique'
        '</div>',
        unsafe_allow_html=True
    )


def render_infobulle_timi():
    """Info-bulle criteres TIMI."""
    st.markdown(
        '<div class="infobulle">'
        '<div class="infobulle-titre">Score TIMI SCA-ST- (Antman et al., JAMA 2000) - Risque a 14 jours</div>'
        '1 pt : Age 65 ans ou plus<br>'
        '1 pt : 3 FRCV ou plus (HTA, tabac, diabete, ATCD familial, dyslipidemie)<br>'
        '1 pt : Stenose coronaire connue superieure ou egale a 50%<br>'
        '1 pt : Deviation ST superieure ou egale a 0.5 mm<br>'
        '1 pt : 2 crises angor ou plus en 24h<br>'
        '1 pt : Utilisation aspirine dans les 7 jours<br>'
        '1 pt : Biomarqueurs cardiaques eleves (Troponine positive)<br>'
        '<b>Risque :</b> 0-2 = faible | 3-4 = intermediaire | 5-7 = eleve'
        '</div>',
        unsafe_allow_html=True
    )


def render_disclaimer():
    """Bandeau disclaimer juridique et conformite RGPD."""
    st.markdown(
        '<div class="disclaimer">'
        '<div class="disclaimer-titre">Avertissement juridique, clinique et RGPD</div>'
        'AKIR-IAO Project est un outil d\'aide a la decision clinique destine aux infirmier(e)s agrees '
        'exerçant en service d\'accueil des urgences (SAU). Il ne se substitue pas au jugement clinique '
        'du professionnel de sante ni a l\'examen medical. Les niveaux de triage proposes sont fondes sur '
        'la grille FRENCH Triage (SFMU V1.1, 2018) et doivent etre valides par l\'IAO. Les prescriptions '
        'anticipees sont des rappels cliniques et ne constituent pas des prescriptions medicales. '
        'Elles doivent etre validees par le medecin responsable. Les doses indiquees referent au BCFI '
        '(Centre Belge d\'Information Pharmacotherapeutique). En cas de doute, sur-trier et demander un avis medical. '
        'Legislation belge exercice infirmier : AR 18/06/1990 modifie.'
        '<div class="disclaimer-signature">'
        'AKIR-IAO Project v14.0 - par Ismail Ibn-Daifa<br>'
        'Outil d\'aide a la decision - Conformite RGPD : Aucune donnee patient n\'est stockee sur serveur.'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


def echelle_douleur(age_patient):
    """
    Retourne (score, nom_echelle, interpretation, css_classe) selon l'age.
    Echelles : FLACC (< 3 ans), Wong-Baker (3-8 ans), EVA (>= 8 ans).
    """
    if age_patient < 3:
        st.markdown("**Echelle FLACC** - Nourrisson et enfant de moins de 3 ans")
        st.caption("Observation comportementale - 5 criteres cotes 0 a 2")
        items = {
            "Visage (grimace, froncement sourcils)":   ["0 - Aucune expression particuliere",   "1 - Grimace occasionnelle",       "2 - Froncement permanent / menton tremblant"],
            "Jambes (agitation, position)":            ["0 - Position normale / detendue",      "1 - Genees, agitees, tendues",    "2 - Crispees ou extension ruades"],
            "Activite (corps, posture)":               ["0 - Allonge, calme",                   "1 - Se tortille, se balance",     "2 - Arquee, rigide ou convulsions"],
            "Pleurs (cri, sanglots)":                  ["0 - Pas de pleurs",                    "1 - Gemissements, soupirs",       "2 - Pleurs continus, cris"],
            "Consolabilite":                           ["0 - Content, detendu",                 "1 - Calme apres contact",         "2 - Difficile a calmer"],
        }
        total = 0
        ca, cb = st.columns(2)
        for i, (lbl, opts) in enumerate(items.items()):
            col = ca if i < 3 else cb
            v = col.selectbox(lbl, opts, key=f"flacc_{i}")
            total += int(v[0])
        if total <= 2:   interp, css = "Douleur legere ou absente", "score-bas"
        elif total <= 6: interp, css = "Douleur moderee - antalgique palier 1 OMS", "score-moy"
        else:            interp, css = "Douleur severe - antalgique IV urgent", "score-haut"
        return total, "FLACC", interp, css

    elif age_patient < 8:
        st.markdown("**Echelle des visages Wong-Baker** - Enfant de 3 a 8 ans")
        st.caption("Montrer les visages et demander : Quel visage montre comment tu te sens ?")
        faces = {
            "0 - Tres heureux, aucune douleur": 0,
            "2 - Un peu de douleur": 2,
            "4 - Douleur un peu plus forte": 4,
            "6 - Douleur encore plus forte": 6,
            "8 - Beaucoup de douleur": 8,
            "10 - Douleur insupportable": 10,
        }
        choix = st.selectbox("Visage choisi par l'enfant", list(faces.keys()), key="wong_baker")
        score = faces[choix]
        if score <= 2:   interp, css = "Douleur legere", "score-bas"
        elif score <= 6: interp, css = "Douleur moderee", "score-moy"
        else:            interp, css = "Douleur severe", "score-haut"
        return score, "Wong-Baker", interp, css

    else:
        st.markdown("**Echelle Visuelle Analogique (EVA)** - Patient de 8 ans et plus")
        options = [str(i) for i in range(11)]
        c1, c2 = st.columns([4, 1])
        with c1:
            score_str = st.select_slider(
                "De 0 (aucune douleur) a 10 (douleur maximale imaginable)",
                options=options, value="0", key="eva_std"
            )
        score = int(score_str)
        with c2:
            st.markdown(f"**{score} / 10**")
        if score <= 3:   interp, css = "Douleur legere - palier 1 OMS", "score-bas"
        elif score <= 6: interp, css = "Douleur moderee - palier 1-2 OMS", "score-moy"
        else:            interp, css = "Douleur severe - palier 2-3 OMS ou IV", "score-haut"
        return score, "EVA", interp, css


# ==============================================================================
# [8] APPLICATION - Point d'entree principal
# ==============================================================================

# --- Etat de session ---
_defaults = {
    'historique_session': [],
    'heure_arrivee':      None,
    'sbar_texte':         "",
    'derniere_reeval':    None,
    'historique_reeval':  [],
    'mode':               'complet',
    'gcs_y':              4,
    'gcs_v':              5,
    'gcs_m':              6,
    'confirmer_suppression': None,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# --- En-tete principal ---
st.markdown(
    '<div class="app-header">'
    '<div class="app-header-title">AKIR-IAO Project</div>'
    '<div class="app-header-sub">Outil d\'aide au triage infirmier - FRENCH Triage SFMU V1.1 - Wallonie, Belgique</div>'
    '</div>',
    unsafe_allow_html=True
)


# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown(
        '<div class="app-header" style="padding:10px 14px;margin-bottom:12px;">'
        '<div class="app-header-title" style="font-size:0.9rem;">AKIR-IAO</div>'
        '<div class="app-header-sub">v14.0 Hospital Pro Edition</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="sidebar-section">Mode d\'interface</div>', unsafe_allow_html=True)
    mode_sel = st.radio("Mode", ["Tri rapide (< 2 min)", "Formulaire complet"], horizontal=True, label_visibility="collapsed")
    st.session_state.mode = "rapide" if "rapide" in mode_sel else "complet"

    st.markdown('<div class="sidebar-section">Chronometre</div>', unsafe_allow_html=True)
    ca, cb = st.columns(2)
    if ca.button("Demarrer", use_container_width=True):
        st.session_state.heure_arrivee    = datetime.now()
        st.session_state.derniere_reeval  = datetime.now()
        st.session_state.historique_reeval = []
    if cb.button("Reinitialiser", use_container_width=True):
        st.session_state.heure_arrivee    = None
        st.session_state.derniere_reeval  = None
        st.session_state.historique_reeval = []

    if st.session_state.heure_arrivee:
        elapsed = datetime.now() - st.session_state.heure_arrivee
        m, s = divmod(int(elapsed.total_seconds()), 60)
        h, m = divmod(m, 60)
        st.markdown(f'<div class="chrono">{h:02d}:{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chrono-label">Arrivee {st.session_state.heure_arrivee.strftime("%H:%M")}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="chrono">--:--:--</div>', unsafe_allow_html=True)
        st.markdown('<div class="chrono-label">En attente</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Patient (anonyme - RGPD)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="alerte-info" style="font-size:0.72rem;padding:7px 10px;margin-bottom:8px;">'
        'Conformite RGPD : aucun nom ni prenom collecte. Identifiant anonyme genere automatiquement.'
        '</div>',
        unsafe_allow_html=True
    )
    age = st.number_input("Age (annees)", 0, 120, 45, key="sb_age")
    atcd = st.multiselect("Antecedents / Facteurs de risque", [
        "HTA", "Diabete", "Tabac", "Dyslipidemie", "ATCD familial coronarien",
        "Insuffisance cardiaque", "BPCO",
        "Anticoagulants / AOD", "Grossesse", "Immunodepression", "Neoplasie"
    ])
    allergies = st.text_input("Allergies connues", "RAS", key="sb_allergies")
    o2_supp   = st.checkbox("O2 supplementaire a l'admission")

    nb_reg = len(charger_registre())
    st.markdown(f'<div class="sidebar-section">Registre : {nb_reg} patient(s)</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="sidebar-sig">AKIR-IAO Project<br>par Ismail Ibn-Daifa</div>'
        '<div class="sidebar-legal">FRENCH Triage (adapt. SIAMU Belgique)<br>Ref. SFMU V1.1 - BCFI - AR 18/06/1990</div>',
        unsafe_allow_html=True
    )


# ==============================================================================
# ONGLETS PRINCIPAUX
# ==============================================================================
if st.session_state.mode == "rapide":
    onglets = st.tabs([
        "Tri rapide", "Reevaluation",
        "Historique", "Registre", "Calculateur perfusion"
    ])
    t_rapide, t_reeval, t_histo, t_registre, t_perfusion = onglets
    t_complet = t_scores = None
else:
    onglets = st.tabs([
        "Signes vitaux", "Anamnese", "Triage et SBAR",
        "Scores complementaires", "Calculateur perfusion",
        "Reevaluation", f"Historique ({len(st.session_state.historique_session)})", "Registre"
    ])
    t_vitaux, t_anamnese, t_triage, t_scores, t_perfusion, t_reeval, t_histo, t_registre = onglets
    t_rapide = None

# Variables constantes par defaut
temp = fc = pas = spo2 = fr = gcs = None


# ==============================================================================
# MODE TRI RAPIDE
# ==============================================================================
if st.session_state.mode == "rapide":
    with t_rapide:
        st.markdown('<div class="sec-header">Constantes vitales</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        temp = c1.number_input("Temperature (C)", 30.0, 45.0, 37.0, 0.1, key="r_temp")
        fc   = c2.number_input("FC (bpm)", 20, 220, 80, key="r_fc")
        pas  = c3.number_input("PAS (mmHg)", 40, 260, 120, key="r_pas")
        c4, c5, c6 = st.columns(3)
        spo2 = c4.number_input("SpO2 (%)", 50, 100, 98, key="r_spo2")
        fr   = c5.number_input("FR (/min)", 5, 60, 16, key="r_fr")
        gcs  = c6.number_input("GCS (3-15)", 3, 15, 15, key="r_gcs")

        si = round(fc / pas, 2) if pas > 0 else 0
        si_css = "badge-crit" if si >= 1.0 else ("badge-warn" if si >= 0.8 else "badge-ok")
        st.markdown(f'Shock Index : <span class="badge-vital {si_css}">{si}</span>', unsafe_allow_html=True)

        bpco_f = "BPCO" in atcd
        news2, n2_warns = calculer_news2(fr, spo2, o2_supp, temp, pas, fc, gcs, bpco_f)
        n2_label, n2_css = niveau_news2(news2)
        for w in n2_warns:
            st.markdown(f'<div class="alerte-attention">{w}</div>', unsafe_allow_html=True)
        st.markdown(f'<span class="news2-val {n2_css}">{n2_label}</span>', unsafe_allow_html=True)

        st.markdown('<div class="sec-header">Motif principal</div>', unsafe_allow_html=True)
        MOTIFS_RAPIDES = [
            "Douleur thoracique / SCA", "Dyspnee / insuffisance respiratoire",
            "AVC / Deficit neurologique", "Alteration de conscience / Coma",
            "Traumatisme cranien", "Hypotension arterielle",
            "Tachycardie / tachyarythmie", "Fievre",
            "Douleur abdominale", "Allergie / anaphylaxie",
            "Hypoglycemie", "Convulsions", "Autres"
        ]
        motif = st.selectbox("Motif de recours", MOTIFS_RAPIDES, key="r_motif")
        cat   = "TRI RAPIDE"

        eva_score = int(st.select_slider(
            "EVA - Douleur de 0 (aucune) a 10 (maximale)",
            options=[str(i) for i in range(11)], value="0", key="r_eva"
        ))
        eva_echelle = "EVA"
        details = {"eva": eva_score}

        # Protocole anticipe douleur thoracique + FRCV
        if motif == "Douleur thoracique / SCA":
            st.markdown('<div class="sec-header">Facteurs de risque cardiovasculaires</div>', unsafe_allow_html=True)
            fx = st.columns(4)
            frcv_vals = [
                fx[0].checkbox("HTA", key="r_frcv_hta", value="HTA" in atcd),
                fx[1].checkbox("Diabete", key="r_frcv_diab", value="Diabete" in atcd),
                fx[2].checkbox("Tabac", key="r_frcv_tab", value="Tabac" in atcd),
                fx[3].checkbox("ATCD coronarien", key="r_frcv_atcd"),
            ]
            frcv_count = sum(frcv_vals)
            details["frcv_count"] = frcv_count
            render_protocole_douleur_thoracique(frcv_count)

        if st.button("Calculer le triage", type="primary", use_container_width=True):
            niveau, justif, critere = french_triage(motif, details, fc, pas, spo2, fr, gcs, temp, age, news2)
            tri_label = LABELS_TRI[niveau]
            secteur   = SECTEURS_TRI[niveau]

            render_bannieres_alerte(news2, None, fc, pas, spo2, fr, gcs, temp)

            st.markdown(
                f'<div class="tri-carte {CSS_TRI[niveau]}">'
                f'<div class="tri-niveau">{tri_label}</div>'
                f'<div class="tri-detail">NEWS2 {news2} | EVA {eva_score}/10 | {justif}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            st.info(f"**Orientation :** {secteur}")

            code_anon = f"PT-{datetime.now().strftime('%H%M%S')}"
            sbar = generer_sbar(
                age, motif, cat, atcd, allergies, o2_supp, temp, fc, pas, spo2, fr, gcs,
                news2, n2_label, eva_score, eva_echelle, "", "", "", "",
                details, niveau, tri_label, justif, critere, secteur,
                code_anon=code_anon
            )
            st.session_state.sbar_texte = sbar

            st.session_state.historique_session.insert(0, {
                "heure": datetime.now().strftime("%H:%M"), "age": age, "motif": motif,
                "cat": cat, "eva": eva_score, "news2": news2, "niveau": niveau,
                "temp": temp, "fc": fc, "pas": pas, "spo2": spo2, "fr": fr, "gcs": gcs,
                "atcd": atcd, "allergies": allergies, "sbar": sbar, "alertes_danger": 0,
            })

        if st.session_state.sbar_texte:
            st.markdown('<div class="sec-header">Transmission SBAR - DPI-Ready</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sbar-bloc">{st.session_state.sbar_texte}</div>', unsafe_allow_html=True)
            st.download_button(
                "Telecharger SBAR (.txt)",
                data=st.session_state.sbar_texte,
                file_name=f"SBAR_AKIR_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        render_disclaimer()


# ==============================================================================
# MODE FORMULAIRE COMPLET
# ==============================================================================
else:
    # ---- SIGNES VITAUX ----
    with t_vitaux:
        st.markdown('<div class="sec-header">Constantes vitales</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        temp = c1.number_input("Temperature (C)", 30.0, 45.0, 37.0, 0.1)
        fc   = c1.number_input("FC (bpm)", 20, 220, 80)
        pas  = c2.number_input("PAS Systolique (mmHg)", 40, 260, 120)
        spo2 = c2.number_input("SpO2 (%)", 50, 100, 98)
        fr   = c3.number_input("FR (resp/min)", 5, 60, 16)
        gcs  = c3.number_input("GCS (3-15)", 3, 15, 15)

        st.markdown('<div class="sec-header">Surveillance clinique</div>', unsafe_allow_html=True)
        a1, a2, a3, a4, a5 = st.columns(5)
        a1.markdown(f"**Temperature** {badge_vital(temp, 36, 35, 38, 40.5, ' C')}", unsafe_allow_html=True)
        a2.markdown(f"**FC** {badge_vital(fc, 50, 40, 100, 130, ' bpm')}", unsafe_allow_html=True)
        a3.markdown(f"**PAS** {badge_vital(pas, 100, 90, 180, 220, ' mmHg')}", unsafe_allow_html=True)
        a4.markdown(f"**SpO2** {badge_vital(spo2, 94, 90, 100, 101, '%')}", unsafe_allow_html=True)
        a5.markdown(f"**FR** {badge_vital(fr, 12, 8, 20, 25, '/min')}", unsafe_allow_html=True)

        si = round(fc / pas, 2) if pas > 0 else 0
        si_css = "badge-crit" if si >= 1.0 else ("badge-warn" if si >= 0.8 else "badge-ok")
        st.markdown(
            f'**Shock Index** : <span class="badge-vital {si_css}">{si}</span>'
            f'{"  -- Choc hemodynamique probable" if si >= 1 else ""}',
            unsafe_allow_html=True
        )

        st.markdown('<div class="sec-header">Score NEWS2</div>', unsafe_allow_html=True)
        with st.expander("Criteres officiels NEWS2 - cliquer pour afficher"):
            render_infobulle_news2()

        bpco_f = "BPCO" in atcd
        news2, n2_warns = calculer_news2(fr, spo2, o2_supp, temp, pas, fc, gcs, bpco_f)
        n2_label, n2_css = niveau_news2(news2)

        for w in n2_warns:
            st.markdown(f'<div class="alerte-attention">{w}</div>', unsafe_allow_html=True)

        cn, ci = st.columns([1, 2])
        cn.markdown(f'<span class="news2-val {n2_css}">{n2_label}</span>', unsafe_allow_html=True)
        interp_n2 = {
            "news2-bas":   ("Surveillance standard", "Reevaluation >= 12h."),
            "news2-moyen": ("Surveillance rapprochee", "Reevaluation dans l'heure."),
            "news2-haut":  ("Surveillance urgente", "Evaluation medicale immediate."),
            "news2-crit":  ("URGENCE ABSOLUE", "Transfert dechocage immediat."),
        }
        ti, di = interp_n2[n2_css]
        ci.markdown(f"**{ti}** - {di}")

        render_bannieres_alerte(news2, None, fc, pas, spo2, fr, gcs, temp)

    # ---- ANAMNESE ----
    with t_anamnese:
        if temp is None: temp = 37.0; fc = 80; pas = 120; spo2 = 98; fr = 16; gcs = 15

        st.markdown('<div class="sec-header">Evaluation de la douleur</div>', unsafe_allow_html=True)
        eva_score, eva_echelle, eva_interp, eva_css = echelle_douleur(age)
        st.markdown(f'<span class="score-val {eva_css}">{eva_score}/10 ({eva_echelle})</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="score-interp">{eva_interp}</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-header">Anamnese PQRST</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            p_pqrst = st.text_input("P - Provoque / Pallie par", placeholder="Effort, repos, position...")
            q_pqrst = st.selectbox("Q - Qualite / Type", ["Sourd", "Etau", "Brulure", "Coup de poignard", "Electrique", "Tension", "Pesanteur", "Crampe"])
            r_pqrst = st.text_input("R - Region / Irradiation", placeholder="Bras, machoire, dos, epaule...")
        with col2:
            t_onset = st.text_input("T - Temps / Duree", placeholder="Depuis 30 min, debut brutal...")

        st.markdown('<div class="sec-header">Motif de recours - Classification FRENCH</div>', unsafe_allow_html=True)
        DICT_MOTIFS = {
            "CARDIO-CIRCULATOIRE": [
                "Arret cardiorespiratoire", "Hypotension arterielle", "Douleur thoracique / SCA",
                "Tachycardie / tachyarythmie", "Bradycardie / bradyarythmie",
                "Hypertension arterielle", "Dyspnee / insuffisance respiratoire", "Palpitations"
            ],
            "RESPIRATOIRE": ["Asthme / aggravation BPCO", "Hemoptysie", "Corps etranger voies aeriennes"],
            "NEUROLOGIE": [
                "AVC / Deficit neurologique", "Alteration de conscience / Coma", "Convulsions",
                "Cephalee", "Vertiges / trouble de l'equilibre", "Confusion / desorientation"
            ],
            "TRAUMATOLOGIE": [
                "Traumatisme avec amputation", "Traumatisme abdomen / thorax / cervical",
                "Traumatisme cranien", "Brulure", "Traumatisme bassin / hanche / femur / rachis",
                "Traumatisme membre / epaule", "Plaie", "Electrisation", "Agression sexuelle / sevices"
            ],
            "ABDOMINAL": ["Hematemese / vomissement de sang", "Rectorragie / melena", "Douleur abdominale"],
            "GENITO-URINAIRE": [
                "Douleur lombaire / colique nephretique", "Retention d'urine / anurie",
                "Douleur testiculaire / torsion", "Hematurie"
            ],
            "GYNECO-OBSTETRIQUE": [
                "Accouchement imminent", "Probleme de grossesse (1er/2eme T)",
                "Probleme de grossesse (3eme T)", "Meno-metrorragie"
            ],
            "PSYCHIATRIE / INTOXICATION": [
                "Idee / comportement suicidaire", "Troubles du comportement / psychiatrie",
                "Intoxication medicamenteuse", "Intoxication non medicamenteuse"
            ],
            "INFECTIOLOGIE": ["Fievre"],
            "METABOLIQUE": [
                "Hyperglycemie", "Hypoglycemie", "Hypothermie",
                "Coup de chaleur / insolation", "Allergie / anaphylaxie"
            ],
            "ORL / OPHTALMOLOGIE": ["Epistaxis", "Corps etranger / brulure oculaire", "Trouble visuel / cecite"],
        }
        cat   = st.selectbox("Categorie", list(DICT_MOTIFS.keys()))
        motif = st.selectbox("Motif principal", DICT_MOTIFS[cat])

        # Conseils score par motif
        hints_scores = {
            "Douleur thoracique / SCA": "Score TIMI recommande (onglet Scores complementaires)",
            "Accouchement imminent": "Score Malinas recommande (onglet Scores complementaires)",
            "Brulure": "Score Brulure + formule de Baux (onglet Scores complementaires)",
            "Alteration de conscience / Coma": "GCS detaille recommande (onglet Scores complementaires)",
        }
        if motif in hints_scores:
            st.markdown(f'<div class="alerte-info">{hints_scores[motif]}</div>', unsafe_allow_html=True)

        # Prescriptions anticipees
        render_prescriptions(motif)

        details = {"eva": eva_score}

        # Protocole anticipe douleur thoracique avec FRCV
        if motif == "Douleur thoracique / SCA":
            st.markdown('<div class="sec-header">Facteurs de risque cardiovasculaires (FRCV)</div>', unsafe_allow_html=True)
            st.caption("Si 2 FRCV ou plus avec douleur thoracique, le niveau de tri sera automatiquement remonte a 3A minimum.")
            fx = st.columns(5)
            frcv_hta    = fx[0].checkbox("HTA", key="c_frcv_hta",  value="HTA" in atcd)
            frcv_diab   = fx[1].checkbox("Diabete", key="c_frcv_diab", value="Diabete" in atcd)
            frcv_tab    = fx[2].checkbox("Tabac", key="c_frcv_tab",  value="Tabac" in atcd)
            frcv_dysli  = fx[3].checkbox("Dyslipidemie", key="c_frcv_dys", value="Dyslipidemie" in atcd)
            frcv_atcd   = fx[4].checkbox("ATCD coronarien", key="c_frcv_atcd")
            frcv_count  = sum([frcv_hta, frcv_diab, frcv_tab, frcv_dysli, frcv_atcd])
            details["frcv_count"] = frcv_count
            render_protocole_douleur_thoracique(frcv_count)

        # Questions discriminantes par motif
        QUESTIONS_GUIDEES = {
            "Douleur thoracique / SCA": [
                ("ECG realise ?", "ecg_fait"),
                ("ECG anormal ?", "ecg_anormal"),
                ("Douleur typique (retrosternale, constrictive, irradiation bras/machoire) ?", "douleur_typique"),
                ("Duree superieure a 20 min ?", "duree_longue"),
            ],
            "Dyspnee / insuffisance respiratoire": [
                ("Peut parler en phrases completes ?", "parole_ok"),
                ("Tirage intercostal ou sibilants audibles ?", "tirage"),
                ("Orthopnee (dort assis) ?", "orthopnee"),
            ],
            "AVC / Deficit neurologique": [
                ("Deficit moteur ou facial ?", "deficit_moteur"),
                ("Aphasie ou trouble du langage ?", "aphasie"),
                ("Heure exacte de debut connue ?", "heure_debut_connue"),
                ("Delai inferieur a 4h30 ?", "delai_ok"),
            ],
            "Traumatisme cranien": [
                ("Perte de connaissance initiale ?", "pdc"),
                ("Vomissements repetes ?", "vomissements_repetes"),
                ("Sous anticoagulants ou AOD ?", "aod_avk"),
            ],
            "Douleur abdominale": [
                ("Defense ou contracture abdominale ?", "defense"),
                ("Fievre associee ?", "fievre_assoc"),
            ],
            "Fievre": [
                ("T superieure a 40C ou inferieure a 35.2C ?", "temp_extreme"),
                ("Confusion ou purpura ?", "confusion"),
                ("Hypotension ou Shock Index >= 1 ?", "hypotension"),
            ],
            "Cephalee": [
                ("Cephalee inhabituelle (1er episode) ?", "inhabituelle"),
                ("Debut brutal (coup de tonnerre) ?", "brutale"),
                ("Fievre ou raideur de la nuque ?", "fievre_assoc"),
            ],
            "Allergie / anaphylaxie": [
                ("Dyspnee ou stridor ?", "dyspnee"),
                ("Chute tensionnelle ou malaise ?", "mauvaise_tolerance"),
            ],
        }

        questions = QUESTIONS_GUIDEES.get(motif, [])
        if questions:
            st.markdown("**Questions discriminantes FRENCH :**")
            cq1, cq2 = st.columns(2)
            for i, (lbl, key) in enumerate(questions):
                col = cq1 if i % 2 == 0 else cq2
                details[key] = col.checkbox(lbl, key=f"qg_{key}")

        # Questions specifiques complementaires
        if motif == "Douleur thoracique / SCA":
            details['ecg']                    = st.selectbox("ECG", ["Normal", "Anormal typique SCA", "Anormal non typique"])
            details['douleur_type']           = st.selectbox("Type de douleur", ["Atypique", "Typique persistante/intense", "Type coronaire"])
            details['comorbidites_coronaires'] = st.checkbox("Comorbidites coronaires documentees")
        elif motif == "Dyspnee / insuffisance respiratoire":
            details['parole_ok'] = st.radio("Phrases completes possibles ?", [True, False], format_func=lambda x: "Oui" if x else "Non", horizontal=True)
            c1a, c1b = st.columns(2)
            details['orthopnee'] = c1a.checkbox("Orthopnee")
            details['tirage']    = c1b.checkbox("Tirage intercostal")
        elif motif == "AVC / Deficit neurologique":
            details['delai_heures'] = st.number_input("Delai depuis debut des symptomes (heures)", 0.0, 72.0, 2.0, 0.5)
        elif motif == "Traumatisme cranien":
            c1a, c1b = st.columns(2)
            details['pdc']                    = c1a.checkbox("Perte de connaissance initiale")
            details['vomissements_repetes']   = c1a.checkbox("Vomissements repetes")
            details['aod_avk']                = c1b.checkbox("AOD ou AVK")
            details['deficit_neuro']          = c1b.checkbox("Deficit neurologique")
        elif motif == "Douleur abdominale":
            c1a, c1b = st.columns(2)
            details['defense']          = c1a.checkbox("Defense abdominale")
            details['contracture']      = c1a.checkbox("Contracture")
            details['regressive']       = c1b.checkbox("Douleur regressive")
            details['mauvaise_tolerance'] = c1b.checkbox("Mauvaise tolerance")
        elif motif == "Fievre":
            c1a, c1b = st.columns(2)
            details['confusion']          = c1a.checkbox("Confusion")
            details['purpura']            = c1a.checkbox("Purpura")
            details['mauvaise_tolerance'] = c1b.checkbox("Mauvaise tolerance")
        elif motif == "Allergie / anaphylaxie":
            details['dyspnee']            = st.checkbox("Dyspnee ou oedeme larynge")
            details['mauvaise_tolerance'] = st.checkbox("Chute tensionnelle ou mauvaise tolerance")
        elif motif in ["Intoxication medicamenteuse", "Intoxication non medicamenteuse"]:
            details['mauvaise_tolerance']   = st.checkbox("Mauvaise tolerance")
            details['intention_suicidaire'] = st.checkbox("Intention suicidaire")
            details['cardiotropes']         = st.checkbox("Substances cardiotropes")
        elif motif == "Brulure":
            details['etendue']     = st.checkbox("Etendue > 10% de la surface corporelle")
            details['main_visage'] = st.checkbox("Localisation main, visage ou perinee")
        elif motif in ["Hematemese / vomissement de sang", "Rectorragie / melena"]:
            details['abondante'] = st.checkbox("Saignement abondant")
        elif motif == "Plaie":
            details['saignement_actif'] = st.checkbox("Saignement actif")
            details['delabrant']        = st.checkbox("Plaie delabrante")
            details['main']             = st.checkbox("Localisation main")
            details['superficielle']    = st.checkbox("Plaie superficielle")
        elif motif == "Meno-metrorragie":
            details['grossesse'] = st.checkbox("Grossesse connue ou suspectee")
            details['abondante'] = st.checkbox("Saignement abondant")
        elif motif in ["Douleur lombaire / colique nephretique", "Hematurie", "Douleur testiculaire / torsion"]:
            details['intense']           = st.checkbox("Douleur intense")
            details['regressive']        = st.checkbox("Douleur regressive")
            details['suspicion_torsion'] = st.checkbox("Suspicion torsion") if "testiculaire" in motif else False
            details['abondante_active']  = st.checkbox("Saignement actif") if "Hematurie" in motif else False
        elif motif == "Hyperglycemie":
            # Glycemie en mg/dl (standard belge)
            gl_mgdl = st.number_input("Glycemie (mg/dl)", 0, 1500, 180, 10)
            gl_mmol = mgdl_vers_mmol(gl_mgdl)
            st.caption(f"Equivalent : {gl_mmol} mmol/l")
            details['glycemie_mgdl'] = gl_mgdl
            details['cetose_elevee']   = st.checkbox("Cetose elevee (bandelette urinaire)")
            details['cetose_positive'] = st.checkbox("Cetose positive")
        elif motif == "Hypoglycemie":
            gl_mgdl_hypo = st.number_input("Glycemie capillaire (mg/dl)", 0, 500, 60, 5)
            st.caption(f"Equivalent : {mgdl_vers_mmol(gl_mgdl_hypo)} mmol/l | Seuil severe : < 54 mg/dl | Seuil modere : < 70 mg/dl")
            details['glycemie_mgdl']      = gl_mgdl_hypo
            details['mauvaise_tolerance'] = st.checkbox("Mauvaise tolerance")
        elif motif == "Troubles du comportement / psychiatrie":
            details['agitation']      = st.checkbox("Agitation ou violence")
            details['hallucinations'] = st.checkbox("Hallucinations")
        elif motif in ["Tachycardie / tachyarythmie", "Bradycardie / bradyarythmie", "Palpitations"]:
            details['mauvaise_tolerance'] = st.checkbox("Mauvaise tolerance hemodynamique")
            details['malaise']            = st.checkbox("Malaise associe")
        elif motif == "Hypertension arterielle":
            details['sf_associes'] = st.checkbox("Symptomes fonctionnels associes (cephalee, trouble visuel, douleur thoracique)")
        elif motif in ["Traumatisme abdomen / thorax / cervical", "Traumatisme bassin / hanche / femur / rachis", "Traumatisme membre / epaule"]:
            details['cinetique']          = st.selectbox("Cinetique traumatique", ["Faible", "Haute"])
            details['mauvaise_tolerance'] = st.checkbox("Mauvaise tolerance")
            details['penetrant']          = st.checkbox("Traumatisme penetrant") if "abdomen" in motif else False
            if "membre" in motif.lower() or "epaule" in motif.lower():
                details['impotence_totale']  = st.checkbox("Impotence totale")
                details['deformation']       = st.checkbox("Deformation")
                details['impotence_moderee'] = st.checkbox("Impotence moderee")
                details['ischemie']          = st.checkbox("Ischemie distale")
        elif motif == "Epistaxis":
            details['abondant_actif']     = st.checkbox("Epistaxis abondante active")
            details['abondant_resolutif'] = st.checkbox("Epistaxis abondante resolutive")
        elif motif in ["Corps etranger / brulure oculaire", "Trouble visuel / cecite"]:
            details['chimique'] = st.checkbox("Brulure chimique")
            details['intense']  = st.checkbox("Douleur intense")
            details['brutal']   = st.checkbox("Debut brutal")
        elif motif == "Convulsions":
            details['crises_multiples']        = st.checkbox("Crises multiples ou en cours")
            details['confusion_post_critique'] = st.checkbox("Confusion post-critique")
        elif motif == "Cephalee":
            details['inhabituelle'] = st.checkbox("Cephalee inhabituelle (1er episode)")
            details['brutale']      = st.checkbox("Debut brutal")
            details['fievre_assoc'] = st.checkbox("Fievre associee")
        elif motif == "Electrisation":
            details['pdc']           = st.checkbox("Perte de connaissance")
            details['foudre']        = st.checkbox("Foudroiement")
            details['haute_tension'] = st.checkbox("Haute tension")

    # ---- TRIAGE ET SBAR ----
    with t_triage:
        # Recuperation des variables si onglets non visites
        if temp is None:  temp = 37.0; fc = 80; pas = 120; spo2 = 98; fr = 16; gcs = 15
        if 'motif' not in dir() or motif is None: motif = "Fievre"
        if 'details' not in dir() or details is None: details = {}
        if 'eva_score' not in dir(): eva_score = 0; eva_echelle = "EVA"
        if 'cat' not in dir(): cat = "METABOLIQUE"
        if 'p_pqrst' not in dir(): p_pqrst = ""; q_pqrst = ""; r_pqrst = ""; t_onset = ""

        bpco_f = "BPCO" in atcd
        news2, n2_warns = calculer_news2(fr, spo2, o2_supp, temp, pas, fc, gcs, bpco_f)
        n2_label, n2_css = niveau_news2(news2)

        for w in n2_warns:
            st.markdown(f'<div class="alerte-attention">{w}</div>', unsafe_allow_html=True)

        niveau, justif, critere = french_triage(
            motif, details, fc, pas, spo2, fr, gcs, temp, age, news2,
            glycemie_mgdl=details.get("glycemie_mgdl")
        )
        tri_label = LABELS_TRI[niveau]
        secteur   = SECTEURS_TRI[niveau]

        render_bannieres_alerte(news2, None, fc, pas, spo2, fr, gcs, temp)

        # Alerte reevaluation en retard
        if st.session_state.derniere_reeval:
            mins_ec = (datetime.now() - st.session_state.derniere_reeval).total_seconds() / 60
            if mins_ec > DELAIS_TRI.get(niveau, 60):
                st.markdown(
                    f'<div class="alerte-danger">Reevaluation en retard : {int(mins_ec)} min ecoulees - delai maximum {DELAIS_TRI[niveau]} min pour Tri {niveau}</div>',
                    unsafe_allow_html=True
                )

        st.markdown(
            f'<div class="tri-carte {CSS_TRI[niveau]}">'
            f'<div class="tri-niveau">{tri_label}</div>'
            f'<div class="tri-detail">NEWS2 {news2} | EVA {details.get("eva", 0)}/10 | {justif}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        st.info(f"**Orientation :** {secteur}")
        st.caption(f"Reference : {critere}")

        st.markdown('<div class="sec-header">Alertes de securite clinique</div>', unsafe_allow_html=True)
        al_d, al_a, _ = verifier_coherence(fc, pas, spo2, fr, gcs, temp, details.get("eva", 0), motif, atcd, details, news2)
        for a in al_d: st.markdown(f'<div class="alerte-danger">{a}</div>', unsafe_allow_html=True)
        for a in al_a: st.markdown(f'<div class="alerte-attention">{a}</div>', unsafe_allow_html=True)
        if not al_d and not al_a:
            st.markdown('<div class="alerte-ok">Aucune incoherence clinique detectee.</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-header">Bilans recommandes</div>', unsafe_allow_html=True)
        bilans = suggerer_bilan(motif, details, fc, pas, spo2, fr, gcs, temp, age, atcd, news2, niveau)
        if bilans:
            cols_b = st.columns(min(len(bilans), 3))
            for i, (bnom, bitems) in enumerate(bilans.items()):
                col = cols_b[i % len(cols_b)]
                html_items = "".join([f'<div class="carte-item">{it}</div>' for it in bitems])
                col.markdown(
                    f'<div class="carte"><div class="carte-titre">{bnom}</div>{html_items}</div>',
                    unsafe_allow_html=True
                )

        st.markdown('<div class="sec-header">Transmission SBAR - DPI-Ready</div>', unsafe_allow_html=True)
        code_anon = f"PT-{datetime.now().strftime('%H%M%S')}"

        if st.button("Generer la transmission SBAR", type="primary", use_container_width=True):
            sbar = generer_sbar(
                age, motif, cat, atcd, allergies, o2_supp, temp, fc, pas, spo2, fr, gcs,
                news2, n2_label,
                details.get("eva", 0),
                eva_echelle if 'eva_echelle' in dir() else "EVA",
                p_pqrst, q_pqrst, r_pqrst, t_onset,
                details, niveau, tri_label, justif, critere, secteur,
                gcs_y=st.session_state.gcs_y,
                gcs_v=st.session_state.gcs_v,
                gcs_m=st.session_state.gcs_m,
                code_anon=code_anon
            )
            st.session_state.sbar_texte = sbar
            st.session_state.historique_session.insert(0, {
                "heure": datetime.now().strftime("%H:%M"), "age": age, "motif": motif,
                "cat": cat, "eva": details.get("eva", 0), "news2": news2, "niveau": niveau,
                "temp": temp, "fc": fc, "pas": pas, "spo2": spo2, "fr": fr, "gcs": gcs,
                "atcd": atcd, "allergies": allergies, "sbar": sbar,
                "alertes_danger": len(al_d),
            })
            st.success("SBAR genere et enregistre dans l'historique de session.")

        if st.session_state.sbar_texte:
            st.markdown(f'<div class="sbar-bloc">{st.session_state.sbar_texte}</div>', unsafe_allow_html=True)
            cd1, cd2 = st.columns(2)
            cd1.download_button(
                "Telecharger SBAR (.txt)",
                data=st.session_state.sbar_texte,
                file_name=f"SBAR_AKIR_{datetime.now().strftime('%Y%m%d_%H%M')}_Tri{niveau}.txt",
                mime="text/plain",
                use_container_width=True,
            )
            if cd2.button("Enregistrer au registre (anonyme)", use_container_width=True):
                uid = ajouter_au_registre({
                    "age": age, "motif": motif, "cat": cat, "niveau": niveau,
                    "news2": news2, "eva": details.get("eva", 0),
                    "temp": temp, "fc": fc, "pas": pas, "spo2": spo2, "fr": fr, "gcs": gcs,
                    "allergies": allergies, "sbar": st.session_state.sbar_texte,
                })
                st.success(f"Enregistrement dans le registre anonyme - identifiant : {uid}")

        render_disclaimer()

    # ---- SCORES COMPLEMENTAIRES ----
    with t_scores:
        if temp is None: temp = 37.0; fc = 80; pas = 120; spo2 = 98; fr = 16; gcs = 15
        bpco_f = "BPCO" in atcd
        news2, _ = calculer_news2(fr, spo2, o2_supp, temp, pas, fc, gcs, bpco_f)

        sc1, sc2 = st.columns(2)

        # GCS DETAILLE
        with sc1:
            st.markdown('<div class="sec-header">Glasgow Coma Scale (GCS)</div>', unsafe_allow_html=True)
            with st.expander("Criteres GCS"):
                st.markdown("""
**Yeux (Y) :** 4 = spontane | 3 = a la voix | 2 = a la douleur | 1 = absent  
**Verbal (V) :** 5 = oriente | 4 = confus | 3 = mots | 2 = sons | 1 = absent  
**Moteur (M) :** 6 = obeit | 5 = localise | 4 = evitement | 3 = flexion | 2 = extension | 1 = absent
                """)
            gy = st.select_slider("Yeux (Y)", options=[1, 2, 3, 4], value=4, key="gcs_gy")
            gv = st.select_slider("Verbal (V)", options=[1, 2, 3, 4, 5], value=5, key="gcs_gv")
            gm = st.select_slider("Moteur (M)", options=[1, 2, 3, 4, 5, 6], value=6, key="gcs_gm")
            st.session_state.gcs_y = gy
            st.session_state.gcs_v = gv
            st.session_state.gcs_m = gm
            gcs_calc, gcs_errs = calculer_gcs(gy, gv, gm)
            for e in gcs_errs: st.warning(e)
            if gcs_calc <= 8:    g_css, g_int = "score-haut", "Coma - protection des voies aeriennes urgente"
            elif gcs_calc <= 13: g_css, g_int = "score-moy",  "Alteration moderee de la conscience"
            elif gcs_calc == 14: g_css, g_int = "score-moy",  "Alteration legere de la conscience"
            else:                g_css, g_int = "score-bas",  "Eveille et oriente"
            st.markdown(f'<span class="score-val {g_css}">GCS {gcs_calc}/15</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">{g_int}</div>', unsafe_allow_html=True)

        # TIMI
        with sc2:
            st.markdown('<div class="sec-header">Score TIMI - SCA-ST-</div>', unsafe_allow_html=True)
            with st.expander("Criteres TIMI"):
                render_infobulle_timi()
            t_a65 = st.checkbox("Age >= 65 ans", key="timi_a65")
            t_frcv = st.number_input("Nombre de FRCV", 0, 5, 0, key="timi_frcv")
            t_sten = st.checkbox("Stenose coronaire connue >= 50%", key="timi_sten")
            t_aspi = st.checkbox("Aspirine dans les 7 derniers jours", key="timi_aspi")
            t_trop = st.checkbox("Troponine positive", key="timi_trop")
            t_st   = st.checkbox("Deviation ST >= 0.5 mm", key="timi_st")
            t_cris = st.number_input("Crises angor en 24h", 0, 10, 0, key="timi_cris")
            timi_sc, timi_errs = calculer_timi(age, t_frcv, t_sten, t_aspi, t_trop, t_st, t_cris)
            for e in timi_errs: st.warning(e)
            if timi_sc <= 2:   t_css, t_int = "score-bas",  "Risque faible (< 10%)"
            elif timi_sc <= 4: t_css, t_int = "score-moy",  "Risque intermediaire (10-20%)"
            else:              t_css, t_int = "score-haut", "Risque eleve (> 20%) - Cardiologue urgent"
            st.markdown(f'<span class="score-val {t_css}">TIMI {timi_sc}/7</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">{t_int}</div>', unsafe_allow_html=True)

        sc3, sc4 = st.columns(2)

        # SILVERMAN
        with sc3:
            st.markdown('<div class="sec-header">Score de Silverman - Detresse neonatale</div>', unsafe_allow_html=True)
            with st.expander("Criteres Silverman"):
                st.markdown("0 = absent | 1 = modere | 2 = intense. Score maximal = 10. Score >= 5 = pediatre urgent.")
            opts = [0, 1, 2]
            s_bt  = st.select_slider("Balancement thoraco-abdominal", options=opts, key="sil_bt")
            s_ti  = st.select_slider("Tirage intercostal", options=opts, key="sil_ti")
            s_rss = st.select_slider("Retraction sus-sternale", options=opts, key="sil_rss")
            s_an  = st.select_slider("Battement aile du nez", options=opts, key="sil_an")
            s_gei = st.select_slider("Geignement expiratoire", options=opts, key="sil_gei")
            sil_sc, sil_errs = calculer_silverman(s_bt, s_ti, s_rss, s_an, s_gei)
            for e in sil_errs: st.warning(e)
            render_bannieres_alerte(news2, sil_sc, fc, pas, spo2, fr, gcs, temp)
            if sil_sc <= 2:   s_css, s_int = "score-bas",  "Normal - pas de detresse"
            elif sil_sc <= 4: s_css, s_int = "score-moy",  "Detresse legere - surveillance rapprochee"
            else:             s_css, s_int = "score-haut", "Detresse severe - pediatre immediat"
            st.markdown(f'<span class="score-val {s_css}">Silverman {sil_sc}/10</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">{s_int}</div>', unsafe_allow_html=True)

        # MALINAS + BRULURE
        with sc4:
            st.markdown('<div class="sec-header">Score de Malinas - Transport obstetrical</div>', unsafe_allow_html=True)
            with st.expander("Criteres Malinas"):
                st.markdown("0-2 pts par item. Score >= 8 = ne pas transporter (accouchement imminent).")
            m_par  = st.select_slider("Parite (0=nullipare, 1=multipare, 2=multipare >=3)", options=[0,1,2], key="mal_par")
            m_dur  = st.select_slider("Duree travail (0=<3h, 1=3-5h, 2=>5h)", options=[0,1,2], key="mal_dur")
            m_con  = st.select_slider("Duree contractions (0=<1min, 1=1min, 2=>1min)", options=[0,1,2], key="mal_con")
            m_int  = st.select_slider("Intervalle (0=>5min, 1=3-5min, 2=<3min)", options=[0,1,2], key="mal_int")
            m_poc  = st.select_slider("Poche des eaux (0=intacte, 1=rompue<1h, 2=rompue>1h)", options=[0,1,2], key="mal_poc")
            mal_sc, mal_errs = calculer_malinas(m_par, m_dur, m_con, m_int, m_poc)
            for e in mal_errs: st.warning(e)
            if mal_sc <= 5:   m_css, m_int = "score-bas",  "Transport possible"
            elif mal_sc <= 7: m_css, m_int = "score-moy",  "Transport sous surveillance medicale"
            else:             m_css, m_int = "score-haut", "Ne pas transporter - accouchement imminent"
            st.markdown(f'<span class="score-val {m_css}">Malinas {mal_sc}/10</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="score-interp">{m_int}</div>', unsafe_allow_html=True)

        # BRULURES
        st.markdown('<div class="sec-header">Brulures - Regle des 9 de Wallace + Formule de Baux</div>', unsafe_allow_html=True)
        with st.expander("Regle des 9 de Wallace et formule de Baux"):
            st.markdown("""
**Regle des 9 :** Tete = 9% | Tronc anterieur = 18% | Tronc posterieur = 18% | Bras = 9% x2 | Jambe = 18% x2 | Perinee = 1%  
**Formule de Baux :** Age + SCB (%) -> pronostic mortalite. > 100 = severe. > 120 = quasi-letal.
            """)
        br1, br2 = st.columns(2)
        scb_pct    = br1.number_input("Surface corporelle brulee (%)", 0, 100, 10, key="scb_pct")
        profondeur = br2.selectbox("Profondeur", ["1er degre", "2eme degre superficiel", "2eme degre profond", "3eme degre"])
        scb_val, baux_val, pronostic, burn_errs = calculer_brulure(scb_pct, age)
        for e in burn_errs: st.warning(e)
        if baux_val < 80:   b_css = "score-bas"
        elif baux_val < 100: b_css = "score-moy"
        else:               b_css = "score-haut"
        st.markdown(f'<span class="score-val {b_css}">SCB {scb_val}% - Baux {baux_val}</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="score-interp">{profondeur} | {pronostic}</div>', unsafe_allow_html=True)

        # Recapitulatif
        st.markdown('<div class="sec-header">Recapitulatif des scores</div>', unsafe_allow_html=True)
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("TIMI", f"{timi_sc}/7")
        r2.metric("Silverman", f"{sil_sc}/10")
        r3.metric("GCS calcule", f"{gcs_calc}/15")
        r4.metric("Malinas", f"{mal_sc}/10")


# ==============================================================================
# CALCULATEUR DE PERFUSION (onglet commun aux deux modes)
# ==============================================================================
with t_perfusion:
    st.markdown('<div class="sec-header">Calculateur de perfusion - Formule V/T</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="alerte-info">Les doses indiquees referent au BCFI (Centre Belge d\'Information Pharmacotherapeutique). '
        'Toute prescription medicamenteuse doit etre validee par le medecin responsable.</div>',
        unsafe_allow_html=True
    )

    poids_kg = st.number_input("Poids du patient (kg)", 1.0, 200.0, 70.0, 0.5, key="perf_poids")

    st.markdown(
        '<div class="infobulle">'
        '<div class="infobulle-titre">Formule du debit de perfusion</div>'
        'Debit (ml/h) = Volume (ml) / Duree (h)<br>'
        'Equivalence gouttes : 1 ml = 20 gouttes (facteur standard). Debit en gouttes/min = Debit (ml/h) / 3.'
        '</div>',
        unsafe_allow_html=True
    )

    p1, p2 = st.columns(2)
    vol_ml  = p1.number_input("Volume a perfuser (ml)", 1, 5000, 500, 50, key="perf_vol")
    dur_h   = p2.number_input("Duree de perfusion (h)", 0.25, 24.0, 4.0, 0.25, key="perf_dur")

    debit_res, debit_err = calculer_debit_perfusion(vol_ml, dur_h)
    if debit_err:
        st.markdown(f'<div class="alerte-attention">{debit_err}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="carte" style="text-align:center;">'
            f'<div class="perf-result">{debit_res["ml_h"]} ml/h</div>'
            f'<div class="perf-label">{vol_ml} ml perfuses en {dur_h}h - Equivalence : {debit_res["gttes_min"]} gouttes/min</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="sec-header">Doses de charge - Protocoles BCFI Belgique</div>', unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)

    # Paracetamol IV (Perfusalgan / Dafalgan IV)
    with d1:
        parac_res, parac_err = dose_paracetamol_iv(poids_kg)
        if parac_err:
            st.markdown(f'<div class="alerte-attention">{parac_err}</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="dose-carte">'
                f'<div class="dose-titre">Paracetamol IV (Perfusalgan/Dafalgan IV)</div>'
                f'<div class="dose-valeur">{parac_res["dose_g"]} g ({parac_res["dose_mg"]:.0f} mg)</div>'
                f'{parac_res["admin"]}<br>'
                f'Intervalle : {parac_res["intervalle"]}<br>'
                f'Maximum : {parac_res["max_jour"]}<br>'
                f'<small style="color:var(--texte-aide);">{parac_res["reference"]}</small>'
                f'</div>',
                unsafe_allow_html=True
            )

    # Morphine IV
    with d2:
        morph_res, morph_err = dose_morphine_iv(poids_kg, age)
        if morph_err:
            st.markdown(f'<div class="alerte-attention">{morph_err}</div>', unsafe_allow_html=True)
        else:
            note_age_html = f'<br><b style="color:var(--rouge-crit);">{morph_res["note_age"]}</b>' if morph_res["note_age"] else ""
            st.markdown(
                f'<div class="dose-carte">'
                f'<div class="dose-titre">Morphine IV - Titration antalgie</div>'
                f'<div class="dose-valeur">{morph_res["bolus_min"]}-{morph_res["bolus_max"]} mg / bolus</div>'
                f'{morph_res["admin"]}<br>'
                f'Objectif : {morph_res["objectif"]}{note_age_html}<br>'
                f'Antidote : {morph_res["antidote"]}<br>'
                f'<small style="color:var(--texte-aide);">{morph_res["reference"]}</small>'
                f'</div>',
                unsafe_allow_html=True
            )

    # Glucose 30% IV
    with d3:
        gl_res, gl_err = dose_glucose_hypoglycemie(poids_kg, "IV")
        if gl_err:
            st.markdown(f'<div class="alerte-attention">{gl_err}</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="dose-carte">'
                f'<div class="dose-titre">Glucose 30% IV (hypoglycemie)</div>'
                f'<div class="dose-valeur">{gl_res["dose_g"]} g</div>'
                f'{gl_res["volume"]}<br>'
                f'{gl_res["controle"]}<br>'
                f'<small style="color:var(--texte-aide);">{gl_res["reference"]}</small>'
                f'</div>',
                unsafe_allow_html=True
            )

    # Adrenaline IM
    st.markdown('<div class="sec-header">Adrenaline IM - Anaphylaxie (BCFI)</div>', unsafe_allow_html=True)
    adre_res, adre_err = dose_adrenaline_anaphylaxie(poids_kg)
    if adre_err:
        st.markdown(f'<div class="alerte-attention">{adre_err}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="dose-carte" style="border-left-color:var(--rouge-crit);">'
            f'<div class="dose-titre" style="color:var(--rouge-crit);">Adrenaline IM - Anaphylaxie</div>'
            f'<div class="dose-valeur">{adre_res["dose_mg"]} mg IM</div>'
            f'Voie : {adre_res["voie"]}<br>'
            f'Note : {adre_res["note"]}<br>'
            f'{adre_res["repeter"]}<br>'
            f'{adre_res["moniteur"]}<br>'
            f'<small style="color:var(--texte-aide);">{adre_res["reference"]}</small>'
            f'</div>',
            unsafe_allow_html=True
        )

    # Glucagon IM/SC (alternative si acces IV impossible)
    st.markdown('<div class="sec-header">Glucagon IM/SC - Alternative si acces IV impossible</div>', unsafe_allow_html=True)
    gluc_res, gluc_err = dose_glucose_hypoglycemie(poids_kg, "IM")
    if gluc_err:
        st.markdown(f'<div class="alerte-attention">{gluc_err}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="dose-carte">'
            f'<div class="dose-titre">Glucagon (GlucaGen HypoKit)</div>'
            f'<div class="dose-valeur">{gluc_res["dose"]}</div>'
            f'{gluc_res["note"]}<br>'
            f'{gluc_res["controle"]}<br>'
            f'<small style="color:var(--texte-aide);">{gluc_res["reference"]}</small>'
            f'</div>',
            unsafe_allow_html=True
        )

    render_disclaimer()


# ==============================================================================
# REEVALUATION STRUCTUREE (commun aux deux modes)
# ==============================================================================
with t_reeval:
    st.markdown("### Reevaluations structurees")
    st.caption("Chaque reevaluation est comparee a la precedente. La tendance clinique est calculee automatiquement.")

    st.markdown('<div class="sec-header">Nouvelle reevaluation</div>', unsafe_allow_html=True)
    cr1, cr2, cr3 = st.columns(3)
    re_temp = cr1.number_input("Temperature (C)", 30.0, 45.0, 37.0, 0.1, key="re_temp")
    re_fc   = cr1.number_input("FC (bpm)", 20, 220, 80, key="re_fc")
    re_pas  = cr2.number_input("PAS (mmHg)", 40, 260, 120, key="re_pas")
    re_spo2 = cr2.number_input("SpO2 (%)", 50, 100, 98, key="re_spo2")
    re_fr   = cr3.number_input("FR (/min)", 5, 60, 16, key="re_fr")
    re_gcs  = cr3.number_input("GCS (3-15)", 3, 15, 15, key="re_gcs")

    re_news2, re_warns = calculer_news2(re_fr, re_spo2, o2_supp, re_temp, re_pas, re_fc, re_gcs, "BPCO" in atcd)
    re_label, re_css   = niveau_news2(re_news2)

    for w in re_warns:
        st.markdown(f'<div class="alerte-attention">{w}</div>', unsafe_allow_html=True)

    re_motif = "Fievre"
    if st.session_state.historique_session:
        re_motif = st.session_state.historique_session[-1].get("motif", "Fievre")
    re_niveau, re_justif, re_ref = french_triage(re_motif, {}, re_fc, re_pas, re_spo2, re_fr, re_gcs, re_temp, age, re_news2)

    rc1, rc2 = st.columns(2)
    rc1.markdown(f'<span class="news2-val {re_css}">{re_label}</span>', unsafe_allow_html=True)
    rc2.info(f"Triage recalcule : **{LABELS_TRI[re_niveau]}**")

    render_bannieres_alerte(re_news2, None, re_fc, re_pas, re_spo2, re_fr, re_gcs, re_temp)

    if st.button("Enregistrer cette reevaluation", use_container_width=True):
        snap = {
            "heure": datetime.now().strftime("%H:%M"),
            "fc": re_fc, "pas": re_pas, "spo2": re_spo2,
            "fr": re_fr, "gcs": re_gcs, "temp": re_temp,
            "niveau": re_niveau, "news2": re_news2,
        }
        st.session_state.historique_reeval.append(snap)
        st.session_state.derniere_reeval = datetime.now()
        st.success(f"Reevaluation enregistree a {snap['heure']} - Tri {re_niveau}")

    st.markdown('<div class="sec-header">Historique des reevaluations</div>', unsafe_allow_html=True)

    if not st.session_state.historique_reeval:
        st.info("Aucune reevaluation enregistree pour ce patient.")
    else:
        hist_r = st.session_state.historique_reeval

        def tendance(old, new, haut_est_grave=True):
            if new > old:
                sym = "+" if haut_est_grave else "-"
                css = "trend-haut" if haut_est_grave else "trend-bas"
            elif new < old:
                sym = "-" if haut_est_grave else "+"
                css = "trend-bas" if haut_est_grave else "trend-haut"
            else:
                sym, css = "=", "trend-egal"
            return f'<span class="{css}">{sym}</span>'

        ord_niv = {"M": 0, "1": 1, "2": 2, "3A": 3, "3B": 4, "4": 5, "5": 6}
        for i, snap in enumerate(hist_r):
            prev = hist_r[i - 1] if i > 0 else snap
            no   = ord_niv.get(snap['niveau'], 3)
            np_  = ord_niv.get(prev['niveau'], 3)
            if no > np_:   r_css, tendance_txt = "reeval-amelio", "AMELIORATION"
            elif no < np_: r_css, tendance_txt = "reeval-aggrav", "AGGRAVATION"
            else:          r_css, tendance_txt = "reeval-stable", "STABLE"

            label_h = "H0" if i == 0 else f"H+{i}"
            st.markdown(
                f'<div class="reeval-ligne {r_css}">'
                f'<b>{snap["heure"]}</b> ({label_h}) | '
                f'Tri {snap["niveau"]} | NEWS2 {snap.get("news2", "?")} | '
                f'FC {snap["fc"]} {tendance(prev["fc"], snap["fc"])} | '
                f'PAS {snap["pas"]} {tendance(prev["pas"], snap["pas"], False)} | '
                f'SpO2 {snap["spo2"]} {tendance(prev["spo2"], snap["spo2"], False)} | '
                f'GCS {snap["gcs"]} {tendance(prev["gcs"], snap["gcs"], False)} | '
                f'<b>{tendance_txt}</b>'
                f'</div>',
                unsafe_allow_html=True
            )

        if len(hist_r) >= 2:
            first, last = hist_r[0], hist_r[-1]
            st.markdown(
                f"**Bilan global :** {len(hist_r)} reevaluations | "
                f"NEWS2 initial {first.get('news2', '?')} -> {last.get('news2', '?')} | "
                f"Tri {first['niveau']} -> {last['niveau']}"
            )

        if st.button("Effacer l'historique de reevaluation"):
            st.session_state.historique_reeval = []
            st.rerun()


# ==============================================================================
# HISTORIQUE DE SESSION
# ==============================================================================
with t_histo:
    if not st.session_state.historique_session:
        st.info("Aucun patient enregistre dans cette session.")
    else:
        st.markdown(f"**{len(st.session_state.historique_session)} patient(s) enregistre(s) cette session**")
        for i, pat in enumerate(reversed(st.session_state.historique_session), 1):
            css_h = CSS_HIST.get(pat['niveau'], 'hist-4')
            tag   = " - ALERTES DANGER" if pat.get('alertes_danger', 0) > 0 else ""
            st.markdown(
                f'<div class="hist-ligne {css_h}">'
                f'<b>{pat["heure"]}</b> | {pat["age"]} ans | <b>{pat["motif"]}</b> | '
                f'EVA {pat["eva"]}/10 | NEWS2 {pat["news2"]} | Tri {pat["niveau"]}{tag}'
                f'</div>',
                unsafe_allow_html=True
            )
            with st.expander(f"SBAR - Patient n {len(st.session_state.historique_session) - i + 1}"):
                st.markdown(f'<div class="sbar-bloc">{pat["sbar"]}</div>', unsafe_allow_html=True)
                st.download_button(
                    "Telecharger SBAR",
                    data=pat["sbar"],
                    file_name=f"SBAR_{pat['heure'].replace(':', 'h')}_Tri{pat['niveau']}.txt",
                    mime="text/plain",
                    key=f"dl_histo_{i}"
                )
        if st.button("Effacer l'historique de session"):
            st.session_state.historique_session = []
            st.rerun()


# ==============================================================================
# REGISTRE PATIENTS - STOCKAGE ANONYME PERSISTANT
# ==============================================================================
with t_registre:
    st.markdown("### Registre des patients - Donnees anonymes persistantes")
    st.markdown(
        '<div class="alerte-info">Conformite RGPD : ce registre ne contient aucun nom ni prenom. '
        'Chaque patient est identifie par un code anonyme genere automatiquement. '
        'Les donnees sont stockees localement sur ce poste uniquement.</div>',
        unsafe_allow_html=True
    )

    registre = charger_registre()

    if registre:
        compt_niv = {}
        for p in registre:
            n = p.get("niveau", "?")
            compt_niv[n] = compt_niv.get(n, 0) + 1
        auj = sum(1 for p in registre if p.get("date") == datetime.now().strftime("%Y-%m-%d"))

        cs = st.columns(5)
        cs[0].markdown(f'<div class="reg-stat"><div class="reg-stat-num">{len(registre)}</div><div class="reg-stat-label">Total</div></div>', unsafe_allow_html=True)
        cs[1].markdown(f'<div class="reg-stat"><div class="reg-stat-num">{auj}</div><div class="reg-stat-label">Aujourd\'hui</div></div>', unsafe_allow_html=True)
        urg = sum(v for k, v in compt_niv.items() if k in ["M", "1", "2"])
        cs[2].markdown(f'<div class="reg-stat"><div class="reg-stat-num" style="color:var(--rouge-crit);">{urg}</div><div class="reg-stat-label">Tri M/1/2</div></div>', unsafe_allow_html=True)
        mod = sum(v for k, v in compt_niv.items() if k in ["3A", "3B"])
        cs[3].markdown(f'<div class="reg-stat"><div class="reg-stat-num" style="color:var(--orange-warn);">{mod}</div><div class="reg-stat-label">Tri 3A/3B</div></div>', unsafe_allow_html=True)
        bas = sum(v for k, v in compt_niv.items() if k in ["4", "5"])
        cs[4].markdown(f'<div class="reg-stat"><div class="reg-stat-num" style="color:var(--vert-ok);">{bas}</div><div class="reg-stat-label">Tri 4/5</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="sec-header">Recherche et filtres</div>', unsafe_allow_html=True)
    cs1, cs2, cs3 = st.columns([3, 2, 2])
    q_rech = cs1.text_input("Rechercher (motif, age, niveau, date...)", placeholder="ex : SCA, 60 ans, Tri 2...", key="reg_rech", label_visibility="collapsed")
    filtre_niv = cs2.selectbox("Filtrer par niveau", ["Tous", "M", "1", "2", "3A", "3B", "4", "5"], key="reg_filtre")

    filtres = rechercher_registre(q_rech) if q_rech else registre
    if filtre_niv != "Tous":
        filtres = [p for p in filtres if p.get("niveau") == filtre_niv]

    if cs3.button("Exporter tout (JSON)", use_container_width=True) and registre:
        st.download_button(
            "Telecharger le registre anonyme",
            data=json.dumps(registre, ensure_ascii=False, indent=2),
            file_name=f"AKIR_registre_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            key="export_registre"
        )

    st.markdown(f'<div class="sec-header">Patients ({len(filtres)} resultat{"s" if len(filtres) != 1 else ""})</div>', unsafe_allow_html=True)

    if not filtres:
        st.markdown(
            '<div style="text-align:center;padding:40px 20px;color:var(--texte-aide);">'
            'Aucun patient dans le registre.<br>Utilisez le bouton "Enregistrer au registre" apres un triage.'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        for idx, pat in enumerate(filtres):
            uid = pat.get("uid", "?")
            niv = pat.get("niveau", "?")

            st.markdown(
                f'<div class="reg-carte">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">'
                f'  <div style="font-family:DM Mono,monospace;font-size:0.95rem;font-weight:500;color:var(--texte-titre);">Code : {uid} - {pat.get("age", "?")} ans</div>'
                f'  <div style="font-family:DM Mono,monospace;font-size:0.68rem;color:var(--texte-aide);">{pat.get("date_heure", "")}</div>'
                f'</div>'
                f'<div style="margin-bottom:8px;">'
                f'  <span class="reg-badge reg-{niv}">Tri {niv}</span>'
                f'  <span style="font-size:0.82rem;color:var(--texte-aide);">{pat.get("motif", "")} - {pat.get("cat", "")}</span>'
                f'</div>'
                f'<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:4px 14px;font-size:0.8rem;">'
                f'  <div><span style="font-size:0.62rem;color:var(--texte-aide);text-transform:uppercase;">Temperature</span><br><b>{pat.get("temp", "")} C</b></div>'
                f'  <div><span style="font-size:0.62rem;color:var(--texte-aide);text-transform:uppercase;">FC</span><br><b>{pat.get("fc", "")} bpm</b></div>'
                f'  <div><span style="font-size:0.62rem;color:var(--texte-aide);text-transform:uppercase;">PAS</span><br><b>{pat.get("pas", "")} mmHg</b></div>'
                f'  <div><span style="font-size:0.62rem;color:var(--texte-aide);text-transform:uppercase;">SpO2</span><br><b>{pat.get("spo2", "")} %</b></div>'
                f'  <div><span style="font-size:0.62rem;color:var(--texte-aide);text-transform:uppercase;">NEWS2</span><br><b>{pat.get("news2", "")}</b></div>'
                f'  <div><span style="font-size:0.62rem;color:var(--texte-aide);text-transform:uppercase;">EVA</span><br><b>{pat.get("eva", "")}/10</b></div>'
                f'  <div><span style="font-size:0.62rem;color:var(--texte-aide);text-transform:uppercase;">Allergies</span><br><b>{pat.get("allergies", "RAS")}</b></div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

            cr1, cr2, cr3 = st.columns([3, 1, 1])
            with cr1:
                with st.expander(f"SBAR complet - {uid}"):
                    sbar_txt = pat.get("sbar", "Aucun SBAR disponible.")
                    st.markdown(f'<div class="sbar-bloc">{sbar_txt}</div>', unsafe_allow_html=True)
                    st.download_button(
                        "Telecharger SBAR",
                        data=sbar_txt,
                        file_name=f"SBAR_AKIR_{uid}_{niv}.txt",
                        mime="text/plain",
                        key=f"dl_reg_{uid}_{idx}"
                    )

            if cr3.button("Supprimer", key=f"del_{uid}_{idx}", use_container_width=True):
                st.session_state.confirmer_suppression = uid

            if st.session_state.confirmer_suppression == uid:
                st.warning(f"Confirmer la suppression du patient {uid} ?")
                cf1, cf2, _ = st.columns([1, 1, 3])
                if cf1.button("Confirmer", key=f"conf_{uid}_{idx}", type="primary"):
                    supprimer_du_registre(uid)
                    st.session_state.confirmer_suppression = None
                    st.success(f"Patient {uid} supprime du registre.")
                    st.rerun()
                if cf2.button("Annuler", key=f"ann_{uid}_{idx}"):
                    st.session_state.confirmer_suppression = None
                    st.rerun()

    if registre:
        st.markdown("---")
        st.markdown('<div class="sec-header">Administration</div>', unsafe_allow_html=True)
        with st.expander("Zone de purge - Action irreversible"):
            st.warning("Cette action supprimera l'ensemble des patients du registre de maniere definitive.")
            if st.button("Purger l'ensemble du registre", type="primary", key="purge_tout"):
                sauvegarder_registre([])
                st.session_state.confirmer_suppression = None
                st.success("Registre vide.")
                st.rerun()

    render_disclaimer()
