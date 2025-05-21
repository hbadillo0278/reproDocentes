
import streamlit as st
import polars as pl

# Cargar hojas de Excel
datos = pl.read_excel("Datos.xlsx", sheet_name="Datos")
planteles = pl.read_excel("Datos.xlsx", sheet_name="Planteles")

# Unir las hojas por 'Plantel'
datos_unidos = datos.join(planteles, on="Plantel", how="inner")

# Simulación de credenciales (puedes cambiar esto a una base de datos)
usuarios = {
    "admin": {"password": "1234", "plantel": "Todos"},
    "user1": {"password": "abcd", "plantel": "Plantel A"},
    "user2": {"password": "xyz", "plantel": "Plantel B"}
}

# Interfaz de usuario en Streamlit
st.title("Sistema de Login y Visualización de Datos")

# Input de usuario y contraseña
usuario = st.text_input("Usuario")
password = st.text_input("Contraseña", type="password")

# Verificación de usuario
if usuario in usuarios and usuarios[usuario]["password"] == password:
    st.success(f"Bienvenido, {usuario}")

    # Filtrar datos según el plantel asignado
    if usuarios[usuario]["plantel"] == "Todos":
        datos_filtrados = datos_unidos
    else:
        datos_filtrados = datos_unidos.filter(pl.col("Plantel") == usuarios[usuario]["plantel"])

    # Mostrar tabla con los datos filtrados
    st.write("Información filtrada según el usuario:")
    st.dataframe(datos_filtrados)

else:
    st.error("Usuario o contraseña incorrectos")