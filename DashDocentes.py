import streamlit as st
import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns

# Aplicar estilos personalizados (Montserrat 10px)
st.markdown("""
    <style>
        body { font-family: 'Montserrat', sans-serif; font-size: 10px; }
        h1, h2, h3, h4, h5, h6 { font-family: 'Montserrat', sans-serif; }
        .stMarkdown { font-size: 10px !important; }
    </style>
""", unsafe_allow_html=True)

# Configurar título y descripción
st.title("📊 Dashboard de Competencias Académicas")
st.markdown("Filtro por Semana, Plantel y Análisis de Docentes y Módulos.")

# Cargar datos con manejo de errores
@st.cache_data
def cargar_datos():
    try:
        df = pl.read_csv("Datos.csv", separator=";")
        df = df.sort(["Semana", "Plantel", "DOCENTE", "MODULO"])
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None

df = cargar_datos()

if df is not None and all(col in df.columns for col in ["Semana", "Plantel", "DOCENTE", "MODULO", "NO COMPETENTES", "COMPETENTES", "TOTAL ALUMNOS"]):

    # 📅 **Filtros generales en contenedor**
    with st.container():
        st.subheader("🎛️ Filtros de Datos")
        semana_seleccionada = st.selectbox("📅 Selecciona una semana", sorted(df["Semana"].unique()))
        df_semanal = df.filter(df["Semana"] == semana_seleccionada)

        plantel_seleccionado = st.selectbox("🏫 Selecciona un plantel", sorted(df_semanal["Plantel"].unique()))
        df_plantel = df_semanal.filter(df_semanal["Plantel"] == plantel_seleccionado)

    # 👩‍🏫 **Ranking de Docentes con más No Competentes**
    ranking_docentes = (df_plantel.group_by("DOCENTE")
                        .agg(pl.sum("NO COMPETENTES"), pl.sum("TOTAL ALUMNOS"))
                        .with_columns((pl.col("NO COMPETENTES") / pl.col("TOTAL ALUMNOS") * 100).alias("PORCENTAJE NO COMPETENCIA"))
                        .sort("PORCENTAJE NO COMPETENCIA", descending=True)
                        .head(15))

    # 📊 **Ranking de los 15 mejores módulos por competencia**
    ranking_modulos = (df_plantel.group_by("MODULO")
                        .agg(pl.sum("COMPETENTES"), pl.sum("NO COMPETENTES"), pl.sum("TOTAL ALUMNOS"))
                        .with_columns((pl.col("COMPETENTES") / pl.col("TOTAL ALUMNOS") * 100).alias("PORCENTAJE COMPETENTES"))
                        .sort("PORCENTAJE COMPETENTES", descending=True)
                        .head(15))

    # 📌 **Sección de Ranking de Docentes**
    with st.container():
        st.subheader("📊 Ranking de Docentes con más No Competentes")
        if ranking_docentes.shape[0] > 0:
            fig, ax = plt.subplots(figsize=(10, 5))
            bars = ax.barh(ranking_docentes["DOCENTE"], ranking_docentes["PORCENTAJE NO COMPETENCIA"], color="red")

            for bar, estudiantes, porcentaje in zip(bars, ranking_docentes["NO COMPETENTES"], ranking_docentes["PORCENTAJE NO COMPETENCIA"]):
                ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f"{estudiantes} ({porcentaje:.1f}%)", ha='left', va='center', fontsize=10, color="black")

            ax.set_xlabel("Porcentaje de No Competencia (%)")
            ax.set_ylabel("Docentes")
            ax.set_title(f"Ranking de Docentes en {plantel_seleccionado}")
            st.pyplot(fig)
        else:
            st.warning("No hay suficientes datos para generar el ranking de docentes.")

    # 📌 **Sección de Ranking de Módulos**
    with st.container():
        st.subheader("📊 Ranking de los 15 Mejores Módulos por Competencia")
        if ranking_modulos.shape[0] > 0:
            fig, ax = plt.subplots(figsize=(10, 5))
            bars = ax.barh(ranking_modulos["MODULO"], ranking_modulos["PORCENTAJE COMPETENTES"], color="green")

            for bar, porcentaje in zip(bars, ranking_modulos["PORCENTAJE COMPETENTES"]):
                ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f"{porcentaje:.1f}%", ha='left', va='center', fontsize=10, color="black")

            ax.set_xlabel("Porcentaje de Competentes (%)")
            ax.set_ylabel("Módulos")
            ax.set_title(f"Ranking de Módulos en {plantel_seleccionado}")
            st.pyplot(fig)
        else:
            st.warning("No hay suficientes datos para generar el ranking de módulos.")

    # 🔥 **Mapa de Calor en Contenedor**
    with st.container():
        st.subheader("🔥 Mapa de Calor de No Competencia por Módulo")
        if ranking_modulos.shape[0] > 0:
            fig, ax = plt.subplots(figsize=(10, 5))
            heatmap_data = ranking_modulos.to_pandas()[["MODULO", "PORCENTAJE COMPETENTES"]].set_index("MODULO")
            sns.heatmap(heatmap_data, annot=True, cmap="coolwarm", linewidths=0.5, fmt=".1f", ax=ax)
            ax.set_title("Mapa de Calor de Competencias por Módulo")
            st.pyplot(fig)
        else:
            st.warning("No hay suficientes datos para generar el mapa de calor.")

else:
    st.warning("No se encontraron algunas columnas clave. Revisa el archivo CSV.")
