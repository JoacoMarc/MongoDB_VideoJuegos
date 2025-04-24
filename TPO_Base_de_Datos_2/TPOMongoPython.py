
import os
import sys
import csv
from io import StringIO
from flask import Flask, jsonify, request, abort, Response
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from dotenv import load_dotenv

#  Carga variables de entorno (.env)
load_dotenv()

#  Debug de variables cargadas
print("DEBUG MONGO_URI:", os.getenv("MONGO_URI"))
print("DEBUG DB_NAME: ", os.getenv("DB_NAME"))
print("DEBUG COLL_NAME:", os.getenv("COLL_NAME"))

# Función para obtener cliente Mongo
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

# Leer configuración desde entorno
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME   = os.getenv("DB_NAME", "Videojuegos")
COLL_NAME = os.getenv("COLL_NAME", "Videojuegos")

# Crear app Flask 
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Inicializar cliente y colección
cliente   = obtener_cliente_mongo(MONGO_URI)
db        = cliente[DB_NAME]
coleccion = db[COLL_NAME]

#  Endpoint JSON: Listado de juegos 
@app.route("/api/juegos", methods=["GET"])
def listar_juegos():
    page     = max(int(request.args.get("page", 1)), 1)
    per_page = max(min(int(request.args.get("per_page", 50)), 100), 1)
    skip     = (page - 1) * per_page

    total = coleccion.count_documents({})
    data = list(
        coleccion.find({}, {"_id": 0})
                  .skip(skip)
                  .limit(per_page)
    )
    return jsonify({
        "page": page,
        "per_page": per_page,
        "total": total,
        "data": data
    })

#  Endpoint JSON: Juego por título
@app.route("/api/juegos/<string:titulo>", methods=["GET"])
def juego_por_titulo(titulo):
    juego = coleccion.find_one({"titulo": titulo}, {"_id": 0})
    if not juego:
        abort(404, "Juego no encontrado")
    return jsonify(juego)

# Funcion opcional para exportar en CSV
@app.route("/api/juegos.csv", methods=["GET"])
def exportar_csv():
    si   = StringIO()
    cols = [
        "titulo",
        "desarrollador",
        "descripcion",
        "anio_de_lanzamiento",
        "calificacion",
        "plataformas",
        "genero"
    ]
    writer = csv.DictWriter(si, fieldnames=cols)
    writer.writeheader()

    for j in coleccion.find({}, {"_id": 0}):
        writer.writerow({
            "titulo":               j.get("titulo", ""),
            "desarrollador":        j.get("desarrollador", ""),
            "descripcion":          j.get("descripcion", ""),
            "anio_de_lanzamiento":  j.get("anio_de_lanzamiento", ""),
            "calificacion":         j.get("calificacion", ""),
            # Convertimos los arrays en strings separados por “;”
            "plataformas":          ";".join(j.get("plataformas", [])),
            "genero":               ";".join(j.get("genero", [])),
        })

    return Response(si.getvalue(), mimetype="text/csv")


# Manejadores de error
@app.errorhandler(404)
def handle_404(error):
    return jsonify({"error": error.description}), 404

@app.errorhandler(500)
def handle_500(error):
    return jsonify({"error": "Error interno"}), 500

#  Ejecutar servidor
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
