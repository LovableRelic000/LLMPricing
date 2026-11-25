import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="LLM Pricing Analytics | K-Means",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root {
    --bg-canvas: #F4F2EC;
    --bg-surface: #FFFFFF;
    --bg-sidebar: #111827;
    --ink-primary: #111827;
    --ink-secondary: #4B5563;
    --ink-muted: #6B7280;
    --border-subtle: #E5E1D8;
    --accent-teal: #0D9488;
    --accent-blue: #1D4ED8;
    --accent-amber: #D97706;
    --accent-crimson: #9F1239;
}
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--bg-canvas) !important;
    color: var(--ink-primary) !important;
}
header[data-testid="stHeader"] {
    background: rgba(244, 242, 236, 0.9) !important;
    border-bottom: 1px solid var(--border-subtle);
}
#MainMenu, footer, [data-testid="stToolbar"] {
    visibility: hidden;
}
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1320px !important;
}
section[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid #1F2937 !important;
}
section[data-testid="stSidebar"] > div {
    background-color: var(--bg-sidebar) !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div {
    color: #E5E7EB;
}
section[data-testid="stSidebar"] hr {
    border-color: #1F2937 !important;
}
section[data-testid="stSidebar"] .stRadio > label {
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #9CA3AF !important;
    font-weight: 700 !important;
    margin-bottom: 6px;
}
section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 8px;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: #1F2937 !important;
    border: 1px solid #374151 !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    margin: 0 !important;
    width: 100%;
    transition: all 0.15s ease;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    border-color: #14B8A6 !important;
    background: #1B2A38 !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(135deg, #0D9488 0%, #0F766E 100%) !important;
    border-color: #14B8A6 !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #1F2937 !important;
    border-color: #374151 !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] [data-baseweb="tag"] {
    background-color: #0F766E !important;
    color: #FFFFFF !important;
    border-radius: 6px !important;
}
.brand-box {
    background: linear-gradient(145deg, #1F2937 0%, #111827 100%);
    border: 1px solid #374151;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 14px;
}
.brand-kicker {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #2DD4BF !important;
    font-weight: 700;
    margin-bottom: 4px;
}
.brand-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #FFFFFF !important;
    line-height: 1.25;
    margin: 0;
}
.brand-meta {
    font-size: 0.78rem;
    color: #9CA3AF !important;
    margin-top: 6px;
    line-height: 1.45;
}
.sidebar-section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #2DD4BF !important;
    font-weight: 700;
    margin: 10px 0 4px 0;
}
.hero-banner {
    background: linear-gradient(120deg, #111827 0%, #1E293B 65%, #134E4A 100%);
    border-radius: 16px;
    padding: 26px 30px;
    margin-bottom: 10px;
    color: #FFFFFF;
    box-shadow: 0 10px 25px -12px rgba(17, 24, 39, 0.45);
}
.hero-kicker {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #5EEAD4;
    font-weight: 700;
    margin-bottom: 8px;
}
.hero-title {
    font-size: 1.9rem;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0 0 8px 0;
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.hero-subtitle {
    font-size: 0.95rem;
    color: #D1D5DB;
    margin: 0;
    max-width: 860px;
    line-height: 1.5;
}
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 10px;
}
@media (max-width: 900px) {
    .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
.kpi-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-top: 3px solid var(--accent-teal);
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 2px 6px rgba(17, 24, 39, 0.04);
}
.kpi-card.blue { border-top-color: var(--accent-blue); }
.kpi-card.amber { border-top-color: var(--accent-amber); }
.kpi-card.crimson { border-top-color: var(--accent-crimson); }
.kpi-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--ink-muted);
    font-weight: 700;
    margin-bottom: 8px;
}
.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--ink-primary);
    line-height: 1.15;
}
.kpi-note {
    font-size: 0.8rem;
    color: var(--ink-secondary);
    margin-top: 6px;
}
.panel-header {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-bottom: none;
    border-radius: 14px 14px 0 0;
    padding: 16px 20px 6px 20px;
    margin-bottom: -16px;
}
.panel-title {
    font-size: 1.02rem;
    font-weight: 700;
    color: var(--ink-primary);
    margin: 0;
}
.panel-caption {
    font-size: 0.82rem;
    color: var(--ink-muted);
    margin: 2px 0 0 0;
}
div[data-testid="stPlotlyChart"] {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-top: none;
    border-radius: 0 0 14px 14px;
    padding: 6px 12px 12px 12px;
    box-shadow: 0 2px 8px rgba(17, 24, 39, 0.035);
}
.section-heading {
    font-size: 1.15rem;
    font-weight: 800;
    color: var(--ink-primary);
    letter-spacing: -0.01em;
    margin: 14px 0 6px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--border-subtle);
}
.cluster-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-left: 5px solid var(--accent-teal);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 14px;
    box-shadow: 0 2px 6px rgba(17, 24, 39, 0.035);
}
.cluster-card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}
.cluster-card h4 {
    margin: 0;
    font-size: 1rem;
    font-weight: 700;
    color: var(--ink-primary);
}
.cluster-share {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    font-weight: 700;
    background: #F4F2EC;
    color: var(--ink-primary);
    padding: 3px 9px;
    border-radius: 999px;
    border: 1px solid var(--border-subtle);
}
.cluster-metrics {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: var(--ink-primary);
    background: #F9F8F5;
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 7px 10px;
    margin-bottom: 8px;
}
.cluster-card p {
    margin: 0;
    font-size: 0.9rem;
    color: var(--ink-secondary);
    line-height: 1.55;
}
.insight-box {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 20px 22px;
    box-shadow: 0 2px 6px rgba(17, 24, 39, 0.035);
}
.insight-box h3 {
    font-size: 1.05rem;
    font-weight: 800;
    color: var(--ink-primary);
    margin: 0 0 14px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border-subtle);
}
.insight-item {
    margin-bottom: 12px;
    padding-left: 12px;
    border-left: 3px solid var(--accent-teal);
    font-size: 0.9rem;
    color: var(--ink-secondary);
    line-height: 1.55;
}
.insight-item.rec {
    border-left-color: var(--accent-blue);
}
.insight-item strong {
    color: var(--ink-primary);
}
</style>
"""

st.html(CSS)

PALETA_CLUSTERS = {
    "Modelos Economicos / Batch": "#0D9488",
    "Gama Media Estandar": "#1D4ED8",
    "Contexto Largo / Cache Alto": "#D97706",
    "Modelos Premium / Alto Rendimiento": "#9F1239",
}

ORDEN_CLUSTERS = [
    "Modelos Economicos / Batch",
    "Gama Media Estandar",
    "Contexto Largo / Cache Alto",
    "Modelos Premium / Alto Rendimiento",
]

FEATURES = ["input_usd_per_1m", "output_usd_per_1m", "cached_input_usd_per_1m"]


@st.cache_data
def cargar_datos():
    ruta = os.path.join(os.path.dirname(__file__), "data", "dataset_procesado.csv")
    if not os.path.exists(ruta):
        st.error(
            "No se encontro data/dataset_procesado.csv. "
            "Ejecuta primero: python analisis_kmeans.py"
        )
        st.stop()
    return pd.read_csv(ruta)


def estilo_plotly(fig, height=370):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=16, r=16, t=18, b=16),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#1F2937"),
        xaxis=dict(gridcolor="#F1EFE9", zerolinecolor="#E5E1D8", linecolor="#E5E1D8"),
        yaxis=dict(gridcolor="#F1EFE9", zerolinecolor="#E5E1D8", linecolor="#E5E1D8"),
    )
    return fig


def panel_title(title, caption=""):
    st.html(
        f"""
        <div class="panel-header">
            <p class="panel-title">{title}</p>
            <p class="panel-caption">{caption}</p>
        </div>
        """
    )


df = cargar_datos()

with st.sidebar:
    st.html(
        """
        <div class="brand-box">
            <div class="brand-kicker">K-Means Analytics</div>
            <div class="brand-title">LLM API Pricing Monitor</div>
            <div class="brand-meta">Segmentacion de tarifas por millon de tokens (USD)</div>
        </div>
        """
    )

pagina = st.sidebar.radio(
    "Navegacion",
    options=["Analisis General", "Segmentacion mediante K-Means"],
)

with st.sidebar:
    st.divider()
    st.html(
        """
        <div class="brand-meta" style="padding: 0 4px;">
            <strong style="color:#F9FAFB;">Dataset:</strong> price_snapshots.csv<br/>
            <strong style="color:#F9FAFB;">Muestra limpia:</strong> 2,151 registros<br/>
            <strong style="color:#F9FAFB;">Modelo:</strong> K-Means (K = 4)<br/>
            <strong style="color:#F9FAFB;">Silhouette Score:</strong> 0.5310
        </div>
        """
    )

if pagina == "Analisis General":
    st.html(
        """
        <div class="hero-banner">
            <div class="hero-kicker">Panorama del Mercado · Tarifas 2026</div>
            <h1 class="hero-title">Analisis General de Precios de APIs de LLMs</h1>
            <p class="hero-subtitle">
                Exploracion de costos por millon de tokens en entrada, salida y cache tras la eliminacion
                de valores nulos y atipicos mediante el metodo IQR (1.5x).
            </p>
        </div>
        """
    )

    st.html(
        f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Registros analizados</div>
                <div class="kpi-value">{len(df):,}</div>
                <div class="kpi-note">Dataset limpio tras filtro IQR</div>
            </div>
            <div class="kpi-card blue">
                <div class="kpi-label">Precio promedio Input</div>
                <div class="kpi-value">${df['input_usd_per_1m'].mean():.2f}</div>
                <div class="kpi-note">USD por 1M de tokens de entrada</div>
            </div>
            <div class="kpi-card amber">
                <div class="kpi-label">Precio promedio Output</div>
                <div class="kpi-value">${df['output_usd_per_1m'].mean():.2f}</div>
                <div class="kpi-note">USD por 1M de tokens generados</div>
            </div>
            <div class="kpi-card crimson">
                <div class="kpi-label">Proveedores activos</div>
                <div class="kpi-value">{df['provider'].nunique()}</div>
                <div class="kpi-note">Ecosistema de APIs evaluado</div>
            </div>
        </div>
        """
    )

    c1, c2 = st.columns(2)

    with c1:
        panel_title("Registros por proveedor", "Volumen de tarifas disponibles tras la limpieza")
        prov_counts = df["provider"].value_counts().reset_index()
        prov_counts.columns = ["Proveedor", "Registros"]
        fig_prov = px.bar(
            prov_counts,
            x="Registros",
            y="Proveedor",
            orientation="h",
            text="Registros",
            color_discrete_sequence=["#0D9488"],
        )
        fig_prov.update_traces(textposition="outside", cliponaxis=False, marker_line_width=0)
        fig_prov.update_layout(
            yaxis={"categoryorder": "total ascending"},
            xaxis={"range": [0, prov_counts["Registros"].max() * 1.16]},
        )
        st.plotly_chart(estilo_plotly(fig_prov, 360), width="stretch")

    with c2:
        panel_title("Precio promedio por proveedor", "Comparacion directa entre Input y Output (USD / 1M)")
        prov_avg = (
            df.groupby("provider")[["input_usd_per_1m", "output_usd_per_1m"]]
            .mean()
            .reset_index()
            .melt(id_vars="provider", var_name="Tipo", value_name="USD_1M")
        )
        prov_avg["Tipo"] = prov_avg["Tipo"].replace(
            {"input_usd_per_1m": "Input USD/1M", "output_usd_per_1m": "Output USD/1M"}
        )
        fig_avg = px.bar(
            prov_avg,
            x="provider",
            y="USD_1M",
            color="Tipo",
            barmode="group",
            color_discrete_map={"Input USD/1M": "#1D4ED8", "Output USD/1M": "#D97706"},
            labels={"provider": "Proveedor", "USD_1M": "USD / 1M tokens"},
        )
        fig_avg.update_layout(legend=dict(orientation="h", y=1.12, x=0, title=""))
        st.plotly_chart(estilo_plotly(fig_avg, 360), width="stretch")

    c3, c4 = st.columns(2)

    with c3:
        panel_title("Distribucion por nivel de servicio (price_tier)", "Frecuencia de modalidades standard, batch, flex y contexto largo")
        tier_counts = df["price_tier"].value_counts().reset_index()
        tier_counts.columns = ["Nivel de precio", "Registros"]
        fig_tier = px.bar(
            tier_counts,
            x="Registros",
            y="Nivel de precio",
            orientation="h",
            text="Registros",
            color_discrete_sequence=["#111827"],
        )
        fig_tier.update_traces(textposition="outside", cliponaxis=False, marker_line_width=0)
        fig_tier.update_layout(
            yaxis={"categoryorder": "total ascending"},
            xaxis={"range": [0, tier_counts["Registros"].max() * 1.16]},
        )
        st.plotly_chart(estilo_plotly(fig_tier, 390), width="stretch")

    with c4:
        panel_title("Distribucion del precio de salida", "Histograma y diagrama de caja de output_usd_per_1m")
        fig_hist = px.histogram(
            df,
            x="output_usd_per_1m",
            nbins=28,
            marginal="box",
            color_discrete_sequence=["#9F1239"],
            labels={"output_usd_per_1m": "Output USD / 1M tokens", "count": "Frecuencia"},
        )
        st.plotly_chart(estilo_plotly(fig_hist, 390), width="stretch")

    st.html('<div class="section-heading">Estadisticas descriptivas generales</div>')
    tabla_gen = (
        df[FEATURES]
        .describe()
        .T.rename(
            columns={
                "count": "Conteo",
                "mean": "Media (USD)",
                "std": "Desv. Estandar",
                "min": "Minimo",
                "25%": "Q1 (25%)",
                "50%": "Mediana (50%)",
                "75%": "Q3 (75%)",
                "max": "Maximo",
            }
        )
        .round(4)
    )
    st.dataframe(tabla_gen, width="stretch")

    with st.expander("Explorar muestra de registros procesados (primeras 20 filas)"):
        st.dataframe(
            df[
                [
                    "snapshot_date",
                    "provider",
                    "model_id",
                    "price_tier",
                    "input_usd_per_1m",
                    "output_usd_per_1m",
                    "cached_input_usd_per_1m",
                    "Nombre_Cluster",
                ]
            ].head(20),
            width="stretch",
        )

else:
    with st.sidebar:
        st.html('<div class="sidebar-section-label">Filtros interactivos</div>')

    proveedores = sorted(df["provider"].dropna().unique())
    filtro_provider = st.sidebar.multiselect("Proveedor (provider)", proveedores, default=proveedores)

    tiers = sorted(df["price_tier"].dropna().unique())
    filtro_tier = st.sidebar.multiselect("Nivel de precio (price_tier)", tiers, default=tiers)

    clusters = [c for c in ORDEN_CLUSTERS if c in df["Nombre_Cluster"].unique()]
    filtro_cluster = st.sidebar.multiselect("Segmento (Nombre_Cluster)", clusters, default=clusters)

    df_f = df[
        df["provider"].isin(filtro_provider)
        & df["price_tier"].isin(filtro_tier)
        & df["Nombre_Cluster"].isin(filtro_cluster)
    ].copy()

    st.html(
        """
        <div class="hero-banner">
            <div class="hero-kicker">Aprendizaje No Supervisado · K = 4 · StandardScaler · Silhouette 0.5310</div>
            <h1 class="hero-title">Segmentacion de Precios mediante K-Means</h1>
            <p class="hero-subtitle">
                Cuatro perfiles reales de costo descubiertos automaticamente a partir de tarifas de entrada,
                salida y lectura en cache. Ajusta los filtros laterales para inspeccionar segmentos especificos.
            </p>
        </div>
        """
    )

    if df_f.empty:
        st.warning("No hay registros que coincidan con la combinacion de filtros seleccionada.")
        st.stop()

    st.html(
        f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Registros filtrados</div>
                <div class="kpi-value">{len(df_f):,}</div>
                <div class="kpi-note">{len(df_f) / len(df) * 100:.1f}% del dataset limpio</div>
            </div>
            <div class="kpi-card blue">
                <div class="kpi-label">Input promedio</div>
                <div class="kpi-value">${df_f['input_usd_per_1m'].mean():.2f}</div>
                <div class="kpi-note">USD / 1M tokens de entrada</div>
            </div>
            <div class="kpi-card amber">
                <div class="kpi-label">Output promedio</div>
                <div class="kpi-value">${df_f['output_usd_per_1m'].mean():.2f}</div>
                <div class="kpi-note">USD / 1M tokens de salida</div>
            </div>
            <div class="kpi-card crimson">
                <div class="kpi-label">Cache promedio</div>
                <div class="kpi-value">${df_f['cached_input_usd_per_1m'].mean():.3f}</div>
                <div class="kpi-note">USD / 1M tokens en cache</div>
            </div>
        </div>
        """
    )

    visibles = [c for c in ORDEN_CLUSTERS if c in df_f["Nombre_Cluster"].unique()]

    g1, g2 = st.columns([1, 1.35])

    with g1:
        panel_title("Distribucion de registros por cluster", "Participacion relativa de cada segmento")
        dist = df_f["Nombre_Cluster"].value_counts().reindex(visibles).reset_index()
        dist.columns = ["Nombre_Cluster", "Registros"]
        dist["Etiqueta"] = dist["Registros"].apply(lambda x: f"{x} ({x / len(df_f) * 100:.1f}%)")

        fig_dist = px.bar(
            dist,
            x="Nombre_Cluster",
            y="Registros",
            color="Nombre_Cluster",
            color_discrete_map=PALETA_CLUSTERS,
            text="Etiqueta",
            labels={"Nombre_Cluster": ""},
        )
        fig_dist.update_traces(textposition="outside", marker_line_width=0)
        fig_dist.update_layout(showlegend=False, xaxis_tickangle=-16)
        st.plotly_chart(estilo_plotly(fig_dist, 410), width="stretch")

    with g2:
        panel_title("Dispersion: Input vs Output USD / 1M", "Agrupamiento K-Means con centroides marcados en X roja")
        fig_scatter = px.scatter(
            df_f,
            x="input_usd_per_1m",
            y="output_usd_per_1m",
            color="Nombre_Cluster",
            category_orders={"Nombre_Cluster": ORDEN_CLUSTERS},
            color_discrete_map=PALETA_CLUSTERS,
            hover_data=["provider", "model_id", "price_tier", "cached_input_usd_per_1m"],
            opacity=0.82,
            labels={
                "input_usd_per_1m": "Input USD / 1M tokens",
                "output_usd_per_1m": "Output USD / 1M tokens",
                "Nombre_Cluster": "",
            },
        )
        fig_scatter.update_traces(marker=dict(size=8, line=dict(width=0.5, color="#FFFFFF")))
        centros = df_f.groupby("Nombre_Cluster")[["input_usd_per_1m", "output_usd_per_1m"]].mean().reset_index()
        fig_scatter.add_trace(
            go.Scatter(
                x=centros["input_usd_per_1m"],
                y=centros["output_usd_per_1m"],
                mode="markers",
                marker=dict(symbol="x", size=16, color="#DC2626", line=dict(width=2, color="#FFFFFF")),
                name="Centroides",
                hovertemplate="<b>Centroide</b><br>Input: $%{x:.2f}<br>Output: $%{y:.2f}<extra></extra>",
            )
        )
        fig_scatter.update_layout(legend=dict(orientation="h", y=-0.24, x=0, title=""))
        st.plotly_chart(estilo_plotly(fig_scatter, 410), width="stretch")

    g3, g4 = st.columns(2)

    with g3:
        panel_title("Precios promedio por cluster", "Comparacion multivariada de Input, Output y Cache")
        prom = (
            df_f.groupby("Nombre_Cluster")[FEATURES]
            .mean()
            .reindex(visibles)
            .reset_index()
            .melt(id_vars="Nombre_Cluster", var_name="Variable", value_name="Promedio_USD")
        )
        prom["Variable"] = prom["Variable"].replace(
            {
                "input_usd_per_1m": "Input USD/1M",
                "output_usd_per_1m": "Output USD/1M",
                "cached_input_usd_per_1m": "Cached Input USD/1M",
            }
        )
        fig_bar = px.bar(
            prom,
            x="Nombre_Cluster",
            y="Promedio_USD",
            color="Variable",
            barmode="group",
            text_auto=".2f",
            color_discrete_sequence=["#1D4ED8", "#9F1239", "#0D9488"],
            labels={"Nombre_Cluster": "", "Promedio_USD": "USD promedio / 1M"},
        )
        fig_bar.update_layout(xaxis_tickangle=-16, legend=dict(orientation="h", y=1.12, x=0, title=""))
        st.plotly_chart(estilo_plotly(fig_bar, 400), width="stretch")

    with g4:
        panel_title("Dispersion interna del precio de salida", "Diagrama de caja (Boxplot) de output_usd_per_1m por segmento")
        fig_box = px.box(
            df_f,
            x="Nombre_Cluster",
            y="output_usd_per_1m",
            color="Nombre_Cluster",
            category_orders={"Nombre_Cluster": ORDEN_CLUSTERS},
            color_discrete_map=PALETA_CLUSTERS,
            labels={"Nombre_Cluster": "", "output_usd_per_1m": "Output USD / 1M tokens"},
        )
        fig_box.update_layout(showlegend=False, xaxis_tickangle=-16)
        st.plotly_chart(estilo_plotly(fig_box, 400), width="stretch")

    st.html('<div class="section-heading">Estadisticas descriptivas por cluster</div>')
    resumen = (
        df_f.groupby("Nombre_Cluster")
        .agg(
            Registros=("input_usd_per_1m", "count"),
            Input_Promedio=("input_usd_per_1m", "mean"),
            Input_Mediana=("input_usd_per_1m", "median"),
            Output_Promedio=("output_usd_per_1m", "mean"),
            Output_Mediana=("output_usd_per_1m", "median"),
            Cached_Promedio=("cached_input_usd_per_1m", "mean"),
            Cached_Max=("cached_input_usd_per_1m", "max"),
        )
        .reindex(visibles)
        .round(3)
    )
    st.dataframe(resumen, width="stretch")

    st.html('<div class="section-heading">Descripcion de los grupos identificados</div>')
    d1, d2 = st.columns(2)

    with d1:
        st.html(
            """
            <div class="cluster-card" style="border-left-color: #0D9488;">
                <div class="cluster-card-top">
                    <h4>1. Modelos Economicos / Batch</h4>
                    <span class="cluster-share">48.9% · 1,051 reg.</span>
                </div>
                <div class="cluster-metrics">Input $0.55 &nbsp;|&nbsp; Output $2.64 &nbsp;|&nbsp; Cache $0.07</div>
                <p>Agrupa modelos ligeros (mini, nano, flash, luna) y tarifas batch/flex disenadas para alto volumen, clasificacion masiva y automatizacion de bajo costo.</p>
            </div>
            <div class="cluster-card" style="border-left-color: #D97706;">
                <div class="cluster-card-top">
                    <h4>3. Contexto Largo / Cache Alto</h4>
                    <span class="cluster-share">4.2% · 91 reg.</span>
                </div>
                <div class="cluster-metrics">Input $4.21 &nbsp;|&nbsp; Output $10.95 &nbsp;|&nbsp; Cache $0.78</div>
                <p>Segmento especializado (tarifas priority_long_context y fast de xAI y OpenAI) donde la lectura en cache alcanza 18-25% del precio de entrada con salida moderada.</p>
            </div>
            """
        )

    with d2:
        st.html(
            """
            <div class="cluster-card" style="border-left-color: #1D4ED8;">
                <div class="cluster-card-top">
                    <h4>2. Gama Media Estandar</h4>
                    <span class="cluster-share">31.8% · 683 reg.</span>
                </div>
                <div class="cluster-metrics">Input $2.13 &nbsp;|&nbsp; Output $9.59 &nbsp;|&nbsp; Cache $0.27</div>
                <p>Reune modelos insignia de uso general (gemini-2.5-pro, gpt-5.4, gpt-5.6-terra) con un equilibrio solido entre capacidad de razonamiento y costo operativo.</p>
            </div>
            <div class="cluster-card" style="border-left-color: #9F1239;">
                <div class="cluster-card-top">
                    <h4>4. Modelos Premium / Alto Rendimiento</h4>
                    <span class="cluster-share">15.2% · 326 reg.</span>
                </div>
                <div class="cluster-metrics">Input $4.93 &nbsp;|&nbsp; Output $24.05 &nbsp;|&nbsp; Cache $0.45</div>
                <p>Concentra modelos de razonamiento avanzado y contexto largo con precios de salida hasta 9 veces superiores al segmento economico.</p>
            </div>
            """
        )

    st.html('<div class="section-heading">Hallazgos y recomendaciones estrategicas</div>')
    h_col, r_col = st.columns(2)

    with h_col:
        st.html(
            """
            <div class="insight-box">
                <h3>Hallazgos relevantes</h3>
                <div class="insight-item">
                    <strong>El precio de salida domina el presupuesto:</strong> Generar tokens cuesta entre 4x y 5x mas que procesarlos como entrada; en el segmento Premium llega a $24.05/1M frente a $2.64/1M en el Economico.
                </div>
                <div class="insight-item">
                    <strong>StandardScaler revelo un nicho oculto:</strong> Al estandarizar las 3 variables el Silhouette Score subio de 0.3627 a 0.5310 y permitio aislar el segmento Contexto Largo / Cache Alto ($0.78/1M en cache).
                </div>
                <div class="insight-item">
                    <strong>Casi la mitad del mercado es economico (48.9%):</strong> Existen amplias opciones por debajo de $1/1M en entrada en modalidades standard, batch y flex.
                </div>
            </div>
            """
        )

    with r_col:
        st.html(
            """
            <div class="insight-box">
                <h3>Recomendaciones practicas</h3>
                <div class="insight-item rec">
                    <strong>Aplicar enrutamiento de modelos (Model Routing):</strong> Enviar tareas rutinarias al segmento Economico / Batch y reservar los modelos Premium solo para razonamiento complejo, reduciendo costos entre 60% y 80%.
                </div>
                <div class="insight-item rec">
                    <strong>Auditar el costo de Prompt Caching en arquitecturas RAG:</strong> Comparar el porcentaje de descuento del cache antes de adoptar modelos del grupo Contexto Largo / Cache Alto.
                </div>
                <div class="insight-item rec">
                    <strong>Migrar procesos asincronos a tarifas batch o flex:</strong> Trasladar cargas nocturnas o por lotes desde tarifas standard permite bajar de segmento sin cambiar de familia de modelo.
                </div>
            </div>
            """
        )
