from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client

import json

app = Flask(__name__)

# Configuración de la base de datos SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///metapython.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Modelo de la tabla log
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_y_hora = db.Column(db.DateTime, default=datetime.now())
    texto = db.Column(db.TEXT)


# Crear la tabla si no existe
with app.app_context():
    db.create_all()


# Función para ordenar los registros por fecha y hora
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora, reverse=True)


@app.route("/")
def index():
    # Visualición de todos los registros de la base de datos
    registros = Log.query.all()
    registros_ordenados = ordenar_por_fecha_y_hora(registros)
    return render_template("index.html", registros=registros_ordenados)


mensajes_log = []


# Función para agregar mensajes y guardar en la base de datos
def agregar_mensajes_log(texto):
    mensajes_log.append(texto)

    # Guardar en la base de datos
    texto_str = json.dumps(texto, ensure_ascii=False)

    nuevo_registro = Log(texto=texto_str)
    db.session.add(nuevo_registro)
    db.session.commit()


# Token de verificación para la configuración
TOKEN_COMTEX = "E6FDFEF7"


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        challenge = verificar_token(request)
        return challenge
    elif request.method == "POST":
        response = recibir_mensajes(request)
        return response


def verificar_token(req):
    token = req.args.get("hub.verify_token")
    challenge = req.args.get("hub.challenge")

    if challenge and token == TOKEN_COMTEX:
        return challenge
    else:
        return jsonify({"error": "Token Inválido"}), 401


def recibir_mensajes(req):
    try:
        req = request.get_json()
        entry = req["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        objeto_mensaje = value["messages"]

        if objeto_mensaje:
            messages = objeto_mensaje[0]

            if "type" in messages:
                tipo = messages["type"]

                agregar_mensajes_log(json.dumps(messages))

                if tipo == "interactive":
                    tipo_interactivo = messages["interactive"]["type"]

                    if tipo_interactivo == "button_reply":
                        text = messages["interactive"]["button_reply"]["id"]
                        numero = messages["from"]

                        enviar_mensajes_whatsapp(text, numero)

                    elif tipo_interactivo == "list_reply":
                        text = messages["interactive"]["list_reply"]["id"]
                        numero = messages["from"]

                        enviar_mensajes_whatsapp(text, numero)

                if "text" in messages:
                    text = messages["text"]["body"]
                    numero = messages["from"]

                    enviar_mensajes_whatsapp(text, numero)
                    agregar_mensajes_log(json.dumps(messages))

        return jsonify({"message": "EVENT_RECEIVED"})
    except Exception as e:
        return jsonify({"message": "EVENT_RECEIVED"})


def enviar_mensajes_whatsapp(texto, number):
    texto = texto.lower()

    if "hola" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "👋 ¡Hola, bienvenido a RIOSOFT369! 🎟️\nPara comenzar con tu compra de boletos, digita tu número de cédula:",
            },
        }
    elif "1" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Mand uno",
            },
        }
    elif "2" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "location",
            "location": {
                "latitude": "45.201418726664606",
                "longitude": "9.149926783187368",
                "name": "Moza Racing",
                "address": "Viale Brambilla, 98, 27100 Pavia PV, Italia",
            },
        }
    elif "3" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": "https://www.turnerlibros.com/wp-content/uploads/2021/02/ejemplo.pdf",
                "caption": "Temario del Curso #001",
            },
        }
    elif "4" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "audio",
            "audio": {"link": "https://filesamples.com/samples/audio/mp3/sample1.mp3"},
        }
    elif "5" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": number,
            "text": {
                "preview_url": True,
                "body": "Introduccion al curso! https://youtu.be/6ULOE2tGlBM",
            },
        }
    elif "6" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🤝 En breve me pondre en contacto contigo. 🤓",
            },
        }
    elif "7" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "📅 Horario de Atención : Lunes a Viernes. \n🕜 Horario : 9:00 am a 5:00 pm 🤓",
            },
        }
    elif "0" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 Hola, visita mi web anderson-bastidas.com para más información.\n \n📌Por favor, ingresa un número #️⃣ para recibir información.\n \n1️⃣. Información del Curso. ❔\n2️⃣. Ubicación del local. 📍\n3️⃣. Enviar temario en PDF. 📄\n4️⃣. Audio explicando curso. 🎧\n5️⃣. Video de Introducción. ⏯️\n6️⃣. Hablar con AnderCode. 🙋‍♂️\n7️⃣. Horario de Atención. 🕜 \n0️⃣. Regresar al Menú. 🕜",
            },
        }
    elif "boton" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": "¿Confirmas tu registro?"},
                "footer": {"text": "Selecciona una de las opciones"},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "btnsi", "title": "Si"}},
                        {"type": "reply", "reply": {"id": "btnno", "title": "No"}},
                        {
                            "type": "reply",
                            "reply": {"id": "btntalvez", "title": "Tal Vez"},
                        },
                    ]
                },
            },
        }
    elif "btnsi" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {"preview_url": False, "body": "Muchas Gracias por Aceptar."},
        }
    elif "btnno" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {"preview_url": False, "body": "Es una Lastima."},
        }
    elif "btntalvez" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {"preview_url": False, "body": "Estare a la espera."},
        }
    elif "lista" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": "Selecciona Alguna Opción"},
                "footer": {
                    "text": "Selecciona una de las opciones para poder ayudarte"
                },
                "action": {
                    "button": "Ver Opciones",
                    "sections": [
                        {
                            "title": "Compra y Venta",
                            "rows": [
                                {
                                    "id": "btncompra",
                                    "title": "Comprar",
                                    "description": "Compra los mejores articulos de tecnologia",
                                },
                                {
                                    "id": "btnvender",
                                    "title": "Vender",
                                    "description": "Vende lo que ya no estes usando",
                                },
                            ],
                        },
                        {
                            "title": "Distribución y Entrega",
                            "rows": [
                                {
                                    "id": "btndireccion",
                                    "title": "Local",
                                    "description": "Puedes visitar nuestro local.",
                                },
                                {
                                    "id": "btnentrega",
                                    "title": "Entrega",
                                    "description": "La entrega se realiza todos los dias.",
                                },
                            ],
                        },
                    ],
                },
            },
        }
    elif "btncompra" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Los mejos articulos top en ofertas.",
            },
        }
    elif "btnvender" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {"preview_url": False, "body": "Excelente elección."},
        }
    else:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Gracias, has ingresado tu número de cédula",
            },
        }

    # Convertir el diccionario a formato Json
    data = json.dumps(data)

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer EAAOIhmqaZAB8BO2siJ2AaB8OSijFHeODqqOMgr2qIAdF1eZCou2ZCJmuy7lT47cgll9Y68AZAZCZB0d40VnqXxptnOZBg0rn9Irq11TrYkJiF7ZCLhxXv48uk79kQMatT8TWDNYEKVTCuPPFVg6yITHXWhZAnt2ZBTWoaiZCFZCxqqLlpkOg32naOhiMV53yGtPxoWZCnFQZDZD",
    }

    connection = http.client.HTTPSConnection("graph.facebook.com")

    try:
        connection.request("POST", "/v22.0/577915962078810/messages", data, headers)
        response = connection.getresponse()
        print("--->" + response.status, response.reason)
    except Exception as e:
        print("eee >> " + e)
        agregar_mensajes_log(json.dumps(e))
    finally:
        connection.close()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
