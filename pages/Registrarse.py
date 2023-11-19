# -*- coding: utf-8 -*-
"""Registrarse.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1nHdHeaJB8xNkP2HlYZxn_RehAiHCfOM3
"""

# Importar librerias necesarias
import streamlit as st
import streamlit_extras
import streamlit_authenticator as stauth
import re
from deta import Deta

# Almacenamos la key de la base de datos en una constante
DETA_KEY = "e0qgr2zg4tq_mbZWcCg7iGCpWFBbCy3GGFjEYHdFmZYR"

# Creamos nuestro objeto deta para hacer la conexion a la DB
deta = Deta(DETA_KEY)

# Realizamos la conexion a la DB
db = deta.Base("NutribalanceUsers")

# Funcion para registrar usuarios en la DB
def insertar_usuario(email, username, age, height, password):
    """
    Agrega un nuevo usuario a la Base de Datos.

    Parameters:
    - email (str): La dirección de correo electrónico del usuario.
    - username (str): El nombre de usuario del usuario.
    - age (int): La edad del usuario.
    - height (float): La altura del usuario en centímetros.
    - password (str): La contraseña del usuario.

    Returns:
    - None: La función no devuelve un valor explícito.

    Note:
    - La función agrega un nuevo usuario a la Base de Datos con la
    información proporcionada. El nuevo usuario también tiene una lista vacía
    llamada "food" que puede contener información
    relacionada con las preferencias alimenticias del usuario en el futuro.
    """
    # Agregar un nuevo usuario a la Base de Datos con la
    # información proporcionada
    db.put({"key": email, "username": username, "age": age, "height": height,
            "password": password, "food": []})

# Funcion que retorna los usuarios registrados
def fetch_usuarios():
    """
    Obtiene un diccionario con los usuarios registrados desde la Base de Datos.

    Returns:
    - dict: Un diccionario que contiene información sobre los
    usuarios registrados. Las claves del diccionario son las
    identificaciones únicas de los usuarios.
    Los valores son diccionarios que representan
    la información detallada de cada usuario.

    """
    # Guardar los datos de la Base de Datos en 'users' y retornar su contenido
    users = db.fetch()
    return users.items

# Funcion que retorna los emails de los usuarios registrados
def get_emails_usuarios():
    """
    Obtiene una lista con los correos electrónicos de cada usuario
    registrado en la Base de Datos.

    Returns:
    - list: Una lista que contiene los correos electrónicos de cada usuario.

    """
    # Guardar los datos de la Base de Datos en 'users'
    users = db.fetch()

    # Inicializar una lista para almacenar los correos electrónicos
    emails = []

    # Filtrar los correos electrónicos del diccionario de usuarios y
    # agregarlos a la lista
    for user in users.items:
        emails.append(user["key"])

    return emails

# Funcion que retorna los nombres de usuario de los usuarios registrados
def get_usernames_usuarios():
    """
    Obtiene una lista con los nombres de usuario de cada usuario
    registrado en la Base de Datos.

    Returns:
    - list: Una lista que contiene los nombres de usuario de cada usuario.

    """
    # Guardar los datos de la Base de Datos en 'users'
    users = db.fetch()

    # Inicializar una lista para almacenar los nombres de usuario
    usernames = []

    # Filtrar los nombres de usuario del diccionario de usuarios y
    # agregarlos a la lista
    for user in users.items:
        usernames.append(user["username"])

    return usernames

# Funcion que verifica si un email ingresado es valido
def validar_email(email):
    """
    Verifica si el email ingresado es válido según patrones típicos.

    Args:
    - email (str): La dirección de correo electrónico a validar.

    Returns:
    - bool: True si el email es válido, False de lo contrario.

    """
    # Patrones típicos de un email válido
    pattern = "^[a-zA-Z0_9-_]+@[a-zA-Z0-9-_]+\.[a-z]{1,3}$"
    pattern1 = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9-_]+\.[a-z]{1,3}+\.[a-z]{1,3}$"

    # Verifica si el email ingresado coincide con alguno de los
    # patrones definidos
    if re.match(pattern, email) or re.match(pattern1, email):
        return True
    return False

def validar_username(username):
    """
    Verifica si el username ingresado es válido según un patrón típico.

    Args:
    - username (str): El nombre de usuario a validar.

    Returns:
    - bool: True si el username es válido, False de lo contrario.

    """
    # Utiliza directamente el resultado de re.match,
    # que es None si no hay coincidencia
    return bool(re.match("^[a-zA-Z0-9]*$", username))

# Formulario de registro con los datos que debe ingresar el usuario
def registro():
    """
    Formulario de registro que guarda un registro de usuario en la
    base de datos si este es válido.

    Parameters:
    None

    Returns:
    None

    """
    # Se define un checkbox en el que se deben aceptar los
    # T&C antes de enviar un registro
    st.write("Debe aceptar los términos y condiciones antes de"
         "poder enviar el formulario")
    aceptar_terminos = st.checkbox("Acepto los [Términos y Condiciones]"
    "(https://github.com/\lflunal/ppi_20/blob/Luis-Lopez/Politica%20de"
    "%20Tratamiento%20de%20Datos.md)")


    # Si se aceptan los términos y condiciones habilitar el registro
    if aceptar_terminos:
        # Creacion del formulario
        with st.form(key="registro", clear_on_submit=True):
            # Titulo del formulario
            st.subheader("Registrarse")

            # Campos a ser llenados por el usuario
            email = st.text_input("Email", placeholder="Ingrese su Email")
            username = st.text_input("Usuario",
                                    placeholder="Ingrese su nombre de usuario")
            age = st.text_input("Edad (en años)",
                                placeholder="Ingrese su edad en años")
            height = st.text_input("Altura (en cm sin puntos ni comas)",
                    placeholder="Ingrese su estatura en cm sin puntos ni comas")
            password = st.text_input("Contraseña",
                            placeholder="Ingrese su contraseña", type="password")
            # Boton de envio de datos de registro
            st.form_submit_button("Registrate")
    else:
        st.warning("Debes aceptar los términos y condiciones antes de registrarte")

        # Revisar validez de los datos ingresados por el usuario
        # y registro a la DB
        if email and username and age and height and password:
            if validar_email(email):
                if email not in get_emails_usuarios():
                    if validar_username(username):
                        if username not in get_usernames_usuarios():
                            password_encriptada = stauth.Hasher([password]) \
                      .generate()
                            insertar_usuario(email, username, age,
                                             height, password_encriptada[0])
                            st.success("Cuenta creada con exito!")
                        else:
                            st.warning("Nombre de usuario en uso")
                    else:
                        st.warning("Nombre de usuario invalido"
                        "(solo debe tener letras y numeros)")
                else:
                    st.warning("El email ya esta en uso")
            else:
                st.warning("Email invalido")
        else:
            st.warning("Debe rellenar todos los campos")

# Manejo de posibles errores
try:
    # Se almacenan los datos necesarios de la DB
    users = fetch_usuarios()
    emails = get_emails_usuarios()
    usernames = get_usernames_usuarios()
    passwords = [user["password"] for user in users]

    # Se crea el diccionario credentials necesario para el
    # funcionamiento del autenticador de cuentas
    credentials = {"usernames" : {}}
    for index in range(len(emails)):
        credentials["usernames"][usernames[index]] = {"name" : emails[index],
                                                 "password" : passwords[index]}

    # Creacion del autenticador
    Authenticator = stauth.Authenticate(credentials, cookie_name="Streamlit",
                                        key="cookiekey", cookie_expiry_days=3)

    # Crear boton de Cerrar sesion si la sesion fue iniciada
    if st.session_state["authentication_status"]:
        Authenticator.logout("Cerrar sesion", location="sidebar")
        st.write("Ya ha iniciado sesion")

    # Si la sesion no fue iniciada, ejecutar el formulario de registro
    else:
        registro()

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
</div>
"""