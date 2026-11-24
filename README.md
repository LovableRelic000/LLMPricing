# 🤖 Segmentación de Precios de APIs de LLMs con K-Means y Streamlit

Proyecto integrador de **Minería de Datos** que aplica aprendizaje no supervisado (**K-Means**) sobre el dataset `price_snapshots.csv` (tarifas de APIs de Modelos de Lenguaje Grande / LLMs en USD por millón de tokens) y presenta los resultados en un **Dashboard interactivo en Streamlit**.

---

## 📌 Descripción del Proyecto

El mercado de APIs de LLMs ofrece cientos de combinaciones de proveedores, modelos y niveles de servicio (`standard`, `batch`, `flex`, `priority`, `long_context`). Este proyecto:

1. **Explora y limpia** el dataset `price_snapshots.csv` (2,970 registros originales), filtrando nulos en las 3 variables principales (`input_usd_per_1m`, `output_usd_per_1m`, `cached_input_usd_per_1m`), verificando duplicados y tratando valores atípicos mediante el método **IQR (1.5×)** (2,151 registros limpios).
2. **Estandariza** las variables con `StandardScaler` y evalúa **K-Means** para $K \in \{2, 3, 4, 5, 6\}$ utilizando el **Método del Codo (Inercia)** y el **Silhouette Score**.
3. **Compara dos configuraciones** (K=4 con datos escalados vs. K=4 sin escalar) para demostrar el impacto del escalamiento en la calidad y cohesión de los clústeres.
4. **Segmenta el mercado en 4 perfiles claros** y exporta el resultado a `data/dataset_procesado.csv`:
   - **Modelos Económicos / Batch**
   - **Gama Media Estándar**
   - **Contexto Largo / Caché Alto**
   - **Modelos Premium / Alto Rendimiento**
5. **Visualiza los hallazgos** en un dashboard interactivo de 2 páginas construido con **Streamlit** y **Plotly**.

---

## 🛠️ Herramientas y Tecnologías

- **Lenguaje:** Python 3.10+
- **Manipulación de datos:** `pandas`, `numpy`
- **Machine Learning:** `scikit-learn` (`StandardScaler`, `KMeans`, `silhouette_score`)
- **Visualización (Notebook):** `matplotlib`, `seaborn`
- **Dashboard Interactivo:** `streamlit`, `plotly`
- **Entorno de análisis:** Jupyter Notebook

---

## 📁 Estructura del Proyecto

```text
Proyecto_Integrador_LLM_Pricing/
├── data/
│   ├── price_snapshots.csv          # Dataset original de precios de APIs de LLMs
│   └── dataset_procesado.csv        # Dataset limpio + columnas Cluster y Nombre_Cluster
├── img/
│   ├── 01_distribucion_precios.png  # Gráfica exploratoria 1 (Histogramas)
│   ├── 02_precios_por_proveedor.png # Gráfica exploratoria 2 (Proveedores)
│   ├── 03_correlacion_y_dispersion.png # Gráfica exploratoria 3 (Correlación y dispersión)
│   ├── 04_codo_y_silhouette.png     # Evaluación de K=2..6 (Inercia y Silhouette)
│   ├── 05_clusters_kmeans.png       # Scatter plot final con centroides (X roja)
│   ├── 06_dashboard_pagina1.png     # Captura del Dashboard — Página 1
│   └── 07_dashboard_pagina2.png     # Captura del Dashboard — Página 2
├── notebooks/
│   └── analisis_kmeans.ipynb        # Análisis completo paso a paso
├── Documentacion_Proyecto_Integrador_KMeans.pdf  # Documentación oficial del proyecto (PDF)
├── app.py                           # Dashboard interactivo en Streamlit (2 páginas)
├── requirements.txt                 # Dependencias del proyecto
├── .gitignore                       # Archivos excluidos para GitHub
└── README.md                        # Documentación del proyecto
```

---

## 🚀 Instrucciones de Instalación y Ejecución

### 1. Clonar o abrir el proyecto e instalar dependencias

```bash
cd Proyecto_Integrador_LLM_Pricing
pip install -r requirements.txt
```

### 2. Ejecutar el Notebook de Análisis K-Means

Puedes abrir y ejecutar `notebooks/analisis_kmeans.ipynb` en Jupyter Notebook o VS Code:

```bash
jupyter notebook notebooks/analisis_kmeans.ipynb
```

Al ejecutar todas las celdas:
- Se generan las gráficas PNG dentro de `img/`.
- Se genera el archivo procesado `data/dataset_procesado.csv`.

### 3. Ejecutar el Dashboard Interactivo en Streamlit

Desde la raíz del proyecto (`Proyecto_Integrador_LLM_Pricing/`):

```bash
streamlit run app.py
```

Se abrirá automáticamente en tu navegador (por defecto en `http://localhost:8501`) con dos páginas navegables desde la barra lateral:
- **Análisis General:** 4 KPIs principales, gráficas por proveedor y nivel de precio, histograma y estadísticas descriptivas.
- **Segmentación mediante K-Means:** 3 filtros interactivos (`provider`, `price_tier`, `Nombre_Cluster`), distribución por clúster, dispersión Input vs Output con centroides, gráficas comparativas, tabla de estadísticas, descripción de grupos, hallazgos y recomendaciones.
