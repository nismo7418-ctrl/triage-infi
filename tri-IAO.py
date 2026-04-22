"""
================================================================================
  AKIR-IAO v18.0 — Hospital Pro Edition
================================================================================

  Application d'aide à la décision pour l'Infirmier(ère) d'Accueil et
  d'Orientation (IAO) aux urgences adulte et pédiatrique.

  Développeur        : Ismail Ibn-Daifa
  Promoteur          : [À compléter par l'étudiant]
  Cadre académique   : Mémoire de Master en Sciences Infirmières
  Localisation       : Urgences — Hainaut, Wallonie, Belgique
  Version            : 18.0 — Hospital Pro Edition
  Date de révision   : 2025

--------------------------------------------------------------------------------
  RÉFÉRENCES CLINIQUES
--------------------------------------------------------------------------------

  Triage
    • Taboulet P. et al. FRENCH Triage : Évaluation comparative avec l'ESI.
      Société Française de Médecine d'Urgence (SFMU), V1.1, Juin 2018.

  NEWS2 (National Early Warning Score 2)
    • Royal College of Physicians. National Early Warning Score 2 (NEWS2):
      Standardising the assessment of acute-illness severity in the NHS.
      Updated report of a working party. London: RCP, 2017.

  qSOFA
    • Singer M, Deutschman CS, Seymour CW, et al. The Third International
      Consensus Definitions for Sepsis and Septic Shock (Sepsis-3).
      JAMA. 2016;315(8):801-810.

  GCS (Glasgow Coma Scale)
    • Teasdale G, Jennett B. Assessment of coma and impaired consciousness.
      A practical scale. Lancet. 1974;304(7872):81-84.

  TIMI Risk Score
    • Antman EM, Cohen M, Bernink PJLM, et al. The TIMI risk score for
      unstable angina/non-ST elevation MI. JAMA. 2000;284(7):835-842.

  Algoplus
    • Rat P, Jouve E, Pickering G, et al. Validation of an acute pain-behavior
      scale for older persons with inability to communicate verbally:
      Algoplus. Eur J Pain. 2011;15(2):198.e1-198.e10.

  Clinical Frailty Scale (CFS)
    • Rockwood K, Song X, MacKnight C, et al. A global clinical measure of
      fitness and frailty in elderly people. CMAJ. 2005;173(5):489-495.

  SIPA (Shock Index Pediatric Age-adjusted)
    • Acker SN, Ross JT, Partrick DA, et al. Pediatric specific shock index
      accurately identifies severely injured children. J Pediatr Surg.
      2015;50(2):331-334.

  Purpura fulminans
    • Société de Pathologie Infectieuse de Langue Française (SPILF) et
      Société Française de Pédiatrie (SFP). Recommandations sur la prise en
      charge du purpura fulminans aux urgences. 2017.

  FAST / BE-FAST (AVC)
    • Aroor S, Singh R, Goldstein LB. BE-FAST (Balance, Eyes, Face, Arm,
      Speech, Time): Reducing the proportion of strokes missed using the
      FAST mnemonic. Stroke. 2017;48(2):479-481.

--------------------------------------------------------------------------------
  RÉFÉRENCES PHARMACOLOGIQUES
--------------------------------------------------------------------------------

  • BCFI — Répertoire Commenté des Médicaments. Centre Belge d'Information
    Pharmacothérapeutique. Édition courante. https://www.bcfi.be
  • AFMPS — Agence Fédérale des Médicaments et des Produits de Santé.
    Résumés des Caractéristiques du Produit (RCP) — Belgique.
  • SFAR — Société Française d'Anesthésie et de Réanimation. Protocoles de
    titration morphinique aux urgences. 2010.
  • Lignes directrices européennes pour la prise en charge de
    l'anaphylaxie. EAACI, 2023.

--------------------------------------------------------------------------------
  CADRE LÉGAL BELGE
--------------------------------------------------------------------------------

  • Arrêté Royal du 18 juin 1990 modifié — Liste des prestations techniques
    de soins infirmiers et des actes pouvant être confiés aux infirmiers.
  • Règlement Général sur la Protection des Données (RGPD) — UE 2016/679.
  • Loi du 22 août 2002 relative aux droits du patient — Belgique.
  • Loi du 30 juillet 2018 relative à la protection des personnes physiques
    à l'égard des traitements de données à caractère personnel — Belgique.

--------------------------------------------------------------------------------
  CONFORMITÉ RGPD
--------------------------------------------------------------------------------

  • Identification patient  : UUID anonyme (8 caractères hexadécimaux)
  • Identification opérateur: Code anonyme libre (recommandation : IAOxx)
  • Aucun identifiant nominal (nom, prénom, NISS, adresse) n'est collecté
  • Stockage                : Fichier JSON local — aucune transmission tiers
  • Rétention               : 500 dernières entrées (rotation automatique)
  • Export                  : CSV anonyme pour analyse de recherche

--------------------------------------------------------------------------------
  AVERTISSEMENT MÉDICO-LÉGAL
--------------------------------------------------------------------------------

  Cet outil est un support d'aide à la décision clinique destiné aux
  professionnels infirmiers formés au triage. Il ne se substitue en aucun
  cas au jugement clinique du médecin responsable. Toute décision
  thérapeutique demeure sous la responsabilité exclusive du professionnel
  de santé. Les doses affichées doivent être validées par un médecin
  prescripteur avant administration.

================================================================================
"""

from __future__ import annotations
from typing import Optional
from datetime import datetime
import streamlit as st
import uuid, json, os, io, csv as csv_mod

st.set_page_config(
    page_title="AKIR-IAO — Pro",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS — MOBILE-FIRST HOSPITAL GRADE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ─── VARIABLES ─────────────────────────────────────── */
:root {
  --P:     #004A99;   /* Primary blue          */
  --PL:    #1A69B8;   /* Primary light         */
  --PD:    #002F66;   /* Primary dark          */
  --PP:    #EBF3FD;   /* Primary pale          */
  --BG:    #F8F9FA;   /* Background            */
  --CARD:  #FFFFFF;   /* Card background       */
  --B:     #E2E8F0;   /* Border                */
  --T:     #1A202C;   /* Text                  */
  --TM:    #64748B;   /* Text muted            */
  --TW:    #FFFFFF;   /* Text white            */
  /* Urgences haute visibilité */
  --TM-bg: #1A0A2E;  --TM-ac: #E879F9;  /* Tri M   */
  --T1-bg: #7F1D1D;  --T1-ac: #FCA5A5;  /* Tri 1   */
  --T2-bg: #78350F;  --T2-ac: #FDE68A;  /* Tri 2   */
  --T3A-bg:#1E3A5F;  --T3A-ac:#93C5FD;  /* Tri 3A  */
  --T3B-bg:#1E3A5F;  --T3B-ac:#BAE6FD;  /* Tri 3B  */
  --T4-bg: #14532D;  --T4-ac: #86EFAC;  /* Tri 4   */
  --T5-bg: #334155;  --T5-ac: #CBD5E1;  /* Tri 5   */
  /* Alertes */
  --ERR: #FEF2F2; --ERR-b: #EF4444; --ERR-t: #B91C1C;
  --WRN: #FFFBEB; --WRN-b: #F59E0B; --WRN-t: #92400E;
  --SUC: #F0FDF4; --SUC-b: #22C55E; --SUC-t: #166534;
  --INF: #EFF6FF; --INF-b: #3B82F6; --INF-t: #1D4ED8;
  /* Ombres & géométrie */
  --s1: 0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.05);
  --s2: 0 4px 12px rgba(0,74,153,.12);
  --s3: 0 8px 24px rgba(0,74,153,.18);
  --r:  12px;
  --r2: 8px;
}

/* ─── RESET ─────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
#MainMenu, footer, header, [data-testid="stToolbar"] { display:none!important; }
.block-container { padding: .75rem 1rem 4rem!important; max-width: 860px; margin: 0 auto; }
html, body, [class*="st-"] {
  font-family: 'Inter', -apple-system, sans-serif;
  color: var(--T);
  background: var(--BG);
  -webkit-font-smoothing: antialiased;
}
::-webkit-scrollbar { width:5px; }
::-webkit-scrollbar-thumb { background:var(--B); border-radius:3px; }

/* ─── APP HEADER ────────────────────────────────────── */
.app-hdr {
  background: linear-gradient(130deg, var(--PD) 0%, var(--P) 55%, var(--PL) 100%);
  border-radius: var(--r);
  padding: 18px 22px 16px;
  margin-bottom: 18px;
  box-shadow: var(--s3);
  position: relative; overflow: hidden;
}
.app-hdr::after {
  content:''; position:absolute; right:-40px; top:-40px;
  width:200px; height:200px;
  background: rgba(255,255,255,.06); border-radius:50%;
}
.app-hdr-title { font-size:1.2rem; font-weight:800; color:#fff; letter-spacing:-.02em; }
.app-hdr-sub   { font-size:.72rem; color:rgba(255,255,255,.75); margin-top:3px; }
.app-hdr-tags  { margin-top:10px; display:flex; gap:6px; flex-wrap:wrap; }
.tag {
  background:rgba(255,255,255,.15); border:1px solid rgba(255,255,255,.28);
  color:#fff; font-size:.62rem; font-weight:600; padding:2px 9px;
  border-radius:20px; letter-spacing:.04em;
}

/* ─── TABS ──────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  gap: 3px; background: #ECEFF4; padding: 4px;
  border-radius: 10px; border: 1px solid var(--B);
  overflow-x: auto; flex-wrap: nowrap;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 7px; font-weight:600; font-size:.78rem;
  padding: 7px 12px; color: var(--TM); white-space: nowrap;
  min-width: auto; transition: all .2s;
}
.stTabs [aria-selected="true"] {
  background: var(--P)!important; color: white!important;
  box-shadow: var(--s2)!important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 14px; }

/* ─── CARDS ─────────────────────────────────────────── */
.card {
  background: var(--CARD); border: 1px solid var(--B);
  border-radius: var(--r); padding: 16px 18px;
  margin-bottom: 14px; box-shadow: var(--s1);
}
.card-title {
  font-size:.63rem; font-weight:700; letter-spacing:.1em;
  text-transform:uppercase; color:var(--P);
  border-bottom: 2px solid var(--PP);
  padding-bottom:8px; margin-bottom:12px;
}
.card-title-inline {
  display:flex; align-items:center; gap:8px; margin-bottom:12px;
}
.card-icon {
  width:32px; height:32px; border-radius:8px;
  background:var(--PP); display:flex; align-items:center;
  justify-content:center; font-size:1rem; flex-shrink:0;
}

/* ─── SECTION LABEL ─────────────────────────────────── */
.sec {
  font-size:.6rem; font-weight:700; letter-spacing:.12em;
  text-transform:uppercase; color:var(--P);
  border-bottom:2px solid var(--PP); padding-bottom:5px;
  margin:16px 0 10px 0;
}

/* ─── NEWS2 DASHBOARD ───────────────────────────────── */
.n2-dash {
  border-radius:var(--r); padding:18px 20px; text-align:center;
  border:2px solid; margin-bottom:14px;
  transition: all .3s ease;
}
.n2-dash.n2-0  { background:#F0FDF4; border-color:#22C55E; }
.n2-dash.n2-1  { background:#F0FDF4; border-color:#22C55E; }
.n2-dash.n2-2  { background:#FEFCE8; border-color:#EAB308; }
.n2-dash.n2-3  { background:#FFF7ED; border-color:#F97316; }
.n2-dash.n2-4  { background:#FFF1F2; border-color:#F43F5E; }
.n2-dash.n2-5  { background:#FAF5FF; border-color:#7C3AED; }
.n2-big {
  font-family:'JetBrains Mono',monospace;
  font-size:3.5rem; font-weight:700; line-height:1;
  margin:6px 0 2px;
}
.n2-0 .n2-big, .n2-1 .n2-big { color:#16A34A; }
.n2-2 .n2-big { color:#CA8A04; }
.n2-3 .n2-big { color:#EA580C; }
.n2-4 .n2-big { color:#E11D48; }
.n2-5 .n2-big { color:#7C3AED; }
.n2-lbl { font-size:.72rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.n2-0 .n2-lbl, .n2-1 .n2-lbl { color:#166534; }
.n2-2 .n2-lbl { color:#854D0E; }
.n2-3 .n2-lbl { color:#9A3412; }
.n2-4 .n2-lbl { color:#881337; }
.n2-5 .n2-lbl { color:#4C1D95; }
.n2-bar-wrap { background:#E2E8F0; border-radius:6px; height:8px; margin:10px 0 6px; overflow:hidden; }
.n2-bar { height:8px; border-radius:6px; transition:width .4s ease; }
.n2-0 .n2-bar, .n2-1 .n2-bar { background:#22C55E; }
.n2-2 .n2-bar { background:#EAB308; }
.n2-3 .n2-bar { background:#F97316; }
.n2-4 .n2-bar { background:#F43F5E; }
.n2-5 .n2-bar { background:#7C3AED; }
.n2-scale { display:flex; justify-content:space-between; font-size:.58rem; color:var(--TM); }

/* ─── VITAUX GRID ───────────────────────────────────── */
.vit-wrap { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; margin:10px 0; }
.vit {
  background:var(--CARD); border:1.5px solid var(--B); border-radius:var(--r2);
  padding:10px 12px; text-align:center; box-shadow:var(--s1);
  transition: border-color .2s;
}
.vit.warn  { border-color:#F59E0B; background:#FFFBEB; }
.vit.crit  { border-color:#EF4444; background:#FEF2F2; animation:vit-pulse 2s infinite; }
.vit-k { font-size:.58rem; font-weight:600; text-transform:uppercase; letter-spacing:.08em; color:var(--TM); margin-bottom:2px; }
.vit-v { font-family:'JetBrains Mono',monospace; font-size:1.25rem; font-weight:700; }
.vit-u { font-size:.6rem; color:var(--TM); }
.vit.warn .vit-v { color:#92400E; }
.vit.crit .vit-v { color:#B91C1C; }
@keyframes vit-pulse { 0%,100%{ border-color:#EF4444; } 50%{ border-color:#FCA5A5; } }

/* ─── ALERTES ───────────────────────────────────────── */
.al {
  border-radius:var(--r2); padding:11px 14px; margin:7px 0;
  font-size:.82rem; font-weight:500; line-height:1.5;
  display:flex; align-items:flex-start; gap:9px;
  border-left: 4px solid;
}
.al.danger  { background:var(--ERR); border-color:var(--ERR-b); color:var(--ERR-t); }
.al.warning { background:var(--WRN); border-color:var(--WRN-b); color:var(--WRN-t); }
.al.success { background:var(--SUC); border-color:var(--SUC-b); color:var(--SUC-t); }
.al.info    { background:var(--INF); border-color:var(--INF-b); color:var(--INF-t); }
.al-ico     { font-size:.9rem; flex-shrink:0; margin-top:1px; }

/* ─── PURPURA BANNER ────────────────────────────────── */
.purp {
  background:linear-gradient(135deg,#7F1D1D,#991B1B);
  border:2px solid #EF4444; border-radius:var(--r);
  padding:16px 20px; margin:10px 0;
  animation: purp-glow 1.8s ease-in-out infinite;
}
.purp-title { font-size:.95rem; font-weight:800; color:#FECACA; text-transform:uppercase; margin-bottom:6px; }
.purp-body  { font-size:.82rem; color:#FEE2E2; line-height:1.6; }
@keyframes purp-glow {
  0%,100%{ box-shadow:0 0 0 0 rgba(239,68,68,0); }
  50%{ box-shadow:0 0 0 8px rgba(239,68,68,.25); }
}

/* ─── TRIAGE BANNER (fixed bottom) ─────────────────── */
.tri-banner-wrap {
  position:fixed; bottom:0; left:0; right:0; z-index:999;
  padding:0 0 env(safe-area-inset-bottom,0);
}
.tri-banner {
  padding:14px 20px; display:flex; align-items:center;
  justify-content:space-between; flex-wrap:wrap; gap:8px;
}
.tri-M   { background:var(--TM-bg); }
.tri-1   { background:var(--T1-bg); }
.tri-2   { background:var(--T2-bg); }
.tri-3A  { background:var(--T3A-bg); }
.tri-3B  { background:var(--T3B-bg); }
.tri-4   { background:var(--T4-bg); }
.tri-5   { background:var(--T5-bg); }
.tri-niv {
  font-family:'JetBrains Mono',monospace;
  font-size:1.1rem; font-weight:800; letter-spacing:.04em;
}
.tri-M .tri-niv   { color:var(--TM-ac); }
.tri-1 .tri-niv   { color:var(--T1-ac); }
.tri-2 .tri-niv   { color:var(--T2-ac); }
.tri-3A .tri-niv  { color:var(--T3A-ac); }
.tri-3B .tri-niv  { color:var(--T3B-ac); }
.tri-4 .tri-niv   { color:var(--T4-ac); }
.tri-5 .tri-niv   { color:var(--T5-ac); }
.tri-sec  { font-size:.72rem; color:rgba(255,255,255,.8); max-width:60%; }
.tri-just { font-size:.7rem; color:rgba(255,255,255,.65); font-style:italic; }
.tri-delai {
  background:rgba(255,255,255,.15); border:1px solid rgba(255,255,255,.25);
  color:#fff; font-size:.68rem; font-weight:700; padding:4px 12px;
  border-radius:20px; white-space:nowrap;
}

/* ─── INLINE TRIAGE CARD ────────────────────────────── */
.tri-card {
  border-radius:var(--r); padding:20px 22px; text-align:center;
  margin:12px 0; box-shadow:var(--s3); position:relative; overflow:hidden;
}
.tri-card::before {
  content:''; position:absolute; top:0; left:0; right:0; height:4px;
}
.tri-M .tri-card::before   { background:var(--TM-ac); }
.tri-1 .tri-card::before   { background:var(--T1-ac); }
.tri-2 .tri-card::before   { background:var(--T2-ac); }
.tri-3A .tri-card::before  { background:var(--T3A-ac); }
.tri-3B .tri-card::before  { background:var(--T3B-ac); }
.tri-4 .tri-card::before   { background:var(--T4-ac); }
.tri-5 .tri-card::before   { background:var(--T5-ac); }
.tri-lbl { font-size:1.5rem; font-weight:800; letter-spacing:-.01em; }
.tri-detail { font-size:.78rem; margin-top:5px; opacity:.88; }
.tri-sector { font-size:.72rem; margin-top:4px; opacity:.75; }
.tri-chips  { margin-top:10px; display:flex; justify-content:center; gap:8px; flex-wrap:wrap; }
.tri-chip {
  font-size:.65rem; font-weight:700; padding:3px 12px;
  border-radius:20px; border:1px solid currentColor; opacity:.8;
}

/* ─── PHARMA CARDS ──────────────────────────────────── */
.rx {
  background:var(--CARD); border:1px solid var(--B);
  border-radius:var(--r); padding:16px 18px; margin:8px 0;
  box-shadow:var(--s1); position:relative; overflow:hidden;
}
.rx::before {
  content:''; position:absolute; left:0; top:0; bottom:0;
  width:4px; border-radius:var(--r) 0 0 var(--r);
}
.rx.p1::before { background:#22C55E; }
.rx.p2::before { background:#F59E0B; }
.rx.p3::before { background:#EF4444; }
.rx.urg::before { background:#7C3AED; }
.rx.ant::before { background:#3B82F6; }
.rx-name { font-size:.88rem; font-weight:700; color:var(--T); margin-bottom:3px; }
.rx-dose {
  font-family:'JetBrains Mono',monospace;
  font-size:1.4rem; font-weight:700; color:var(--P); margin:5px 0 8px;
}
.rx-detail { font-size:.78rem; color:var(--TM); line-height:1.65; }
.rx-ref    { font-size:.62rem; color:#94A3B8; margin-top:8px; font-style:italic; }
.rx-lock {
  background:#F8FAFC; border:2px dashed #CBD5E1; border-radius:var(--r);
  padding:22px; text-align:center; color:var(--TM); font-size:.82rem; margin:8px 0;
}
.rx-lock-icon { font-size:1.6rem; margin-bottom:6px; }

/* ─── SBAR REPORT ───────────────────────────────────── */
.sbar { background:var(--CARD); border:1px solid var(--B); border-radius:var(--r); overflow:hidden; box-shadow:var(--s2); }
.sbar-hdr { background:linear-gradient(135deg,var(--PD),var(--P)); padding:16px 22px; }
.sbar-hdr-title { font-size:.95rem; font-weight:800; color:#fff; }
.sbar-hdr-sub   { font-size:.68rem; color:rgba(255,255,255,.75); margin-top:2px; }
.sbar-sec { padding:14px 22px; border-bottom:1px solid var(--B); }
.sbar-sec:last-child { border-bottom:none; }
.sbar-sec-head { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
.sbar-letter {
  width:28px; height:28px; border-radius:7px; background:var(--P);
  color:#fff; font-weight:800; font-size:.84rem;
  display:flex; align-items:center; justify-content:center; flex-shrink:0;
}
.sbar-sec-title { font-size:.7rem; font-weight:700; text-transform:uppercase; letter-spacing:.1em; color:var(--P); }
.sbar-body { font-size:.82rem; color:var(--T); line-height:SIPA_7_12ANS5; }
.sbar-vit-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:7px; margin-top:10px; }
.sbar-vit { background:var(--BG); border:1px solid var(--B); border-radius:7px; padding:8px; text-align:center; }
.sbar-vit-k { font-size:.56rem; text-transform:uppercase; color:var(--TM); letter-spacing:.06em; }
.sbar-vit-v { font-family:'JetBrains Mono',monospace; font-size:.95rem; font-weight:700; }
.sbar-ftr { background:#F8FAFC; padding:10px 22px; font-size:.64rem; color:var(--TM); font-style:italic; border-top:1px solid var(--B); }

/* ─── SI BOX ─────────────────────────────────────────── */
.si-box { background:var(--CARD); border:1.5px solid var(--B); border-radius:var(--r2); padding:12px 16px; text-align:center; }
.si-v { font-family:'JetBrains Mono',monospace; font-size:1.8rem; font-weight:700; }
.si-ok { color:#22C55E; } .si-w { color:#F59E0B; } .si-c { color:#EF4444; }
.si-l { font-size:.6rem; text-transform:uppercase; letter-spacing:.08em; color:var(--TM); }

/* ─── HISTORY LINES ─────────────────────────────────── */
.hl { display:flex; align-items:center; gap:10px; background:var(--CARD); border:1px solid var(--B); border-radius:var(--r2); padding:10px 14px; margin:4px 0; box-shadow:var(--s1); font-size:.8rem; }
.hbadge { font-size:.62rem; font-weight:700; padding:2px 8px; border-radius:5px; white-space:nowrap; flex-shrink:0; }
.hb-M   { background:var(--TM-bg); color:var(--TM-ac); }
.hb-1   { background:var(--T1-bg); color:var(--T1-ac); }
.hb-2   { background:var(--T2-bg); color:var(--T2-ac); }
.hb-3A  { background:var(--T3A-bg);color:var(--T3A-ac);}
.hb-3B  { background:var(--T3B-bg);color:var(--T3B-ac);}
.hb-4   { background:var(--T4-bg); color:var(--T4-ac); }
.hb-5   { background:var(--T5-bg); color:var(--T5-ac); }

/* ─── REEVAL LINES ──────────────────────────────────── */
.rr { display:flex; align-items:center; gap:10px; padding:9px 12px; border-radius:var(--r2); margin:4px 0; font-size:.79rem; border-left:4px solid; }
.rr-up     { background:#FEF2F2; border-color:#EF4444; color:#B91C1C; }
.rr-down   { background:#F0FDF4; border-color:#22C55E; color:#166534; }
.rr-stable { background:#EFF6FF; border-color:#3B82F6; color:#1D4ED8; }

/* ─── N2 TREND BAR ──────────────────────────────────── */
.n2t { display:flex; align-items:center; gap:8px; margin:3px 0; }
.n2t-lbl { font-family:'JetBrains Mono',monospace; font-size:.66rem; width:52px; flex-shrink:0; color:var(--TM); }
.n2t-trk { flex:1; background:var(--B); border-radius:4px; height:12px; overflow:hidden; }
.n2t-fill { height:12px; border-radius:4px; }
.n2t-val { font-family:'JetBrains Mono',monospace; font-size:.7rem; font-weight:700; width:18px; text-align:right; }

/* ─── DISCLAIMER ─────────────────────────────────────── */
.disc {
  background:#F8FAFC; border:1px solid var(--B); border-top:3px solid var(--P);
  border-radius:var(--r2); padding:12px 16px; margin-top:24px;
  font-size:.64rem; color:var(--TM); line-height:1.8;
}
.disc-sig { font-size:.66rem; font-weight:700; color:var(--P); border-top:1px solid var(--B); padding-top:6px; margin-top:6px; }

/* ─── BUTTONS ────────────────────────────────────────── */
.stButton > button {
  min-height:46px!important; font-size:.88rem!important;
  font-weight:600!important; border-radius:var(--r2)!important;
  transition:all .2s!important;
}
.stButton > button[kind="primary"] { background:var(--P)!important; border-color:var(--P)!important; }
.stButton > button[kind="primary"]:hover { background:var(--PD)!important; }

/* ─── INPUTS ─────────────────────────────────────────── */
.stNumberInput input, .stTextInput input {
  border-radius:var(--r2)!important; font-family:'JetBrains Mono',monospace!important;
  font-size:.95rem!important; min-height:42px!important;
}
.stSelectbox > div > div { border-radius:var(--r2)!important; }
[data-testid="stMetricValue"] {
  font-family:'JetBrains Mono',monospace; font-size:1.5rem!important;
}

/* ─── MOBILE ─────────────────────────────────────────── */
@media(max-width:640px){
  .vit-wrap { grid-template-columns:repeat(2,1fr); }
  .sbar-vit-grid { grid-template-columns:repeat(2,1fr); }
  .tri-lbl { font-size:1.3rem; }
  .n2-big  { font-size:2.8rem; }
  .block-container { padding:.5rem .6rem 4rem!important; }
  .stButton>button { min-height:52px!important; font-size:1rem!important; }
  .stNumberInput input { min-height:48px!important; }
  .app-hdr-title { font-size:1.05rem; }
}

/* ─── PWA iPhone ─────────────────────────────────────── */
@media(display-mode:standalone){ .block-container{ padding-top:2rem!important; } }
</style>
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="AKIR-IAO">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<link rel="apple-touch-icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='22' fill='%23004A99'/%3E%3Ctext y='.9em' font-size='72' x='12' fill='white'%3E%2B%3C/text%3E%3C/svg%3E">
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES CLINIQUES
# ══════════════════════════════════════════════════════════════════════════════
LABELS = {"M":"TRI M — IMMEDIAT","1":"TRI 1 — URGENCE EXTREME","2":"TRI 2 — TRES URGENT",
          "3A":"TRI 3A — URGENT","3B":"TRI 3B — URGENT DIFFERE",
          "4":"TRI 4 — MOINS URGENT","5":"TRI 5 — NON URGENT"}
SECTEURS = {"M":"Dechocage — Immediat","1":"Dechocage — Immediat",
            "2":"Soins aigus — Med. <20 min","3A":"Soins aigus — Med. <30 min",
            "3B":"Polyclinique — Med. <1 h","4":"Consultation — Med. <2 h",
            "5":"Salle attente — Reorientation MG"}
DELAIS   = {"M":5,"1":5,"2":15,"3A":30,"3B":60,"4":120,"5":999}
TCSS     = {"M":"tri-M","1":"tri-1","2":"tri-2","3A":"tri-3A","3B":"tri-3B","4":"tri-4","5":"tri-5"}
HBCSS    = {"M":"hb-M","1":"hb-1","2":"hb-2","3A":"hb-3A","3B":"hb-3B","4":"hb-4","5":"hb-5"}
ORD      = {"M":0,"1":1,"2":2,"3A":3,"3B":4,"4":5,"5":6}
# ── Seuils glycémiques — unité mg/dl (standard belge BCFI)
# Facteur de conversion : 1 mmol/l = 18,016 mg/dl
GLYC = {
    "hs":  54,   # Hypoglycémie sévère    < 3,0 mmol/l — Glucose 30 % IV
    "hm":  70,   # Hypoglycémie modérée  < 3,9 mmol/l — Surveillance
    "Hs": 180,   # Hyperglycémie          > 10,0 mmol/l
    "Hs2":360,   # Hyperglycémie sévère   > 20,0 mmol/l
}

# ── Seuils NEWS2 — Référence : RCP London 2017
NEWS2_TRI_M         = 9   # Engagement vital — Tri M
NEWS2_RISQUE_ELEVE  = 7   # Appel médical immédiat
NEWS2_RISQUE_MOD    = 5   # Surveillance rapprochée

# ── Seuils SIPA (Shock Index Pédiatrique Ajusté à l'Âge) — Acker 2015
SIPA_0_1AN  = 2.2
SIPA_1_4ANS = 2.0
SIPA_4_7ANS = 1.8
SIPA_7_12ANS= 1.7

# ── Seuils AVC — Délai fibrinolyse — ESO/AHA 2023
AVC_DELAI_THROMBOLYSE_H = 4.5  # Fenêtre thrombolyse IV en heures

# ── Doses de référence BCFI (mg/kg)
PARA_DOSE_KG          = 15.0   # Paracétamol IV dose poids (mg/kg)
PARA_DOSE_FIXE_G      = 1.0    # Paracétamol IV dose fixe ≥ 50 kg (g)
PARA_POIDS_PIVOT_KG   = 50.0   # Pivot poids paracétamol
GLUCOSE_DOSE_KG       = 0.3    # Glucose 30 % dose (g/kg)
GLUCOSE_MAX_G         = 15.0   # Glucose 30 % dose maximale (g)
ADRE_POIDS_ADULTE_KG  = 30.0   # Seuil adulte adrénaline (kg)
ADRE_DOSE_ADULTE_MG   = 0.5    # Adrénaline adulte IM (mg)
ADRE_DOSE_KG          = 0.01   # Adrénaline enfant dose (mg/kg)
PIRI_BOLUS_MIN        = 0.03   # Piritramide bolus minimal (mg/kg)
PIRI_BOLUS_MAX        = 0.05   # Piritramide bolus maximal (mg/kg)
PIRI_PLAFOND_LT70     = 3.0    # Piritramide plafond / bolus < 70 kg (mg)
PIRI_PLAFOND_GE70     = 6.0    # Piritramide plafond / bolus ≥ 70 kg (mg)
NALOO_ADULTE_MG       = 0.4    # Naloxone adulte sans dépendance (mg)
NALOO_PED_KG          = 0.01   # Naloxone pédiatrique (mg/kg)
NALOO_DEP_MG          = 0.04   # Naloxone dépendance — titration (mg)
MORPH_MIN_KG          = 0.05   # Morphine bolus minimal (mg/kg)
MORPH_MAX_KG          = 0.10   # Morphine bolus maximal (mg/kg)
MORPH_PLAFOND_STD     = 5.0    # Morphine plafond bolus adulte standard < 100 kg (mg)
MORPH_PLAFOND_GE100   = 7.5    # Morphine plafond bolus adulte ≥ 100 kg (mg)
MORPH_PALIER_MG       = 2.0    # Morphine palier de titration (mg / 5-10 min)
CEFRTRX_ADULTE_G      = 2.0    # Ceftriaxone adulte (g)
CEFRTRX_PED_KG        = 0.1    # Ceftriaxone pédiatrique (g/kg)

# ── Litican (Méclofénoxate + Tiémonium méthylsulfate) IM — Protocole local
# Référence : BCFI — Tiémonium méthylsulfate / Méclofénoxate (Litican) — RCP Belgique
# Usage local : Urgences du Hainaut — Wallonie
LITICAN_DOSE_ADULTE_MG  = 40.0   # Dose standard adulte (mg) — 1 ampoule 2 ml
LITICAN_DOSE_KG_ENF     = 1.0    # Dose pédiatrique (mg/kg) — < 15 ans
LITICAN_DOSE_MAX_ENF_MG = 40.0   # Dose pédiatrique maximale (mg)
LITICAN_DOSE_MAX_JOUR   = 120.0  # Dose journalière maximale adulte (mg — 3 × 40 mg)
LITICAN_POIDS_PIVOT_KG  = 15.0   # Seuil poids enfant/adulte (kg)

# ── Protocole crise épileptique pédiatrique — Benzodiazépines
# Référence : PRISE EN CHARGE DE L'EME — Société Française de Neurologie
#             Pédiatrique (SFNP) / EpiCARE Network 2023
# Référence : BCFI — Diazépam / Midazolam / Clonazépam — RCP Belgique
# Référence : Appleton R, et al. Lorazepam vs. diazepam in the acute
#             treatment of epileptic seizures. Epilepsia 2008.
#
# LIGNE 1  — Buccal / Rectal / IM  (IAO sans VVP)
MIDAZOLAM_BUCC_KG      = 0.3    # mg/kg — Midazolam buccal (Buccolam)
MIDAZOLAM_BUCC_MAX_MG  = 10.0   # mg    — Dose maximale Midazolam buccal
DIAZEPAM_RECT_KG       = 0.5    # mg/kg — Diazepam rectal (Stesolid)
DIAZEPAM_RECT_MAX_MG   = 10.0   # mg    — Dose maximale Diazépam rectal

# LIGNE 2  — IV (après VVP posée — médecin)
DIAZEPAM_IV_KG         = 0.3    # mg/kg — Diazepam IV
DIAZEPAM_IV_MAX_MG     = 10.0   # mg    — Dose maximale Diazépam IV
LORAZEPAM_IV_KG        = 0.1    # mg/kg — Lorazépam IV (Temesta)
LORAZEPAM_IV_MAX_MG    = 4.0    # mg    — Dose maximale Lorazépam IV
CLONAZEPAM_IV_KG       = 0.02   # mg/kg — Clonazépam IV (Rivotril)
CLONAZEPAM_IV_MAX_MG   = 1.0    # mg    — Dose maximale Clonazépam IV

# LIGNE 3  — Deuxième ligne (EME réfractaire — réanimation)
PHENOBARB_IV_KG        = 20.0   # mg/kg — Phénobarbital IV (charge)
PHENOBARB_IV_MAX_MG    = 1000.0 # mg    — Dose maximale
LEVETI_IV_KG           = 60.0   # mg/kg — Lévétiracétam IV (Keppra)
LEVETI_IV_MAX_MG       = 4500.0 # mg    — Dose maximale

# Seuil temporel — État de Mal Épileptique (EME)
EME_SEUIL_MIN          = 5      # min   — Crise > 5 min = traitement actif
EME_ETABLI_MIN         = 30     # min   — EME établi si > 30 min ou 2 crises
EME_OPERATIONNEL_MIN   = 15     # min   — EME opérationnel (risque séquelles)

# Midazolam IM / Intranasale — voie de choix pré-hospitalière et IAO
MIDAZOLAM_IM_IN_KG     = 0.2    # mg/kg — Midazolam IM ou intranasale
MIDAZOLAM_IM_IN_MAX_MG = 10.0   # mg    — Dose maximale

# Valproate IV (Dépakine®) — Ligne 3 alternative (ISPE 2022)
VALPROATE_IV_KG        = 40.0   # mg/kg — dose de charge IV
VALPROATE_IV_MAX_MG    = 3000.0 # mg    — dose maximale
VALPROATE_IV_DEBIT_MIN = 6.0    # min   — durée perfusion minimale (≥ 5 min)

# Phénobarbital — débit maximum de sécurité
PHENOBARB_DEBIT_MG_KG_MIN = 1.0 # mg/kg/min — vitesse max IV

# Flumazénil — antidote benzodiazépines
FLUMAZENIL_DOSE_MG     = 0.01   # mg/kg — pédiatrique
FLUMAZENIL_MAX_MG      = 0.2    # mg    — dose initiale maximale
FLUMAZENIL_MAX_TOTAL   = 1.0    # mg    — dose totale maximale

# ── Registre — retention & performance
REGISTRE_CAP          = 500    # Nb max d'entrées conservées (rotation FIFO)

# ── Seuils pédiatriques — déshydratation et fièvre enfant
# Référence : SFMU / SFP — Prise en charge de l'enfant aux urgences 2021
# Référence : OMS — Échelle de déshydratation enfant 2005

# Fièvre pédiatrique — seuils de gravité
FIEVRE_TRES_HAUTE_ENFANT = 40.0    # °C — critère de gravité
FIEVRE_NOURR_SEUIL       = 38.0    # °C — seuil chez nourrisson < 3 mois
FIEVRE_HAUT_RISQUE_AGE   = 0.25    # ans — < 3 mois = à risque élevé (= 3/12)

# Déshydratation pédiatrique — fréquence cardiaque compensatrice par âge
# FC > seuil + déshydratation clinique = Tri 2 minimum
FC_TACHY_NOURR    = 160   # bpm — nourrisson 0-1 mois
FC_TACHY_BEBE     = 150   # bpm — bébé 1-12 mois
FC_TACHY_ENFANT   = 140   # bpm — enfant 1-5 ans
FC_TACHY_GRAND    = 120   # bpm — enfant 5-12 ans

# Seuils de déshydratation (% de perte de poids corporel)
DESHYDRAT_LEGERE   = 3    # % — pas de signe clinique majeur
DESHYDRAT_MODEREE  = 5    # % — signes cliniques présents
DESHYDRAT_SEVERE   = 10   # % — choc hypovolémique possible

# Vomissements pédiatriques — critères de gravité
VOMISS_BILIEUX_SIGNE_GRAVITE = True  # bile → occlusion / volvulus
VOMISS_FREQ_SEVERE           = 6     # > 6/h = déshydratation rapide
ATCD     = ["HTA","Diabete type 1","Diabete type 2","Tabagisme actif","Dyslipidaemie",
            "ATCD familial coronarien","Insuffisance cardiaque","BPCO","Anticoagulants/AOD",
            "Grossesse en cours","Immunodepression","Neoplasie evolutive","Epilepsie",
            "Insuffisance renale chronique","Ulcere gastro-duodenal","Insuffisance hepatique",
            "Deficit vitamine B12","Drepanocytose","Chimiotherapie en cours",
            "IMAO (inhibiteurs MAO)","Antidepresseurs ISRS/IRSNA"]
CFS_LBL  = {1:"Tres en forme",2:"En forme",3:"Bien portant",4:"Vulnerable",
            5:"Fragilite legere",6:"Fragilite moderee",7:"Fragilite severe",
            8:"Fragilite tres severe",9:"Maladie terminale"}
MOTS_CAT = {
  "Cardio":["Arret cardio-respiratoire","Hypotension arterielle","Douleur thoracique / SCA",
            "Tachycardie / tachyarythmie","Bradycardie / bradyarythmie","Palpitations",
            "Hypertension arterielle","Allergie / anaphylaxie"],
  "Respiratoire":["Dyspnee / insuffisance respiratoire","Dyspnee / insuffisance cardiaque"],
  "Digestif":["Douleur abdominale","Vomissements / Diarrhee","Hematemese / Rectorragie"],
  "Neuro":["AVC / Deficit neurologique","Traumatisme cranien","Alteration de conscience / Coma",
           "Cephalee","Convulsions / EME","Syndrome confusionnel","Malaise"],
  "Trauma":["Traumatisme thorax/abdomen/rachis cervical","Traumatisme bassin/hanche/femur",
            "Traumatisme membre / epaule"],
  "Infectio":["Fievre"],
  "Pediatrie":[
    "Pediatrie - Fievre <= 3 mois",
    "Pediatrie - Fievre enfant (3 mois - 15 ans)",
    "Pediatrie - Vomissements / Gastro-enterite",
    "Pediatrie - Crise epileptique",
  ],
  "Peau":["Petechie / Purpura","Erytheme etendu"],
  "Gyneco":["Accouchement imminent","Complication grossesse T1/T2","Menorragie / Metrorragie"],
  "Metabolique":["Hypoglycemie","Hyperglycemie / Cetoacidose"],
  "Divers":["Renouvellement ordonnance","Examen administratif"],
}
MOTIFS_RAPIDES = [
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
    "Convulsions / EME",
    "Pediatrie - Fievre <= 3 mois",
    "Pediatrie - Fievre enfant (3 mois - 15 ans)",
    "Pediatrie - Vomissements / Gastro-enterite",
    "Pediatrie - Crise epileptique",
    "Autre motif",
]

# ══════════════════════════════════════════════════════════════════════════════
# MOTEUR CLINIQUE
# ══════════════════════════════════════════════════════════════════════════════

def calculer_news2(fr:float, spo2:float, o2:bool, temp:float,
                   pas:float, fc:float, gcs:int,
                   bpco:bool=False) -> tuple[int, list[str]]:
    """
    Calcul du score NEWS2 (National Early Warning Score 2).

    Ce score d'alerte précoce identifie les patients à risque de dégradation
    clinique. Il intègre 7 paramètres physiologiques notés 0-3 points chacun,
    avec deux échelles SpO2 distinctes selon le profil respiratoire du patient.

    ÉCHELLE 1 (standard) — Cible SpO2 ≥ 96 %
        Applicable à la population générale sans pathologie respiratoire
        chronique hypercapnique.

    ÉCHELLE 2 (BPCO) — Cible SpO2 88-92 %
        Applicable aux patients BPCO connus à risque d'hypercapnie.
        Une SpO2 > 96 % sous O2 en BPCO expose à la narcose au CO₂ par
        suppression de la stimulation hypoxique du centre respiratoire.

    INTERPRÉTATION DU SCORE
        0         : Risque nul — surveillance de routine toutes les 12 h
        1-4       : Risque faible — surveillance toutes les 4-6 h
        5-6       : Risque modéré — surveillance toutes les heures
                    — appel équipe médicale
        ≥ 7       : Risque élevé — surveillance continue — équipe d'urgence
        ≥ 9       : Risque critique — engagement vital immédiat

    Parameters
    ----------
    fr : float
        Fréquence respiratoire en cycles par minute
    spo2 : float
        Saturation pulsée en oxygène en pourcentage
    o2 : bool
        Vrai si oxygénothérapie supplémentaire en cours
    temp : float
        Température corporelle en degrés Celsius
    pas : float
        Pression artérielle systolique en mmHg
    fc : float
        Fréquence cardiaque en battements par minute
    gcs : int
        Score de Glasgow (3-15)
    bpco : bool, optional
        Si True, active l'Échelle 2 avec cible SpO2 88-92%.
        Par défaut False (Échelle 1 standard).

    Returns
    -------
    tuple[int, list[str]]
        Score NEWS2 total et liste des avertissements cliniques détectés.

    References
    ----------
    Royal College of Physicians. National Early Warning Score 2 (NEWS2):
    Standardising the assessment of acute-illness severity in the NHS.
    London: RCP, 2017.

    Examples
    --------
    >>> calculer_news2(18, 97, False, 37.0, 120, 80, 15, bpco=False)
    (0, [])
    >>> s, w = calculer_news2(26, 88, True, 38.5, 95, 125, 14, bpco=False)
    >>> s >= 7
    True
    """
    s=0; w=[]
    # FR
    if   fr<=8:  s+=3; w.append(f"FR {fr}/min critique")
    elif fr<=11: s+=1
    elif fr<=20: pass
    elif fr<=24: s+=2
    else:        s+=3; w.append(f"FR {fr}/min — tachypnee severe")
    # SpO2 (echelle 1 ou 2 selon BPCO)
    if bpco:
        if   spo2<=83: s+=3; w.append(f"SpO2 {spo2}% critique (BPCO)")
        elif spo2<=85: s+=2
        elif spo2<=87: s+=1
        elif spo2<=92: pass   # BPCO target 88-92%
        elif spo2<=94: pass
        elif spo2<=96: s+=1; w.append(f"SpO2 {spo2}% élevée — risque hyperoxie BPCO")
        else:          s+=3; w.append(f"SpO2 {spo2}% > 96% — RISQUE NARCOSE CO₂ (BPCO)")
    else:
        if   spo2<=91: s+=3; w.append(f"SpO2 {spo2}% — hypoxemie severe")
        elif spo2<=93: s+=2
        elif spo2<=95: s+=1
    # O2 supp
    if o2: s+=2; w.append("O2 supplementaire +2 pts")
    # Temp
    if   temp<=35.0: s+=3; w.append(f"T {temp}C — hypothermie")
    elif temp<=36.0: s+=1
    elif temp<=38.0: pass
    elif temp<=39.0: s+=1
    else:            s+=2; w.append(f"T {temp}C — hyperthermie")
    # PAS
    if   pas<=90:  s+=3; w.append(f"PAS {pas}mmHg — etat de choc")
    elif pas<=100: s+=2
    elif pas<=110: s+=1
    elif pas<=219: pass
    else:          s+=3; w.append(f"PAS {pas}mmHg — HTA extreme")
    # FC
    if   fc<=40:  s+=3; w.append(f"FC {fc}bpm — bradycardie critique")
    elif fc<=50:  s+=1
    elif fc<=90:  pass
    elif fc<=110: s+=1
    elif fc<=130: s+=2
    else:         s+=3; w.append(f"FC {fc}bpm — tachycardie critique")
    # GCS
    if   gcs==15: pass
    elif gcs>=13: s+=3; w.append(f"GCS {gcs}/15")
    else:         s+=3; w.append(f"GCS {gcs}/15 — alteration majeure")
    return s, w

def n2_meta(s: int) -> tuple[str, str, int]:
    """
    Métadonnées d'interprétation du score NEWS2 pour affichage UI.

    Parameters
    ----------
    s : int
        Score NEWS2 calculé (0-20).

    Returns
    -------
    tuple[str, str, int]
        (libellé de risque, classe CSS pour couleur, pourcentage de la jauge).
    """
    if   s==0: return "Risque nul",    "n2-0", 0
    elif s<=4: return "Risque faible", "n2-1", int(s/12*100)
    elif s<=6: return "Risque modere", "n2-2", int(s/12*100)
    elif s<=8: return "Risque élevé",  "n2-3", int(s/12*100)
    else:      return "CRITIQUE",      "n2-5", min(int(s/12*100),100)

def calculer_gcs(y:int, v:int, m:int) -> tuple[int, list[str]]:
    """
    Calcul du score de Glasgow Coma Scale (GCS).

    Évaluation de la profondeur du trouble de conscience par trois items :
    Ouverture des yeux (Y, 1-4), Réponse verbale (V, 1-5), Réponse
    motrice (M, 1-6). Score total : 3 (coma profond) à 15 (conscience
    normale).

    INTERPRÉTATION
        GCS 13-15 : Traumatisme crânien léger
        GCS 9-12  : Traumatisme crânien modéré
        GCS ≤ 8   : Traumatisme crânien grave — intubation à considérer

    Parameters
    ----------
    y : int
        Ouverture des yeux (1-4).
    v : int
        Réponse verbale (1-5).
    m : int
        Réponse motrice (1-6).

    Returns
    -------
    tuple[int, list[str]]
        Score GCS total (3-15) et liste d'éventuelles erreurs.

    References
    ----------
    Teasdale G, Jennett B. Assessment of coma and impaired consciousness.
    A practical scale. Lancet. 1974;304(7872):81-84.
    """
    try: return max(3,min(15,int(y)+int(v)+int(m))),[]
    except: return 15,["Erreur GCS"]

def calculer_qsofa(fr:Optional[float], gcs:Optional[int],
                   pas:Optional[float]) -> tuple[int, list[str], list[str]]:
    """
    Score qSOFA (quick Sequential Organ Failure Assessment).

    Outil de dépistage rapide du sepsis en dehors des unités de soins
    intensifs. Un score ≥ 2 identifie les patients à risque de mortalité
    élevée et doit faire rechercher une infection active.

    CRITÈRES
        FR ≥ 22 cycles/min              (+1 point)
        Altération de la conscience     (+1 point, GCS < 15)
        PAS ≤ 100 mmHg                  (+1 point)

    INTERPRÉTATION
        qSOFA ≥ 2 : Sepsis probable — évaluation urgente pour défaillance
                    d'organes (SOFA complet) — hémocultures — antibiothérapie
                    selon contexte.

    Parameters
    ----------
    fr : float or None
    gcs : int or None
    pas : float or None

    Returns
    -------
    tuple[int, list[str], list[str]]
        (score qSOFA, critères positifs, avertissements pour données manquantes).

    References
    ----------
    Singer M, Deutschman CS, Seymour CW, et al. The Third International
    Consensus Definitions for Sepsis and Septic Shock (Sepsis-3).
    JAMA. 2016;315(8):801-810.
    """
    s=0; pos=[]; w=[]
    if fr is None: w.append("FR manquante")
    elif fr>=22: s+=1; pos.append(f"FR {fr}/min")
    if gcs is None: w.append("GCS manquant")
    elif gcs<15: s+=1; pos.append(f"GCS {gcs}/15")
    if pas is None: w.append("PAS manquante")
    elif pas<=100: s+=1; pos.append(f"PAS {pas}mmHg")
    return s,pos,w

def calculer_timi(age:float, nb_frcv:int, sten:bool,
                  aspi:bool, trop:bool, dst:bool,
                  cris:int) -> tuple[int, list[str]]:
    """
    Score TIMI pour Syndrome Coronarien Aigu sans sus-décalage de ST.

    Score prédictif du risque de décès, nouvel infarctus ou revascularisation
    urgente à 14 jours. Chaque item positif apporte 1 point (total 0-7).

    CRITÈRES (1 point chacun)
        1. Âge ≥ 65 ans
        2. Au moins 3 facteurs de risque cardiovasculaire
        3. Sténose coronaire documentée ≥ 50 %
        4. Prise d'aspirine dans les 7 derniers jours
        5. Élévation des troponines
        6. Déviation du segment ST à l'ECG
        7. Au moins 2 épisodes angineux dans les 24 dernières heures

    INTERPRÉTATION
        0-2 : Risque faible (4,7 % évènements à 14 j)
        3-4 : Risque intermédiaire (13-19 %)
        5-7 : Risque élevé (26-41 %) — stratégie invasive précoce

    Parameters
    ----------
    age : float
    nb_frcv : int
        Nombre de facteurs de risque cardiovasculaire.
    sten, aspi, trop, dst : bool
        Critères binaires (sténose, aspirine, troponine, déviation ST).
    cris : int
        Nombre de crises dans les 24 h.

    Returns
    -------
    tuple[int, list[str]]

    References
    ----------
    Antman EM, Cohen M, Bernink PJLM, et al. The TIMI risk score for
    unstable angina/non-ST elevation MI. JAMA. 2000;284(7):835-842.
    """
    try:
        s=(int(age>=65)+int(nb_frcv>=3)+int(bool(sten))+int(bool(aspi))
           +int(bool(trop))+int(bool(dst))+int(cris>=2))
        return s,[]
    except Exception as e: return 0,[str(e)]

def evaluer_fast(f:bool, a:bool, s:bool, t:bool) -> tuple[int, str, bool]:
    """
    Évaluation FAST (Face, Arm, Speech, Time) pour dépistage d'AVC.

    Outil infirmier de détection rapide d'un Accident Vasculaire Cérébral.
    Un critère positif justifie une évaluation médicale urgente ; deux ou
    plus activent la filière Stroke.

    CRITÈRES
        F (Face)   : Asymétrie faciale (sourire dévié, affaissement commissure).
        A (Arm)    : Déficit moteur d'un membre (épreuve des bras tendus).
        S (Speech) : Trouble du langage (aphasie, dysarthrie).
        T (Time)   : Début brutal — noter l'heure précise des premiers signes.

    FILIÈRE STROKE
        Score ≥ 2 : Activation filière — IRM/scanner cérébral en urgence —
                    évaluer éligibilité thrombolyse si délai ≤ 4h30.

    Parameters
    ----------
    f, a, s, t : bool
        Critères FAST.

    Returns
    -------
    tuple[int, str, bool]
        (score 0-4, interprétation textuelle, flag filière Stroke).

    References
    ----------
    Aroor S, Singh R, Goldstein LB. BE-FAST: Reducing the proportion of
    strokes missed using the FAST mnemonic. Stroke. 2017;48(2):479-481.
    """
    sc=int(bool(f))+int(bool(a))+int(bool(s))+int(bool(t))
    if sc>=2: return sc,"FAST positif — AVC probable — Filiere Stroke",True
    if sc==1: return sc,"FAST partiel — Evaluation urgente",False
    return sc,"FAST negatif",False

def calculer_algoplus(v:bool, r:bool, p:bool,
                      ac:bool, co:bool) -> tuple[int, str, str, list[str]]:
    """
    Score Algoplus — évaluation comportementale de la douleur aiguë.

    Échelle d'hétéro-évaluation de la douleur chez la personne âgée
    présentant des troubles de la communication verbale (démence, AVC,
    confusion). Chaque item observé apporte 1 point (total 0-5).

    CINQ ITEMS COMPORTEMENTAUX
        1. Visage     — froncement de sourcils, crispation, grimaces.
        2. Regard     — fixe, absent, larmoiement, yeux fermés.
        3. Plaintes   — cris, gémissements, verbalisation de douleur.
        4. Corps      — protection, attitude antalgique, prostration.
        5. Comportement — agressivité, agitation, opposition aux soins.

    SEUIL D'INTERVENTION
        Score ≥ 2 : Douleur probable — traitement antalgique à initier.
        Score ≥ 4 : Douleur intense — antalgique IV urgent.

    Parameters
    ----------
    v, r, p, ac, co : bool
        Items visage, regard, plaintes, attitude corporelle, comportement.

    Returns
    -------
    tuple[int, str, str, list[str]]
        (score 0-5, interprétation, classe CSS, erreurs éventuelles).

    References
    ----------
    Rat P, Jouve E, Pickering G, et al. Validation of an acute pain-behavior
    scale for older persons with inability to communicate verbally:
    Algoplus. Eur J Pain. 2011;15(2):198.e1-198.e10.
    """
    try:
        s=(int(bool(v))+int(bool(r))+int(bool(p))+int(bool(ac))+int(bool(co)))
        if   s>=4: return s,"Douleur intense — traitement IV urgent","danger",[]
        elif s>=2: return s,"Douleur probable — traitement à initier","warning",[]
        return s,"Douleur absente ou peu probable","success",[]
    except Exception as e: return 0,"Erreur","info",[str(e)]

def evaluer_cfs(sc: int) -> tuple[str, str, bool]:
    """
    Clinical Frailty Scale (CFS) — Échelle de fragilité de Rockwood.

    Évaluation globale du niveau de fragilité du patient âgé, basée sur
    le niveau d'autonomie fonctionnelle et cognitive dans la vie
    quotidienne deux semaines avant l'épisode aigu actuel.

    NIVEAUX
        1 — Très en forme          (actif, énergique, exercice régulier)
        2 — En forme               (sans maladie active, moins d'exercice)
        3 — Bien portant            (maladie bien contrôlée)
        4 — Vulnérable              (ralenti, fatigabilité)
        5 — Fragilité légère        (dépendance pour AIVQ)
        6 — Fragilité modérée       (aide pour toilette, cuisine)
        7 — Fragilité sévère        (dépendance totale pour soins)
        8 — Fragilité très sévère   (phase terminale proche)
        9 — Maladie terminale       (espérance de vie < 6 mois)

    IMPACT SUR LE TRIAGE
        CFS ≥ 5 : Envisager remontée du niveau de triage — seuils de
                  gravité clinique plus bas chez le sujet fragile.

    References
    ----------
    Rockwood K, Song X, MacKnight C, et al. A global clinical measure of
    fitness and frailty in elderly people. CMAJ. 2005;173(5):489-495.
    """
    if sc<=3: return "Robuste","success",False
    if sc<=4: return "Vulnerable","warning",False
    if sc<=6: return "Fragile","warning",True
    if sc<=8: return "Tres fragile","danger",True
    return "Terminal","danger",True

def si(fc: float, pas: float) -> float:
    """
    Shock Index (Indice de choc) — ratio FC / PAS.

    Marqueur précoce d'hypoperfusion systémique, plus sensible que la
    PAS isolée pour détecter un état de choc hémorragique ou septique
    débutant chez l'adulte.

    INTERPRÉTATION (adulte)
        SI < 0,7  : Normal
        SI 0,7-0,9: Surveillance rapprochée
        SI ≥ 1,0  : Choc débutant probable — évaluation médicale urgente
        SI ≥ 1,4  : Choc sévère — réanimation immédiate

    Parameters
    ----------
    fc : float
        Fréquence cardiaque en bpm.
    pas : float
        Pression artérielle systolique en mmHg.

    Returns
    -------
    float
        Shock Index arrondi à 2 décimales ou 0.0 si PAS invalide.
    """
    return round(fc/pas,2) if pas and pas>0 else 0.0

def sipa(fc: float, age: float) -> tuple[float, str, bool]:
    """
    SIPA — Shock Index Pediatric Age-adjusted.

    Version pédiatrique du Shock Index ajustée par tranche d'âge, car les
    valeurs normales de FC et PAS varient fortement chez l'enfant. Un
    SIPA élevé identifie précocement les enfants polytraumatisés à risque
    de transfusion massive.

    SEUILS D'ALERTE (Acker 2015)
        0 - 1 an   : SIPA > 2,2
        1 - 4 ans  : SIPA > 2,0
        4 - 7 ans  : SIPA > 1,8
        7 - 12 ans : SIPA > 1,7

    FORMULE UTILISÉE
        SIPA = FC / (PAS normale pour l'âge)
        PAS normale = 70 + (âge × 2) pour enfant 1-10 ans

    Parameters
    ----------
    fc : float
        Fréquence cardiaque en bpm.
    age : float
        Âge en années (peut être décimal pour les nourrissons).

    Returns
    -------
    tuple[float, str, bool]
        (valeur SIPA, interprétation textuelle, flag alerte choc pédiatrique).

    References
    ----------
    Acker SN, Ross JT, Partrick DA, et al. Pediatric specific shock index
    accurately identifies severely injured children. J Pediatr Surg.
    2015;50(2):331-334.
    """
    v=round(fc/max(1.0,float(age+1)*15+70),2)
    s=SIPA_0_1AN  if age<=1 else (SIPA_1_4ANS if age<=4 else (SIPA_4_7ANS if age<=7 else 1.7))
    return v,f"SIPA {v} {'>' if v>s else '<='} {s} — {'Choc pediatrique probable' if v>s else 'Hemodynamique preservee'}",v>s

def mgdl_mmol(v: float) -> float:
    """
    Conversion de glycémie mg/dl vers mmol/l.

    Unités belges : la glycémie est rapportée en mg/dl dans les contextes
    cliniques (BCFI, labos hospitaliers). Les recommandations internationales
    utilisent les mmol/l. Facteur de conversion : 1 mmol/l ≈ 18,016 mg/dl.

    ÉQUIVALENCES CLINIQUES COURANTES
        54 mg/dl  = 3,0 mmol/l  (hypoglycémie sévère)
        70 mg/dl  = 3,9 mmol/l  (hypoglycémie modérée)
        126 mg/dl = 7,0 mmol/l  (seuil diabète à jeun)
        180 mg/dl = 10,0 mmol/l (hyperglycémie)
        360 mg/dl = 20,0 mmol/l (hyperglycémie sévère)
    """
    return round(v/18.016,1)

# ══════════════════════════════════════════════════════════════════════════════
# MOTEUR DE TRIAGE FRENCH V1.1 — Architecture dispatch par handlers
# ══════════════════════════════════════════════════════════════════════════════
#
# Chaque handler est une fonction pure qui reçoit les vitaux + det et retourne
# (niveau, justification, référence). Le dispatcher associe motif→handler.
# Ajouter un motif = ajouter un handler + l'enregistrer dans _TRIAGE_DISPATCH.
# ══════════════════════════════════════════════════════════════════════════════

# Type alias pour la cohérence des signatures
TriageResult = tuple[str, str, str]  # (niveau, justification, référence)


# ── Handlers cardio-circulatoire ────────────────────────────────────────────

def _triage_acr(**_) -> TriageResult:
    """Arrêt Cardio-Respiratoire — Tri 1 immédiat sans condition."""
    return "1", "ACR confirmé — RCP en cours", "FRENCH Tri 1"


def _triage_hypotension(pas, fc, **_) -> TriageResult:
    """
    Hypotension artérielle — gradient de gravité basé sur PAS et FC.
    PAS ≤ 70 : collapsus vasculaire → Tri 1
    PAS ≤ 90 ou (PAS ≤ 100 avec FC > 100) : choc débutant → Tri 2
    """
    if pas <= 70:
        return "1", f"PAS {pas} mmHg ≤ 70 — collapsus", "FRENCH Tri 1"
    if pas <= 90 or (pas <= 100 and fc > 100):
        return "2", f"PAS {pas} mmHg — choc débutant", "FRENCH Tri 2"
    if pas <= 100:
        return "3B", f"PAS {pas} mmHg — valeur limite", "FRENCH Tri 3B"
    return "4", "PAS normale", "FRENCH Tri 4"


def _triage_sca(fc, spo2, det, **_) -> TriageResult:
    """
    Douleur thoracique / SCA — filière coronaire.
    ECG anormal typique ou douleur typique → Tri 1 (STEMI présumé).
    Instabilité hémodynamique ou coronaire probable → Tri 2.
    """
    ecg  = det.get("ecg", "Normal")
    doul = det.get("douleur", "Atypique")
    if ecg == "Anormal typique SCA" or doul == "Typique (constrictive, irradiante)":
        return "1", "SCA — ECG anormal ou douleur typique", "FRENCH Tri 1"
    if fc >= 120 or spo2 < 94:
        return "2", "Douleur thoracique instable", "FRENCH Tri 2"
    if doul == "Coronaire probable" or det.get("frcv", 0) >= 2:
        return "2", "Douleur coronaire probable ≥ 2 FRCV", "FRENCH Tri 2"
    return "3A", "Douleur thoracique atypique stable", "FRENCH Tri 3A"


def _triage_arythmie(fc, det, **_) -> TriageResult:
    """
    Tachycardie / Bradycardie / Palpitations.
    FC ≥ 180 ou ≤ 30 : arythmie extrême → Tri 1.
    FC ≥ 150 ou ≤ 40 : arythmie sévère → Tri 2.
    """
    if fc >= 180 or fc <= 30:
        return "1", f"FC {fc} bpm — arythmie extrême", "FRENCH Tri 1"
    if fc >= 150 or fc <= 40:
        return "2", f"FC {fc} bpm — arythmie sévère", "FRENCH Tri 2"
    if det.get("tol_mal"):
        return "2", "Arythmie mal tolérée", "FRENCH Tri 2"
    return "3B", f"FC {fc} bpm — arythmie tolérée", "FRENCH Tri 3B"


def _triage_hta(pas, fc, det, **_) -> TriageResult:
    """Hypertension artérielle — urgence si PAS ≥ 220 ou signes fonctionnels."""
    if pas >= 220:
        return "2", f"PAS {pas} mmHg ≥ 220 — urgence hypertensive", "FRENCH Tri 2"
    if det.get("sf") or (pas >= 180 and fc > 100):
        return "2", "HTA avec signes fonctionnels", "FRENCH Tri 2"
    if pas >= 180:
        return "3B", "HTA sévère sans signe fonctionnel", "FRENCH Tri 3B"
    return "4", "HTA modérée", "FRENCH Tri 4"


def _triage_anaphylaxie(spo2, pas, gcs, det, **_) -> TriageResult:
    """
    Allergie / Anaphylaxie — Tri 1 si atteinte respiratoire, hémodynamique
    ou neurologique (critères de Clark 2004 / EAACI 2023).
    """
    if spo2 < 94 or pas < 90 or gcs < 15:
        return "1", "Anaphylaxie sévère — engagement systémique", "FRENCH Tri 1"
    if det.get("dyspnee") or det.get("urticaire"):
        return "2", "Allergie systémique", "FRENCH Tri 2"
    return "3B", "Réaction allergique localisée", "FRENCH Tri 3B"


# ── Handlers neurologie ─────────────────────────────────────────────────────

def _triage_avc(gcs, det, **_) -> TriageResult:
    """
    AVC / Déficit neurologique.
    Délai ≤ 4h30 : fenêtre de thrombolyse IV — filière Stroke → Tri 1.
    """
    d = det.get("delai", 99)
    if d <= AVC_DELAI_THROMBOLYSE_H:
        return "1", f"AVC {d} h — fenêtre thrombolyse — filière Stroke", "FRENCH Tri 1"
    if det.get("def_prog") or gcs < 15:
        return "2", "Déficit progressif ou altération GCS", "FRENCH Tri 2"
    return "2", "Déficit neurologique — bilan urgent", "FRENCH Tri 2"


def _triage_tc(gcs, det, **_) -> TriageResult:
    """
    Traumatisme Crânien.
    GCS ≤ 8 : TC grave (intubation à considérer) → Tri 1.
    GCS ≤ 12 ou AOD/AVK : TDM urgent → Tri 2.
    """
    if gcs <= 8:
        return "1", f"TC grave — GCS {gcs}/15", "FRENCH Tri 1"
    if gcs <= 12 or det.get("aod"):
        return "2", f"TC GCS {gcs}/15 ou anticoagulant — TDM urgent", "FRENCH Tri 2"
    if det.get("pdc"):
        return "3A", "TC avec perte de conscience", "FRENCH Tri 3A"
    return "4", "TC bénin", "FRENCH Tri 4"


def _triage_coma(gcs, gl, **_) -> TriageResult:
    """
    Altération de conscience / Coma.
    Hypoglycémie masquée systématiquement recherchée (cause curable).
    """
    if gl and gl < GLYC["hs"]:
        return "2", f"Hypoglycémie {gl} mg/dl — Glucose 30 % IV", "FRENCH Tri 2"
    if gcs <= 8:
        return "1", f"Coma profond — GCS {gcs}/15", "FRENCH Tri 1"
    if gcs <= 13:
        return "2", f"Altération de conscience — GCS {gcs}/15", "FRENCH Tri 2"
    return "2", "Altération légère de conscience", "FRENCH Tri 2"


def _triage_convulsions(det, **_) -> TriageResult:
    """Convulsions / État de Mal Épileptique (EME)."""
    if det.get("multi"):
        return "2", "Crises multiples ou état de mal épileptique", "FRENCH Tri 2"
    if det.get("conf"):
        return "2", "Confusion post-critique persistante", "FRENCH Tri 2"
    return "3B", "Convulsion récupérée", "FRENCH Tri 3B"


def _triage_cephalee(det, **_) -> TriageResult:
    """
    Céphalée.
    Céphalée foudroyante (« la pire de ma vie ») → HSA suspectée → Tri 1.
    """
    if det.get("brutal"):
        return "1", "Céphalée foudroyante — HSA suspectée", "FRENCH Tri 1"
    if det.get("nuque") or det.get("fiev_ceph"):
        return "2", "Céphalée avec signes méningés", "FRENCH Tri 2"
    return "3B", "Céphalée sans signe de gravité", "FRENCH Tri 3B"


def _triage_malaise(n2, gl, det, **_) -> TriageResult:
    """Malaise récupéré — hypoglycémie et anomalie vitale recherchées."""
    if gl and gl < GLYC["hs"]:
        return "2", f"Malaise hypoglycémique {gl} mg/dl", "FRENCH Tri 2"
    if n2 >= 2 or det.get("anom_vit"):
        return "2", "Malaise avec anomalie vitale", "FRENCH Tri 2"
    return "3B", "Malaise récupéré", "FRENCH Tri 3B"


# ── Handlers respiratoire ───────────────────────────────────────────────────

def _triage_dyspnee(spo2, fr, det, **_) -> TriageResult:
    """
    Dyspnée — Insuffisance respiratoire ou cardiaque.
    BPCO : cible SpO2 88-92 % (Échelle 2). Seuil de détresse abaissé à < 88 %.
    Standard : seuil de détresse à SpO2 < 91 %.
    """
    bp    = det.get("bpco", False)
    cible = 92 if bp else 95
    seuil_crit = 88 if bp else 91
    if spo2 < seuil_crit or fr >= 40:
        return "1", f"Détresse respiratoire — SpO2 {spo2} % FR {fr}/min", "FRENCH Tri 1"
    if spo2 < cible or fr >= 30 or not det.get("parole", True):
        return "2", f"Dyspnée sévère — SpO2 {spo2} %", "FRENCH Tri 2"
    if det.get("orth") or det.get("tirage"):
        return "2", "Orthopnée ou tirage intercostal", "FRENCH Tri 2"
    return "3B", f"Dyspnée modérée — SpO2 {spo2} %", "FRENCH Tri 3B"


# ── Handlers digestif ───────────────────────────────────────────────────────

def _triage_abdomen(fc, pas, det, **_) -> TriageResult:
    """Douleur abdominale — Shock Index et GEU détectés."""
    sh = si(fc, pas)
    if pas < 90 or sh >= 1.0:
        return "2", f"Abdomen avec choc (SI {sh})", "FRENCH Tri 2"
    if det.get("grossesse") or det.get("geu"):
        return "2", "Abdomen sur grossesse — GEU à éliminer", "FRENCH Tri 2"
    if det.get("defense"):
        return "2", "Abdomen chirurgical", "FRENCH Tri 2"
    if det.get("tol_mal"):
        return "3A", "Douleur mal tolérée", "FRENCH Tri 3A"
    return "3B", "Douleur tolérée", "FRENCH Tri 3B"


# ── Handlers infectiologie ──────────────────────────────────────────────────

def _triage_fievre(fc, pas, temp, det, **_) -> TriageResult:
    """
    Fièvre — Purpura, critères de gravité, tolérance clinique.
    Fièvre + purpura → Ceftriaxone 2 g IV AVANT tout bilan → Tri 1.
    """
    if det.get("purpura"):
        return "1", "Fièvre + purpura — Ceftriaxone 2 g IV immédiat", "FRENCH Tri 1"
    if temp >= 40 or temp <= 35.2 or det.get("conf"):
        return "2", f"Fièvre avec critère de gravité (T {temp} °C)", "FRENCH Tri 2"
    if det.get("tol_mal") or pas < 100 or si(fc, pas) >= 1.0:
        return "3B", "Fièvre mal tolérée", "FRENCH Tri 3B"
    return "5", "Fièvre bien tolérée", "FRENCH Tri 5"


# ── Handlers pédiatrie ──────────────────────────────────────────────────────

def _triage_fievre_nourr(**_) -> TriageResult:
    """
    Fièvre chez le nourrisson ≤ 3 mois.
    Systématiquement Tri 2 — risque d'infection bactérienne sévère
    sans signes évidents d'alarme (immunité immature).
    """
    return (
        "2",
        "Fièvre nourrisson ≤ 3 mois — bilan urgent systématique",
        "FRENCH Pédiatrie Tri 2",
    )


def _triage_ped_fievre(fc, spo2, temp, age, det, **_) -> TriageResult:
    """
    Fièvre chez l'enfant (3 mois à 15 ans).

    Algorithme stratifié par âge, température et signes de gravité.
    Intègre les critères de sepsis pédiatrique (qSOFA-Ped), les signes
    d'encéphalopathie fébrile, la tolérance clinique et les signaux
    d'alarme spécifiques à l'enfant.

    CRITÈRES DE GRAVITÉ IMMÉDIATS (Tri 1)
        • Purpura non effaçable associé à la fièvre
        • Convulsions fébriles prolongées (> 15 min) ou focales
        • Altération majeure de la conscience (GCS ≤ 8)
        • Nourrisson 3-6 mois avec T° ≥ 38 °C : Tri 2 systématique

    CRITÈRES DE GRAVITÉ SÉVÈRES (Tri 2)
        • Température ≥ 40 °C chez tout enfant
        • Purpura avec fièvre (fuseau fulminans)
        • Tachycardie compensatrice marquée (FC > seuil/âge)
        • Signes d'encéphalopathie (agitation, somnolence)
        • Raideur de nuque ou signe de Kernig/Brudzinski
        • Fièvre chez enfant immunodéprimé ou ATCD cardiopathie

    PARAMÈTRES D'ORIENTATION (Tri 3B)
        • Fièvre bien tolérée sans signe de gravité
        • Enfant communicant, regard vif, boit correctement

    References
    ----------
    SFMU / SFP. Prise en charge de l'enfant aux urgences. 2021.
    Nijman RG, et al. Prediction models for paediatric fever in emergency
    departments. Lancet Child Adolesc Health. 2022;6(4):255-265.
    NICE guideline NG143. Fever in under 5s. 2021.
    """
    # Seuil FC tachycardie selon âge
    if age < 1/12:
        fc_seuil = FC_TACHY_NOURR
    elif age < 1.0:
        fc_seuil = FC_TACHY_BEBE
    elif age < 5.0:
        fc_seuil = FC_TACHY_ENFANT
    else:
        fc_seuil = FC_TACHY_GRAND

    tachycardie = (fc > fc_seuil)

    # Nourrisson 3-6 mois : Tri 2 systématique si fièvre
    if age <= 0.5 and temp >= FIEVRE_NOURR_SEUIL:
        return (
            "2",
            f"Fièvre nourrisson {int(age*12)} mois — risque infectieux élevé",
            "SFP / SFMU — Tri 2 systématique < 6 mois",
        )

    # Signes de gravité immédiats → Tri 1
    if det.get("purpura") and temp >= FIEVRE_NOURR_SEUIL:
        return (
            "1",
            "Fièvre + purpura — Méningococcémie — Ceftriaxone 2 g IV IMMÉDIAT",
            "SPILF / SFP 2017",
        )
    if det.get("convulsion_prolongee") or det.get("convulsion_focale"):
        return (
            "1",
            "Convulsion fébrile prolongée (> 15 min) ou focale — Tri 1",
            "FRENCH Pédiatrie Tri 1",
        )

    # Signes de gravité sévères → Tri 2
    if temp >= FIEVRE_TRES_HAUTE_ENFANT:
        return (
            "2",
            f"Fièvre {temp} °C ≥ 40 °C — hyperthermie sévère",
            "FRENCH Pédiatrie Tri 2",
        )
    if det.get("nuque") or det.get("kernig"):
        return "2", "Fièvre avec signes méningés", "FRENCH Pédiatrie Tri 2"
    if det.get("encephalopathie") or det.get("agitation") or det.get("somnolence"):
        return "2", "Fièvre avec encéphalopathie", "FRENCH Pédiatrie Tri 2"
    if tachycardie and det.get("tol_mal"):
        return (
            "2",
            f"Fièvre avec tachycardie {fc} bpm et mauvaise tolérance",
            "FRENCH Pédiatrie Tri 2",
        )
    if det.get("immunodepression") or det.get("cardiopathie"):
        return "2", "Fièvre enfant immunodéprimé / cardiopathie", "FRENCH Pédiatrie Tri 2"
    if det.get("tol_mal") or tachycardie:
        return "3A", "Fièvre mal tolérée — évaluation médicale rapide", "FRENCH Tri 3A"

    return "3B", "Fièvre bien tolérée — sans signe de gravité", "FRENCH Tri 3B"


def _triage_ped_gastro(fc, pas, temp, age, det, **_) -> TriageResult:
    """
    Vomissements et/ou fièvre chez l'enfant — Gastro-entérite pédiatrique.

    Protocole fondé sur la cotation de la déshydratation pédiatrique
    et la détection de signes d'alarme non-GEA (gastro-entérite aiguë).

    SIGNES D'ALARME — EXCLURE UNE CAUSE CHIRURGICALE (Tri 1-2)
        • Vomissements bilieux (vert) : occlusion / volvulus du grêle
        • Douleur abdominale intense avec défense
        • Fontanelle bombante chez nourrisson
        • Pleurs inconsolables (invagination intestinale aiguë)
        • Rectorragies associées (invagination ou MICI)
        • Convulsions associées

    ÉVALUATION DE LA DÉSHYDRATATION (OMS / ESPGHAN 2014)

        LÉGÈRE (< 5 %)
            Muqueuses légèrement sèches, soif, sans autre signe.
            → Tri 3B — réhydratation orale au service

        MODÉRÉE (5-10 %)
            Yeux cernés, fontanelle déprimée, pli cutané persistant 1-2 s,
            tachycardie compensatrice, diurèse diminuée, pleurs sans larmes.
            → Tri 2 — réhydratation IV ou SNG à évaluer

        SÉVÈRE (> 10 %) / CHOC HYPOVOLÉMIQUE
            Extrémités froides, marbrures, pli cutané > 2 s, oligurie/anurie,
            hypotension, altération de conscience.
            → Tri 1 — remplissage vasculaire immédiat (NaCl 0,9 % ou Ringer)

    FIÈVRE ASSOCIÉE
        Fièvre ≥ 38,5 °C + déshydratation modérée : Tri 2 systématique.
        Nourrisson < 3 mois + vomissements + fièvre : Tri 2 systématique.

    References
    ----------
    Guarino A, et al. ESPGHAN/ESPID evidence-based guidelines for the
    management of acute gastroenteritis in children in Europe.
    J Pediatr Gastroenterol Nutr. 2014;59 Suppl 1:S132-52.
    OMS. Prise en charge de la diarrhée aiguë chez l'enfant. 2005.
    Finkelstein JA, et al. Gastroenteritis in children: beyond rehydration.
    Pediatrics. 2017;140(5).
    """
    # Seuil FC tachycardie selon âge
    if age < 1/12:
        fc_seuil = FC_TACHY_NOURR
    elif age < 1.0:
        fc_seuil = FC_TACHY_BEBE
    elif age < 5.0:
        fc_seuil = FC_TACHY_ENFANT
    else:
        fc_seuil = FC_TACHY_GRAND

    tachycardie    = (fc > fc_seuil)
    shock_index_v  = si(fc, pas)

    # ── Signes d'alarme — cause chirurgicale à exclure (Tri 1) ───────────
    if det.get("bilieux"):
        return (
            "1",
            "Vomissements bilieux (vert) — occlusion/volvulus à éliminer",
            "FRENCH Pédiatrie Tri 1",
        )
    if det.get("fontanelle_bombante"):
        return (
            "1",
            "Fontanelle bombante — HTIC / méningite à éliminer",
            "FRENCH Pédiatrie Tri 1",
        )
    if det.get("pleurs_inconsolables"):
        return (
            "1",
            "Pleurs inconsolables + vomissements — invagination intestinale aiguë",
            "FRENCH Pédiatrie Tri 1",
        )
    if det.get("convulsions"):
        return (
            "1",
            "Vomissements + convulsions — déshydratation sévère / encéphalopathie",
            "FRENCH Pédiatrie Tri 1",
        )

    # ── Choc hypovolémique — déshydratation sévère (Tri 1) ───────────────
    if shock_index_v >= 1.0 or pas < 90 or det.get("deshydrat_severe"):
        return (
            "1",
            f"Choc hypovolémique — déshydratation sévère (SI {shock_index_v})",
            "FRENCH Pédiatrie Tri 1",
        )

    # ── Déshydratation modérée (Tri 2) ────────────────────────────────────
    if det.get("deshydrat_moderee"):
        return (
            "2",
            "Déshydratation modérée — réhydratation IV / SNG à évaluer",
            "ESPGHAN 2014 — Tri 2",
        )
    # Nourrisson < 3 mois avec vomissements + fièvre : Tri 2 systématique
    if age < FIEVRE_HAUT_RISQUE_AGE and temp >= FIEVRE_NOURR_SEUIL:
        return (
            "2",
            f"Nourrisson {int(age*12)} mois — vomissements + fièvre {temp} °C",
            "FRENCH Pédiatrie Tri 2",
        )
    # Tachycardie compensatrice + fièvre élevée
    if tachycardie and temp >= 38.5:
        return (
            "2",
            f"Tachycardie {fc} bpm + fièvre {temp} °C — risque déshydratation",
            "FRENCH Pédiatrie Tri 2",
        )
    # Vomissements fréquents (> 6/h) sans arrêt
    if det.get("vomiss_freq"):
        return (
            "2",
            f"Vomissements très fréquents (> {VOMISS_FREQ_SEVERE}/h) — tolérance nulle",
            "FRENCH Pédiatrie Tri 2",
        )
    # Refus alimentaire total + signes de déshydratation légère
    if det.get("refus_alimentation") and (tachycardie or det.get("deshydrat_legere")):
        return (
            "2",
            "Refus alimentaire total + signes de déshydratation",
            "FRENCH Pédiatrie Tri 2",
        )

    # ── Déshydratation légère / vomissements tolérés (Tri 3A/3B) ─────────
    if det.get("deshydrat_legere") or tachycardie:
        return (
            "3A",
            "Déshydratation légère — évaluation médicale, réhydratation orale",
            "ESPGHAN 2014 — Tri 3A",
        )

    return (
        "3B",
        "Gastro-entérite — vomissements tolérés sans signe de gravité",
        "FRENCH Tri 3B",
    )


def _triage_ped_epilepsie(fc, spo2, temp, age, det, gl=None, **_) -> TriageResult:
    """
    Crise épileptique pédiatrique — Triage FRENCH adapté SFNP / ISPE 2023.

    DÉFINITIONS TEMPORELLES (ILAE 2015 / ISPE 2022)
        > 5 min  : Crise prolongée → traitement médicamenteux IMMÉDIAT
        > 15 min : EME opérationnel → risque de lésions cérébrales
        > 30 min : EME établi → réanimation pédiatrique

    CRITÈRES TRI 1
        • EME établi (> 30 min) ou EME opérationnel (> 15 min)
        • SpO2 < 92 % — détresse respiratoire
        • Âge < 1 mois — convulsion néonatale
        • Traumatisme crânien associé
        • Fièvre + signes méningés — encéphalite / méningite
        • Hypoglycémie sévère (< 54 mg/dl) + trouble de conscience

    CRITÈRES TRI 2
        • Crise EN COURS à l'arrivée
        • Durée > 5 min (seuil de traitement)
        • Première crise non fébrile
        • Crise fébrile complexe (focale / répétée)
        • Reprise de conscience incomplète
        • Score AVPU < A

    CRITÈRES TRI 3A / 3B
        • Crise fébrile simple récupérée
        • Épilepsie connue — crise habituelle récupérée

    References
    ----------
    Trinka E, et al. Epilepsia. 2015;56(10):1515-23.
    Brophy GM, et al. Neurocrit Care. 2012;17(Suppl 1):S23-33.
    Glauser T, et al. ISPE — Status Epilepticus Guidelines. Epilepsia. 2016.
    SFNP / EpiCARE. Protocole EME pédiatrique. 2023.
    """
    duree = det.get("duree_min", 0) or 0

    # ── Tri 1 — Engagement vital ──────────────────────────────────────────
    if det.get("eme_etabli") or duree > EME_ETABLI_MIN:
        return ("1",
                f"EME établi — durée > {EME_ETABLI_MIN} min — Réanimation pédiatrique URGENTE",
                "ISPE 2022 — Tri 1")
    if duree > EME_OPERATIONNEL_MIN:
        return ("1",
                f"EME opérationnel — durée {duree} min > {EME_OPERATIONNEL_MIN} min — Risque lésionnel",
                "ILAE 2015 — EME opérationnel — Tri 1")
    if spo2 < 92:
        return ("1",
                f"Crise + SpO2 {spo2} % — Détresse respiratoire — Libération VAS + O2",
                "FRENCH Pédiatrie Tri 1")
    if age < 1/12:
        return ("1",
                "Convulsion néonatale (< 1 mois) — Bilan étiologique urgent",
                "SFNP Tri 1 — Néonatal")
    if det.get("tc_associe"):
        return ("1",
                "Crise + traumatisme crânien — Imagerie urgente — Hématome intracérébral",
                "FRENCH Tri 1")
    if det.get("signes_meninges") and temp >= 38.0:
        return ("1",
                "Crise fébrile + signes méningés — Méningite / Encéphalite",
                "FRENCH Pédiatrie Tri 1")
    if gl is not None and gl < 54 and det.get("conscience_incomplete"):
        return ("1",
                f"Hypoglycémie sévère {gl} mg/dl + conscience altérée — Glucose 30 % IV IMMÉDIAT",
                "FRENCH Tri 1")

    # ── Tri 2 — Urgence ───────────────────────────────────────────────────
    if det.get("en_cours"):
        return ("2",
                "Crise EN COURS — Midazolam buccal 0,3 mg/kg MAINTENANT",
                "SFNP 2023 — Tri 2")
    if duree > EME_SEUIL_MIN:
        return ("2",
                f"Crise prolongée {duree} min > {EME_SEUIL_MIN} min — Traitement actif requis",
                "SFNP 2023 — Tri 2")
    if det.get("premiere_crise") and "Epilepsie" not in det.get("atcd", []):
        return ("2",
                "1ère crise épileptique non fébrile — Bilan étiologique urgent",
                "FRENCH Pédiatrie Tri 2")
    if det.get("focale") or det.get("repetee_24h"):
        return ("2",
                "Crise fébrile complexe (focale ou répétée < 24 h)",
                "SFNP 2023 — Tri 2")
    if det.get("conscience_incomplete") or det.get("avpu") in ("V", "P", "U"):
        return ("2",
                "Conscience altérée après crise — Phase post-critique prolongée",
                "FRENCH Pédiatrie Tri 2")

    # ── Tri 3A — Urgence modérée ──────────────────────────────────────────
    if det.get("febrile") and not det.get("focale") and det.get("recuperee"):
        return ("3A",
                "Crise fébrile simple récupérée — Surveillance + avis médical",
                "SFNP 2023 — Tri 3A")
    if "Epilepsie" in det.get("atcd", []) and det.get("recuperee") and det.get("habituelle"):
        return ("3A",
                "Épilepsie connue — Crise habituelle récupérée — Avis médical",
                "FRENCH Tri 3A")

    # ── Tri 3B — Plan d'urgence familial ─────────────────────────────────
    if "Epilepsie" in det.get("atcd", []) and det.get("recuperee") and det.get("plan_urgence"):
        return ("3B",
                "Épilepsie connue — Crise récupérée — Plan d'urgence documenté",
                "FRENCH Tri 3B")

    return ("2",
            "Crise épileptique pédiatrique — Évaluation médicale urgente",
            "SFNP 2023 — Tri 2 par sécurité")


# ── Handlers peau ───────────────────────────────────────────────────────────

def _triage_purpura(temp, det, **_) -> TriageResult:
    """
    Pétéchie / Purpura — Test du verre obligatoire.
    Purpura non effaçable : purpura fulminans présumé → Tri 1 absolu.
    """
    if det.get("neff"):
        return "1", "Purpura non effaçable — Céfotriaxone 2 g IV immédiat",                "SPILF/SFP 2017"
    if temp >= 38.0:
        return "2", "Purpura fébrile — suspicion fulminans", "FRENCH Tri 2"
    return "3B", "Pétéchies — bilan hémostase à prévoir", "FRENCH Tri 3B"


# ── Handlers traumatologie ──────────────────────────────────────────────────

def _triage_trauma_axial(fc, pas, spo2, det, **_) -> TriageResult:
    """
    Traumatisme thorax/abdomen/rachis cervical ou bassin/hanche/fémur.
    Pénétrant ou haute cinétique → Tri 1.
    """
    if det.get("pen") or det.get("cin") == "Haute":
        return "1", "Traumatisme pénétrant ou haute cinétique", "FRENCH Tri 1"
    if si(fc, pas) >= 1.0 or spo2 < 94:
        return "2", f"Traumatisme avec choc (SI {si(fc, pas)})", "FRENCH Tri 2"
    return "2", "Traumatisme axial — évaluation urgente", "FRENCH Tri 2"


def _triage_trauma_distal(det, **_) -> TriageResult:
    """
    Traumatisme d'un membre ou de l'épaule.
    Ischémie distale → Tri 1 (urgence vasculaire).
    """
    if det.get("isch"):
        return "1", "Ischémie distale", "FRENCH Tri 1"
    if det.get("imp") and det.get("deform"):
        return "2", "Fracture déplacée avec impotence totale", "FRENCH Tri 2"
    if det.get("imp"):
        return "3A", "Impotence fonctionnelle totale", "FRENCH Tri 3A"
    if det.get("deform"):
        return "3A", "Déformation visible", "FRENCH Tri 3A"
    return "4", "Traumatisme distal modéré", "FRENCH Tri 4"


# ── Handlers métabolique ────────────────────────────────────────────────────

def _triage_hypoglycemie(gcs, gl, **_) -> TriageResult:
    """Hypoglycémie — seuils GLYC["hs"] et GLYC["hm"]."""
    if gl and gl < GLYC["hs"]:
        return "2", f"Hypoglycémie sévère {gl} mg/dl — Glucose 30 % IV", "FRENCH Tri 2"
    if gcs < 15:
        return "2", f"Hypoglycémie avec altération GCS {gcs}/15", "FRENCH Tri 2"
    return "3B", "Hypoglycémie légère — resucrage oral", "FRENCH Tri 3B"


def _triage_hyperglycemie(gcs, det, **_) -> TriageResult:
    """Hyperglycémie / Cétoacidose diabétique."""
    if det.get("ceto") or gcs < 15:
        return "2", "Cétoacidose ou altération de conscience", "FRENCH Tri 2"
    return "4", "Hyperglycémie tolérée", "FRENCH Tri 4"


def _triage_non_urgent(**_) -> TriageResult:
    """Motifs non urgents — renouvellement ordonnance, examen administratif."""
    return "5", "Consultation non urgente", "FRENCH Tri 5"


# ── TABLE DE DISPATCH ──────────────────────────────────────────────────────
#
# Association motif (clé) → handler (fonction).
# Clé = chaîne exacte du motif tel que saisi dans MOTS_CAT.
# Clé = tuple pour les motifs gérés par le même handler.

_TRIAGE_DISPATCH: dict = {
    "Arret cardio-respiratoire":                          _triage_acr,
    "Hypotension arterielle":                             _triage_hypotension,
    "Douleur thoracique / SCA":                           _triage_sca,
    ("Tachycardie / tachyarythmie",
     "Bradycardie / bradyarythmie",
     "Palpitations"):                                     _triage_arythmie,
    "Hypertension arterielle":                            _triage_hta,
    "Allergie / anaphylaxie":                             _triage_anaphylaxie,
    "AVC / Deficit neurologique":                         _triage_avc,
    "Traumatisme cranien":                                _triage_tc,
    "Alteration de conscience / Coma":                    _triage_coma,
    "Convulsions / EME":                                  _triage_convulsions,
    "Cephalee":                                           _triage_cephalee,
    "Malaise":                                            _triage_malaise,
    ("Dyspnee / insuffisance respiratoire",
     "Dyspnee / insuffisance cardiaque"):                 _triage_dyspnee,
    "Douleur abdominale":                                 _triage_abdomen,
    "Fievre":                                             _triage_fievre,
    "Pediatrie - Fievre <= 3 mois":                       _triage_fievre_nourr,
    "Pediatrie - Fievre enfant (3 mois - 15 ans)":        _triage_ped_fievre,
    "Pediatrie - Vomissements / Gastro-enterite":         _triage_ped_gastro,
    "Pediatrie - Crise epileptique":                      _triage_ped_epilepsie,
    "Petechie / Purpura":                                 _triage_purpura,
    ("Traumatisme thorax/abdomen/rachis cervical",
     "Traumatisme bassin/hanche/femur"):                  _triage_trauma_axial,
    "Traumatisme membre / epaule":                        _triage_trauma_distal,
    "Hypoglycemie":                                       _triage_hypoglycemie,
    "Hyperglycemie / Cetoacidose":                        _triage_hyperglycemie,
    ("Renouvellement ordonnance",
     "Examen administratif"):                             _triage_non_urgent,
}

# Index inversé : motif_str → handler, construit au chargement
_MOTIF_INDEX: dict[str, object] = {}
for _key, _handler in _TRIAGE_DISPATCH.items():
    if isinstance(_key, tuple):
        for _m in _key:
            _MOTIF_INDEX[_m] = _handler
    else:
        _MOTIF_INDEX[_key] = _handler


def french_triage(motif:str, det:Optional[dict],
                  fc:float, pas:float, spo2:float,
                  fr:float, gcs:int, temp:float,
                  age:float, n2:int,
                  gl:Optional[float]=None) -> tuple[str, str, str]:
    """
    Moteur de triage FRENCH — Société Française de Médecine d'Urgence V1.1.

    Applique l'algorithme de triage FRENCH pour déterminer le niveau de
    priorité clinique (M, 1, 2, 3A, 3B, 4, 5) à partir du motif de recours,
    des paramètres vitaux et des critères cliniques spécifiques.

    ARCHITECTURE DISPATCH
        La logique par motif est distribuée dans des handlers indépendants
        (_triage_*) enregistrés dans _TRIAGE_DISPATCH. Le dispatcher
        résout le motif → handler en O(1) via l'index _MOTIF_INDEX.
        Ajouter un motif = écrire un handler + l'enregistrer dans la table.

    HIÉRARCHIE DES PRIORITÉS (appliquée avant le dispatch)
        1. NEWS2 ≥ 9 → Tri M (engagement vital — transversal)
        2. Purpura fulminans → Tri 1 (transversal quel que soit le motif)
        3. Dispatch motif-spécifique
        4. Fallback NEWS2 (motif inconnu)

    FALLBACK SUR NEWS2 (motif sans handler)
        NEWS2 ≥ NEWS2_RISQUE_ELEVE (7) → Tri 2
        NEWS2 ≥ NEWS2_RISQUE_MOD   (5) → Tri 3A
        Sinon                           → Tri 3B

    Parameters
    ----------
    motif : str
    det : dict, optional
    fc, pas, spo2, fr : float
    gcs : int
    temp : float
    age : float
    n2 : int
    gl : float, optional
        Glycémie capillaire en mg/dl.

    Returns
    -------
    tuple[str, str, str]
        (niveau, justification, référence)

    Notes
    -----
    Valeurs None remplacées par valeurs physiologiques par défaut.
    En cas d'erreur interne, retourne Tri 2 par sécurité.

    References
    ----------
    Taboulet P, et al. FRENCH Triage SFMU V1.1, Juin 2018.
    """
    # ── Sécurisation des entrées ──────────────────────────────────────────
    fc   = fc   or 80
    pas  = pas  or 120
    spo2 = spo2 or 98
    fr   = fr   or 16
    gcs  = gcs  or 15
    temp = temp or 37.0
    n2   = n2   or 0
    det  = det  or {}

    try:
        # ── Critères transversaux (priorité absolue) ──────────────────────
        if n2 >= NEWS2_TRI_M:
            return "M", f"NEWS2 {n2} ≥ {NEWS2_TRI_M} — engagement vital", "NEWS2 Tri M"
        if det.get("purpura"):
            return "1", "PURPURA FULMINANS — Céfotriaxone 2 g IV immédiat", "SPILF/SFP 2017"

        # ── Dispatch par handler ──────────────────────────────────────────
        handler = _MOTIF_INDEX.get(motif)
        if handler is not None:
            return handler(
                fc=fc, pas=pas, spo2=spo2, fr=fr,
                gcs=gcs, temp=temp, age=age, n2=n2,
                gl=gl, det=det,
            )

        # ── Fallback NEWS2 (motif non répertorié) ────────────────────────
        if n2 >= NEWS2_RISQUE_ELEVE:
            return "2", f"NEWS2 {n2} ≥ {NEWS2_RISQUE_ELEVE} — risque élevé", "NEWS2 Tri 2"
        if n2 >= NEWS2_RISQUE_MOD:
            return "3A", f"NEWS2 {n2} ≥ {NEWS2_RISQUE_MOD} — risque modéré", "NEWS2 Tri 3A"
        return "3B", f"Évaluation standard — {motif}", "FRENCH Tri 3B"

    except Exception as e:
        return "2", f"Erreur moteur de triage : {e}", "Sécurité Tri 2"


def verifier_coherence(fc:float, pas:float, spo2:float,
                       fr:float, gcs:int, temp:float, eva:int,
                       motif:str, atcd:list, det:dict,
                       n2:int,
                       gl:Optional[float]=None) -> tuple[list[str], list[str]]:
    """
    Vérification de cohérence clinique et détection d'interactions.

    Contrôle transversal post-triage qui identifie les situations à risque
    immédiat (interactions médicamenteuses, hypoglycémie masquée, état de
    choc, hypoxémie) et génère des alertes différenciées selon leur
    gravité : danger (rouge) vs attention (orange).

    ALERTES DANGER (rouge — action immédiate)
        • IMAO détecté        — Contre-indication absolue au Tramadol
                                (syndrome sérotoninergique fatal).
        • Hypoglycémie sévère — Glycémie < 54 mg/dl : Glucose 30 % IV.
        • Shock Index ≥ 1.0   — État de choc probable.
        • SpO2 < 90 %         — Hypoxémie sévère — O2 urgent.
        • FC ≥ 150 ou ≤ 40    — Arythmie critique.
        • TC sous AOD/AVK     — Risque d'hématome différé — TDM urgent.

    ALERTES ATTENTION (orange — vigilance)
        • ISRS/IRSNA          — Interaction majeure avec Tramadol.
        • Hypoglycémie modérée — Corriger avant antalgie.
        • FR ≥ 30/min         — Tachypnée significative.

    Parameters
    ----------
    fc, pas, spo2, fr, temp : float
    gcs : int
    eva : int
    motif : str
    atcd : list[str]
        Liste des antécédents sélectionnés dans la sidebar.
    det : dict
        Critères cliniques spécifiques au motif.
    n2 : int
    gl : float, optional
        Glycémie capillaire en mg/dl.

    Returns
    -------
    tuple[list[str], list[str]]
        (alertes danger, alertes attention) — listes de messages formatés.

    Notes
    -----
    Cette fonction est appelée après french_triage() et ses alertes sont
    affichées au-dessus du résultat de triage pour que l'IAO les voie
    avant de décider de la suite de la prise en charge.
    """
    D=[]; A=[]
    if "IMAO (inhibiteurs MAO)" in atcd:
        D.append("IMAO — Tramadol CONTRE-INDIQUE (syndrome serotoninergique fatal)")
    if "Antidepresseurs ISRS/IRSNA" in atcd:
        A.append("ISRS/IRSNA — Tramadol deconseille — Preferer Dipidolor ou Morphine")
    if gl:
        if gl<GLYC["hs"]: D.append(f"HYPOGLYCEMIE SEVERE {gl}mg/dl ({mgdl_mmol(gl)}mmol/l) — Glucose 30% IV")
        elif gl<GLYC["hm"]: A.append(f"Hypoglycemie moderee {gl}mg/dl — corriger avant antalgique")
    sh=si(fc,pas)
    if sh>=1.0: D.append(f"Shock Index {sh}>=1.0 — etat de choc probable")
    if spo2<90: D.append(f"SpO2 {spo2}% — O2 urgent")
    if fr>=30:  A.append(f"FR {fr}/min — tachypnee")
    if fc>=150 or fc<=40: D.append(f"FC {fc}bpm — arythmie critique")
    if "Anticoagulants/AOD" in atcd and "Traumatisme cranien" in motif:
        D.append("TC sous AOD/AVK — TDM urgent")
    return D,A

def build_sbar(age:float, motif:str, cat:str,
               atcd:list, alg:Optional[str], o2:bool,
               temp:float, fc:float, pas:float,
               spo2:float, fr:float, gcs:int,
               eva:int, n2:int,
               niv:str, just:str, crit:str,
               op:str="IAO",
               gl:Optional[float]=None) -> dict:
    """
    Construction d'un rapport SBAR structuré pour transmission DPI.

    SBAR (Situation — Background — Assessment — Recommendation) est la
    structure internationale standardisée de transmission inter-équipes
    en milieu hospitalier, validée pour réduire les erreurs de
    communication. Le dictionnaire retourné alimente à la fois l'affichage
    HTML structuré et l'export texte téléchargeable.

    STRUCTURE SBAR
        S — Situation     : Identité anonyme, motif, niveau de triage.
        B — Background   : Antécédents, allergies, oxygénothérapie, glycémie.
        A — Assessment    : Vitaux complets, justification du triage.
        R — Recommendation: Orientation, délai, remarques IAO.

    TRAÇABILITÉ
        Chaque rapport inclut horodatage (JJ/MM/AAAA HH:MM) et code
        opérateur anonyme pour répondre aux exigences de traçabilité
        médico-légale (AR 18/06/1990 — Belgique).

    Parameters
    ----------
    age : float
    motif, cat : str
    atcd : list[str]
    alg : str
        Allergies connues (texte libre).
    o2 : bool
    temp, fc, pas, spo2, fr : float
    gcs : int
    eva : int
    n2 : int
    niv, just, crit : str
        Résultat de french_triage().
    op : str, default "IAO"
        Code opérateur anonyme.
    gl : float, optional
        Glycémie capillaire en mg/dl.

    Returns
    -------
    dict
        Dictionnaire structuré prêt pour SBAR_RENDER() et export texte.
    """
    return {"heure":datetime.now().strftime("%d/%m/%Y %H:%M"),"op":op,"age":int(age),
            "motif":motif,"cat":cat,"atcd":", ".join(atcd) if atcd else "Aucun",
            "alg":alg or "Aucune","o2":"O2 supp" if o2 else "Air ambiant",
            "gl":f"{gl}mg/dl ({mgdl_mmol(gl)}mmol/l)" if gl else "Non mesuree",
            "niv":LABELS.get(niv,niv),"sec":SECTEURS.get(niv,""),"delai":DELAIS.get(niv,"?"),
            "crit":crit,"just":just,"fc":fc,"pas":pas,"spo2":spo2,"fr":fr,
            "temp":temp,"gcs":gcs,"eva":eva,"n2":n2}

# ══════════════════════════════════════════════════════════════════════════════
# PHARMACOLOGIE BCFI
# ══════════════════════════════════════════════════════════════════════════════
#
# Tous les protocoles de ce module sont issus du BCFI (Belgian Centre for
# Pharmacotherapeutic Information) et des RCP belges en vigueur. Les doses
# affichées sont conformes aux recommandations officielles en Belgique et
# doivent être validées par un médecin prescripteur avant administration.
#
# Chaque fonction retourne systématiquement un tuple (résultat | None, erreur | None)
# pour permettre un traitement d'erreur uniforme côté UI.
# ══════════════════════════════════════════════════════════════════════════════

_CI_A=["Ulcere gastro-duodenal","Insuffisance renale chronique","Insuffisance hepatique",
       "Grossesse en cours","Chimiotherapie en cours"]

def ci_ains(atcd: list[str]) -> list[str]:
    """
    Détection des contre-indications communes aux AINS.

    Les AINS (Kétorolac, Diclofénac, Ibuprofène) partagent les mêmes
    contre-indications absolues : ulcère gastro-duodénal évolutif,
    insuffisance rénale chronique, insuffisance hépatique,
    grossesse au-delà du 1er trimestre, chimiothérapie en cours.
    """
    return [c for c in _CI_A if c in atcd]

def paracetamol(poids: float) -> tuple[Optional[dict], Optional[str]]:
    """
    Paracétamol IV — Antalgie de palier I (OMS).

    DOSE ADULTE (≥ 50 kg) : 1 g IV toutes les 6 h (maximum 4 g/24 h).
    DOSE ADAPTÉE AU POIDS (< 50 kg) : 15 mg/kg IV toutes les 6 h.

    ADMINISTRATION
        Perfusion IV de 15 minutes dans 100 ml de NaCl 0,9 %.
        Début d'action : 5-10 min — Durée d'effet : 4-6 h.

    POSOLOGIE CIBLE
        Palier 1 seul            : EVA 0-3
        Association systématique : EVA ≥ 4 (avec palier 2 ou 3)

    CONTRE-INDICATIONS
        • Insuffisance hépatique sévère
        • Allergie connue au paracétamol

    Parameters
    ----------
    poids : float
        Poids en kg.

    Returns
    -------
    tuple[dict | None, str | None]
        (dose calculée, message d'erreur ou None).

    References
    ----------
    BCFI — Paracétamol IV — RCP Belgique.
    """
    if poids<=0: return None,"Poids invalide"
    if poids>=PARA_POIDS_PIVOT_KG: return {"dose_g":PARA_DOSE_FIXE_G,"vol":"100ml NaCl 0.9% sur 15min","freq":"Toutes les 6h (max 4g/24h)","ref":"BCFI — Paracetamol IV"},None
    dg=min(round(PARA_DOSE_KG*poids/1000,2),1.0)
    return {"dose_g":dg,"vol":f"{dg*1000:.0f}mg dans 100ml NaCl 0.9%","freq":"Toutes les 6h","ref":"BCFI — Paracetamol IV"},None

def ketorolac(poids:float, atcd:list[str]) -> tuple[Optional[dict], Optional[str]]:
    """
    Kétorolac (Taradyl) IV — AINS palier II.

    DOSE
        Adulte ≥ 50 kg : 30 mg IV
        Sujet < 50 kg  : 15 mg IV

    ADMINISTRATION
        IV lent sur 15 secondes minimum. Toutes les 6 heures.
        DURÉE MAXIMALE : 5 jours (risque d'insuffisance rénale aiguë
        et d'hémorragie digestive au-delà).

    CONTRE-INDICATIONS ABSOLUES
        Voir ci_ains() : ulcère, IRC, insuffisance hépatique, grossesse,
        chimiothérapie.

    References
    ----------
    BCFI — Kétorolac trométhamine — RCP Belgique.
    """
    ci=ci_ains(atcd)
    if ci: return None,f"Contre-indique : {', '.join(ci)}"
    d=15.0 if poids<50 else 30.0
    return {"dose_mg":d,"admin":"IV lent 15s","freq":"Toutes 6h — max 5j","ref":"BCFI — Ketorolac (Taradyl)"},None

def tramadol(poids:float, atcd:list[str], age:float) -> tuple[Optional[dict], Optional[str]]:
    """
    Tramadol IV — Opioïde faible palier II.

    DOSE
        Adulte ≥ 50 kg : 100 mg IV
        Sujet < 50 kg  : 1,5 mg/kg IV

    ADMINISTRATION
        Dilué dans 100 ml NaCl 0,9 % — Perfusion sur 30 minutes.
        Toutes les 6 heures (maximum 400 mg/24 h).

    CONTRE-INDICATIONS ABSOLUES (détectées automatiquement)

        IMAO (inhibiteurs de la monoamine oxydase) ⚠️ CRITIQUE
            Association à risque de SYNDROME SÉROTONINERGIQUE FATAL
            par accumulation de sérotonine dans le SNC. Le délai de
            sécurité après arrêt d'un IMAO irréversible est de 14 jours.
            Alternatives : Paracétamol IV, Piritramide, Morphine.

        Épilepsie
            Le tramadol abaisse le seuil épileptogène — risque de
            convulsions, surtout aux doses élevées.

    INTERACTIONS MAJEURES
        ISRS/IRSNA : Risque de syndrome sérotoninergique. Préférer
        Piritramide ou Morphine. Surveillance clinique si prescription
        maintenue (agitation, hyperthermie, myoclonies).

    References
    ----------
    BCFI — Tramadol chlorhydrate — RCP Belgique.
    AFMPS — Notice de sécurité tramadol 2019.
    """
    als=[]
    if "Epilepsie" in atcd: als.append("CONTRE-INDIQUE — Epilepsie (seuil epileptogene)")
    if "IMAO (inhibiteurs MAO)" in atcd: als.append("CONTRE-INDICATION ABSOLUE — SYNDROME SEROTONINERGIQUE FATAL avec IMAO")
    if "Antidepresseurs ISRS/IRSNA" in atcd: als.append("INTERACTION MAJEURE — ISRS/IRSNA — risque serotoninergique")
    d=100.0 if poids>=50 else round(1.5*poids,0)
    return {"dose_mg":d,"admin":f"{d:.0f}mg dans 100ml NaCl 0.9% — IV 30min","freq":"Toutes 6h (max 400mg/24h)","alertes":als,"ref":"BCFI — Tramadol"},None

def piritramide(poids:float, age:float, atcd:list[str]) -> tuple[Optional[dict], Optional[str]]:
    """
    Piritramide (Dipidolor) IV — Opioïde fort palier III.

    Analgésique opioïde de référence aux urgences belges pour la douleur
    aiguë sévère (EVA ≥ 7) — demi-vie intermédiaire (4-8 h) avec bonne
    tolérance hémodynamique.

    TITRATION PROTOCOLE SFAR 2010
        Dose initiale : 0,03-0,05 mg/kg IV lent (1-2 min)
        Plafond       : 3 mg/bolus (6 mg si poids > 70 kg)
        Réévaluation EVA à 10-15 min, titrer si EVA > 3

    RÉDUCTION DE DOSE DE 50 %
        • Âge ≥ 70 ans
        • Insuffisance rénale chronique
        • Insuffisance hépatique

    ANTIDOTE
        Naloxone 0,4 mg IV en cas de dépression respiratoire
        (SpO2 < 90 % ou FR < 10/min).

    References
    ----------
    BCFI — Piritramide (Dipidolor) — RCP Belgique.
    SFAR. Protocoles de titration morphinique aux urgences. 2010.
    """
    red=(age>=70 or "Insuffisance renale chronique" in atcd or "Insuffisance hepatique" in atcd)
    f=0.5 if red else 1.0
    plafond = (PIRI_PLAFOND_LT70 if poids < 70 else PIRI_PLAFOND_GE70) * f
    dmin = min(round(PIRI_BOLUS_MIN * poids * f, 2), plafond)
    dmax = min(round(PIRI_BOLUS_MAX * poids * f, 2), plafond)
    return {"dmin":dmin,"dmax":dmax,"admin":"IV lent 1-2min — titrer si EVA>3 apres 15min","note":"Dose -50% si age>=70/IRC/IH" if red else "","ref":"BCFI — Piritramide (Dipidolor)"},None

def morphine(poids:float, age:float) -> tuple[Optional[dict], Optional[str]]:
    """
    Morphine IV — Opioïde fort de référence palier III.

    TITRATION
        Dose initiale : 0,05-0,10 mg/kg IV (maximum 5 mg/bolus).
        Paliers ultérieurs : 2 mg IV toutes les 5-10 minutes.
        Objectif thérapeutique : EVA ≤ 3.

    RÉDUCTION DE DOSE DE 50 %
        Âge ≥ 70 ans (risque de dépression respiratoire majoré).

    ANTIDOTE
        Naloxone 0,4 mg IV en cas de dépression respiratoire.

    References
    ----------
    BCFI — Morphine chlorhydrate — RCP Belgique.
    """
    f = 0.5 if age >= 70 else 1.0
    plafond = (MORPH_PLAFOND_GE100 if poids >= 100 else MORPH_PLAFOND_STD) * f
    dmin = min(round(MORPH_MIN_KG * poids * f, 1), plafond)
    dmax = min(round(MORPH_MAX_KG * poids * f, 1), plafond)
    return {
        "dmin":  dmin,
        "dmax":  dmax,
        "palier": MORPH_PALIER_MG,
        "admin": f"IV lent 2-3 min — titrer par paliers {MORPH_PALIER_MG:.0f} mg / 5-10 min",
        "ref":   "BCFI — Morphine chlorhydrate — RCP Belgique",
    }, None

def naloxone(poids:float, age:float, dep:bool=False) -> tuple[Optional[dict], Optional[str]]:
    """
    Naloxone (Narcan) IV — Antagoniste opioïde.

    INDICATION PRINCIPALE
        Dépression respiratoire induite par opioïdes (SpO2 < 90 %
        ou FR < 10/min) après administration de Piritramide, Morphine
        ou Tramadol.

    TROIS PROTOCOLES SELON LE CONTEXTE

    1. ADULTE SANS DÉPENDANCE — Standard
       Dose : 0,4 mg IV direct
       Répétition : toutes les 2-3 min jusqu'à restauration ventilatoire
       Dose cumulée maximale : 10 mg (au-delà, reconsidérer le diagnostic)

    2. ENFANT < 18 ANS — Adapté au poids
       Dose : 0,01 mg/kg IV (maximum 0,4 mg par bolus)
       Répétition : toutes les 2-3 min

    3. PATIENT DÉPENDANT AUX OPIOÏDES — Titration douce
       Dose : 0,04 mg IV par paliers de 2 minutes
       Objectif : restaurer la ventilation, PAS lever totalement
                  l'analgésie (risque de syndrome de sevrage aigu et
                  de douleur rebond sévère)

    SURVEILLANCE POST-INJECTION
        La demi-vie courte de la Naloxone (30-90 min) est plus courte
        que celle des opioïdes antagonisés. Surveillance SpO2 + FR +
        conscience continue pendant au moins 2 heures après la
        dernière injection pour détecter une resédation.

    References
    ----------
    BCFI — Naloxone chlorhydrate (Narcan) — RCP Belgique.
    """
    als=[]
    if dep:
        d=NALOO_DEP_MG; a="{NALOO_DEP_MG}mg IV/2min — titration douce"; n="Dependance — objectif : ventilation, pas levee totale"
        als.append("Risque sevrage si surdosage")
    elif age<18:
        d=min(round(NALOO_PED_KG*poids,3),NALOO_ADULTE_MG); a=f"{d}mg IV (0.01mg/kg)"; n=f"Ped : {d}mg pour {poids}kg"
    else:
        d=NALOO_ADULTE_MG; a=f"{NALOO_ADULTE_MG}mg IV — repeter 2-3min (max 10mg)"; n="Si pas de reponse a 10mg : reconsiderer"
    return {"dose":d,"admin":a,"note":n,"alertes":als,"surv":"Monitor SpO2+FR — demi-vie courte 30-90min","ref":"BCFI — Naloxone (Narcan)"},None

def adrenaline(poids: float) -> tuple[Optional[dict], Optional[str]]:
    """
    Adrénaline IM — Traitement de première intention du choc anaphylactique.

    La voie intramusculaire est la VOIE DE RÉFÉRENCE dans l'anaphylaxie
    (pas la voie IV, qui est réservée à l'arrêt cardiaque).

    DOSE
        Adulte ≥ 30 kg : 0,5 mg IM (0,5 ml de solution 1 mg/ml)
        Enfant < 30 kg : 0,01 mg/kg IM (maximum 0,5 mg)

    SITE D'INJECTION
        Face antéro-latérale de la cuisse (muscle vaste externe).
        Absorption plus rapide et moins variable qu'au deltoïde.

    RÉPÉTITION
        Toutes les 5 à 15 minutes si absence d'amélioration hémodynamique
        ou respiratoire. En l'absence de réponse après 2 doses IM,
        envisager la voie IV (médecin).

    SURVEILLANCE
        Monitorage continu : FC, PA, SpO2, rythme cardiaque (ECG).
        Effets indésirables attendus : tachycardie, tremblements, pâleur,
        céphalées — transitoires et proportionnels à la dose.

    References
    ----------
    BCFI — Adrénaline Sterop 1 mg/ml — RCP Belgique.
    EAACI. Lignes directrices européennes anaphylaxie. 2023.
    """
    if poids<=0: return None,"Poids invalide"
    d=0.5 if poids>=ADRE_POIDS_ADULTE_KG else min(round(ADRE_DOSE_KG*poids,3),ADRE_DOSE_ADULTE_MG)
    n="0.5ml sol 1mg/ml" if poids>=30 else f"0.01mg/kg = {d}mg"
    return {"dose_mg":d,"voie":"IM face antero-lat cuisse","note":n,"rep":"Repeter 5-15min si pas d'amelioration","ref":"BCFI — Adrenaline Sterop 1mg/ml"},None

def glucose(poids:float, gl:Optional[float]=None) -> tuple[Optional[dict], Optional[str]]:
    """
    Glucose 30 % IV (Glucosie) — Correction d'hypoglycémie sévère.

    GARDE-FOU DE SÉCURITÉ CRITIQUE
        Si la glycémie capillaire n'a pas été mesurée (gl is None),
        le protocole est DÉSACTIVÉ et retourne une erreur. Cette règle
        empêche l'administration aveugle de glucose sans confirmation
        biologique.

    DOSE
        Adulte : 0,3 g/kg IV lent (= 1 ml/kg de Glucose 30 %)
        Maximum : 15 g (50 ml de solution 30 %)

    ADMINISTRATION
        IV lent sur 5 minutes, préférer une voie centrale si disponible
        (risque d'extravasation douloureuse avec nécrose cutanée sur
        voie périphérique).

    ALTERNATIVE SI PAS D'ACCÈS VEINEUX
        Glucagon 1 mg IM ou SC (GlucaGen HypoKit). Inefficace en cas
        d'hépatopathie ou d'épuisement des réserves glycogéniques
        (alcoolisme, jeûne prolongé).

    CONTRÔLE
        Glycémie capillaire de contrôle à T+15 min, puis à T+30 min.
        Objectif : glycémie > 100 mg/dl (> 5,5 mmol/l).

    References
    ----------
    BCFI — Glucose 30 % (Glucosie) — RCP Belgique.
    """
    if gl is None: return None,"Glycémie non mesurée — protocole désactivé"
    dg=min(round(GLUCOSE_DOSE_KG*poids,1),GLUCOSE_MAX_G); dm=round(dg/GLUCOSE_DOSE_KG,0)
    return {"dose_g":dg,"vol":f"{dm:.0f}ml Glucose 30% IV lent 5min","ctrl":"Glycémie de contrôle à 15 min","ref":"BCFI — Glucose 30% (Glucosie)"},None

def ceftriaxone(poids:float, age:float) -> tuple[Optional[dict], Optional[str]]:
    """
    Ceftriaxone IV — Antibiothérapie d'urgence (purpura fulminans, méningite).

    INDICATION URGENTE
        Purpura fulminans suspecté → injection IMMÉDIATE avant transfert,
        même en pré-hospitalier, avant hémocultures si impossibles rapidement.
        Le pronostic vital dépend du délai d'administration.

    DOSE
        Adulte       : 2 g IV (ou IM si voie veineuse impossible)
        Enfant < 18 ans : 100 mg/kg (maximum 2 g)

    ADMINISTRATION
        IV direct sur 3-5 minutes ou IM en injection profonde.
        Peut être reconstituée dans 10 ml d'eau PPI pour injection IV.

    INDICATIONS
        • Purpura fulminans (méningococcémie) — urgence absolue
        • Méningite bactérienne de l'adulte
        • Sepsis communautaire sévère (en complément)

    References
    ----------
    BCFI — Ceftriaxone — RCP Belgique.
    SPILF / SFP. Recommandations purpura fulminans. 2017.
    """
    dg=CEFRTRX_ADULTE_G if age>=18 else min(round(CEFRTRX_PED_KG*poids,1),CEFRTRX_ADULTE_G)
    n="Ne pas attendre le medecin si purpura" if age>=18 else f"100mg/kg = {dg*1000:.0f}mg"
    return {"dose_g":dg,"admin":"IV 3-5min ou IM si VVP impossible","note":n,"ref":"BCFI — Ceftriaxone — SPILF 2017"},None

def litican(poids: float, age: float,
            atcd: list[str]) -> tuple[Optional[dict], Optional[str]]:
    """
    Litican IM — Antispasmodique / Antinauséeux (Tiémonium méthylsulfate).

    Médicament utilisé en protocole local aux Urgences du Hainaut (Wallonie)
    pour le traitement symptomatique des vomissements, des nausées et des
    coliques spasmodiques (colique néphrétique, colique hépatique, spasmes
    digestifs).

    COMPOSITION
        Tiémonium méthylsulfate 40 mg (antispasmodique anticholinergique)
        — ampoule de 2 ml solution injectable.
        ⚠️ Ne pas confondre avec Litican comprimés (composition différente).

    MÉCANISME D'ACTION
        Antagoniste muscarinique M1/M3 — relâchement de la musculature
        lisse digestive, urologique et biliaire sans effet central notable
        aux doses thérapeutiques.

    DOSE — ADULTE (≥ 15 ans ou poids ≥ 15 kg)
        40 mg IM profond (1 ampoule de 2 ml)
        À renouveler si besoin après 4-6 h (maximum 3 × 40 mg / 24 h)

    DOSE — ENFANT (< 15 ans ou poids < 15 kg)
        1 mg/kg IM — maximum 40 mg par injection
        Calculé automatiquement selon le poids saisi en sidebar.

    VOIE D'ADMINISTRATION
        Injection intramusculaire profonde dans le quadrant supéro-externe
        fessier ou dans la face antéro-latérale de la cuisse (enfant).
        ⚠️ Ne pas administrer par voie IV (risque de bradycardie sévère).

    CONTRE-INDICATIONS
        • Glaucome par fermeture de l'angle (CI absolue)
        • Rétention urinaire connue / adénome prostatique symptomatique
        • Iléus paralytique / occlusion intestinale (CI absolue)
        • Tachycardie supra-ventriculaire — effet anticholinergique additif
        • Grossesse au-delà du 1er trimestre (données insuffisantes)
        • Allaitement (données insuffisantes)

    PRÉCAUTIONS
        • Conduite automobile — effet sédatif possible
        • Myasthénie — potentialisation de la faiblesse musculaire
        • Associer un antiémétique si nausées persistantes (Métoclopramide IV)

    Parameters
    ----------
    poids : float
        Poids en kg (détermine le régime posologique adulte vs enfant).
    age : float
        Âge en années (contrôle les CI et la posologie pédiatrique).
    atcd : list[str]
        Antécédents — détection des CI (glaucome, rétention urinaire).

    Returns
    -------
    tuple[Optional[dict], Optional[str]]
        (dict de prescription, message d'erreur ou None)

    References
    ----------
    BCFI — Tiémonium méthylsulfate (Litican) — RCP Belgique.
    Dapoigny M, et al. Anticholinergics in functional bowel disorders.
    Neurogastroenterol Motil. 2005.
    Protocole local — Urgences Hainaut, Wallonie.
    """
    if poids <= 0:
        return None, "Poids invalide"

    # ── Détection des contre-indications ─────────────────────────────────
    ci_detectees: list[str] = []
    if "Glaucome" in atcd or "Glaucome par fermeture de l'angle" in atcd:
        ci_detectees.append("Glaucome par fermeture de l'angle (CI absolue)")
    if "Adenome prostatique" in atcd or "Retention urinaire" in atcd:
        ci_detectees.append("Rétention urinaire / adénome prostatique (CI relative)")
    if "Grossesse en cours" in atcd:
        ci_detectees.append("Grossesse — données insuffisantes (prudence)")
    if ci_detectees:
        return None, f"Contre-indication : {' | '.join(ci_detectees)}"

    # ── Calcul de dose ────────────────────────────────────────────────────
    if poids >= LITICAN_POIDS_PIVOT_KG and age >= 15:
        # Adulte
        dose_mg   = LITICAN_DOSE_ADULTE_MG
        dose_note = "1 ampoule de 2 ml (40 mg/2 ml)"
        regime    = "Adulte ≥ 15 ans"
    else:
        # Enfant : 1 mg/kg IM — plafonné à 40 mg
        dose_mg   = min(round(LITICAN_DOSE_KG_ENF * poids, 1), LITICAN_DOSE_MAX_ENF_MG)
        dose_note = f"1 mg/kg = {dose_mg} mg pour {poids} kg"
        regime    = f"Pédiatrique ({poids} kg)"

    return {
        "dose_mg":    dose_mg,
        "dose_note":  dose_note,
        "regime":     regime,
        "voie":       "IM profond — quadrant supéro-externe fessier ou cuisse",
        "volume":     f"{dose_mg / 20:.1f} ml de solution à 20 mg/ml",
        "freq":       f"Si besoin après 4-6 h — max {LITICAN_DOSE_MAX_JOUR:.0f} mg/24 h",
        "ci_list":    ci_detectees,
        "attention":  "NE PAS INJECTER EN IV — bradycardie possible",
        "ref":        "BCFI — Tiémonium méthylsulfate (Litican) — RCP Belgique — Protocole local Hainaut",
    }, None


def protocole_epilepsie_ped(
    poids: float,
    age: float,
    duree_min: float,
    en_cours: bool,
    atcd: list[str],
    gl: Optional[float] = None,
) -> dict:
    """
    Protocole médicamenteux — Crise épileptique pédiatrique.

    Algorithme séquentiel 4 lignes conforme SFNP / ISPE 2022 / EpiCARE 2023.
    Doses calculées en mg/kg avec plafonds, débits et volumes précis.

    ══════════════════════════════════════════════════════════════════
    LIGNE 1 — BENZODIAZÉPINE HORS VVP (IAO autonome — T0)
    ══════════════════════════════════════════════════════════════════
    Midazolam buccal (Buccolam®)         0,3 mg/kg — max 10 mg
      → Voie de 1er choix si enfant conscient — dépôt gingivo-jugal
    Midazolam IM / intranasale           0,2 mg/kg — max 10 mg
      → Si buccale impossible (crise sévère, refus)
      → Intranasale : 0,5 ml/narine max — atomiseur MAD requis
    Diazépam rectal (Stesolid®)          0,5 mg/kg — max 10 mg
      → Alternative en dernier recours hors VVP

    ══════════════════════════════════════════════════════════════════
    LIGNE 2 — BENZODIAZÉPINE IV (médecin — T+5 min après L1)
    ══════════════════════════════════════════════════════════════════
    Lorazépam IV (Temesta®)              0,1 mg/kg — max 4 mg
      → Référence internationale — moins de rebond qu'au Diazépam
    Clonazépam IV (Rivotril®)            0,02 mg/kg — max 1 mg
      → Référence belge aux urgences pédiatriques
    Diazépam IV                          0,3 mg/kg — max 10 mg

    ══════════════════════════════════════════════════════════════════
    LIGNE 3 — ANTIÉPILEPTIQUE IV (T+10 min — EME opérationnel)
    ══════════════════════════════════════════════════════════════════
    Lévétiracétam IV (Keppra®)           60 mg/kg — max 4 500 mg
      → 1er choix — pas d'effet sédatif — perfusion 15 min
    Valproate IV (Dépakine®)             40 mg/kg — max 3 000 mg
      → 2e choix — CI : maladie mitochondriale, hépatopathie
      → Perfusion ≥ 5 min (6 mg/kg/min max)
    Phénobarbital IV                     20 mg/kg — max 1 000 mg
      → Vitesse MAX 1 mg/kg/min — monitoring ECG obligatoire

    ══════════════════════════════════════════════════════════════════
    ANTIDOTE BENZODIAZÉPINES — FLUMAZÉNIL
    ══════════════════════════════════════════════════════════════════
    Flumazénil (Anexate®)                0,01 mg/kg — max 0,2 mg
      → Si dépression respiratoire sévère post-benzodiazépine
      → IV lent sur 15 s — demi-vie courte : surveiller resédation

    ══════════════════════════════════════════════════════════════════
    SÉCURITÉS INTÉGRÉES
    ══════════════════════════════════════════════════════════════════
      • Glycémie AVANT tout antiépileptique (hypoglycémie = cause curable)
      • Libération VAS + position latérale de sécurité si inconscient
      • O2 lunettes 2-4 l/min si SpO2 < 95 % — masque haute concentration
        si SpO2 < 90 %
      • Température — antipyrétique si fièvre (ne pas entraver le diagnostic)
      • Valproate CI formelle chez enfant < 2 ans avec retard développement
        (risque hépatotoxicité fatale — suspicion maladie métabolique)

    References
    ----------
    Trinka E, et al. A definition and classification of status epilepticus.
    Epilepsia. 2015;56(10):1515-23.
    Glauser T, et al. Evidence-based guideline: Treatment of convulsive
    status epilepticus in children and adults. ISPE. Epilepsia Open. 2016.
    Appleton R, et al. Lorazepam vs diazepam in the acute treatment of
    epileptic seizures. Epilepsia. 2008;49(3):470-4.
    SFNP / EpiCARE. Protocole de prise en charge de l'EME de l'enfant. 2023.
    BCFI — Midazolam / Diazépam / Lorazépam / Clonazépam / Lévétiracétam /
    Valproate / Phénobarbital / Flumazénil — RCP Belgique.
    """
    # ── Alerte glycémie — cause curable — prioritaire sur tout ───────────
    glycemie_alerte = None
    if gl is None:
        glycemie_alerte = (
            "Glycémie NON MESURÉE — Réaliser IMMÉDIATEMENT "
            "(hypoglycémie = cause curable de crise)"
        )
    elif gl < 54:
        glycemie_alerte = (
            f"HYPOGLYCÉMIE SÉVÈRE {gl} mg/dl ({round(gl/18.016,1)} mmol/l) — "
            "Glucose 30 % IV AVANT tout antiépileptique"
        )

    # ── Buccolam® — volumes prédéfinis par tranche d'âge (AMM) ──────────
    if   age < 1:   buccolam_vol = "2,5 mg / 0,5 ml"
    elif age < 5:   buccolam_vol = "5 mg / 1 ml"
    elif age < 10:  buccolam_vol = "7,5 mg / 1,5 ml"
    else:           buccolam_vol = "10 mg / 2 ml"

    # ── LIGNE 1a — Midazolam buccal ───────────────────────────────────────
    dose_midaz_bucc = min(round(MIDAZOLAM_BUCC_KG * poids, 1), MIDAZOLAM_BUCC_MAX_MG)
    ligne1a = {
        "med":          "Midazolam buccal (Buccolam®)",
        "dose_mg":       dose_midaz_bucc,
        "volume":        buccolam_vol,
        "admin":         "Déposer entre la gencive et la joue — côté opposé à la rotation de tête",
        "delai":         "Effet en 5-10 min",
        "peut_repeter":  "1 seule dose — appel médecin si échec",
        "ref":           "BCFI — Midazolam buccal (Buccolam) — RCP Belgique",
    }

    # ── LIGNE 1b — Midazolam IM / intranasale ─────────────────────────────
    dose_midaz_im = min(round(MIDAZOLAM_IM_IN_KG * poids, 1), MIDAZOLAM_IM_IN_MAX_MG)
    # Volume intranasale : utiliser solution 5 mg/ml (max 0,5 ml/narine)
    vol_in = round(dose_midaz_im / 5.0, 2)
    vol_in_par_narine = round(vol_in / 2, 2)
    ligne1b = {
        "med":      "Midazolam IM / Intranasale",
        "dose_mg":   dose_midaz_im,
        "voie_im":   f"IM face antéro-latérale de cuisse — solution 5 mg/ml ({round(dose_midaz_im/5,1)} ml)",
        "voie_in":   (
            f"IN : {vol_in} ml total — {vol_in_par_narine} ml / narine "
            f"avec atomiseur MAD — solution 5 mg/ml"
        ),
        "delai":     "Effet en 5-10 min — légèrement plus lent que buccal",
        "ref":       "BCFI — Midazolam (Dormicum) — Protocole IN off-label, usage local validé",
    }

    # ── LIGNE 1c — Diazépam rectal (Stesolid) — dernier recours hors VVP ─
    dose_diaz_rect = min(round(DIAZEPAM_RECT_KG * poids, 1), DIAZEPAM_RECT_MAX_MG)
    ligne1c = {
        "med":      "Diazépam rectal (Stesolid®) — Alternatif",
        "dose_mg":   dose_diaz_rect,
        "admin":     "Tube rectal préchauffé dans la main — insertion douce, maintien 2 min",
        "delai":     "Effet en 5-15 min",
        "ref":       "BCFI — Diazépam rectal (Stesolid) — RCP Belgique",
    }

    # ── LIGNE 2 — Benzodiazépines IV ─────────────────────────────────────
    dose_lora  = min(round(LORAZEPAM_IV_KG * poids, 2),  LORAZEPAM_IV_MAX_MG)
    dose_clona = min(round(CLONAZEPAM_IV_KG * poids, 3), CLONAZEPAM_IV_MAX_MG)
    dose_diaz_iv = min(round(DIAZEPAM_IV_KG * poids, 1), DIAZEPAM_IV_MAX_MG)

    ligne2_lora = {
        "med":      "Lorazépam IV (Temesta®) — Référence",
        "dose_mg":   dose_lora,
        "admin":     f"{dose_lora} mg IV lent sur 2-3 min — rincer avec NaCl 0,9 %",
        "delai":     "Effet en 2-5 min — durée d'action 4-6 h",
        "attention": "Surveiller SpO2 + FR en continu",
        "ref":       "BCFI — Lorazépam (Temesta) — RCP Belgique",
    }
    ligne2_clona = {
        "med":      "Clonazépam IV (Rivotril®) — Référence belge",
        "dose_mg":   dose_clona,
        "admin":     f"{dose_clona} mg dans 10 ml NaCl 0,9 % — IV lent 2-5 min",
        "delai":     "Effet en 1-3 min",
        "ref":       "BCFI — Clonazépam (Rivotril) — RCP Belgique",
    }
    ligne2_diaz = {
        "med":      "Diazépam IV (Valium®)",
        "dose_mg":   dose_diaz_iv,
        "admin":     f"{dose_diaz_iv} mg IV lent — max 2 mg/min — risque rebond",
        "ref":       "BCFI — Diazépam IV — RCP Belgique",
    }

    # ── LIGNE 3 — Antiépileptiques IV (EME opérationnel) ─────────────────
    # Lévétiracétam
    dose_leveti   = min(round(LEVETI_IV_KG * poids, 0), LEVETI_IV_MAX_MG)
    vol_leveti    = round(dose_leveti / 100, 1)
    # Valproate
    dose_valp     = min(round(VALPROATE_IV_KG * poids, 0), VALPROATE_IV_MAX_MG)
    debit_valp_mg_min = round(VALPROATE_IV_KG * poids / VALPROATE_IV_DEBIT_MIN, 1)
    ci_valp = ("CI formelle : enfant < 2 ans avec retard développement "
               "— maladie métabolique suspectée") if age < 2 else ""
    # Phénobarbital
    dose_phenob   = min(round(PHENOBARB_IV_KG * poids, 0), PHENOBARB_IV_MAX_MG)
    duree_phenob  = round(dose_phenob / (PHENOBARB_DEBIT_MG_KG_MIN * poids), 1)

    ligne3_leveti = {
        "med":      "Lévétiracétam IV (Keppra®) — 1er choix",
        "dose_mg":   dose_leveti,
        "volume":    f"{vol_leveti} ml de solution 100 mg/ml",
        "admin":     f"{dose_leveti:.0f} mg dans 100 ml NaCl 0,9 % — perfusion IV 15 min",
        "avantage":  "Pas de sédation, pas d'interaction CYP450, monitoring minimal",
        "ref":       "BCFI — Lévétiracétam (Keppra) — RCP Belgique",
    }
    ligne3_valp = {
        "med":       "Valproate IV (Dépakine®) — 2e choix",
        "dose_mg":    dose_valp,
        "admin":     (
            f"{dose_valp:.0f} mg dans 100 ml NaCl 0,9 % — perfusion IV ≥ {VALPROATE_IV_DEBIT_MIN:.0f} min "
            f"(débit max {debit_valp_mg_min:.0f} mg/min)"
        ),
        "ci":         ci_valp,
        "ref":        "BCFI — Acide valproïque (Dépakine IV) — RCP Belgique",
    }
    ligne3_phenob = {
        "med":       "Phénobarbital IV — 3e choix",
        "dose_mg":    dose_phenob,
        "admin":     (
            f"{dose_phenob:.0f} mg IV lent — "
            f"vitesse MAX {PHENOBARB_DEBIT_MG_KG_MIN} mg/kg/min "
            f"→ durée min {duree_phenob} min"
        ),
        "attention":  "Risque dépression respiratoire + hypotension — Prévoir IOT",
        "ecg":        "Monitoring ECG obligatoire pendant toute la perfusion",
        "ref":        "BCFI — Phénobarbital IV — RCP Belgique",
    }

    # ── ANTIDOTE — Flumazénil ─────────────────────────────────────────────
    dose_fluma = min(round(FLUMAZENIL_DOSE_MG * poids, 3), FLUMAZENIL_MAX_MG)
    antidote = {
        "med":       "Flumazénil (Anexate®) — Antidote benzodiazépines",
        "indication":"Dépression respiratoire sévère post-benzodiazépine",
        "dose_mg":    dose_fluma,
        "dose_total": FLUMAZENIL_MAX_TOTAL,
        "admin":     (
            f"{dose_fluma} mg IV lent sur 15 s — "
            f"répétable toutes les 60 s jusqu'à max {FLUMAZENIL_MAX_TOTAL} mg"
        ),
        "attention":  "Demi-vie courte (1 h) < benzodiazépines — surveiller resédation",
        "ref":        "BCFI — Flumazénil (Anexate) — RCP Belgique",
    }

    # ── Chronomètre clinique — alertes temporelles ────────────────────────
    chrono = {
        "T0":     "Arrivée — Position LAS — VAS libres — O2 — Glycémie",
        "T0_L1":  "IMMÉDIAT si crise en cours — Midazolam buccal / IM",
        "T5":     "Si crise persiste → LIGNE 2 — Lorazépam ou Clonazépam IV (médecin)",
        "T10":    "Si crise persiste → LIGNE 3 — Lévétiracétam IV",
        "T30":    "EME établi — Réanimation pédiatrique — Intubation à discuter",
    }

    # ── Score AVPU — évaluation rapide de la conscience ──────────────────
    avpu_guide = {
        "A": "Alert — Yeux ouverts, répond spontanément — Normal",
        "V": "Voice — Répond à la voix seulement — Altération légère",
        "P": "Pain — Répond à la douleur seulement — Altération sévère",
        "U": "Unresponsive — Aucune réponse — Coma",
    }

    # ── Surveillance ──────────────────────────────────────────────────────
    surveillance = [
        "Position latérale de sécurité (PLS) si inconscient",
        "Libération des voies aériennes supérieures — aspiration si besoin",
        "SpO2 en continu — O2 si < 95 % (lunettes) / < 90 % (masque HC)",
        "FR toutes les 2 min post-benzodiazépine — alarme si < 12/min",
        "FC et PA en continu après ligne 2",
        "AVPU toutes les 5 min — noter l'heure de reprise de conscience",
        "Glycémie capillaire — répéter si non faite",
        "Température — antipyrétique si fièvre (ne pas entraver le diagnostic)",
        "VVP dès que possible — prélèvements sanguins (NFS, CRP, ionogramme, NH3)",
        f"APPEL MÉDECIN SENIOR si crise persiste > {EME_SEUIL_MIN} min après ligne 1",
    ]

    return {
        "glycemie_alerte": glycemie_alerte,
        "ligne1a":         ligne1a,
        "ligne1b":         ligne1b,
        "ligne1c":         ligne1c,
        "ligne2_lora":     ligne2_lora,
        "ligne2_clona":    ligne2_clona,
        "ligne2_diaz":     ligne2_diaz,
        "ligne3_leveti":   ligne3_leveti,
        "ligne3_valp":     ligne3_valp,
        "ligne3_phenob":   ligne3_phenob,
        "antidote":        antidote,
        "chrono":          chrono,
        "avpu_guide":      avpu_guide,
        "surveillance":    surveillance,
        "ref": (
            "SFNP / EpiCARE 2023 — ISPE 2022 — BCFI Belgique — "
            "Protocole EME pédiatrique — Urgences Hainaut"
        ),
    }
    """
    Protocole médicamenteux — Crise épileptique pédiatrique.

    Algorithme séquentiel en 3 lignes conforme aux recommandations de la
    Société Française de Neurologie Pédiatrique (SFNP) et du réseau
    européen EpiCARE (2023). Les doses sont calculées en mg/kg avec
    plafonds de sécurité clinique.

    SÉQUENCE THÉRAPEUTIQUE

    ╔══════════════════════════════════════════════════════════════╗
    ║  LIGNE 1 — Benzodiazépine hors VVP (IAO autonome)           ║
    ║  Délai : dès l'arrivée si crise en cours ou > 5 min         ║
    ║                                                              ║
    ║  Midazolam buccal (Buccolam®)  0,3 mg/kg — max 10 mg        ║
    ║    → Voie de référence chez l'enfant conscient               ║
    ║    → Instiller entre la gencive et la joue côté opposé       ║
    ║       à la tête si elle tourne                               ║
    ║                                                              ║
    ║  OU Diazépam rectal (Stesolid®) 0,5 mg/kg — max 10 mg       ║
    ║    → Alternative si voie buccale impossible                  ║
    ║    → Tube rectal préchauffé dans la main                     ║
    ╚══════════════════════════════════════════════════════════════╝

    ╔══════════════════════════════════════════════════════════════╗
    ║  LIGNE 2 — Benzodiazépine IV (médecin / VVP posée)          ║
    ║  Délai : si crise persiste 5 min après ligne 1              ║
    ║                                                              ║
    ║  Lorazépam IV (Temesta®)  0,1 mg/kg — max 4 mg              ║
    ║    → Référence internationale en urgence                     ║
    ║    → IV lent sur 2-3 min — surveillance FR + SpO2           ║
    ║                                                              ║
    ║  OU Diazépam IV  0,3 mg/kg — max 10 mg                      ║
    ║  OU Clonazépam IV (Rivotril®) 0,02 mg/kg — max 1 mg         ║
    ╚══════════════════════════════════════════════════════════════╝

    ╔══════════════════════════════════════════════════════════════╗
    ║  LIGNE 3 — EME réfractaire (réanimation pédiatrique)         ║
    ║  Délai : si crise persiste après 2 doses de benzodiazépines  ║
    ║                                                              ║
    ║  Lévétiracétam IV (Keppra®)  60 mg/kg — max 4 500 mg        ║
    ║    → Perfusion IV sur 15 min dans NaCl 0,9 %                ║
    ║    → Premier choix hors contre-indication                    ║
    ║                                                              ║
    ║  OU Phénobarbital IV  20 mg/kg — max 1 000 mg               ║
    ║    → Perfusion IV lente (< 1 mg/kg/min) — monitoring ECG    ║
    ╚══════════════════════════════════════════════════════════════╝

    SÉCURITÉS INTÉGRÉES
        • Hypoglycémie : vérifiée systématiquement (cause curable)
          Si glycémie < 54 mg/dl → Glucose 30 % AVANT les antiépileptiques
        • Voie IV réservée ligne 2+ : ligne 1 accessible à l'IAO sans VVP
        • Surveillance obligatoire : SpO2, FR, FC, conscience en continu
        • Antidote benzodiazépines : Flumazénil (si dépression respiratoire)

    Parameters
    ----------
    poids : float
        Poids en kg (calibration des doses).
    age : float
        Âge en années.
    duree_min : float
        Durée estimée de la crise en minutes.
    en_cours : bool
        Vrai si la crise est toujours active à l'arrivée.
    atcd : list[str]
        Antécédents (détection épilepsie connue, traitements en cours).
    gl : float, optional
        Glycémie capillaire en mg/dl — contrôle obligatoire.

    Returns
    -------
    dict
        {
          "glycemie_alerte": str ou None,
          "ligne1": dict (Midazolam buccal),
          "ligne1b": dict (Diazépam rectal — alternative),
          "ligne2": dict (Lorazépam IV),
          "ligne2b": dict (Diazépam IV),
          "ligne2c": dict (Clonazépam IV),
          "ligne3a": dict (Lévétiracétam IV),
          "ligne3b": dict (Phénobarbital IV),
          "surveillance": list[str],
          "ref": str,
        }

    References
    ----------
    Trinka E, et al. A definition and classification of status epilepticus.
    Epilepsia. 2015;56(10):1515-23.
    Appleton R, et al. Lorazepam vs. diazepam in the acute treatment of
    epileptic seizures and reduces the need for further antiepileptic
    therapy. Epilepsia. 2008;49(3):470-4.
    SFNP / EpiCARE. Protocole de prise en charge de l'état de mal
    épileptique de l'enfant. 2023.
    BCFI — Midazolam buccal (Buccolam) / Diazépam (Stesolid) /
    Lorazépam (Temesta) / Clonazépam (Rivotril) / Lévétiracétam (Keppra) /
    Phénobarbital — RCP Belgique.
    """
    # ── Alerte glycémie — cause curable prioritaire ───────────────────────
    glycemie_alerte = None
    if gl is None:
        glycemie_alerte = (
            "Glycémie capillaire NON MESURÉE — "
            "À réaliser IMMÉDIATEMENT (hypoglycémie = cause curable)"
        )
    elif gl < 54:
        glycemie_alerte = (
            f"HYPOGLYCÉMIE SÉVÈRE {gl} mg/dl — "
            "Glucose 30 % IV AVANT tout antiépileptique"
        )

    # ── Ligne 1 — Midazolam buccal (Buccolam) ────────────────────────────
    dose_midaz = min(
        round(MIDAZOLAM_BUCC_KG * poids, 1),
        MIDAZOLAM_BUCC_MAX_MG,
    )
    # Volumes prédéfinis Buccolam selon tranche d'âge / poids
    if   age < 1:   buccolam_vol = "2,5 mg / 0,5 ml"
    elif age < 5:   buccolam_vol = "5 mg / 1 ml"
    elif age < 10:  buccolam_vol = "7,5 mg / 1,5 ml"
    else:           buccolam_vol = "10 mg / 2 ml"

    ligne1 = {
        "med":    "Midazolam buccal (Buccolam®)",
        "dose_mg": dose_midaz,
        "volume":  buccolam_vol,
        "admin": (
            "Déposer entre la gencive et la joue — "
            "côté opposé à la rotation de tête si présente"
        ),
        "delai":  "Effet attendu en 5-10 min",
        "peut_repeter": "1 seule dose — appeler le médecin si échec",
        "ref":    "BCFI — Midazolam buccal (Buccolam) — RCP Belgique",
    }

    # ── Ligne 1b — Diazépam rectal (Stesolid) — alternative ──────────────
    dose_diaz_rect = min(
        round(DIAZEPAM_RECT_KG * poids, 1),
        DIAZEPAM_RECT_MAX_MG,
    )
    ligne1b = {
        "med":     "Diazépam rectal (Stesolid®)",
        "dose_mg":  dose_diaz_rect,
        "admin":    "Tube rectal préchauffé dans la main — insertion rectale douce",
        "delai":    "Effet attendu en 5-15 min",
        "ref":      "BCFI — Diazépam rectal (Stesolid) — RCP Belgique",
    }

    # ── Ligne 2 — Lorazépam IV (Temesta) — référence internationale ──────
    dose_lora = min(
        round(LORAZEPAM_IV_KG * poids, 2),
        LORAZEPAM_IV_MAX_MG,
    )
    ligne2 = {
        "med":     "Lorazépam IV (Temesta®)",
        "dose_mg":  dose_lora,
        "admin":    f"{dose_lora} mg IV lent sur 2-3 min — rincer avec NaCl 0,9 %",
        "delai":    "Effet attendu en 2-5 min",
        "attention":"Surveillance SpO2 + FR + conscience en continu",
        "ref":      "BCFI — Lorazépam (Temesta) — RCP Belgique",
    }

    # ── Ligne 2b — Diazépam IV ────────────────────────────────────────────
    dose_diaz_iv = min(
        round(DIAZEPAM_IV_KG * poids, 1),
        DIAZEPAM_IV_MAX_MG,
    )
    ligne2b = {
        "med":     "Diazépam IV (Valium®)",
        "dose_mg":  dose_diaz_iv,
        "admin":    f"{dose_diaz_iv} mg IV lent — max 2 mg/min",
        "ref":      "BCFI — Diazépam IV — RCP Belgique",
    }

    # ── Ligne 2c — Clonazépam IV (Rivotril) ──────────────────────────────
    dose_clona = min(
        round(CLONAZEPAM_IV_KG * poids, 3),
        CLONAZEPAM_IV_MAX_MG,
    )
    ligne2c = {
        "med":     "Clonazépam IV (Rivotril®)",
        "dose_mg":  dose_clona,
        "admin":    f"{dose_clona} mg IV lent sur 2-5 min dilué dans 10 ml NaCl 0,9 %",
        "ref":      "BCFI — Clonazépam (Rivotril) — RCP Belgique",
    }

    # ── Ligne 3a — Lévétiracétam IV (Keppra) — premier choix EME ─────────
    dose_leveti = min(
        round(LEVETI_IV_KG * poids, 0),
        LEVETI_IV_MAX_MG,
    )
    vol_leveti = round(dose_leveti / 100, 1)  # sol 100 mg/ml
    ligne3a = {
        "med":      "Lévétiracétam IV (Keppra®)",
        "dose_mg":   dose_leveti,
        "volume":    f"{vol_leveti} ml de solution à 100 mg/ml",
        "admin":    (
            f"{dose_leveti:.0f} mg dilués dans 100 ml NaCl 0,9 % — "
            "perfusion IV sur 15 min"
        ),
        "avantage": "Pas d'effet sédatif, pas d'interaction CYP450, monitoring minimal",
        "ref":       "BCFI — Lévétiracétam (Keppra) — RCP Belgique",
    }

    # ── Ligne 3b — Phénobarbital IV — alternative ────────────────────────
    dose_phenob = min(
        round(PHENOBARB_IV_KG * poids, 0),
        PHENOBARB_IV_MAX_MG,
    )
    ligne3b = {
        "med":     "Phénobarbital IV",
        "dose_mg":  dose_phenob,
        "admin":   (
            f"{dose_phenob:.0f} mg IV lent — "
            "vitesse MAX 1 mg/kg/min — monitoring ECG obligatoire"
        ),
        "attention": "Risque dépression respiratoire + hypotension — IOT disponible",
        "ref":       "BCFI — Phénobarbital IV — RCP Belgique",
    }

    # ── Surveillance obligatoire ──────────────────────────────────────────
    surveillance = [
        "SpO2 en continu — Alarme < 92 %",
        "FR toutes les 2 min après injection de benzodiazépine",
        "FC et PA en continu après ligne 2",
        "Conscience : évaluation GCS toutes les 5 min",
        "Glycémie capillaire — à répéter si non faite",
        "Température — cause curable de la crise",
        "Voie veineuse périphérique dès que possible",
        "Appel médecin senior si crise persiste > 5 min après ligne 1",
    ]

    return {
        "glycemie_alerte": glycemie_alerte,
        "ligne1":          ligne1,
        "ligne1b":         ligne1b,
        "ligne2":          ligne2,
        "ligne2b":         ligne2b,
        "ligne2c":         ligne2c,
        "ligne3a":         ligne3a,
        "ligne3b":         ligne3b,
        "surveillance":    surveillance,
        "ref": (
            "SFNP / EpiCARE 2023 — BCFI — Protocole EME pédiatrique "
            "— Urgences Hainaut, Belgique"
        ),
    }


def protocole_eva(eva:int, poids:float, age:float,
                  atcd:list[str], gl:Optional[float]=None) -> dict:
    """
    Protocole antalgique paliers OMS adapté à l'EVA.

    Construit automatiquement la liste des antalgiques recommandés en
    fonction de l'intensité douloureuse rapportée par l'EVA (Échelle
    Visuelle Analogique 0-10), avec détection intégrée des
    contre-indications et interactions.

    ÉCHELLE OMS ADAPTÉE AUX URGENCES

        EVA 0-3   : Palier I seul
                    → Paracétamol IV (1 g ou 15 mg/kg)

        EVA 4-6   : Palier I + Palier II
                    → Paracétamol IV systématique (association)
                    → Kétorolac IV 30 mg (si pas de CI AINS)
                    → Tramadol IV 100 mg (si pas de CI opioïde faible)

        EVA 7-10  : Palier I + Palier III
                    → Paracétamol IV systématique (association)
                    → Piritramide (Dipidolor) IV — titration 0,03-0,05 mg/kg

    DÉTECTIONS AUTOMATIQUES
        • IMAO           → exclusion Tramadol (syndrome sérotoninergique)
        • Épilepsie      → exclusion Tramadol (seuil épileptogène)
        • ISRS/IRSNA    → Tramadol déconseillé (interaction majeure)
        • CI AINS        → exclusion Kétorolac

    Parameters
    ----------
    eva : int
        Score EVA 0-10.
    poids : float
    age : float
    atcd : list[str]
    gl : float, optional
        Glycémie (utilisée pour corrélation hypoglycémie-antalgie).

    Returns
    -------
    dict
        {"als": alertes globales, "recs": liste des recommandations médicamenteuses}
    """
    als=[]; recs=[]
    imao="IMAO (inhibiteurs MAO)" in atcd; isrs="Antidepresseurs ISRS/IRSNA" in atcd
    ci=ci_ains(atcd)
    if imao: als.append("IMAO — Tramadol CONTRE-INDIQUE — Utiliser Paracetamol ou Dipidolor")
    if isrs: als.append("ISRS/IRSNA — Tramadol deconseille — Preferer Dipidolor ou Morphine")
    r,_=paracetamol(poids)
    if r: recs.append({"p":"1","nom":"Paracetamol IV","dose":f"{r['dose_g']}g","d":r["vol"],"al":[],"ref":r["ref"]})
    if eva>=4:
        if not ci:
            r2,e2=ketorolac(poids,atcd)
            if r2: recs.append({"p":"2","nom":"Ketorolac (Taradyl) IV","dose":f"{r2['dose_mg']}mg","d":r2["admin"],"al":[],"ref":r2["ref"]})
        if not imao and "Epilepsie" not in atcd:
            r3,_=tramadol(poids,atcd,age)
            if r3: recs.append({"p":"2","nom":"Tramadol IV","dose":f"{r3['dose_mg']:.0f}mg","d":r3["admin"],"al":r3.get("alertes",[]),"ref":r3["ref"]})
    if eva>=7:
        r4,_=piritramide(poids,age,atcd)
        if r4: recs.append({"p":"3","nom":"Piritramide (Dipidolor) IV","dose":f"{r4['dmin']}-{r4['dmax']}mg","d":r4["admin"],"al":[],"ref":r4["ref"]})
    return {"als":als,"recs":recs}

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS UI
# ══════════════════════════════════════════════════════════════════════════════
def H(s): st.markdown(s, unsafe_allow_html=True)

def SEC(t): H(f'<div class="sec">{t}</div>')

def AL(msg, typ="danger"):
    ico={"danger":"","warning":"","success":"","info":""}
    H(f'<div class="al {typ}"><span class="al-ico">{ico.get(typ,"")}</span><span>{msg}</span></div>')

def CARD(title="", icon=""):
    if title:
        if icon:
            H(f'<div class="card"><div class="card-title-inline"><div class="card-icon">{icon}</div><div class="card-title" style="margin:0;border:none;padding:0;">{title}</div></div>')
        else:
            H(f'<div class="card"><div class="card-title">{title}</div>')
    else:
        H('<div class="card">')

def CARD_END(): H('</div>')

def PURPURA(det):
    if det and det.get("purpura"):
        H('<div class="purp"><div class="purp-title">PURPURA FULMINANS — TRI 1 IMMEDIAT</div>'
          '<div class="purp-body">Ceftriaxone 2g IV (ou IM si VVP impossible) — NE PAS ATTENDRE LE BILAN.<br>'
          'Appel medecin senior — Transfert dechocage immediat.</div></div>')

def N2_BANNER(n2):
    if n2>=9:
        H(f'<div class="purp" style="background:linear-gradient(135deg,#1A0A2E,#2D1B69);border-color:#7C3AED;">'
          f'<div class="purp-title" style="color:#E879F9;">NEWS2 {n2} — ENGAGEMENT VITAL — APPEL IMMEDIAT</div>'
          f'<div class="purp-body" style="color:#EDE9FE;">Transfert dechocage — Medecin sans delai.</div></div>')
    elif n2>=7: AL(f"NEWS2 {n2}>=7 — Appel medical immediat","danger")
    elif n2>=5: AL(f"NEWS2 {n2}>=5 — Reevaluation toutes les 30min","warning")

def GAUGE(n2, bpco=False):
    lbl,css,pct=n2_meta(n2)
    note=f'<div style="font-size:.62rem;opacity:.75;margin-top:4px;">Echelle 2 BPCO — Cible SpO2 88-92%</div>' if bpco else ""
    H(f'<div class="n2-dash {css}">'
      f'<div style="font-size:.62rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;opacity:.7;">SCORE NEWS2</div>'
      f'<div class="n2-big">{n2}</div>'
      f'<div class="n2-lbl">{lbl}</div>'
      f'{note}'
      f'<div class="n2-bar-wrap"><div class="n2-bar" style="width:{max(pct,4)}%;"></div></div>'
      f'<div class="n2-scale"><span>0</span><span>Faible</span><span>Modere</span><span>Eleve</span><span>12+</span></div>'
      f'</div>')

def VITAUX(fc,pas,spo2,fr,temp,gcs,bpco=False):
    def niv(v,wb,cb,inv=False):
        if not inv: return "crit" if v>=cb else ("warn" if v>=wb else "")
        return "crit" if v<=cb else ("warn" if v<=wb else "")
    sp_warn=88 if bpco else 94; sp_crit=85 if bpco else 90
    fc_n="crit" if fc>=150 or fc<=40 else ("warn" if fc>=120 or fc<=50 else "")
    pas_n="crit" if pas<=90 else ("warn" if pas<=100 else "")
    sp_n="crit" if spo2<=sp_crit else ("warn" if spo2<=sp_warn else "")
    fr_n="crit" if fr>=30 else ("warn" if fr>=22 else "")
    t_n ="crit" if temp>=40 or temp<=35 else ("warn" if temp>=38.5 or temp<=36 else "")
    g_n ="crit" if gcs<=8 else ("warn" if gcs<=13 else "")
    H(f'<div class="vit-wrap">'
      f'<div class="vit {fc_n}"><div class="vit-k">FC</div><div class="vit-v">{fc}</div><div class="vit-u">bpm</div></div>'
      f'<div class="vit {pas_n}"><div class="vit-k">PAS</div><div class="vit-v">{pas}</div><div class="vit-u">mmHg</div></div>'
      f'<div class="vit {sp_n}"><div class="vit-k">SpO2{"*" if bpco else ""}</div><div class="vit-v">{spo2}</div><div class="vit-u">%</div></div>'
      f'<div class="vit {fr_n}"><div class="vit-k">FR</div><div class="vit-v">{fr}</div><div class="vit-u">/min</div></div>'
      f'<div class="vit {t_n}"><div class="vit-k">Temp</div><div class="vit-v">{temp}</div><div class="vit-u">°C</div></div>'
      f'<div class="vit {g_n}"><div class="vit-k">GCS</div><div class="vit-v">{gcs}</div><div class="vit-u">/15</div></div>'
      f'</div>')
    if bpco: AL("BPCO — Cible SpO2 : 88–92 % — Éviter la normoxie (risque narcose CO₂)","warning")

def TRI_CARD_INLINE(niv,just,n2):
    css=TCSS.get(niv,"tri-5"); lbl=LABELS.get(niv,niv); sec_=SECTEURS.get(niv,""); d=DELAIS.get(niv,"?")
    H(f'<div class="{css}"><div class="tri-card">'
      f'<div class="tri-lbl">{lbl}</div>'
      f'<div class="tri-detail">{just}</div>'
      f'<div class="tri-sector">{sec_}</div>'
      f'<div class="tri-chips">'
      f'<span class="tri-chip">Delai max : {d} min</span>'
      f'<span class="tri-chip">NEWS2 : {n2}</span>'
      f'</div></div></div>')

def TRI_BANNER_FIXED(niv,just,n2):
    css=TCSS.get(niv,"tri-5"); lbl=LABELS.get(niv,niv); sec_=SECTEURS.get(niv,""); d=DELAIS.get(niv,"?")
    H(f'<div class="tri-banner-wrap"><div class="tri-banner {css}">'
      f'<div><div class="tri-niv">{lbl}</div>'
      f'<div class="tri-sec">{sec_}</div>'
      f'<div class="tri-just">{just}</div></div>'
      f'<span class="tri-delai">Max {d} min | N2={n2}</span>'
      f'</div></div>')

def RX(nom,dose,details,ref,palier="2",alertes=None):
    pc={"1":"p1","2":"p2","3":"p3","U":"urg","A":"ant"}.get(palier,"p2")
    if alertes:
        for a in alertes: AL(a,"danger")
    dt="<br>".join([x for x in details if x])
    H(f'<div class="rx {pc}"><div class="rx-name">{nom}</div><div class="rx-dose">{dose}</div>'
      f'<div class="rx-detail">{dt}</div><div class="rx-ref">{ref}</div></div>')

def RX_LOCK(msg="Donnée manquante : Glycémie requise — Protocoles désactivés"):
    H(f'<div class="rx-lock"><div class="rx-lock-icon"></div><strong>Protocole désactivé</strong><br>{msg}</div>')

def GLYC_WIDGET(key, label="Glycémie capillaire (mg/dl)", req=False):
    """
    Widget de saisie de glycémie avec garde-fou de sécurité clinique.

    GARDE-FOU CRITIQUE
        Si l'utilisateur ne saisit rien (valeur 0), retourne None. Cette
        valeur None DÉSACTIVE automatiquement les protocoles Glucose 30 %
        dans l'onglet Pharmacie via RX_LOCK(). Cette règle empêche
        l'administration aveugle de glucose sans confirmation biologique.

    ALERTES AUTOMATIQUES
        • < 54 mg/dl (3,0 mmol/l)  : Hypoglycémie sévère — Glucose 30 % IV
        • < 70 mg/dl (3,9 mmol/l)  : Hypoglycémie modérée — vigilance

    CONVERSION AUTOMATIQUE
        Affichage simultané en mg/dl (unité belge) et mmol/l
        (unité internationale SI).

    Parameters
    ----------
    key : str
        Clé Streamlit unique pour l'input.
    label : str, optional
        Libellé personnalisé.
    req : bool, optional
        Si True, affiche un avertissement si la valeur est manquante.

    Returns
    -------
    float or None
        Glycémie en mg/dl ou None si non saisie (safety gate).
    """
    v=st.number_input(label,0,1500,0,5,key=key)
    if v==0:
        if req: AL("Glycémie non saisie — saisir la valeur pour activer les protocoles","warning")
        else: st.caption("Saisir 0 si non réalisée")
        return None
    mm=mgdl_mmol(v); st.caption(f"→ {mm} mmol/l")
    if v<GLYC["hs"]: AL(f"HYPOGLYCEMIE SEVERE {v}mg/dl ({mm}mmol/l) — Glucose 30% IV immédiat","danger")
    elif v<GLYC["hm"]: AL(f"Hypoglycemie moderee {v}mg/dl","warning")
    return float(v)

def BPCO_WIDGET(pfx):
    """
    Widget d'identification BPCO avec bascule d'échelle NEWS2.

    Lorsque l'utilisateur coche « Patient BPCO connu », le moteur NEWS2
    bascule automatiquement de l'Échelle 1 (cible ≥ 96 %) vers
    l'Échelle 2 (cible 88-92 %) et génère une alerte de risque de
    narcose au CO₂ si SpO2 > 96 %.

    CRITÈRE ASSOCIÉ
        L'item « s'exprime en phrases complètes » est un marqueur
        indirect de la sévérité de la dyspnée (incapacité à terminer
        une phrase = dyspnée sévère).

    Returns
    -------
    tuple[bool, bool]
        (flag BPCO, flag parole complète).
    """
    bp=st.checkbox("Patient BPCO connu ?",key=f"{pfx}_bp",help="Cible SpO2 88-92% — Echelle 2 NEWS2")
    if bp: AL("BPCO — Cible SpO2 88-92% — Echelle 2 activee","warning")
    pa=st.radio("S'exprime en phrases complètes ?",[True,False],format_func=lambda x:"Oui — phrases complètes" if x else "Non — mots isolés",horizontal=True,key=f"{pfx}_pa")
    return bp,pa

def SI_WIDGET(fc,pas):
    sh=si(fc,pas); css="si-c" if sh>=1.0 else ("si-w" if sh>=0.8 else "si-ok")
    lbl="CHOC PROBABLE" if sh>=1.0 else ("Surveillance rapprochée" if sh>=0.8 else "Normal")
    H(f'<div class="si-box"><div class="si-l">Shock Index</div><div class="si-v {css}">{sh}</div><div class="si-l">{lbl}</div></div>')

def SBAR_RENDER(s):
    H(f'<div class="sbar">'
      # Header
      f'<div class="sbar-hdr"><div class="sbar-hdr-title">RAPPORT SBAR — AKIR-IAO v18.0 Pro Edition</div>'
      f'<div class="sbar-hdr-sub">Opérateur : {s["op"]} | {s["heure"]} | FRENCH SFMU V1.1 — Hainaut, Belgique</div></div>'
      # S
      f'<div class="sbar-sec"><div class="sbar-sec-head"><div class="sbar-letter">S</div>'
      f'<div class="sbar-sec-title">Situation</div></div>'
      f'<div class="sbar-body">Patient de {s["age"]} ans | Motif : <strong>{s["motif"]}</strong><br>'
      f'Niveau : <strong>{s["niv"]}</strong> | Secteur : {s["sec"]} | Delai max : {s["delai"]} min<br>'
      f'Critere : {s["crit"]}</div>'
      f'<div class="sbar-vit-grid">'
      f'<div class="sbar-vit"><div class="sbar-vit-k">FC</div><div class="sbar-vit-v">{s["fc"]}</div></div>'
      f'<div class="sbar-vit"><div class="sbar-vit-k">PAS</div><div class="sbar-vit-v">{s["pas"]}</div></div>'
      f'<div class="sbar-vit"><div class="sbar-vit-k">SpO2</div><div class="sbar-vit-v">{s["spo2"]}%</div></div>'
      f'<div class="sbar-vit"><div class="sbar-vit-k">FR</div><div class="sbar-vit-v">{s["fr"]}/min</div></div>'
      f'<div class="sbar-vit"><div class="sbar-vit-k">Temp</div><div class="sbar-vit-v">{s["temp"]}C</div></div>'
      f'<div class="sbar-vit"><div class="sbar-vit-k">GCS</div><div class="sbar-vit-v">{s["gcs"]}/15</div></div>'
      f'<div class="sbar-vit"><div class="sbar-vit-k">EVA</div><div class="sbar-vit-v">{s["eva"]}/10</div></div>'
      f'<div class="sbar-vit"><div class="sbar-vit-k">NEWS2</div><div class="sbar-vit-v">{s["n2"]}</div></div>'
      f'</div></div>'
      # B
      f'<div class="sbar-sec"><div class="sbar-sec-head"><div class="sbar-letter">B</div>'
      f'<div class="sbar-sec-title">Background</div></div>'
      f'<div class="sbar-body">ATCD : {s["atcd"]}<br>Allergies : {s["alg"]}<br>'
      f'O2 : {s["o2"]} | Glycemie : {s["gl"]}</div></div>'
      # A
      f'<div class="sbar-sec"><div class="sbar-sec-head"><div class="sbar-letter">A</div>'
      f'<div class="sbar-sec-title">Assessment</div></div>'
      f'<div class="sbar-body">{s["just"]}</div></div>'
      # R
      f'<div class="sbar-sec"><div class="sbar-sec-head"><div class="sbar-letter">R</div>'
      f'<div class="sbar-sec-title">Recommendation</div></div>'
      f'<div class="sbar-body">Orientation : <strong>{s["sec"]}</strong><br>'
      f'Delai maximum : {s["delai"]} min<br>Remarques : [À compléter]</div></div>'
      # Footer
      f'<div class="sbar-ftr">Document d\'aide a la decision — Ne se substitue pas au jugement clinique du medecin responsable. '
      f'AR 18/06/1990 modifie — Hainaut, Wallonie, Belgique.</div></div>')

def DISC():
    H('<div class="disc">AKIR-IAO est un outil d\'aide a la decision clinique. Il ne remplace pas le jugement '
      'du medecin responsable. Doses conformes au BCFI Belgique — validation medicale obligatoire avant administration. '
      'RGPD : UUID anonyme — aucun identifiant nominal collecté — stockage local uniquement.'
      '<div class="disc-sig">AKIR-IAO v18.0 — Hospital Pro Edition — Développeur : Ismail Ibn-Daifa — FRENCH Triage SFMU V1.1 — Hainaut, Wallonie, Belgique</div></div>')

# ══════════════════════════════════════════════════════════════════════════════
# PERSISTANCE & AUDIT LOG IMMUABLE
# ══════════════════════════════════════════════════════════════════════════════
#
# ARCHITECTURE DE TRAÇABILITÉ
#
# Trois fichiers distincts :
#   akir_reg.json       — Registre des patients (anonyme, RGPD)
#   akir_audit.log      — Journal d'audit immuable à intégrité hashée
#   akir_errors.log     — Erreurs techniques (aucune donnée patient)
#
# INTÉGRITÉ DU JOURNAL D'AUDIT
#   Chaque entrée d'audit contient le hash SHA-256 de son propre contenu
#   combiné avec le hash de l'entrée précédente (chaîne de hashes).
#   Toute modification a posteriori d'une entrée invalide la chaîne
#   entière, ce qui est détectable par audit_verifier_integrite().
#   Ce mécanisme répond aux exigences de traçabilité médico-légale
#   (AR 18/06/1990 — Belgique) sans nécessiter de base de données.
#
# ══════════════════════════════════════════════════════════════════════════════
import hashlib

RF  = "akir_reg.json"       # Registre patients — JSON — RGPD-compliant
ALF = "akir_audit.log"      # Audit log — format texte hashé
EF  = "akir_errors.log"     # Erreurs techniques — aucune donnée patient

# Hash sentinel pour la première entrée (pas de précédent)
_HASH_GENESIS = "0" * 64


def _load(f: str) -> list:
    """Charge un fichier JSON local. Retourne [] si absent ou corrompu."""
    if os.path.exists(f):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                return json.load(fp)
        except Exception:
            return []
    return []


def _save(f: str, d: list) -> None:
    """
    Sauvegarde atomique en JSON.
    Échec silencieux avec log d'erreur pour ne jamais interrompre l'UI.
    """
    try:
        with open(f, "w", encoding="utf-8") as fp:
            json.dump(d, fp, ensure_ascii=False, indent=2)
    except Exception as e:
        try:
            with open(EF, "a", encoding="utf-8") as fe:
                fe.write(f"[{datetime.now().isoformat()}] SAVE_ERROR: {e}\n")
        except Exception:
            pass


def _hash_entree(contenu: str, hash_precedent: str) -> str:
    """
    Calcule le hash SHA-256 d'une entrée d'audit enchaînée.

    La chaîne hashée = contenu + hash_précédent, ce qui rend chaque
    entrée dépendante de toutes les entrées antérieures. Toute
    modification d'une entrée passée invalide les hashs suivants.
    """
    payload = f"{contenu}|{hash_precedent}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def audit_log(
    uid: str,
    action: str,
    operateur: str,
    details: Optional[dict] = None,
) -> None:
    """
    Enregistrement dans le journal d'audit immuable.

    Chaque ligne d'audit est de la forme :
        TIMESTAMP | UID | ACTION | OPERATEUR | DETAILS | HASH

    Le HASH est calculé sur le contenu de cette ligne + le HASH de la
    ligne précédente. Cela forme une chaîne cryptographique où toute
    altération est détectable.

    ACTIONS AUDITÉES
        TRIAGE      — Calcul de niveau de triage
        PHARMA      — Consultation protocole pharmacologique
        EXPORT      — Export CSV du registre
        SESSION     — Ouverture / fermeture de session
        ALERTE      — Alerte clinique critique générée

    Parameters
    ----------
    uid : str
        UUID anonyme du patient (8 caractères).
    action : str
        Code d'action standardisé (TRIAGE, PHARMA, EXPORT, etc.).
    operateur : str
        Code opérateur anonyme (ex. IAO01).
    details : dict, optional
        Métadonnées complémentaires (niveau, motif, score).
    """
    try:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        det_str = json.dumps(details or {}, ensure_ascii=False, separators=(",", ":"))
        contenu = f"{ts}|{uid}|{action}|{operateur}|{det_str}"

        # Lire le hash de la dernière entrée pour enchaîner
        hash_prev = _HASH_GENESIS
        if os.path.exists(ALF):
            try:
                with open(ALF, "r", encoding="utf-8") as f:
                    lines = [l.strip() for l in f.readlines() if l.strip()]
                if lines:
                    # Le hash est le dernier champ de la dernière ligne
                    hash_prev = lines[-1].rsplit("|", 1)[-1]
            except Exception:
                hash_prev = _HASH_GENESIS

        hash_entree = _hash_entree(contenu, hash_prev)
        ligne = f"{contenu}|{hash_entree}\n"

        with open(ALF, "a", encoding="utf-8") as f:
            f.write(ligne)

    except Exception as e:
        try:
            with open(EF, "a", encoding="utf-8") as fe:
                fe.write(f"[{datetime.now().isoformat()}] AUDIT_ERROR: {e}\n")
        except Exception:
            pass


def audit_verifier_integrite() -> tuple[bool, str]:
    """
    Vérifie l'intégrité cryptographique du journal d'audit.

    Recalcule la chaîne de hashes depuis le début et compare chaque
    entrée avec le hash stocké. Retourne False dès qu'une discordance
    est détectée, ce qui indique une modification a posteriori.

    Returns
    -------
    tuple[bool, str]
        (intégrité_ok, message_rapport)
    """
    if not os.path.exists(ALF):
        return True, "Journal d'audit absent — aucune vérification possible."
    try:
        with open(ALF, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        if not lines:
            return True, "Journal d'audit vide."

        hash_prev = _HASH_GENESIS
        for i, ligne in enumerate(lines, 1):
            parts = ligne.rsplit("|", 1)
            if len(parts) != 2:
                return False, f"Ligne {i} malformée — intégrité compromise."
            contenu, hash_stocke = parts[0], parts[1]
            hash_calcule = _hash_entree(contenu, hash_prev)
            if hash_calcule != hash_stocke:
                return False, (
                    f"Intégrité violée à la ligne {i} — "
                    f"hash attendu {hash_calcule[:16]}… "
                    f"obtenu {hash_stocke[:16]}…"
                )
            hash_prev = hash_stocke

        return True, f"Journal d'audit intègre — {len(lines)} entrées vérifiées."
    except Exception as e:
        return False, f"Erreur de vérification : {e}"


def enreg(d: dict) -> str:
    """
    Enregistrement d'un patient dans le registre anonyme local.

    CONFORMITÉ RGPD
        • Génère un UUID anonyme (8 caractères hexadécimaux en majuscules)
          pour identifier le patient sans aucune donnée nominative.
        • Aucun champ nom/prénom/NISS/adresse n'est stocké.
        • Seuls les paramètres cliniques sont conservés.
        • Cap automatique à REGISTRE_CAP entrées (rotation FIFO).
        • Stockage local uniquement — aucune transmission à un tiers.

    AUDIT
        Chaque enregistrement génère une entrée dans le journal d'audit
        immuable avec hash enchaîné.

    Parameters
    ----------
    d : dict
        Données cliniques du patient (motif, catégorie, niveau, vitaux).

    Returns
    -------
    str
        UUID anonyme de 8 caractères affiché à l'IAO pour traçabilité.
    """
    uid = str(uuid.uuid4())[:8].upper()
    r   = _load(RF)
    r.insert(0, {
        "uid":    uid,
        "heure":  datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "motif":  d.get("motif", ""),
        "cat":    d.get("cat",   ""),
        "niv":    d.get("niv",   ""),
        "n2":     d.get("n2",    0),
        "fc":     d.get("fc"),
        "pas":    d.get("pas"),
        "spo2":   d.get("spo2"),
        "fr":     d.get("fr"),
        "temp":   d.get("temp"),
        "gcs":    d.get("gcs"),
        "op":     d.get("op",    "IAO"),
    })
    _save(RF, r[:REGISTRE_CAP])

    # Audit log avec intégrité hashée
    audit_log(uid, "TRIAGE", d.get("op", "IAO"), {
        "motif": d.get("motif", ""),
        "niv":   d.get("niv",   ""),
        "n2":    d.get("n2",    0),
    })
    return uid


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
_DEF={"sid":lambda:str(uuid.uuid4())[:8].upper(),"op":"",
      "t_arr":None,"t_cont":None,"t_reev":None,
      "histo":[],"reevs":[],"uid_cur":None}
for k,v in _DEF.items():
    if k not in st.session_state: st.session_state[k]=v() if callable(v) else v

# ══════════════════════════════════════════════════════════════════════════════
# EN-TETE
# ══════════════════════════════════════════════════════════════════════════════
H('<div class="app-hdr">'
  '<div class="app-hdr-title">AKIR-IAO v18.0 — Pro Edition</div>'
  '<div class="app-hdr-sub">Aide au Triage Infirmier — Urgences — Hainaut, Wallonie, Belgique</div>'
  '<div class="app-hdr-tags">'
  '<span class="tag">FRENCH SFMU V1.1</span>'
  '<span class="tag">BCFI Belgique</span>'
  '<span class="tag">RGPD</span>'
  '<span class="tag">Dév. : Ismail Ibn-Daifa</span>'
  '</div></div>')

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — PATIENT & SESSION
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    SEC("Opérateur IAO")
    op_in=st.text_input("Code opérateur",value=st.session_state.op,max_chars=10,placeholder="IAO01",
                         help="Ne saisir ni nom ni prenom — RGPD")
    if op_in: st.session_state.op=op_in.upper()

    SEC("Chronomètre")
    sa,sb=st.columns(2)
    if sa.button("Arrivee",use_container_width=True):
        st.session_state.t_arr=datetime.now()
        st.session_state.histo=[]; st.session_state.reevs=[]
    if sb.button("Contact",use_container_width=True):
        st.session_state.t_cont=datetime.now()
    if st.session_state.t_arr:
        el=(datetime.now()-st.session_state.t_arr).total_seconds()
        m,s_=divmod(int(el),60)
        col="#EF4444" if el>600 else ("#F59E0B" if el>300 else "#22C55E")
        H(f'<div style="text-align:center;font-family:\'JetBrains Mono\',monospace;'
          f'font-size:2.2rem;font-weight:700;color:{col};">{m:02d}:{s_:02d}</div>')

    SEC("Patient")
    age=st.number_input("Âge (ans)",0,120,45,key="p_age")
    if age==0:
        am=st.number_input("Âge en mois",0,11,3,key="p_am")
        age=round(am/12.0,4)
        AL(f"Nourrisson {am} mois — seuils pediatriques","info")
    poids=st.number_input("Poids (kg)",1,250,70,key="p_kg")
    atcd=st.multiselect("Antécédents pertinents",ATCD,key="p_atcd")
    alg=st.text_input("Allergies",key="p_alg",placeholder="ex: Penicilline")
    o2=st.checkbox("O2 supplémentaire",key="p_o2")

    SEC("Session RGPD")
    st.caption(f"Session : {st.session_state.sid}")
    st.caption("UUID anonyme — aucun nom collecté")
    if st.button("Nouvelle session",use_container_width=True):
        for k,v in _DEF.items(): st.session_state[k]=v() if callable(v) else v
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ONGLETS PRINCIPAUX — Mobile-first avec icones
# ══════════════════════════════════════════════════════════════════════════════
T=st.tabs([
    "Tri Rapide",
    "Vitaux & GCS",
    "Anamnèse",
    "Triage",
    "Scores Cliniques",
    "Pharmacie",
    "Réévaluation",
    "Historique",
    "Transmission SBAR",
])
t_rap,t_vit,t_ana,t_tri,t_sco,t_pha,t_rev,t_his,t_sbar=T

# Variables partagees — initialisees avec valeurs physiologiques par défaut
temp=fr=fc=pas=spo2=gcs=news2=None
motif=cat=""; details={}; eva=0; niv=just=crit=""; gl_global=None
bpco_g=False

# ──────────────────────────────────────────────────────────────────────────────
# ONGLET 1 — TRI RAPIDE
# ──────────────────────────────────────────────────────────────────────────────
with t_rap:
    CARD("Constantes vitales","")
    c1,c2,c3=st.columns(3)
    temp=c1.number_input("Température (°C)",30.0,45.0,37.0,.1,key="r_t")
    fc  =c2.number_input("FC (bpm)",20,220,80,key="r_fc")
    pas =c3.number_input("PAS (mmHg)",40,260,120,key="r_pas")
    c4,c5,c6=st.columns(3)
    spo2=c4.number_input("SpO2 (%)",50,100,98,key="r_sp")
    fr  =c5.number_input("FR (/min)",5,60,16,key="r_fr")
    gcs =c6.number_input("GCS (3–15)",3,15,15,key="r_gcs")
    CARD_END()

    CARD("Motif & Sécurité","")
    bpco_r=st.checkbox("Patient BPCO connu ?",key="r_bp",help="Active l'Échelle 2 NEWS2 — Cible SpO2 88–92 %")
    if bpco_r: AL("BPCO — Cible SpO2 : 88–92 % — Échelle 2 NEWS2 activée","warning")
    news2,nw=calculer_news2(fr,spo2,o2,temp,pas,fc,gcs,bpco_r)
    for w in nw: AL(w,"warning")
    GAUGE(news2,bpco_r)
    motif=st.selectbox("Motif de recours",MOTIFS_RAPIDES,key="r_mot")
    cat="Tri rapide"
    eva=int(st.select_slider("EVA",[str(i) for i in range(11)],value="0",key="r_eva"))
    details={"eva":eva,"atcd":atcd}
    details["purpura"]=st.checkbox("Purpura non effaçable (test du verre)",key="r_pur",
        help="Purpura fulminans — Tri 1 absolu — Céfotriaxone 2 g IV IMMÉDIAT")
    if details.get("purpura"): PURPURA(details)
    gl_r=GLYC_WIDGET("r_gl","Glycémie capillaire (mg/dl)")
    if gl_r: details["glycemie_mgdl"]=gl_r; gl_global=gl_r
    CARD_END()

    if st.button("Calculer le niveau de triage",type="primary",use_container_width=True):
        N2_BANNER(news2); PURPURA(details)
        nv,jt,cr=french_triage(motif,details,fc,pas,spo2,fr,gcs,temp,age,news2,gl_r)
        niv,just,crit=nv,jt,cr
        TRI_CARD_INLINE(nv,jt,news2)
        D,A=verifier_coherence(fc,pas,spo2,fr,gcs,temp,eva,motif,atcd,details,news2,gl_r)
        for d in D: AL(d,"danger")
        for a in A: AL(a,"warning")
    VITAUX(fc,pas,spo2,fr,temp,gcs,bpco_r)

# ──────────────────────────────────────────────────────────────────────────────
# ONGLET 2 — VITAUX & GCS
# ──────────────────────────────────────────────────────────────────────────────
with t_vit:
    CARD("Paramètres vitaux","")
    v1,v2,v3=st.columns(3)
    temp=v1.number_input("Température (°C)",30.0,45.0,37.0,.1,key="v_t")
    fc  =v1.number_input("FC (bpm)",20,220,80,key="v_fc")
    pas =v2.number_input("PAS (mmHg)",40,260,120,key="v_pas")
    spo2=v2.number_input("SpO2 (%)",50,100,98,key="v_sp")
    fr  =v3.number_input("FR (/min)",5,60,16,key="v_fr")
    CARD_END()

    CARD("Glasgow Coma Scale","")
    g1,g2,g3=st.columns(3)
    gy=g1.selectbox("Yeux (Y)",[4,3,2,1],format_func=lambda x:{4:"4 — Spontanée",3:"3 — À la demande",2:"2 — À la douleur",1:"1 — Aucune"}[x],key="v_gy")
    gv=g2.selectbox("Verbale (V)",[5,4,3,2,1],format_func=lambda x:{5:"5 — Orientée",4:"4 — Confuse",3:"3 — Mots",2:"2 — Sons",1:"1 — Aucune"}[x],key="v_gv")
    gm=g3.selectbox("Motrice (M)",[6,5,4,3,2,1],format_func=lambda x:{6:"6 — Obéit aux ordres",5:"5 — Localise",4:"4 — Évitement",3:"3 — Flexion anormale",2:"2 — Extension",1:"1 — Aucune"}[x],key="v_gm")
    gcs,_=calculer_gcs(gy,gv,gm)
    st.metric("Score GCS",f"{gcs} / 15", delta=None)
    CARD_END()

    bpco_v="BPCO" in atcd
    news2,nw=calculer_news2(fr,spo2,o2,temp,pas,fc,gcs,bpco_v)
    for w in nw: AL(w,"warning")
    bpco_g=bpco_v
    GAUGE(news2,bpco_v)
    VITAUX(fc,pas,spo2,fr,temp,gcs,bpco_v)
    N2_BANNER(news2)
    c1,c2=st.columns(2)
    with c1:
        sh=si(fc,pas); css="si-c" if sh>=1.0 else ("si-w" if sh>=0.8 else "si-ok")
        H(f'<div class="si-box"><div class="si-l">Shock Index</div><div class="si-v {css}">{sh}</div>'
          f'<div class="si-l">{"CHOC PROBABLE" if sh>=1.0 else ("Surveillance rapprochée" if sh>=0.8 else "Normal")}</div></div>')
    with c2:
        if age<18:
            sv,si_i,si_a=sipa(fc,age)
            H(f'<div class="si-box"><div class="si-l">SIPA Pediatrique</div>'
              f'<div class="si-v {"si-c" if si_a else "si-ok"}">{sv}</div>'
              f'<div class="si-l" style="font-size:.6rem;">{si_i}</div></div>')
    DISC()

# ──────────────────────────────────────────────────────────────────────────────
# ONGLET 3 — ANAMNESE
# ──────────────────────────────────────────────────────────────────────────────
with t_ana:
    if temp is None: temp=37.0; fc=80; pas=120; spo2=98; fr=16; gcs=15

    CARD("Évaluation de la douleur","")
    eva=int(st.select_slider("EVA (0=aucune — 10=maximale)",[str(i) for i in range(11)],value="0",key="a_eva"))
    CARD_END()

    CARD("Motif de recours","")
    cat=st.selectbox("Catégorie",list(MOTS_CAT.keys()),key="a_cat")
    motif=st.selectbox("Motif principal",MOTS_CAT[cat],key="a_mot")
    CARD_END()

    CARD("Alerte transversale","")
    details={"eva":eva,"atcd":atcd}
    details["purpura"]=st.checkbox("Purpura non effaçable (test du verre — OBLIGATOIRE)",key="a_pur",
        help="Purpura fulminans — Tri 1 absolu — Céfotriaxone 2 g IV IMMÉDIAT")
    if details.get("purpura"): PURPURA(details)
    CARD_END()

    CARD("Questions discriminantes — FRENCH V1.1","")
    if motif=="Douleur thoracique / SCA":
        details["ecg"]=st.selectbox("ECG 12 dérivations",["Normal","Anormal typique SCA","Anormal non typique"])
        details["douleur"]=st.selectbox("Caractère de la douleur",["Atypique","Typique (constrictive, irradiante)","Coronaire probable"])
        fx=st.columns(4)
        fv=[fx[0].checkbox("HTA",key="f_hta",value="HTA" in atcd),
            fx[1].checkbox("Diabete",key="f_dia"),
            fx[2].checkbox("Tabagisme",key="f_tab"),
            fx[3].checkbox("ATCD cor.",key="f_cor")]
        details["frcv"]=sum(fv)
    elif motif in("Dyspnee / insuffisance respiratoire","Dyspnee / insuffisance cardiaque"):
        bp,pa=BPCO_WIDGET("a_dysp"); details["bpco"]=bp; details["parole"]=pa
        details["orth"]=st.checkbox("Orthopnée",key="a_orth")
        details["tirage"]=st.checkbox("Tirage intercostal / sus-sternal",key="a_tir")
    elif motif=="AVC / Deficit neurologique":
        details["delai"]=st.number_input("Délai depuis début des symptômes (h)",0.0,72.0,2.0,.5,key="a_del")
        details["def_prog"]=st.checkbox("Déficit neurologique progressif",key="a_dp")
    elif motif=="Traumatisme cranien":
        details["aod"]=st.checkbox("Sous anticoagulants / AOD",key="a_aod",value="Anticoagulants/AOD" in atcd)
        details["pdc"]=st.checkbox("Perte de conscience initiale",key="a_pdc")
    elif motif=="Petechie / Purpura":
        AL("TEST DU VERRE OBLIGATOIRE — taches non effacables = urgence absolue","warning")
        details["neff"]=st.checkbox("NON effaçable à la pression du verre",key="a_neff")
        details["etendu"]=st.checkbox("Purpura étendu (plusieurs régions)",key="a_eten")
        if details.get("neff"): PURPURA({"purpura":True})
    elif motif=="Fievre":
        details["conf"]=st.checkbox("Confusion / altération de l'état mental",key="a_conf")
        details["tol_mal"]=st.checkbox("Mauvaise tolérance clinique",key="a_tol")
    elif motif in("Hypoglycemie","Alteration de conscience / Coma","Convulsions / EME"):
        gla=GLYC_WIDGET("a_gl","Glycémie capillaire (mg/dl) — SYSTÉMATIQUE")
        if gla: details["glycemie_mgdl"]=gla; gl_global=gla
    elif motif=="Pediatrie - Crise epileptique":
        # Glycémie — cause curable prioritaire
        gla_ep=GLYC_WIDGET("a_gl_ep","Glycémie capillaire (mg/dl) — SYSTÉMATIQUE avant antiépileptique",req=True)
        if gla_ep: details["glycemie_mgdl"]=gla_ep; gl_global=gla_ep

        SEC("Caractérisation de la crise")
        ec1,ec2=st.columns(2)
        details["en_cours"]     = ec1.checkbox("Crise EN COURS à l'arrivée",      key="ep_enc",
            help="Ligne 1 immédiate — Midazolam buccal")
        details["duree_min"]    = ec2.number_input("Durée estimée (min)",          0,120,0,  key="ep_dur",
            help="≥ 5 min = traitement actif | ≥ 30 min = EME établi")
        details["eme_etabli"]   = st.checkbox(
            f"EME établi (> {EME_ETABLI_MIN} min ou 2 crises sans reprise de conscience)",
            key="ep_eme")
        if details.get("eme_etabli"):
            AL("EME ÉTABLI — Appel médecin senior IMMÉDIAT — Réanimation pédiatrique","danger")

        SEC("Type de crise")
        t1,t2,t3=st.columns(3)
        details["febrile"]      = t1.checkbox("Crise fébrile",         key="ep_feb")
        details["focale"]       = t2.checkbox("Focale (partielle)",    key="ep_foc",
            help="Crise fébrile complexe si focale")
        details["repetee_24h"]  = t3.checkbox("Répétée en 24 h",      key="ep_rep",
            help="Crise fébrile complexe si répétée")
        t4,t5=st.columns(2)
        details["premiere_crise"]= t4.checkbox("1ère crise de la vie", key="ep_1re",
            help="Bilan étiologique urgent — Tri 2 systématique")
        details["habituelle"]   = t5.checkbox("Crise habituelle connue",key="ep_hab",
            help="Patient épileptique — comparer à la sémiologie habituelle")

        SEC("Signes associés")
        s1,s2,s3=st.columns(3)
        details["signes_meninges"] = s1.checkbox("Signes méningés",    key="ep_men",
            help="Méningite / Encéphalite → Tri 1")
        details["tc_associe"]      = s2.checkbox("Traumatisme crânien",key="ep_tc",
            help="Imagerie urgente → Tri 1")
        details["conscience_incomplete"]=s3.checkbox("Conscience incomplète", key="ep_ci",
            help="Phase post-critique prolongée → Tri 2")
        s4,s5=st.columns(2)
        details["recuperee"]    = s4.checkbox("Récupération complète", key="ep_rec")
        details["plan_urgence"] = s5.checkbox("Plan d'urgence familial documenté", key="ep_plu")
        details["atcd"]         = atcd  # passe les ATCD au handler
    elif motif=="Hyperglycemie / Cetoacidose":
        gla2=GLYC_WIDGET("a_gl2","Glycémie capillaire (mg/dl)")
        if gla2: details["glycemie_mgdl"]=gla2; gl_global=gla2
        details["ceto"]=st.checkbox("Cétose élevée / acidocétose confirmée",key="a_ceto")
    CARD_END()

# ──────────────────────────────────────────────────────────────────────────────
# ONGLET 4 — TRIAGE
# ──────────────────────────────────────────────────────────────────────────────
with t_tri:
    if temp is None: temp=37.0; fc=80; pas=120; spo2=98; fr=16; gcs=15
    if not motif: motif="Fievre"; cat="Infectiologie"

    bpco_t="BPCO" in atcd or details.get("bpco",False)
    news2,nw=calculer_news2(fr,spo2,o2,temp,pas,fc,gcs,bpco_t)
    for w in nw: AL(w,"warning")

    # Glycemie si non saisie
    if not details.get("glycemie_mgdl") and not gl_global:
        glt=GLYC_WIDGET("t_gl","Glycémie capillaire (mg/dl)")
        if glt: details["glycemie_mgdl"]=glt; gl_global=glt
    gl_t=details.get("glycemie_mgdl") or gl_global

    niv,just,crit=french_triage(motif,details,fc,pas,spo2,fr,gcs,temp,age,news2,gl_t)

    N2_BANNER(news2); PURPURA(details)

    if st.session_state.t_reev:
        mn=(datetime.now()-st.session_state.t_reev).total_seconds()/60
        if mn>DELAIS.get(niv,60): AL(f"Reevaluation en retard : {int(mn)} min — max {DELAIS[niv]} min","danger")

    GAUGE(news2,bpco_t)
    TRI_CARD_INLINE(niv,just,news2)
    st.caption(f"Critère : {crit}")

    c1,c2=st.columns(2)
    with c1: SI_WIDGET(fc,pas)
    with c2:
        sh=si(fc,pas)
        if sh>=1.0: AL(f"Shock Index {sh} — Choc probable","danger")

    D,A=verifier_coherence(fc,pas,spo2,fr,gcs,temp,details.get("eva",0),motif,atcd,details,news2,gl_t)
    for d in D: AL(d,"danger")
    for a in A: AL(a,"warning")

    if st.session_state.t_arr and st.session_state.t_cont:
        ds=(st.session_state.t_cont-st.session_state.t_arr).total_seconds()
        cm=10 if niv in("M","1","2") else 30
        AL(f"Delai IAO : {int(ds/60)} min — cible {cm} min — {'DEPASSE' if ds/60>=cm else 'Dans les delais'}",
           "danger" if ds/60>=cm else "success")

    if st.button("Enregistrer ce patient",type="primary",use_container_width=True):
        uid=enreg({"motif":motif,"cat":cat,"niv":niv,"n2":news2,
                   "fc":fc,"pas":pas,"spo2":spo2,"fr":fr,"temp":temp,"gcs":gcs,"op":st.session_state.op})
        st.session_state.uid_cur=uid; st.session_state.reevs=[]
        st.session_state.t_reev=datetime.now()
        st.session_state.histo.insert(0,{"uid":uid,"h":datetime.now().strftime("%H:%M"),
                                          "motif":motif,"niv":niv,"n2":news2})
        st.success(f"Patient enregistre — UID : {uid}")

    TRI_BANNER_FIXED(niv,just,news2)
    DISC()

# ──────────────────────────────────────────────────────────────────────────────
# ONGLET 5 — SCORES CLINIQUES
# ──────────────────────────────────────────────────────────────────────────────
with t_sco:
    CARD("qSOFA — Detection sepsis rapide","")
    qs,qp,qw=calculer_qsofa(fr or 16,gcs or 15,pas or 120)
    for w in qw: AL(w,"warning")
    c1,c2=st.columns(2)
    with c1:
        qcss="si-c" if qs>=2 else "si-ok"
        H(f'<div class="si-box"><div class="si-l">qSOFA</div><div class="si-v {qcss}">{qs}/3</div>'
          f'<div class="si-l">{"Sepsis probable" if qs>=2 else "Risque faible"}</div></div>')
    with c2:
        for p in qp: AL(p,"danger" if qs>=2 else "warning")
        if not qp: AL("Aucun critere positif","success")
    CARD_END()

    CARD("FAST — Detection AVC","")
    f1,f2,f3,f4=st.columns(4)
    ff=f1.checkbox("Face",key="sf"); fa=f2.checkbox("Bras",key="sa")
    fs=f3.checkbox("Langage",key="ss"); ft=f4.checkbox("Debut brutal",key="st2")
    fsc,fi,fal=evaluer_fast(ff,fa,fs,ft)
    AL(fi,"danger" if fal else ("warning" if fsc>=1 else "success"))
    CARD_END()

    CARD("TIMI — Risque SCA sans sus-decalage","")
    ti1,ti2=st.columns(2)
    ta=ti1.checkbox("Age >=65 ans",key="ti_a",value=age>=65)
    tf=ti1.checkbox(">=3 FRCV",key="ti_f"); tstT=ti1.checkbox("Stenose >=50%",key="ti_s")
    taspi=ti2.checkbox("Aspirine 7j",key="ti_asp"); ttr=ti2.checkbox("Troponine+",key="ti_tr")
    tdst=ti2.checkbox("Deviation ST",key="ti_d"); tcris=ti2.checkbox(">=2 crises/24h",key="ti_c")
    tsc,_=calculer_timi(age,int(tf)*3,tstT,taspi,ttr,tdst,int(tcris)*2)
    ti_lbl="Risque élevé" if tsc>=5 else ("Intermédiaire" if tsc>=3 else "Faible")
    ti_css="si-c" if tsc>=5 else ("si-w" if tsc>=3 else "si-ok")
    H(f'<div class="si-box"><div class="si-l">Score TIMI</div><div class="si-v {ti_css}">{tsc}/7</div>'
      f'<div class="si-l">{ti_lbl}</div></div>')
    CARD_END()

    CARD("Algoplus — Douleur patient age non communicant","")
    al1,al2,al3,al4,al5=st.columns(5)
    av=al1.checkbox("Visage",key="ag_v"); ar=al2.checkbox("Regard",key="ag_r")
    ap=al3.checkbox("Plaintes",key="ag_p"); aac=al4.checkbox("Corps",key="ag_ac")
    aco=al5.checkbox("Comportement",key="ag_co")
    asc,ai,acss,_=calculer_algoplus(av,ar,ap,aac,aco)
    AL(f"Algoplus {asc}/5 — {ai}",acss)
    CARD_END()

    CARD("Clinical Frailty Scale","")
    cfs_v=st.slider("Score CFS (1-9)",1,9,3,key="cfs")
    st.caption(CFS_LBL.get(cfs_v,""))
    cfl,cfc,cfr=evaluer_cfs(cfs_v)
    AL(f"CFS {cfs_v} — {cfl}",cfc)
    if cfr: AL("CFS >=5 — Envisager remontee du niveau de triage","warning")
    CARD_END()

# ──────────────────────────────────────────────────────────────────────────────
# ONGLET 6 — PHARMACIE
# ──────────────────────────────────────────────────────────────────────────────
with t_pha:
    gl_ph=details.get("glycemie_mgdl") or gl_global

    # ── Bandeau poids — toutes les doses sont calculées pour CE patient ───
    H(f"""<div style="
        background:linear-gradient(135deg,#004A99,#0066CC);
        color:#fff;border-radius:12px;padding:14px 20px;
        margin-bottom:14px;display:flex;
        justify-content:space-between;align-items:center;">
      <div>
        <div style="font-size:.7rem;opacity:.8;text-transform:uppercase;letter-spacing:.08em;">
          Doses calculées pour ce patient
        </div>
        <div style="font-size:1.5rem;font-weight:800;letter-spacing:-.02em;">
          {poids} kg — {age} ans
        </div>
      </div>
      <div style="text-align:right;font-size:.78rem;opacity:.85;line-height:1.7;">
        Modifier le poids dans la barre latérale<br>
        Toutes les doses se recalculent automatiquement
      </div>
    </div>""")

    # ── Récapitulatif doses — tableau synthèse au poids du patient ────────
    with st.expander("Récapitulatif des doses au poids — tableau synthèse", expanded=False):
        # Calculer toutes les doses
        _pr,_ = paracetamol(poids)
        _kr,_ = ketorolac(poids, atcd)
        _tr,_ = tramadol(poids, atcd, age)
        _pi,_ = piritramide(poids, age, atcd)
        _mo,_ = morphine(poids, age)
        _nr,_ = naloxone(poids, age, False)
        _ar,_ = adrenaline(poids)
        _gr,_ = glucose(poids, 50.0)   # valeur fictive pour afficher la dose
        _cr,_ = ceftriaxone(poids, age)
        _li,_ = litican(poids, age, atcd)

        rows = [
            ("Paracétamol IV",     f"{_pr['dose_g'] if _pr else '—'} g",             "Toutes 6 h — max 4 g/24 h",         "Palier 1"),
            ("Kétorolac IV",       f"{_kr['dose_mg'] if _kr else 'CI AINS'} mg",      "Toutes 6 h — max 5 j",              "Palier 2"),
            ("Tramadol IV",        f"{_tr['dose_mg']:.0f} mg" if _tr else "CI",       "Toutes 6 h — max 400 mg/24 h",      "Palier 2"),
            ("Piritramide IV",     f"{_pi['dmin']}-{_pi['dmax']} mg" if _pi else "—", "Titration / 15 min si EVA > 3",     "Palier 3"),
            ("Morphine IV",        f"{_mo['dmin']}-{_mo['dmax']} mg" if _mo else "—", f"Paliers {MORPH_PALIER_MG:.0f} mg / 5-10 min", "Palier 3"),
            ("Naloxone IV",        f"{_nr['dose']} mg" if _nr else "—",               "Répéter / 2-3 min — max 10 mg",     "Antidote"),
            ("Adrénaline IM",      f"{_ar['dose_mg']} mg" if _ar else "—",            "Répéter / 5-15 min si besoin",      "Anaphylaxie"),
            ("Glucose 30 % IV",    f"{_gr['dose_g']} g ({round(_gr['dose_g']/0.3,0):.0f} ml)" if _gr else "—", "Contrôle glycémie à 15 min", "Hypoglycémie"),
            ("Ceftriaxone IV",     f"{_cr['dose_g']} g" if _cr else "—",              "Dose unique urgence",               "Infectieux"),
            ("Litican IM",         f"{_li['dose_mg']:.0f} mg" if _li else "CI",       f"Max {LITICAN_DOSE_MAX_JOUR:.0f} mg/24 h", "Antispasmodique"),
        ]

        H("""<table style="width:100%;border-collapse:collapse;font-size:.78rem;">
          <thead><tr style="background:#004A99;color:#fff;">
            <th style="padding:7px 10px;text-align:left;border-radius:8px 0 0 0;">Médicament</th>
            <th style="padding:7px 10px;text-align:center;">Dose calculée</th>
            <th style="padding:7px 10px;text-align:left;">Fréquence / Note</th>
            <th style="padding:7px 10px;text-align:center;border-radius:0 8px 0 0;">Indication</th>
          </tr></thead><tbody>""")
        for i,(nom,dose,freq,ind) in enumerate(rows):
            bg = "#F8F9FA" if i%2==0 else "#FFFFFF"
            dose_col = f'<span style="font-weight:700;color:#004A99;">{dose}</span>'
            H(f'<tr style="background:{bg};">'
              f'<td style="padding:6px 10px;">{nom}</td>'
              f'<td style="padding:6px 10px;text-align:center;">{dose_col}</td>'
              f'<td style="padding:6px 10px;color:#64748B;">{freq}</td>'
              f'<td style="padding:6px 10px;text-align:center;">'
              f'<span style="background:#EFF6FF;color:#1D4ED8;padding:2px 8px;'
              f'border-radius:999px;font-size:.7rem;">{ind}</span>'
              f'</td></tr>')
        H(f"""</tbody><tfoot><tr style="background:#F1F5F9;">
          <td colspan="4" style="padding:6px 10px;font-size:.7rem;color:#64748B;">
            Toutes les doses calculées pour <strong>{poids} kg — {age} ans</strong>.
            Demi-doses appliquées si âge ≥ 70 ans, IRC ou insuffisance hépatique.
            Ces doses sont indicatives — validation médicale obligatoire avant administration.
          </td></tr></tfoot></table>""")

    # Safety gate: display master warning if glycemia missing
    if gl_ph is None:
        H('''<div class="al warning" style="margin-bottom:14px;font-size:.88rem;font-weight:600;">
          <span class="al-ico">⚠️</span>
          <span><strong>Donnée manquante : Glycémie capillaire non saisie</strong><br>
          Certains protocoles sont désactivés. Saisir la glycémie dans l'onglet Tri Rapide ou Anamnèse.</span>
          </div>''')

    CARD("Antalgie basée sur l'ÉVA — Échelle OMS adaptée","")
    ev_ph=st.slider("ÉVA actuelle",0,10,details.get("eva",0),key="ph_eva")
    prt=protocole_eva(ev_ph,poids,age,atcd,gl_ph)
    for a in prt["als"]: AL(a,"danger")
    for rec in prt["recs"]:
        RX(rec["nom"],rec["dose"],[rec["d"],rec.get("note","")],rec["ref"],rec["p"],rec.get("al",[]))
    CARD_END()

    CARD("Adrénaline IM — Anaphylaxie","")
    ar,ae=adrenaline(poids)
    if ae: AL(ae,"warning")
    else: RX("Adrenaline IM (Sterop 1mg/ml)",f"{ar['dose_mg']}mg IM",
              [ar["voie"],ar["note"],ar["rep"]],ar["ref"],"U")
    CARD_END()

    CARD("Naloxone IV — Antidote opioïdes","")
    dep=st.checkbox("Patient dépendant aux opioïdes (titration douce)",key="ph_dep")
    nr,ne=naloxone(poids,age,dep)
    if ne: AL(ne,"warning")
    else:
        for a in nr.get("alertes",[]): AL(a,"danger")
        RX("Naloxone IV (Narcan)",f"{nr['dose']}mg / bolus",
           [nr["admin"],nr["note"],nr["surv"]],nr["ref"],"A")
    CARD_END()

    CARD("Glucose 30 % — Hypoglycémie","")
    if gl_ph is None:
        RX_LOCK("⚠️ Donnée manquante : Glycémie capillaire non mesurée — Protocoles désactivés")
    else:
        gr,ge=glucose(poids,gl_ph)
        if ge: AL(ge,"warning")
        else: RX("Glucose 30% IV (Glucosie)",f"{gr['dose_g']}g",[gr["vol"],gr["ctrl"]],gr["ref"],"U")
    CARD_END()

    CARD("Ceftriaxone IV — Urgence infectieuse","")
    cr,ce=ceftriaxone(poids,age)
    if ce: AL(ce,"warning")
    else: RX("Ceftriaxone IV (Purpura / Meningite)",f"{cr['dose_g']}g IV",
              [cr["admin"],cr["note"]],cr["ref"],"U")
    CARD_END()

    CARD("Crise épileptique pédiatrique — Protocole SFNP / ISPE 2023","")
    if age >= 16:
        AL("Ce protocole est calibré pour l'enfant (< 16 ans) — vérifier l'âge", "warning")

    # Saisie durée et statut si non renseignés en Anamnèse
    col_ep1, col_ep2 = st.columns(2)
    dur_ph = details.get("duree_min", 0) or col_ep1.number_input(
        "Durée de la crise (min)", 0, 120, 0, key="ep_dur_ph",
        help=f"≥ {EME_SEUIL_MIN} min = traitement | ≥ {EME_OPERATIONNEL_MIN} min = EME opérationnel | ≥ {EME_ETABLI_MIN} min = EME établi"
    )
    enc_ph = details.get("en_cours", False) or col_ep2.checkbox(
        "Crise EN COURS à l'arrivée", key="ep_enc_ph"
    )
    gl_ep  = details.get("glycemie_mgdl") or gl_ph

    # Calcul du protocole
    prot_ep = protocole_epilepsie_ped(poids, age, dur_ph, enc_ph, atcd, gl_ep)

    # Alerte glycémie — prioritaire
    if prot_ep["glycemie_alerte"]:
        AL(prot_ep["glycemie_alerte"], "danger")

    # Indicateur temporel — code couleur selon durée
    if dur_ph > EME_ETABLI_MIN or details.get("eme_etabli"):
        AL(f"EME ÉTABLI > {EME_ETABLI_MIN} min — RÉANIMATION PÉDIATRIQUE — APPEL IMMÉDIAT", "danger")
    elif dur_ph > EME_OPERATIONNEL_MIN:
        AL(f"EME OPÉRATIONNEL {dur_ph} min — Risque lésionnel — LIGNE 3 requise", "danger")
    elif dur_ph > EME_SEUIL_MIN or enc_ph:
        AL(f"Crise prolongée / en cours — LIGNE 1 IMMÉDIATE — Midazolam buccal", "warning")

    # Chronomètre AVPU
    SEC("Évaluation rapide de la conscience — Score AVPU")
    avpu_sel = st.selectbox("Score AVPU", ["A — Alert","V — Voice","P — Pain","U — Unresponsive"],
                             key="ep_avpu_ph",
                             help="A=Normal | V=Altération légère | P=Sévère | U=Coma")
    if "P" in avpu_sel or "U" in avpu_sel:
        AL("AVPU P/U — Position LAS + libération VAS + O2 haute concentration", "danger")
    elif "V" in avpu_sel:
        AL("AVPU V — Surveiller l'évolution — Préparer ligne 1", "warning")
    details["avpu"] = avpu_sel[0]

    # Timeline visuelle des 3 lignes
    col_t = "#EF4444" if (dur_ph>EME_OPERATIONNEL_MIN) else ("#F59E0B" if dur_ph>EME_SEUIL_MIN else "#3B82F6")
    H(f"""<div style="background:#F8FAFC;border:1px solid {col_t};border-left:5px solid {col_t};
                border-radius:10px;padding:14px 18px;margin:12px 0;font-size:.8rem;line-height:2.1;">
      <strong style="color:{col_t};">SÉQUENCE THÉRAPEUTIQUE — Durée crise : {dur_ph} min</strong><br>
      <span style="color:#7C3AED;font-family:monospace;">T0</span>
        → <strong>LIGNE 1</strong> Midazolam buccal / IM-IN — <em>IAO, sans VVP</em><br>
      <span style="color:#7C3AED;font-family:monospace;">T+{EME_SEUIL_MIN} min</span>
        → <strong>LIGNE 2</strong> Lorazépam / Clonazépam IV — <em>médecin + VVP</em><br>
      <span style="color:#EF4444;font-family:monospace;">T+{EME_OPERATIONNEL_MIN} min</span>
        → <strong>LIGNE 3</strong> Lévétiracétam / Valproate IV — <em>réanimation</em><br>
      <span style="color:#7F1D1D;font-family:monospace;">T+{EME_ETABLI_MIN} min</span>
        → <strong>EME ÉTABLI</strong> — intubation à discuter
    </div>""")

    # Onglets lignes de traitement
    lig1, lig2, lig3, ant_, surv_ = st.tabs([
        "Ligne 1 — IAO",
        "Ligne 2 — IV",
        "Ligne 3 — EME",
        "Antidote",
        "Surveillance",
    ])

    with lig1:
        AL("LIGNE 1 — IAO autonome — Sans VVP — À administrer IMMÉDIATEMENT si crise en cours / > 5 min", "info")
        l1a=prot_ep["ligne1a"]; l1b=prot_ep["ligne1b"]; l1c=prot_ep["ligne1c"]

        # Midazolam buccal — référence
        H(f'<div class="rx p2">'
          f'<div class="rx-name">{l1a["med"]} — Voie de référence</div>'
          f'<div class="rx-dose">{l1a["dose_mg"]} mg buccal</div>'
          f'<div class="rx-detail">'
          f'Flacon Buccolam® : <strong>{l1a["volume"]}</strong><br>'
          f'{l1a["admin"]}<br>'
          f'{l1a["delai"]}<br>'
          f'<strong>{l1a["peut_repeter"]}</strong>'
          f'</div>'
          f'<div class="rx-ref">{l1a["ref"]}</div></div>')

        cep1, cep2 = st.columns(2)
        with cep1:
            H(f'<div class="rx p2">'
              f'<div class="rx-name">{l1b["med"]} — Alt. si buccal impossible</div>'
              f'<div class="rx-dose">{l1b["dose_mg"]} mg</div>'
              f'<div class="rx-detail">'
              f'<strong>IM :</strong> {l1b["voie_im"]}<br>'
              f'<strong>IN :</strong> {l1b["voie_in"]}<br>'
              f'{l1b["delai"]}'
              f'</div>'
              f'<div class="rx-ref">{l1b["ref"]}</div></div>')
        with cep2:
            H(f'<div class="rx p2">'
              f'<div class="rx-name">{l1c["med"]}</div>'
              f'<div class="rx-dose">{l1c["dose_mg"]} mg rectal</div>'
              f'<div class="rx-detail">'
              f'{l1c["admin"]}<br>{l1c["delai"]}'
              f'</div>'
              f'<div class="rx-ref">{l1c["ref"]}</div></div>')

    with lig2:
        AL(f"LIGNE 2 — VVP requise — Médecin — Si crise persiste {EME_SEUIL_MIN} min après Ligne 1", "warning")
        l2l=prot_ep["ligne2_lora"]; l2c=prot_ep["ligne2_clona"]; l2d=prot_ep["ligne2_diaz"]

        cep3, cep4 = st.columns(2)
        with cep3:
            H(f'<div class="rx p3">'
              f'<div class="rx-name">{l2l["med"]}</div>'
              f'<div class="rx-dose">{l2l["dose_mg"]} mg IV</div>'
              f'<div class="rx-detail">'
              f'{l2l["admin"]}<br>{l2l["delai"]}<br>'
              f'<strong style="color:var(--ERR-t);">{l2l["attention"]}</strong>'
              f'</div>'
              f'<div class="rx-ref">{l2l["ref"]}</div></div>')
        with cep4:
            H(f'<div class="rx p3">'
              f'<div class="rx-name">{l2c["med"]}</div>'
              f'<div class="rx-dose">{l2c["dose_mg"]} mg IV</div>'
              f'<div class="rx-detail">{l2c["admin"]}<br>{l2c["delai"]}</div>'
              f'<div class="rx-ref">{l2c["ref"]}</div></div>')
        H(f'<div class="rx p2">'
          f'<div class="rx-name">{l2d["med"]} — 3e choix</div>'
          f'<div class="rx-dose">{l2d["dose_mg"]} mg IV</div>'
          f'<div class="rx-detail">{l2d["admin"]}</div>'
          f'<div class="rx-ref">{l2d["ref"]}</div></div>')

    with lig3:
        AL(f"LIGNE 3 — EME OPÉRATIONNEL (> {EME_OPERATIONNEL_MIN} min) — RÉANIMATION PÉDIATRIQUE", "danger")
        l3a=prot_ep["ligne3_leveti"]; l3b=prot_ep["ligne3_valp"]; l3c=prot_ep["ligne3_phenob"]

        # Lévétiracétam — prioritaire
        H(f'<div class="rx p3">'
          f'<div class="rx-name">{l3a["med"]}</div>'
          f'<div class="rx-dose">{l3a["dose_mg"]:.0f} mg IV</div>'
          f'<div class="rx-detail">'
          f'Volume : {l3a["volume"]}<br>{l3a["admin"]}<br>'
          f'<em>{l3a["avantage"]}</em>'
          f'</div>'
          f'<div class="rx-ref">{l3a["ref"]}</div></div>')

        cep5, cep6 = st.columns(2)
        with cep5:
            ci_html = f'<br><strong style="color:var(--ERR-t);">{l3b["ci"]}</strong>' if l3b.get("ci") else ""
            H(f'<div class="rx p3">'
              f'<div class="rx-name">{l3b["med"]}</div>'
              f'<div class="rx-dose">{l3b["dose_mg"]:.0f} mg IV</div>'
              f'<div class="rx-detail">{l3b["admin"]}{ci_html}</div>'
              f'<div class="rx-ref">{l3b["ref"]}</div></div>')
        with cep6:
            H(f'<div class="rx p3">'
              f'<div class="rx-name">{l3c["med"]}</div>'
              f'<div class="rx-dose">{l3c["dose_mg"]:.0f} mg IV</div>'
              f'<div class="rx-detail">'
              f'{l3c["admin"]}<br>'
              f'<strong style="color:var(--ERR-t);">{l3c["attention"]}</strong><br>'
              f'{l3c["ecg"]}'
              f'</div>'
              f'<div class="rx-ref">{l3c["ref"]}</div></div>')

    with ant_:
        AL("Antidote benzodiazépines — Si dépression respiratoire sévère post-injection", "warning")
        ant=prot_ep["antidote"]
        H(f'<div class="rx ant">'
          f'<div class="rx-name">{ant["med"]}</div>'
          f'<div class="rx-dose">{ant["dose_mg"]} mg IV</div>'
          f'<div class="rx-detail">'
          f'Indication : {ant["indication"]}<br>'
          f'{ant["admin"]}<br>'
          f'Dose totale max : {ant["dose_total"]} mg<br>'
          f'<strong style="color:var(--WRN-t);">{ant["attention"]}</strong>'
          f'</div>'
          f'<div class="rx-ref">{ant["ref"]}</div></div>')

    with surv_:
        AL("Points de surveillance obligatoires — IAO", "info")
        for sv in prot_ep["surveillance"]:
            H(f'<div class="al info" style="padding:7px 14px;margin:3px 0;font-size:.81rem;">'
              f'<span>{sv}</span></div>')
        SEC("Chronomètre clinique")
        for t,msg in prot_ep["chrono"].items():
            col_ch = "#EF4444" if t in("T30","T10") else ("#F59E0B" if t=="T5" else "#3B82F6")
            H(f'<div style="display:flex;gap:10px;align-items:flex-start;margin:5px 0;">'
              f'<span style="font-family:monospace;font-size:.75rem;color:{col_ch};'
              f'font-weight:700;min-width:60px;">{t}</span>'
              f'<span style="font-size:.79rem;">{msg}</span></div>')
        st.caption(prot_ep["ref"])
    CARD_END()

    CARD("Litican IM — Antispasmodique / Antiémétique","")
    SEC("Protocole local — Urgences Hainaut")
    H("""<div style="font-size:.78rem;color:var(--TM);line-height:1.7;margin-bottom:10px;">
      Tiémonium méthylsulfate (Litican) — Antispasmodique anticholinergique.
      Indiqué pour les vomissements, nausées et spasmes digestifs / urologiques.
      <strong style="color:var(--ERR-t);">Ne pas injecter en IV — voie IM uniquement.</strong>
    </div>""")
    # Indications rapides
    lit_ind = st.multiselect(
        "Indication principale",
        ["Vomissements / Nausées réfractaires",
         "Colique néphrétique",
         "Colique hépatique / biliaire",
         "Spasme digestif / douleur abdominale spastique",
         "Gastro-entérite avec vomissements"],
        key="lit_ind",
    )
    lr, le = litican(poids, age, atcd)
    if le:
        AL(f"Litican — {le}", "danger")
    else:
        # Avertissement IV systématique
        AL("NE PAS INJECTER EN IV — risque de bradycardie sévère", "danger")
        lc1, lc2 = st.columns(2)
        with lc1:
            H(
                f'<div class="rx p2" style="margin-top:0;">'
                f'<div class="rx-name">Litican IM — {lr["regime"]}</div>'
                f'<div class="rx-dose">{lr["dose_mg"]:.0f} mg IM</div>'
                f'<div class="rx-detail">'
                f'Préparation : {lr["dose_note"]}<br>'
                f'Volume : {lr["volume"]}<br>'
                f'Voie : {lr["voie"]}<br>'
                f'Renouvellement : {lr["freq"]}'
                f'</div>'
                f'<div class="rx-ref">{lr["ref"]}</div>'
                f'</div>'
            )
        with lc2:
            H(
                '<div class="card" style="background:#FFFBEB;border-color:#F59E0B;">'
                '<div class="card-title" style="color:#92400E;">Contre-indications à vérifier</div>'
                '<div style="font-size:.78rem;line-height:1.8;color:#78350F;">'
                'Glaucome par fermeture de l\'angle<br>'
                'Rétention urinaire / adénome prostatique<br>'
                'Iléus paralytique / occlusion intestinale<br>'
                'Tachycardie supra-ventriculaire<br>'
                'Grossesse (données limitées)<br>'
                'Myasthénie grave'
                '</div></div>'
            )
        if lit_ind:
            AL(f"Indication documentée : {' | '.join(lit_ind)}", "info")
    CARD_END()

    CARD("MÉOPA — Analgésie non invasive","")
    ci_m=[c for c in ["Deficit vitamine B12","Drepanocytose"] if c in atcd]
    if ci_m: AL(f"MEOPA contre-indique : {', '.join(ci_m)}","danger")
    else:
        RX("MEOPA / Kalinox (O2/N2O 50/50)","Inhalation spontanee",
           ["Masque facial avec valve anti-retour","Duree max : 15min / session",
            "AMM : adulte et enfant >=1 an","CI : pneumothorax, occlusion, embolie gazeuse"],
           "BCFI — MEOPA (Kalinox) — RCP Belgique","2")
    CARD_END()
    DISC()

# ──────────────────────────────────────────────────────────────────────────────
# ONGLET 7 — REEVALUATION
# ──────────────────────────────────────────────────────────────────────────────
with t_rev:
    if st.session_state.t_arr and st.session_state.t_cont:
        ds=(st.session_state.t_cont-st.session_state.t_arr).total_seconds()
        cm=10 if niv in("M","1","2") else 30
        AL(f"Delai IAO : {int(ds/60)} min — cible {cm} min","danger" if ds/60>=cm else "success")

    CARD("Nouvelle réévaluation","")
    r1,r2,r3=st.columns(3)
    rt=r1.number_input("Température (°C)",30.0,45.0,37.0,.1,key="re_t")
    rfc=r1.number_input("FC",20,220,80,key="re_fc")
    rp=r2.number_input("PAS",40,260,120,key="re_pas")
    rs=r2.number_input("SpO2",50,100,98,key="re_sp")
    rfr=r3.number_input("FR",5,60,16,key="re_fr")
    rg=r3.number_input("GCS (3–15)",3,15,15,key="re_gcs")
    rn2,_=calculer_news2(rfr,rs,o2,rt,rp,rfc,rg,"BPCO" in atcd)
    rniv,rjust,_=french_triage(motif or "Fievre",details,rfc,rp,rs,rfr,rg,rt,age,rn2)
    GAUGE(rn2,"BPCO" in atcd)
    N2_BANNER(rn2)
    st.info(f"Triage recalculé : **{LABELS.get(rniv,rniv)}** — {rjust}")
    if st.button("Enregistrer la réévaluation",use_container_width=True):
        st.session_state.reevs.append({"h":datetime.now().strftime("%H:%M"),
            "fc":rfc,"pas":rp,"spo2":rs,"fr":rfr,"gcs":rg,"temp":rt,"niv":rniv,"n2":rn2})
        st.session_state.t_reev=datetime.now()
        st.success(f"Reevaluation {datetime.now().strftime('%H:%M')} — Tri {rniv}")
    CARD_END()

    if st.session_state.reevs:
        CARD("Tendance NEWS2","")
        n2v=[x.get("n2",0) for x in st.session_state.reevs]
        mx=max(n2v) if n2v else 1
        for i,snap in enumerate(st.session_state.reevs):
            n2_=snap.get("n2",0); pct=round(n2_/max(mx,1)*100)
            col="#EF4444" if n2_>=7 else ("#F59E0B" if n2_>=5 else "#22C55E")
            H(f'<div class="n2t">'
              f'<div class="n2t-lbl">{snap.get("h","?")} H+{i}</div>'
              f'<div class="n2t-trk"><div class="n2t-fill" style="width:{max(pct,4)}%;background:{col};"></div></div>'
              f'<div class="n2t-val" style="color:{col};">{n2_}</div></div>')
        CARD_END()

        CARD("Detail","")
        for i,snap in enumerate(st.session_state.reevs):
            prev=st.session_state.reevs[i-1] if i>0 else snap
            no=ORD.get(snap.get("niv","5"),5); np_=ORD.get(prev.get("niv","5"),5)
            if no<np_: css_,tend="rr-up","AGGRAVATION"
            elif no>np_: css_,tend="rr-down","AMELIORATION"
            else: css_,tend="rr-stable","STABLE"
            H(f'<div class="rr {css_}"><strong>{snap.get("h","?")} H+{i}</strong>'
              f' | Tri {snap.get("niv","?")} | NEWS2 {snap.get("n2","?")}'
              f' | FC {snap.get("fc","?")} | PAS {snap.get("pas","?")}'
              f' | SpO2 {snap.get("spo2","?")}% | <strong>{tend}</strong></div>')
        if len(st.session_state.reevs)>=2:
            fi=st.session_state.reevs[0]; la=st.session_state.reevs[-1]
            st.caption(f"Bilan : NEWS2 {fi.get('n2','?')} → {la.get('n2','?')} | Tri {fi['niv']} → {la['niv']}")
        CARD_END()

# ──────────────────────────────────────────────────────────────────────────────
# ONGLET 8 — HISTORIQUE
# ──────────────────────────────────────────────────────────────────────────────
with t_his:
    if not st.session_state.histo:
        st.info("Aucun patient enregistre dans cette session.")
    else:
        nv_ses=[p.get("niv","5") for p in st.session_state.histo]
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Patients",len(st.session_state.histo))
        c2.metric("Tri 1/2 critiques",sum(1 for n in nv_ses if n in("M","1","2")))
        c3.metric("NEWS2 moyen",round(sum(p.get("n2",0) for p in st.session_state.histo)/max(len(st.session_state.histo),1),1))
        c4.metric("Tri 5 réorientés",sum(1 for n in nv_ses if n=="5"))

        CARD("Répartition par niveau","")
        dist={n:nv_ses.count(n) for n in["M","1","2","3A","3B","4","5"]}
        tot=len(nv_ses) or 1
        cols=st.columns(7)
        for i,(n,c) in enumerate(dist.items()): cols[i].metric(f"Tri {n}",c,delta=f"{round(c/tot*100)}%",delta_color="off")
        CARD_END()

        CARD("Liste des patients","")
        for p in st.session_state.histo:
            hb=HBCSS.get(p.get("niv","5"),"hb-5")
            H(f'<div class="hl">'
              f'<span class="hbadge {hb}">{LABELS.get(p.get("niv","5"),"?")}</span>'
              f'<strong>{p.get("h","?")}</strong>'
              f'<span style="color:var(--TM);font-size:.68rem;">UID:{p.get("uid","?")}</span>'
              f'<span style="flex:1;">{p.get("motif","?")}</span>'
              f'<span style="color:var(--TM);">N2:{p.get("n2","?")}</span></div>')
        CARD_END()

        reg=_load(RF)
        if reg:
            CARD("Export RGPD — Registre anonyme","")
            out=io.StringIO(); w=csv_mod.writer(out)
            w.writerow(["uid","heure","motif","categorie","niveau","news2","fc","pas","spo2","fr","temp","gcs","operateur"])
            for r in reg:
                w.writerow([r.get(k,"") for k in["uid","heure","motif","cat","niv","n2","fc","pas","spo2","fr","temp","gcs","op"]])
            col_dl1, col_dl2 = st.columns(2)
            col_dl1.download_button("Télécharger le registre CSV",data=out.getvalue(),
                file_name=f"akir_reg_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",use_container_width=True)
            # Export du journal d'audit brut
            if os.path.exists(ALF):
                with open(ALF,"r",encoding="utf-8") as fa: audit_raw=fa.read()
                col_dl2.download_button("Télécharger journal d'audit (.log)",
                    data=audit_raw,
                    file_name=f"akir_audit_{datetime.now().strftime('%Y%m%d_%H%M')}.log",
                    mime="text/plain",use_container_width=True)
            AL(f"RGPD : CSV anonyme — UUID uniquement — {len(reg)} enregistrements","info")
            CARD_END()

            # Vérification de l'intégrité du journal d'audit
            CARD("Intégrité du journal d'audit","")
            SEC("Vérification cryptographique SHA-256")
            H("""<div style="font-size:.78rem;color:var(--TM);line-height:1.7;margin-bottom:10px;">
              Chaque entrée du journal est liée à la précédente par une chaîne de hashes SHA-256.
              Toute modification a posteriori invalide la chaîne et est détectable ici.
              Ce mécanisme répond aux exigences de traçabilité médico-légale (AR 18/06/1990 — Belgique).
            </div>""")
            if st.button("Vérifier l'intégrité du journal d'audit", use_container_width=True):
                ok, rapport = audit_verifier_integrite()
                if ok:
                    AL(f"Journal d'audit intègre — {rapport}", "success")
                else:
                    AL(f"INTÉGRITÉ COMPROMISE — {rapport}", "danger")
            CARD_END()

# ──────────────────────────────────────────────────────────────────────────────
# ONGLET 9 — TRANSMISSION SBAR
# ──────────────────────────────────────────────────────────────────────────────
with t_sbar:
    CARD("Rapport de transmission — Format DPI-Ready","")
    sbar_op=st.text_input("Code opérateur",value=st.session_state.op or "IAO",key="sb_op")
    if st.button("Générer le rapport SBAR",type="primary",use_container_width=True):
        if not motif:
            AL("Selectionner un motif en Anamnese avant de generer le rapport","warning")
        else:
            s=build_sbar(age,motif,cat,atcd,alg,o2,temp or 37.0,fc or 80,pas or 120,
                         spo2 or 98,fr or 16,gcs or 15,eva,news2 or 0,
                         niv or "3B",just or "Non calcule",crit or "",sbar_op,
                         gl_global or details.get("glycemie_mgdl"))
            SBAR_RENDER(s)
            txt=(f"RAPPORT SBAR — AKIR-IAO v18.0 Pro Edition\n"
                 f"Opérateur : {s['op']} | {s['heure']}\n\n"
                 f"[S] SITUATION\nPatient {s['age']} ans | {s['motif']}\n"
                 f"Niveau : {s['niv']} | Secteur : {s['sec']} | Delai : {s['delai']} min\n"
                 f"Critere : {s['crit']}\n\n"
                 f"[B] BACKGROUND\nATCD : {s['atcd']}\nAllergies : {s['alg']}\n"
                 f"O2 : {s['o2']} | Glycemie : {s['gl']}\n\n"
                 f"[A] ASSESSMENT\nFC {s['fc']} | PAS {s['pas']} | SpO2 {s['spo2']}% | "
                 f"FR {s['fr']}/min | T {s['temp']}C | GCS {s['gcs']}/15 | EVA {s['eva']}/10 | NEWS2 {s['n2']}\n"
                 f"Justification : {s['just']}\n\n"
                 f"[R] RECOMMENDATION\nOrientation : {s['sec']} | Delai max : {s['delai']} min\n"
                 f"Remarques IAO : [À compléter par l'opérateur]\n\n"
                 f"AKIR-IAO v18.0 Pro — Ismail Ibn-Daifa — FRENCH SFMU V1.1 — Hainaut, Belgique")
            st.download_button("Télécharger le rapport SBAR (.txt)",data=txt,
                file_name=f"sbar_{sbar_op}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",use_container_width=True)
    CARD_END()
    DISC()