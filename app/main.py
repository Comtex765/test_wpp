from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import json

app = Flask(__name__)

# Configuración de la base de datos SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///metapython.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Modelo de la tabla log
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_y_hora = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc))
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
    req = request.get_json()

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

                if tipo == "interactive":
                    return 0

                if "text" in messages:
                    text = messages["text"]["body"]
                    numero = messages["from"]

                    agregar_mensajes_log(json.dumps(messages))

        return jsonify({"message": "EVENT_RECEIVED"})
    except Exception as e:
        return jsonify({"message": "EVENT_RECEIVED"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
