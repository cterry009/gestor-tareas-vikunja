from dotenv import load_dotenv
from config import os
import gkeepapi

# Cargar las variables desde el archivo .env
load_dotenv('config/.env')

# Autenticación
correo = os.getenv("GOOGLE_KEEP_EMAIL")
contrasena = os.getenv("GOOGLE_KEEP_PASSWORD")

# correo = "cpenav@unal.edu.co"
correo = "c.terry009@gmail.com"
contrasena = "Cristian91."
# contrasena = "Mauricio12"
device_id = '28ff10666e72a30b'
# device_id = 'G001NW0614660MP1'
# contrasena = 'vitx yvaj grck uexc'

print(correo, contrasena, device_id)

# Conexión a Google Keep
keep = gkeepapi.Keep()
keep.login(correo, contrasena, device_id=device_id)
# try:
#     success = keep.login(correo, contrasena, device_id=device_id)
#     if not success:
#         print("No se pudo autenticar.")
# except Exception as e:
#     print(f"Error durante la autenticación: {e}")

# Buscar la nota específica por título
titulo_buscar = "Calendario semanal"  # Título exacto de la nota
nota_encontrada = None

# Obtiene todas las notas
notas = keep.all()


# Buscar la nota
notas = keep.all()
for nota in notas:
    if nota.title == titulo_buscar:
        nota_encontrada = nota
        break

# Procesar la nota si se encuentra
if nota_encontrada:
    print(f"Nota encontrada: {nota_encontrada.title}\n")
    
    # Si la nota es una checklist, imprimir los elementos
    if nota_encontrada.isList:
        print("Elementos de la checklist:")
        for item in nota_encontrada.items:
            estado = "✔" if item.checked else "❌"
            print(f"{estado} {item.text}")
    else:
        # Si no es una checklist, mostrar el contenido
        print(f"Contenido de la nota: {nota_encontrada.text}")
else:
    print(f"No se encontró ninguna nota con el título '{titulo_buscar}'")

# # Filtra solo las notas que son "checklists" o tienen etiquetas específicas
# tareas = []
# for nota in notas:
#     if nota.labels and 'tarea' in [label.name for label in nota.labels]:
#         # Si la nota tiene la etiqueta "tarea"
#         tareas.append({
#             'nombre': nota.title,
#             'contenido': nota.text,
#             'completada': nota.checked
#         })
#     elif nota.isList:
#         # Si es una lista tipo "checklist"
#         tareas.append({
#             'nombre': nota.title,
#             'contenido': [item.text for item in nota.items],
#             'completada': all(item.checked for item in nota.items)
#         })

# # Imprime las tareas encontradas
# for tarea in tareas:
#     print(f"Tarea: {tarea['nombre']}, Completada: {tarea['completada']}")

# --------------------------------------------------------------------------------------------
# import sys
# import keyring
# import getpass
# import logging
# import gkeepapi

# USERNAME = "cpenav@unal.edu.co"


# # Set up logging
# logger = logging.getLogger("gkeepapi")
# logger.setLevel(logging.INFO)
# ch = logging.StreamHandler(sys.stdout)
# formatter = logging.Formatter("[%(levelname)s] %(message)s")
# ch.setFormatter(formatter)
# logger.addHandler(ch)

# # Initialize the client
# keep = gkeepapi.Keep()

# token = keyring.get_password("google-keep-token", USERNAME)
# store_token = False

# if not token:
#     token = getpass.getpass("Master token: ")
#     store_token = True

# # Authenticate using a master token
# logger.info("Authenticating")
# try:
#     keep.authenticate(USERNAME, token, sync=False)
#     logger.info("Success")
# except gkeepapi.exception.LoginException:
#     logger.erWror("Failed to authenticate")
#     sys.exit(1)

# if store_token:
#     keyring.set_password("google-keep-token", USERNAME, token)

# # Sync state down
# keep.sync()