import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

sns.set_theme(style="whitegrid")
os.makedirs("img", exist_ok=True)

print("=== 1. EXPLORACION INICIAL ===")
df = pd.read_csv("data/price_snapshots.csv")

print("\nPrimeros 10 registros:")
print(df.head(10))

print("\nDimensiones (filas, columnas):", df.shape)
print("\nColumnas y tipos de datos:")
print(df.dtypes)

print("\nEstadisticas descriptivas:")
print(df.describe())

print("\nValores nulos por columna:")
print(df.isnull().sum())

print("\nRegistros duplicados totales:", df.duplicated().sum())

cols = ["input_usd_per_1m", "output_usd_per_1m", "cached_input_usd_per_1m"]

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
titulos = ["Input USD / 1M", "Output USD / 1M", "Cached Input USD / 1M"]
for i in range(3):
    datos = df[cols[i]].dropna()
    sns.histplot(datos, bins=30, kde=True, ax=axes[i], color="#2563EB")
    axes[i].axvline(datos.median(), color="red", linestyle="--", label=f"Mediana: ${datos.median():.2f}")
    axes[i].set_title(titulos[i])
    axes[i].set_xlabel("USD por 1M tokens")
    axes[i].set_ylabel("Frecuencia")
    axes[i].legend()
plt.suptitle("Distribucion de Precios de APIs de LLMs (Dataset Original)")
plt.tight_layout()
plt.savefig("img/01_distribucion_precios.png", dpi=150)
plt.close()

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
conteo_prov = df["provider"].value_counts()
sns.barplot(x=conteo_prov.values, y=conteo_prov.index, ax=axes[0], color="#2563EB")
axes[0].set_title("Registros por Proveedor")
axes[0].set_xlabel("Cantidad de registros")
axes[0].set_ylabel("Proveedor")

prom_prov = df.groupby("provider")[["input_usd_per_1m", "output_usd_per_1m"]].mean()
prom_prov = prom_prov.sort_values("output_usd_per_1m", ascending=False)
prom_prov.plot(kind="barh", ax=axes[1], color=["#2563EB", "#F59E0B"])
axes[1].set_title("Precio Promedio (Input vs Output) por Proveedor")
axes[1].set_xlabel("USD por 1M tokens")
axes[1].set_ylabel("Proveedor")
axes[1].legend(["Input USD/1M", "Output USD/1M"])
plt.tight_layout()
plt.savefig("img/02_precios_por_proveedor.png", dpi=150)
plt.close()

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.heatmap(df[cols].corr(), annot=True, fmt=".3f", cmap="Blues", square=True, ax=axes[0])
axes[0].set_title("Correlacion entre Variables de Precio")

top5 = df["provider"].value_counts().head(5).index
df_temp = df.copy()
df_temp["proveedor_top"] = df_temp["provider"].where(df_temp["provider"].isin(top5), "Otros")
sns.scatterplot(data=df_temp, x="input_usd_per_1m", y="output_usd_per_1m", hue="proveedor_top", alpha=0.65, ax=axes[1])
axes[1].set_title("Dispersion Input vs Output por Proveedor")
axes[1].set_xlabel("Input USD / 1M tokens")
axes[1].set_ylabel("Output USD / 1M tokens")
plt.tight_layout()
plt.savefig("img/03_correlacion_y_dispersion.png", dpi=150)
plt.close()

print("\n=== 2. LIMPIEZA Y PREPARACION ===")
print("Registros originales:", len(df))

df_limpio = df.dropna(subset=cols).drop_duplicates().copy()
print("Eliminados por nulos en las 3 columnas:", len(df) - len(df_limpio))
print("Registros despues de quitar nulos y duplicados:", len(df_limpio))

filtro_iqr = pd.Series(True, index=df_limpio.index)
for col in cols:
    q1 = df_limpio[col].quantile(0.25)
    q3 = df_limpio[col].quantile(0.75)
    iqr = q3 - q1
    lim_inf = q1 - 1.5 * iqr
    lim_sup = q3 + 1.5 * iqr
    filtro_iqr = filtro_iqr & (df_limpio[col] >= lim_inf) & (df_limpio[col] <= lim_sup)

eliminados_outliers = (~filtro_iqr).sum()
df_limpio = df_limpio[filtro_iqr].reset_index(drop=True)
print(f"Eliminados por outliers (IQR 1.5x): {eliminados_outliers}")
print("Registros limpios finales:", len(df_limpio))

scaler = StandardScaler()
X_raw = df_limpio[cols].values
X_scaled = scaler.fit_transform(X_raw)

print("\n=== 3. EVALUACION DE K-MEANS (K = 2 a 6) ===")
valores_k = [2, 3, 4, 5, 6]
inercias = []
silhouettes = []

for k in valores_k:
    modelo = KMeans(n_clusters=k, random_state=42, n_init=10)
    etiquetas = modelo.fit_predict(X_scaled)
    inercia = modelo.inertia_
    sil = silhouette_score(X_scaled, etiquetas)
    inercias.append(inercia)
    silhouettes.append(sil)
    print(f"K={k} -> Inercia: {inercia:.2f} | Silhouette Score: {sil:.4f} | Iteraciones: {modelo.n_iter_}")

fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
axes[0].plot(valores_k, inercias, marker="o", linewidth=2, color="#2563EB")
axes[0].set_title("Metodo del Codo (Inercia vs K)")
axes[0].set_xlabel("Numero de clusteres (K)")
axes[0].set_ylabel("Inercia")
axes[0].set_xticks(valores_k)

axes[1].plot(valores_k, silhouettes, marker="s", linewidth=2, color="#10B981")
axes[1].set_title("Silhouette Score vs K")
axes[1].set_xlabel("Numero de clusteres (K)")
axes[1].set_ylabel("Silhouette Score")
axes[1].set_xticks(valores_k)

plt.tight_layout()
plt.savefig("img/04_codo_y_silhouette.png", dpi=150)
plt.close()

print("\n=== 4. MODELO FINAL (K = 4, ESCALADO) ===")
kmeans_final = KMeans(n_clusters=4, random_state=42, n_init=10)
df_limpio["Cluster"] = kmeans_final.fit_predict(X_scaled)

sil_escalado = silhouette_score(X_scaled, df_limpio["Cluster"])
print("Iteraciones (n_iter_):", kmeans_final.n_iter_)
print(f"Silhouette Score final: {sil_escalado:.4f}")
print("\nCantidad de registros por cluster:")
print(df_limpio["Cluster"].value_counts().sort_index())

centroides = pd.DataFrame(scaler.inverse_transform(kmeans_final.cluster_centers_), columns=cols)
print("\nCentroides desescalados (USD por 1M tokens):")
print(centroides.round(4))

print("\n=== COMPARACION: ESCALADO VS SIN ESCALAR (K = 4) ===")
kmeans_raw = KMeans(n_clusters=4, random_state=42, n_init=10)
etiquetas_raw = kmeans_raw.fit_predict(X_raw)

sil_raw_en_std = silhouette_score(X_scaled, etiquetas_raw)
sil_raw_en_usd = silhouette_score(X_raw, etiquetas_raw)
print(f"Escalado    -> Silhouette (espacio estandarizado): {sil_escalado:.4f}")
print(f"Sin escalar -> Silhouette (espacio estandarizado): {sil_raw_en_std:.4f} | (en USD): {sil_raw_en_usd:.4f}")
print("\nDistribucion sin escalar:")
print(pd.Series(etiquetas_raw).value_counts().sort_index())
print("\nCentroides sin escalar (USD):")
print(pd.DataFrame(kmeans_raw.cluster_centers_, columns=cols).round(4))

print("\n=== 5. INTERPRETACION Y EXPORTACION ===")
id_eco = centroides["output_usd_per_1m"].idxmin()
id_prem = centroides["output_usd_per_1m"].idxmax()
id_cache = centroides["cached_input_usd_per_1m"].idxmax()
id_media = [c for c in centroides.index if c not in {id_eco, id_prem, id_cache}][0]

nombres = {
    id_eco: "Modelos Economicos / Batch",
    id_media: "Gama Media Estandar",
    id_cache: "Contexto Largo / Cache Alto",
    id_prem: "Modelos Premium / Alto Rendimiento",
}
df_limpio["Nombre_Cluster"] = df_limpio["Cluster"].map(nombres)

print("\nEstadisticas descriptivas por grupo:")
print(df_limpio.groupby("Nombre_Cluster")[cols].agg(["count", "mean", "median", "min", "max"]).round(3))

orden = [
    "Modelos Economicos / Batch",
    "Gama Media Estandar",
    "Contexto Largo / Cache Alto",
    "Modelos Premium / Alto Rendimiento",
]
paleta = {
    "Modelos Economicos / Batch": "#10B981",
    "Gama Media Estandar": "#2563EB",
    "Contexto Largo / Cache Alto": "#F59E0B",
    "Modelos Premium / Alto Rendimiento": "#7C3AED",
}

plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=df_limpio,
    x="input_usd_per_1m",
    y="output_usd_per_1m",
    hue="Nombre_Cluster",
    hue_order=orden,
    palette=paleta,
    alpha=0.75,
    s=60,
)
plt.scatter(
    centroides["input_usd_per_1m"],
    centroides["output_usd_per_1m"],
    marker="X",
    s=240,
    color="red",
    edgecolor="black",
    zorder=10,
    label="Centroides",
)
plt.title("Segmentacion K-Means (K=4) de Precios de APIs de LLMs")
plt.xlabel("Input USD / 1M tokens")
plt.ylabel("Output USD / 1M tokens")
plt.legend(title="Segmento")
plt.tight_layout()
plt.savefig("img/05_clusters_kmeans.png", dpi=150)
plt.close()

df_limpio.to_csv("data/dataset_procesado.csv", index=False, encoding="utf-8")
print("\nArchivo exportado correctamente: data/dataset_procesado.csv")
print("Graficas guardadas en la carpeta img/")
