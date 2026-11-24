import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configuración general de la página
st.set_page_config(
    page_title="Segmentación de Precios de APIs de LLMs (K-Means)",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paleta consistente por clúster
PALETA_CLUSTERS = {
    "Modelos Económicos / Batch": "#10B981",
    "Gama Media Estándar": "#3B82F6",
    "Contexto Largo / Caché Alto": "#F59E0B",
    "Modelos Premium / Alto Rendimiento": "#8B5CF6",
}

ORDEN_CLUSTERS = [
    "Modelos Económicos / Batch",
    "Gama Media Estándar",
    "Contexto Largo / Caché Alto",
    "Modelos Premium / Alto Rendimiento",
]

FEATURES = ["input_usd_per_1m", "output_usd_per_1m", "cached_input_usd_per_1m"]


@st.cache_data
def cargar_datos() -> pd.DataFrame:
    ruta = os.path.join(os.path.dirname(__file__), "data", "dataset_procesado.csv")
    if not os.path.exists(ruta):
        st.error(
            "No se encontró el archivo `data/dataset_procesado.csv`. "
            "Ejecuta primero el notebook `notebooks/analisis_kmeans.ipynb`."
        )
        st.stop()
    return pd.read_csv(ruta)


df = cargar_datos()

# ==============================================================================
# BARRA LATERAL: NAVEGACIÓN ENTRE PÁGINAS
# ==============================================================================
st.sidebar.title("🧭 Navegación")
pagina = st.sidebar.radio(
    "Selecciona una vista:",
    options=[
        "📊 Análisis General",
        "🎯 Segmentación mediante K-Means",
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "**Proyecto Integrador de Minería de Datos**\n\n"
    "Dataset: `price_snapshots.csv` (Precios de APIs de LLMs)\n\n"
    "Algoritmo: K-Means (K=4, `StandardScaler`)"
)

# ==============================================================================
# PÁGINA 1: ANÁLISIS GENERAL
# ==============================================================================
if pagina == "📊 Análisis General":
    st.title("🤖 Análisis de Precios de APIs de LLMs")
    st.markdown(
        "Dashboard interactivo para explorar el mercado de tarifas de Modelos de Lenguaje Grande "
        "(LLMs) en USD por millón de tokens, tras el proceso de limpieza, eliminación de outliers (IQR) "
        "y segmentación mediante **K-Means**."
    )

    # 4 KPIs principales
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registros Analizados", f"{len(df):,}")
    col2.metric("Precio Promedio Input", f"${df['input_usd_per_1m'].mean():.2f} / 1M")
    col3.metric("Precio Promedio Output", f"${df['output_usd_per_1m'].mean():.2f} / 1M")
    col4.metric("Cantidad de Proveedores", f"{df['provider'].nunique()}")

    st.markdown("---")

    # Visualizaciones generales: Proveedores y Niveles de Precio
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Registros por Proveedor")
        prov_counts = df["provider"].value_counts().reset_index()
        prov_counts.columns = ["Proveedor", "Registros"]
        fig_prov = px.bar(
            prov_counts,
            x="Registros",
            y="Proveedor",
            orientation="h",
            text="Registros",
            color="Registros",
            color_continuous_scale="Blues",
        )
        fig_prov.update_layout(
            yaxis={"categoryorder": "total ascending"},
            showlegend=False,
            coloraxis_showscale=False,
            height=400,
        )
        st.plotly_chart(fig_prov, width="stretch")

    with c2:
        st.subheader("Precio Promedio (Input vs Output) por Proveedor")
        prov_avg = (
            df.groupby("provider")[["input_usd_per_1m", "output_usd_per_1m"]]
            .mean()
            .reset_index()
            .melt(id_vars="provider", var_name="Tipo", value_name="USD_por_1M")
        )
        prov_avg["Tipo"] = prov_avg["Tipo"].replace(
            {
                "input_usd_per_1m": "Input USD/1M",
                "output_usd_per_1m": "Output USD/1M",
            }
        )
        fig_avg = px.bar(
            prov_avg,
            x="provider",
            y="USD_por_1M",
            color="Tipo",
            barmode="group",
            color_discrete_map={"Input USD/1M": "#3B82F6", "Output USD/1M": "#F59E0B"},
            labels={"provider": "Proveedor", "USD_por_1M": "USD por 1M tokens"},
        )
        fig_avg.update_layout(height=400)
        st.plotly_chart(fig_avg, width="stretch")

    # Distribución por price_tier y distribución de precios
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Distribución por Nivel de Precio (price_tier)")
        tier_counts = df["price_tier"].value_counts().reset_index()
        tier_counts.columns = ["Nivel de Precio", "Registros"]
        fig_tier = px.bar(
            tier_counts,
            x="Registros",
            y="Nivel de Precio",
            orientation="h",
            text="Registros",
            color="Registros",
            color_continuous_scale="Teal",
        )
        fig_tier.update_layout(
            yaxis={"categoryorder": "total ascending"},
            coloraxis_showscale=False,
            height=420,
        )
        st.plotly_chart(fig_tier, width="stretch")

    with c4:
        st.subheader("Distribución de Precios de Salida (output_usd_per_1m)")
        fig_hist = px.histogram(
            df,
            x="output_usd_per_1m",
            nbins=30,
            marginal="box",
            color_discrete_sequence=["#6366F1"],
            labels={"output_usd_per_1m": "Output USD / 1M tokens"},
        )
        fig_hist.update_layout(height=420)
        st.plotly_chart(fig_hist, width="stretch")

    st.markdown("---")
    st.subheader("📋 Estadísticas Descriptivas Generales")
    st.dataframe(
        df[FEATURES].describe().T.rename(
            columns={
                "count": "Conteo",
                "mean": "Media (USD)",
                "std": "Desv. Estándar",
                "min": "Mínimo",
                "25%": "Q1 (25%)",
                "50%": "Mediana (50%)",
                "75%": "Q3 (75%)",
                "max": "Máximo",
            }
        ).round(4),
        width="stretch",
    )

    with st.expander("🔍 Ver muestra del dataset procesado (primeros 20 registros)"):
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

# ==============================================================================
# PÁGINA 2: SEGMENTACIÓN MEDIANTE K-MEANS
# ==============================================================================
else:
    st.title("🎯 Segmentación de Precios mediante K-Means (K = 4)")
    st.markdown(
        "Explora los 4 segmentos identificados por el algoritmo **K-Means** con datos estandarizados "
        "(`StandardScaler`, **Silhouette Score = 0.5310**). Utiliza los filtros de la barra lateral "
        "para inspeccionar proveedores, niveles de precio y clústeres específicos."
    )

    # 3 Filtros interactivos en el sidebar
    st.sidebar.markdown("### 🎛️ Filtros Interactivos")

    proveedores_disp = sorted(df["provider"].dropna().unique())
    filtro_provider = st.sidebar.multiselect(
        "1. Proveedor (provider):",
        options=proveedores_disp,
        default=proveedores_disp,
    )

    tiers_disp = sorted(df["price_tier"].dropna().unique())
    filtro_tier = st.sidebar.multiselect(
        "2. Nivel de precio (price_tier):",
        options=tiers_disp,
        default=tiers_disp,
    )

    clusters_disp = [c for c in ORDEN_CLUSTERS if c in df["Nombre_Cluster"].unique()]
    filtro_cluster = st.sidebar.multiselect(
        "3. Segmento (Nombre_Cluster):",
        options=clusters_disp,
        default=clusters_disp,
    )

    # Aplicar filtros
    df_filtrado = df[
        df["provider"].isin(filtro_provider)
        & df["price_tier"].isin(filtro_tier)
        & df["Nombre_Cluster"].isin(filtro_cluster)
    ].copy()

    if df_filtrado.empty:
        st.warning(
            "No hay registros que coincidan con la combinación de filtros seleccionada. "
            "Ajusta los filtros en la barra lateral."
        )
        st.stop()

    # KPIs dinámicos según filtros
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Registros Filtrados", f"{len(df_filtrado):,}")
    k2.metric("Input Promedio", f"${df_filtrado['input_usd_per_1m'].mean():.2f} / 1M")
    k3.metric("Output Promedio", f"${df_filtrado['output_usd_per_1m'].mean():.2f} / 1M")
    k4.metric("Caché Promedio", f"${df_filtrado['cached_input_usd_per_1m'].mean():.3f} / 1M")

    st.markdown("---")

    # Fila 1: Distribución por clúster + Dispersión Input vs Output
    g1, g2 = st.columns([1, 1.35])

    with g1:
        st.subheader("Distribución de Registros por Clúster")
        dist_cluster = (
            df_filtrado["Nombre_Cluster"]
            .value_counts()
            .reindex([c for c in ORDEN_CLUSTERS if c in df_filtrado["Nombre_Cluster"].unique()])
            .reset_index()
        )
        dist_cluster.columns = ["Nombre_Cluster", "Registros"]
        dist_cluster["Porcentaje"] = (dist_cluster["Registros"] / len(df_filtrado) * 100).round(1)

        fig_dist = px.bar(
            dist_cluster,
            x="Nombre_Cluster",
            y="Registros",
            color="Nombre_Cluster",
            color_discrete_map=PALETA_CLUSTERS,
            text=dist_cluster.apply(lambda r: f"{r['Registros']} ({r['Porcentaje']}%)", axis=1),
            labels={"Nombre_Cluster": "Clúster"},
        )
        fig_dist.update_layout(showlegend=False, xaxis_tickangle=-15, height=440)
        st.plotly_chart(fig_dist, width="stretch")

    with g2:
        st.subheader("Dispersión: Input vs Output USD/1M por Clúster")
        fig_scatter = px.scatter(
            df_filtrado,
            x="input_usd_per_1m",
            y="output_usd_per_1m",
            color="Nombre_Cluster",
            category_orders={"Nombre_Cluster": ORDEN_CLUSTERS},
            color_discrete_map=PALETA_CLUSTERS,
            hover_data=["provider", "model_id", "price_tier", "cached_input_usd_per_1m"],
            opacity=0.75,
            labels={
                "input_usd_per_1m": "Input USD / 1M tokens",
                "output_usd_per_1m": "Output USD / 1M tokens",
                "Nombre_Cluster": "Clúster",
            },
        )
        # Superponer centroides (medias) de los clústeres visibles
        centros = (
            df_filtrado.groupby("Nombre_Cluster")[["input_usd_per_1m", "output_usd_per_1m"]]
            .mean()
            .reset_index()
        )
        fig_scatter.add_trace(
            go.Scatter(
                x=centros["input_usd_per_1m"],
                y=centros["output_usd_per_1m"],
                mode="markers",
                marker=dict(symbol="x", size=14, color="red", line=dict(width=2, color="black")),
                name="Centroides",
                hovertemplate="<b>Centroide</b><br>Input: $%{x:.2f}<br>Output: $%{y:.2f}<extra></extra>",
            )
        )
        fig_scatter.update_layout(height=440, legend=dict(orientation="h", y=-0.22))
        st.plotly_chart(fig_scatter, width="stretch")

    # Fila 2: 2 Gráficas adicionales comparando características de los grupos
    g3, g4 = st.columns(2)

    with g3:
        st.subheader("Comparación de Precios Promedio por Clúster")
        prom_cluster = (
            df_filtrado.groupby("Nombre_Cluster")[FEATURES]
            .mean()
            .reindex([c for c in ORDEN_CLUSTERS if c in df_filtrado["Nombre_Cluster"].unique()])
            .reset_index()
            .melt(id_vars="Nombre_Cluster", var_name="Variable", value_name="Promedio_USD")
        )
        prom_cluster["Variable"] = prom_cluster["Variable"].replace(
            {
                "input_usd_per_1m": "Input USD/1M",
                "output_usd_per_1m": "Output USD/1M",
                "cached_input_usd_per_1m": "Cached Input USD/1M",
            }
        )
        fig_bar_comp = px.bar(
            prom_cluster,
            x="Nombre_Cluster",
            y="Promedio_USD",
            color="Variable",
            barmode="group",
            text_auto=".2f",
            color_discrete_sequence=["#3B82F6", "#8B5CF6", "#10B981"],
            labels={"Nombre_Cluster": "Clúster", "Promedio_USD": "USD promedio / 1M tokens"},
        )
        fig_bar_comp.update_layout(xaxis_tickangle=-15, height=430)
        st.plotly_chart(fig_bar_comp, width="stretch")

    with g4:
        st.subheader("Distribución de Precios de Salida por Clúster (Boxplot)")
        fig_box = px.box(
            df_filtrado,
            x="Nombre_Cluster",
            y="output_usd_per_1m",
            color="Nombre_Cluster",
            category_orders={"Nombre_Cluster": ORDEN_CLUSTERS},
            color_discrete_map=PALETA_CLUSTERS,
            points="outliers",
            labels={
                "Nombre_Cluster": "Clúster",
                "output_usd_per_1m": "Output USD / 1M tokens",
            },
        )
        fig_box.update_layout(showlegend=False, xaxis_tickangle=-15, height=430)
        st.plotly_chart(fig_box, width="stretch")

    st.markdown("---")

    # Tabla con estadísticas descriptivas por clúster
    st.subheader("📊 Estadísticas Descriptivas por Clúster")
    resumen_grupos = (
        df_filtrado.groupby("Nombre_Cluster")
        .agg(
            Registros=("input_usd_per_1m", "count"),
            Input_Promedio=("input_usd_per_1m", "mean"),
            Input_Mediana=("input_usd_per_1m", "median"),
            Output_Promedio=("output_usd_per_1m", "mean"),
            Output_Mediana=("output_usd_per_1m", "median"),
            Cached_Promedio=("cached_input_usd_per_1m", "mean"),
            Cached_Max=("cached_input_usd_per_1m", "max"),
        )
        .reindex([c for c in ORDEN_CLUSTERS if c in df_filtrado["Nombre_Cluster"].unique()])
        .round(3)
    )
    st.dataframe(resumen_grupos, width="stretch")

    st.markdown("---")

    # Sección de texto: Descripción de los grupos identificados
    st.subheader("🧩 Descripción de los Grupos Identificados")
    desc_col1, desc_col2 = st.columns(2)

    with desc_col1:
        st.info(
            "**1. Modelos Económicos / Batch (~48.9% del mercado)**\n\n"
            "Centroide aproximado: **\\$0.55** input | **\\$2.64** output | **\\$0.07** caché. "
            "Agrupa modelos ligeros (`mini`, `nano`, `flash`, `luna`) y modalidades `batch`/`flex` "
            "orientados a alto volumen, clasificación masiva, extracción estructurada y automatización de bajo costo."
        )
        st.warning(
            "**3. Contexto Largo / Caché Alto (~4.2% del mercado)**\n\n"
            "Centroide aproximado: **\\$4.21** input | **\\$10.95** output | **\\$0.78** caché. "
            "Segmento especializado (dominado por tarifas `priority_long_context` y `fast` de xAI y OpenAI) "
            "donde el costo de lectura en caché representa ~18–25% del input (muy superior al 10% habitual), "
            "aunque con un costo de generación (output) moderado."
        )

    with desc_col2:
        st.success(
            "**2. Gama Media Estándar (~31.8% del mercado)**\n\n"
            "Centroide aproximado: **\\$2.13** input | **\\$9.59** output | **\\$0.27** caché. "
            "Incluye modelos insignia de uso general (`gemini-2.5-pro`, `gpt-5.4`, `gpt-5.6-terra`, gama media de Anthropic y xAI) "
            "con un equilibrio sólido entre calidad de razonamiento y costo operativo."
        )
        st.error(
            "**4. Modelos Premium / Alto Rendimiento (~15.2% del mercado)**\n\n"
            "Centroide aproximado: **\\$4.93** input | **\\$24.05** output | **\\$0.45** caché. "
            "Concentra los modelos de mayor capacidad y tarifas de contexto largo (`gpt-5.6-sol`, `gpt-5.5`, "
            "`gemini-3.1-pro-preview`, modelos flagship de Anthropic), con costos de generación hasta **9x superiores** al segmento económico."
        )

    st.markdown("---")

    # Sección de Hallazgos Relevantes y Recomendaciones Prácticas
    h_col, r_col = st.columns(2)

    with h_col:
        st.subheader("🔎 Hallazgos Relevantes")
        st.markdown(
            """
            1. **El precio de salida (output) es el principal diferenciador de costo:** En promedio, generar tokens cuesta entre **4x y 5x más** que procesarlos como entrada; en el segmento Premium el output alcanza **\\$24.05/1M**, casi **9 veces** el costo del segmento Económico (\\$2.64/1M).
            2. **El escalamiento con `StandardScaler` reveló un segmento oculto de Caché Alto:** Sin escalar, la variable `output_usd_per_1m` domina la distancia euclidiana y oculta los patrones de caché. Al estandarizar las 3 variables, el modelo alcanzó un **Silhouette Score de 0.5310** y descubrió el clúster *Contexto Largo / Caché Alto* (\\$0.78/1M en caché).
            3. **Casi la mitad del mercado (48.9%) compite en el segmento Económico / Batch:** Proveedores como OpenAI, Google, Mistral y xAI ofrecen múltiples niveles (`batch`, `flex`, `standard`) por debajo de \\$1/1M en entrada, democratizando cargas masivas de IA.
            4. **Presencia de outliers extremos en modelos especializados:** Antes de aplicar IQR (1.5x), 291 registros (11.9%) presentaban precios de hasta \\$40 en entrada y \\$150 en salida, lo que demuestra una fuerte asimetría en las tarifas de modelos *Pro* y de razonamiento profundo.
            """
        )

    with r_col:
        st.subheader("💡 Recomendaciones Prácticas")
        st.markdown(
            """
            1. **Implementar enrutamiento inteligente de modelos (Model Routing):** Dirigir tareas rutinarias (clasificación, extracción, resúmenes simples) al clúster **Económicos / Batch** y reservar los modelos **Premium** exclusivamente para razonamiento complejo, reduciendo la factura de API entre un **60% y 80%**.
            2. **Auditar el costo de *Prompt Caching* en aplicaciones RAG o de contexto largo:** Antes de elegir un proveedor del clúster **Contexto Largo / Caché Alto**, comparar el porcentaje de descuento del caché (10% vs 25% del precio de entrada), ya que puede duplicar el gasto en flujos con alta reutilización de contexto.
            3. **Aprovechar modalidades `batch` y `flex` para procesos asíncronos:** Migrar pipelines nocturnos, análisis de documentos y generación masiva de datos de tarifas `standard` a `batch` permite mover cargas de **Gama Media** al segmento **Económico** sin perder calidad del modelo base.
            4. **Monitorear precios periódicamente:** Dado que el dataset registra cambios entre snapshots temporales, se recomienda re-ejecutar el pipeline de K-Means mensualmente para detectar caídas de precio y reclasificaciones de modelos insignia.
            """
        )
