import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Segmentacion de Precios de APIs de LLMs",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2.5rem;
        max-width: 1280px;
    }
    [data-testid="stSidebar"] {
        border-right: 1px solid #E2E8F0;
    }
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 600;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.75rem;
        color: #0F172A;
        font-weight: 700;
    }
    .info-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #2563EB;
        border-radius: 8px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }
    .info-card h4 {
        margin: 0 0 6px 0;
        font-size: 1rem;
        color: #0F172A;
    }
    .info-card p {
        margin: 0;
        font-size: 0.92rem;
        color: #334155;
        line-height: 1.5;
    }
    .section-subtitle {
        color: #475569;
        font-size: 0.98rem;
        margin-top: -8px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

PALETA_CLUSTERS = {
    "Modelos Economicos / Batch": "#10B981",
    "Gama Media Estandar": "#2563EB",
    "Contexto Largo / Cache Alto": "#F59E0B",
    "Modelos Premium / Alto Rendimiento": "#7C3AED",
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


def estilo_plotly(fig, height=390):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=20, r=20, t=24, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(family="sans-serif", size=12, color="#1E293B"),
        xaxis=dict(gridcolor="#F1F5F9", zerolinecolor="#E2E8F0"),
        yaxis=dict(gridcolor="#F1F5F9", zerolinecolor="#E2E8F0"),
    )
    return fig


df = cargar_datos()

st.sidebar.markdown("## Panel de Control")
pagina = st.sidebar.radio(
    "Seccion:",
    options=["Analisis General", "Segmentacion mediante K-Means"],
)

st.sidebar.divider()
st.sidebar.caption(
    "Proyecto Integrador de Mineria de Datos\n\n"
    "Dataset: price_snapshots.csv\n\n"
    "Modelo: K-Means (K = 4, StandardScaler)"
)

if pagina == "Analisis General":
    st.title("Analisis de Precios de APIs de LLMs")
    st.markdown(
        '<p class="section-subtitle">'
        "Panorama general de tarifas por millon de tokens (USD) tras la limpieza de nulos y outliers (IQR)."
        "</p>",
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registros analizados", f"{len(df):,}")
    col2.metric("Precio promedio Input", f"${df['input_usd_per_1m'].mean():.2f} / 1M")
    col3.metric("Precio promedio Output", f"${df['output_usd_per_1m'].mean():.2f} / 1M")
    col4.metric("Cantidad de proveedores", f"{df['provider'].nunique()}")

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Registros por proveedor")
        prov_counts = df["provider"].value_counts().reset_index()
        prov_counts.columns = ["Proveedor", "Registros"]
        fig_prov = px.bar(
            prov_counts,
            x="Registros",
            y="Proveedor",
            orientation="h",
            text="Registros",
            color_discrete_sequence=["#2563EB"],
        )
        fig_prov.update_traces(textposition="outside")
        fig_prov.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(estilo_plotly(fig_prov, 380), width="stretch")

    with c2:
        st.subheader("Precio promedio (Input vs Output) por proveedor")
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
            color_discrete_map={"Input USD/1M": "#2563EB", "Output USD/1M": "#F59E0B"},
            labels={"provider": "Proveedor", "USD_1M": "USD por 1M tokens"},
        )
        fig_avg.update_layout(legend=dict(orientation="h", y=1.12, x=0))
        st.plotly_chart(estilo_plotly(fig_avg, 380), width="stretch")

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Distribucion por nivel de precio (price_tier)")
        tier_counts = df["price_tier"].value_counts().reset_index()
        tier_counts.columns = ["Nivel de precio", "Registros"]
        fig_tier = px.bar(
            tier_counts,
            x="Registros",
            y="Nivel de precio",
            orientation="h",
            text="Registros",
            color_discrete_sequence=["#0EA5E9"],
        )
        fig_tier.update_traces(textposition="outside")
        fig_tier.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(estilo_plotly(fig_tier, 400), width="stretch")

    with c4:
        st.subheader("Distribucion del precio de salida (output_usd_per_1m)")
        fig_hist = px.histogram(
            df,
            x="output_usd_per_1m",
            nbins=28,
            marginal="box",
            color_discrete_sequence=["#6366F1"],
            labels={"output_usd_per_1m": "Output USD / 1M tokens", "count": "Frecuencia"},
        )
        st.plotly_chart(estilo_plotly(fig_hist, 400), width="stretch")

    st.divider()
    st.subheader("Estadisticas descriptivas generales")
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

    with st.expander("Ver muestra de datos procesados (primeros 20 registros)"):
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
    st.title("Segmentacion de Precios mediante K-Means (K = 4)")
    st.markdown(
        '<p class="section-subtitle">'
        "Agrupamiento con datos estandarizados (StandardScaler, Silhouette Score = 0.5310). "
        "Usa los filtros de la barra lateral para explorar proveedores, niveles y segmentos."
        "</p>",
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("### Filtros")

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

    if df_f.empty:
        st.warning("No hay registros que coincidan con los filtros seleccionados.")
        st.stop()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Registros filtrados", f"{len(df_f):,}")
    k2.metric("Input promedio", f"${df_f['input_usd_per_1m'].mean():.2f} / 1M")
    k3.metric("Output promedio", f"${df_f['output_usd_per_1m'].mean():.2f} / 1M")
    k4.metric("Cache promedio", f"${df_f['cached_input_usd_per_1m'].mean():.3f} / 1M")

    st.divider()

    g1, g2 = st.columns([1, 1.35])

    with g1:
        st.subheader("Distribucion de registros por cluster")
        visibles = [c for c in ORDEN_CLUSTERS if c in df_f["Nombre_Cluster"].unique()]
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
            labels={"Nombre_Cluster": "Segmento"},
        )
        fig_dist.update_traces(textposition="outside")
        fig_dist.update_layout(showlegend=False, xaxis_tickangle=-15)
        st.plotly_chart(estilo_plotly(fig_dist, 420), width="stretch")

    with g2:
        st.subheader("Dispersion: Input vs Output USD/1M")
        fig_scatter = px.scatter(
            df_f,
            x="input_usd_per_1m",
            y="output_usd_per_1m",
            color="Nombre_Cluster",
            category_orders={"Nombre_Cluster": ORDEN_CLUSTERS},
            color_discrete_map=PALETA_CLUSTERS,
            hover_data=["provider", "model_id", "price_tier", "cached_input_usd_per_1m"],
            opacity=0.78,
            labels={
                "input_usd_per_1m": "Input USD / 1M tokens",
                "output_usd_per_1m": "Output USD / 1M tokens",
                "Nombre_Cluster": "Segmento",
            },
        )
        centros = df_f.groupby("Nombre_Cluster")[["input_usd_per_1m", "output_usd_per_1m"]].mean().reset_index()
        fig_scatter.add_trace(
            go.Scatter(
                x=centros["input_usd_per_1m"],
                y=centros["output_usd_per_1m"],
                mode="markers",
                marker=dict(symbol="x", size=13, color="#DC2626", line=dict(width=1.5, color="#0F172A")),
                name="Centroides",
                hovertemplate="<b>Centroide</b><br>Input: $%{x:.2f}<br>Output: $%{y:.2f}<extra></extra>",
            )
        )
        fig_scatter.update_layout(legend=dict(orientation="h", y=-0.24, x=0))
        st.plotly_chart(estilo_plotly(fig_scatter, 420), width="stretch")

    g3, g4 = st.columns(2)

    with g3:
        st.subheader("Precios promedio por cluster")
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
            color_discrete_sequence=["#2563EB", "#7C3AED", "#10B981"],
            labels={"Nombre_Cluster": "Segmento", "Promedio_USD": "USD promedio / 1M"},
        )
        fig_bar.update_layout(xaxis_tickangle=-15, legend=dict(orientation="h", y=1.12, x=0))
        st.plotly_chart(estilo_plotly(fig_bar, 410), width="stretch")

    with g4:
        st.subheader("Distribucion de precios de salida (Boxplot)")
        fig_box = px.box(
            df_f,
            x="Nombre_Cluster",
            y="output_usd_per_1m",
            color="Nombre_Cluster",
            category_orders={"Nombre_Cluster": ORDEN_CLUSTERS},
            color_discrete_map=PALETA_CLUSTERS,
            labels={"Nombre_Cluster": "Segmento", "output_usd_per_1m": "Output USD / 1M tokens"},
        )
        fig_box.update_layout(showlegend=False, xaxis_tickangle=-15)
        st.plotly_chart(estilo_plotly(fig_box, 410), width="stretch")

    st.divider()

    st.subheader("Estadisticas descriptivas por cluster")
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

    st.divider()

    st.subheader("Descripcion de los grupos identificados")
    d1, d2 = st.columns(2)

    with d1:
        st.markdown(
            """
            <div class="info-card" style="border-left-color: #10B981;">
                <h4>1. Modelos Economicos / Batch (48.9% del mercado)</h4>
                <p>Centroide promedio: <b>$0.55</b> input | <b>$2.64</b> output | <b>$0.07</b> cache.
                Agrupa modelos ligeros (mini, nano, flash, luna) y tarifas batch/flex disenadas para alto volumen y automatizacion de bajo costo.</p>
            </div>
            <div class="info-card" style="border-left-color: #F59E0B;">
                <h4>3. Contexto Largo / Cache Alto (4.2% del mercado)</h4>
                <p>Centroide promedio: <b>$4.21</b> input | <b>$10.95</b> output | <b>$0.78</b> cache.
                Segmento especializado (tarifas priority_long_context y fast de xAI y OpenAI) con un costo de lectura en cache elevado (~18-25% del input).</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with d2:
        st.markdown(
            """
            <div class="info-card" style="border-left-color: #2563EB;">
                <h4>2. Gama Media Estandar (31.8% del mercado)</h4>
                <p>Centroide promedio: <b>$2.13</b> input | <b>$9.59</b> output | <b>$0.27</b> cache.
                Reune modelos insignia de uso general (gemini-2.5-pro, gpt-5.4, gpt-5.6-terra) con un equilibrio solido entre capacidad y costo.</p>
            </div>
            <div class="info-card" style="border-left-color: #7C3AED;">
                <h4>4. Modelos Premium / Alto Rendimiento (15.2% del mercado)</h4>
                <p>Centroide promedio: <b>$4.93</b> input | <b>$24.05</b> output | <b>$0.45</b> cache.
                Concentra modelos de razonamiento avanzado y contexto largo con precios de salida hasta 9 veces mayores que el segmento economico.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    h_col, r_col = st.columns(2)

    with h_col:
        st.subheader("Hallazgos relevantes")
        st.markdown(
            """
            1. **El precio de salida domina el presupuesto:** Generar tokens cuesta entre 4x y 5x mas que procesarlos como entrada; en el segmento Premium llega a \\$24.05/1M frente a \\$2.64/1M en el Economico.
            2. **StandardScaler revelo un nicho oculto:** Al estandarizar las 3 variables el Silhouette Score subio de 0.3627 a 0.5310 y permitio aislar el segmento *Contexto Largo / Cache Alto* (\\$0.78/1M en cache).
            3. **Casi la mitad del mercado es economico (48.9%):** Existen amplias opciones por debajo de \\$1/1M en entrada en modalidades standard, batch y flex.
            """
        )

    with r_col:
        st.subheader("Recomendaciones practicas")
        st.markdown(
            """
            1. **Aplicar enrutamiento de modelos (Model Routing):** Enviar tareas rutinarias al segmento *Economico / Batch* y reservar los modelos *Premium* solo para razonamiento complejo, reduciendo costos entre 60% y 80%.
            2. **Auditar el costo de Prompt Caching en aplicaciones RAG:** Comparar el porcentaje de descuento del cache antes de adoptar modelos del grupo *Contexto Largo / Cache Alto*.
            3. **Migrar procesos asincronos a tarifas batch o flex:** Trasladar cargas nocturnas o por lotes desde tarifas standard permite bajar de segmento sin cambiar de familia de modelo.
            """
        )
