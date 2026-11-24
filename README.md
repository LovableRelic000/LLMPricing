# Segmentacion de Precios de APIs de LLMs con K-Means y Streamlit

Proyecto integrador de **Mineria de Datos** que aplica aprendizaje no supervisado (**K-Means**) sobre el dataset `price_snapshots.csv` (fuente: Kaggle, tarifas de APIs de Modelos de Lenguaje Grande en USD por millon de tokens) y presenta los resultados en un **Dashboard interactivo en Streamlit**.

## Descripcion del Proyecto

El mercado de APIs de LLMs ofrece decenas de combinaciones de proveedores, modelos y niveles de servicio (`standard`, `batch`, `flex`, `priority`, `long_context`). Este proyecto:

1. **Explora y limpia** `data/price_snapshots.csv` (2,970 registros originales), eliminando nulos en las 3 variables principales (`input_usd_per_1m`, `output_usd_per_1m`, `cached_input_usd_per_1m`), verificando duplicados y filtrando valores atipicos mediante **IQR (1.5x)** (2,151 registros limpios).
2. **Estandariza** las variables con `StandardScaler` y evalua **K-Means** para `K = 2, 3, 4, 5, 6` mediante el Metodo del Codo (Inercia) y Silhouette Score.
3. **Compara dos configuraciones** (`K = 4` con datos escalados vs. `K = 4` sin escalar) demostrando el impacto del escalamiento.
4. **Segmenta el mercado en 4 grupos** y exporta el resultado a `data/dataset_procesado.csv`:
   - Modelos Economicos / Batch
   - Gama Media Estandar
   - Contexto Largo / Cache Alto
   - Modelos Premium / Alto Rendimiento
5. **Presenta los resultados** en un dashboard interactivo de 2 paginas en **Streamlit** y **Plotly**.

## Herramientas Utilizadas

- **Python 3.10+**
- **Analisis y modelado:** `pandas`, `scikit-learn` (`StandardScaler`, `KMeans`, `silhouette_score`)
- **Visualizacion (script):** `matplotlib`, `seaborn`
- **Dashboard interactivo:** `streamlit`, `plotly`

## Estructura del Proyecto

```text
Proyecto_Integrador_LLM_Pricing/
├── .streamlit/
│   └── config.toml                               # Tema visual claro del dashboard
├── data/
│   ├── price_snapshots.csv                       # Dataset original (Kaggle)
│   └── dataset_procesado.csv                     # Dataset limpio con Cluster y Nombre_Cluster
├── img/
│   ├── 01_distribucion_precios.png               # Grafica exploratoria 1
│   ├── 02_precios_por_proveedor.png              # Grafica exploratoria 2
│   ├── 03_correlacion_y_dispersion.png           # Grafica exploratoria 3
│   ├── 04_codo_y_silhouette.png                  # Evaluacion K = 2 a 6
│   ├── 05_clusters_kmeans.png                    # Dispersion final con centroides (X roja)
│   ├── 06_dashboard_pagina1.png                  # Captura del Dashboard (Pagina 1)
│   └── 07_dashboard_pagina2.png                  # Captura del Dashboard (Pagina 2)
├── analisis_kmeans.py                            # Script completo de analisis y K-Means
├── app.py                                        # Dashboard interactivo en Streamlit
├── Documentacion_Proyecto_Integrador_KMeans.pdf  # Documentacion oficial en PDF
├── requirements.txt                              # Dependencias del proyecto
├── .gitignore
└── README.md
```

## Instrucciones de Ejecucion

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar el analisis K-Means

```bash
python analisis_kmeans.py
```

Esto genera las 5 graficas PNG dentro de `img/` y exporta `data/dataset_procesado.csv`.

### 3. Ejecutar el Dashboard en Streamlit

```bash
streamlit run app.py
```

Se abrira en `http://localhost:8501` con dos paginas navegables desde la barra lateral:
- **Analisis General:** 4 KPIs principales, graficas por proveedor y nivel de precio, histograma y estadisticas descriptivas.
- **Segmentacion mediante K-Means:** 3 filtros interactivos (`provider`, `price_tier`, `Nombre_Cluster`), distribucion por cluster, dispersion con centroides, graficas comparativas, tabla descriptiva, descripcion de grupos, hallazgos y recomendaciones.
