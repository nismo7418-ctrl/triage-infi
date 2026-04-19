"""
================================================================================
  AKIR-IAO v18.0 — Pro Edition
  Développeur exclusif : Ismail Ibn-Daifa
  Urgences du Hainaut — Wallonie, Belgique
  Référence clinique  : FRENCH Triage SFMU V1.1 — Juin 2018
  Pharmacologie       : BCFI — Répertoire Commenté des Médicaments — Belgique
  RGPD                : UUID anonyme — aucun identifiant nominal collecté
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
.sbar-body { font-size:.82rem; color:var(--T); line-height:1.75; }
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
GLYC     = {"hs":54,"hm":70,"Hs":180,"Hs2":360}
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
  "Pediatrie":["Pediatrie - Fievre <= 3 mois"],
  "Peau":["Petechie / Purpura","Erytheme etendu"],
  "Gyneco":["Accouchement imminent","Complication grossesse T1/T2","Menorragie / Metrorragie"],
  "Metabolique":["Hypoglycemie","Hyperglycemie / Cetoacidose"],
  "Divers":["Renouvellement ordonnance","Examen administratif"],
}
MOTIFS_RAPIDES = ["Douleur thoracique / SCA","Dyspnee / insuffisance respiratoire",
                  "AVC / Deficit neurologique","Alteration de conscience / Coma",
                  "Traumatisme cranien","Hypotension arterielle","Tachycardie / tachyarythmie",
                  "Fievre","Douleur abdominale","Allergie / anaphylaxie","Hypoglycemie",
                  "Convulsions / EME","Pediatrie - Fievre <= 3 mois","Autre motif"]

# ══════════════════════════════════════════════════════════════════════════════
# MOTEUR CLINIQUE
# ══════════════════════════════════════════════════════════════════════════════

def calculer_news2(fr,spo2,o2,temp,pas,fc,gcs,bpco=False):
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

def n2_meta(s):
    if   s==0: return "Risque nul",    "n2-0", 0
    elif s<=4: return "Risque faible", "n2-1", int(s/12*100)
    elif s<=6: return "Risque modere", "n2-2", int(s/12*100)
    elif s<=8: return "Risque élevé",  "n2-3", int(s/12*100)
    else:      return "CRITIQUE",      "n2-5", min(int(s/12*100),100)

def calculer_gcs(y,v,m):
    try: return max(3,min(15,int(y)+int(v)+int(m))),[]
    except: return 15,["Erreur GCS"]

def calculer_qsofa(fr,gcs,pas):
    s=0; pos=[]; w=[]
    if fr is None: w.append("FR manquante")
    elif fr>=22: s+=1; pos.append(f"FR {fr}/min")
    if gcs is None: w.append("GCS manquant")
    elif gcs<15: s+=1; pos.append(f"GCS {gcs}/15")
    if pas is None: w.append("PAS manquante")
    elif pas<=100: s+=1; pos.append(f"PAS {pas}mmHg")
    return s,pos,w

def calculer_timi(age,nb_frcv,sten,aspi,trop,dst,cris):
    try:
        s=(int(age>=65)+int(nb_frcv>=3)+int(bool(sten))+int(bool(aspi))
           +int(bool(trop))+int(bool(dst))+int(cris>=2))
        return s,[]
    except Exception as e: return 0,[str(e)]

def evaluer_fast(f,a,s,t):
    sc=int(bool(f))+int(bool(a))+int(bool(s))+int(bool(t))
    if sc>=2: return sc,"FAST positif — AVC probable — Filiere Stroke",True
    if sc==1: return sc,"FAST partiel — Evaluation urgente",False
    return sc,"FAST negatif",False

def calculer_algoplus(v,r,p,ac,co):
    try:
        s=(int(bool(v))+int(bool(r))+int(bool(p))+int(bool(ac))+int(bool(co)))
        if   s>=4: return s,"Douleur intense — traitement IV urgent","danger",[]
        elif s>=2: return s,"Douleur probable — traitement à initier","warning",[]
        return s,"Douleur absente ou peu probable","success",[]
    except Exception as e: return 0,"Erreur","info",[str(e)]

def evaluer_cfs(sc):
    if sc<=3: return "Robuste","success",False
    if sc<=4: return "Vulnerable","warning",False
    if sc<=6: return "Fragile","warning",True
    if sc<=8: return "Tres fragile","danger",True
    return "Terminal","danger",True

def si(fc,pas): return round(fc/pas,2) if pas and pas>0 else 0.0

def sipa(fc,age):
    v=round(fc/max(1.0,float(age+1)*15+70),2)
    s=2.2 if age<=1 else (2.0 if age<=4 else (1.8 if age<=7 else 1.7))
    return v,f"SIPA {v} {'>' if v>s else '<='} {s} — {'Choc pediatrique probable' if v>s else 'Hemodynamique preservee'}",v>s

def mgdl_mmol(v): return round(v/18.016,1)

def french_triage(motif,det,fc,pas,spo2,fr,gcs,temp,age,n2,gl=None):
    fc=fc or 80; pas=pas or 120; spo2=spo2 or 98
    fr=fr or 16; gcs=gcs or 15; temp=temp or 37.0; n2=n2 or 0
    det=det or {}
    try:
        if n2>=9: return "M",f"NEWS2 {n2}>=9 — engagement vital","NEWS2 Tri M"
        if det.get("purpura"): return "1","PURPURA FULMINANS — Céfotriaxone 2 g IV","SPILF/SFP 2017"
        if motif=="Arret cardio-respiratoire": return "1","ACR confirme","FRENCH Tri 1"
        if motif=="Hypotension arterielle":
            if pas<=70: return "1",f"PAS {pas}<=70","FRENCH Tri 1"
            if pas<=90 or (pas<=100 and fc>100): return "2","Choc débutant","FRENCH Tri 2"
            if pas<=100: return "3B","PAS limite","FRENCH Tri 3B"
            return "4","PAS normale","FRENCH Tri 4"
        if motif=="Douleur thoracique / SCA":
            ecg=det.get("ecg","Normal"); doul=det.get("douleur","Atypique")
            if ecg=="Anormal typique SCA" or doul=="Typique (constrictive, irradiante)": return "1","SCA — ECG anormal ou douleur typique","FRENCH Tri 1"
            if fc>=120 or spo2<94: return "2","Douleur thoracique instable","FRENCH Tri 2"
            if doul=="Coronaire probable" or det.get("frcv",0)>=2: return "2","Douleur coronaire probable","FRENCH Tri 2"
            return "3A","Douleur atypique stable","FRENCH Tri 3A"
        if motif in("Tachycardie / tachyarythmie","Bradycardie / bradyarythmie","Palpitations"):
            if fc>=180 or fc<=30: return "1",f"FC {fc}bpm extreme","FRENCH Tri 1"
            if fc>=150 or fc<=40: return "2",f"FC {fc}bpm severe","FRENCH Tri 2"
            if det.get("tol_mal"): return "2","Arythmie mal tolérée","FRENCH Tri 2"
            return "3B",f"FC {fc} bpm — tolérée","FRENCH Tri 3B"
        if motif=="Hypertension arterielle":
            if pas>=220: return "2",f"PAS {pas}>=220","FRENCH Tri 2"
            if det.get("sf") or (pas>=180 and fc>100): return "2","HTA avec SF","FRENCH Tri 2"
            if pas>=180: return "3B","HTA sévère sans signe fonctionnel","FRENCH Tri 3B"
            return "4","HTA modérée","FRENCH Tri 4"
        if motif=="Allergie / anaphylaxie":
            if spo2<94 or pas<90 or gcs<15: return "1","Anaphylaxie sévère","FRENCH Tri 1"
            if det.get("dyspnee") or det.get("urticaire"): return "2","Allergie systemique","FRENCH Tri 2"
            return "3B","Réaction allergique localisée","FRENCH Tri 3B"
        if motif=="AVC / Deficit neurologique":
            d=det.get("delai",99)
            if d<=4.5: return "1",f"AVC {d}h — filiere Stroke","FRENCH Tri 1"
            if det.get("def_prog") or gcs<15: return "2","Déficit progressif ou GCS altéré","FRENCH Tri 2"
            return "2","Déficit neurologique — bilan urgent","FRENCH Tri 2"
        if motif=="Traumatisme cranien":
            if gcs<=8: return "1",f"TC grave GCS {gcs}","FRENCH Tri 1"
            if gcs<=12 or det.get("aod"): return "2",f"TC GCS {gcs} ou AOD","FRENCH Tri 2"
            if det.get("pdc"): return "3A","TC avec perte de conscience","FRENCH Tri 3A"
            return "4","TC bénin","FRENCH Tri 4"
        if motif=="Alteration de conscience / Coma":
            if gl and gl<GLYC["hs"]: return "2",f"Hypoglycemie {gl}mg/dl — Glucose 30%","FRENCH Tri 2"
            if gcs<=8: return "1",f"Coma GCS {gcs}","FRENCH Tri 1"
            if gcs<=13: return "2",f"Altération GCS {gcs}","FRENCH Tri 2"
            return "2","Altération légère","FRENCH Tri 2"
        if motif=="Convulsions / EME":
            if det.get("multi"): return "2","Crises multiples ou état de mal épileptique","FRENCH Tri 2"
            if det.get("conf"): return "2","Confusion post-critique","FRENCH Tri 2"
            return "3B","Convulsion récupérée","FRENCH Tri 3B"
        if motif=="Cephalee":
            if det.get("brutal"): return "1","Cephalee foudroyante — HSA","FRENCH Tri 1"
            if det.get("nuque") or det.get("fiev_ceph"): return "2","Signes méningés","FRENCH Tri 2"
            return "3B","Céphalée sans signe de gravité","FRENCH Tri 3B"
        if motif=="Malaise":
            if gl and gl<GLYC["hs"]: return "2",f"Malaise hypoglycémique {gl}mg/dl","FRENCH Tri 2"
            if n2>=2 or det.get("anom_vit"): return "2","Malaise avec anomalie vitale","FRENCH Tri 2"
            return "3B","Malaise récupéré","FRENCH Tri 3B"
        if motif in("Dyspnee / insuffisance respiratoire","Dyspnee / insuffisance cardiaque"):
            bp=det.get("bpco",False); cible=92 if bp else 95
            if spo2<(88 if bp else 91) or fr>=40: return "1",f"Detresse respi SpO2 {spo2}% FR {fr}","FRENCH Tri 1"
            if spo2<cible or fr>=30 or not det.get("parole",True): return "2",f"Dyspnée sévère SpO2 {spo2}%","FRENCH Tri 2"
            if det.get("orth") or det.get("tirage"): return "2","Orthopnée ou tirage","FRENCH Tri 2"
            return "3B",f"Dyspnée modérée SpO2 {spo2}%","FRENCH Tri 3B"
        if motif=="Douleur abdominale":
            sh=si(fc,pas)
            if pas<90 or sh>=1.0: return "2",f"Abdomen avec état de choc SI {sh}","FRENCH Tri 2"
            if det.get("grossesse") or det.get("geu"): return "2","Abdomen sur grossesse / GEU","FRENCH Tri 2"
            if det.get("defense"): return "2","Abdomen chirurgical","FRENCH Tri 2"
            if det.get("tol_mal"): return "3A","Douleur mal toleree","FRENCH Tri 3A"
            return "3B","Douleur toleree","FRENCH Tri 3B"
        if motif=="Fievre":
            if det.get("purpura"): return "1","Fievre + purpura — Ceftriaxone 2g","FRENCH Tri 1"
            if temp>=40 or temp<=35.2 or det.get("conf"): return "2",f"Fièvre avec critère de gravité T {temp}C","FRENCH Tri 2"
            if det.get("tol_mal") or pas<100 or si(fc,pas)>=1.0: return "3B","Fièvre mal tolérée","FRENCH Tri 3B"
            return "5","Fièvre bien tolérée","FRENCH Tri 5"
        if motif=="Pediatrie - Fievre <= 3 mois": return "2","Fièvre nourrisson <=3 mois","FRENCH Pediatrie Tri 2"
        if motif=="Petechie / Purpura":
            if det.get("neff"): return "1","Purpura non effaçable — Ceftriaxone 2g IV","SPILF/SFP 2017"
            if temp>=38.0: return "2","Purpura fébrile — suspicion fulminans","FRENCH Tri 2"
            return "3B","Pétéchies — bilan hémostase","FRENCH Tri 3B"
        if motif in("Traumatisme thorax/abdomen/rachis cervical","Traumatisme bassin/hanche/femur"):
            if det.get("pen") or det.get("cin")=="Haute": return "1","Traumatisme penetrant haute cinetique","FRENCH Tri 1"
            if si(fc,pas)>=1.0 or spo2<94: return "2","Traumatisme avec choc","FRENCH Tri 2"
            return "2","Traumatisme axial — evaluation urgente","FRENCH Tri 2"
        if motif=="Traumatisme membre / epaule":
            if det.get("isch"): return "1","Ischémie distale","FRENCH Tri 1"
            if det.get("imp") and det.get("deform"): return "2","Fracture déplacée","FRENCH Tri 2"
            if det.get("imp"): return "3A","Impotence fonctionnelle totale","FRENCH Tri 3A"
            if det.get("deform"): return "3A","Déformation visible","FRENCH Tri 3A"
            return "4","Traumatisme distal modéré","FRENCH Tri 4"
        if motif=="Hypoglycemie":
            if gl and gl<GLYC["hs"]: return "2",f"Hypoglycémie sévère {gl}mg/dl","FRENCH Tri 2"
            if gcs<15: return "2",f"Hypoglycémie avec GCS {gcs}","FRENCH Tri 2"
            return "3B","Hypoglycémie légère","FRENCH Tri 3B"
        if motif=="Hyperglycemie / Cetoacidose":
            if det.get("ceto") or gcs<15: return "2","Cétoacidose ou GCS altéré","FRENCH Tri 2"
            return "4","Hyperglycémie tolérée","FRENCH Tri 4"
        if motif in("Renouvellement ordonnance","Examen administratif"): return "5","Non urgent","FRENCH Tri 5"
        if n2>=7: return "2",f"NEWS2 {n2}>=7","NEWS2 Tri 2"
        if n2>=5: return "3A",f"NEWS2 {n2}>=5","NEWS2 Tri 3A"
        return "3B",f"Evaluation standard — {motif}","FRENCH Tri 3B"
    except Exception as e:
        return "2",f"Erreur moteur : {e}","Securite Tri 2"

def verifier_coherence(fc,pas,spo2,fr,gcs,temp,eva,motif,atcd,det,n2,gl=None):
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

def build_sbar(age,motif,cat,atcd,alg,o2,temp,fc,pas,spo2,fr,gcs,eva,n2,niv,just,crit,op="IAO",gl=None):
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
_CI_A=["Ulcere gastro-duodenal","Insuffisance renale chronique","Insuffisance hepatique",
       "Grossesse en cours","Chimiotherapie en cours"]

def ci_ains(atcd): return [c for c in _CI_A if c in atcd]

def paracetamol(poids):
    if poids<=0: return None,"Poids invalide"
    if poids>=50: return {"dose_g":1.0,"vol":"100ml NaCl 0.9% sur 15min","freq":"Toutes les 6h (max 4g/24h)","ref":"BCFI — Paracetamol IV"},None
    dg=min(round(15*poids/1000,2),1.0)
    return {"dose_g":dg,"vol":f"{dg*1000:.0f}mg dans 100ml NaCl 0.9%","freq":"Toutes les 6h","ref":"BCFI — Paracetamol IV"},None

def ketorolac(poids,atcd):
    ci=ci_ains(atcd)
    if ci: return None,f"Contre-indique : {', '.join(ci)}"
    d=15.0 if poids<50 else 30.0
    return {"dose_mg":d,"admin":"IV lent 15s","freq":"Toutes 6h — max 5j","ref":"BCFI — Ketorolac (Taradyl)"},None

def tramadol(poids,atcd,age):
    als=[]
    if "Epilepsie" in atcd: als.append("CONTRE-INDIQUE — Epilepsie (seuil epileptogene)")
    if "IMAO (inhibiteurs MAO)" in atcd: als.append("CONTRE-INDICATION ABSOLUE — SYNDROME SEROTONINERGIQUE FATAL avec IMAO")
    if "Antidepresseurs ISRS/IRSNA" in atcd: als.append("INTERACTION MAJEURE — ISRS/IRSNA — risque serotoninergique")
    d=100.0 if poids>=50 else round(1.5*poids,0)
    return {"dose_mg":d,"admin":f"{d:.0f}mg dans 100ml NaCl 0.9% — IV 30min","freq":"Toutes 6h (max 400mg/24h)","alertes":als,"ref":"BCFI — Tramadol"},None

def piritramide(poids,age,atcd):
    red=(age>=70 or "Insuffisance renale chronique" in atcd or "Insuffisance hepatique" in atcd)
    f=0.5 if red else 1.0
    dmin=min(round(0.03*poids*f,2),(3.0 if poids<70 else 6.0)*f)
    dmax=min(round(0.05*poids*f,2),(3.0 if poids<70 else 6.0)*f)
    return {"dmin":dmin,"dmax":dmax,"admin":"IV lent 1-2min — titrer si EVA>3 apres 15min","note":"Dose -50% si age>=70/IRC/IH" if red else "","ref":"BCFI — Piritramide (Dipidolor)"},None

def morphine(poids,age):
    f=0.5 if age>=70 else 1.0
    return {"dmin":min(round(0.05*poids*f,1),2.5),"dmax":min(round(0.10*poids*f,1),5.0),
            "admin":"IV lent 2-3min — titrer par paliers 2mg/5-10min","ref":"BCFI — Morphine IV"},None

def naloxone(poids,age,dep=False):
    als=[]
    if dep:
        d=0.04; a="0.04mg IV/2min — titration douce"; n="Dependance — objectif : ventilation, pas levee totale"
        als.append("Risque sevrage si surdosage")
    elif age<18:
        d=min(round(0.01*poids,3),0.4); a=f"{d}mg IV (0.01mg/kg)"; n=f"Ped : {d}mg pour {poids}kg"
    else:
        d=0.4; a="0.4mg IV — repeter 2-3min (max 10mg)"; n="Si pas de reponse a 10mg : reconsiderer"
    return {"dose":d,"admin":a,"note":n,"alertes":als,"surv":"Monitor SpO2+FR — demi-vie courte 30-90min","ref":"BCFI — Naloxone (Narcan)"},None

def adrenaline(poids):
    if poids<=0: return None,"Poids invalide"
    d=0.5 if poids>=30 else min(round(0.01*poids,3),0.5)
    n="0.5ml sol 1mg/ml" if poids>=30 else f"0.01mg/kg = {d}mg"
    return {"dose_mg":d,"voie":"IM face antero-lat cuisse","note":n,"rep":"Repeter 5-15min si pas d'amelioration","ref":"BCFI — Adrenaline Sterop 1mg/ml"},None

def glucose(poids,gl=None):
    if gl is None: return None,"Glycémie non mesurée — protocole désactivé"
    dg=min(round(0.3*poids,1),15.0); dm=round(dg/0.3,0)
    return {"dose_g":dg,"vol":f"{dm:.0f}ml Glucose 30% IV lent 5min","ctrl":"Glycémie de contrôle à 15 min","ref":"BCFI — Glucose 30% (Glucosie)"},None

def ceftriaxone(poids,age):
    dg=2.0 if age>=18 else min(round(0.1*poids,1),2.0)
    n="Ne pas attendre le medecin si purpura" if age>=18 else f"100mg/kg = {dg*1000:.0f}mg"
    return {"dose_g":dg,"admin":"IV 3-5min ou IM si VVP impossible","note":n,"ref":"BCFI — Ceftriaxone — SPILF 2017"},None

def protocole_eva(eva,poids,age,atcd,gl=None):
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
# PERSISTANCE
# ══════════════════════════════════════════════════════════════════════════════
RF="akir_reg.json"; EF="akir_errors.log"

def _load(f):
    if os.path.exists(f):
        try:
            with open(f,"r",encoding="utf-8") as fp: return json.load(fp)
        except: return []
    return []

def _save(f,d):
    try:
        with open(f,"w",encoding="utf-8") as fp: json.dump(d,fp,ensure_ascii=False,indent=2)
    except Exception as e:
        try:
            with open(EF,"a") as fe: fe.write(f"[{datetime.now()}] {e}\n")
        except: pass

def enreg(d):
    uid=str(uuid.uuid4())[:8].upper()
    r=_load(RF)
    r.insert(0,{"uid":uid,"heure":datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "motif":d.get("motif",""),"cat":d.get("cat",""),"niv":d.get("niv",""),
                "n2":d.get("n2",0),"fc":d.get("fc"),"pas":d.get("pas"),
                "spo2":d.get("spo2"),"fr":d.get("fr"),"temp":d.get("temp"),
                "gcs":d.get("gcs"),"op":d.get("op","IAO")})
    _save(RF,r[:500]); return uid

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
            st.download_button("Télécharger le registre CSV",data=out.getvalue(),
                file_name=f"akir_reg_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",use_container_width=True)
            AL(f"RGPD : CSV anonyme — UUID uniquement — {len(reg)} enregistrements","info")
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