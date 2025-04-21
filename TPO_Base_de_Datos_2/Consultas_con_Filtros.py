
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError

def obtener_cliente_mongo(uri: str) -> MongoClient:
    try:
        cliente = MongoClient(
            uri,
            serverSelectionTimeoutMS=5000,  
            connectTimeoutMS=5000,          
            directConnection=True           
        )
        # Ping al servidor para validar la conexión
        cliente.admin.command('ping')
        print("Conexión exitosa a MongoDB")
        return cliente
    except (ConnectionFailure, ConfigurationError) as e:
        print(f"Error conectando a MongoDB: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    
    # URI completo con usuario/clave. Asegúrate de no comprometer esta cadena.
    url_mongo = (
        "mongodb://root:yF0wB3iLa57VzZztO0ReI22GYELMkQF3Xz9kedSWJ6HYQ1d6dSDEzODNfIOei4nd"
        "@188.245.255.235:5437"
        "/?authSource=admin&directConnection=true"
    )

    nombre_db = "Videojuegos"
    nombre_coleccion = "Videojuegos"

    cliente = obtener_cliente_mongo(url_mongo)
    db = cliente[nombre_db]
    coleccion = db[nombre_coleccion]


    # Listar bases de datos disponibles
    print("Bases de datos disponibles:", cliente.list_database_names())

if __name__ == "__main__":
    main()
