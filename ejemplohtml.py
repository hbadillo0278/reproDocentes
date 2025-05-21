from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd

app = Flask(__name__)
app.secret_key = 'clave_secreta'  # Cambiar en producción

# Cargar datos de Excel
def cargar_datos():
    archivo = "datos.xlsx"
    df_planteles = pd.read_excel(archivo, sheet_name="Planteles")
    df_datos = pd.read_excel(archivo, sheet_name="Datos")
    return df_planteles, df_datos

# Página de inicio de sesión
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        contrasena = request.form["contrasena"]

        df_planteles, _ = cargar_datos()
        credenciales = df_planteles.set_index("Usuario")["Contrasena"].to_dict()

        if usuario in credenciales and credenciales[usuario] == contrasena:
            session["usuario"] = usuario
            session["plantel"] = df_planteles[df_planteles["Usuario"] == usuario]["Planteles"].values[0]
            return redirect(url_for("dashboard"))

        return "Credenciales incorrectas"

    return render_template("login.html")

# Página protegida con datos filtrados
@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))

    _, df_datos = cargar_datos()
    plantel_usuario = session["plantel"]
    datos_filtrados = df_datos[df_datos["Planteles"] == plantel_usuario]

    return render_template("dashboard.html", datos=datos_filtrados.to_dict(orient="records"))

# Cerrar sesión
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)