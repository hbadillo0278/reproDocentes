import streamlit as st
import polars as pl
import matplotlib.pyplot as plt

# Configuración de la página con fuente Montserrat y fondo institucional
st.set_page_config(layout="wide", page_title="Dashboard de Competencias Académicas", page_icon="📊")

# Estilos para imagen de fondo y fuente
st.markdown("""
    <style>
    .block-container {
        background-image: url('D:/Tutorial/colibri_gem.png'); /* Ruta local de la imagen del colibrí */
        background-size: cover;
        background-position: center;
        font-family: 'Montserrat', sans-serif;
        font-size: 11px;
        color: white;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Mostrar logotipo de CONALEP Estado de México
st.image("LogotipoConalep.png", width=650)  # Ruta local del logotipo

# Cargar datos con caching
@st.cache_data(ttl=600)
def cargar_datos():
    try:
        df = pl.read_csv("Datos.csv", separator=";")
        df = df.sort(["Semana", "Plantel", "DOCENTE"])
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None

df = cargar_datos()

if df is None or not all(col in df.columns for col in ["Semana", "Plantel", "DOCENTE", "MODULO", "COMPETENTES", "NO COMPETENTES", "TOTAL ALUMNOS"]):
    st.warning("No se encontraron algunas columnas clave. Revisa el archivo CSV.")
    st.stop()

# Menú Principal sin "Competentes"
opcion = st.sidebar.selectbox("📌 Menú Principal", ["No Competentes", "Comportamiento Semanal de Docentes"])

### 📊 OPCIÓN 1: NO COMPETENTES
if opcion == "No Competentes":
    st.title("📉 Datos de Docentes NO Competentes")

    semana_seleccionada = st.selectbox("📅 Selecciona una semana", sorted(df["Semana"].unique()))
    plantel_seleccionado = st.selectbox("🏫 Selecciona un plantel", sorted(df["Plantel"].unique()))
    df_filtrado = df.filter((df["Semana"] == semana_seleccionada) & (df["Plantel"] == plantel_seleccionado))

    # 📊 Ranking de Docentes NO Competentes - TOP 15
    st.subheader("📊 Ranking de Docentes NO Competentes - TOP 15")
    ranking_docentes_no = df_filtrado.group_by("DOCENTE").agg(pl.sum("NO COMPETENTES"), pl.sum("TOTAL ALUMNOS")).sort("NO COMPETENTES", descending=True).head(15)

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(ranking_docentes_no["DOCENTE"], ranking_docentes_no["NO COMPETENTES"], color="red")

    ax.invert_yaxis()  # Ordenar de mayor a menor

    # Etiquetas en las barras
    for bar, estudiantes, total in zip(bars, ranking_docentes_no["NO COMPETENTES"], ranking_docentes_no["TOTAL ALUMNOS"]):
        porcentaje = (estudiantes / total) * 100
        ax.text(bar.get_width() - 3, bar.get_y() + bar.get_height()/2, f"{estudiantes} - {porcentaje:.1f}%",  
                ha='right', va='center', fontsize=10, color="white", fontweight="bold")

    ax.set_xlabel("Total de Estudiantes NO Competentes - % de No Competencia")
    ax.set_ylabel("Docentes")
    ax.set_title(f"Cantidad y porcentaje de estudiantes reprobados por los 15 docentes con mayor número de reprobaciones - Semana {semana_seleccionada}")
    st.pyplot(fig)

    # 📊 Ranking de Módulos con más estudiantes NO Competentes - TOP 15
    st.subheader("📌 Ranking de Módulos con más Estudiantes NO Competentes - TOP 15")

    ranking_modulos = df_filtrado.group_by("MODULO").agg(pl.sum("NO COMPETENTES"), pl.sum("TOTAL ALUMNOS")).sort("NO COMPETENTES", descending=True).head(15)

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(ranking_modulos["MODULO"], ranking_modulos["NO COMPETENTES"], color="darkred", edgecolor="black", alpha=0.7)

    ax.invert_yaxis()  # Ordenar de mayor a menor

    # Etiquetas en las barras
    for bar, estudiantes, total in zip(bars, ranking_modulos["NO COMPETENTES"], ranking_modulos["TOTAL ALUMNOS"]):
        porcentaje = (estudiantes / total) * 100
        ax.text(bar.get_width() - 3, bar.get_y() + bar.get_height()/2, f"{estudiantes} - {porcentaje:.1f}%",  
                ha='right', va='center', fontsize=10, color="white", fontweight="bold")

    ax.set_xlabel("Total de Estudiantes NO Competentes - % de No Competencia")
    ax.set_ylabel("Módulo")
    ax.set_title(f"Cantidad y porcentaje de estudiantes reprobados en los 15 módulos con mayor número de reprobaciones - Semana {semana_seleccionada}")
    st.pyplot(fig)

### 📊 OPCIÓN 2: COMPORTAMIENTO SEMANAL DE DOCENTES
elif opcion == "Comportamiento Semanal de Docentes":
    st.title("📊 Evolución Semanal de Docentes")

    plantel_seleccionado = st.selectbox("🏫 Selecciona un plantel", sorted(df["Plantel"].unique()))
    docentes_disponibles = df.filter(df["Plantel"] == plantel_seleccionado)["DOCENTE"].unique()
    docente_seleccionado = st.selectbox("👨‍🏫 Selecciona un docente", sorted(docentes_disponibles))

    df_filtrado = df.filter((df["Plantel"] == plantel_seleccionado) & (df["DOCENTE"] == docente_seleccionado))
    df_agrupado = df_filtrado.group_by("Semana").agg(pl.sum("NO COMPETENTES"), pl.sum("TOTAL ALUMNOS"))

    st.subheader(f"📊 Evolución de Estudiantes NO Competentes para {docente_seleccionado}")

    fig, ax = plt.subplots(figsize=(10, 5))

    valores = df_agrupado["NO COMPETENTES"]
    max_valor = valores.max()
    min_valor = valores.min()

    colores = ["red" if val == max_valor else "green" if val == min_valor else "orange" for val in valores]

    bars = ax.bar(df_agrupado["Semana"], valores, color=colores, edgecolor="black", alpha=0.7)

    # Etiquetas con total y porcentaje
    for bar, estudiantes, total in zip(bars, valores, df_agrupado["TOTAL ALUMNOS"]):
        porcentaje = (estudiantes / total) * 100
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 5, f"{estudiantes} - {porcentaje:.1f}%",
                ha="center", fontsize=10, color="white", fontweight="bold")

    ax.set_xlabel("Semana")
    ax.set_ylabel("Total Estudiantes NO Competentes - % de No Competencia")
    ax.set_title(f"Evolución Semanal - {docente_seleccionado}")

    st.pyplot(fig)

