import pandas as pd
import streamlit as st

# 📌 Paso 1: Cargar los datos con cache para mejorar rendimiento
@st.cache_data
def cargar_datos():
    # Cargar todas las hojas del archivo Excel
    sheets_dict = pd.read_excel("DashboardPython.xlsx", sheet_name=None)

    # Convertir todas las hojas en un solo DataFrame
    df_list = []
    for sheet_name, df in sheets_dict.items():
        df["Hoja"] = sheet_name  # Agregar el nombre de la hoja como referencia
        df_list.append(df)

    return pd.concat(df_list, ignore_index=True)

df = cargar_datos()

# 📌 Paso 2: Obtener lista única de planteles
planteles = df["Plantel"].dropna().unique()

# 📌 Paso 3: Crear el filtro interactivo en Streamlit
st.title("Dashboard de Datos Actualizados")
plantel_seleccionado = st.selectbox("Selecciona un plantel:", planteles)

# Filtrar los datos según la selección
df_filtrado = df[df["Plantel"] == plantel_seleccionado]

# 📌 Paso 4: Mostrar los datos filtrados en una tabla interactiva
st.write(f"Datos para el plantel: **{plantel_seleccionado}**")
st.dataframe(df_filtrado)

# 📌 Paso 5: Agregar gráficos dinámicos (Ejemplo con cantidad de alumnos por grado)
if "Grado" in df_filtrado.columns and "Cantidad" in df_filtrado.columns:
    st.bar_chart(df_filtrado.groupby("Grado")["Cantidad"].sum())

# 📌 Paso 6: Instrucciones para actualizar datos periódicamente
st.write("🔄 Para actualizar los datos, asegúrate de que el archivo Excel se modifique y recarga la página.")

# 📌 Paso 7: Guardar datos si se requiere exportar
if st.button("Descargar datos filtrados"):
    df_filtrado.to_excel("datos_filtrados.xlsx", index=False)
    st.success("Archivo listo para descargar.")