"""
Análisis de Permisos de Circulación 2023
Solemne II — FITO9017 Programación en Python

Aplicación Streamlit que consume la API REST pública de datos.gob.cl
para analizar el registro de permisos de circulación 2023 publicado
por la Municipalidad de Calbuco.
"""

import json
from io import StringIO

import requests
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


# Identificador del dataset en el portal CKAN de datos.gob.cl
DATASET_ID = "d8a8dfb3-8b28-4193-bff7-af3a42794d25"
API_BASE = "https://datos.gob.cl/api/3/action"

st.set_page_config(page_title="Permisos de Circulación 2023", layout="centered")


# ---------- Funciones de acceso a la API ----------

@st.cache_data(ttl=3600, show_spinner=False)
def obtener_dataset(dataset_id):
    """GET package_show: metadatos y recursos del dataset."""
    r = requests.get(f"{API_BASE}/package_show", params={"id": dataset_id}, timeout=30)
    r.raise_for_status()
    return json.loads(r.text)["result"]


@st.cache_data(ttl=3600, show_spinner=False)
def cargar_csv(url):
    """Descarga el CSV (codificación latin-1 y separador ; como es habitual en Chile)."""
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return pd.read_csv(StringIO(r.content.decode("latin-1")), sep=";", on_bad_lines="skip")


# ---------- Encabezado ----------

st.title("Permisos de Circulación 2023")
st.write(
    "Análisis de los permisos de circulación 2023 emitidos por la "
    "**Municipalidad de Calbuco**. Los datos se obtienen en tiempo real desde "
    "la API pública de [datos.gob.cl](https://datos.gob.cl)."
)


# ---------- Carga de datos ----------

with st.spinner("Consultando la API..."):
    ds = obtener_dataset(DATASET_ID)

csv_url = next(r["url"] for r in ds["resources"] if r.get("format", "").upper() == "CSV")

with st.spinner("Descargando el archivo CSV..."):
    df = cargar_csv(csv_url)

with st.expander("Información del dataset"):
    st.write(f"**{ds['title']}**")
    st.write(f"Organización: {ds['organization']['title']}")
    st.write(f"Actualizado: {ds.get('metadata_modified', '')[:10]}")
    if ds.get("notes"):
        st.write(ds["notes"])


# ---------- 1. Resumen ----------

st.subheader("1. Resumen general")

c1, c2, c3 = st.columns(3)
c1.metric("Vehículos", f"{len(df):,}")
c2.metric("Variables", df.shape[1])
c3.metric("Marcas distintas", df["Marca"].nunique())

st.dataframe(df.head(8), width="stretch")


# ---------- 2. Filtros ----------

st.subheader("2. Filtros")

c1, c2 = st.columns(2)
combustibles = sorted(df["Tipo Combustible"].dropna().unique())
sel_comb = c1.multiselect("Tipo de combustible", combustibles, default=combustibles)

tipos = sorted(df["Tipo Vehiculo"].dropna().unique())
sel_tipo = c2.multiselect("Tipo de vehículo", tipos, default=tipos)

df_f = df[df["Tipo Combustible"].isin(sel_comb) & df["Tipo Vehiculo"].isin(sel_tipo)]
st.caption(f"Mostrando **{len(df_f):,}** de {len(df):,} registros.")


# ---------- 3. Análisis ----------

st.subheader("3. Análisis")

valor = pd.to_numeric(df_f["Valor Pagado"], errors="coerce")
año = pd.to_numeric(df_f["Año Vehículo"], errors="coerce")

c1, c2, c3 = st.columns(3)
c1.metric("Valor pagado promedio", f"${valor.mean():,.0f}")
c2.metric("Recaudación total", f"${valor.sum():,.0f}")
c3.metric("Antigüedad promedio", f"{2023 - año.mean():.1f} años")


# ---------- 4. Visualizaciones ----------

st.subheader("4. Visualizaciones")

tab1, tab2, tab3 = st.tabs(["Marcas", "Combustible", "Antigüedad"])

with tab1:
    top = df_f["Marca"].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(top.index[::-1], top.values[::-1], color="#1f77b4")
    ax.set_xlabel("Cantidad de vehículos")
    ax.set_title("Top 10 marcas en Calbuco (2023)")
    plt.tight_layout()
    st.pyplot(fig)

with tab2:
    conteo = df_f["Tipo Combustible"].value_counts()
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.pie(conteo.values, labels=conteo.index, autopct="%1.1f%%", colors=plt.cm.Set2.colors)
    ax.set_title("Distribución por tipo de combustible")
    plt.tight_layout()
    st.pyplot(fig)

with tab3:
    a = año.dropna()
    a = a[(a >= 1950) & (a <= 2024)]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.hist(a, bins=30, color="#2ca02c", edgecolor="white")
    ax.set_xlabel("Año del vehículo")
    ax.set_ylabel("Cantidad")
    ax.set_title("Antigüedad del parque vehicular")
    plt.tight_layout()
    st.pyplot(fig)


# ---------- 5. Hallazgos ----------

st.subheader("5. Hallazgos")

top_marca = df_f["Marca"].value_counts().head(1)
top_comb = df_f["Tipo Combustible"].value_counts().head(1)

st.markdown(f"- Se analizaron **{len(df_f):,}** permisos de circulación de 2023.")
st.markdown(
    f"- Marca más común: **{top_marca.index[0]}** "
    f"({100 * top_marca.iloc[0] / len(df_f):.1f}% del total)."
)
st.markdown(
    f"- Combustible predominante: **{top_comb.index[0]}** "
    f"({100 * top_comb.iloc[0] / len(df_f):.1f}% del parque)."
)
st.markdown(
    f"- Recaudación total estimada: **${valor.sum():,.0f}** "
    f"(promedio ${valor.mean():,.0f} por permiso)."
)


# ---------- Descarga ----------

st.divider()
st.download_button(
    "Descargar datos filtrados (CSV)",
    df_f.to_csv(index=False).encode("utf-8"),
    file_name="permisos_circulacion_2023_filtrado.csv",
    mime="text/csv",
)
st.caption("Fuente: Portal de Datos Abiertos del Gobierno de Chile — datos.gob.cl")
