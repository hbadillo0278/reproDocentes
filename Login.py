import streamlit as st
import polars as pl

# Convertir Excel a Parquet para mejorar rendimiento
def convertir_a_parquet(excel_path, sheet_name, parquet_path):
    try:
        data = pl.read_excel(excel_path, sheet_name=sheet_name)
        data.write_parquet(parquet_path)
        return data
    except Exception as e:
        st.error(f"Error al convertir {sheet_name} a Parquet: {e}")
        st.stop()

# Cargar datos en formato Parquet
datos = convertir_a_parquet("Planteles.xlsx", "Datos", "datos.parquet")
planteles = convertir_a_parquet("Planteles.xlsx", "Planteles", "planteles.parquet")

# Validar existencia de la columna "Plantel"
if "Plantel" not in datos.columns or "Plantel" not in planteles.columns:
    st.error("Las hojas de datos deben contener la columna 'Plantel'.")
    st.stop()

# Unir datos por 'Plantel'
datos_unidos = datos.join(planteles, on="Plantel", how="inner")

# Simulación de credenciales
usuarios = {
    "admin": {"password": "1234", "plantel": "Todos"},
    "user1": {"password": "abcd", "plantel": "Plantel A"},
    "user2": {"password": "xyz", "plantel": "Plantel B"}
}

# Estado de sesión
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.usuario = ""

# Contenedor de login
login_container = st.empty()

if not st.session_state.logged_in:
    with login_container:
        st.title("Iniciar sesión")
        with st.form("login_form"):
            usuario = st.text_input("Usuario").strip()
            password = st.text_input("Contraseña", type="password").strip()
            submit_button = st.form_submit_button("Iniciar sesión")

        if submit_button:
            if usuario in usuarios:
                if usuarios[usuario]["password"] == password:
                    planteles_disponibles = datos_unidos["Plantel"].unique().to_list()
                    if usuarios[usuario]["plantel"] == "Todos" or usuarios[usuario]["plantel"] in planteles_disponibles:
                        st.session_state.logged_in = True
                        st.session_state.usuario = usuario
                        st.experimental_rerun()
                    else:
                        st.error("El plantel asignado a este usuario no existe en los datos.")
                else:
                    st.error("Contraseña incorrecta.")
            else:
                st.error("Usuario incorrecto.")

# Mostrar datos filtrados si el usuario está autenticado
if st.session_state.logged_in:
    login_container.empty()
    st.title("Información filtrada")

    plantel_usuario = usuarios[st.session_state.usuario]["plantel"]
    
    datos_filtrados = datos_unidos if plantel_usuario == "Todos" else datos_unidos.filter(pl.col("Plantel") == plantel_usuario)

    if not datos_filtrados.is_empty():
        st.write(f"Datos correspondientes a tu plantel ({plantel_usuario}):")
        st.dataframe(datos_filtrados)
    else:
        st.warning(f"No hay datos disponibles para el plantel {plantel_usuario}.")

    # Botón para cerrar sesión
    if st.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.session_state.usuario = ""
        st.experimental_rerun()
