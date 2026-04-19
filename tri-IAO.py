"""
================================================================================
  AKIR-IAO v18.0 — Hospital Pro
  Développeur exclusif : Ismail Ibn-Daifa
  Application d'aide au triage infirmier — Urgences du Hainaut, Belgique
  Référence clinique : FRENCH Triage SFMU V1.1 — Juin 2018
  Pharmacologie      : BCFI — Répertoire Commenté des Médicaments — Belgique
  RGPD               : Aucun nom ni prénom collecté — UUID anonyme uniquement
================================================================================
"""

from __future__ import annotations
from typing import Optional
from datetime import datetime
import streamlit as st
import uuid
import json
import os

st.set_page_config(
    page_title="AKIR-IAO v18.0 — Hospital Pro",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# DESIGN SYSTEM — CSS HOSPITAL PRO
# ==============================================================================

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --brand:         #004A99;
    --brand-light:   #1A69B8;
    --brand-pale:    #E8F1FB;
    --brand-dark:    #002F66;
    --slate:         #1A202C;
    --slate-mid:     #2D3748;
    --slate-light:   #4A5568;
    --slate-pale:    #718096;
    --bg:            #F0F4F8;
    --bg-card:       #FFFFFF;
    --bg-input:      #F7FAFC;
    --border:        #E2E8F0;
    --border-focus:  #004A99;
    --text:          #1A202C;
    --text-muted:    #4A5568;
    --text-white:    #FFFFFF;
    /* Urgences */
    --tri-M-bg:      #1A0A2E; --tri-M-fg:  #D946EF; --tri-M-bd: #9333EA;
    --tri-1-bg:      #7F1D1D; --tri-1-fg:  #FCA5A5; --tri-1-bd: #EF4444;
    --tri-2-bg:      #78350F; --tri-2-fg:  #FCD34D; --tri-2-bd: #F59E0B;
    --tri-3A-bg:     #1E3A5F; --tri-3A-fg: #93C5FD; --tri-3A-bd:#3B82F6;
    --tri-3B-bg:     #1E3A5F; --tri-3B-fg: #BAE6FD; --tri-3B-bd:#60A5FA;
    --tri-4-bg:      #14532D; --tri-4-fg:  #86EFAC; --tri-4-bd: #22C55E;
    --tri-5-bg:      #334155; --tri-5-fg:  #CBD5E1; --tri-5-bd: #94A3B8;
    /* Alertes */
    --danger-bg:     #FEF2F2; --danger-bd: #EF4444; --danger-tx: #B91C1C;
    --warn-bg:       #FFFBEB; --warn-bd:   #F59E0B; --warn-tx:   #92400E;
    --success-bg:    #F0FDF4; --success-bd:#22C55E; --success-tx:#166534;
    --info-bg:       #EFF6FF; --info-bd:   #3B82F6; --info-tx:   #1E40AF;
    /* Shadows */
    --shadow-sm:     0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.06);
    --shadow-md:     0 4px 6px rgba(0,0,0,.07), 0 2px 4px rgba(0,0,0,.06);
    --shadow-lg:     0 10px 15px rgba(0,0,0,.1), 0 4px 6px rgba(0,0,0,.05);
    --shadow-brand:  0 4px 14px rgba(0,74,153,.25);
    --radius:        12px;
    --radius-sm:     8px;
}

/* Base */
html, body, [class*="st-"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text);
    background: var(--bg);
    -webkit-font-smoothing: antialiased;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }

/* ======= HEADER ======= */
.hp-header {
    background: linear-gradient(135deg, var(--brand-dark) 0%, var(--brand) 50%, var(--brand-light) 100%);
    border-radius: var(--radius);
    padding: 22px 28px;
    margin-bottom: 24px;
    box-shadow: var(--shadow-brand);
    position: relative;
    overflow: hidden;
}
.hp-header::before {
    content: '';
    position: absolute;
    top: -50%; right: -10%;
    width: 300px; height: 300px;
    background: rgba(255,255,255,.05);
    border-radius: 50%;
}
.hp-header::after {
    content: '';
    position: absolute;
    bottom: -60%; left: 5%;
    width: 200px; height: 200px;
    background: rgba(255,255,255,.04);
    border-radius: 50%;
}
.hp-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.01em;
    margin-bottom: 4px;
}
.hp-subtitle {
    font-size: 0.75rem;
    color: rgba(255,255,255,.75);
    font-weight: 400;
    letter-spacing: 0.02em;
}
.hp-badge {
    display: inline-block;
    background: rgba(255,255,255,.15);
    border: 1px solid rgba(255,255,255,.3);
    color: #FFFFFF;
    font-size: 0.68rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    margin-right: 6px;
    margin-top: 8px;
    backdrop-filter: blur(4px);
}

/* ======= CARDS ======= */
.hp-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: var(--shadow-sm);
    transition: box-shadow .2s ease;
}
.hp-card:hover { box-shadow: var(--shadow-md); }
.hp-card-title {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--brand);
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--brand-pale);
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ======= SECTION LABEL ======= */
.hp-sec {
    font-size: 0.63rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--brand);
    margin: 20px 0 10px 0;
    padding-bottom: 6px;
    border-bottom: 2px solid var(--brand-pale);
}

/* ======= TRIAGE RESULT CARDS ======= */
.tri-result {
    border-radius: var(--radius);
    padding: 24px 28px;
    margin: 16px 0;
    text-align: center;
    box-shadow: var(--shadow-lg);
    position: relative;
    overflow: hidden;
}
.tri-result::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
}
.tri-M  { background: var(--tri-M-bg);  color: var(--tri-M-fg);  border: 1px solid var(--tri-M-bd); }
.tri-M::before  { background: var(--tri-M-bd); }
.tri-1  { background: var(--tri-1-bg);  color: var(--tri-1-fg);  border: 1px solid var(--tri-1-bd); }
.tri-1::before  { background: var(--tri-1-bd); }
.tri-2  { background: var(--tri-2-bg);  color: var(--tri-2-fg);  border: 1px solid var(--tri-2-bd); }
.tri-2::before  { background: var(--tri-2-bd); }
.tri-3A { background: var(--tri-3A-bg); color: var(--tri-3A-fg); border: 1px solid var(--tri-3A-bd); }
.tri-3A::before { background: var(--tri-3A-bd); }
.tri-3B { background: var(--tri-3B-bg); color: var(--tri-3B-fg); border: 1px solid var(--tri-3B-bd); }
.tri-3B::before { background: var(--tri-3B-bd); }
.tri-4  { background: var(--tri-4-bg);  color: var(--tri-4-fg);  border: 1px solid var(--tri-4-bd); }
.tri-4::before  { background: var(--tri-4-bd); }
.tri-5  { background: var(--tri-5-bg);  color: var(--tri-5-fg);  border: 1px solid var(--tri-5-bd); }
.tri-5::before  { background: var(--tri-5-bd); }
.tri-label {
    font-size: 1.6rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin-bottom: 6px;
}
.tri-sector {
    font-size: 0.78rem;
    opacity: .85;
    font-weight: 400;
    margin-top: 6px;
}
.tri-justif {
    font-size: 0.82rem;
    opacity: .9;
    margin-top: 8px;
    font-weight: 500;
}
.tri-badge {
    display: inline-block;
    font-size: 0.68rem;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 20px;
    border: 1px solid currentColor;
    margin-top: 8px;
    opacity: .8;
}

/* ======= NEWS2 GAUGE ======= */
.news2-gauge {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px 22px;
    box-shadow: var(--shadow-sm);
    text-align: center;
}
.news2-score {
    font-family: 'JetBrains Mono', monospace;
    font-size: 3rem;
    font-weight: 700;
    line-height: 1;
    margin: 8px 0 4px;
}
.news2-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.news2-bar-track {
    background: #E2E8F0;
    border-radius: 6px;
    height: 10px;
    overflow: hidden;
    margin: 8px 0;
}
.news2-bar-fill {
    height: 10px;
    border-radius: 6px;
    transition: width .5s ease;
}
.n2-0 { color: #22C55E; }  /* vert */
.n2-1 { color: #84CC16; }
.n2-2 { color: #EAB308; }  /* jaune */
.n2-3 { color: #F97316; }  /* orange */
.n2-4 { color: #EF4444; }  /* rouge */
.n2-5 { color: #7C3AED; }  /* violet critique */

/* ======= VITAL BADGES ======= */
.vit-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin: 12px 0;
}
.vit-item {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 12px 14px;
    text-align: center;
    box-shadow: var(--shadow-sm);
}
.vit-item.warn  { border-color: var(--warn-bd);    background: var(--warn-bg); }
.vit-item.crit  { border-color: var(--danger-bd);  background: var(--danger-bg); }
.vit-label { font-size: 0.62rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: .08em; }
.vit-value { font-family: 'JetBrains Mono', monospace; font-size: 1.3rem; font-weight: 700; margin: 2px 0; }
.vit-unit  { font-size: 0.65rem; color: var(--text-muted); }
.vit-item.warn .vit-value { color: var(--warn-tx); }
.vit-item.crit .vit-value { color: var(--danger-tx); }

/* ======= ALERTES ======= */
.hp-alert {
    border-radius: var(--radius-sm);
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.84rem;
    font-weight: 500;
    display: flex;
    align-items: flex-start;
    gap: 10px;
    line-height: 1.5;
}
.hp-alert-icon { font-size: 1rem; flex-shrink: 0; margin-top: 1px; }
.hp-alert.danger  { background: var(--danger-bg);  border-left: 4px solid var(--danger-bd);  color: var(--danger-tx); }
.hp-alert.warning { background: var(--warn-bg);    border-left: 4px solid var(--warn-bd);    color: var(--warn-tx);   }
.hp-alert.success { background: var(--success-bg); border-left: 4px solid var(--success-bd); color: var(--success-tx);}
.hp-alert.info    { background: var(--info-bg);    border-left: 4px solid var(--info-bd);    color: var(--info-tx);   }

/* ======= PURPURA BANNER ======= */
.purpura-banner {
    background: linear-gradient(135deg, #7F1D1D, #991B1B);
    border: 2px solid #EF4444;
    border-radius: var(--radius);
    padding: 18px 22px;
    margin: 12px 0;
    box-shadow: 0 0 20px rgba(239,68,68,.4);
    animation: pulse-red 2s ease-in-out infinite;
}
.purpura-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #FCA5A5;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.purpura-body {
    font-size: 0.85rem;
    color: #FEE2E2;
    line-height: 1.6;
}
@keyframes pulse-red {
    0%, 100% { box-shadow: 0 0 20px rgba(239,68,68,.4); }
    50%       { box-shadow: 0 0 35px rgba(239,68,68,.7); }
}

/* ======= PHARMA CARDS ======= */
.pharma-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px 22px;
    margin: 10px 0;
    box-shadow: var(--shadow-sm);
    position: relative;
    overflow: hidden;
}
.pharma-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 5px;
    border-radius: var(--radius) 0 0 var(--radius);
}
.pharma-card.palier-1::before { background: #22C55E; }
.pharma-card.palier-2::before { background: #F59E0B; }
.pharma-card.palier-3::before { background: #EF4444; }
.pharma-card.urgence::before  { background: #7C3AED; }
.pharma-card.antidote::before { background: #3B82F6; }
.pharma-name {
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 4px;
}
.pharma-dose {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--brand);
    margin: 6px 0;
}
.pharma-detail {
    font-size: 0.8rem;
    color: var(--text-muted);
    line-height: 1.6;
}
.pharma-ref {
    font-size: 0.68rem;
    color: var(--slate-pale);
    margin-top: 8px;
    font-style: italic;
}
.pharma-locked {
    background: #F8FAFC;
    border: 2px dashed #CBD5E1;
    border-radius: var(--radius);
    padding: 20px;
    text-align: center;
    color: var(--text-muted);
    font-size: 0.84rem;
}

/* ======= SHOCK INDEX ======= */
.si-box {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 14px 18px;
    text-align: center;
}
.si-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
}
.si-normal { color: #22C55E; }
.si-warn   { color: #F59E0B; }
.si-crit   { color: #EF4444; }
.si-label  { font-size: 0.65rem; text-transform: uppercase; letter-spacing: .1em; color: var(--text-muted); }

/* ======= SBAR PRO ======= */
.sbar-report {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow-md);
}
.sbar-header {
    background: linear-gradient(135deg, var(--brand-dark), var(--brand));
    padding: 16px 24px;
    color: white;
}
.sbar-header-title { font-size: 1rem; font-weight: 700; }
.sbar-header-sub   { font-size: 0.72rem; opacity: .8; margin-top: 2px; }
.sbar-section {
    padding: 16px 24px;
    border-bottom: 1px solid var(--border);
}
.sbar-section:last-child { border-bottom: none; }
.sbar-section-letter {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px; height: 28px;
    background: var(--brand);
    color: white;
    font-weight: 800;
    font-size: 0.85rem;
    border-radius: 6px;
    margin-right: 10px;
    flex-shrink: 0;
}
.sbar-section-title {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .1em;
    color: var(--brand);
}
.sbar-section-row {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 10px;
}
.sbar-content {
    font-size: 0.85rem;
    color: var(--text);
    line-height: 1.7;
    margin-top: 8px;
}
.sbar-vital-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin-top: 10px;
}
.sbar-vital-item {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px 10px;
    text-align: center;
}
.sbar-vital-key   { font-size: 0.6rem; color: var(--text-muted); text-transform: uppercase; }
.sbar-vital-val   { font-family: 'JetBrains Mono', monospace; font-size: 1.0rem; font-weight: 700; color: var(--text); }
.sbar-footer {
    background: #F8FAFC;
    padding: 12px 24px;
    font-size: 0.68rem;
    color: var(--text-muted);
    font-style: italic;
    border-top: 1px solid var(--border);
}

/* ======= REEVAL HISTORY ======= */
.reeval-line {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    border-radius: var(--radius-sm);
    margin: 4px 0;
    font-size: 0.82rem;
    border-left: 4px solid transparent;
}
.reeval-up     { background: #FEF2F2; border-color: #EF4444; color: #B91C1C; }
.reeval-down   { background: #F0FDF4; border-color: #22C55E; color: #166534; }
.reeval-stable { background: var(--info-bg); border-color: #3B82F6; color: #1E40AF; }

/* ======= NEWS2 TREND BAR ======= */
.n2-trend-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 4px 0;
}
.n2-trend-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    width: 56px;
    flex-shrink: 0;
    color: var(--text-muted);
}
.n2-trend-track {
    flex: 1;
    background: var(--border);
    border-radius: 4px;
    height: 14px;
    overflow: hidden;
}
.n2-trend-fill { height: 14px; border-radius: 4px; }
.n2-trend-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    width: 20px;
    text-align: right;
}

/* ======= HIST LINES ======= */
.hist-line {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    margin: 5px 0;
    font-size: 0.82rem;
    box-shadow: var(--shadow-sm);
}
.hist-badge {
    display: inline-block;
    font-size: 0.68rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 4px;
    white-space: nowrap;
}
.hb-M   { background: var(--tri-M-bg);  color: var(--tri-M-fg);  }
.hb-1   { background: var(--tri-1-bg);  color: var(--tri-1-fg);  }
.hb-2   { background: var(--tri-2-bg);  color: var(--tri-2-fg);  }
.hb-3A  { background: var(--tri-3A-bg); color: var(--tri-3A-fg); }
.hb-3B  { background: var(--tri-3B-bg); color: var(--tri-3B-fg); }
.hb-4   { background: var(--tri-4-bg);  color: var(--tri-4-fg);  }
.hb-5   { background: var(--tri-5-bg);  color: var(--tri-5-fg);  }

/* ======= DISCLAIMER ======= */
.hp-disclaimer {
    background: #F8FAFC;
    border: 1px solid var(--border);
    border-top: 3px solid var(--brand);
    border-radius: var(--radius-sm);
    padding: 14px 18px;
    margin-top: 28px;
    font-size: 0.68rem;
    color: var(--text-muted);
    line-height: 1.8;
}
.hp-disclaimer-sig {
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--brand);
    border-top: 1px solid var(--border);
    padding-top: 8px;
    margin-top: 8px;
}

/* ======= BUTTONS ======= */
.stButton > button {
    min-height: 46px;
    font-size: 0.9rem;
    font-weight: 600;
    border-radius: var(--radius-sm) !important;
    transition: all .2s ease !important;
}
.stButton > button[kind="primary"] {
    background: var(--brand) !important;
    border-color: var(--brand) !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--brand-dark) !important;
    box-shadow: var(--shadow-brand) !important;
}

/* ======= INPUTS ======= */
.stNumberInput input, .stTextInput input, .stSelectbox select {
    border-radius: var(--radius-sm) !important;
    border-color: var(--border) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.95rem !important;
}
.stNumberInput input:focus, .stTextInput input:focus {
    border-color: var(--brand) !important;
    box-shadow: 0 0 0 3px rgba(0,74,153,.15) !important;
}

/* ======= TABS ======= */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: var(--bg);
    padding: 4px;
    border-radius: 10px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.82rem;
    padding: 8px 14px;
    color: var(--text-muted);
    transition: all .2s;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: var(--brand) !important;
    color: white !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 16px;
}

/* ======= SIDEBAR ======= */
.css-1d391kg, [data-testid="stSidebar"] {
    background: var(--slate) !important;
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox,
[data-testid="stSidebar"] p {
    color: #E2E8F0 !important;
}
[data-testid="stSidebar"] .hp-sec {
    color: #93C5FD !important;
    border-color: rgba(147,197,253,.3) !important;
}

/* ======= METRICS ======= */
[data-testid="metric-container"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 12px 16px;
    box-shadow: var(--shadow-sm);
}

/* ======= MOBILE ======= */
@media (max-width: 768px) {
    .tri-label     { font-size: 1.3rem; }
    .news2-score   { font-size: 2.2rem; }
    .vit-grid      { grid-template-columns: repeat(2, 1fr); }
    .sbar-vital-grid { grid-template-columns: repeat(2, 1fr); }
    .stButton > button { min-height: 52px !important; font-size: 1rem !important; }
    .hp-header     { padding: 16px 18px; }
    .hp-title      { font-size: 1.05rem; }
}
/* iPhone PWA */
@media (display-mode: standalone) {
    .block-container { padding-top: 2rem !important; }
}
</style>
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="AKIR-IAO">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<link rel="apple-touch-icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='22' fill='%23004A99'/%3E%3Ctext y='.9em' font-size='72' x='12'%3E%2B%3C/text%3E%3C/svg%3E">
"""

st.markdown(CSS, unsafe_allow_html=True)

# ==============================================================================
# [1] CONSTANTES CLINIQUES
# ==============================================================================

LABELS_TRI = {
    "M":  "TRI M — IMMEDIAT",
    "1":  "TRI 1 — URGENCE EXTREME",
    "2":  "TRI 2 — TRES URGENT",
    "3A": "TRI 3A — URGENT",
    "3B": "TRI 3B — URGENT DIFFERE",
    "4":  "TRI 4 — MOINS URGENT",
    "5":  "TRI 5 — NON URGENT",
}
SECTEURS_TRI = {
    "M":  "Dechocage — Prise en charge immediate",
    "1":  "Dechocage — Prise en charge immediate",
    "2":  "Soins aigus — Medecin en moins de 20 min",
    "3A": "Soins aigus — Medecin en moins de 30 min",
    "3B": "Polyclinique — Medecin en moins de 1 h",
    "4":  "Consultation — Medecin en moins de 2 h",
    "5":  "Salle d'attente — Reorientation MG possible",
}
DELAIS_TRI = {"M":5,"1":5,"2":15,"3A":30,"3B":60,"4":120,"5":999}
CSS_TRI    = {"M":"tri-M","1":"tri-1","2":"tri-2","3A":"tri-3A","3B":"tri-3B","4":"tri-4","5":"tri-5"}
HB_CSS     = {"M":"hb-M","1":"hb-1","2":"hb-2","3A":"hb-3A","3B":"hb-3B","4":"hb-4","5":"hb-5"}
ORD_NIV    = {"M":0,"1":1,"2":2,"3A":3,"3B":4,"4":5,"5":6}

GLYCEMIE = {
    "hypoglycemie_severe":  54,
    "hypoglycemie_moderee": 70,
    "hyperglycemie_seuil":  180,
    "hyperglycemie_severe": 360,
}
SEUILS_PEDIATRIQUES = {
    "0_1m":  (100,180,60),
    "1_6m":  (100,160,70),
    "6_24m": (80, 150,75),
    "1_10a": (70, 140,70),
}
LISTE_ATCD = [
    "HTA","Diabete de type 1","Diabete de type 2","Tabagisme actif",
    "Dyslipidaemie","ATCD familial coronarien","Insuffisance cardiaque chronique",
    "BPCO","Anticoagulants / AOD","Grossesse en cours","Immunodepression",
    "Neoplasie evolutive","Epilepsie","Insuffisance renale chronique",
    "Ulcere gastro-duodenal","Insuffisance hepatique","Deficit en vitamine B12",
    "Drepanocytose / hemoglobinopathie","Chimiotherapie en cours",
    "IMAO (inhibiteurs MAO)","Antidepresseurs serotoninergiques (ISRS / IRSNA)",
]
CFS_NIVEAUX = {
    1:"Tres en forme",2:"En forme",3:"Bien portant",4:"Vulnerable",
    5:"Fragilite legere",6:"Fragilite moderee",7:"Fragilite severe",
    8:"Fragilite tres severe",9:"Maladie terminale",
}

# ==============================================================================
# [2] MOTEUR CLINIQUE
# ==============================================================================

def calculer_news2(fr,spo2,o2_supp,temp,pas,fc,gcs,bpco=False):
    warns=[]
    s=0
    if   fr<=8:  s+=3;warns.append(f"FR {fr}/min <=8")
    elif fr<=11: s+=1
    elif fr<=20: s+=0
    elif fr<=24: s+=2
    else:        s+=3;warns.append(f"FR {fr}/min >=25")
    if bpco:
        if   spo2<=83: s+=3;warns.append(f"SpO2 {spo2}% critique (BPCO)")
        elif spo2<=85: s+=2
        elif spo2<=87: s+=1
        elif spo2<=92: s+=0
        elif spo2<=94: s+=0
        elif spo2<=96: s+=1
        else:          s+=2;warns.append(f"SpO2 {spo2}% hyperoxie en contexte BPCO")
    else:
        if   spo2<=91: s+=3;warns.append(f"SpO2 {spo2}% <=91% — hypoxemie severe")
        elif spo2<=93: s+=2
        elif spo2<=95: s+=1
        else:          s+=0
    if o2_supp: s+=2;warns.append("O2 supplementaire — +2 pts NEWS2")
    if   temp<=35.0: s+=3;warns.append(f"T {temp}C — hypothermie")
    elif temp<=36.0: s+=1
    elif temp<=38.0: s+=0
    elif temp<=39.0: s+=1
    else:            s+=2;warns.append(f"T {temp}C — hyperthermie")
    if   pas<=90:  s+=3;warns.append(f"PAS {pas}mmHg — etat de choc")
    elif pas<=100: s+=2
    elif pas<=110: s+=1
    elif pas<=219: s+=0
    else:          s+=3;warns.append(f"PAS {pas}mmHg — HTA hypertensive")
    if   fc<=40:  s+=3;warns.append(f"FC {fc}bpm — bradycardie severe")
    elif fc<=50:  s+=1
    elif fc<=90:  s+=0
    elif fc<=110: s+=1
    elif fc<=130: s+=2
    else:         s+=3;warns.append(f"FC {fc}bpm — tachycardie severe")
    if   gcs==15: s+=0
    elif gcs>=13: s+=3;warns.append(f"GCS {gcs}/15")
    else:         s+=3;warns.append(f"GCS {gcs}/15 — alteration majeure")
    return s, warns

def news2_meta(score):
    if   score==0: return "Risque nul",    "n2-0", "#22C55E", 0
    elif score<=4: return "Risque faible", "n2-1", "#84CC16", int(score/12*100)
    elif score<=6: return "Risque modere", "n2-2", "#EAB308", int(score/12*100)
    elif score<=8: return "Risque eleve",  "n2-3", "#F97316", int(score/12*100)
    else:          return "CRITIQUE",      "n2-5", "#7C3AED", min(int(score/12*100),100)

def calculer_gcs(y,v,m):
    try:    return max(3,min(15,int(y)+int(v)+int(m))),[]
    except: return 15,["Erreur GCS"]

def calculer_qsofa(fr,gcs,pas):
    pos=[]; w=[]; s=0
    if fr  is None: w.append("FR manquante")
    elif fr>=22: s+=1; pos.append(f"FR {fr}/min >=22")
    if gcs is None: w.append("GCS manquant")
    elif gcs<15:  s+=1; pos.append(f"GCS {gcs}/15")
    if pas is None: w.append("PAS manquante")
    elif pas<=100: s+=1; pos.append(f"PAS {pas}mmHg <=100")
    return s,pos,w

def calculer_timi(age,nb_frcv,stenose_50,aspirine_7j,troponine_pos,deviation_st,crises_24h):
    try:
        s = (
            int(age>=65)
            + int(nb_frcv>=3)
            + int(bool(stenose_50))
            + int(bool(aspirine_7j))
            + int(bool(troponine_pos))
            + int(bool(deviation_st))
            + int(crises_24h>=2)
        )
        return s,[]
    except (TypeError,ValueError) as e:
        return 0,[str(e)]

def evaluer_fast(face,bras,lang,debut):
    s=int(bool(face))+int(bool(bras))+int(bool(lang))+int(bool(debut))
    if s>=2: return s,"FAST positif — AVC suspect — Filiere Stroke",True
    if s==1: return s,"FAST partiel — Evaluation neurologique urgente",False
    return s,"FAST negatif",False

def calculer_algoplus(visage,regard,plaintes,attitude_corpo,comportement):
    try:
        s = (
            int(bool(visage))
            + int(bool(regard))
            + int(bool(plaintes))
            + int(bool(attitude_corpo))
            + int(bool(comportement))
        )
        if   s>=4: interp,css="Douleur intense — IV urgent","danger"
        elif s>=2: interp,css="Douleur probable — traitement","warning"
        else:      interp,css="Douleur absente ou faible","success"
        return s,interp,css,[]
    except (TypeError,ValueError) as e:
        return 0,"Erreur","info",[str(e)]

def evaluer_cfs(score):
    if score<=3: return "Robuste","success",False
    if score<=4: return "Vulnerable","warning",False
    if score<=6: return "Fragile","warning",True
    if score<=8: return "Tres fragile","danger",True
    return "Terminal","danger",True

def calculer_shock_index(fc,pas):
    return round(fc/pas,2) if pas and pas>0 else 0.0

def calculer_sipa(fc,age_annees):
    sipa=round(fc/max(1.0,float(age_annees+1)*15+70),2)
    seuil=2.2 if age_annees<=1 else (2.0 if age_annees<=4 else (1.8 if age_annees<=7 else 1.7))
    if sipa>seuil:
        return sipa,f"SIPA {sipa} > {seuil} — Choc pediatrique probable — Tri 1",True
    return sipa,f"SIPA {sipa} <= {seuil} — Hemodynamique preservee",False

def mgdl_vers_mmol(v): return round(v/18.016,1)
def mmol_vers_mgdl(v): return round(v*18.016,0)

def seuils_pediatriques(age_annees):
    if age_annees<1/12:   return SEUILS_PEDIATRIQUES["0_1m"]
    elif age_annees<0.5:  return SEUILS_PEDIATRIQUES["1_6m"]
    elif age_annees<=2:   return SEUILS_PEDIATRIQUES["6_24m"]
    elif age_annees<=10:
        fc_min,fc_max=SEUILS_PEDIATRIQUES["1_10a"][:2]
        return fc_min,fc_max,int(70+age_annees*2)
    return 60,120,80

def french_triage(motif,details,fc,pas,spo2,fr,gcs,temp,age,news2,glycemie_mgdl=None):
    fc=fc or 80; pas=pas or 120; spo2=spo2 or 98
    fr=fr or 16; gcs=gcs or 15; temp=temp or 37.0; news2=news2 or 0
    if details is None: details={}
    try:
        if news2>=9: return "M",f"NEWS2 {news2} >=9 — engagement vital","NEWS2 Tri M"
        if details.get("purpura"):
            return "1","PURPURA FULMINANS — Ceftriaxone 2g IV IMMEDIAT","SPILF/SFP 2017"
        if motif=="Arret cardio-respiratoire":
            return "1","ACR confirme","FRENCH Tri 1"
        if motif=="Hypotension arterielle":
            if pas<=70: return "1",f"PAS {pas}<=70","FRENCH Tri 1"
            if pas<=90 or (pas<=100 and fc>100): return "2",f"PAS {pas} — choc debutant","FRENCH Tri 2"
            if pas<=100: return "3B",f"PAS {pas} — valeur limite","FRENCH Tri 3B"
            return "4","PAS normale","FRENCH Tri 4"
        if motif=="Douleur thoracique / SCA":
            ecg=details.get("ecg","Normal"); doul=details.get("douleur_type","Atypique")
            if ecg=="Anormal typique SCA" or doul=="Typique persistante/intense":
                return "1","SCA avec ECG anormal ou douleur typique","FRENCH Tri 1"
            if fc>=120 or spo2<94: return "2","Douleur thoracique instable","FRENCH Tri 2"
            if doul=="Type coronaire" or details.get("frcv_count",0)>=2:
                return "2","Douleur coronaire probable","FRENCH Tri 2"
            if ecg=="Anormal non typique": return "2","ECG non typique","FRENCH Tri 2"
            return "3A","Douleur atypique stable","FRENCH Tri 3A"
        if motif in ("Tachycardie / tachyarythmie","Bradycardie / bradyarythmie","Palpitations"):
            if fc>=180 or fc<=30: return "1",f"FC {fc}bpm extreme","FRENCH Tri 1"
            if fc>=150 or fc<=40: return "2",f"FC {fc}bpm severe","FRENCH Tri 2"
            if details.get("mauvaise_tolerance"): return "2","Arythmie mal toleree","FRENCH Tri 2"
            return "3B",f"FC {fc}bpm toleree","FRENCH Tri 3B"
        if motif=="Hypertension arterielle":
            if pas>=220: return "2",f"PAS {pas}>=220 — urgence hypertensive","FRENCH Tri 2"
            if details.get("sf_associes") or (pas>=180 and fc>100):
                return "2","HTA avec signes fonctionnels","FRENCH Tri 2"
            if pas>=180: return "3B",f"PAS {pas} severe sans SF","FRENCH Tri 3B"
            return "4",f"PAS {pas} moderee","FRENCH Tri 4"
        if motif=="Allergie / anaphylaxie":
            if spo2<94 or pas<90 or gcs<15: return "1","Anaphylaxie severe","FRENCH Tri 1"
            if details.get("dyspnee") or details.get("urticaire"): return "2","Allergie systemique","FRENCH Tri 2"
            return "3B","Reaction allergique localisee","FRENCH Tri 3B"
        if motif=="AVC / Deficit neurologique":
            delai=details.get("delai_heures",99)
            if delai<=4.5: return "1",f"AVC {delai}h <=4h30 — filiere Stroke","FRENCH Tri 1"
            if details.get("deficit_progressif") or gcs<15:
                return "2","Deficit progressif ou GCS altere","FRENCH Tri 2"
            return "2","Deficit neurologique — bilan urgent","FRENCH Tri 2"
        if motif=="Traumatisme cranien":
            if gcs<=8: return "1",f"TC grave GCS {gcs}","FRENCH Tri 1"
            if gcs<=12 or details.get("aod_avk"):
                return "2",f"TC GCS {gcs} ou anticoagulant","FRENCH Tri 2"
            if details.get("perte_conscience"): return "3A","TC avec PDC","FRENCH Tri 3A"
            return "4","TC benin","FRENCH Tri 4"
        if motif=="Alteration de conscience / Coma":
            gl=glycemie_mgdl or details.get("glycemie_mgdl",0)
            if gl and gl<GLYCEMIE["hypoglycemie_severe"]:
                return "2",f"Hypoglycemie {gl}mg/dl — Glucose 30% IV","FRENCH Tri 2"
            if gcs<=8: return "1",f"Coma GCS {gcs}","FRENCH Tri 1"
            if gcs<=13: return "2",f"Alteration GCS {gcs}","FRENCH Tri 2"
            return "2","Alteration legere — evaluation urgente","FRENCH Tri 2"
        if motif=="Etat de mal epileptique / Convulsions":
            if details.get("crises_multiples"): return "2","Crises multiples ou EME","FRENCH Tri 2"
            if details.get("confusion"): return "2","Confusion post-critique","FRENCH Tri 2"
            return "3B","Convulsion recuperee","FRENCH Tri 3B"
        if motif=="Cephalee":
            if details.get("brutal"): return "1","Cephalee foudroyante — HSA","FRENCH Tri 1"
            if details.get("raideur_nuque") or details.get("fievre_cephalee"):
                return "2","Cephalee avec signes meninges","FRENCH Tri 2"
            return "3B","Cephalee sans signe de gravite","FRENCH Tri 3B"
        if motif=="Malaise":
            gl=glycemie_mgdl or details.get("glycemie_mgdl",0)
            if gl and gl<GLYCEMIE["hypoglycemie_severe"]:
                return "2",f"Malaise hypoglycemique {gl}mg/dl","FRENCH Tri 2"
            if news2>=2 or details.get("anomalie_vitaux"): return "2","Malaise avec anomalie vitale","FRENCH Tri 2"
            return "3B","Malaise recupere","FRENCH Tri 3B"
        if motif in ("Dyspnee / insuffisance respiratoire","Dyspnee / insuffisance cardiaque"):
            bpco_dysp="BPCO" in details.get("atcd",[]) or details.get("bpco_dyspnee",False)
            cible=92 if bpco_dysp else 95
            if spo2<(88 if bpco_dysp else 91) or fr>=40:
                return "1",f"Detresse respiratoire SpO2 {spo2}% FR {fr}/min","FRENCH Tri 1"
            if spo2<cible or fr>=30 or not details.get("parole_ok",True):
                return "2",f"Dyspnee severe SpO2 {spo2}%","FRENCH Tri 2"
            if details.get("orthopnee") or details.get("tirage"):
                return "2","Dyspnee avec orthopnee ou tirage","FRENCH Tri 2"
            return "3B",f"Dyspnee moderee SpO2 {spo2}%","FRENCH Tri 3B"
        if motif=="Douleur abdominale":
            si=calculer_shock_index(fc,pas)
            if pas<90 or si>=1.0: return "2",f"Douleur abdominale avec choc SI {si}","FRENCH Tri 2"
            if details.get("grossesse") or details.get("geu"): return "2","Abdomen sur grossesse — GEU","FRENCH Tri 2"
            if details.get("defense"): return "2","Abdomen chirurgical","FRENCH Tri 2"
            if details.get("mauvaise_tolerance"): return "3A","Douleur mal toleree","FRENCH Tri 3A"
            return "3B","Douleur toleree","FRENCH Tri 3B"
        if motif=="Fievre":
            si=calculer_shock_index(fc,pas)
            if details.get("purpura"): return "1","Fievre + purpura — Ceftriaxone 2g IV","FRENCH Tri 1"
            if temp>=40 or temp<=35.2 or details.get("confusion"):
                return "2",f"Fievre severe T {temp}C","FRENCH Tri 2"
            if details.get("mauvaise_tolerance") or pas<100 or si>=1.0:
                return "3B",f"Fievre mal toleree SI {si}","FRENCH Tri 3B"
            return "5","Fievre bien toleree","FRENCH Tri 5"
        if motif=="Pediatrie - Fievre <= 3 mois":
            return "2","Fievre nourrisson <=3 mois — systematique","FRENCH Pediatrie Tri 2"
        if motif=="Petechie / Purpura":
            if details.get("non_effacable"):
                return "1","Purpura non effacable — Ceftriaxone 2g IV","SPILF/SFP 2017"
            if temp>=38.0 or details.get("mauvaise_tolerance"):
                return "2","Purpura febrile — suspicion fulminans","FRENCH Tri 2"
            return "3B","Petechies — bilan hemostase","FRENCH Tri 3B"
        if motif in ("Traumatisme du thorax / abdomen / rachis cervical","Traumatisme du bassin / hanche / femur"):
            if details.get("penetrant") or details.get("cinetique")=="Haute":
                return "1","Traumatisme penetrant haute cinetique","FRENCH Tri 1"
            si=calculer_shock_index(fc,pas)
            if si>=1.0 or spo2<94: return "2",f"Traumatisme avec choc SI {si}","FRENCH Tri 2"
            return "2","Traumatisme axial — evaluation urgente","FRENCH Tri 2"
        if motif=="Traumatisme d'un membre / epaule":
            if details.get("ischemie"): return "1","Ischemie distale","FRENCH Tri 1"
            if details.get("impotence_totale") and details.get("deformation"):
                return "2","Fracture deplacee","FRENCH Tri 2"
            if details.get("impotence_totale"): return "3A","Impotence totale","FRENCH Tri 3A"
            if details.get("deformation"): return "3A","Deformation visible","FRENCH Tri 3A"
            return "4","Traumatisme distal modere","FRENCH Tri 4"
        if motif=="Hypoglycemie":
            gl=glycemie_mgdl or details.get("glycemie_mgdl",0)
            if gl and gl<GLYCEMIE["hypoglycemie_severe"]:
                return "2",f"Hypoglycemie severe {gl}mg/dl","FRENCH Tri 2"
            if gcs<15: return "2",f"Hypoglycemie avec GCS {gcs}","FRENCH Tri 2"
            if gl and gl<GLYCEMIE["hypoglycemie_moderee"]:
                return "3A",f"Hypoglycemie moderee {gl}mg/dl","FRENCH Tri 3A"
            return "3B","Hypoglycemie legere","FRENCH Tri 3B"
        if motif=="Hyperglycemie / Cetoacidose diabetique":
            gl=glycemie_mgdl or details.get("glycemie_mgdl",0)
            if details.get("cetose") or gcs<15: return "2","Cetoacidose ou GCS altere","FRENCH Tri 2"
            if gl and gl>=GLYCEMIE["hyperglycemie_severe"]: return "3B",f"Hyperglycemie severe {gl}mg/dl","FRENCH Tri 3B"
            return "4","Hyperglycemie toleree","FRENCH Tri 4"
        if motif in ("Renouvellement ordonnance","Examen administratif"):
            return "5","Consultation non urgente","FRENCH Tri 5"
        if news2>=7: return "2",f"NEWS2 {news2}>=7","NEWS2 Tri 2"
        if news2>=5: return "3A",f"NEWS2 {news2}>=5","NEWS2 Tri 3A"
        return "3B",f"Motif '{motif}' — evaluation standard","FRENCH Tri 3B"
    except Exception as e:
        return "2",f"Erreur moteur triage : {e}","Securite Tri 2"

def verifier_coherence(fc,pas,spo2,fr,gcs,temp,eva,motif,atcd,details,news2,glycemie_mgdl=None):
    danger=[]; attention=[]; infos=[]
    sous_ac="Anticoagulants / AOD" in atcd
    if "IMAO (inhibiteurs MAO)" in atcd:
        danger.append("IMAO DETECTES — Tramadol CONTRE-INDIQUE (syndrome serotoninergique fatal)")
    if "Antidepresseurs serotoninergiques (ISRS / IRSNA)" in atcd:
        attention.append("ISRS/IRSNA — Tramadol deconseille. Preferer Dipidolor ou Morphine")
    gl=glycemie_mgdl or (details.get("glycemie_mgdl") if details else None)
    if gl:
        if gl<GLYCEMIE["hypoglycemie_severe"]:
            danger.append(f"HYPOGLYCEMIE SEVERE {gl}mg/dl ({mgdl_vers_mmol(gl)}mmol/l) — Glucose 30% IV immediat")
        elif gl<GLYCEMIE["hypoglycemie_moderee"]:
            attention.append(f"Hypoglycemie moderee {gl}mg/dl — corriger avant antalgique")
    si=calculer_shock_index(fc,pas)
    if si>=1.0: danger.append(f"Shock Index {si} >=1.0 — etat de choc probable")
    if spo2<90: danger.append(f"SpO2 {spo2}% — hypoxemie severe — O2 urgent")
    if fr>=30:  attention.append(f"FR {fr}/min — tachypnee significative")
    if fc>=150 or fc<=40: danger.append(f"FC {fc}bpm — arythmie critique")
    if sous_ac and "Traumatisme cranien" in motif:
        danger.append("TC sous AOD/AVK — TDM cerebral urgent — risque hematome differe")
    return danger,attention,infos

def generer_sbar(age,motif,cat,atcd,allergies,o2_supp,temp,fc,pas,spo2,fr,gcs,eva,news2,
                 niveau,justif,critere,code_operateur="IAO",glycemie_mgdl=None):
    heure=datetime.now().strftime("%d/%m/%Y %H:%M")
    atcd_str=", ".join(atcd) if atcd else "Aucun antecedent notable"
    gl_str=f"{glycemie_mgdl}mg/dl ({mgdl_vers_mmol(glycemie_mgdl)}mmol/l)" if glycemie_mgdl else "Non mesuree"
    o2_str="O2 supplementaire" if o2_supp else "Air ambiant"
    return {
        "heure":    heure,
        "op":       code_operateur,
        "age":      age,
        "motif":    motif,
        "cat":      cat,
        "atcd":     atcd_str,
        "allergies": allergies or "Aucune connue",
        "niveau":   LABELS_TRI.get(niveau,niveau),
        "secteur":  SECTEURS_TRI.get(niveau,""),
        "critere":  critere,
        "justif":   justif,
        "delai":    DELAIS_TRI.get(niveau,"?"),
        "fc": fc,"pas":pas,"spo2":spo2,"fr":fr,"temp":temp,"gcs":gcs,
        "eva":eva,"news2":news2,"glycemie":gl_str,"o2":o2_str,
    }

# ==============================================================================
# [3] PHARMACOLOGIE BCFI
# ==============================================================================

_CI_AINS = ["Ulcere gastro-duodenal","Insuffisance renale chronique",
            "Insuffisance hepatique","Grossesse en cours","Chimiotherapie en cours"]

def _ci_ains(atcd): return [c for c in _CI_AINS if c in atcd]

def dose_paracetamol_iv(poids_kg):
    if poids_kg<=0: return None,"Poids invalide"
    if poids_kg>=50:
        return {"dose_g":1.0,"volume":"100ml NaCl 0.9% sur 15min","freq":"Toutes les 6h (max 4g/24h)","ref":"BCFI — Paracetamol IV"},None
    dg=min(round(15*poids_kg/1000,2),1.0)
    return {"dose_g":dg,"volume":f"{dg*1000:.0f}mg dans 100ml NaCl 0.9%","freq":"Toutes les 6h","ref":"BCFI — Paracetamol IV"},None

def dose_ketorolac_iv(poids_kg,atcd):
    ci=_ci_ains(atcd)
    if ci: return None,f"Contre-indique : {', '.join(ci)}"
    d=15.0 if poids_kg<50 else 30.0
    return {"dose_mg":d,"admin":"IV lent 15 secondes","freq":"Toutes les 6h — max 5j","ref":"BCFI — Ketorolac (Taradyl)"},None

def dose_tramadol_iv(poids_kg,atcd,age_patient):
    alertes=[]
    if "Epilepsie" in atcd: alertes.append("CONTRE-INDIQUE — Epilepsie (seuil epileptogene abaisse)")
    if "IMAO (inhibiteurs MAO)" in atcd: alertes.append("CONTRE-INDICATION ABSOLUE — SYNDROME SEROTONINERGIQUE FATAL avec IMAO")
    if "Antidepresseurs serotoninergiques (ISRS / IRSNA)" in atcd: alertes.append("INTERACTION MAJEURE — ISRS/IRSNA — risque syndrome serotoninergique")
    d=100.0 if poids_kg>=50 else round(1.5*poids_kg,0)
    return {"dose_mg":d,"admin":f"{d:.0f}mg dans 100ml NaCl 0.9% — IV sur 30min","freq":"Toutes les 6h (max 400mg/24h)","alertes":alertes,"ref":"BCFI — Tramadol"},None

def dose_piritramide_iv(poids_kg,age_patient,atcd):
    red=(age_patient>=70 or "Insuffisance renale chronique" in atcd or "Insuffisance hepatique" in atcd)
    f=0.5 if red else 1.0
    dmin=min(round(0.03*poids_kg*f,2),(3.0 if poids_kg<70 else 6.0)*f)
    dmax=min(round(0.05*poids_kg*f,2),(3.0 if poids_kg<70 else 6.0)*f)
    return {"bolus_min":dmin,"bolus_max":dmax,"admin":"IV lent sur 1-2min — titrer si EVA>3 apres 10-15min","note":"Dose reduite 50% si age>=70, IRC ou IH" if red else "","ref":"BCFI — Piritramide (Dipidolor)"},None

def dose_morphine_iv(poids_kg,age_patient):
    red=age_patient>=70
    f=0.5 if red else 1.0
    dmin=min(round(0.05*poids_kg*f,1),2.5)
    dmax=min(round(0.10*poids_kg*f,1),5.0)
    return {"bolus_min":dmin,"bolus_max":dmax,"admin":"IV lent 2-3min — titrer par paliers 2mg/5-10min","note":"Dose reduite 50% si age>=70" if red else "","ref":"BCFI — Morphine IV"},None

def dose_naloxone(poids_kg,age_patient,dependance=False):
    alertes=[]
    if dependance:
        d=0.04; admin="0.04mg IV par paliers de 2min — titration douce"
        note="DEPENDANCE — objectif : ventilation adequate, PAS levee totale"
        alertes.append("Risque sevrage aigu si surdosage Naloxone")
    elif age_patient<18:
        d=min(round(0.01*poids_kg,3),0.4); admin=f"{d}mg IV direct — 0.01mg/kg"
        note=f"Dose pediatrique : {d}mg pour {poids_kg}kg"
    else:
        d=0.4; admin="0.4mg IV direct — repeter toutes les 2-3min (max 10mg)"
        note="Absence reponse apres 10mg : reconsiderer le diagnostic"
    return {"dose_bolus":d,"admin":admin,"note":note,"alertes":alertes,
            "surveillance":"Monitoring SpO2+FR+conscience — demi-vie courte 30-90min","ref":"BCFI — Naloxone (Narcan)"},None

def dose_adrenaline_anaphylaxie(poids_kg):
    if poids_kg<=0: return None,"Poids invalide"
    if poids_kg>=30: d=0.5; note="0.5ml solution 1mg/ml"
    else: d=min(round(0.01*poids_kg,3),0.5); note=f"0.01mg/kg = {d}mg ({round(d*1000):.0f}µg)"
    return {"dose_mg":d,"voie":"IM face antero-laterale cuisse","note":note,
            "repeter":"Repeter 5-15min si pas d'amelioration","moniteur":"Monitoring FC PA SpO2",
            "ref":"BCFI — Adrenaline Sterop 1mg/ml — Lignes directrices anaphylaxie 2023"},None

def dose_glucose_hypoglycemie(poids_kg,voie="IV",glycemie_mgdl=None):
    if glycemie_mgdl is None:
        return None,"Glycemie non mesuree — protocole desactive par securite. Mesurer avant administration."
    if poids_kg<=0: return None,"Poids invalide"
    if voie=="IV":
        dg=min(round(0.3*poids_kg,1),15.0); dm=round(dg/0.3,0)
        return {"dose_g":dg,"volume":f"{dm:.0f}ml Glucose 30% IV lent sur 5min","controle":"Glycemie de controle a 15min","ref":"BCFI — Glucose 30% (Glucosie)"},None
    return {"dose":"1mg Glucagon","admin":"IM ou SC si acces veineux impossible","controle":"Glycemie a 20min","ref":"BCFI — Glucagon (GlucaGen HypoKit)"},None

def dose_ceftriaxone_iv(poids_kg,age_patient):
    if poids_kg<=0: return None,"Poids invalide"
    if age_patient<18:
        dg=min(round(0.1*poids_kg,1),2.0); note=f"100mg/kg = {dg*1000:.0f}mg pour {poids_kg}kg"
    else:
        dg=2.0; note="Ne pas attendre le medecin si purpura fulminans"
    return {"dose_g":dg,"admin":"IV direct 3-5min ou IM si VVP impossible","note":note,"ref":"BCFI — Ceftriaxone — SPILF 2017"},None

def protocole_antalgique_eva(eva,poids_kg,age,atcd,glycemie_mgdl=None):
    alertes=[]; recs=[]
    imao="IMAO (inhibiteurs MAO)" in atcd
    isrs="Antidepresseurs serotoninergiques (ISRS / IRSNA)" in atcd
    ci_ains=_ci_ains(atcd)
    if imao: alertes.append("IMAO — Tramadol CONTRE-INDIQUE. Utiliser Paracetamol IV ou Dipidolor.")
    if isrs: alertes.append("ISRS/IRSNA — Tramadol deconseille. Preferer Dipidolor ou Morphine.")
    res_para,_=dose_paracetamol_iv(poids_kg)
    if res_para: recs.append({"palier":"1","med":"Paracetamol IV","dose":f"{res_para['dose_g']}g","detail":res_para["volume"],"ref":res_para["ref"],"alertes":[]})
    if eva>=4:
        if not ci_ains:
            res,err=dose_ketorolac_iv(poids_kg,atcd)
            if res: recs.append({"palier":"2","med":"Ketorolac (Taradyl) IV","dose":f"{res['dose_mg']}mg","detail":res["admin"],"ref":res["ref"],"alertes":[]})
        if not imao and "Epilepsie" not in atcd:
            res,err=dose_tramadol_iv(poids_kg,atcd,age)
            if res: recs.append({"palier":"2","med":"Tramadol IV","dose":f"{res['dose_mg']:.0f}mg","detail":res["admin"],"ref":res["ref"],"alertes":res.get("alertes",[])})
    if eva>=7:
        res,_=dose_piritramide_iv(poids_kg,age,atcd)
        if res: recs.append({"palier":"3","med":"Piritramide (Dipidolor) IV","dose":f"{res['bolus_min']}-{res['bolus_max']}mg","detail":res["admin"],"ref":res["ref"],"alertes":[]})
    return {"alertes":alertes,"recs":recs}

# ==============================================================================
# [4] HELPERS UI
# ==============================================================================

def html(code): st.markdown(code, unsafe_allow_html=True)

def sec(titre):
    html(f'<div class="hp-sec">{titre}</div>')

def alerte(msg, typ="danger"):
    icons={"danger":"","warning":"","success":"","info":""}
    html(f'<div class="hp-alert {typ}"><span class="hp-alert-icon">{icons.get(typ,"")}</span><span>{msg}</span></div>')

def carte_debut(titre=""):
    html(f'<div class="hp-card"><div class="hp-card-title">{titre}</div>' if titre else '<div class="hp-card">')

def carte_fin():
    html('</div>')

def banniere_purpura(details):
    if details and details.get("purpura"):
        html(
            '<div class="purpura-banner">'
            '<div class="purpura-title">PURPURA FULMINANS — TRI 1 IMMEDIAT</div>'
            '<div class="purpura-body">'
            'Ceftriaxone 2g IV (ou IM si VVP impossible) — NE PAS ATTENDRE le bilan.<br>'
            'Appel medecin senior immediat — Transfert dechocage.'
            '</div></div>'
        )

def banniere_news2_critique(n2):
    if n2>=9:
        html(
            f'<div class="purpura-banner" style="background:linear-gradient(135deg,#1A0A2E,#2D1B69);border-color:#7C3AED;">'
            f'<div class="purpura-title" style="color:#D8B4FE;">NEWS2 {n2} — ENGAGEMENT VITAL — APPEL MEDICAL IMMEDIAT</div>'
            f'<div class="purpura-body" style="color:#EDE9FE;">Transfert dechocage — Medecin au chevet sans delai.</div></div>'
        )
    elif n2>=7:
        alerte(f"NEWS2 {n2} >= 7 — Risque critique — Appel medical immediat","danger")
    elif n2>=5:
        alerte(f"NEWS2 {n2} >= 5 — Risque eleve — Reevaluation toutes les 30min","warning")

def gauge_news2(n2, bpco=False):
    lbl, css_n2, color, pct = news2_meta(n2)
    pct_bar = min(int(n2/12*100), 100)
    bpco_note = '<br><small style="opacity:.7;font-size:.65rem;">Echelle 2 BPCO (SpO2 cible 88-92%) activee</small>' if bpco else ""
    html(
        f'<div class="news2-gauge">'
        f'<div class="hp-sec" style="margin-top:0;">Score NEWS2</div>'
        f'<div class="news2-score {css_n2}">{n2}</div>'
        f'<div class="news2-label {css_n2}">{lbl}{bpco_note}</div>'
        f'<div class="news2-bar-track">'
        f'<div class="news2-bar-fill" style="width:{pct_bar}%;background:{color};"></div>'
        f'</div>'
        f'<div style="display:flex;justify-content:space-between;font-size:.62rem;color:var(--text-muted);margin-top:4px;">'
        f'<span>0</span><span>Faible</span><span>Modere</span><span>Eleve</span><span>12</span>'
        f'</div>'
        f'</div>'
    )

def vitaux_grid(fc, pas, spo2, fr, temp, gcs, bpco=False):
    def niv(val, seuil_w, seuil_c, inverse=False):
        ok = val >= seuil_w if not inverse else val <= seuil_w
        bad = val >= seuil_c if not inverse else val <= seuil_c
        return "crit" if bad else ("warn" if not ok else "")

    spo2_warn = 88 if bpco else 94
    spo2_crit = 85 if bpco else 90
    spo2_niv = "crit" if spo2<=spo2_crit else ("warn" if spo2<=spo2_warn else "")

    fc_niv  = "crit" if fc>=150 or fc<=40 else ("warn" if fc>=120 or fc<=50 else "")
    pas_niv = "crit" if pas<=90 else ("warn" if pas<=100 else "")
    fr_niv  = "crit" if fr>=30 else ("warn" if fr>=22 else "")
    t_niv   = "crit" if temp>=40 or temp<=35 else ("warn" if temp>=38.5 or temp<=36 else "")
    g_niv   = "crit" if gcs<=8 else ("warn" if gcs<=13 else "")

    html(
        f'<div class="vit-grid">'
        f'<div class="vit-item {fc_niv}"><div class="vit-label">FC</div><div class="vit-value">{fc}</div><div class="vit-unit">bpm</div></div>'
        f'<div class="vit-item {pas_niv}"><div class="vit-label">PAS</div><div class="vit-value">{pas}</div><div class="vit-unit">mmHg</div></div>'
        f'<div class="vit-item {spo2_niv}"><div class="vit-label">SpO2{"*" if bpco else ""}</div><div class="vit-value">{spo2}</div><div class="vit-unit">%</div></div>'
        f'<div class="vit-item {fr_niv}"><div class="vit-label">FR</div><div class="vit-value">{fr}</div><div class="vit-unit">/min</div></div>'
        f'<div class="vit-item {t_niv}"><div class="vit-label">Temperature</div><div class="vit-value">{temp}</div><div class="vit-unit">degres C</div></div>'
        f'<div class="vit-item {g_niv}"><div class="vit-label">GCS</div><div class="vit-value">{gcs}</div><div class="vit-unit">/15</div></div>'
        f'</div>'
    )
    if bpco:
        alerte("BPCO — Cible SpO2 : 88-92% — Echelle 2 NEWS2 activee — Eviter l'hyperoxie","warning")

def carte_triage(niv, justif, n2):
    css = CSS_TRI.get(niv,"tri-5")
    lbl = LABELS_TRI.get(niv,niv)
    sec_lbl = SECTEURS_TRI.get(niv,"")
    delai = DELAIS_TRI.get(niv,"?")
    html(
        f'<div class="tri-result {css}">'
        f'<div class="tri-label">{lbl}</div>'
        f'<div class="tri-justif">{justif}</div>'
        f'<div class="tri-sector">{sec_lbl}</div>'
        f'<span class="tri-badge">Delai max : {delai} min</span>'
        f'<span class="tri-badge" style="margin-left:8px;">NEWS2 : {n2}</span>'
        f'</div>'
    )

def pharma_card(nom, dose, details_lines, ref, palier="2", alertes=None):
    palier_css={"1":"palier-1","2":"palier-2","3":"palier-3","U":"urgence","A":"antidote"}.get(palier,"palier-2")
    if alertes:
        for a in alertes:
            alerte(a,"danger")
    detail_html="<br>".join([l for l in details_lines if l])
    html(
        f'<div class="pharma-card {palier_css}">'
        f'<div class="pharma-name">{nom}</div>'
        f'<div class="pharma-dose">{dose}</div>'
        f'<div class="pharma-detail">{detail_html}</div>'
        f'<div class="pharma-ref">{ref}</div>'
        f'</div>'
    )

def pharma_locked(msg="Glycemie requise avant activation du protocole glucose / insuline"):
    html(f'<div class="pharma-locked"><strong>Protocole desactive</strong><br>{msg}</div>')

def disclaimer():
    html(
        '<div class="hp-disclaimer">'
        'AKIR-IAO est un outil d\'aide a la decision clinique. Il ne se substitue pas au jugement '
        'clinique du medecin responsable. Les doses affichees sont conformes au BCFI (Belgique) et '
        'doivent etre validees par un medecin prescripteur avant administration.<br>'
        'RGPD : aucun nom ni prenom collecte — UUID anonyme uniquement — stockage local.<br>'
        '<div class="disclaimer-sig">'
        'AKIR-IAO v18.0 Hospital Pro — Ismail Ibn-Daifa — FRENCH Triage SFMU V1.1 — Hainaut, Wallonie, Belgique'
        '</div></div>'
    )

def widget_glycemie(key, label="Glycemie capillaire (mg/dl)", required=False):
    v = st.number_input(label, min_value=0, max_value=1500, value=0, step=5, key=key)
    if v==0:
        if required:
            alerte("Glycemie non mesuree — Saisir la valeur pour activer les protocoles glucose","warning")
        else:
            st.caption("Saisir 0 si non realisee")
        return None
    mmol=mgdl_vers_mmol(v)
    st.caption(f"Reference : {mmol} mmol/l")
    if v<GLYCEMIE["hypoglycemie_severe"]:
        alerte(f"HYPOGLYCEMIE SEVERE : {v}mg/dl ({mmol}mmol/l) — Glucose 30% IV immediat","danger")
    elif v<GLYCEMIE["hypoglycemie_moderee"]:
        alerte(f"Hypoglycemie moderee : {v}mg/dl ({mmol}mmol/l)","warning")
    return float(v)

def widget_bpco(key_prefix):
    bpco=st.checkbox("Patient BPCO connu ?",key=f"{key_prefix}_bpco",
        help="Active l'echelle 2 NEWS2 — cible SpO2 88-92%")
    if bpco:
        alerte("BPCO — Cible SpO2 : 88-92% — Eviter la normoxie — Echelle 2 NEWS2","warning")
    parole=st.radio("Peut s'exprimer en phrases completes ?",
        [True,False],format_func=lambda x:"Oui — phrases completes" if x else "Non — mots isoles",
        horizontal=True,key=f"{key_prefix}_parole")
    return bpco, parole

# ==============================================================================
# [5] PERSISTANCE RGPD
# ==============================================================================

REG_FILE="akir_registre_anon.json"
ANT_FILE="akir_antalgie_log.json"
ALR_FILE="akir_journal_alertes.json"
ERR_FILE="akir_errors.log"

def _charger(f):
    if os.path.exists(f):
        try:
            with open(f,"r",encoding="utf-8") as fp: return json.load(fp)
        except: return []
    return []

def _sauver(f,data):
    try:
        with open(f,"w",encoding="utf-8") as fp: json.dump(data,fp,ensure_ascii=False,indent=2)
    except Exception as e:
        try:
            with open(ERR_FILE,"a") as fe: fe.write(f"[{datetime.now()}] {e}\n")
        except: pass

def ajouter_registre(d):
    uid=str(uuid.uuid4())[:8].upper()
    entree={
        "uid":uid,"heure":datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "motif":d.get("motif",""),"categorie":d.get("categorie",""),
        "niveau":d.get("niveau",""),"news2":d.get("news2",0),
        "fc":d.get("fc"),"pas":d.get("pas"),"spo2":d.get("spo2"),
        "fr":d.get("fr"),"temp":d.get("temp"),"gcs":d.get("gcs"),
        "code_operateur":d.get("code_operateur","IAO"),
    }
    reg=_charger(REG_FILE); reg.insert(0,entree); _sauver(REG_FILE,reg[:500])
    return uid

def enregistrer_alerte(uid,n2,niv,alertes,op="IAO"):
    e={"uid":uid,"heure":datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
       "news2":n2,"niveau":niv,"alertes":alertes,"operateur":op}
    j=_charger(ALR_FILE); j.insert(0,e); _sauver(ALR_FILE,j[:500])

# ==============================================================================
# [6] SESSION STATE
# ==============================================================================

DEFS={
    "session_uid":          lambda: str(uuid.uuid4())[:8].upper(),
    "code_operateur":       "",
    "heure_arrivee":        None,
    "heure_premier_contact":None,
    "derniere_reeval":      None,
    "historique":           [],
    "histo_reeval":         [],
    "uid_patient_courant":  None,
}
for k,v in DEFS.items():
    if k not in st.session_state:
        st.session_state[k]=v() if callable(v) else v

# ==============================================================================
# [7] EN-TETE
# ==============================================================================

html(
    '<div class="hp-header">'
    '<div class="hp-title">AKIR-IAO v18.0 — Hospital Pro</div>'
    '<div class="hp-subtitle">Aide au Triage Infirmier — Urgences du Hainaut, Wallonie, Belgique</div>'
    '<div>'
    '<span class="hp-badge">FRENCH SFMU V1.1</span>'
    '<span class="hp-badge">BCFI Belgique</span>'
    '<span class="hp-badge">RGPD</span>'
    '<span class="hp-badge">Ismail Ibn-Daifa</span>'
    '</div>'
    '</div>'
)

# ==============================================================================
# [8] SIDEBAR
# ==============================================================================

with st.sidebar:
    html('<div class="hp-sec">Operateur IAO</div>')
    code_op=st.text_input("Code operateur (anonyme)",value=st.session_state.code_operateur,
        max_chars=10,placeholder="ex: IAO01",help="Ne saisir ni nom ni prenom (RGPD)")
    if code_op: st.session_state.code_operateur=code_op.upper()

    html('<div class="hp-sec">Chronometre patient</div>')
    cb1,cb2=st.columns(2)
    if cb1.button("Arrivee",use_container_width=True):
        st.session_state.heure_arrivee=datetime.now()
        st.session_state.histo_reeval=[]; st.session_state.historique=[]
    if cb2.button("Contact IAO",use_container_width=True):
        st.session_state.heure_premier_contact=datetime.now()

    if st.session_state.heure_arrivee:
        el=(datetime.now()-st.session_state.heure_arrivee).total_seconds()
        m,s=divmod(int(el),60)
        col=(f"#EF4444" if el>600 else ("#F59E0B" if el>300 else "#22C55E"))
        html(f'<div style="text-align:center;font-family:\'JetBrains Mono\',monospace;font-size:2rem;font-weight:700;color:{col};">{m:02d}:{s:02d}</div>')
        st.caption(f"Arrivee : {st.session_state.heure_arrivee.strftime('%H:%M')}")
    else:
        st.info("Cliquer sur 'Arrivee' pour demarrer")

    html('<div class="hp-sec">Patient</div>')
    age=st.number_input("Age (annees)",0,120,45,key="sb_age")
    if age==0:
        age_mois=st.number_input("Age en mois",0,11,3,key="sb_mois")
        age=round(age_mois/12.0,4)
        alerte(f"Nourrisson {age_mois} mois — seuils pediatriques appliques","info")
    poids_kg=st.number_input("Poids (kg)",1,250,70,key="sb_poids")
    atcd=st.multiselect("Antecedents",LISTE_ATCD,key="sb_atcd")
    allergies=st.text_input("Allergies",key="sb_allergies",placeholder="ex: Penicilline")
    o2_supp=st.checkbox("O2 supplementaire en cours",key="sb_o2")

    html('<div class="hp-sec">Session RGPD</div>')
    st.caption(f"Session : {st.session_state.session_uid}")
    st.caption("Aucun nom collecte — UUID anonyme")
    if st.button("Nouvelle session (reset)",use_container_width=True):
        for k,v in DEFS.items(): st.session_state[k]=v() if callable(v) else v
        st.rerun()

# ==============================================================================
# [9] ONGLETS
# ==============================================================================

TABS=["Tri Rapide","Signes Vitaux","Anamnesee","Triage","Scores","Pharmacie","Reevaluation","Historique","Transmission SBAR"]
t_rapide,t_vitaux,t_anamnese,t_triage,t_scores,t_pharma,t_reeval,t_histo,t_sbar=st.tabs(TABS)

# Variables partagees
temp=fr=fc=pas=spo2=gcs=news2=None
motif=cat=""
details: dict={}
eva_sc=0
niveau=justif=critere=""
bpco_global=False

# ------------------------------------------------------------------------------
# ONGLET 1 — TRI RAPIDE
# ------------------------------------------------------------------------------
with t_rapide:
    sec("Constantes vitales")
    c1,c2,c3=st.columns(3)
    temp=c1.number_input("T (degres C)",30.0,45.0,37.0,0.1,key="r_temp")
    fc  =c2.number_input("FC (bpm)",20,220,80,key="r_fc")
    pas =c3.number_input("PAS (mmHg)",40,260,120,key="r_pas")
    c4,c5,c6=st.columns(3)
    spo2=c4.number_input("SpO2 (%)",50,100,98,key="r_spo2")
    fr  =c5.number_input("FR (/min)",5,60,16,key="r_fr")
    gcs =c6.number_input("GCS (3-15)",3,15,15,key="r_gcs")

    bpco_r=st.checkbox("Patient BPCO",key="r_bpco",help="Active SpO2 cible 88-92%")
    if bpco_r: alerte("BPCO — Cible SpO2 : 88-92% — Echelle 2 NEWS2","warning")

    news2,n2w=calculer_news2(fr,spo2,o2_supp,temp,pas,fc,gcs,bpco_r)
    for w in n2w: alerte(w,"warning")

    gauge_news2(news2, bpco_r)
    vitaux_grid(fc,pas,spo2,fr,temp,gcs,bpco_r)

    si=calculer_shock_index(fc,pas)
    si_css="si-crit" if si>=1.0 else ("si-warn" if si>=0.8 else "si-normal")
    html(f'<div class="si-box"><div class="si-label">Shock Index</div><div class="si-value {si_css}">{si}</div><div class="si-label">FC/PAS — >1.0 = choc probable</div></div>')

    if age<18:
        sipa_v,sipa_i,sipa_a=calculer_sipa(fc,age)
        alerte(sipa_i,"danger" if sipa_a else "info")

    sec("Motif de recours")
    MOTIFS_R=["Douleur thoracique / SCA","Dyspnee / insuffisance respiratoire",
              "AVC / Deficit neurologique","Alteration de conscience / Coma",
              "Traumatisme cranien","Hypotension arterielle","Tachycardie / tachyarythmie",
              "Fievre","Douleur abdominale","Allergie / anaphylaxie","Hypoglycemie",
              "Etat de mal epileptique / Convulsions","Pediatrie - Fievre <= 3 mois","Autre motif"]
    motif=st.selectbox("Motif",MOTIFS_R,key="r_motif"); cat="Tri rapide"
    eva_sc=int(st.select_slider("EVA (0-10)",[str(i) for i in range(11)],value="0",key="r_eva"))
    details={"eva":eva_sc,"atcd":atcd}

    details["purpura"]=st.checkbox("Purpura non effacable a la pression — TEST DU VERRE OBLIGATOIRE",
        key="r_purpura",help="Purpura fulminans — Tri 1 absolu — Ceftriaxone 2g IV IMMEDIAT")
    if details.get("purpura"): banniere_purpura(details)

    gl_r=widget_glycemie("r_glyc","Glycemie capillaire (mg/dl)")
    if gl_r: details["glycemie_mgdl"]=gl_r

    if st.button("Calculer le niveau de triage",type="primary",use_container_width=True):
        banniere_news2_critique(news2)
        banniere_purpura(details)
        niv_r,just_r,crit_r=french_triage(motif,details,fc,pas,spo2,fr,gcs,temp,age,news2,gl_r)
        carte_triage(niv_r,just_r,news2)
        d2,at2,_=verifier_coherence(fc,pas,spo2,fr,gcs,temp,eva_sc,motif,atcd,details,news2,gl_r)
        for d in d2: alerte(d,"danger")
        for a in at2: alerte(a,"warning")

# ------------------------------------------------------------------------------
# ONGLET 2 — SIGNES VITAUX
# ------------------------------------------------------------------------------
with t_vitaux:
    sec("Parametres vitaux")
    v1,v2,v3=st.columns(3)
    temp=v1.number_input("T (degres C)",30.0,45.0,37.0,0.1,key="v_temp")
    fc  =v1.number_input("FC (bpm)",20,220,80,key="v_fc")
    pas =v2.number_input("PAS (mmHg)",40,260,120,key="v_pas")
    spo2=v2.number_input("SpO2 (%)",50,100,98,key="v_spo2")
    fr  =v3.number_input("FR (/min)",5,60,16,key="v_fr")

    sec("Glasgow Coma Scale")
    g1,g2,g3=st.columns(3)
    gy=g1.selectbox("Yeux (Y)",[4,3,2,1],format_func=lambda x:{4:"4-Spontanee",3:"3-Demande",2:"2-Douleur",1:"1-Aucune"}[x],key="v_gy")
    gv=g2.selectbox("Verbale (V)",[5,4,3,2,1],format_func=lambda x:{5:"5-Orientee",4:"4-Confuse",3:"3-Mots",2:"2-Sons",1:"1-Aucune"}[x],key="v_gv")
    gm=g3.selectbox("Motrice (M)",[6,5,4,3,2,1],format_func=lambda x:{6:"6-Obeit",5:"5-Localise",4:"4-Evitement",3:"3-Flexion",2:"2-Extension",1:"1-Aucune"}[x],key="v_gm")
    gcs,_=calculer_gcs(gy,gv,gm)
    st.metric("Score GCS",f"{gcs} / 15")

    bpco_v="BPCO" in atcd
    news2,n2w=calculer_news2(fr,spo2,o2_supp,temp,pas,fc,gcs,bpco_v)
    for w in n2w: alerte(w,"warning")
    bpco_global=bpco_v

    gauge_news2(news2, bpco_v)
    vitaux_grid(fc,pas,spo2,fr,temp,gcs,bpco_v)
    banniere_news2_critique(news2)

    if age<18:
        sipa_v2,sipa_i2,sipa_a2=calculer_sipa(fc,age)
        alerte(sipa_i2,"danger" if sipa_a2 else "info")

    si=calculer_shock_index(fc,pas)
    si_css="si-crit" if si>=1.0 else ("si-warn" if si>=0.8 else "si-normal")
    html(f'<div class="si-box"><div class="si-label">Shock Index</div><div class="si-value {si_css}">{si}</div></div>')
    disclaimer()

# ------------------------------------------------------------------------------
# ONGLET 3 — ANAMNESE
# ------------------------------------------------------------------------------
with t_anamnese:
    if temp is None: temp=37.0; fc=80; pas=120; spo2=98; fr=16; gcs=15

    sec("Evaluation de la douleur")
    eva_sc=int(st.select_slider("EVA (0=aucune — 10=maximale)",[str(i) for i in range(11)],value="0",key="an_eva"))

    sec("Motif de recours")
    MOTS_CAT={
        "Cardio-circulatoire":["Arret cardio-respiratoire","Hypotension arterielle","Douleur thoracique / SCA","Tachycardie / tachyarythmie","Bradycardie / bradyarythmie","Palpitations","Hypertension arterielle","Allergie / anaphylaxie"],
        "Respiratoire":["Dyspnee / insuffisance respiratoire","Dyspnee / insuffisance cardiaque"],
        "Digestif":["Douleur abdominale","Vomissements / Diarrhee","Hematemese / Rectorragie"],
        "Neurologie":["AVC / Deficit neurologique","Traumatisme cranien","Alteration de conscience / Coma","Cephalee","Etat de mal epileptique / Convulsions","Syndrome confusionnel","Malaise"],
        "Traumatologie":["Traumatisme du thorax / abdomen / rachis cervical","Traumatisme du bassin / hanche / femur","Traumatisme d'un membre / epaule"],
        "Infectiologie":["Fievre"],
        "Pediatrie":["Pediatrie - Fievre <= 3 mois"],
        "Peau":["Petechie / Purpura","Erytheme etendu / Eruption cutanee"],
        "Gynecologie":["Accouchement imminent","Complication de grossesse (1er / 2eme trimestre)","Menorragie / Metrorragie"],
        "Metabolique":["Hypoglycemie","Hyperglycemie / Cetoacidose diabetique"],
        "Divers":["Renouvellement ordonnance","Examen administratif"],
    }
    cat=st.selectbox("Categorie",list(MOTS_CAT.keys()),key="an_cat")
    motif=st.selectbox("Motif",MOTS_CAT[cat],key="an_motif")

    sec("Alerte transversale")
    details={"eva":eva_sc,"atcd":atcd}
    details["purpura"]=st.checkbox("Purpura non effacable (test du verre)",key="an_purpura",
        help="Purpura fulminans — Tri 1 absolu — Ceftriaxone 2g IV IMMEDIAT")
    if details.get("purpura"): banniere_purpura(details)

    sec("Questions discriminantes")
    if motif=="Douleur thoracique / SCA":
        details["ecg"]=st.selectbox("ECG",["Normal","Anormal typique SCA","Anormal non typique"])
        details["douleur_type"]=st.selectbox("Type douleur",["Atypique","Typique persistante/intense","Type coronaire"])
        fx=st.columns(4)
        fv=[fx[0].checkbox("HTA",key="f_hta",value="HTA" in atcd),fx[1].checkbox("Diabete",key="f_diab"),
            fx[2].checkbox("Tabagisme",key="f_tab"),fx[3].checkbox("ATCD coronarien",key="f_atcd")]
        details["frcv_count"]=sum(fv)
    elif motif=="Dyspnee / insuffisance respiratoire":
        bpco_d,parole_d=widget_bpco("an_dysp")
        details["bpco_dyspnee"]=bpco_d; details["parole_ok"]=parole_d
        details["orthopnee"]=st.checkbox("Orthopnee",key="an_orth")
        details["tirage"]=st.checkbox("Tirage intercostal",key="an_tir")
    elif motif=="AVC / Deficit neurologique":
        details["delai_heures"]=st.number_input("Delai depuis debut symptomes (h)",0.0,72.0,2.0,0.5,key="an_del")
        details["deficit_progressif"]=st.checkbox("Deficit progressif",key="an_dp")
    elif motif=="Traumatisme cranien":
        details["aod_avk"]=st.checkbox("Sous anticoagulants / AOD",key="an_aod",value="Anticoagulants / AOD" in atcd)
        details["perte_conscience"]=st.checkbox("Perte de conscience initiale",key="an_pc")
    elif motif=="Petechie / Purpura":
        alerte("TEST DU VERRE OBLIGATOIRE — Appuyer un verre sur les taches. Si elles NE S'EFFACENT PAS = urgence absolue.","warning")
        details["non_effacable"]=st.checkbox("Purpura NON effacable au verre",key="an_noneff")
        details["etendu"]=st.checkbox("Purpura etendu",key="an_etend")
        details["mauvaise_tolerance"]=st.checkbox("Mauvaise tolerance clinique",key="an_tol")
        if details.get("non_effacable"): banniere_purpura({"purpura":True})
    elif motif=="Fievre":
        details["confusion"]=st.checkbox("Confusion / alteration mentale",key="an_conf")
        details["mauvaise_tolerance"]=st.checkbox("Mauvaise tolerance",key="an_tolv")
    elif motif in ("Hypoglycemie","Alteration de conscience / Coma","Etat de mal epileptique / Convulsions"):
        gl_an=widget_glycemie("an_glyc","Glycemie capillaire (mg/dl) — SYSTEMATIQUE")
        if gl_an: details["glycemie_mgdl"]=gl_an
    elif motif=="Hyperglycemie / Cetoacidose diabetique":
        gl_an2=widget_glycemie("an_glyc2","Glycemie capillaire (mg/dl)")
        if gl_an2: details["glycemie_mgdl"]=gl_an2
        details["cetose"]=st.checkbox("Cetose elevee / cetoacidose",key="an_ceto")

# ------------------------------------------------------------------------------
# ONGLET 4 — TRIAGE
# ------------------------------------------------------------------------------
with t_triage:
    if temp is None: temp=37.0; fc=80; pas=120; spo2=98; fr=16; gcs=15
    if not motif: motif="Fievre"; cat="Infectiologie"

    bpco_t="BPCO" in atcd or details.get("bpco_dyspnee",False)
    news2,n2w=calculer_news2(fr,spo2,o2_supp,temp,pas,fc,gcs,bpco_t)
    for w in n2w: alerte(w,"warning")

    # Glycemie dans le triage (si pas encore saisie en anamnese)
    if not details.get("glycemie_mgdl"):
        gl_t_widget=widget_glycemie("t_glyc","Glycemie capillaire (mg/dl) — si non saisie en Anamnese")
        if gl_t_widget:
            details["glycemie_mgdl"]=gl_t_widget
    gl_t=details.get("glycemie_mgdl")

    niveau,justif,critere=french_triage(motif,details,fc,pas,spo2,fr,gcs,temp,age,news2,gl_t)

    banniere_news2_critique(news2)
    banniere_purpura(details)

    # Shock Index affiché dans le triage
    si_t=calculer_shock_index(fc,pas)
    si_t_css="si-crit" if si_t>=1.0 else ("si-warn" if si_t>=0.8 else "si-normal")
    html(f'<div class="si-box" style="margin-bottom:12px;">'
         f'<div class="si-label">Shock Index (FC/PAS)</div>'
         f'<div class="si-value {si_t_css}">{si_t}</div>'
         f'<div class="si-label">{"CHOC PROBABLE" if si_t>=1.0 else ("Surveillance" if si_t>=0.8 else "Normal")}</div>'
         f'</div>')

    if st.session_state.derniere_reeval:
        mins=(datetime.now()-st.session_state.derniere_reeval).total_seconds()/60
        if mins>DELAIS_TRI.get(niveau,60):
            alerte(f"Reevaluation en retard : {int(mins)} min ecoulees — max {DELAIS_TRI[niveau]} min","danger")

    carte_triage(niveau,justif,news2)
    st.caption(f"Critere : {critere}")

    d_coh,at_coh,_=verifier_coherence(fc,pas,spo2,fr,gcs,temp,details.get("eva",0),motif,atcd,details,news2,gl_t)
    for d in d_coh:
        alerte(d,"danger")
        enregistrer_alerte(st.session_state.uid_patient_courant or "ANON",news2,niveau,[d],st.session_state.code_operateur)
    for a in at_coh: alerte(a,"warning")

    if st.session_state.heure_arrivee and st.session_state.heure_premier_contact:
        ds=(st.session_state.heure_premier_contact-st.session_state.heure_arrivee).total_seconds()
        cm=10 if niveau in("M","1","2") else 30
        alerte(f"Delai IAO : {int(ds/60)} min — cible {cm} min — {'DEPASSE' if ds/60>=cm else 'Dans les delais'}",
               "danger" if ds/60>=cm else "success")

    if st.button("Enregistrer ce patient",use_container_width=True,type="primary"):
        uid=ajouter_registre({"motif":motif,"categorie":cat,"niveau":niveau,"news2":news2,
            "fc":fc,"pas":pas,"spo2":spo2,"fr":fr,"temp":temp,"gcs":gcs,
            "code_operateur":st.session_state.code_operateur})
        st.session_state.uid_patient_courant=uid
        st.session_state.histo_reeval=[]
        st.session_state.derniere_reeval=datetime.now()
        st.session_state.historique.insert(0,{"uid":uid,"heure":datetime.now().strftime("%H:%M"),
            "motif":motif,"niveau":niveau,"news2":news2})
        st.success(f"Patient enregistre — UID : {uid}")
    disclaimer()

# ------------------------------------------------------------------------------
# ONGLET 5 — SCORES
# ------------------------------------------------------------------------------
with t_scores:
    sec("qSOFA — Detection sepsis")
    qs,qpos,qw=calculer_qsofa(fr or 16,gcs or 15,pas or 120)
    for w in qw: alerte(w,"warning")
    col_qs1,col_qs2=st.columns(2)
    with col_qs1:
        interp_qs="Sepsis probable — evaluation urgente" if qs>=2 else "Risque sepsis faible"
        qs_css="si-crit" if qs>=2 else "si-normal"
        html(f'<div class="si-box"><div class="si-label">qSOFA</div><div class="si-value {qs_css}">{qs}/3</div><div class="si-label">{interp_qs}</div></div>')
    with col_qs2:
        if qpos:
            for p in qpos: alerte(p,"danger" if qs>=2 else "warning")
        else:
            alerte("Aucun critere qSOFA positif","success")

    sec("FAST — Detection AVC")
    f1,f2,f3,f4=st.columns(4)
    ff=f1.checkbox("Face",key="fast_f"); fa=f2.checkbox("Bras",key="fast_a")
    fs=f3.checkbox("Langage",key="fast_s"); ft=f4.checkbox("Debut brutal",key="fast_t")
    fsc,fi,fal=evaluer_fast(ff,fa,fs,ft)
    alerte(fi,"danger" if fal else ("warning" if fsc>=1 else "success"))

    sec("TIMI — Risque SCA sans sus-decalage")
    ti1,ti2=st.columns(2)
    ta65=ti1.checkbox("Age >=65 ans",key="ti_age",value=age>=65)
    tfrcv=ti1.checkbox(">=3 FRCV",key="ti_frcv")
    tsten=ti1.checkbox("Stenose coronaire >=50%",key="ti_sten")
    taspi=ti2.checkbox("Aspirine dans les 7j",key="ti_aspi")
    ttrop=ti2.checkbox("Troponine positive",key="ti_trop")
    tdst=ti2.checkbox("Deviation ST",key="ti_dst")
    tcris=ti2.checkbox(">=2 crises en 24h",key="ti_cris")
    tsc,_=calculer_timi(age,int(tfrcv)*3,tsten,taspi,ttrop,tdst,int(tcris)*2)
    ti_interp="Risque eleve" if tsc>=5 else ("Risque intermediaire" if tsc>=3 else "Risque faible")
    ti_cls="si-crit" if tsc>=5 else ("si-warn" if tsc>=3 else "si-normal")
    html(f'<div class="si-box"><div class="si-label">Score TIMI</div><div class="si-value {ti_cls}">{tsc}/7</div><div class="si-label">{ti_interp}</div></div>')

    sec("Algoplus — Douleur patient age non communicant")
    al1,al2,al3,al4,al5=st.columns(5)
    alg_f=al1.checkbox("Visage",key="alg_f"); alg_r=al2.checkbox("Regard",key="alg_r")
    alg_p=al3.checkbox("Plaintes",key="alg_p"); alg_ac=al4.checkbox("Corps",key="alg_ac")
    alg_co=al5.checkbox("Comportement",key="alg_co")
    asc,ai,acss,_=calculer_algoplus(alg_f,alg_r,alg_p,alg_ac,alg_co)
    alerte(f"Algoplus {asc}/5 — {ai}",acss)

    sec("Clinical Frailty Scale")
    cfs_sc=st.slider("Score CFS (1-9)",1,9,3,key="cfs_sc")
    st.caption(CFS_NIVEAUX.get(cfs_sc,""))
    cfs_l,cfs_c,cfs_r=evaluer_cfs(cfs_sc)
    alerte(f"CFS {cfs_sc} — {cfs_l}",cfs_c)
    if cfs_r: alerte("CFS >=5 — Envisager remontee du niveau de triage","warning")

# ------------------------------------------------------------------------------
# ONGLET 6 — PHARMACIE
# ------------------------------------------------------------------------------
with t_pharma:
    sec("Antalgie basee sur l'EVA")
    eva_ph=st.slider("EVA actuelle",0,10,details.get("eva",0),key="ph_eva")
    gl_ph=details.get("glycemie_mgdl")
    proto=protocole_antalgique_eva(eva_ph,poids_kg,age,atcd,gl_ph)
    for al in proto["alertes"]: alerte(al,"danger")
    for rec in proto["recs"]:
        pharma_card(
            nom=rec["med"], dose=rec["dose"],
            details_lines=[rec.get("detail",""), rec.get("note","")],
            ref=rec["ref"], palier=rec["palier"],
            alertes=rec.get("alertes",[]),
        )

    sec("Adrenaline IM — Choc anaphylactique")
    a_res,a_err=dose_adrenaline_anaphylaxie(poids_kg)
    if a_err: alerte(a_err,"warning")
    else:
        pharma_card("Adrenaline IM (Sterop 1mg/ml)",
            f"{a_res['dose_mg']}mg IM",
            [a_res["voie"],a_res["note"],a_res["repeter"],a_res["moniteur"]],
            a_res["ref"],palier="U")

    sec("Naloxone IV — Antidote opioides")
    dep_op=st.checkbox("Patient dependant aux opioides (titration douce)",key="ph_dep")
    nal_res,nal_err=dose_naloxone(poids_kg,age,dependance=dep_op)
    if nal_err: alerte(nal_err,"warning")
    else:
        pharma_card("Naloxone IV (Narcan)",
            f"{nal_res['dose_bolus']}mg / bolus",
            [nal_res["admin"],nal_res["note"],nal_res["surveillance"]],
            nal_res["ref"],palier="A",alertes=nal_res.get("alertes",[]))

    sec("Glucose 30% — Correction hypoglycemie")
    # Securite dynamique : desactive si glycemie non mesuree
    if gl_ph is None:
        pharma_locked("Mesurer la glycemie capillaire pour activer le protocole glucose / resucrage")
    else:
        g_res,g_err=dose_glucose_hypoglycemie(poids_kg,"IV",glycemie_mgdl=gl_ph)
        if g_err: alerte(g_err,"warning")
        else:
            pharma_card("Glucose 30% IV (Glucosie)",
                f"{g_res['dose_g']}g",
                [g_res["volume"],g_res["controle"]],
                g_res["ref"],palier="U")

    sec("Ceftriaxone IV — Urgence infectieuse")
    cef_res,cef_err=dose_ceftriaxone_iv(poids_kg,age)
    if cef_err: alerte(cef_err,"warning")
    else:
        pharma_card("Ceftriaxone IV (Purpura fulminans / Meningite)",
            f"{cef_res['dose_g']}g IV",
            [cef_res["admin"],cef_res["note"]],
            cef_res["ref"],palier="U")

    sec("MEOPA — Analgesie non invasive (Kalinox)")
    _ci_meopa=[ci for ci in ["Deficit en vitamine B12","Pneumothorax","Traumatisme cranien grave"]
               if ci in atcd]
    if _ci_meopa:
        alerte(f"MEOPA contre-indique : {', '.join(_ci_meopa)}","danger")
    else:
        html(
            f'<div class="pharma-card palier-2">'
            f'<div class="pharma-name">MEOPA — Melange O2/N2O 50/50 (Kalinox)</div>'
            f'<div class="pharma-dose">Inhalation spontanee</div>'
            f'<div class="pharma-detail">'
            f'Administration : masque facial avec valve anti-retour<br>'
            f'Duree maximum : 15 min par session<br>'
            f'AMM : adulte et enfant >= 1 an<br>'
            f'Surveillance : SpO2, FC, etat de conscience — arret si desaturation<br>'
            f'Ventilation de la salle obligatoire apres usage<br>'
            f'CI absolues : pneumothorax, occlusion intestinale, embolie gazeuse, deficit B12'
            f'</div>'
            f'<div class="pharma-ref">BCFI — MEOPA (Kalinox) — RCP Belgique</div>'
            f'</div>'
        )
    disclaimer()

# ------------------------------------------------------------------------------
# ONGLET 7 — REEVALUATION
# ------------------------------------------------------------------------------
with t_reeval:
    sec("Nouvelle reevaluation")

    if st.session_state.heure_arrivee and st.session_state.heure_premier_contact:
        ds=(st.session_state.heure_premier_contact-st.session_state.heure_arrivee).total_seconds()
        cm=10 if niveau in("M","1","2") else 30
        alerte(f"Delai IAO : {int(ds/60)} min — cible {cm} min",
               "danger" if ds/60>=cm else "success")

    rr1,rr2,rr3=st.columns(3)
    re_temp=rr1.number_input("T (degres C)",30.0,45.0,37.0,0.1,key="re_temp")
    re_fc  =rr1.number_input("FC (bpm)",20,220,80,key="re_fc")
    re_pas =rr2.number_input("PAS (mmHg)",40,260,120,key="re_pas")
    re_spo2=rr2.number_input("SpO2 (%)",50,100,98,key="re_spo2")
    re_fr  =rr3.number_input("FR (/min)",5,60,16,key="re_fr")
    re_gcs =rr3.number_input("GCS (3-15)",3,15,15,key="re_gcs")

    re_n2,_=calculer_news2(re_fr,re_spo2,o2_supp,re_temp,re_pas,re_fc,re_gcs,"BPCO" in atcd)
    re_niv,re_just,_=french_triage(motif or "Fievre",details,re_fc,re_pas,re_spo2,re_fr,re_gcs,re_temp,age,re_n2)

    gauge_news2(re_n2,"BPCO" in atcd)
    banniere_news2_critique(re_n2)
    st.info(f"Triage recalcule : **{LABELS_TRI[re_niv]}** — {re_just}")

    if st.button("Enregistrer cette reevaluation",use_container_width=True):
        st.session_state.histo_reeval.append({
            "heure":datetime.now().strftime("%H:%M"),
            "fc":re_fc,"pas":re_pas,"spo2":re_spo2,
            "fr":re_fr,"gcs":re_gcs,"temp":re_temp,
            "niveau":re_niv,"news2":re_n2,
        })
        st.session_state.derniere_reeval=datetime.now()
        st.success(f"Reevaluation a {datetime.now().strftime('%H:%M')} — Tri {re_niv}")

    sec("Tendance NEWS2")
    if not st.session_state.histo_reeval:
        st.info("Aucune reevaluation enregistree.")
    else:
        n2vals=[s.get("news2",0) for s in st.session_state.histo_reeval]
        maxn2=max(n2vals) if n2vals else 1
        for i,(snap) in enumerate(st.session_state.histo_reeval):
            n2=snap.get("news2",0); pct=round(n2/max(maxn2,1)*100)
            col="#EF4444" if n2>=7 else ("#F59E0B" if n2>=5 else "#22C55E")
            html(f'<div class="n2-trend-row"><div class="n2-trend-label">{snap.get("heure","?")} (H+{i})</div>'
                 f'<div class="n2-trend-track"><div class="n2-trend-fill" style="width:{max(pct,4)}%;background:{col};"></div></div>'
                 f'<div class="n2-trend-val" style="color:{col};">{n2}</div></div>')

        sec("Detail reevaluations")
        for i,snap in enumerate(st.session_state.histo_reeval):
            prev=st.session_state.histo_reeval[i-1] if i>0 else snap
            no=ORD_NIV.get(snap.get("niveau","5"),5); np_=ORD_NIV.get(prev.get("niveau","5"),5)
            if no<np_: rcss,rtend="reeval-up","AGGRAVATION"
            elif no>np_: rcss,rtend="reeval-down","AMELIORATION"
            else: rcss,rtend="reeval-stable","STABLE"
            html(f'<div class="reeval-line {rcss}">'
                 f'<strong>{snap.get("heure","?")} (H+{i})</strong>'
                 f' | Tri {snap.get("niveau","?")} | NEWS2 {snap.get("news2","?")} | '
                 f'FC {snap.get("fc","?")} | PAS {snap.get("pas","?")} | '
                 f'SpO2 {snap.get("spo2","?")}% | <strong>{rtend}</strong></div>')

        if len(st.session_state.histo_reeval)>=2:
            fi=st.session_state.histo_reeval[0]; la=st.session_state.histo_reeval[-1]
            st.markdown(f"**Bilan :** {len(st.session_state.histo_reeval)} reevaluations — "
                        f"NEWS2 : {fi.get('news2','?')} → {la.get('news2','?')} — "
                        f"Tri : {fi['niveau']} → {la['niveau']}")

# ------------------------------------------------------------------------------
# ONGLET 8 — HISTORIQUE
# ------------------------------------------------------------------------------
with t_histo:
    if not st.session_state.historique:
        st.info("Aucun patient enregistre dans cette session.")
    else:
        # Metriques de session
        niveaux_session=[p.get("niveau","5") for p in st.session_state.historique]
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Patients tries",len(st.session_state.historique))
        c2.metric("Tri 1/2 critiques",sum(1 for n in niveaux_session if n in("M","1","2")))
        c3.metric("NEWS2 moyen",round(sum(p.get("news2",0) for p in st.session_state.historique)/max(len(st.session_state.historique),1),1))
        c4.metric("Tri 5 reorientes",sum(1 for n in niveaux_session if n=="5"))

        # Histogramme rapide de repartition
        sec("Repartition par niveau de triage — session en cours")
        dist={n:niveaux_session.count(n) for n in ["M","1","2","3A","3B","4","5"]}
        total_h=len(niveaux_session) or 1
        cols_dist=st.columns(7)
        for i,(niv,count) in enumerate(dist.items()):
            pct=round(count/total_h*100)
            cols_dist[i].metric(f"Tri {niv}",count,delta=f"{pct}%",delta_color="off")

        # Liste patients
        sec("Liste des patients")
        for p in st.session_state.historique:
            hb=HB_CSS.get(p.get("niveau","5"),"hb-5")
            html(f'<div class="hist-line">'
                 f'<span class="hist-badge {hb}">{LABELS_TRI.get(p.get("niveau","5"),"?")}</span>'
                 f'<strong>{p.get("heure","?")}</strong>'
                 f'<span style="color:var(--text-muted);font-size:.72rem;">UID : {p.get("uid","?")}</span>'
                 f'<span>{p.get("motif","?")}</span>'
                 f'<span style="color:var(--text-muted);">NEWS2 {p.get("news2","?")}</span>'
                 f'</div>')

        # Export CSV du registre complet
        sec("Export des donnees — Registre anonyme")
        tous_reg=_charger(REG_FILE)
        if tous_reg:
            import io, csv as csv_mod
            out=io.StringIO()
            w_csv=csv_mod.writer(out)
            w_csv.writerow(["uid","heure","motif","categorie","niveau","news2","fc","pas","spo2","fr","temp","gcs","operateur"])
            for r in tous_reg:
                w_csv.writerow([
                    r.get("uid",""),r.get("heure",""),r.get("motif",""),r.get("categorie",""),
                    r.get("niveau",""),r.get("news2",""),r.get("fc",""),r.get("pas",""),
                    r.get("spo2",""),r.get("fr",""),r.get("temp",""),r.get("gcs",""),
                    r.get("code_operateur",""),
                ])
            csv_data=out.getvalue()
            col_exp1,col_exp2=st.columns(2)
            col_exp1.download_button(
                label="Telecharger registre CSV (toutes sessions)",
                data=csv_data,
                file_name=f"akir_registre_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",use_container_width=True,
            )
            col_exp2.metric("Patients dans le registre",len(tous_reg))
            alerte(
                f"RGPD : Le fichier CSV ne contient aucun nom ni prenom. "
                f"Identifiants UUID anonymes uniquement. {len(tous_reg)} enregistrements.",
                "info"
            )
        else:
            st.info("Aucun enregistrement dans le registre persistant.")

# ------------------------------------------------------------------------------
# ONGLET 9 — TRANSMISSION SBAR
# ------------------------------------------------------------------------------
with t_sbar:
    sec("Rapport de transmission SBAR — Format DPI-Ready")
    sbar_op=st.text_input("Code operateur pour le rapport",
        value=st.session_state.code_operateur or "IAO",key="sbar_op")

    if st.button("Generer le rapport SBAR",use_container_width=True,type="primary"):
        if not motif:
            alerte("Selectionner un motif de recours avant de generer le rapport","warning")
        else:
            sbar=generer_sbar(
                age=age,motif=motif,cat=cat,atcd=atcd,allergies=allergies,
                o2_supp=o2_supp,temp=temp or 37.0,fc=fc or 80,pas=pas or 120,
                spo2=spo2 or 98,fr=fr or 16,gcs=gcs or 15,
                eva=details.get("eva",0),news2=news2 or 0,
                niveau=niveau or "3B",justif=justif or "Non calcule",
                critere=critere or "",code_operateur=sbar_op,
                glycemie_mgdl=details.get("glycemie_mgdl"),
            )
            # Rendu visuel rapport SBAR
            html(
                f'<div class="sbar-report">'
                # Header
                f'<div class="sbar-header">'
                f'<div class="sbar-header-title">RAPPORT DE TRIAGE IAO — AKIR-IAO v18.0 Hospital Pro</div>'
                f'<div class="sbar-header-sub">Operateur : {sbar["op"]} | {sbar["heure"]} | FRENCH Triage SFMU V1.1 — Hainaut, Belgique</div>'
                f'</div>'
                # S
                f'<div class="sbar-section">'
                f'<div class="sbar-section-row"><div class="sbar-section-letter">S</div><div class="sbar-section-title">Situation</div></div>'
                f'<div class="sbar-content">'
                f'Patient de {int(sbar["age"])} ans | Motif : <strong>{sbar["motif"]}</strong> | Categorie : {sbar["cat"]}<br>'
                f'Niveau de triage attribue : <strong>{sbar["niveau"]}</strong><br>'
                f'Secteur : {sbar["secteur"]} | Delai maximum : {sbar["delai"]} min<br>'
                f'Critere de triage : {sbar["critere"]}'
                f'</div>'
                f'<div class="sbar-vital-grid">'
                f'<div class="sbar-vital-item"><div class="sbar-vital-key">FC</div><div class="sbar-vital-val">{sbar["fc"]}</div></div>'
                f'<div class="sbar-vital-item"><div class="sbar-vital-key">PAS</div><div class="sbar-vital-val">{sbar["pas"]}</div></div>'
                f'<div class="sbar-vital-item"><div class="sbar-vital-key">SpO2</div><div class="sbar-vital-val">{sbar["spo2"]}%</div></div>'
                f'<div class="sbar-vital-item"><div class="sbar-vital-key">FR</div><div class="sbar-vital-val">{sbar["fr"]}/min</div></div>'
                f'<div class="sbar-vital-item"><div class="sbar-vital-key">T</div><div class="sbar-vital-val">{sbar["temp"]}C</div></div>'
                f'<div class="sbar-vital-item"><div class="sbar-vital-key">GCS</div><div class="sbar-vital-val">{sbar["gcs"]}/15</div></div>'
                f'<div class="sbar-vital-item"><div class="sbar-vital-key">EVA</div><div class="sbar-vital-val">{sbar["eva"]}/10</div></div>'
                f'<div class="sbar-vital-item"><div class="sbar-vital-key">NEWS2</div><div class="sbar-vital-val">{sbar["news2"]}</div></div>'
                f'</div>'
                f'</div>'
                # B
                f'<div class="sbar-section">'
                f'<div class="sbar-section-row"><div class="sbar-section-letter">B</div><div class="sbar-section-title">Background</div></div>'
                f'<div class="sbar-content">'
                f'Antecedents : {sbar["atcd"]}<br>'
                f'Allergies : {sbar["allergies"]}<br>'
                f'O2 : {sbar["o2"]} | Glycemie : {sbar["glycemie"]}'
                f'</div></div>'
                # A
                f'<div class="sbar-section">'
                f'<div class="sbar-section-row"><div class="sbar-section-letter">A</div><div class="sbar-section-title">Assessment</div></div>'
                f'<div class="sbar-content">{sbar["justif"]}</div>'
                f'</div>'
                # R
                f'<div class="sbar-section">'
                f'<div class="sbar-section-row"><div class="sbar-section-letter">R</div><div class="sbar-section-title">Recommendation</div></div>'
                f'<div class="sbar-content">'
                f'Orientation : <strong>{sbar["secteur"]}</strong><br>'
                f'Delai maximum : {sbar["delai"]} minutes<br>'
                f'Remarques IAO : [A completer par l\'operateur]'
                f'</div></div>'
                # Footer
                f'<div class="sbar-footer">'
                f'AVERTISSEMENT MEDICO-LEGAL : Ce document est un support d\'aide a la decision clinique. '
                f'Il ne se substitue pas au jugement clinique du medecin responsable. '
                f'AR 18/06/1990 modifie — Responsabilite infirmiere — Hainaut, Wallonie, Belgique.'
                f'</div></div>'
            )
            # Export texte brut
            txt=(f"RAPPORT SBAR — AKIR-IAO v18.0 — {sbar['heure']}\n"
                 f"Operateur : {sbar['op']}\n\n"
                 f"[S] SITUATION\nPatient {int(sbar['age'])} ans | {sbar['motif']} | {sbar['categorie'] if 'categorie' in sbar else cat}\n"
                 f"Triage : {sbar['niveau']} | {sbar['secteur']} | Delai : {sbar['delai']} min\n\n"
                 f"[B] BACKGROUND\nATCD : {sbar['atcd']}\nAllergies : {sbar['allergies']}\n\n"
                 f"[A] ASSESSMENT\nFC {sbar['fc']} | PAS {sbar['pas']} | SpO2 {sbar['spo2']}% | FR {sbar['fr']}/min | T {sbar['temp']}C | GCS {sbar['gcs']}/15\n"
                 f"EVA {sbar['eva']}/10 | NEWS2 {sbar['news2']} | Glycemie {sbar['glycemie']} | {sbar['o2']}\n"
                 f"Justification : {sbar['justif']}\n\n"
                 f"[R] RECOMMENDATION\nOrientation : {sbar['secteur']}\nDelai max : {sbar['delai']} min\n"
                 f"Remarques : [A completer]\n\n"
                 f"AKIR-IAO v18.0 — Ismail Ibn-Daifa — FRENCH SFMU V1.1 — Hainaut, Wallonie, Belgique")
            st.download_button("Telecharger rapport SBAR (.txt)",data=txt,
                file_name=f"sbar_{sbar_op}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",use_container_width=True)
    disclaimer()
    