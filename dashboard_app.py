import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

st.set_page_config(page_title="Dashboard de Pedidos", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main > div { padding: 1rem 2rem; }
    .stApp { background-color: #f8f9fa; }
    .kpi-card { background: white; border-radius: 12px; padding: 1.2rem 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border-left: 4px solid #1a5276; margin-bottom: 0.5rem; }
    .kpi-card .label { font-size: 0.75rem; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-card .value { font-size: 1.6rem; font-weight: 700; color: #1a5276; margin-top: 0.2rem; }
    .kpi-card .sub { font-size: 0.8rem; color: #6c757d; margin-top: 0.1rem; }
    .card { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 1rem; }
    h1, h2, h3 { color: #1a5276; }
    .stButton > button { background: #1a5276; color: white; border: none; border-radius: 8px; padding: 0.4rem 1.5rem; font-weight: 500; }
    .stButton > button:hover { background: #154360; }
    div[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
    .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; padding: 0.5rem 1.2rem; font-weight: 500; }
    footer { display: none; }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("<h2 style='color:#1a5276; margin-bottom:0;'>📊 Dashboard</h2><p style='color:#6c757d; font-size:0.85rem; margin-top:0;'>Fujicom - Pedidos</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

GCP_JSON_SECRET = st.secrets.get("gcp_service_account") or st.secrets.get("gcp_service_account_json")
SHEET_URL_SECRET = st.secrets.get("sheet_url")
CLOUD_MODE = bool(GCP_JSON_SECRET and SHEET_URL_SECRET)

if CLOUD_MODE:
    st.sidebar.success("☁️ Modo nuvem")
else:
    st.sidebar.info("💻 Modo local")

USE_SAMPLE_DATA = st.sidebar.checkbox("Usar dados de exemplo", value=not CLOUD_MODE)

if not USE_SAMPLE_DATA and not CLOUD_MODE:
    st.sidebar.markdown("### 🔑 Conexão Google Sheets")
    json_key = st.sidebar.file_uploader("Service Account JSON", type="json")
    sheet_url = st.sidebar.text_input("URL da Planilha", placeholder="https://docs.google.com/spreadsheets/d/...")
    conectar = st.sidebar.button("Conectar", type="primary")

def parse_br(v):
    if pd.isna(v) or v == "" or v is None:
        return 0.0
    v = str(v).strip().replace(".", "").replace(",", ".")
    try:
        return float(v)
    except:
        return 0.0

STATUS_TRANSLATE = {
    "awaitingApprovalOfCost": "Aguardando Aprov. Custo",
    "awaitingIssue": "Aguardando Emissão",
    "approved": "Aprovado", "canceled": "Cancelado",
    "finalized": "Finalizado", "issued": "Emitido",
    "pending": "Pendente", "concluded": "Concluído",
}

@st.cache_data(ttl=300)
def load_sample_data():
    np.random.seed(42)
    n = 200
    pedidos = []
    status_opts = ["Aprovado", "Concluído", "Pendente", "Cancelado"]
    centros_custo = ["Comercial", "TI", "RH", "Financeiro", "Operações", "Diretoria"]
    colaboradores = ["Carlos Silva", "Ana Oliveira", "Bruno Santos", "Daniela Costa",
        "Eduardo Lima", "Fernanda Souza", "Gabriel Rocha", "Helena Martins",
        "Igor Pereira", "Julia Almeida"]
    fornecedores = ["Copastur", "Latam", "Azul", "Gol", "Localiza", "Booking", "Uber", "Decolar", "Airbnb", "Rappi"]
    categorias = ["Passagem Aérea", "Hotel", "Aluguel Carro", "Alimentação", "Uber/Táxi", "Pedágio", "Estacionamento", "Outros"]
    for i in range(n):
        data_emissao = datetime(2025, 1, 1) + timedelta(days=np.random.randint(0, 545), hours=np.random.randint(0, 23))
        data_viagem = data_emissao + timedelta(days=np.random.randint(1, 30))
        status = np.random.choice(status_opts, p=[0.4, 0.3, 0.2, 0.1])
        valor = round(np.random.gamma(2, 500) + 100, 2)
        if status == "Cancelado": valor = 0
        pedidos.append({
            "Nº Pedido": f"OS-{25000 + i}", "Data Emissão": data_emissao, "Data Viagem": data_viagem,
            "Solicitante": np.random.choice(colaboradores), "Centro Custo": np.random.choice(centros_custo),
            "Departamento": np.random.choice(["Vendas", "Admin", "Operacional"]), "Status": status,
            "Valor Total": valor, "Categoria": np.random.choice(categorias),
            "Fornecedor": np.random.choice(fornecedores),
            "Destino": np.random.choice(["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Brasília", "Salvador", "Recife", "Fortaleza", "Curitiba", "Porto Alegre", "Manaus"]),
            "Motivo Viagem": np.random.choice(["Reunião Cliente", "Treinamento", "Conferência", "Vistoria Técnica", "Visita Comercial", "Auditoria"]),
            "Qtd Diárias": np.random.randint(1, 10), "Qtd Passageiros": np.random.randint(1, 4),
        })
    df = pd.DataFrame(pedidos)
    df["Mês"] = df["Data Emissão"].dt.month_name()
    return df

@st.cache_data(ttl=300)
def load_pedidos_gsheets(json_key_file, sheet_url):
    import gspread, json
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    if isinstance(json_key_file, (bytes, str)):
        creds_dict = json.loads(json_key_file)
    else:
        creds_dict = json_key_file
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url)
    ws = sheet.worksheet("Pedidos")
    dados = ws.get_all_records()
    return pd.DataFrame(dados)

@st.cache_data(ttl=300)
def load_reembolsos_gsheets(json_key_file, sheet_url):
    import gspread, json
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    if isinstance(json_key_file, (bytes, str)):
        creds_dict = json.loads(json_key_file)
    else:
        creds_dict = json_key_file
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url)
    ws = sheet.worksheet("Reembolsos")
    dados = ws.get_all_records()
    return pd.DataFrame(dados)

if USE_SAMPLE_DATA:
    df_pedidos = load_sample_data()
    df_reemb = None
    st.sidebar.success("✅ Dados de exemplo")
elif CLOUD_MODE:
    with st.spinner("Carregando dados..."):
        try:
            import json
            js = json.dumps(GCP_JSON_SECRET) if not isinstance(GCP_JSON_SECRET, str) else GCP_JSON_SECRET
            df_pedidos = load_pedidos_gsheets(js, SHEET_URL_SECRET)
            df_reemb = load_reembolsos_gsheets(js, SHEET_URL_SECRET)
            st.sidebar.success(f"✅ {len(df_pedidos)} pedidos + {len(df_reemb)} reembolsos")
        except Exception as e:
            st.sidebar.error(f"Erro: {e}")
            df_pedidos = load_sample_data()
            df_reemb = None
else:
    if "df_loaded" in st.session_state and st.session_state.df_loaded is not None:
        df_pedidos = st.session_state.df_loaded
        df_reemb = st.session_state.get("df_reemb")
    elif conectar and json_key and sheet_url:
        with st.spinner("Carregando..."):
            try:
                jk = json_key.read()
                df_pedidos = load_pedidos_gsheets(jk, sheet_url)
                df_reemb = load_reembolsos_gsheets(jk, sheet_url)
                st.session_state.df_loaded = df_pedidos
                st.session_state.df_reemb = df_reemb
                st.sidebar.success(f"✅ {len(df_pedidos)} registros")
            except Exception as e:
                st.sidebar.error(f"Erro: {e}")
                df_pedidos = load_sample_data()
                df_reemb = None
    else:
        st.info("👈 Conecte-se ao Google Sheets ou marque 'Dados de exemplo'")
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
COLS["DATA"] = next((c for c in df_pedidos.columns if "data" in c.lower() and "pedido" in c.lower()), None)
if not COLS["DATA"]: COLS["DATA"] = next((c for c in df_pedidos.columns if "data" in c.lower() and "emiss" in c.lower()), None)
if not COLS["DATA"]: COLS["DATA"] = next((c for c in df_pedidos.columns if "data" in c.lower() and "cria" in c.lower()), None)
COLS["TIPO"] = next((c for c in df_pedidos.columns if "tipo" in c.lower()), None)

# ── PARSE ──
if COLS["VALOR"]:
    df_pedidos[COLS["VALOR"]] = df_pedidos[COLS["VALOR"]].apply(parse_br)
if COLS["STATUS"]:
    df_pedidos[COLS["STATUS"]] = df_pedidos[COLS["STATUS"]].astype(str).map(STATUS_TRANSLATE).fillna(df_pedidos[COLS["STATUS"]].astype(str)).replace("", "Indefinido")
for col in list(COLS.values()):
    if col and any(k in col.lower() for k in ["data"]):
        try: df_pedidos[col] = pd.to_datetime(df_pedidos[col], errors="coerce", dayfirst=True)
        except: pass

# ── REEMBOLSOS PARSE ──
if df_reemb is not None and not df_reemb.empty:
    REEMB_CAT = next((c for c in df_reemb.columns if "categoria" in c.lower()), None)
    REEMB_VAL = next((c for c in df_reemb.columns if c.lower() in ["valor total", "total", "valor"]), None)
    REEMB_DESP = next((c for c in df_reemb.columns if "despesa" in c.lower()), None)
    REEMB_PED = next((c for c in df_reemb.columns if "pedido" in c.lower()), None)
    if REEMB_VAL: df_reemb[REEMB_VAL] = df_reemb[REEMB_VAL].apply(parse_br)
    if REEMB_PED: df_reemb[REEMB_PED] = df_reemb[REEMB_PED].astype(str)

# ── SIDEBAR FILTERS ──
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Filtros")

filtros_aplicados = 0
df_filt = df_pedidos.copy()

data_col = COLS["DATA"]
data_ok = data_col and pd.api.types.is_datetime64_any_dtype(df_filt[data_col])
if data_ok:
    min_d, max_d = df_filt[data_col].min().date(), df_filt[data_col].max().date()
    dr = st.sidebar.date_input("Período", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    if len(dr) == 2:
        df_filt = df_filt[(df_filt[data_col].dt.date >= dr[0]) & (df_filt[data_col].dt.date <= dr[1])]
        filtros_aplicados += 1

# ── SINGLE ORDER FILTER ──
st.sidebar.markdown("### 🔎 Pedido Específico")
busca_pedido = st.sidebar.text_input("Nº do Pedido", placeholder="Ex: 1935")
if busca_pedido:
    if COLS["PEDIDO"]:
        df_filt[COLS["PEDIDO"]] = df_filt[COLS["PEDIDO"]].astype(str)
        mask = df_filt[COLS["PEDIDO"]].str.contains(busca_pedido.strip(), case=False, na=False)
        if mask.any():
            df_filt = df_filt[mask]
            filtros_aplicados += 1
            st.sidebar.success(f"Pedido {busca_pedido} encontrado")
        else:
            st.sidebar.warning("Pedido não encontrado")

if COLS["STATUS"]:
    opts = sorted(df_pedidos[COLS["STATUS"]].dropna().unique())
    sel = st.sidebar.multiselect("Status", opts, default=opts)
    if sel and len(sel) < len(opts):
        df_filt = df_filt[df_filt[COLS["STATUS"]].isin(sel)]
        filtros_aplicados += 1

if COLS["SOLICITANTE"]:
    opts = sorted(df_pedidos[COLS["SOLICITANTE"]].dropna().unique())
    sel = st.sidebar.multiselect("Solicitante", opts, default=[])
    if sel:
        df_filt = df_filt[df_filt[COLS["SOLICITANTE"]].isin(sel)]
        filtros_aplicados += 1

if COLS["CCUSTO"]:
    opts = sorted(df_pedidos[COLS["CCUSTO"]].dropna().unique())
    sel = st.sidebar.multiselect("Centro de Custo", opts, default=[])
    if sel:
        df_filt = df_filt[df_filt[COLS["CCUSTO"]].isin(sel)]
        filtros_aplicados += 1

if COLS["EMPRESA"]:
    opts = sorted(df_pedidos[COLS["EMPRESA"]].dropna().unique())
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

st.sidebar.markdown("---")

# ── MAIN KPIs ──
total_gasto = df_filt[COLS["VALOR"]].sum() if COLS["VALOR"] else 0
total_pedidos = len(df_filt)
ticket_medio = total_gasto / total_pedidos if total_pedidos > 0 else 0

st.markdown(f"""
<div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
    <div>
        <h1 style="margin:0;">📊 Dashboard de Pedidos</h1>
        <p style="color:#6c757d; margin:0;">{total_pedidos} pedidos • R$ {total_gasto:,.2f} em gastos</p>
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
    st.markdown(f"""<div class="kpi-card"><div class="label">🎫 Ticket Médio</div><div class="value">R$ {ticket_medio:,.2f}</div><div class="sub">por pedido</div></div>""", unsafe_allow_html=True)
with k4:
    cat_count = df_filt[COLS["STATUS"]].nunique() if COLS["STATUS"] else 0
    forn_count = df_filt[COLS["AGENCIA"]].nunique() if COLS["AGENCIA"] else 0
    st.markdown(f"""<div class="kpi-card"><div class="label">📊 Abrangência</div><div class="value">{cat_count} status</div><div class="sub">{forn_count} agências</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ──
tab_labels = ["📈 Visão Geral"]
if COLS["STATUS"]: tab_labels.append("📊 Por Status")
if COLS["SOLICITANTE"]: tab_labels.append("👥 Por Solicitante")
if data_ok: tab_labels.append("📅 Tendência")
tab_labels.append("📋 Dados Exportáveis")
tab_labels.append("💰 Reembolsos")

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
                plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Distribuição por Empresa")
        if COLS["EMPRESA"]:
            ec = df_filt[COLS["EMPRESA"]].value_counts()
            fig = go.Figure(data=[go.Pie(labels=ec.index, values=ec.values, hole=0.55,
                marker=dict(colors=px.colors.sequential.Blues[::-1][:len(ec)]),
                textinfo="label+percent", textposition="outside", showlegend=False)])
            fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Top Agências")
        if COLS["AGENCIA"] and COLS["VALOR"]:
            g = df_filt.groupby(COLS["AGENCIA"])[COLS["VALOR"]].sum().sort_values(ascending=False).head(10)
            fig = px.bar(g, x=g.values, y=g.index, orientation="h", color=g.values, color_continuous_scale="Blues")
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Motivos de Viagem")
        if COLS["MOTIVO"]:
            mc = df_filt[COLS["MOTIVO"]].value_counts().head(10)
            fig = px.bar(mc, x=mc.values, y=mc.index, orientation="h", color=mc.values, color_continuous_scale="Teal")
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(fig, use_container_width=True)
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
            fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
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

# TAB 3: Por Solicitante
if COLS["SOLICITANTE"]:
    with tabs[ti]:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Ranking de Gastos")
            if COLS["VALOR"]:
                g = df_filt.groupby(COLS["SOLICITANTE"])[COLS["VALOR"]].sum().sort_values(ascending=True).tail(20)
                fig = go.Figure(go.Bar(x=g.values, y=g.index, orientation="h",
                    marker=dict(color=g.values, colorscale="Blues", line=dict(width=0)),
                    text=g.apply(lambda x: f"R$ {x:,.0f}"), textposition="outside"))
                fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
                st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Volume de Pedidos")
            sc = df_filt[COLS["SOLICITANTE"]].value_counts().sort_values(ascending=True).tail(20)
            fig = go.Figure(go.Bar(x=sc.values, y=sc.index, orientation="h",
                marker=dict(color=sc.values, colorscale="Teal", line=dict(width=0)),
                text=sc.values, textposition="outside"))
            fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
            st.plotly_chart(fig, use_container_width=True)
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
                tr = df_filt.set_index(data_col).resample("ME")[COLS["VALOR"]].sum().reset_index()
                fig = px.line(tr, x=data_col, y=COLS["VALOR"], markers=True)
                fig.update_traces(line=dict(color="#1a5276", width=3), marker=dict(size=6))
                fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white", xaxis=dict(title=None), yaxis=dict(title="R$"))
                fig.update_yaxes(tickprefix="R$ ")
                st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Volume de Pedidos por Mês")
            ct = df_filt.set_index(data_col).resample("ME")[COLS["PEDIDO"] or df_filt.columns[0]].count().reset_index()
            fig = px.bar(ct, x=data_col, y=COLS["PEDIDO"] or df_filt.columns[0], color_discrete_sequence=["#2e86c1"])
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white", xaxis=dict(title=None), yaxis=dict(title="Pedidos"))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        ti += 1

# TAB 5: Tabela Exportável
with tabs[ti]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Dados Filtrados")
    st.caption(f"{len(df_filt)} registros • {len(df_filt.columns)} colunas")
    export_cols = [c for c in df_filt.columns]
    search = st.text_input("🔎 Buscar na tabela", placeholder="Digite para filtrar...")
    col_sel = st.multiselect("Colunas", options=export_cols, default=export_cols, label_visibility="collapsed")
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
    d1.download_button("📥 CSV", csv, f"pedidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", use_container_width=True)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as w: df_disp.to_excel(w, index=False, sheet_name="Pedidos")
    d2.download_button("📥 Excel", output.getvalue(), f"pedidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    d3.download_button("📥 JSON", df_disp.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8-sig"), f"pedidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "application/json", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    ti += 1

# TAB 6: Reembolsos
with tabs[ti]:
    if df_reemb is not None and not df_reemb.empty:
        df_r = df_reemb.copy()
        if COLS["PEDIDO"] and REEMB_PED:
            pedidos_filtrados = set(df_filt[COLS["PEDIDO"]].astype(str))
            df_r = df_r[df_r[REEMB_PED].astype(str).isin(pedidos_filtrados)]
        elif busca_pedido and REEMB_PED:
            df_r = df_r[df_r[REEMB_PED].astype(str).str.contains(busca_pedido.strip(), case=False, na=False)]

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("💰 Despesas Reembolsáveis")
        st.caption(f"{len(df_r)} despesas • R$ {df_r[REEMB_VAL].sum():,.2f}" if REEMB_VAL else f"{len(df_r)} despesas")

        r1, r2, r3, r4 = st.columns(4)
        r1.markdown(f"""<div class="kpi-card"><div class="label">💵 Total Reembolsável</div><div class="value">R$ {df_r[REEMB_VAL].sum():,.2f}</div></div>""" if REEMB_VAL else "", unsafe_allow_html=True)
        r2.markdown(f"""<div class="kpi-card"><div class="label">📝 Total Despesas</div><div class="value">{len(df_r)}</div></div>""", unsafe_allow_html=True)

        if REEMB_CAT and REEMB_VAL:
            cats = df_r.groupby(REEMB_CAT)[REEMB_VAL].sum().sort_values(ascending=False)
            r3.markdown(f"""<div class="kpi-card"><div class="label">🍽️ Alimentação</div><div class="value">R$ {cats.get('Alimentação', 0):,.2f}</div></div>""" if "Alimentação" in cats.index else "", unsafe_allow_html=True)
            uber_val = sum(v for k, v in cats.items() if any(x in k.lower() for x in ["transporte", "uber", "táxi", "taxi"]))
            r4.markdown(f"""<div class="kpi-card"><div class="label">🚕 Uber/Táxi</div><div class="value">R$ {uber_val:,.2f}</div></div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)

        c1, c2 = st.columns([1, 1])
        with c1:
            st.subheader("Gastos por Categoria")
            if REEMB_CAT and REEMB_VAL:
                cs = df_r.groupby(REEMB_CAT)[REEMB_VAL].sum().sort_values(ascending=True)
                fig = go.Figure(go.Bar(x=cs.values, y=cs.index, orientation="h",
                    marker=dict(color=cs.values, colorscale="Blues", line=dict(width=0)),
                    text=cs.apply(lambda x: f"R$ {x:,.0f}"), textposition="outside"))
                fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.subheader("Distribuição por Categoria")
            cc = df_r[REEMB_CAT].value_counts()
            fig = go.Figure(data=[go.Pie(labels=cc.index, values=cc.values, hole=0.55,
                marker=dict(colors=px.colors.sequential.Blues[::-1][:len(cc)]),
                textinfo="label+percent", textposition="outside", showlegend=False)])
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if REEMB_DESP:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Top 10 Tipos de Despesa")
            if REEMB_VAL:
                ds = df_r.groupby(REEMB_DESP)[REEMB_VAL].sum().sort_values(ascending=False).head(10)
                fig = go.Figure(go.Bar(x=ds.values, y=ds.index, orientation="h",
                    marker=dict(color=ds.values, colorscale="Teal", line=dict(width=0)),
                    text=ds.apply(lambda x: f"R$ {x:,.0f}"), textposition="outside"))
                fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
                st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📋 Despesas Detalhadas")
        cols_r = [c for c in df_r.columns if c not in ["Ativo", "Verificado", "Código Moeda", "Moeda Ref.", "Cotação Ref."]]
        sr = st.text_input("🔎 Buscar despesa", placeholder="alimentação, uber...", key="reemb_search")
        df_rd = df_r[cols_r].copy()
        if sr:
            df_rd = df_rd[df_rd.astype(str).apply(lambda row: row.str.contains(sr, case=False, na=False)).any(axis=1)]
        for c in df_rd.select_dtypes(include=["datetime64"]).columns:
            df_rd[c] = df_rd[c].dt.strftime("%d/%m/%Y")
        st.dataframe(df_rd, use_container_width=True, hide_index=True, height=400)
        st.download_button("📥 Exportar Reembolsos CSV", df_rd.to_csv(index=False).encode("utf-8-sig"),
            f"reembolsos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Dados de reembolso não disponíveis (use dados de exemplo ou conecte ao Google Sheets)")
