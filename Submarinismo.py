import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
import getpass
import pymongo
from pymongo import MongoClient

# Obtener el nombre de usuario del sistema operativo
#usuario_actual = getpass.getuser()
#if usuario_actual != "Felip":
#   messagebox.showerror("Error de Acceso", "Lo siento, no tienes permiso para usar este programa.")
#    exit()


# Conexión a la base de datos MongoDB
client = MongoClient('mongodb://localhost/')
db = client['club_submarinismo']
expediciones = db['expediciones']
animales = db['animales']

# Crear la base de datos y las colecciones si no existen
if 'club_submarinismo' not in client.list_database_names():
    db = client.club_submarinismo

if 'expediciones' not in db.list_collection_names():
    expediciones = db.create_collection('expediciones')

if 'animales' not in db.list_collection_names():
    animales = db.create_collection('animales')

def agregar_expedicion_animal():
    fecha = fecha_entry.get()
    lugar = lugar_entry.get()
    animal = animal_entry.get()
    N_cient = N_cient_entry.get()

    if not fecha or not lugar or not animal or not N_cient:
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return

    # Verificar si el animal o nombre científico ya existe en la base de datos
    resultado = animales.find_one({'$or': [{'nombre': animal}, {'N_cient': N_cient}]})

    if resultado:
        fecha_expedicion = expediciones.find_one({'_id': resultado['idExpedicion']})['fecha']
        messagebox.showinfo("Aviso", f"Esta especie ya se introdujo en la base de datos el {fecha_expedicion}.")
        return

    # Si no existe, agregar la expedición y el animal
    expedicion_id = expediciones.insert_one({'fecha': fecha, 'lugar': lugar}).inserted_id
    animales.insert_one({'nombre': animal, 'N_cient': N_cient, 'idExpedicion': expedicion_id, 'cebo': None})
    messagebox.showinfo("Éxito", "Expedición y Animal agregados con éxito.")

def mostrar_animales():
    animales_registrados = animales.aggregate([
        {
            '$lookup': {
                'from': 'expediciones',
                'localField': 'idExpedicion',
                'foreignField': '_id',
                'as': 'expedicion'
            }
        },
        {
            '$unwind': '$expedicion'
        }
    ])
    animales_text = ""
    for animal in animales_registrados:
        animales_text += f"ID: {animal['_id']}\n"
        animales_text += f"Nombre: {animal['nombre']}\n"
        animales_text += f"N Científico: {animal['N_cient']}\n"
        if animal['cebo']:
            animales_text += f"Cebo: {animal['cebo']}\n"
        animales_text += f"Lugar: {animal['expedicion']['lugar']}\n"
        animales_text += f"Fecha: {animal['expedicion']['fecha']}\n"
        animales_text += "-------------------------------------\n"
    if animales_text:
        messagebox.showinfo("Animales Registrados", animales_text)
    else:
        messagebox.showinfo("Animales Registrados", "No hay animales registrados.")

def agregar_cebo():
    id_animal = simpledialog.askstring("ID del Animal", "Introduce el ID del animal:")
    cebo = simpledialog.askstring("Agregar Cebo", "Introduce el cebo:")

    if not id_animal or not cebo:
        messagebox.showerror("Error", "Debes proporcionar el ID del animal y el cebo.")
        return

    # Verificar si la ID del animal está registrada en la base de datos
    resultado = animales.find_one({'_id': id_animal})
    if not resultado:
        messagebox.showerror("Error", "La ID del animal no está registrada en la base de datos.")
        return

    # Actualizar el cebo del animal
    animales.update_one({'_id': id_animal}, {'$set': {'cebo': cebo}})
    messagebox.showinfo("Éxito", "Cebo agregado con éxito.")

# Interfaz gráfica con Tkinter
root = tk.Tk()
root.title("Club de Submarinismo")

frame_datos = tk.Frame(root)
frame_datos.pack(pady=10)

tk.Label(frame_datos, text="Fecha:", anchor="w").grid(row=0, column=0, sticky="w")
fecha_entry = tk.Entry(frame_datos)
fecha_entry.grid(row=0, column=1, sticky="w")

tk.Label(frame_datos, text="Lugar:", anchor="w").grid(row=1, column=0, sticky="w")
lugar_entry = tk.Entry(frame_datos)
lugar_entry.grid(row=1, column=1, sticky="w")

tk.Label(frame_datos, text="Animal:", anchor="w").grid(row=2, column=0, sticky="w")
animal_entry = tk.Entry(frame_datos)
animal_entry.grid(row=2, column=1, sticky="w")

tk.Label(frame_datos, text="N. científico:", anchor="w").grid(row=3, column=0, sticky="w")
N_cient_entry = tk.Entry(frame_datos)
N_cient_entry.grid(row=3, column=1, sticky="w")

agregar_button = tk.Button(frame_datos, text="Agregar Expedición y Animal", command=agregar_expedicion_animal)
agregar_button.grid(row=4, columnspan=2, pady=5)

mostrar_animales_button = tk.Button(frame_datos, text="Mostrar Animales", command=mostrar_animales)
mostrar_animales_button.grid(row=5, columnspan=2, pady=5)

agregar_cebo_button = tk.Button(frame_datos, text="Agregar Cebo", command=agregar_cebo)
agregar_cebo_button.grid(row=6, columnspan=2, pady=5)

# Botón para salir
salir_button = tk.Button(frame_datos, text="Salir", command=root.destroy)
salir_button.grid(row=7, columnspan=2, pady=5)

root.mainloop()
