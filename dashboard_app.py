import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

st.set_page_config(
    page_title="Dashboard de Pedidos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main > div { padding: 1rem 2rem; }
    .stApp { background-color: #f8f9fa; }
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 4px solid #1a5276;
        margin-bottom: 0.5rem;
    }
    .kpi-card .label { font-size: 0.75rem; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-card .value { font-size: 1.6rem; font-weight: 700; color: #1a5276; margin-top: 0.2rem; }
    .kpi-card .sub { font-size: 0.8rem; color: #6c757d; margin-top: 0.1rem; }
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
    }
    h1, h2, h3 { color: #1a5276; }
    .stButton > button {
        background: #1a5276; color: white; border: none;
        border-radius: 8px; padding: 0.4rem 1.5rem; font-weight: 500;
    }
    .stButton > button:hover { background: #154360; }
    div[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
    .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0; padding: 0.5rem 1.2rem; font-weight: 500;
    }
    .css-1d391kg { background-color: white; }
    .sidebar .sidebar-content { background: white; }
    footer { display: none; }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown(
    "<h2 style='color:#1a5276; margin-bottom:0;'>📊 Dashboard</h2>"
    "<p style='color:#6c757d; font-size:0.85rem; margin-top:0;'>Fujicom - Pedidos</p>",
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

# --- Ambiente: Streamlit Cloud vs Local ---
GCP_JSON_SECRET = st.secrets.get("gcp_service_account") or st.secrets.get("gcp_service_account_json")
SHEET_URL_SECRET = st.secrets.get("sheet_url")
CLOUD_MODE = bool(GCP_JSON_SECRET and SHEET_URL_SECRET)

if CLOUD_MODE:
    st.sidebar.success("☁️ Modo nuvem — conectado ao Google Sheets")
else:
    st.sidebar.info("💻 Modo local — use upload manual ou dados de exemplo")

USE_SAMPLE_DATA = st.sidebar.checkbox("Usar dados de exemplo",
    value=not CLOUD_MODE,
    help="Marque para testar sem conectar ao Google Sheets")

if not USE_SAMPLE_DATA and not CLOUD_MODE:
    st.sidebar.markdown("### 🔑 Conexão Google Sheets")
    json_key = st.sidebar.file_uploader("Service Account JSON", type="json")
    sheet_url = st.sidebar.text_input("URL da Planilha",
        placeholder="https://docs.google.com/spreadsheets/d/...")
    conectar = st.sidebar.button("Conectar", type="primary")

@st.cache_data(ttl=300)
def load_sample_data():
    np.random.seed(42)
    n = 200
    pedidos = []
    status_opts = ["Aprovado", "Concluído", "Pendente", "Cancelado"]
    centros_custo = ["Comercial", "TI", "RH", "Financeiro", "Operações", "Diretoria"]
    colaboradores = [
        "Carlos Silva", "Ana Oliveira", "Bruno Santos", "Daniela Costa",
        "Eduardo Lima", "Fernanda Souza", "Gabriel Rocha", "Helena Martins",
        "Igor Pereira", "Julia Almeida"
    ]
    fornecedores = ["Copastur", "Latam", "Azul", "Gol", "Localiza", "Booking",
                    "Uber", "Decolar", "Airbnb", "Rappi"]
    categorias = ["Passagem Aérea", "Hotel", "Aluguel Carro", "Alimentação",
                  "Uber/Táxi", "Pedágio", "Estacionamento", "Outros"]

    for i in range(n):
        data_emissao = datetime(2025, 1, 1) + timedelta(
            days=np.random.randint(0, 545), hours=np.random.randint(0, 23))
        data_viagem = data_emissao + timedelta(days=np.random.randint(1, 30))
        status = np.random.choice(status_opts, p=[0.4, 0.3, 0.2, 0.1])
        valor = round(np.random.gamma(2, 500) + 100, 2)
        if status == "Cancelado":
            valor = 0

        pedidos.append({
            "Nº Pedido": f"OS-{25000 + i}",
            "Data Emissão": data_emissao,
            "Data Viagem": data_viagem,
            "Solicitante": np.random.choice(colaboradores),
            "Centro Custo": np.random.choice(centros_custo),
            "Departamento": np.random.choice(["Vendas", "Admin", "Operacional"]),
            "Status": status,
            "Valor Total": valor,
            "Categoria": np.random.choice(categorias),
            "Fornecedor": np.random.choice(fornecedores),
            "Destino": np.random.choice([
                "São Paulo", "Rio de Janeiro", "Belo Horizonte",
                "Brasília", "Salvador", "Recife", "Fortaleza",
                "Curitiba", "Porto Alegre", "Manaus"]),
            "Motivo Viagem": np.random.choice([
                "Reunião Cliente", "Treinamento", "Conferência",
                "Vistoria Técnica", "Visita Comercial", "Auditoria"]),
            "Qtd Diárias": np.random.randint(1, 10),
            "Qtd Passageiros": np.random.randint(1, 4),
        })
    df = pd.DataFrame(pedidos)
    df["Mês"] = df["Data Emissão"].dt.month_name(locale="pt_BR.UTF-8" if False else None)
    try:
        df["Mês"] = df["Data Emissão"].dt.month_name()
    except:
        df["Mês"] = df["Data Emissão"].dt.month.map({
            1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
            7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"})
    df["Ano"] = df["Data Emissão"].dt.year.astype(int)
    df["Trimestre"] = df["Data Emissão"].dt.quarter.map(
        {1:"Q1",2:"Q2",3:"Q3",4:"Q4"})
    df["Dia Semana"] = df["Data Emissão"].dt.day_name()
    df["Mês/Ano"] = df["Data Emissão"].dt.to_period("M").astype(str)
    return df

@st.cache_data
def load_from_gsheets(json_key_file, sheet_url):
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    import json
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    if isinstance(json_key_file, (bytes, str)):
        creds_dict = json.loads(json_key_file)
    else:
        creds_dict = json_key_file
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url)
    worksheets = sheet.worksheets()
    main_sheet_name = None
    for ws in worksheets:
        if ws.title.lower() in ("pedidos", "pedido"):
            main_sheet_name = ws.title
            break
    if not main_sheet_name:
        main_sheet_name = worksheets[0].title
    df_main = pd.DataFrame(sheet.worksheet(main_sheet_name).get_all_records())
    key_col = None
    for col in df_main.columns:
        if any(kw in col.lower() for kw in ["pedido", "os", "ordem", "num", "id", "chave"]):
            key_col = col
            break
    if not key_col:
        key_col = df_main.columns[0]
    df_main[key_col] = df_main[key_col].astype(str)
    for ws in worksheets:
        name = ws.title.strip()
        if name == main_sheet_name:
            continue
        try:
            df_tab = pd.DataFrame(ws.get_all_records())
            if df_tab.empty:
                continue
            df_tab[key_col] = df_tab[key_col].astype(str)
            for col in df_tab.columns:
                if col != key_col:
                    new_name = f"{name}: {col}"
                    if new_name not in df_main.columns and col not in df_main.columns:
                        df_tab.rename(columns={col: new_name}, inplace=True)
            merge_cols = [c for c in df_tab.columns if c in df_main.columns or c == key_col]
            df_main = df_main.merge(
                df_tab[merge_cols + [c for c in df_tab.columns if c not in merge_cols and c != key_col]],
                on=key_col, how="left", suffixes=("", f"_{name}")
            )
        except Exception:
            continue
    return df_main

if USE_SAMPLE_DATA:
    df = load_sample_data()
    st.sidebar.success("✅ Dados de exemplo carregados")
elif CLOUD_MODE:
    with st.spinner("Carregando dados do Google Sheets..."):
        try:
            import json
            if isinstance(GCP_JSON_SECRET, str):
                df = load_from_gsheets(GCP_JSON_SECRET, SHEET_URL_SECRET)
            else:
                df = load_from_gsheets(json.dumps(GCP_JSON_SECRET), SHEET_URL_SECRET)
            st.sidebar.success(f"✅ {len(df)} registros carregados da planilha")
        except Exception as e:
            st.sidebar.error(f"Erro ao carregar: {e}")
            df = load_sample_data()
else:
    if "df_loaded" not in st.session_state:
        st.session_state.df_loaded = None

    if conectar and json_key and sheet_url:
        with st.spinner("Carregando dados do Google Sheets..."):
            try:
                df = load_from_gsheets(json_key.read(), sheet_url)
                st.session_state.df_loaded = df
                st.sidebar.success(f"✅ {len(df)} registros carregados")
            except Exception as e:
                st.sidebar.error(f"Erro: {e}")
                df = load_sample_data()
    elif st.session_state.df_loaded is not None:
        df = st.session_state.df_loaded
    else:
        st.info("👈 Conecte-se ao Google Sheets ou marque 'Usar dados de exemplo'")
        df = None

if df is None:
    st.stop()

cat_map = {
    "Passagem Aérea": "🛩️", "Hotel": "🏨", "Aluguel Carro": "🚗",
    "Alimentação": "🍽️", "Uber/Táxi": "🚕", "Pedágio": "🛣️",
    "Estacionamento": "🅿️", "Outros": "📌",
    "Aéreo": "🛩️", "Hospedagem": "🏨", "Transporte": "🚗",
}
df["Ícone"] = df["Categoria"].map(cat_map).fillna("📌")

date_cols = [c for c in df.columns if "data" in c.lower() or "emiss" in c.lower() or "viagem" in c.lower()]
for c in date_cols:
    try:
        df[c] = pd.to_datetime(df[c], errors="coerce", dayfirst=True)
    except:
        pass

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Filtros")

filtros_aplicados = 0
df_filtered = df.copy()

# --- Filtro de data ---
data_cols_present = [c for c in date_cols if c in df.columns and pd.api.types.is_datetime64_any_dtype(df[c])]
if data_cols_present:
    default_col = data_cols_present[0]
    min_d = df[default_col].min().date()
    max_d = df[default_col].max().date()
    date_range = st.sidebar.date_input(
        "Período",
        value=(min_d, max_d),
        min_value=min_d,
        max_value=max_d,
    )
    if len(date_range) == 2:
        mask = (df[default_col].dt.date >= date_range[0]) & (df[default_col].dt.date <= date_range[1])
        df_filtered = df_filtered[mask]
        filtros_aplicados += 1

# --- Filtro de status ---
if "Status" in df.columns:
    status_opts_all = sorted(df["Status"].dropna().unique())
    status_sel = st.sidebar.multiselect("Status", status_opts_all, default=status_opts_all)
    if status_sel and len(status_sel) < len(status_opts_all):
        df_filtered = df_filtered[df_filtered["Status"].isin(status_sel)]
        filtros_aplicados += 1

# --- Filtro de categoria ---
if "Categoria" in df.columns:
    cat_opts_all = sorted(df["Categoria"].dropna().unique())
    cat_sel = st.sidebar.multiselect("Categoria", cat_opts_all, default=cat_opts_all)
    if cat_sel and len(cat_sel) < len(cat_opts_all):
        df_filtered = df_filtered[df_filtered["Categoria"].isin(cat_sel)]
        filtros_aplicados += 1

# --- Filtro de solicitante ---
if "Solicitante" in df.columns:
    sol_opts_all = sorted(df["Solicitante"].dropna().unique())
    sol_sel = st.sidebar.multiselect("Solicitante", sol_opts_all, default=[])
    if sol_sel:
        df_filtered = df_filtered[df_filtered["Solicitante"].isin(sol_sel)]
        filtros_aplicados += 1

# --- Filtro de centro de custo ---
if "Centro Custo" in df.columns:
    cc_opts_all = sorted(df["Centro Custo"].dropna().unique())
    cc_sel = st.sidebar.multiselect("Centro de Custo", cc_opts_all, default=[])
    if cc_sel:
        df_filtered = df_filtered[df_filtered["Centro Custo"].isin(cc_sel)]
        filtros_aplicados += 1

# --- Filtro de fornecedor ---
if "Fornecedor" in df.columns:
    forn_opts_all = sorted(df["Fornecedor"].dropna().unique())
    forn_sel = st.sidebar.multiselect("Fornecedor", forn_opts_all, default=[])
    if forn_sel:
        df_filtered = df_filtered[df_filtered["Fornecedor"].isin(forn_sel)]
        filtros_aplicados += 1

# --- Filtro de destino ---
if "Destino" in df.columns:
    dest_opts_all = sorted(df["Destino"].dropna().unique())
    dest_sel = st.sidebar.multiselect("Destino", dest_opts_all, default=[])
    if dest_sel:
        df_filtered = df_filtered[df_filtered["Destino"].isin(dest_sel)]
        filtros_aplicados += 1

st.sidebar.markdown("---")

col1, col2 = st.sidebar.columns(2)
with col1:
    if filtros_aplicados > 0:
        st.caption(f"{filtros_aplicados} filtro(s) ativo(s)")
with col2:
    if filtros_aplicados > 0:
        if st.button("Limpar Filtros"):
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='color:#6c757d; font-size:0.7rem; text-align:center;'>"
    "Dashboard v1.0 • Dados atualizados via Google Sheets</p>",
    unsafe_allow_html=True
)

# ================================================================
# MAIN CONTENT
# ================================================================

total_gasto = df_filtered["Valor Total"].sum() if "Valor Total" in df_filtered.columns else 0
total_pedidos = len(df_filtered)
ticket_medio = total_gasto / total_pedidos if total_pedidos > 0 else 0

valor_col = "Valor Total"
qtd_col = None
for c in ["Qtd Diárias", "Qtd Passageiros", "Quantidade", "Qtd"]:
    if c in df_filtered.columns:
        qtd_col = c
        break

st.markdown(f"""
<div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
    <div>
        <h1 style="margin:0;">📊 Dashboard de Pedidos</h1>
        <p style="color:#6c757d; margin:0;">{total_pedidos} pedidos • R$ {total_gasto:,.2f} em gastos</p>
    </div>
    <div style="font-size:0.85rem; color:#6c757d;">
        {datetime.now().strftime("%d/%m/%Y %H:%M")}
    </div>
</div>
""", unsafe_allow_html=True)

# --- KPI ROW ---
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="label">💰 Total Gasto</div>
        <div class="value">R$ {total_gasto:,.2f}</div>
        <div class="sub">em {total_pedidos} pedidos</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    delta_ped = df_filtered[df_filtered["Status"] == "Pendente"].shape[0] if "Status" in df_filtered.columns else 0
    pct_pend = delta_ped / total_pedidos * 100 if total_pedidos > 0 else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="label">📋 Total de Pedidos</div>
        <div class="value">{total_pedidos}</div>
        <div class="sub">{delta_ped} pendentes ({pct_pend:.1f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="label">🎫 Ticket Médio</div>
        <div class="value">R$ {ticket_medio:,.2f}</div>
        <div class="sub">por pedido</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    cat_count = df_filtered["Categoria"].nunique() if "Categoria" in df_filtered.columns else 0
    forne_count = df_filtered["Fornecedor"].nunique() if "Fornecedor" in df_filtered.columns else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="label">📊 Abrangência</div>
        <div class="value">{cat_count} categorias</div>
        <div class="sub">{forne_count} fornecedores</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Visão Geral", "🏷️ Por Categoria", "👥 Por Solicitante",
    "📅 Tendência Temporal", "📋 Tabela Exportável"
])

# ------ TAB 1: VISÃO GERAL ------
with tab1:
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Gastos por Categoria")
        if "Categoria" in df_filtered.columns and valor_col in df_filtered.columns:
            cat_sum = df_filtered.groupby("Categoria")[valor_col].sum().sort_values(ascending=True)
            fig = go.Figure(go.Bar(
                x=cat_sum.values,
                y=cat_sum.index,
                orientation="h",
                marker=dict(color=cat_sum.values, colorscale="Blues", line=dict(width=0)),
                text=cat_sum.apply(lambda x: f"R$ {x:,.0f}"),
                textposition="outside",
            ))
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10),
                              plot_bgcolor="white", xaxis=dict(visible=False, showgrid=False),
                              yaxis=dict(title=None), hovermode="y")
            fig.update_traces(textfont=dict(size=11))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Distribuição por Status")
        if "Status" in df_filtered.columns:
            status_count = df_filtered["Status"].value_counts()
            colors_status = {"Aprovado": "#2e86c1", "Concluído": "#28b463",
                             "Pendente": "#f39c12", "Cancelado": "#e74c3c"}
            fig = go.Figure(data=[go.Pie(
                labels=status_count.index,
                values=status_count.values,
                hole=0.55,
                marker=dict(colors=[colors_status.get(s, "#95a5a6") for s in status_count.index]),
                textinfo="label+percent",
                textposition="outside",
                showlegend=False,
            )])
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Top 10 Fornecedores")
        if "Fornecedor" in df_filtered.columns and valor_col in df_filtered.columns:
            forn_sum = df_filtered.groupby("Fornecedor")[valor_col].sum().sort_values(ascending=False).head(10)
            fig = px.bar(forn_sum, x=forn_sum.values, y=forn_sum.index, orientation="h",
                         color=forn_sum.values, color_continuous_scale="Blues")
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10),
                              plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Destinos Mais Frequentes")
        if "Destino" in df_filtered.columns:
            dest_count = df_filtered["Destino"].value_counts().head(10)
            fig = px.bar(dest_count, x=dest_count.values, y=dest_count.index, orientation="h",
                         color=dest_count.values, color_continuous_scale="Teal")
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10),
                              plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ------ TAB 2: POR CATEGORIA ------
with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if "Categoria" in df_filtered.columns:
        cat_cols = ["Categoria", "Ícone"]
        cat_pivot = df_filtered.groupby("Categoria").agg(
            Total_Gasto=(valor_col, "sum"),
            Qtd_Pedidos=("Nº Pedido", "count"),
            Ticket_Medio=(valor_col, "mean"),
        ).reset_index()
        cat_pivot.columns = ["Categoria", "Total Gasto", "Qtd Pedidos", "Ticket Médio"]
        cat_pivot["Total Gasto"] = cat_pivot["Total Gasto"].apply(lambda x: f"R$ {x:,.2f}")
        cat_pivot["Ticket Médio"] = cat_pivot["Ticket Médio"].apply(lambda x: f"R$ {x:,.2f}")
        cat_pivot["%"] = (df_filtered.groupby("Categoria")[valor_col].sum()
                          / total_gasto * 100).round(1).apply(lambda x: f"{x}%").values

        c1, c2 = st.columns([1, 1.5])
        with c1:
            cat_sum = df_filtered.groupby("Categoria")[valor_col].sum()
            fig = go.Figure(data=[go.Pie(
                labels=cat_sum.index,
                values=cat_sum.values,
                hole=0.5,
                marker=dict(colors=px.colors.sequential.Blues[::-1][:len(cat_sum)]),
                textinfo="label+percent",
                textposition="outside",
                showlegend=False,
            )])
            fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.dataframe(cat_pivot, use_container_width=True, hide_index=True,
                         column_config={c: st.column_config.TextColumn(c) for c in cat_pivot.columns})

    st.markdown("</div>", unsafe_allow_html=True)

    if "Categoria" in df_filtered.columns and "Centro Custo" in df_filtered.columns:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Gastos por Categoria × Centro de Custo")
        heat = df_filtered.pivot_table(
            values=valor_col, index="Categoria", columns="Centro Custo",
            aggfunc="sum", fill_value=0
        )
        fig = px.imshow(heat, text_auto=".0f", aspect="auto",
                        color_continuous_scale="Blues",
                        labels={"x": "Centro de Custo", "y": "Categoria", "color": "R$"})
        fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ------ TAB 3: POR SOLICITANTE ------
with tab3:
    if "Solicitante" in df_filtered.columns:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Ranking de Gastos por Solicitante")
            sol_sum = df_filtered.groupby("Solicitante")[valor_col].sum().sort_values(ascending=True)
            fig = go.Figure(go.Bar(
                x=sol_sum.values,
                y=sol_sum.index,
                orientation="h",
                marker=dict(color=sol_sum.values, colorscale="Blues", line=dict(width=0)),
                text=sol_sum.apply(lambda x: f"R$ {x:,.0f}"),
                textposition="outside",
            ))
            fig.update_layout(height=450, margin=dict(l=10, r=10, t=10, b=10),
                              plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
            fig.update_traces(textfont=dict(size=10))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Qtd de Pedidos por Solicitante")
            sol_count = df_filtered["Solicitante"].value_counts().sort_values(ascending=True)
            fig = go.Figure(go.Bar(
                x=sol_count.values,
                y=sol_count.index,
                orientation="h",
                marker=dict(color=sol_count.values, colorscale="Teal", line=dict(width=0)),
                text=sol_count.values,
                textposition="outside",
            ))
            fig.update_layout(height=450, margin=dict(l=10, r=10, t=10, b=10),
                              plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(title=None))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if "Categoria" in df_filtered.columns:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Distribuição de Gastos por Solicitante e Categoria")
            stacked = df_filtered.groupby(["Solicitante", "Categoria"])[valor_col].sum().reset_index()
            fig = px.bar(stacked, x="Solicitante", y=valor_col, color="Categoria",
                         color_discrete_sequence=px.colors.qualitative.Set2,
                         text_auto=".0f")
            fig.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10),
                              plot_bgcolor="white", xaxis=dict(title=None), yaxis=dict(title="R$"))
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ------ TAB 4: TENDÊNCIA TEMPORAL ------
with tab4:
    c1, c2 = st.columns([1, 1])
    time_col = data_cols_present[0] if data_cols_present else None

    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Gastos ao Longo do Tempo")
        if time_col:
            trend = df_filtered.set_index(time_col).resample("ME")[valor_col].sum().reset_index()
            fig = px.line(trend, x=time_col, y=valor_col, markers=True)
            fig.update_traces(line=dict(color="#1a5276", width=3), marker=dict(size=6))
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10),
                              plot_bgcolor="white", xaxis=dict(title=None), yaxis=dict(title="R$"))
            fig.update_yaxes(tickprefix="R$ ")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Volume de Pedidos por Mês")
        if time_col:
            count_trend = df_filtered.set_index(time_col).resample("ME")["Nº Pedido"].count().reset_index()
            fig = px.bar(count_trend, x=time_col, y="Nº Pedido",
                         color_discrete_sequence=["#2e86c1"])
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10),
                              plot_bgcolor="white", xaxis=dict(title=None), yaxis=dict(title="Pedidos"))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Gastos por Dia da Semana")
        if time_col and "Dia Semana" in df_filtered.columns:
            dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            dow_labels = {"Monday":"Seg","Tuesday":"Ter","Wednesday":"Qua",
                          "Thursday":"Qui","Friday":"Sex","Saturday":"Sáb","Sunday":"Dom"}
            dow = df_filtered.copy()
            dow["Dia"] = dow[time_col].dt.day_name()
            dow_sum = dow.groupby("Dia")[valor_col].sum().reindex(dow_order).fillna(0)
            dow_sum.index = [dow_labels.get(d, d) for d in dow_sum.index]
            fig = px.bar(dow_sum, x=dow_sum.index, y=valor_col, color_discrete_sequence=["#1a5276"])
            fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10),
                              plot_bgcolor="white", xaxis=dict(title=None), yaxis=dict(title="R$"))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Gastos por Trimestre")
        if "Trimestre" in df_filtered.columns:
            tri = df_filtered.groupby("Trimestre")[valor_col].sum().reset_index()
            fig = px.bar(tri, x="Trimestre", y=valor_col, color="Trimestre",
                         color_discrete_sequence=px.colors.sequential.Blues_r)
            fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10),
                              plot_bgcolor="white", xaxis=dict(title=None), yaxis=dict(title="R$"),
                              showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ------ TAB 5: TABELA EXPORTÁVEL ------
with tab5:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("📋 Dados Filtrados")
    st.caption(f"{len(df_filtered)} registros • {len(df_filtered.columns)} colunas")

    export_cols = [c for c in df_filtered.columns if c != "Ícone"]

    col_left, col_right = st.columns([3, 1])
    with col_left:
        search = st.text_input("🔎 Buscar na tabela", placeholder="Digite para filtrar...")
    with col_right:
        col_sel = st.multiselect(
            "Colunas para exportar",
            options=export_cols,
            default=export_cols,
            label_visibility="collapsed",
        )

    df_display = df_filtered[col_sel].copy() if col_sel else df_filtered[export_cols].copy()

    if search:
        mask = df_display.astype(str).apply(
            lambda row: row.str.contains(search, case=False, na=False)).any(axis=1)
        df_display = df_display[mask]

    for c in df_display.select_dtypes(include=["datetime64"]).columns:
        df_display[c] = df_display[c].dt.strftime("%d/%m/%Y")

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        height=450,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    d1, d2, d3 = st.columns([1, 1, 1])
    with d1:
        csv = df_display.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "📥 Download CSV",
            csv,
            f"pedidos_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "text/csv",
            use_container_width=True,
        )
    with d2:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_display.to_excel(writer, index=False, sheet_name="Pedidos")
        xlsx = output.getvalue()
        st.download_button(
            "📥 Download Excel",
            xlsx,
            f"pedidos_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with d3:
        st.download_button(
            "📥 Download JSON",
            df_display.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8-sig"),
            f"pedidos_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "application/json",
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)
