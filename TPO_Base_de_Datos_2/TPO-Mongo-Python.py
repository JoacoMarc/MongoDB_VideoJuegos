#!/usr/bin/env python3
import os
import sys
from flask import Flask, jsonify, request, abort
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from dotenv import load_dotenv

# 1. Carga variables de entorno (.env)
load_dotenv()

print("DEBUG MONGO_URI:", os.getenv("MONGO_URI"))
print("DEBUG DB_NAME: ", os.getenv("DB_NAME"))
print("DEBUG COLL_NAME:", os.getenv("COLL_NAME"))


def obtener_cliente_mongo(uri: str) -> MongoClient:
    try:
        cliente = MongoClient(
            uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            directConnection=True
        )
        cliente.admin.command('ping')
        print(" Conexión exitosa a MongoDB")
        return cliente
    except (ConnectionFailure, ConfigurationError) as e:
        print(f" Error conectando a MongoDB: {e}", file=sys.stderr)
        sys.exit(1)

# 3. Lee URL y nombres de colección de las variables de entorno
MONGO_URI        = os.getenv("MONGO_URI")
NOMBRE_DB        = os.getenv("DB_NAME", "Videojuegos")
NOMBRE_COLECCION = os.getenv("COLL_NAME", "Videojuegos")

# 4. Crea la app de Flask
app = Flask(__name__)

# 5. Inicializa el cliente y la colección 
cliente   = obtener_cliente_mongo(MONGO_URI)
db        = cliente[NOMBRE_DB]
coleccion = db[NOMBRE_COLECCION]

# 6. Ruta para listar juegos con paginación
@app.route("/api/juegos", methods=["GET"])
def listar_juegos():
    # Parámetros opcionales ?page=1&per_page=50
    page     = max(int(request.args.get("page", 1)), 1)
    per_page = max(min(int(request.args.get("per_page", 50)), 100), 1)
    skip     = (page - 1) * per_page

    total = coleccion.count_documents({})
    datos = list(
        coleccion
        .find({}, {"_id": 0})
        .skip(skip)
        .limit(per_page)
    )

    return jsonify({
        "page":     page,
        "per_page": per_page,
        "total":    total,
        "data":     datos
    })

# 7. Ruta para obtener un juego por su título
@app.route("/api/juegos/<string:titulo>", methods=["GET"])
def juego_por_titulo(titulo):
    juego = coleccion.find_one({"titulo": titulo}, {"_id": 0})
    if not juego:
        abort(404, "Juego no encontrado")
    return jsonify(juego)

# 8. Manejadores de error
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": e.description}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Error interno"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)

