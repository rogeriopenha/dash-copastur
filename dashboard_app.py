import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import io
import os
import time
from PIL import Image

st.set_page_config(page_title="Dashboard - COPASTUR", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    * { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; }
    .main > div { padding: 1rem 2rem; }
    .stApp { background: #0f1629; }
    .kpi-card { background: #1a2340; border-radius: 14px; padding: 1.2rem 1.5rem; box-shadow: 0 4px 16px rgba(0,0,0,0.3); border-left: 4px solid #7c9ccf; margin-bottom: 0.5rem; transition: transform 0.15s ease; }
    .kpi-card:hover { transform: translateY(-1px); }
    .kpi-card .label { font-size: 0.72rem; color: #8899b8; text-transform: uppercase; letter-spacing: 0.6px; font-weight: 600; }
    .kpi-card .value { font-size: 1.6rem; font-weight: 700; color: #e8edf5; margin-top: 0.15rem; }
    .kpi-card .sub { font-size: 0.78rem; color: #8899b8; margin-top: 0.1rem; }
    .card { background: #1a2340; border-radius: 14px; padding: 1.5rem; box-shadow: 0 4px 16px rgba(0,0,0,0.3); margin-bottom: 1rem; }
    .stSubheader, .card h1, .card h2, .card h3, .card h4, .card h5, .card h6,
    [data-testid="stHeadingWithAction"],
    [data-testid="stHeadingWithAction"] *,
    .stApp h3 { color: #ffffff !important; }
    h1, h2, h3, h4, h5, h6 { color: #e8edf5; font-weight: 600; }
    p, .stMarkdown, .caption, .stCaption { color: #c5ccd9; }
    .stButton > button, .stDownloadButton > button { background: linear-gradient(180deg, #2b5090 0%, #1e3a6e 100%); color: white; border: none; border-radius: 8px; padding: 0.4rem 1.5rem; font-weight: 500; box-shadow: 0 3px 0 #152a4e, 0 4px 12px rgba(37,62,129,0.3); transition: all 0.1s ease; position: relative; top: 0; }
    .stButton > button:hover, .stDownloadButton > button:hover { background: linear-gradient(180deg, #3663a8 0%, #2b5090 100%); box-shadow: 0 2px 0 #152a4e, 0 6px 16px rgba(37,62,129,0.4); transform: translateY(-1px); }
    .stButton > button:active, .stDownloadButton > button:active { box-shadow: 0 1px 0 #152a4e; transform: translateY(2px); }
    div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; border: 1px solid #253052; }
    .stTabs [data-baseweb="tab-list"] { gap: 0.4rem; background: #1a2340; padding: 0.5rem 0.8rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); margin-bottom: 1rem; }
    .stTabs button[data-baseweb="tab"] { border-radius: 8px; padding: 0.45rem 1.1rem; font-weight: 500; font-size: 0.85rem; color: #8899b8; border: none; transition: all 0.15s ease; }
    .stTabs button[data-baseweb="tab"]:hover { color: #e8edf5; background: #253052; }
    .stTabs button[data-baseweb="tab"][aria-selected="true"] { background: #253e81 !important; color: white !important; }
    footer { display: none; }
    section[data-testid="stSidebar"] { background: #283556; border-right: 1px solid #3a4a6a; display: flex; flex-direction: column; }
    section[data-testid="stSidebar"] > div:last-of-type { margin-top: auto; }
    .stSidebar .stMarkdown, .stSidebar .stMarkdown p, .stSidebar .stMarkdown h2, .stSidebar .stMarkdown h3 { color: #e8edf5; }
    .stSidebar .stSelectbox label, .stSidebar .stMultiSelect label, .stSidebar .stTextInput label, .stSidebar .stDateInput label { font-weight: 500; font-size: 0.78rem; color: #8899b8; }
    .stDownloadButton > button { padding: 0.3rem 1.2rem; }
    .row-widget.stSelectbox div[data-baseweb="select"] > div, .stTextInput input, .stMultiSelect div[data-baseweb="select"] > div { background: #1a2340; border-color: #253052; color: #e8edf5; }
    section[data-testid="stSidebar"] [data-baseweb="select"] > div,
    section[data-testid="stSidebar"] .stTextInput input,
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div { background: #d9e4f4 !important; border-color: #b8c9dd !important; }
    section[data-testid="stSidebar"] [data-baseweb="select"] * { color: #000000 !important; }
    section[data-testid="stSidebar"] .stTextInput input { color: #000000 !important; }
    section[data-testid="stSidebar"] .stDateInput input { background: #d9e4f4 !important; border-color: #b8c9dd !important; color: #000000 !important; }
    .st-cx { color: #e8edf5; }
    .stDateInput input { background: #1a2340; border-color: #253052; color: #e8edf5; }
    div[data-baseweb="menu"] { background: #ffffff; border: 1px solid #a0b8cc; }
    li[role="option"] { color: #1a1a2e; }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] { background: #6a9ee8; color: #ffffff; }
    .stAlert { background: #1a2340; color: #e8edf5; border-color: #253052; }
    .login-container { max-width: 380px; margin: 0 auto; padding: 2rem 0; }
    .login-container .stImage { text-align: center; }
    .login-container .stTextInput { text-align: center; }
    .login-container .stTextInput label { display: block; text-align: center; width: 100%; font-size: 0.75rem; }
    .login-container .stTextInput input { padding: 0.2rem 0.4rem; font-size: 0.75rem; text-align: center; }
    .login-container .st-emotion-cache-1kyxreq { gap: 0.2rem; }
    .login-container .stForm { text-align: center; }
    .change-pw-container { max-width: 400px; margin: 2rem auto; }
</style>
""", unsafe_allow_html=True)

logo_path = "Fujicom/logo_fujicom.jpg"

# ─── LOGIN SYSTEM ───
ALLOWED_EMAILS = [
    "glecya.frota@fujicom.com.br",
    "luis.claudio@fujicom.com.br",
    "larissa.fujita@fujicom.com.br",
    "rogeriopenha@gmail.com",
    "guilherme.abreu@fujicom.com.br",
    "financeiro01@fujicom.com.br",
]

if "authenticated_email" not in st.session_state:
    st.session_state.authenticated_email = None

# ─── LOGIN SCREEN ───
if not st.session_state.authenticated_email:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        try:
            logo_login = Image.open(logo_path)
            logo_login = logo_login.resize((220, int(logo_login.height * 220 / logo_login.width)))
            st.image(logo_login)
        except:
            st.markdown("<h1 style='color:#e8edf5;'>Dashboard COPASTUR</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#e8edf5; margin-bottom:1.5rem;'>Painel - Fujicom / Copastur</h3>", unsafe_allow_html=True)
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="seu@email.com.br")
            pw = st.text_input("Senha", placeholder="Digite sua senha", type="password")
            if st.form_submit_button("Entrar", type="primary", use_container_width=True):
                email_ok = email.strip().lower() in [e.strip().lower() for e in ALLOWED_EMAILS]
                pw_ok = pw == "fujicom2026"
                if email_ok and pw_ok:
                    st.session_state.authenticated_email = email.strip().lower()
                    st.rerun()
                elif not email_ok:
                    st.error("Email não autorizado")
                else:
                    st.error("Senha incorreta")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ─── SIDEBAR ───
try:
    logo = Image.open(logo_path)
    logo = logo.resize((180, int(logo.height * 180 / logo.width)))
    st.sidebar.image(logo, use_container_width=False)
except:
    pass
st.sidebar.markdown("<h2 style='color:#b8cfe8; margin-bottom:0;'>Dashboard - COPASTUR</h2><p style='color:#8899b8; font-size:0.85rem; margin-top:0;'>Fujicom - Pedidos</p>", unsafe_allow_html=True)
_email = st.session_state.authenticated_email
st.sidebar.markdown(f"👤 {_email}", unsafe_allow_html=True)
if st.sidebar.button("🚪 Sair", type="primary"):
    st.session_state.authenticated_email = None
    st.rerun()
st.sidebar.markdown("---")

GCP_JSON_SECRET = st.secrets.get("gcp_service_account") or st.secrets.get("gcp_service_account_json")
SHEET_URL_SECRET = st.secrets.get("sheet_url")
CLOUD_MODE = bool(GCP_JSON_SECRET and SHEET_URL_SECRET)

if CLOUD_MODE:
    st.sidebar.success("☁️ Modo nuvem")
else:
    st.sidebar.info("💻 Modo local")

if not CLOUD_MODE:
    st.sidebar.markdown("### 🔑 Conexão Google Sheets")
    json_key = st.sidebar.file_uploader("Service Account JSON", type="json")
    sheet_url = st.sidebar.text_input("URL da Planilha", placeholder="https://docs.google.com/spreadsheets/d/...")
    conectar = st.sidebar.button("Conectar", type="primary")

def parse_br(v):
    if pd.isna(v) or v == "" or v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    v = str(v).strip().replace(".", "").replace(",", ".")
    try:
        return float(v)
    except:
        return 0.0

MAX_VALOR = 10_000_000  # valores acima disso sao considerados erro de formato

STATUS_TRANSLATE = {
    "awaitingApprovalOfCost": "Aguardando Aprov. Custo",
    "awaitingIssue": "Aguardando Emissão",
    "approved": "Aprovado", "canceled": "Cancelado",
    "finalized": "Finalizado", "issued": "Emitido",
    "pending": "Pendente", "concluded": "Concluído",
}

def gsheet_connect(creds_dict, sheet_url):
    import gspread, json
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    if isinstance(creds_dict, bytes):
        creds_dict = creds_dict.decode("utf-8")
    if isinstance(creds_dict, str):
        creds_dict = json.loads(creds_dict)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open_by_url(sheet_url)

def df_from_ws(ws):
    """Load worksheet using get_all_values() (strings) to avoid gspread corrupting Brazilian-formatted numbers."""
    raw = ws.get_all_values()
    return pd.DataFrame(raw[1:], columns=raw[0])

def load_gsheets_tab(creds_dict, sheet_url, tab_name):
    sheet = gsheet_connect(creds_dict, sheet_url)
    ws = sheet.worksheet(tab_name)
    return df_from_ws(ws)

@st.cache_data(ttl=300)
def compute_subtotais(df_pedidos, creds_dict, sheet_url):
    sheet = gsheet_connect(creds_dict, sheet_url)
    ped_id = next(c for c in df_pedidos.columns if "pedido" in c.lower() and "root" not in c.lower())
    ped_vals = df_pedidos[ped_id].astype(str)
    total_calc = pd.Series(0.0, index=df_pedidos.index)

    for tab in ["Aereos", "Hoteis", "Carros", "Servicos", "Transporte", "Reembolsos"]:
        try:
            ws = sheet.worksheet(tab)
            df_tab = df_from_ws(ws)
            if df_tab.empty:
                continue
            t_ped = next(c for c in df_tab.columns if "pedido" in c.lower())
            t_val = next((c for c in df_tab.columns if c.lower() in ["total", "valor total"]), None)
            if t_val is None:
                continue
            df_tab[t_val] = df_tab[t_val].apply(parse_br)
            df_tab[t_ped] = df_tab[t_ped].astype(str)
            lookup = df_tab.groupby(t_ped)[t_val].sum()
            mapped = ped_vals.map(lookup).fillna(0.0)
            total_calc = total_calc + mapped
            time.sleep(0.5)
        except Exception:
            continue

    total_calc = total_calc.clip(upper=MAX_VALOR)
    return total_calc

@st.cache_data(ttl=300)
def load_pedidos_gsheets(json_key_file, sheet_url):
    sheet = gsheet_connect(json_key_file, sheet_url)
    ws = sheet.worksheet("Pedidos")
    return df_from_ws(ws)

@st.cache_data(ttl=300)
def load_reembolsos_gsheets(json_key_file, sheet_url):
    sheet = gsheet_connect(json_key_file, sheet_url)
    ws = sheet.worksheet("Reembolsos")
    return df_from_ws(ws)

@st.cache_data(ttl=300)
def load_viajantes_gsheets(json_key_file, sheet_url):
    try:
        sheet = gsheet_connect(json_key_file, sheet_url)
        ws = sheet.worksheet("Viajantes")
        return df_from_ws(ws)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_subtab(tab_name, creds_json, sheet_url):
    return load_gsheets_tab(creds_json, sheet_url, tab_name)

if CLOUD_MODE:
    with st.spinner("Carregando dados..."):
        try:
            import json
            js = json.dumps(GCP_JSON_SECRET) if not isinstance(GCP_JSON_SECRET, str) else GCP_JSON_SECRET
            df_pedidos = load_pedidos_gsheets(js, SHEET_URL_SECRET)
            df_reemb = load_reembolsos_gsheets(js, SHEET_URL_SECRET)
            df_viajantes = load_viajantes_gsheets(js, SHEET_URL_SECRET)
            # Compute real totals from sub-tabs (Aereos, Hoteis, Carros, Servicos)
            with st.spinner("Calculando totais reais..."):
                df_pedidos["total_calculado"] = compute_subtotais(df_pedidos, js, SHEET_URL_SECRET)
            st.session_state._creds = js
            st.session_state._sheet_url = SHEET_URL_SECRET
            st.sidebar.success(f"✅ {len(df_pedidos)} pedidos")
        except Exception as e:
            st.sidebar.error(f"Erro ao carregar dados: {e}")
            st.stop()
else:
    if "df_loaded" in st.session_state and st.session_state.df_loaded is not None:
        df_pedidos = st.session_state.df_loaded
        df_reemb = st.session_state.get("df_reemb")
        df_viajantes = st.session_state.get("df_viajantes", pd.DataFrame())
    elif conectar and json_key and sheet_url:
        with st.spinner("Carregando..."):
            try:
                jk = json_key.read()
                df_pedidos = load_pedidos_gsheets(jk, sheet_url)
                df_reemb = load_reembolsos_gsheets(jk, sheet_url)
                df_viajantes = load_viajantes_gsheets(jk, sheet_url)
                df_pedidos["total_calculado"] = compute_subtotais(df_pedidos, jk, sheet_url)
                st.session_state.df_loaded = df_pedidos
                st.session_state.df_reemb = df_reemb
                st.session_state.df_viajantes = df_viajantes
                st.session_state._creds = jk
                st.session_state._sheet_url = sheet_url
                st.sidebar.success(f"✅ {len(df_pedidos)} registros")
            except Exception as e:
                st.sidebar.error(f"Erro: {e}")
                st.stop()
    else:
        st.info("👈 Conecte-se ao Google Sheets para carregar os dados")
        st.stop()

# ── COLUMN MAPPING ──
COLS = {}
COLS["PEDIDO"] = next((c for c in df_pedidos.columns if "pedido" in c.lower() and "root" not in c.lower()), None)
COLS["STATUS"] = None
for kw in ["status viagem", "status despesa", "status"]:
    cand = [c for c in df_pedidos.columns if kw in c.lower()]
    if cand: COLS["STATUS"] = cand[0]; break
COLS["VALOR"] = None
for kw in ["total", "valor"]:
    cand = [c for c in df_pedidos.columns if kw in c.lower() and not any(k in c.lower() for k in ["data", "numero"])]
    if cand: COLS["VALOR"] = cand[0]; break
COLS["SOLICITANTE"] = next((c for c in df_pedidos.columns if "solicitante" in c.lower()), None)
COLS["CCUSTO"] = next((c for c in df_pedidos.columns if "centro" in c.lower()), None)
COLS["EMPRESA"] = next((c for c in df_pedidos.columns if "empresa" in c.lower() and "cod" not in c.lower()), None)
COLS["AGENCIA"] = next((c for c in df_pedidos.columns if "agência" in c.lower() or "agencia" in c.lower()), None)
COLS["VIAJANTE"] = next((c for c in df_pedidos.columns if "viajante" in c.lower()), None)
COLS["MOTIVO"] = next((c for c in df_pedidos.columns if "motivo" in c.lower()), None)
# ── DATE COLUMN DETECTION ──
# Priority-based name matching, validated by actual datetime parsing
def _try_parse_date(_series):
    """Try dayfirst (handles dd/mm/yyyy, yyyy-mm-dd timestamps with tz), auto-detect, Excel serial."""
    _s_clean = _series.astype(str).str.strip()
    _t1 = pd.to_datetime(_s_clean, errors="coerce", dayfirst=True)
    if _t1.notna().sum() > 0:
        return True, _t1
    _t2 = pd.to_datetime(_s_clean, errors="coerce")
    if _t2.notna().sum() > 0:
        return True, _t2
    if pd.api.types.is_numeric_dtype(_series):
        _t3 = pd.to_datetime(_series, unit="D", origin="1899-12-30", errors="coerce")
        if _t3.notna().sum() > 0:
            return True, _t3
    return False, _series

COLS["DATA"] = None
# First: try exact patterns with "data" prefix
_COLS_DATA_PRIORITY = [
    lambda c: "data" in c.lower() and "pedido" in c.lower(),
    lambda c: "data" in c.lower() and "cota" in c.lower(),
    lambda c: "data" in c.lower() and "emiss" in c.lower(),
    lambda c: "data" in c.lower() and "cria" in c.lower(),
    lambda c: "data" in c.lower(),
    lambda c: c.lower().startswith("dt"),
]
for _fn in _COLS_DATA_PRIORITY:
    _cands = [c for c in df_pedidos.columns if _fn(c)]
    for _c in _cands:
        _ok, _t = _try_parse_date(df_pedidos[_c])
        if _ok:
            COLS["DATA"] = _c
            df_pedidos[_c] = _t
            break
    if COLS["DATA"]:
        break
# Brute-force: try remaining non-obvious columns
if COLS["DATA"] is None:
    _COLS_NON_DATE_KW = ["nº", "num", "cod", "id", "total", "valor", "preço", "preco", "qtd", "quant", "telefone", "cnpj", "cpf", "cep", "email", "site", "obs", "descri"]
    _candidates_bf = [c for c in df_pedidos.columns if not any(k in c.lower() for k in _COLS_NON_DATE_KW)]
    for _c in _candidates_bf:
        _ok, _t = _try_parse_date(df_pedidos[_c])
        if _ok and _t.notna().sum() > len(df_pedidos) * 0.3:
            COLS["DATA"] = _c
            df_pedidos[_c] = _t
            break
COLS["TIPO"] = next((c for c in df_pedidos.columns if "tipo" in c.lower()), None)

# Use sum of all sub-tabs + Reembolsos as the order value (ignore Total column)
if "total_calculado" in df_pedidos.columns:
    df_pedidos[COLS["VALOR"]] = df_pedidos["total_calculado"]
    df_pedidos = df_pedidos.drop(columns=["total_calculado"])

if COLS["STATUS"]:
    df_pedidos[COLS["STATUS"]] = df_pedidos[COLS["STATUS"]].astype(str).map(STATUS_TRANSLATE).fillna(df_pedidos[COLS["STATUS"]].astype(str)).replace("", "Indefinido")
for col in list(COLS.values()):
    if col and any(k in col.lower() for k in ["data"]):
        try:
            _ok, _t = _try_parse_date(df_pedidos[col])
            if _ok: df_pedidos[col] = _t
        except: pass

# ── REEMBOLSOS PARSE ──
if df_reemb is not None and not df_reemb.empty:
    REEMB_CAT = next((c for c in df_reemb.columns if "categoria" in c.lower()), None)
    # Prioridade: "Valor Total" > "Total" > "Valor" (coluna "Valor" tem quantidade, nao valor monetario)
    REEMB_VAL = next((c for c in df_reemb.columns if c.lower() == "valor total"), None)
    if not REEMB_VAL: REEMB_VAL = next((c for c in df_reemb.columns if c.lower() == "total"), None)
    if not REEMB_VAL: REEMB_VAL = next((c for c in df_reemb.columns if c.lower() == "valor"), None)
    REEMB_DESP = next((c for c in df_reemb.columns if "descricao" in c.lower() or "descri" in c.lower()), None)
    REEMB_PED = next((c for c in df_reemb.columns if "pedido" in c.lower()), None)
    if REEMB_VAL: df_reemb[REEMB_VAL] = df_reemb[REEMB_VAL].apply(parse_br)
    if REEMB_PED: df_reemb[REEMB_PED] = df_reemb[REEMB_PED].astype(str)

# ── SOLICITANTE LOOKUP ──
SOLICITANTE_MAP = {}
if COLS["PEDIDO"] and COLS["SOLICITANTE"]:
    SOLICITANTE_MAP = dict(zip(df_pedidos[COLS["PEDIDO"]].astype(str).str.strip(), df_pedidos[COLS["SOLICITANTE"]]))

# ── VIAJANTES LOOKUP ──
VIAJANTE_ORDER_MAP = {}
VIAJANTE_LIST = []
VIAJ_PED = None
VIAJ_NOME = None
if df_viajantes is not None and not df_viajantes.empty:
    VIAJ_PED = next((c for c in df_viajantes.columns if "pedido" in c.lower()), None)
    VIAJ_NOME = next((c for c in df_viajantes.columns if any(k in c.lower() for k in ["viajante", "passageiro", "colaborador", "nome", "solicitante"])), None)
    if VIAJ_PED and VIAJ_NOME:
        df_viajantes[VIAJ_PED] = df_viajantes[VIAJ_PED].astype(str).str.strip().str.lstrip("0")
        df_viajantes[VIAJ_NOME] = df_viajantes[VIAJ_NOME].astype(str).str.strip()
        VIAJANTE_LIST = sorted(df_viajantes[VIAJ_NOME].dropna().unique())
        VIAJANTE_ORDER_MAP = df_viajantes.groupby(VIAJ_NOME)[VIAJ_PED].apply(set).to_dict()


# ── VIAJANTE REVERSE MAP (pedido → viajante name) ──
VIAJANTE_REVERSE_MAP = {}
if VIAJ_PED and VIAJ_NOME and df_viajantes is not None and not df_viajantes.empty:
    # Join multiple travelers with " + " for pedidos with more than one
    VIAJANTE_REVERSE_MAP = df_viajantes.groupby(VIAJ_PED)[VIAJ_NOME].apply(lambda x: " + ".join(x.dropna().unique())).to_dict()
# ── SIDEBAR FILTERS ──
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Filtros")

filtros_aplicados = 0
df_filt = df_pedidos.copy()

data_col = COLS["DATA"]
data_ok = data_col and pd.api.types.is_datetime64_any_dtype(df_filt[data_col])
if not data_ok and data_col:
    # Re-try conversion with multi-strategy on df_filt
    _ok, _t = _try_parse_date(df_filt[data_col])
    if _ok:
        df_filt[data_col] = _t
        data_ok = True
if data_ok:
    valid_dates = df_filt[data_col].dropna()
    if len(valid_dates) == 0:
        data_ok = False
    else:
        min_d, max_d = valid_dates.min().date(), valid_dates.max().date()
        st.sidebar.markdown("### 📅 Período")
        dc1, dc2 = st.sidebar.columns(2)
        with dc1:
            start_date = st.date_input("De", value=min_d, min_value=min_d, max_value=max_d, format="DD/MM/YYYY")
        with dc2:
            end_date = st.date_input("Até", value=max_d, min_value=min_d, max_value=max_d, format="DD/MM/YYYY")
        _before = len(df_filt)
        date_mask = (df_filt[data_col].dt.date >= start_date) & (df_filt[data_col].dt.date <= end_date)
        df_filt = df_filt[date_mask]
        _after = len(df_filt)
        if _after < _before:
            filtros_aplicados += 1
        st.sidebar.caption(f"📅 {data_col}: {_before} → {_after} registros")
elif COLS["DATA"]:
    st.sidebar.caption(f'⚠️ Coluna "{COLS["DATA"]}" não é data')
else:
    st.sidebar.caption('⚠️ Nenhuma coluna de data encontrada em "Pedidos"')
    st.sidebar.caption(f"Colunas: {', '.join(df_pedidos.columns[:10])}{'...' if len(df_pedidos.columns) > 10 else ''}")

# ── SINGLE ORDER FILTER ──
st.sidebar.markdown("### 🔎 Pedido Específico")
busca_pedido = st.sidebar.text_input("Nº do Pedido", placeholder="Ex: 1935", key="busca_pedido")
if busca_pedido:
    if COLS["PEDIDO"]:
        ped_str = df_filt[COLS["PEDIDO"]].astype(str).str.strip()
        busca = busca_pedido.strip()
        # Tenta match exato primeiro, depois contains
        mask_exato = ped_str == busca
        if mask_exato.any():
            df_filt = df_filt[mask_exato]
            filtros_aplicados += 1
            st.sidebar.success(f"Pedido {busca} encontrado")
        else:
            mask_contem = ped_str.str.contains(busca, case=False, na=False)
            if mask_contem.any():
                df_filt = df_filt[mask_contem]
                filtros_aplicados += 1
                st.sidebar.success(f"Pedido {busca} encontrado")
            else:
                st.sidebar.warning(f"Pedido {busca} não encontrado")
                st.sidebar.caption(f"Exemplo: {ped_str.iloc[0] if len(ped_str) > 0 else 'sem dados'}")

if COLS["STATUS"]:
    opts = sorted(df_filt[COLS["STATUS"]].dropna().unique())
    sel = st.sidebar.multiselect("Status", opts, default=opts)
    if sel and len(sel) < len(opts):
        df_filt = df_filt[df_filt[COLS["STATUS"]].isin(sel)]
        filtros_aplicados += 1

if COLS["SOLICITANTE"]:
    opts = sorted(df_filt[COLS["SOLICITANTE"]].dropna().unique())
    sel = st.sidebar.multiselect("Solicitante", opts, default=[])
    if sel:
        df_filt = df_filt[df_filt[COLS["SOLICITANTE"]].isin(sel)]
        filtros_aplicados += 1

if COLS["CCUSTO"]:
    opts = sorted(df_filt[COLS["CCUSTO"]].dropna().unique())
    sel = st.sidebar.multiselect("Centro de Custo", opts, default=[])
    if sel:
        df_filt = df_filt[df_filt[COLS["CCUSTO"]].isin(sel)]
        filtros_aplicados += 1

if VIAJANTE_LIST:
    if COLS["PEDIDO"]:
        filt_pedidos_set = set(df_filt[COLS["PEDIDO"]].astype(str).str.strip().str.lstrip("0"))
        viajantes_contextuais = sorted(
            v for v in VIAJANTE_LIST
            if any(p in filt_pedidos_set for p in VIAJANTE_ORDER_MAP.get(v, set()))
        )
    else:
        viajantes_contextuais = VIAJANTE_LIST
    sel_viajantes = st.sidebar.multiselect("Viajante", viajantes_contextuais, default=[])
    if sel_viajantes:
        viajante_pedidos = set()
        for v in sel_viajantes:
            viajante_pedidos.update(VIAJANTE_ORDER_MAP.get(v, set()))
        if viajante_pedidos and COLS["PEDIDO"]:
            df_filt = df_filt[df_filt[COLS["PEDIDO"]].astype(str).str.strip().str.lstrip("0").isin(viajante_pedidos)]
            filtros_aplicados += 1

if COLS["EMPRESA"]:
    opts = sorted(df_filt[COLS["EMPRESA"]].dropna().unique())
    sel = st.sidebar.multiselect("Empresa", opts, default=[])
    if sel:
        df_filt = df_filt[df_filt[COLS["EMPRESA"]].isin(sel)]
        filtros_aplicados += 1

c1, c2 = st.sidebar.columns(2)
with c1:
    if filtros_aplicados > 0:
        st.caption(f"{filtros_aplicados} filtro(s)")
with c2:
    if filtros_aplicados > 0 and st.button("Limpar"):
        st.rerun()

FILTERED_PEDIDOS = set(df_filt[COLS["PEDIDO"]].astype(str).str.strip().str.lstrip("0")) if COLS["PEDIDO"] else set()

if VIAJANTE_LIST and FILTERED_PEDIDOS:
    QTDE_VIAJANTES = sum(1 for v in VIAJANTE_LIST if VIAJANTE_ORDER_MAP.get(v, set()) & FILTERED_PEDIDOS)
else:
    QTDE_VIAJANTES = len(VIAJANTE_LIST) if VIAJANTE_LIST else 0

st.sidebar.markdown("---")

st.sidebar.markdown('<div style="background:#2a3d5e; border:1px solid #4a6a8a; border-radius:10px; padding:0.7rem 1rem; box-shadow:0 3px 0 #1a2a4a, 0 4px 12px rgba(37,62,129,0.25); margin-bottom:0.8rem;">'
    '<p style="margin:0; font-size:12px; font-style:italic; color:#ffd700; line-height:1.6;">'
    'Desenvolvido por <b>Rogerio Penha</b><br>'
    'rogeriopenha@gmail.com<br>'
    "(016)99798-2392<br>"
    'versão: 1.0 release 01<br>'
    'Data: 05/07/2026'
    '</p></div>', unsafe_allow_html=True)


# ── MAIN KPIs ──
total_gasto = df_filt[COLS["VALOR"]].sum() if COLS["VALOR"] else 0
total_pedidos = len(df_filt)

st.markdown(f"""
<div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
    <div>
        <h1 style="margin:0;">📊 Dashboard - COPASTUR</h1>
        <p style="color:#6c757d; margin:0;">{total_pedidos} de {len(df_pedidos)} pedidos • R$ {total_gasto:,.2f} em gastos</p>
    </div>
    <div style="font-size:0.85rem; color:#6c757d;">{datetime.now().strftime("%d/%m/%Y %H:%M")}</div>
</div>
""", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="kpi-card"><div class="label">💰 Total Gasto</div><div class="value">R$ {total_gasto:,.2f}</div><div class="sub">em {total_pedidos} pedidos</div></div>""", unsafe_allow_html=True)
with k2:
    pendentes = df_filt[df_filt[COLS["STATUS"]].astype(str).str.contains("Aguardando|Pendente", case=False, na=False)].shape[0] if COLS["STATUS"] else 0
    pct = pendentes / total_pedidos * 100 if total_pedidos > 0 else 0
    st.markdown(f"""<div class="kpi-card"><div class="label">📋 Total Pedidos</div><div class="value">{total_pedidos}</div><div class="sub">{pendentes} pendentes ({pct:.1f}%)</div></div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-card"><div class="label">👤 Viajantes</div><div class="value">{QTDE_VIAJANTES}</div><div class="sub">viajantes distintos</div></div>""", unsafe_allow_html=True)
with k4:
    cat_count = df_filt[COLS["STATUS"]].nunique() if COLS["STATUS"] else 0
    forn_count = df_filt[COLS["AGENCIA"]].nunique() if COLS["AGENCIA"] else 0
    st.markdown(f"""<div class="kpi-card"><div class="label">📊 Abrangência</div><div class="value">{cat_count} status</div><div class="sub">{forn_count} agências</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ──
tab_labels = ["📈 Visão Geral"]
if COLS["STATUS"]: tab_labels.append("📊 Por Status")
if VIAJANTE_REVERSE_MAP and COLS["PEDIDO"]: tab_labels.append("👥 Por Viajante")
if data_ok: tab_labels.append("📅 Tendência")
tab_labels.append("📋 Dados Exportáveis")
tab_labels.append("📋 Detalhamento")

tabs = st.tabs(tab_labels)
ti = 0

# TAB 1: Visão Geral
with tabs[ti]:
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Gastos por Centro de Custo")
        if COLS["CCUSTO"] and COLS["VALOR"]:
            g = df_filt.groupby(COLS["CCUSTO"])[COLS["VALOR"]].sum().sort_values(ascending=True).tail(15)
            fig = go.Figure(go.Bar(x=g.values, y=g.index, orientation="h",
                marker=dict(color=g.values, colorscale="Blues", line=dict(width=0)),
                text=g.apply(lambda x: f"R$ {x:,.0f}"), textposition="outside"))
            fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
            fig.update_traces(hovertemplate="R$ %{x:,.2f}<extra></extra>")
            st.plotly_chart(fig, use_container_width=True, key="chart_gastos_ccusto")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Distribuição por Empresa")
        if COLS["EMPRESA"]:
            ec = df_filt[COLS["EMPRESA"]].value_counts()
            fig = go.Figure(data=[go.Pie(labels=ec.index, values=ec.values, hole=0.55,
                marker=dict(colors=px.colors.sequential.Blues[::-1][:len(ec)]),
                textinfo="label+percent", textposition="outside", showlegend=False)])
            fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="white", font=dict(color="#1a1a2e"))
            st.plotly_chart(fig, use_container_width=True, key="chart_dist_empresa")
        st.markdown("</div>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Top Agências")
        if COLS["AGENCIA"] and COLS["VALOR"]:
            g = df_filt.groupby(COLS["AGENCIA"])[COLS["VALOR"]].sum().sort_values(ascending=False).head(10)
            fig = px.bar(g, x=g.values, y=g.index, orientation="h", color=g.values, color_continuous_scale="Blues")
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
            fig.update_coloraxes(showscale=False)
            fig.update_traces(hovertemplate="R$ %{x:,.2f}<extra></extra>")
            st.plotly_chart(fig, use_container_width=True, key="chart_top_agencias")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Motivos de Viagem")
        if COLS["MOTIVO"]:
            mc = df_filt[COLS["MOTIVO"]].value_counts().head(10)
            fig = px.bar(mc, x=mc.values, y=mc.index, orientation="h", color=mc.values, color_continuous_scale="Teal", text_auto=".0f")
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
            fig.update_coloraxes(showscale=False)
            fig.update_traces(hovertemplate="%{x}<extra></extra>")
            st.plotly_chart(fig, use_container_width=True, key="chart_motivos_viagem")
        st.markdown("</div>", unsafe_allow_html=True)
    ti += 1

# TAB 2: Por Status
if COLS["STATUS"]:
    with tabs[ti]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1.5])
        with c1:
            sc = df_filt[COLS["STATUS"]].value_counts()
            fig = go.Figure(data=[go.Pie(labels=sc.index, values=sc.values, hole=0.5,
                marker=dict(colors=px.colors.sequential.Blues[::-1][:len(sc)]),
                textinfo="label+percent", textposition="outside", showlegend=False)])
            fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="white", font=dict(color="#1a1a2e"))
            st.plotly_chart(fig, use_container_width=True, key="chart_status_pie")
        with c2:
            if COLS["VALOR"]:
                sp = df_filt.groupby(COLS["STATUS"]).agg(
                    Total=(COLS["VALOR"], "sum"), Qtd=(COLS["PEDIDO"] or "Nº Pedido", "count"),
                    Ticket=(COLS["VALOR"], "mean")).reset_index()
                sp["Total"] = sp["Total"].apply(lambda x: f"R$ {x:,.2f}")
                sp["Ticket"] = sp["Ticket"].apply(lambda x: f"R$ {x:,.2f}")
                st.dataframe(sp, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
        ti += 1

# TAB 3: Por Viajante
if VIAJANTE_REVERSE_MAP and COLS["PEDIDO"]:
    with tabs[ti]:
        df_filt_via = df_filt.copy()
        df_filt_via["Viajante"] = df_filt_via[COLS["PEDIDO"]].astype(str).str.strip().str.lstrip("0").map(VIAJANTE_REVERSE_MAP)
        df_filt_via = df_filt_via.dropna(subset=["Viajante"])
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Ranking de Gastos")
            if COLS["VALOR"] and not df_filt_via.empty:
                g = df_filt_via.groupby("Viajante")[COLS["VALOR"]].sum().sort_values(ascending=True).tail(20)
                fig = go.Figure(go.Bar(x=g.values, y=g.index, orientation="h",
                    marker=dict(color=g.values, colorscale="Blues", line=dict(width=0)),
                    text=g.apply(lambda x: f"R$ {x:,.0f}"), textposition="outside"))
                fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
                fig.update_traces(hovertemplate="R$ %{x:,.2f}<extra></extra>")
                st.plotly_chart(fig, use_container_width=True, key="chart_ranking_solicitante")
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Volume de Pedidos")
            sc = df_filt_via["Viajante"].value_counts().sort_values(ascending=True).tail(20)
            fig = go.Figure(go.Bar(x=sc.values, y=sc.index, orientation="h",
                marker=dict(color=sc.values, colorscale="Teal", line=dict(width=0)),
                text=sc.values, textposition="outside"))
            fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
            fig.update_traces(hovertemplate="%{x}<extra></extra>")
            st.plotly_chart(fig, use_container_width=True, key="chart_volume_pedidos")
            st.markdown("</div>", unsafe_allow_html=True)
        ti += 1

# TAB 4: Tendência
if data_ok:
    with tabs[ti]:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Gastos ao Longo do Tempo")
            if COLS["VALOR"]:
                try:
                    tr = df_filt.dropna(subset=[data_col]).set_index(data_col).resample("ME")[COLS["VALOR"]].sum().reset_index()
                    if not tr.empty:
                        fig = px.line(tr, x=data_col, y=COLS["VALOR"], markers=True)
                        fig.update_traces(line=dict(color="#1a5276", width=3), marker=dict(size=6))
                        fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(title=None), yaxis=dict(title="R$"))
                        fig.update_yaxes(tickprefix="R$ ")
                        fig.update_traces(hovertemplate="R$ %{y:,.2f}<extra></extra>")
                        st.plotly_chart(fig, use_container_width=True, key="chart_gastos_tempo")
                    else:
                        st.caption("Sem dados suficientes para o gráfico de tendência.")
                except Exception:
                    st.caption("Não foi possível gerar o gráfico de gastos ao longo do tempo.")
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Volume de Pedidos por Mês")
            try:
                ct = df_filt.dropna(subset=[data_col]).set_index(data_col).resample("ME")[COLS["PEDIDO"] or df_filt.columns[0]].count().reset_index()
                if not ct.empty:
                    fig = px.bar(ct, x=data_col, y=COLS["PEDIDO"] or df_filt.columns[0], color_discrete_sequence=["#2e86c1"])
                    fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(title=None), yaxis=dict(title="Pedidos"))
                    fig.update_traces(hovertemplate="%{y}<extra></extra>")
                    st.plotly_chart(fig, use_container_width=True, key="chart_pedidos_mes")
                else:
                    st.caption("Sem dados suficientes para o gráfico de volume.")
            except Exception:
                st.caption("Não foi possível gerar o gráfico de volume de pedidos.")
            st.markdown("</div>", unsafe_allow_html=True)
        ti += 1

# TAB 5: Tabela Exportável (com sub-abas por função)
with tabs[ti]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Dados Exportáveis")
    _ed_creds = st.session_state.get("_creds")
    _ed_url = st.session_state.get("_sheet_url")
    if not _ed_creds and CLOUD_MODE:
        import json
        _ed_creds = json.dumps(GCP_JSON_SECRET) if not isinstance(GCP_JSON_SECRET, str) else GCP_JSON_SECRET
        _ed_url = SHEET_URL_SECRET

    ed_labels = ["📋 Todas", "✈️ Aéreos", "🏨 Hotéis", "🚗 Carros", "🚚 Transporte", "💰 Adiantamentos", "🛠️ Serviços", "💰 Reembolsos"]
    ed_keys = ["Pedidos", "Aereos", "Hoteis", "Carros", "Transporte", "Adiantamentos", "Servicos", "Reembolsos"]
    ed_tabs = st.tabs(ed_labels)
    for ei, ek in enumerate(ed_keys):
        with ed_tabs[ei]:
            if ek == "Pedidos":
                st.caption(f"{len(df_filt)} registros • {len(df_filt.columns)} colunas")
                export_cols = [c for c in df_filt.columns]
                search = st.text_input("🔎 Buscar na tabela", placeholder="Digite para filtrar...", key="ed_search_pedidos")
                col_sel = st.multiselect("Colunas", options=export_cols, default=export_cols, label_visibility="collapsed", key="ed_cols_pedidos")
                df_disp = df_filt[col_sel].copy() if col_sel else df_filt[export_cols].copy()
                if search:
                    mask = df_disp.astype(str).apply(lambda row: row.str.contains(search, case=False, na=False)).any(axis=1)
                    df_disp = df_disp[mask]
                for c in df_disp.select_dtypes(include=["datetime64"]).columns:
                    df_disp[c] = df_disp[c].dt.strftime("%d/%m/%Y")
                st.dataframe(df_disp, use_container_width=True, hide_index=True, height=450)
                st.markdown("<br>", unsafe_allow_html=True)
                d1, d2, d3 = st.columns(3)
                csv = df_disp.to_csv(index=False).encode("utf-8-sig")
                d1.download_button("📥 CSV", csv, f"pedidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", use_container_width=True, key="dl_pedidos_csv")
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as w: df_disp.to_excel(w, index=False, sheet_name="Pedidos")
                d2.download_button("📥 Excel", output.getvalue(), f"pedidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key="dl_pedidos_xlsx")
                d3.download_button("📥 JSON", df_disp.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8-sig"), f"pedidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "application/json", use_container_width=True, key="dl_pedidos_json")
            else:
                if not _ed_creds or not _ed_url:
                    st.info("💻 Conecte-se ao Google Sheets para visualizar os dados desta aba.")
                else:
                    try:
                        df_ed = load_subtab(ek, _ed_creds, _ed_url)
                        time.sleep(0.8)
                    except Exception:
                        df_ed = None
                    if df_ed is not None and not df_ed.empty:
                        _ed_ped_col = next((c for c in df_ed.columns if "pedido" in c.lower()), None)
                        if _ed_ped_col and FILTERED_PEDIDOS:
                            df_ed = df_ed[df_ed[_ed_ped_col].astype(str).str.strip().str.lstrip("0").isin(FILTERED_PEDIDOS)]
                        _ed_data_col = next((c for c in df_ed.columns if any(k in c.lower() for k in ["data", "cotacao", "emissao", "viagem", "check", "pagamento", "vencimento", "lancamento"])), None)
                        if data_ok and _ed_data_col:
                            try:
                                _ok_dt, _t_dt = _try_parse_date(df_ed[_ed_data_col])
                                if _ok_dt:
                                    df_ed[_ed_data_col] = _t_dt
                                    _ed_date_mask = (df_ed[_ed_data_col].dt.date >= start_date) & (df_ed[_ed_data_col].dt.date <= end_date)
                                    df_ed = df_ed[_ed_date_mask]
                            except:
                                pass
                        st.caption(f"{len(df_ed)} registros • {len(df_ed.columns)} colunas")
                        search_ed = st.text_input("🔎 Buscar", placeholder="Digite para filtrar...", key=f"ed_search_{ek}")
                        df_ed_disp = df_ed.copy()
                        if search_ed:
                            mask = df_ed_disp.astype(str).apply(lambda row: row.str.contains(search_ed, case=False, na=False)).any(axis=1)
                            df_ed_disp = df_ed_disp[mask]
                        for c in df_ed_disp.select_dtypes(include=["datetime64"]).columns:
                            df_ed_disp[c] = df_ed_disp[c].dt.strftime("%d/%m/%Y")
                        st.dataframe(df_ed_disp, use_container_width=True, hide_index=True, height=450)
                        st.markdown("<br>", unsafe_allow_html=True)
                        e1, e2, e3 = st.columns(3)
                        csv_ed = df_ed_disp.to_csv(index=False).encode("utf-8-sig")
                        e1.download_button("📥 CSV", csv_ed, f"{ek.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", use_container_width=True, key=f"dl_{ek}_csv")
                        output_ed = io.BytesIO()
                        with pd.ExcelWriter(output_ed, engine="openpyxl") as w: df_ed_disp.to_excel(w, index=False, sheet_name=ek)
                        e2.download_button("📥 Excel", output_ed.getvalue(), f"{ek.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key=f"dl_{ek}_xlsx")
                        e3.download_button("📥 JSON", df_ed_disp.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8-sig"), f"{ek.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "application/json", use_container_width=True, key=f"dl_{ek}_json")
                    else:
                        st.info(f"Dados de {ek} não disponíveis.")
    st.markdown("</div>", unsafe_allow_html=True)
    ti += 1

# TAB 6: Detalhamento por Aba (segunda linha de abas)
with tabs[ti]:
    _creds = st.session_state.get("_creds")
    _sheet_url = st.session_state.get("_sheet_url")

    if not _creds or not _sheet_url:
        st.info("💻 Conecte-se ao Google Sheets para visualizar os detalhes das abas.")
    else:
        subtab_labels = ["✈️ Aéreos", "🏨 Hotéis", "🚗 Carros", "🚚 Transporte", "💰 Adiantamentos", "🛠️ Serviços", "💰 Reembolsos"]
        subtab_keys = ["Aereos", "Hoteis", "Carros", "Transporte", "Adiantamentos", "Servicos", "Reembolsos"]
        # Column letters: J=9, K=10, L=11, N=13, Q=16 (0-indexed)
        SUBTAB_VAL_COL = {"Aereos": 9, "Hoteis": 11, "Carros": 16, "Transporte": 13, "Adiantamentos": 9, "Servicos": 10}

        subtabs_2 = st.tabs(subtab_labels)
        for si, sk in enumerate(subtab_keys):
            with subtabs_2[si]:
                try:
                    df_st = load_subtab(sk, _creds, _sheet_url)
                    time.sleep(0.8)
                except Exception:
                    df_st = None

                if df_st is None or df_st.empty:
                    st.info(f"Dados de {sk} não disponíveis.")
                else:
                    if sk == "Reembolsos":
                        val_col = next((c for c in df_st.columns if c.lower() == "valor total"), None)
                        if not val_col: val_col = next((c for c in df_st.columns if c.lower() == "total"), None)
                        if not val_col: val_col = next((c for c in df_st.columns if c.lower() == "valor"), None)
                    else:
                        val_idx = SUBTAB_VAL_COL.get(sk)
                        val_col = df_st.columns[val_idx] if val_idx is not None and val_idx < len(df_st.columns) else None

                    if val_col is None:
                        st.info(f"Coluna de valor não encontrada em {sk}.")
                    else:
                        df_st[val_col] = df_st[val_col].apply(parse_br)
                    df_st[val_col] = df_st[val_col].clip(upper=MAX_VALOR)

                    if sk == "Reembolsos":
                        _desp_col = next((c for c in df_st.columns if "descri" in c.lower()), None)
                        if _desp_col:
                            df_st["_desp_clean"] = df_st[_desp_col].astype(str).str.replace(r"\s*-.*$", "", regex=True).str.strip()

                    _st_ped_col = next((c for c in df_st.columns if "pedido" in c.lower()), None)
                    if _st_ped_col and FILTERED_PEDIDOS:
                        df_st = df_st[df_st[_st_ped_col].astype(str).str.strip().str.lstrip("0").isin(FILTERED_PEDIDOS)]
                    # Apply date filter directly to subtab data
                    _st_data_col = next((c for c in df_st.columns if any(k in c.lower() for k in ["data", "cotacao", "emissao", "viagem", "check", "pagamento", "vencimento", "lancamento"])), None)
                    if data_ok and _st_data_col:
                        try:
                            _ok_dt, _t_dt = _try_parse_date(df_st[_st_data_col])
                            if _ok_dt:
                                df_st[_st_data_col] = _t_dt
                                _st_date_mask = (df_st[_st_data_col].dt.date >= start_date) & (df_st[_st_data_col].dt.date <= end_date)
                                df_st = df_st[_st_date_mask]
                        except:
                            pass

                    total_val = df_st[val_col].sum()
                    count_records = len(df_st)
                    avg_val = total_val / count_records if count_records > 0 else 0
                    nonzero = (df_st[val_col] > 0).sum()

                    st.caption(f"{count_records} registros • R$ {total_val:,.2f} total • {nonzero} com valor")

                    d1, d2, d3, d4 = st.columns(4)
                    d1.markdown(f"""<div class="kpi-card"><div class="label">💰 Total {sk}</div><div class="value">R$ {total_val:,.2f}</div></div>""", unsafe_allow_html=True)
                    d2.markdown(f"""<div class="kpi-card"><div class="label">📝 Registros</div><div class="value">{count_records}</div></div>""", unsafe_allow_html=True)
                    d3.markdown(f"""<div class="kpi-card"><div class="label">🎫 Valor Médio</div><div class="value">R$ {avg_val:,.2f}</div></div>""", unsafe_allow_html=True)
                    d4.markdown(f"""<div class="kpi-card"><div class="label">✅ Com Valor</div><div class="value">{nonzero}</div></div>""", unsafe_allow_html=True)

                    st.markdown('<div class="card">', unsafe_allow_html=True)

                    grupo_col = next((c for c in df_st.columns if any(k in c.lower() for k in ["categoria", "tipo", "despesa"])), None)
                    if sk == "Adiantamentos":
                        mot_col = next((c for c in df_st.columns if "motivo" in c.lower()), None)
                        if mot_col:
                            ca1, ca2 = st.columns([1, 1])
                            with ca1:
                                st.markdown("<h3 style='color:#ffffff; margin-bottom:0.5rem;'>Total por Motivo Viagem</h3>", unsafe_allow_html=True)
                                smot_st = df_st.groupby(mot_col)[val_col].sum().sort_values(ascending=True)
                                fig = go.Figure(go.Bar(x=smot_st.values, y=smot_st.index, orientation="h",
                                    marker=dict(color=smot_st.values, colorscale="Blues", line=dict(width=0)),
                                    text=smot_st.apply(lambda x: f"R$ {x:,.0f}"), textposition="outside"))
                                fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10),
                                    paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
                                fig.update_traces(hovertemplate="R$ %{x:,.2f}<extra></extra>")
                                st.plotly_chart(fig, use_container_width=True, key=f"chart_{sk}_total_motivo")
                            with ca2:
                                st.markdown("<h3 style='color:#ffffff; margin-bottom:0.5rem;'>Distribuição por Motivo de Viagem</h3>", unsafe_allow_html=True)
                                gc = df_st[mot_col].value_counts()
                                fig = go.Figure(data=[go.Pie(labels=gc.index, values=gc.values, hole=0.65,
                                    marker=dict(colors=px.colors.sequential.Blues[::-1][:len(gc)]),
                                    textinfo="label+percent", textposition="outside", showlegend=False,
                                    textfont=dict(size=10))])
                                fig.update_layout(height=350, margin=dict(l=60, r=60, t=20, b=60), paper_bgcolor="white", font=dict(color="#1a1a2e"))
                                st.plotly_chart(fig, use_container_width=True, key=f"chart_{sk}_dist_motivo")
                        else:
                            st.caption("Sem coluna de motivo viagem.")
                    elif grupo_col:
                        if sk == "Transporte":
                            ct1, ct2 = st.columns([1, 1])
                            with ct1:
                                cia_col = next((c for c in df_st.columns if "cia" in c.lower() or "companhia" in c.lower()), None)
                                if cia_col:
                                    st.markdown("<h3 style='color:#ffffff; margin-bottom:0.5rem;'>Total por CIA</h3>", unsafe_allow_html=True)
                                    scia_st = df_st.groupby(cia_col)[val_col].sum().sort_values(ascending=True)
                                    fig = go.Figure(go.Bar(x=scia_st.values, y=scia_st.index, orientation="h",
                                        marker=dict(color=scia_st.values, colorscale="Blues", line=dict(width=0)),
                                        text=scia_st.apply(lambda x: f"R$ {x:,.0f}"), textposition="outside"))
                                    fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10),
                                        paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
                                    fig.update_traces(hovertemplate="R$ %{x:,.2f}<extra></extra>")
                                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{sk}_total_cia")
                                else:
                                    st.caption("Sem coluna de CIA.")
                            with ct2:
                                td_col = next((c for c in df_st.columns if "terminal" in c.lower()), None)
                                if not td_col:
                                    td_col = next((c for c in df_st.columns if "destino" in c.lower()), None)
                                if td_col:
                                    st.markdown("<h3 style='color:#ffffff; margin-bottom:0.5rem;'>Total por Terminal Destino</h3>", unsafe_allow_html=True)
                                    std_st = df_st.groupby(td_col)[val_col].sum().sort_values(ascending=True)
                                    fig = go.Figure(go.Bar(x=std_st.values, y=std_st.index, orientation="h",
                                        marker=dict(color=std_st.values, colorscale="Blues", line=dict(width=0)),
                                        text=std_st.apply(lambda x: f"R$ {x:,.0f}"), textposition="outside"))
                                    fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10),
                                        paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
                                    fig.update_traces(hovertemplate="R$ %{x:,.2f}<extra></extra>")
                                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{sk}_total_terminal")
                                else:
                                    st.caption("Sem coluna de terminal/destino.")
                        else:
                            if sk == "Reembolsos":
                                r1c1, r1c2 = st.columns([1, 1])
                                with r1c1:
                                    st.markdown("<h3 style='color:#ffffff; margin-bottom:0.5rem;'>Total por Despesa</h3>", unsafe_allow_html=True)
                                    gs = df_st.groupby(grupo_col)[val_col].sum().sort_values(ascending=True).tail(15)
                                    fig = go.Figure(go.Bar(x=gs.values, y=gs.index, orientation="h",
                                        marker=dict(color=gs.values, colorscale="Blues", line=dict(width=0)),
                                        text=gs.apply(lambda x: f"R$ {x:,.0f}"), textposition="outside"))
                                    fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10),
                                        paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
                                    fig.update_traces(hovertemplate="R$ %{x:,.2f}<extra></extra>")
                                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{sk}_total_despesa")
                                with r1c2:
                                    ped_col_st = next((c for c in df_st.columns if "pedido" in c.lower()), None)
                                    if ped_col_st and VIAJANTE_REVERSE_MAP:
                                        df_st["Viajante"] = df_st[ped_col_st].astype(str).str.strip().str.lstrip("0").map(VIAJANTE_REVERSE_MAP)
                                    if "Viajante" in df_st.columns and df_st["Viajante"].notna().sum() > 0:
                                        st.markdown("<h3 style='color:#ffffff; margin-bottom:0.5rem;'>Total por Viajante <span style='font-size:10px; font-style:italic; color:#8899b8;'>(15 maiores gastos)</span></h3>", unsafe_allow_html=True)
                                        stotal_st = df_st.groupby("Viajante")[val_col].sum().sort_values(ascending=False).head(15)
                                        fig = go.Figure(go.Bar(x=stotal_st.values, y=stotal_st.index, orientation="h",
                                            marker=dict(color=stotal_st.values, colorscale="Blues", line=dict(width=0)),
                                            text=stotal_st.apply(lambda x: f"R$ {x:,.0f}"), textposition="outside"))
                                        fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10),
                                            paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
                                        fig.update_traces(hovertemplate="R$ %{x:,.2f}<extra></extra>")
                                        st.plotly_chart(fig, use_container_width=True, key=f"chart_{sk}_total_solicitante")
                                    else:
                                        st.caption("Sem viajante para esta despesa.")
                                if "Viajante" in df_st.columns and df_st["Viajante"].notna().sum() > 0:
                                    st.markdown("<h3 style='color:#ffffff; margin-bottom:0.5rem;'>Gastos: Viajante x Categoria</h3>", unsafe_allow_html=True)
                                    gs_st = df_st.groupby(["Viajante", grupo_col])[val_col].sum().reset_index()
                                    top_via = gs_st.groupby("Viajante")[val_col].sum().sort_values(ascending=False).head(10).index
                                    gs_st = gs_st[gs_st["Viajante"].isin(top_via)]
                                    via_tot = gs_st.groupby("Viajante")[val_col].sum()
                                    gs_st["Pct"] = gs_st.apply(lambda r: r[val_col] / via_tot.get(r["Viajante"], 1) * 100 if via_tot.get(r["Viajante"], 0) > 0 else 0, axis=1).round(1)
                                    fig = px.bar(gs_st, x="Viajante", y="Pct", color=grupo_col,
                                        color_discrete_sequence=px.colors.qualitative.Bold,
                                        barmode="stack", custom_data=[val_col])
                                    fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside", textfont=dict(size=9),
                                        hovertemplate="R$ %{customdata[0]:,.2f} (%{y:.1f}%)<extra>%{fullData.name}</extra>")
                                    fig.update_layout(height=400, margin=dict(l=10, r=120, t=50, b=10),
                                        paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white",
                                        yaxis=dict(title="%", range=[0, 115]),
                                        legend=dict(orientation="v", y=1, x=1.02, font=dict(size=8)))
                                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{sk}_sol_categoria")
                                st.markdown("<h3 style='color:#ffffff; margin-bottom:0.5rem;'>Distribuição por Despesa</h3>", unsafe_allow_html=True)
                                gc_val = df_st.groupby(grupo_col)[val_col].sum().sort_values(ascending=False)
                                fig = go.Figure(go.Bar(x=gc_val.index, y=gc_val.values,
                                    marker=dict(color=gc_val.values, colorscale="Blues", line=dict(width=0)),
                                    text=gc_val.apply(lambda x: f"R$ {x:,.0f}"), textposition="outside"))
                                fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10),
                                    paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(title=None), yaxis=dict(title="R$"))
                                fig.update_traces(hovertemplate="R$ %{y:,.2f}<extra></extra>")
                                st.plotly_chart(fig, use_container_width=True, key=f"chart_{sk}_dist_despesa")
                                desp_col = next((c for c in df_st.columns if "descri" in c.lower()), None)
                                if desp_col and grupo_col:
                                    st.subheader("Subcategorias")
                                    cat_order = df_st.groupby(grupo_col)[val_col].sum().sort_values(ascending=False).index
                                    sc1, sc2 = st.columns(2)
                                    sc_cols = [sc1, sc2]
                                    for idx, cat in enumerate(cat_order):
                                        mask = df_st[grupo_col] == cat
                                        _lb = "_desp_clean" if "_desp_clean" in df_st.columns else desp_col
                                        sub_df = df_st[mask].groupby(_lb)[val_col].sum().sort_values(ascending=False).head(5)
                                        if sub_df.empty: continue
                                        with sc_cols[idx % 2]:
                                            st.markdown(f"**{cat}** (R$ {sub_df.sum():,.2f})")
                                            sub_fig = go.Figure(go.Bar(x=sub_df.values, y=sub_df.index, orientation="h",
                                                marker=dict(color=sub_df.values, colorscale="Teal", line=dict(width=0)),
                                                text=sub_df.apply(lambda x: f"R$ {x:,.0f}"), textposition="outside"))
                                            sub_fig.update_layout(height=200, margin=dict(l=10, r=10, t=5, b=5),
                                                paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
                                            sub_fig.update_traces(hovertemplate="R$ %{x:,.2f}<extra></extra>")
                                            st.plotly_chart(sub_fig, use_container_width=True, key=f"chart_{sk}_subcat_{idx}")
                            else:
                                c1, c2 = st.columns([1, 1])
                                with c1:
                                    st.subheader(f"Total por {grupo_col}")
                                    gs = df_st.groupby(grupo_col)[val_col].sum().sort_values(ascending=True).tail(15)
                                    fig = go.Figure(go.Bar(x=gs.values, y=gs.index, orientation="h",
                                        marker=dict(color=gs.values, colorscale="Blues", line=dict(width=0)),
                                        text=gs.apply(lambda x: f"R$ {x:,.0f}"), textposition="outside"))
                                    fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10),
                                        paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
                                    fig.update_traces(hovertemplate="R$ %{x:,.2f}<extra></extra>")
                                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{sk}_total_grupo")
                                with c2:
                                    st.subheader(f"Distribuição por {grupo_col}")
                                    gc = df_st[grupo_col].value_counts()
                                    fig = go.Figure(data=[go.Pie(labels=gc.index, values=gc.values, hole=0.55,
                                        marker=dict(colors=px.colors.sequential.Blues[::-1][:len(gc)]),
                                        textinfo="label+percent", textposition="outside", showlegend=False)])
                                    fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="white", font=dict(color="#1a1a2e"))
                                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{sk}_dist_grupo")
                                desp_col = next((c for c in df_st.columns if "descri" in c.lower()), None)
                                if desp_col and grupo_col:
                                    st.subheader("Subcategorias")
                                    cat_order = df_st.groupby(grupo_col)[val_col].sum().sort_values(ascending=False).index
                                    sc1, sc2 = st.columns(2)
                                    sc_cols = [sc1, sc2]
                                    for idx, cat in enumerate(cat_order):
                                        mask = df_st[grupo_col] == cat
                                        sub_df = df_st[mask].groupby(desp_col)[val_col].sum().sort_values(ascending=False).head(5)
                                        if sub_df.empty: continue
                                        with sc_cols[idx % 2]:
                                            st.markdown(f"**{cat}** (R$ {sub_df.sum():,.2f})")
                                            sub_fig = go.Figure(go.Bar(x=sub_df.values, y=sub_df.index, orientation="h",
                                                marker=dict(color=sub_df.values, colorscale="Teal", line=dict(width=0)),
                                                text=sub_df.apply(lambda x: f"R$ {x:,.0f}"), textposition="outside"))
                                            sub_fig.update_layout(height=200, margin=dict(l=10, r=10, t=5, b=5),
                                                paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
                                            sub_fig.update_traces(hovertemplate="R$ %{x:,.2f}<extra></extra>")
                                            st.plotly_chart(sub_fig, use_container_width=True, key=f"chart_{sk}_subcat2_{idx}")

                    st.markdown("</div>", unsafe_allow_html=True)

                    # ── GRAFICOS POR VIAJANTE ──
                    if sk != "Reembolsos":
                        ped_col_st = next((c for c in df_st.columns if "pedido" in c.lower()), None)
                        if ped_col_st and VIAJANTE_REVERSE_MAP:
                            df_st["Viajante"] = df_st[ped_col_st].astype(str).str.strip().str.lstrip("0").map(VIAJANTE_REVERSE_MAP)
                            if df_st["Viajante"].notna().sum() > 0:
                                st.markdown('<div class="card">', unsafe_allow_html=True)
                                if sk == "Adiantamentos":
                                    mot_col = next((c for c in df_st.columns if "motivo" in c.lower()), None)
                                    if mot_col:
                                        st.markdown("<h3 style='color:#ffffff; margin-bottom:0.5rem;'>Total Viajante X Motivo Viagem</h3>", unsafe_allow_html=True)
                                        gs_st = df_st.groupby(["Viajante", mot_col])[val_col].sum().reset_index()
                                        top_via_mot = gs_st.groupby("Viajante")[val_col].sum().sort_values(ascending=False).head(10).index
                                        gs_st = gs_st[gs_st["Viajante"].isin(top_via_mot)]
                                        via_tot = gs_st.groupby("Viajante")[val_col].sum()
                                        gs_st["Pct"] = gs_st.apply(lambda r: r[val_col] / via_tot.get(r["Viajante"], 1) * 100 if via_tot.get(r["Viajante"], 0) > 0 else 0, axis=1).round(1)
                                        fig = px.bar(gs_st, x="Viajante", y="Pct", color=mot_col,
                                            color_discrete_sequence=px.colors.qualitative.Bold,
                                            barmode="stack", custom_data=[val_col])
                                        for i, tr in enumerate(fig.data):
                                            tr.texttemplate = "%{y:.1f}%"
                                            tr.textposition = "inside"
                                            tr.insidetextanchor = "middle"
                                            tr.textfont = dict(size=9)
                                            tr.hovertemplate = "R$ %{customdata[0]:,.2f} (%{y:.1f}%)<extra>%{fullData.name}</extra>"
                                        fig.update_layout(height=400, margin=dict(l=10, r=120, t=50, b=10),
                                            paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white",
                                            yaxis=dict(title="%", range=[0, 115]),
                                            legend=dict(orientation="v", y=1, x=1.02, font=dict(size=8)))
                                        for via in via_tot.index:
                                            fig.add_annotation(x=via, y=106, text=f"R$ {via_tot[via]:,.0f}",
                                                showarrow=False, font=dict(size=9, color="#1a1a2e"))
                                        st.plotly_chart(fig, use_container_width=True, key=f"chart_{sk}_sol_motivo")
                                    else:
                                        st.caption("Sem coluna de motivo viagem.")
                                    st.markdown("<h3 style='color:#ffffff; margin-bottom:0.5rem;'>Total por Viajante</h3>", unsafe_allow_html=True)
                                    stotal_st = df_st.groupby("Viajante")[val_col].sum().sort_values(ascending=False).head(10)
                                    fig = go.Figure(go.Bar(x=stotal_st.values, y=stotal_st.index, orientation="h",
                                        marker=dict(color=stotal_st.values, colorscale="Blues", line=dict(width=0)),
                                        text=stotal_st.apply(lambda x: f"R$ {x:,.0f}"), textposition="outside"))
                                    fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10),
                                        paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
                                    fig.update_traces(hovertemplate="R$ %{x:,.2f}<extra></extra>")
                                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{sk}_total_solicitante2")
                                else:
                                    gc1, gc2 = st.columns([1, 1])
                                    with gc1:
                                        if sk == "Aereos":
                                            or_col = next((c for c in df_st.columns if "origem" in c.lower()), None)
                                            des_col = next((c for c in df_st.columns if "destino" in c.lower()), None)
                                            if or_col and des_col:
                                                df_st["Trecho"] = df_st[or_col].astype(str).str.strip() + " → " + df_st[des_col].astype(str).str.strip()
                                                st.markdown("<h3 style='color:#ffffff; margin-bottom:0.5rem;'>Total por Trecho <span style='font-size:10px; font-style:italic; color:#8899b8;'>(Valores dos 20 maiores trechos)</span></h3>", unsafe_allow_html=True)
                                                sto_st = df_st.groupby("Trecho")[val_col].sum().sort_values(ascending=False).head(20).sort_values(ascending=True)
                                                fig = go.Figure(go.Bar(x=sto_st.values, y=sto_st.index, orientation="h",
                                                    marker=dict(color=sto_st.values, colorscale="Blues", line=dict(width=0)),
                                                    text=sto_st.apply(lambda x: f"R$ {x:,.0f}"), textposition="outside"))
                                                fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10),
                                                    paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
                                                fig.update_traces(hovertemplate="R$ %{x:,.2f}<extra></extra>")
                                                st.plotly_chart(fig, use_container_width=True, key=f"chart_{sk}_total_trecho")
                                            else:
                                                st.caption("Sem colunas de origem/destino.")
                                        elif sk == "Hoteis":
                                            cid_col = next((c for c in df_st.columns if "cidade" in c.lower()), None)
                                            if cid_col:
                                                st.markdown("<h3 style='color:#ffffff; margin-bottom:0.5rem;'>Total por Cidade <span style='font-size:10px; font-style:italic; color:#8899b8;'>(Total dos 20 maiores gastos por cidades)</span></h3>", unsafe_allow_html=True)
                                                scid_st = df_st.groupby(cid_col)[val_col].sum().sort_values(ascending=False).head(20).sort_values(ascending=True)
                                                fig = go.Figure(go.Bar(x=scid_st.values, y=scid_st.index, orientation="h",
                                                    marker=dict(color=scid_st.values, colorscale="Blues", line=dict(width=0)),
                                                    text=scid_st.apply(lambda x: f"R$ {x:,.0f}"), textposition="outside"))
                                                fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10),
                                                    paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
                                                fig.update_traces(hovertemplate="R$ %{x:,.2f}<extra></extra>")
                                                st.plotly_chart(fig, use_container_width=True, key=f"chart_{sk}_total_cidade")
                                            else:
                                                st.caption("Sem coluna de cidade.")
                                        elif sk == "Transporte":
                                            tr_cia = next((c for c in df_st.columns if "cia" in c.lower() or "companhia" in c.lower()), None)
                                            if tr_cia:
                                                st.markdown("<h3 style='color:#ffffff; margin-bottom:0.5rem;'>Gastos: Viajante x CIA</h3>", unsafe_allow_html=True)
                                                gs_st = df_st.groupby(["Viajante", tr_cia])[val_col].sum().reset_index()
                                                fig = px.bar(gs_st, x="Viajante", y=val_col, color=tr_cia,
                                                    color_discrete_sequence=px.colors.qualitative.Bold,
                                                    text_auto=".2s", barmode="group")
                                                fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=60),
                                                    paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(title=None))
                                                fig.update_traces(hovertemplate="R$ %{y:,.2f}<extra></extra>")
                                                st.plotly_chart(fig, use_container_width=True, key=f"chart_{sk}_sol_cia")
                                            else:
                                                st.caption("Sem coluna de CIA.")
                                        elif grupo_col:
                                            st.markdown("<h3 style='color:#ffffff; margin-bottom:0.5rem;'>Gastos: Viajante x Categoria</h3>", unsafe_allow_html=True)
                                            gs_st = df_st.groupby(["Viajante", grupo_col])[val_col].sum().reset_index()
                                            fig = px.bar(gs_st, x="Viajante", y=val_col, color=grupo_col,
                                                color_discrete_sequence=px.colors.qualitative.Bold,
                                                text_auto=".2s", barmode="group")
                                            fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=60),
                                                paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(title=None))
                                            fig.update_traces(hovertemplate="R$ %{y:,.2f}<extra></extra>")
                                            st.plotly_chart(fig, use_container_width=True, key=f"chart_{sk}_sol_categoria2")
                                        else:
                                            st.caption("Sem coluna de categoria.")
                                    with gc2:
                                        st.markdown("<h3 style='color:#ffffff; margin-bottom:0.5rem;'>Total por Viajante</h3>", unsafe_allow_html=True)
                                        stotal_st = df_st.groupby("Viajante")[val_col].sum().sort_values(ascending=False).head(10)
                                        fig = go.Figure(go.Bar(x=stotal_st.values, y=stotal_st.index, orientation="h",
                                            marker=dict(color=stotal_st.values, colorscale="Blues", line=dict(width=0)),
                                            text=stotal_st.apply(lambda x: f"R$ {x:,.0f}"), textposition="outside"))
                                        fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10),
                                            paper_bgcolor="white", font=dict(color="#1a1a2e"), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
                                        fig.update_traces(hovertemplate="R$ %{x:,.2f}<extra></extra>")
                                        st.plotly_chart(fig, use_container_width=True, key=f"chart_{sk}_total_solicitante3")
                                st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.subheader(f"📋 Registros - {sk}")

                    search_st = st.text_input("🔎 Buscar", placeholder="Digite para filtrar...", key=f"subtab_search_{sk}")
                    df_st_disp = df_st.copy()
                    if search_st:
                        mask = df_st_disp.astype(str).apply(lambda row: row.str.contains(search_st, case=False, na=False)).any(axis=1)
                        df_st_disp = df_st_disp[mask]
                    for c in df_st_disp.select_dtypes(include=["datetime64"]).columns:
                        df_st_disp[c] = df_st_disp[c].dt.strftime("%d/%m/%Y")
                    st.dataframe(df_st_disp, use_container_width=True, hide_index=True, height=400)
                    st.markdown("<br>", unsafe_allow_html=True)
                    s1, s2, s3 = st.columns(3)
                    csv_st = df_st_disp.to_csv(index=False).encode("utf-8-sig")
                    s1.download_button("📥 CSV", csv_st, f"{sk.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", use_container_width=True, key=f"dl_subtab_{sk}_csv")
                    output_st = io.BytesIO()
                    with pd.ExcelWriter(output_st, engine="openpyxl") as w: df_st_disp.to_excel(w, index=False, sheet_name=sk)
                    s2.download_button("📥 Excel", output_st.getvalue(), f"{sk.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key=f"dl_subtab_{sk}_xlsx")
                    s3.download_button("📥 JSON", df_st_disp.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8-sig"), f"{sk.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "application/json", use_container_width=True, key=f"dl_subtab_{sk}_json")
                    st.markdown("</div>", unsafe_allow_html=True)
