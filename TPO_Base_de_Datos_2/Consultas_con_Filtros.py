from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def obtener_cliente_mongo(uri: str) -> MongoClient:
    try:
        cliente = MongoClient(uri, serverSelectionTimeoutMS=5000)
        cliente.admin.command('ping')  # Confirma conexión
        print("Conexión exitosa a MongoDB")
        return cliente
    except ConnectionFailure as e:
        print(f"No se pudo conectar a MongoDB: {e}")
        raise

# Configuración principal
url_mongo = "mongodb://localhost:27017"
nombre_db = "Videojuegos"
nombre_coleccion = "Videojuegos"
# Conectar y usar la colección
cliente = obtener_cliente_mongo(url_mongo)
db = cliente[nombre_db]
coleccion = db[nombre_coleccion]
lista_dbs = cliente.list_database_names()

print(lista_dbs)

#CONSULTAS CON FILTROS
ocultar= { "_id": 0 , "plataformas":0,"calificacion":0,"desarrollador":0}

print("Juegos con genero Supervivencia: ")
print()
for documento in coleccion.find( { "genero": "Supervivencia"},ocultar):
    print(documento)

print()
print("Juegos con fecha de lanzamiento posterior a 2015: ")
print()
for documento in coleccion.find({ "anio_de_lanzamiento": { "$gt": 2015 } },ocultar):
    print (documento)

print()
print("Juegos desarrollados por Nintendo:\n")
for doc in coleccion.find({"desarrollador": "Nintendo"}, ocultar):
    print(doc)

print()
print("Juegos con calificación mayor o igual a 9.5:\n")
for doc in coleccion.find({"calificacion": { "$gte": 9.5 }}, ocultar):
    print(doc)
