import streamlit as st
import pandas as pd
import polars as pl
import matplotlib.pyplot as plt
import numpy as np
import io

st.markdown("""
    <style>
        #MainMenu {display: none !important;}
        header {display: none !important;}
        footer {display: none !important;}
        button[title="View fullscreen"] {display: none !important;}
        button[title="View source"] {display: none !important;}
        button[title="Report a bug"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)
@st.cache_data(ttl=600)
def cargar_datos():
    try:
        archivo_excel = "Datos1.xlsx"
        xls = pd.ExcelFile(archivo_excel)
        hojas_disponibles = xls.sheet_names

        if "Datos" not in hojas_disponibles:
            st.error("La hoja 'Datos' no fue encontrada en el archivo.")
            return None

        df_pandas_datos = pd.read_excel(archivo_excel, sheet_name="Datos")
        df = pl.from_pandas(df_pandas_datos).sort(["Semana", "Plantel", "DOCENTE"])
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None

df = cargar_datos()

if df is None or not all(col in df.columns for col in ["Semana", "Plantel", "DOCENTE", "MODULO", "COMPETENTES", "NO COMPETENTES", "TOTAL ALUMNOS"]):
    st.warning("No se encontraron algunas columnas clave. Revisa el archivo Excel.")
    st.stop()

if "logueado" not in st.session_state:
    st.session_state.logueado = False
    st.session_state.plantel_usuario = None
    st.session_state.administrador = False

if not st.session_state.logueado:
    st.sidebar.title("🔒 Inicio de sesión")
    usuario = st.sidebar.text_input("Usuario")
    contrasena = st.sidebar.text_input("Contraseña", type="password")
    login_btn = st.sidebar.button("Iniciar sesión")

    @st.cache_data(ttl=600)
    def validar_usuario(user, password):
        if user.lower() == "admin" and password == "admin":
            return True, "ADMIN"
        try:
            archivo_excel = "Datos1.xlsx"
            xls = pd.ExcelFile(archivo_excel)
            hojas_disponibles = xls.sheet_names

            if "Planteles" not in hojas_disponibles:
                st.error("La hoja 'Planteles' no existe en el archivo Excel.")
                return False, None

            df_pandas_planteles = pd.read_excel(archivo_excel, sheet_name="Planteles")
            planteles = pl.from_pandas(df_pandas_planteles)

            usuario_filtrado = planteles.filter(
                (planteles["Usuario"].str.strip_chars() == user) & (planteles["Contrasena"].str.strip_chars() == password)
            )

            if usuario_filtrado.is_empty():
                return False, None
            return True, usuario_filtrado["Plantel"][0]
        except Exception as e:
            st.error(f"Error en la autenticación: {e}")
            return False, None

    if login_btn:
        acceso, plantel_usuario = validar_usuario(usuario, contrasena)
        if acceso:
            st.session_state.logueado = True
            st.session_state.plantel_usuario = plantel_usuario
            st.session_state.administrador = (usuario.lower() == "admin")
            st.sidebar.success(f"Bienvenido, {'ADMINISTRADOR' if st.session_state.administrador else usuario}")
        else:
            st.sidebar.error("Acceso denegado. Verifica tu usuario y contraseña.")

if st.session_state.logueado:
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.logueado = False
        st.session_state.plantel_usuario = None
        st.session_state.administrador = False
        st.rerun()

    opcion = st.sidebar.selectbox("📌 Menú Principal", [
        "No Competentes",
        "Comportamiento Semanal de Docentes",
        "Módulos Críticos y Recomendaciones"
    ])

    def graficar_barras(df_plot, etiqueta):
        fig, ax = plt.subplots(figsize=(10, max(4, len(df_plot)*0.5)))
        bars = ax.barh(df_plot[etiqueta], df_plot["NO_COMP"], color="crimson")
        ax.invert_yaxis()
        for bar, nc, total in zip(bars, df_plot["NO_COMP"], df_plot["TOTAL"]):
            pct = (nc / total) * 100 if total > 0 else 0
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f"{nc} - {pct:.1f}%", 
                    ha='left', va='center', fontsize=9, color="black", fontweight="bold")
        ax.set_xlabel("Alumnos No Competentes")
        st.pyplot(fig)

    if opcion == "No Competentes":
        st.subheader("📉 Top 15 Docentes y Módulos con Mayor Porcentaje de No Competencia")
        semana_seleccionada = st.selectbox("📅 Selecciona una semana", sorted(df["Semana"].unique()))
        plantel_seleccionado = st.selectbox("🏫 Selecciona un plantel", sorted(df["Plantel"].unique())) if st.session_state.administrador else st.session_state.plantel_usuario
        df_filtrado = df.filter((df["Semana"] == semana_seleccionada) & (df["Plantel"] == plantel_seleccionado))

        # Procesamiento de Docentes (sin filtro de porcentaje mínimo)
        docentes = df_filtrado.group_by("DOCENTE").agg(
            pl.sum("NO COMPETENTES").alias("NO_COMP"),
            pl.sum("TOTAL ALUMNOS").alias("TOTAL")
        ).with_columns((pl.col("NO_COMP") / pl.col("TOTAL") * 100).alias("PORCENTAJE"))
        docentes = docentes.sort("PORCENTAJE", descending=True).head(20)

        # Procesamiento de Módulos (sin filtro de porcentaje mínimo)
        modulos = df_filtrado.group_by("MODULO").agg(
            pl.sum("NO COMPETENTES").alias("NO_COMP"),
            pl.sum("TOTAL ALUMNOS").alias("TOTAL")
        ).with_columns((pl.col("NO_COMP") / pl.col("TOTAL") * 100).alias("PORCENTAJE"))
        modulos = modulos.sort("PORCENTAJE", descending=True).head(20)

        # Gráfica de Docentes
        st.markdown("### 👨‍🏫 Top 15 Docentes con Mayor Porcentaje de No Competencia")
        if not docentes.is_empty():
           graficar_barras(docentes, "DOCENTE")
        else:
            st.info("No hay docentes en el top 15 de no competencia.")

        # Gráfica de Módulos
        st.markdown("### 📚 Top 15 Módulos con Mayor Porcentaje de No Competencia")
        if not modulos.is_empty():
            graficar_barras(modulos, "MODULO")
        else:
            st.info("No hay módulos en el top 15 de no competencia.")

    elif opcion == "Comportamiento Semanal de Docentes":
        st.subheader("📈 Evolución Semanal del Desempeño Docente")
        plantel_seleccionado = st.selectbox("🏫 Selecciona un plantel", sorted(df["Plantel"].unique())) if st.session_state.administrador else st.session_state.plantel_usuario
        docentes = df.filter(df["Plantel"] == plantel_seleccionado)["DOCENTE"].unique().to_list()
        docente_seleccionado = st.selectbox("👨‍🏫 Selecciona un docente", sorted(docentes))

        df_docente = df.filter((df["Plantel"] == plantel_seleccionado) & (df["DOCENTE"] == docente_seleccionado))
        df_agrupado = df_docente.group_by("Semana").agg(
            pl.sum("NO COMPETENTES").alias("NC"),
            pl.sum("TOTAL ALUMNOS").alias("TA")
        ).sort("Semana")

        semanas = df_agrupado["Semana"]
        nc = df_agrupado["NC"]
        ta = df_agrupado["TA"]
        porcentajes = [f"{(n / t * 100):.1f}%" if t > 0 else "0%" for n, t in zip(nc, ta)]

        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(semanas, nc, color="orange", edgecolor="black")
        for i, bar in enumerate(bars):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{nc[i]} - {porcentajes[i]}", ha='center', va='bottom')
        st.pyplot(fig)

        st.markdown("### 📘 Módulos asignados al docente")
        df_modulos = df_docente.select(["MODULO"]).unique()
        st.dataframe(df_modulos.to_pandas(), use_container_width=True)

    elif opcion == "Módulos Críticos y Recomendaciones":
        st.subheader("🚩 Módulos Críticos por Semana y Docente")
        plantel_seleccionado = st.selectbox("🏫 Selecciona un plantel", sorted(df["Plantel"].unique())) if st.session_state.administrador else st.session_state.plantel_usuario
        df_plantel = df.filter(pl.col("Plantel") == plantel_seleccionado)

        modulos_criticos = df_plantel.group_by(["Semana", "MODULO", "DOCENTE"]).agg(
            pl.sum("NO COMPETENTES").alias("NO_COMP"),
            pl.sum("TOTAL ALUMNOS").alias("TOTAL")
        ).with_columns((pl.col("NO_COMP") / pl.col("TOTAL") * 100).alias("PORCENTAJE"))
        modulos_criticos = modulos_criticos.filter(pl.col("PORCENTAJE") >= 20).sort(["Semana", "PORCENTAJE"], descending=True)

        if not modulos_criticos.is_empty():
            st.dataframe(modulos_criticos.to_pandas(), use_container_width=True)
            def to_excel(df_pandas):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    df_pandas.to_excel(writer, index=False)
                return output.getvalue()
            excel_data = to_excel(modulos_criticos.to_pandas())
            st.download_button(
                label="📥 Descargar reporte de módulos críticos",
                data=excel_data,
                file_name="modulos_criticos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No hay módulos críticos en el plantel seleccionado.")
