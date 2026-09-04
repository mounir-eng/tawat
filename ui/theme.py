# -*- coding: utf-8 -*-
"""Th\u00e8me visuel de l'application (jetons de design + CSS inject\u00e9 dans Streamlit).

v4 : inspir\u00e9 des apps BTP modernes \u2014 fond gris clair, cartes blanches flottantes,
pastilles pastel, bandeau de KPI, tuiles d'actions, barre d'onglets ambre.
Interface bilingue : arabe d'abord, fran\u00e7ais entre parenth\u00e8ses.
"""
import streamlit as st

JETONS = {
    "encre": "#182230",
    "texte": "#1F2A37",
    "gris": "#667085",
    "canvas": "#FFFFFF",
    "doux": "#F7F9FA",
    "page": "#F2F4F7",
    "surface2": "#EDF0F2",
    "bordure": "#E8EBEE",
    "bleu": "#2783DE",
    "bleu_doux": "#E9F2FD",
    "vert": "#46A171",
    "vert_doux": "#EAF4EE",
    "ambre": "#E8A33D",
    "ambre_fonce": "#9C5A21",
    "ambre_doux": "#FDF3E3",
    "rouge": "#E56458",
    "rouge_doux": "#FCEBE9",
}

COULEURS_PILULE = {
    "blue": ("#E9F2FD", "#1A5FA5"),
    "green": ("#EAF4EE", "#2F7452"),
    "amber": ("#FDF3E3", "#9C5A21"),
    "red": ("#FCEBE9", "#B24338"),
    "grey": ("#EDF0F2", "#667085"),
    "ink": ("#182230", "#FFFFFF"),
}

CSS = """
<style>
:root{
  --encre:#182230; --txt:#1F2A37; --gris:#667085; --page:#F2F4F7; --doux:#F7F9FA;
  --surf2:#EDF0F2; --bord:#E8EBEE; --bleu:#2783DE; --bleu-d:#E9F2FD;
  --vert:#46A171; --vert-d:#EAF4EE; --ambre:#E8A33D; --ambre-f:#9C5A21; --ambre-d:#FDF3E3;
  --rouge:#E56458; --rouge-d:#FCEBE9;
  --sh:0 1px 2px rgba(16,24,40,.05), 0 8px 20px rgba(16,24,40,.04);
}
html, body, [class*="css"]{
  font-family:"Segoe UI","Helvetica Neue",Tahoma,Arial,sans-serif;
  -webkit-font-smoothing:antialiased;
}
.stApp{ background:var(--page); color:var(--txt); }
#MainMenu, footer, header [data-testid="stStatusWidget"]{ visibility:hidden; }
[data-testid="stHeader"]{ background:transparent; height:0; }
[data-testid="stDecoration"]{ display:none; }
[data-testid="stSidebarCollapsedControl"]{ top:12px; }

/* --- largeur de lecture confortable, respiration en bas pour la barre --- */
.block-container{ padding:14px 18px 138px !important; max-width:1080px; }

/* --- typographie --- */
h1,h2,h3,h4{ color:var(--encre); letter-spacing:-.015em; font-weight:750; }
h1{ font-size:1.6rem !important; }
h2{ font-size:1.24rem !important; margin:.2rem 0 .4rem !important; }
h3{ font-size:1.05rem !important; }
p, li, label, .stMarkdown{ font-size:15px; }

/* --- cartes natives (st.container(border=True)) : blanches, flottantes --- */
div[data-testid="stVerticalBlockBorderWrapper"]{
  background:#fff; border-radius:16px; border:1px solid var(--bord);
  box-shadow:var(--sh);
}

/* --- boutons --- */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button, .stLinkButton > a{
  border-radius:12px; border:1px solid var(--bord); background:#fff; color:var(--txt);
  font-weight:650; font-size:14.5px; min-height:44px; padding:.45rem .9rem;
  transition:transform .05s ease, box-shadow .15s ease, background .15s ease;
  box-shadow:0 1px 1px rgba(16,24,40,.03);
}
.stButton > button:hover, .stDownloadButton > button:hover, .stLinkButton > a:hover{
  border-color:#D3D8DD; background:#FCFDFD; color:var(--encre);
}
.stButton > button:active{ transform:translateY(1px); }
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"]{
  background:var(--bleu); border-color:var(--bleu); color:#fff;
  box-shadow:0 4px 14px rgba(39,131,222,.28);
}
.stButton > button[kind="primary"]:hover{ background:#1F6FBF; border-color:#1F6FBF; color:#fff; }

/* --- tuiles d'actions rapides (accueil) --- */
.st-key-tuiles .stButton > button{
  background:#fff; border:1px solid var(--bord); border-radius:14px; box-shadow:var(--sh);
  min-height:96px; white-space:pre-line; line-height:1.35; font-size:13.5px;
  font-weight:650; color:var(--txt); padding:12px 6px 10px;
}
.st-key-tuiles .stButton > button p::first-line{ font-size:26px; line-height:1.7; }
.st-key-tuiles .stButton > button:hover{
  border-color:#CFD8E3; transform:translateY(-1px); box-shadow:0 6px 16px rgba(16,24,40,.08);
}

/* --- champs de saisie --- */
[data-baseweb="input"], [data-baseweb="select"] > div, .stTextArea textarea, .stNumberInput input{
  border-radius:12px !important; border-color:var(--bord) !important; font-size:15px !important;
  background:#fff !important;
}
[data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within{
  border-color:var(--bleu) !important; box-shadow:0 0 0 3px rgba(39,131,222,.14) !important;
}
.stTextInput label, .stNumberInput label, .stSelectbox label, .stDateInput label,
.stTextArea label, .stRadio label, .stFileUploader label{
  font-size:13px !important; font-weight:650 !important; color:var(--gris) !important;
}
.stNumberInput input{ font-variant-numeric:tabular-nums; font-weight:600; }

/* --- onglets --- */
.stTabs [data-baseweb="tab-list"]{ gap:4px; border-bottom:1px solid var(--bord); }
.stTabs [data-baseweb="tab"]{
  height:42px; padding:0 14px; border-radius:10px 10px 0 0; font-weight:650; font-size:14px;
  background:transparent;
}
.stTabs [aria-selected="true"]{ background:#fff; color:var(--encre) !important;
  border:1px solid var(--bord); border-bottom-color:#fff; }

/* --- pilules de filtre --- */
[data-testid="stPills"] button, [data-testid="stSegmentedControl"] button{
  border-radius:999px !important; font-size:13.5px !important; font-weight:650 !important;
  min-height:38px; background:#fff;
}

/* --- expander : d\u00e9tails priv\u00e9s artisan --- */
[data-testid="stExpander"]{ border:none; }
[data-testid="stExpander"] details{
  border:1px dashed var(--bord); border-radius:12px; background:var(--doux);
}
[data-testid="stExpander"] summary{ font-size:13px; font-weight:650; color:var(--ambre-f); }

/* --- barre de navigation fixe : ic\u00f4ne au-dessus du libell\u00e9, actif ambre --- */
.st-key-navbar{
  position:fixed; left:0; right:0; bottom:0; z-index:999;
  background:rgba(255,255,255,.98); border-top:1px solid var(--bord);
  padding:6px max(12px, calc(50vw - 540px)) 8px;
  box-shadow:0 -6px 20px rgba(16,24,40,.06);
}
.st-key-navbar .stButton > button{
  width:100%; border:none; background:transparent; box-shadow:none;
  color:var(--gris); font-size:11px; font-weight:600; min-height:54px;
  padding:4px 0; line-height:1.3; white-space:pre-line; border-radius:12px;
}
.st-key-navbar .stButton > button p::first-line{ font-size:20px; line-height:1.5; }
.st-key-navbar .stButton > button:hover{ background:var(--doux); color:var(--encre); }
.st-key-navbar .stButton > button[kind="primary"]{
  background:transparent; color:var(--ambre); box-shadow:none; font-weight:750;
}
.st-key-navbar [data-testid="stHorizontalBlock"]{ gap:2px; }

/* --- barre d'action collante en bas d'\u00e9diteur --- */
.st-key-barre_action{
  position:sticky; bottom:96px; z-index:50; background:#fff;
  border:1px solid var(--bord); border-radius:14px; padding:10px 12px;
  box-shadow:0 -4px 18px rgba(16,24,40,.07);
}

/* =====================  blocs HTML maison  ===================== */

/* --- en-t\u00eate de salutation --- */
.greet{ display:flex; align-items:center; gap:12px; margin:4px 0 14px; }
.greet .logo{ width:46px; height:46px; border-radius:14px; background:#fff;
  border:1px solid var(--bord); box-shadow:var(--sh); display:flex; align-items:center;
  justify-content:center; font-size:22px; flex:0 0 46px; }
.greet .app{ font-size:17px; font-weight:800; color:var(--encre); letter-spacing:-.01em; }
.greet .salut{ font-size:13px; color:var(--gris); margin-top:1px; }
.greet .cloche{ margin-left:auto; position:relative; width:42px; height:42px;
  border-radius:12px; background:#fff; border:1px solid var(--bord); display:flex;
  align-items:center; justify-content:center; font-size:18px; }
.greet .badge{ position:absolute; top:-5px; right:-5px; min-width:18px; height:18px;
  border-radius:9px; background:var(--rouge); color:#fff; font-size:10.5px; font-weight:750;
  display:flex; align-items:center; justify-content:center; padding:0 4px; }

/* --- bandeau de 3 KPI --- */
.band{ background:#fff; border:1px solid var(--bord); border-radius:16px; box-shadow:var(--sh);
  padding:12px; display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-bottom:6px; }
.kpi2{ background:var(--doux); border-radius:12px; padding:12px 13px; min-width:0; }
.kpi2.warn{ background:var(--ambre-d); }
.kpi2 .top{ display:flex; align-items:center; gap:7px; }
.kpi2 .ic{ width:26px; height:26px; border-radius:8px; display:flex; align-items:center;
  justify-content:center; font-size:14px; background:#fff; border:1px solid var(--bord);
  flex:0 0 26px; }
.kpi2 .lab{ font-size:11px; font-weight:700; color:var(--gris); }
.kpi2 .val{ font-size:21px; font-weight:800; color:var(--encre); margin-top:6px;
  font-variant-numeric:tabular-nums; letter-spacing:-.01em; }
.kpi2 .val small{ font-size:12px; color:var(--gris); font-weight:650; margin-left:3px; }
.kpi2 .cap{ font-size:11.5px; color:var(--gris); margin-top:2px; }
.kpi2.warn .lab, .kpi2.warn .cap{ color:var(--ambre-f); }
.kpi2 .lien{ font-size:12.5px; font-weight:700; color:var(--ambre-f); margin-top:6px; }

/* --- h\u00e9ros encre (KPI principal d'une page) --- */
.hero{ background:linear-gradient(155deg,#182230 0%,#243447 100%); color:#fff;
  border-radius:16px; padding:18px 18px 16px; box-shadow:0 10px 24px rgba(24,34,48,.20); }
.hero .lbl{ font-size:12px; color:rgba(255,255,255,.62); font-weight:650; }
.hero .val{ font-size:30px; font-weight:800; letter-spacing:-.02em; margin-top:2px;
  font-variant-numeric:tabular-nums; }
.hero .val small{ font-size:14px; opacity:.66; margin-left:5px; font-weight:600; }
.hero .split{ display:flex; gap:10px; margin-top:14px; }
.hero .split div{ flex:1; background:rgba(255,255,255,.09); border:1px solid rgba(255,255,255,.14);
  border-radius:10px; padding:8px 11px; }
.hero .split .k{ font-size:11.5px; color:rgba(255,255,255,.66); font-weight:600; }
.hero .split .v{ font-size:16px; font-weight:700; margin-top:1px; font-variant-numeric:tabular-nums; }

/* --- titre de section (pas de majuscules : respect de l'arabe) --- */
.sec{ display:flex; align-items:center; gap:8px; font-size:14.5px; font-weight:750;
  color:var(--encre); margin:20px 0 8px; }
.sec .lien{ margin-left:auto; font-size:12.5px; font-weight:650; color:var(--gris); }

/* --- barre de progression (avancement chantier) --- */
.prog{ height:8px; border-radius:99px; background:var(--surf2); overflow:hidden; }
.prog i{ display:block; height:100%; border-radius:99px;
  background:linear-gradient(90deg,#2783DE,#5AA2EC); }

.pill{ display:inline-flex; align-items:center; gap:5px; border-radius:999px; padding:4px 10px;
  font-size:12.5px; font-weight:650; white-space:nowrap; }
.money{ font-variant-numeric:tabular-nums; font-weight:750; letter-spacing:-.01em; }
.muted{ color:var(--gris); }
.xs{ font-size:12px; } .sm{ font-size:13px; }

.bar{ height:8px; border-radius:99px; background:var(--surf2); overflow:hidden; display:flex; }
.bar i{ display:block; height:100%; }
.leg{ display:flex; gap:12px; flex-wrap:wrap; margin-top:7px; font-size:11.5px; color:var(--gris); }
.leg span{ display:flex; align-items:center; gap:5px; }
.leg b{ width:8px; height:8px; border-radius:3px; display:inline-block; }

.row{ display:flex; gap:12px; align-items:center; }
.av{ width:42px; height:42px; border-radius:12px; display:flex; align-items:center;
  justify-content:center; font-weight:750; font-size:14px; flex:0 0 42px; }
.num{ font-size:11.5px; color:var(--gris); font-weight:650; }
.nm{ font-size:15.5px; font-weight:700; color:var(--encre); }
.ds{ font-size:12.5px; color:var(--gris); margin-top:1px; }
.step{ display:flex; align-items:center; gap:4px; margin-top:8px; }
.step i{ height:4px; flex:1; border-radius:99px; background:var(--surf2); }
.step i.on{ background:var(--bleu); }
.step span{ font-size:11px; color:var(--gris); margin-left:6px; white-space:nowrap; }

/* --- 3 colonnes de stats dans une carte chantier --- */
.st3{ display:grid; grid-template-columns:repeat(3,1fr); gap:8px; margin-top:10px; }
.st3 .l{ font-size:11.5px; color:var(--gris); font-weight:600; }
.st3 .v{ font-size:14.5px; font-weight:750; color:var(--encre); margin-top:2px;
  font-variant-numeric:tabular-nums; }

.empty{ text-align:center; padding:28px 18px; border:1px dashed var(--bord);
  border-radius:16px; background:#fff; }
.empty .ic{ font-size:30px; } .empty .t{ font-weight:700; margin-top:8px; font-size:15.5px; }
.empty .s{ color:var(--gris); font-size:13.5px; margin-top:3px; }

.msg{ background:var(--doux); border:1px solid var(--bord); border-radius:12px;
  padding:12px 13px; font-size:14px; line-height:1.6; white-space:pre-wrap; }
.tag{ display:inline-block; background:var(--surf2); color:var(--gris); border-radius:8px;
  padding:2px 8px; font-size:11.5px; font-weight:650; margin-right:5px; }

@media (max-width: 640px){
  .block-container{ padding:10px 12px 146px !important; }
  h1{ font-size:1.35rem !important; }
  .hero .val{ font-size:26px; }
  .band{ grid-template-columns:1fr 1fr; }
  .kpi2 .val{ font-size:18px; }
}
</style>
"""


# ==========================================================================
#  v8 — couche visuelle moderne + correctif largeur des fenetres
# ==========================================================================
CSS_V8 = """
<style>
:root{
  --bleu:#2D5BFF; --bleu-d:#EEF3FF; --indigo:#1B2559;
  --grad:linear-gradient(135deg,#2D5BFF 0%,#6E8BFF 100%);
  --grad-nuit:linear-gradient(135deg,#101935 0%,#1B2559 55%,#26356B 100%);
  --sh:0 1px 2px rgba(16,24,40,.04),0 10px 26px rgba(16,24,40,.06);
  --sh-fort:0 18px 44px rgba(16,24,40,.14);
  --r:18px;
}
.stApp{ background:
  radial-gradient(1100px 460px at 12% -12%, #E9F0FF 0%, rgba(233,240,255,0) 62%),
  radial-gradient(900px 420px at 105% 0%, #E6FAF5 0%, rgba(230,250,245,0) 58%),
  var(--page); }

/* ---------- boutons : plus doux, plus vivants ---------- */
.stButton>button, .stDownloadButton>button, .stLinkButton>a{
  border-radius:14px !important; font-weight:700 !important; letter-spacing:-.01em;
  transition:transform .12s ease, box-shadow .18s ease, background .18s ease,
             border-color .18s ease !important; }
.stButton>button:hover, .stDownloadButton>button:hover, .stLinkButton>a:hover{
  transform:translateY(-1px); box-shadow:0 8px 18px rgba(16,24,40,.10) !important; }
.stButton>button[kind="primary"], .stDownloadButton>button[kind="primary"],
.stLinkButton>a[kind="primary"]{
  background:var(--grad) !important; border:0 !important; color:#fff !important;
  box-shadow:0 10px 24px rgba(45,91,255,.28) !important; }

/* ---------- FENETRES : jamais toute la largeur de l'ecran ---------- */
[data-testid="stDialog"] div[role="dialog"],
[data-testid="stModal"] div[role="dialog"]{
  max-width:min(560px,94vw) !important; width:min(560px,94vw) !important;
  border-radius:20px !important; border:1px solid var(--bord) !important;
  box-shadow:var(--sh-fort) !important; margin:6vh auto 0 !important;
  max-height:86vh !important; }
[data-testid="stDialog"] div[role="dialog"] .block-container,
[data-testid="stModal"] div[role="dialog"] .block-container{
  padding:6px 2px 2px !important; max-width:100% !important; }

/* ---------- cartes de la page Devis ---------- */
.st-key-dx_client, .st-key-dx_panel, .st-key-dx_remcard, .st-key-dx_envoi{
  background:#fff; border:1px solid var(--bord); border-radius:var(--r);
  padding:14px 15px 6px; box-shadow:var(--sh); margin-bottom:12px; }
.st-key-dx_panel{ border-color:#CFDBFF; box-shadow:0 0 0 4px #F2F6FF, var(--sh); }

/* ---------- rail de progression ---------- */
.dx-rail{ display:flex; align-items:center; gap:8px; background:#fff;
  border:1px solid var(--bord); border-radius:16px; padding:8px 10px;
  box-shadow:var(--sh); margin:0 0 14px; }
.dx-st{ display:flex; align-items:center; gap:7px; padding:6px 10px; border-radius:12px;
  background:var(--doux); flex:1; min-width:0; }
.dx-st i{ width:22px; height:22px; border-radius:50%; background:#E4E8EE; color:#6B7688;
  font-style:normal; font-size:12px; font-weight:800; display:grid; place-items:center;
  flex:0 0 22px; }
.dx-st b{ font-size:13.5px; font-weight:750; color:var(--gris); white-space:nowrap; }
.dx-st span{ font-size:11px; color:#98A2B3; white-space:nowrap; overflow:hidden;
  text-overflow:ellipsis; }
.dx-st.on{ background:var(--bleu-d); box-shadow:inset 0 0 0 1px #CBD9FF; }
.dx-st.on i{ background:var(--grad); color:#fff; }
.dx-st.on b{ color:var(--indigo); }
.dx-st.ok i{ background:#DFF3E7; color:#2E8B57; }
.dx-st.ok b{ color:#46A171; }
.dx-rail-tot{ margin-left:auto; text-align:right; padding:2px 12px 2px 14px;
  border-left:1px dashed var(--bord); }
.dx-rail-tot span{ display:block; font-size:10.5px; color:var(--gris); font-weight:650; }
.dx-rail-tot b{ font-size:17px; font-weight:800; color:var(--indigo);
  font-variant-numeric:tabular-nums; }
.dx-rail-tot small{ font-size:10px; color:var(--gris); margin-left:3px; font-weight:700; }

/* ---------- petits titres numerotes ---------- */
.dx-lab{ display:flex; align-items:center; gap:9px; margin:16px 2px 8px;
  font-size:15px; font-weight:800; color:var(--encre); }
.dx-lab i{ width:24px; height:24px; border-radius:8px; background:var(--grad); color:#fff;
  font-style:normal; font-size:12.5px; font-weight:800; display:grid; place-items:center;
  flex:0 0 24px; box-shadow:0 4px 10px rgba(45,91,255,.30); }
.dx-lab small{ font-size:11.5px; font-weight:600; color:#98A2B3; margin-left:auto; }

/* ---------- tuiles (batiments, modes, pieces) ---------- */
.st-key-dx_bats .stButton>button, .st-key-dx_pcs .stButton>button,
.st-key-dx_modes .stButton>button{
  background:#fff !important; border:1.5px solid var(--bord) !important;
  color:var(--encre) !important; border-radius:16px !important;
  min-height:104px; padding:12px 8px !important; line-height:1.35;
  box-shadow:0 1px 2px rgba(16,24,40,.04) !important; }
.st-key-dx_bats .stButton>button p:first-child,
.st-key-dx_pcs .stButton>button p:first-child,
.st-key-dx_modes .stButton>button p:first-child{ font-size:26px !important; margin:0 0 2px; }
.st-key-dx_bats .stButton>button:hover, .st-key-dx_pcs .stButton>button:hover,
.st-key-dx_modes .stButton>button:hover{
  border-color:#B9C9FF !important; background:#FCFDFF !important;
  transform:translateY(-2px); box-shadow:0 12px 24px rgba(16,24,40,.10) !important; }
.st-key-dx_bats .stButton>button[kind="primary"],
.st-key-dx_pcs .stButton>button[kind="primary"],
.st-key-dx_modes .stButton>button[kind="primary"]{
  background:linear-gradient(180deg,#F4F8FF,#EAF1FF) !important;
  border:1.5px solid var(--bleu) !important; color:var(--indigo) !important;
  box-shadow:0 10px 22px rgba(45,91,255,.18) !important; }
.st-key-dx_modes .stButton>button{ min-height:120px; }
.dx-modehelp{ font-size:11.5px; color:var(--gris); line-height:1.55; padding:6px 6px 0;
  text-align:center; }
.st-key-dx_icones .stButton>button{ min-height:0; padding:6px 0 !important;
  font-size:19px !important; border-radius:12px !important; }
@media (max-width:640px){
  .st-key-dx_bats [data-testid="column"], .st-key-dx_pcs [data-testid="column"]{
    min-width:46% !important; }
  .dx-st span{ display:none; }
}

/* ---------- entete du panneau + icône personnalisable ---------- */
.dx-phead{ display:flex; align-items:center; gap:10px; margin:0 0 10px; }
.dx-phead b{ font-size:16.5px; font-weight:800; color:var(--indigo); }
.dx-phead span{ font-size:11.5px; font-weight:700; color:var(--bleu);
  background:var(--bleu-d); border-radius:999px; padding:3px 10px; }
.dx-icobox{ width:56px; height:56px; border-radius:16px; display:grid; place-items:center;
  font-size:27px; background:linear-gradient(180deg,#F7FAFF,#EEF3FF);
  border:1.5px solid #D9E2FF; margin-top:22px; }
.dx-icobox.vide{ background:#fff; border:2px dashed #C6CFDD; color:#AEB8C8;
  font-size:24px; font-weight:700; }
.dx-fix{ font-size:11.5px; color:var(--gris); font-weight:650; margin-top:34px;
  text-align:center; }
.dx-hint{ background:#FFF8EC; border:1px solid #FBE3BE; color:#8A5A16;
  border-radius:12px; padding:9px 12px; font-size:12.5px; line-height:1.6;
  margin:10px 0 6px; }
.dx-note{ background:var(--bleu-d); border:1px solid #CBD9FF; color:#1E3A8A;
  border-radius:12px; padding:10px 12px; font-size:12.5px; margin:10px 0 2px; }

/* ---------- total du panneau ---------- */
.dx-tot{ display:flex; align-items:center; gap:12px; flex-wrap:wrap;
  background:var(--grad-nuit); color:#fff; border-radius:14px;
  padding:11px 14px; margin:10px 0 4px; box-shadow:0 12px 26px rgba(16,25,53,.22); }
.dx-tot b{ font-size:19px; font-weight:800; font-variant-numeric:tabular-nums; }
.dx-tot small{ font-size:10.5px; opacity:.75; margin-left:4px; }
.dx-tot span{ font-size:11.5px; color:#C7D2F0; margin-left:auto; }

/* ---------- cartes pièce ---------- */
.dx-piece{ display:flex; align-items:center; gap:12px; background:#fff;
  border:1px solid var(--bord); border-left:4px solid #D9E2FF; border-radius:16px;
  padding:11px 13px; box-shadow:var(--sh); margin:8px 0 2px; }
.dx-piece .ico{ width:44px; height:44px; border-radius:13px; display:grid;
  place-items:center; font-size:22px; background:linear-gradient(180deg,#F7FAFF,#EDF2FF);
  border:1px solid #E2E9FF; flex:0 0 44px; }
.dx-piece .mid{ min-width:0; }
.dx-piece .nm{ font-size:14.5px; font-weight:750; color:var(--encre);
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.dx-piece .ds{ font-size:11.5px; color:var(--gris); margin-top:2px; }
.dx-piece .tot{ margin-left:auto; font-size:15.5px; font-weight:800; color:var(--indigo);
  font-variant-numeric:tabular-nums; white-space:nowrap; }
.dx-piece .tot small{ font-size:9.5px; color:var(--gris); margin-left:3px; }

/* ---------- bandeau d'etage ---------- */
.dx-flr{ display:flex; align-items:center; gap:8px; margin:16px 0 2px;
  padding:7px 12px; border-radius:12px; background:var(--surf2);
  border:1px dashed var(--bord); }
.dx-flr b{ font-size:13.5px; font-weight:800; color:var(--encre); }
.dx-flr span{ margin-left:auto; font-size:12px; font-weight:750; color:var(--gris);
  font-variant-numeric:tabular-nums; }

/* ---------- tableau du resume ---------- */
.dx-grp{ background:#fff; border:1px solid var(--bord); border-radius:16px;
  overflow:hidden; box-shadow:var(--sh); margin:10px 0; }
.dx-grp .gh{ display:flex; align-items:center; gap:8px; padding:10px 13px;
  background:linear-gradient(180deg,#FBFCFE,#F4F7FB); border-bottom:1px solid var(--bord); }
.dx-grp .gh b{ font-size:13.5px; font-weight:800; color:var(--indigo); }
.dx-grp .gh span{ margin-left:auto; font-size:12.5px; font-weight:750; color:var(--bleu);
  font-variant-numeric:tabular-nums; }
.dx-tbl{ width:100%; border-collapse:collapse; }
.dx-tbl td{ padding:8px 13px; font-size:12.5px; color:var(--txt);
  border-top:1px solid #F2F4F7; }
.dx-tbl tr:first-child td{ border-top:0; }
.dx-tbl tr:hover td{ background:#FAFBFD; }
.dx-tbl td:nth-child(2), .dx-tbl td:nth-child(3){ color:var(--gris); text-align:right;
  white-space:nowrap; font-variant-numeric:tabular-nums; }
.dx-tbl td:last-child{ text-align:right; font-weight:750; color:var(--encre);
  white-space:nowrap; font-variant-numeric:tabular-nums; }

/* ---------- barre d'action collante ---------- */
.dx-barre-tot{ display:flex; align-items:baseline; gap:10px; padding:2px 4px 8px; }
.dx-barre-tot span{ font-size:11.5px; color:var(--gris); font-weight:650; }
.dx-barre-tot b{ margin-left:auto; font-size:20px; font-weight:800; color:var(--indigo);
  font-variant-numeric:tabular-nums; }
.dx-barre-tot small{ font-size:10.5px; color:var(--gris); margin-left:3px; }

/* ---------- tableaux Streamlit ---------- */
[data-testid="stDataFrame"], [data-testid="stDataEditor"]{
  border-radius:14px; overflow:hidden; border:1px solid var(--bord);
  box-shadow:var(--sh); }
[data-testid="stExpander"] details{ border-radius:14px !important;
  border:1px solid var(--bord) !important; background:#fff !important; }
</style>
"""


# ==========================================================================
#  v9 : tuiles au gabarit unique + compteurs sur la tuile
# ==========================================================================
CSS_V9 = """
<style>
/* ---------- tuiles (batiments, modes, pieces) ---------- */
[class*="st-key-dxbox_"], [class*="st-key-dxtile_"]{
  background:#fff; border:1.5px solid var(--bord); border-radius:18px;
  padding:12px 10px 10px; box-shadow:0 2px 10px rgba(24,34,48,.05);
  transition:border-color .16s ease, box-shadow .16s ease, transform .16s ease;
  height:100%; }
[class*="st-key-dxbox_"]:hover, [class*="st-key-dxtile_"]:hover{
  border-color:#C4D2FF; box-shadow:0 10px 22px rgba(24,34,48,.10);
  transform:translateY(-2px); }
[class*="st-key-dxbox_on_"], [class*="st-key-dxbox_m_on_"],
[class*="st-key-dxtile_on_"]{
  border-color:var(--bleu); background:linear-gradient(180deg,#F4F8FF 0%,#FFFFFF 72%);
  box-shadow:0 10px 26px rgba(45,91,255,.18); }

/* ---------- gabarit d'icone STRICTEMENT identique partout ---------- */
.dx-t{ text-align:center; }
.dx-t .ico{ height:38px; line-height:38px; font-size:27px; overflow:hidden;
  font-family:"Segoe UI Emoji","Apple Color Emoji","Noto Color Emoji",sans-serif; }
.dx-t .nm{ display:flex; align-items:center; justify-content:center; min-height:34px;
  font-weight:800; color:var(--indigo); font-size:13.5px; line-height:1.22;
  padding:0 2px; }
.dx-t .nm.sm{ font-size:11.8px; line-height:1.2; }
.dx-t .nm.xs{ font-size:10.4px; line-height:1.16; letter-spacing:-.2px; }
.dx-t .fr{ min-height:14px; font-size:10.5px; color:var(--gris); margin-top:1px;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

/* ---------- bandeau de selection sous la tuile ---------- */
.st-key-dx_bats .stButton>button, .st-key-dx_modes .stButton>button,
.st-key-dx_pcs .stButton>button{
  min-height:34px!important; height:34px!important; padding:0 10px!important;
  margin-top:8px; border-radius:11px!important; box-shadow:none!important;
  font-size:12.5px!important; font-weight:700!important; }
.st-key-dx_bats .stButton>button p, .st-key-dx_modes .stButton>button p,
.st-key-dx_pcs .stButton>button p{ font-size:12.5px!important; line-height:1.1!important; }

/* ---------- compteur dans la tuile ---------- */
[class*="st-key-dxtile_"] [data-testid="stNumberInput"]{ margin-top:8px; }
[class*="st-key-dxtile_"] [data-testid="stNumberInput"] input{
  text-align:center; font-weight:800; font-size:15px; color:var(--indigo);
  padding:3px 0; }
[class*="st-key-dxtile_"] [data-testid="stNumberInput"] button{
  border-radius:9px!important; }

/* ---------- recapitulatif du lot + bouton d'ajout ---------- */
.dx-lot{ display:flex; align-items:center; gap:10px; margin:12px 0 6px;
  padding:10px 14px; border-radius:14px; border:1px dashed #B9CCFF;
  background:#F3F7FF; }
.dx-lot b{ display:inline-flex; align-items:center; justify-content:center;
  min-width:30px; height:30px; padding:0 8px; border-radius:9px;
  background:var(--grad); color:#fff; font-size:14px; }
.dx-lot span{ font-size:12.5px; color:var(--indigo); font-weight:600; }
.st-key-dx_addbar{ margin:2px 0 14px; }
.st-key-dx_addbar .stButton>button{ min-height:46px!important; border-radius:14px!important;
  font-size:14.5px!important; }

/* ---------- etat de personnalisation sur la carte de piece ---------- */
.dx-piece .bg{ display:inline-block; margin-top:5px; padding:2px 9px;
  border-radius:999px; background:var(--surf2); color:var(--gris);
  font-size:10.5px; font-weight:700; }
.dx-piece .bg.ok{ background:#E8F7EF; color:#2F7A54; }

@media (max-width:640px){
  .dx-t .ico{ height:32px; line-height:32px; font-size:23px; }
  .dx-t .nm{ min-height:30px; font-size:12px; }
  .dx-t .nm.sm{ font-size:10.8px; }
  .dx-t .nm.xs{ font-size:9.8px; }
  .dx-t .fr{ display:none; }
  [class*="st-key-dxbox_"], [class*="st-key-dxtile_"]{ padding:10px 7px 8px;
    border-radius:15px; }
}
</style>
"""


def appliquer():
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(CSS_V8, unsafe_allow_html=True)
    st.markdown(CSS_V9, unsafe_allow_html=True)
