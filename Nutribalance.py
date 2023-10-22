# Importar librerias
import pandas as pd
import streamlit as st
import streamlit_extras
import streamlit_authenticator as stauth
import re
from deta import Deta
from datetime import time

# Almacenamos la key de la base de datos en una constante
DETA_KEY = "e0qgr2zg4tq_mbZWcCg7iGCpWFBbCy3GGFjEYHdFmZYR"

# Creamos nuestro objeto deta para hacer la conexion a la DB
deta = Deta(DETA_KEY)

# Realizamos la conexion a la DB
db = deta.Base("NutribalanceUsers")

# Funcion para registrar usuarios en la DB
def insertar_usuario(email, username, age, height, password):
    """Agrega usuarios a la Base de Datos"""
    return db.put({"key":email, "username": username, "age":age, "height":height, "password":password})

# Funcion que retorna los usuarios registrados
def fetch_usuarios():
    """Regresa un diccionario con los usuarios registrados"""
    # guardamos los datos de la DB en users y retornamos su contenido
    users = db.fetch()
    return users.items

# Funcion que retorna los emails de los usuarios registrados
def get_emails_usuarios():
    """Regresa una lista con los emails de cada usuario"""
    # guardamos los datos de la DB en users
    users = db.fetch()
    emails = []
    # filtramos los emails de la DB
    for user in users.items:
        emails.append(user["key"])
    return emails

# Funcion que retorna los nombres de usuario de los usuarios registrados
def get_usernames_usuarios():
    """Regresa una lista con los username de cada usuario"""
    # guardamos los datos de la DB en users
    users = db.fetch()
    usernames = []
    # filtramos los usernames de la DB
    for user in users.items:
        usernames.append(user["username"])
    return usernames

# Funcion que verifica si un email ingresado es valido
def validar_email(email):
    """Retorna True si el email ingresado es valido, de lo contrario retorna False"""
    # Patrones tipicos de un email valido
    pattern = "^[a-zA-Z0_9-_]+@[a-zA-Z0_9-_]+\.[a-z]{1,3}$"
    pattern1 = "^[a-zA-Z0_9-_]+@[a-zA-Z0_9-_]+\.[a-z]{1,3}+\.[a-z]{1,3}$"

    # Verifica si el email ingresado coincide con algun patron definido
    if re.match(pattern, email) or re.match(pattern1, email):
        return True
    return False

# Funcion que verifica si un username ingresado es valido
def validar_username(username):
    """Retorna True si el username es valido, de lo contrario, retorna False"""
    # Se define el patron de un username tipico
    pattern = "^[a-zA-Z0-9]*$"
    # Se verifica si el username ingresado coincide con el patron tipico
    if re.match(pattern, username):
        return True
    return False

# Titulo en la pagina
st.title("Nutribalance")

# Manejo de posibles errores
try:
    # Se almacenan los datos necesarios de la DB
    users = fetch_usuarios()
    emails = get_emails_usuarios()
    usernames = get_usernames_usuarios()
    passwords = [user["password"] for user in users]

    # Se crea el diccionario credentials necesario para el funcionamiento del autenticador de cuentas
    credentials = {"usernames" : {}}
    for index in range(len(emails)):
        credentials["usernames"][usernames[index]] = {"name" : emails[index], "password" : passwords[index]}

    # Creacion del autenticador
    Authenticator = stauth.Authenticate(credentials, cookie_name="Streamlit", key="cookiekey", cookie_expiry_days=3)

    # Crear boton de Cerrar sesion si la sesion fue iniciada
    if st.session_state["authentication_status"]:
        Authenticator.logout("Cerrar sesion", location="sidebar")

# Informar de que hubo una excepcion en caso de que la haya
except:
    st.error("Excepcion lanzada")

# Crear pie de pagina con los datos de contacto de los creadores
footer = """
<style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        z-index: 10;
        width: 100%;
        background-color: rgb(14, 17, 23);
        color: black;
        text-align: center;
    }
    .footer p {
        color: white;
    }
</style>
<div class="footer">
    <p>App desarrollada por: <br />
    Luis Fernando López Echeverri | Andres Felipe Ramirez Suarez <br />
    Contactenos: <a href="#">lulopeze@unal.edu.co</a> | <a href="#">aramirezsu@unal.edu.co</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)

# Función para calcular el IMC
def calcular_imc(peso, altura):
    try:
        # Convertir la altura de cm a metros
        altura_metros = altura / 100
        imc = peso / (altura_metros ** 2)
        return imc
    except ZeroDivisionError:
        return "La altura no puede ser cero."

# Calcular las calorías necesarias diarias
def calcular_calorias_diarias(sexo, peso, altura, edad, nivel_actividad):
    calorias_diarias = 0  # Inicializar la variable con un valor predeterminado

    if sexo == "Masculino":
        tmb = 88.362 + (13.397 * peso) + (4.799 * altura) - (5.677 * edad)
    elif sexo == "Femenino":
        tmb = 447.593 + (9.247 * peso) + (3.098 * altura) - (4.330 * edad)

    if nivel_actividad == "Sedentario":
        calorias_diarias = tmb * 1.2
    elif nivel_actividad == "Ligera actividad":
        calorias_diarias = tmb * 1.375
    elif nivel_actividad == "Moderada actividad":
        calorias_diarias = tmb * 1.55
    elif nivel_actividad == "Alta actividad":
        calorias_diarias = tmb * 1.725
    elif nivel_actividad == "Muy alta actividad":
        calorias_diarias = tmb * 1.9

    return calorias_diarias

# Función para determinar la categoría de IMC
def determinar_categoria(imc):
    if imc < 18.5:
        return "Bajo peso"
    elif 18.5 <= imc < 24.9:
        return "Peso normal"
    elif 24.9 <= imc < 29.9:
        return "Sobrepeso"
    else:
        return "Obesidad"

# Función para calcular horas de sueño
def calcular_horas_de_sueno(hora_sueno, hora_despertar):
    # Obtener las horas de sueño y despertar
    hora_sueno_horas = hora_sueno.hour
    hora_despertar_horas = hora_despertar.hour

    # Calcular la diferencia de horas
    horas_sueno = hora_despertar_horas - hora_sueno_horas

    # Manejar el caso en el que la hora de despertar,
    # sea anterior a la hora de dormir (cruce de medianoche)
    if horas_sueno < 0:
        horas_sueno += 24

    return horas_sueno

# Solicitar al usuario ingresar peso y altura
peso = st.number_input("Ingresa tu peso en kilogramos", min_value=0.1)
altura = st.number_input("Ingresa tu altura en centímetros, "
                         "Sin puntos ni comas", step=1)
edad = st.number_input (" Ingrese su edad", step=1)

# Agregar un menú desplegable para seleccionar el sexo
sexo = st.selectbox("Selecciona tu sexo:", ["Masculino", "Femenino"])

# Solicitar al usuario hora de sueño y hora de despertar
hora_sueno = st.time_input("Ingresa la hora en que te dormiste")
hora_despertar = st.time_input("Ingresa la hora en que te despertaste")

# Agregar un menú desplegable para seleccionar el nivel de actividad física
nivel_actividad = st.selectbox("Selecciona tu nivel de actividad física:", [
    "Sedentario",
    "Ligera actividad",
    "Moderada actividad",
    "Alta actividad",
    "Muy alta actividad"
])

# Verificar si el usuario ha ingresado valores válidos
if peso > 0 and altura > 0:
    # Calcular el IMC
    altura_metros = altura / 100
    imc = peso / (altura_metros ** 2)

    # Determinar la categoría de IMC basada en el sexo
    if sexo == "Masculino":
        if isinstance(imc, str):
            st.write(imc)
        else:
            if imc < 18.5:
                categoria = "Bajo peso"
            elif 18.5 <= imc < 24.9:
                categoria = "Peso normal"
            elif 24.9 <= imc < 29.9:
                categoria = "Sobrepeso"
            else:
                categoria = "Obesidad"
            st.write(f"Tu IMC es {imc:.2f}, lo que corresponde a la categoría de "
         f"{categoria} para hombres.")


    elif sexo == "Femenino":
        if isinstance(imc, str):
            st.write(imc)
        else:
            if imc < 18.5:
                categoria = "Bajo peso"
            elif 18.5 <= imc < 24.9:
                categoria = "Peso normal"
            elif 24.9 <= imc < 29.9:
                categoria = "Sobrepeso"
            else:
                categoria = "Obesidad"
            st.write(f"Tu IMC es {imc:.2f}, lo que corresponde a la categoría de "
         f"{categoria} para mujeres.")
else:
    st.write("Por favor, ingresa valores válidos para peso y altura.")

objetivo = st.selectbox("Selecciona tu objetivo:",
                       ["Aumentar masa muscular", "Mantenerse", "Bajar grasa"])

# Crear un botón para realizar el cálculo
st.button("CALCULAR")

# Mostrar y calcular tiempo de sueño
horas_sueno = calcular_horas_de_sueno(hora_sueno, hora_despertar)

# Mostrar las horas de sueño
st.write(f"Dormiste durante {horas_sueno} horas")

# Llamada a la función y almacenar el resultado
calorias_diarias = calcular_calorias_diarias(sexo, peso, altura, edad, nivel_actividad)

# Mostrar el resultado
st.write(f"Calorías necesarias en un día: {int(calorias_diarias)} calorías")

# Mostrar las horas de sueño
st.write(f"Dormiste durante {horas_sueno} horas")

# Llamada a la función y almacenar el resultado
calorias_diarias = calcular_calorias_diarias(sexo, peso, altura, edad, nivel_actividad)

# Mostrar el resultado
st.write(f"Calorías necesarias en un día: {int(calorias_diarias)} calorías")

# Lectura de datos
url_foods = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vSOahgzh7JD0eqEEOE5DdXPqJci2D7ZH16nb8Ski1OcZkR448sOMPRE"
    "LuLLEG4EiNuNhWz5DpaAHf8E/pub?output=csv"
)

url_exercise = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTXXom0c0qWSJIPrIQZo_0qGxSzoM0u_xe8Cijv1ZAY"
    "bP6EKshVAtvwVV2eh5Yj1Ueio8tzb7FEsV5j/pub?output=csv"
)

# Cargar el DataFrame desde la URL
df_foods_base = pd.read_csv(url_foods)
df_exercise=pd.read_csv(url_exercise)

# Eliminar comas y convertir a enteros en el DataFrame food
columns_to_clean = ["Calories"]

for column in columns_to_clean:
    df_foods_base[column] = df_foods_base[column]\
        .str.replace(' cal', '', regex=True)
    df_foods_base[column] = df_foods_base[column].astype(int)
=======
    df_foods[column] = df_foods[column]\
        .str.replace(' cal', '', regex=True)
    df_foods[column] = df_foods[column].astype(int)

# Convertir a enteros en el DataFrame food
columnas_to_clean = ["130 lb", "155 lb", "180 lb", "205 lb"]

for elements in columnas_to_clean:
    df_exercise[elements] = df_exercise[elements].astype(int)

# Configuración de la aplicación Streamlit
st.title("Registro de Alimentos Consumidos en el Día")

# Seleccionar posibles alergias o disgustos de algun alimento
alergias_seleccionadas = st.multiselect(
    "Selecciona los alimentos que no desea incluir:",
    df_foods_base["Food"]
)


# Inicializa una variable para realizar el seguimiento del total de calorías
total_calorias_consumidas = 0

# Guardamos inicialmente todos los alimentos en df_foods
df_foods = df_foods_base

# Ocultar del dataframe los elementos seleccionados
for alergia in alergias_seleccionadas:
    df_foods = df_foods[df_foods["Food"] != alergia]

st.write("### Lista de Alimentos:")
st.write(df_foods)

# Variable para la selecion de varias comidas
alimentos_seleccionados = st.multiselect(
    "Selecciona los alimentos que has consumido:",
    df_foods["Food"]
)

# Obtener los detalles de los alimentos seleccionados
for alimento_seleccionado in alimentos_seleccionados:
    detalles_alimento = df_foods[df_foods["Food"] == alimento_seleccionado]
    if not detalles_alimento.empty:
        st.write(f"### Detalles del Alimento Seleccionado ({alimento_seleccionado}):")
        calorias_alimento = detalles_alimento["Calories"].values[0]
        total_calorias_consumidas += calorias_alimento
        st.write(detalles_alimento)

=======
# Inicializa una variable para realizar el seguimiento del total de calorías
total_calorias_consumidas = 0

# Obtener los detalles de los alimentos seleccionados
for alimento_seleccionado in alimentos_seleccionados:
    detalles_alimento = df_foods[df_foods["Food"] == alimento_seleccionado]
    if not detalles_alimento.empty:
        st.write(f"### Detalles del Alimento Seleccionado ({alimento_seleccionado}):")
        calorias_alimento = detalles_alimento["Calories"].values[0]
        total_calorias_consumidas += calorias_alimento
        st.write(detalles_alimento)

    else:
        st.write(f"Selecciona un alimento de la lista o verifica la ortografía.")

# Mostrar el total de calorías
st.write(f"Total de calorías consumidas: {total_calorias_consumidas} calorías")

# Mostrar el dataframe
st.write("### Lista de ejercicios por hora:")
st.write(df_exercise)

# Elemento interactivo para que el usuario seleccione alimentos
ejercicio_seleccionado = st.selectbox(
    "Selecciona un ejercicio:",
    df_exercise["Activity, Exercise or Sport (1 hour)"]
)

# Obtener los detalles del alimento seleccionado
detalles_ejercicio = df_exercise[
    df_exercise["Activity, Exercise or Sport (1 hour)"] == ejercicio_seleccionado
]

if not detalles_ejercicio.empty:
    st.write("### Detalles del Ejercicio Seleccionado:")
    st.write(detalles_ejercicio)
else:
    st.write("Selecciona un ejercicio de la lista.")

# Inicializa una variable para realizar,
# el seguimiento del total de calorías quemadas
total_calorias_quemadas = 0

# Variable que almacena varios ejercicios
ejercicios_seleccionados = st.multiselect(
    "Selecciona los ejercicios que has realizado:",
    df_exercise["Activity, Exercise or Sport (1 hour)"]
)

# Obtener los detalles de los ejercicios seleccionados y sumar las calorías
for ejercicio_seleccionado in ejercicios_seleccionados:
    detalles_ejercicio = df_exercise[df_exercise["Activity, Exercise or Sport (1 hour)"] == ejercicio_seleccionado]

    if not detalles_ejercicio.empty and "130 lb" in detalles_ejercicio.columns:
        calorias_ejercicio = detalles_ejercicio["130 lb"].values[0]
        total_calorias_quemadas += calorias_ejercicio
        st.write(f"Detalles del Ejercicio Seleccionado ({ejercicio_seleccionado}):")
        st.write(detalles_ejercicio)
        st.write(f"Calorías quemadas:{calorias_ejercicio}")

# Mostrar el total de calorías quemadas
st.write(f"Total de calorías quemadas: {total_calorias_quemadas}")

# Almacenamiento de los datos de los pasos
st.write("### Pasos del dia: ")

# Variable para mostrar diferencia de calorias en base a consumidas - gastadas
def mostrar_diferencia_calorias(total_calorias_consumidas, total_calorias_quemadas, calorias_diarias):
    diferencia_calorias = calorias_diarias - (total_calorias_consumidas - total_calorias_quemadas)
    if diferencia_calorias > 0:
        st.write(f"Has consumido {int(diferencia_calorias)} calorías en exceso hoy. Considera ajustar tu ingesta calórica.")
    elif diferencia_calorias < 0:
        st.write(f"Te faltan {int(abs(diferencia_calorias))} calorías para alcanzar tu ingesta calórica diaria. ¡Asegúrate de comer lo suficiente!")

st.write("### Calculadora de Calorías: ")
# Llamar a la función con los valores adecuados
mostrar_diferencia_calorias(calorias_diarias, total_calorias_quemadas, total_calorias_consumidas)
