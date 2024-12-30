from tkinter import ttk, messagebox
from tkinter import messagebox
from tasks import Tarea
from config import tk
import threading
import time
import json
import os

DATA_FILE = 'data/tareas.json'

class Ventana:
    """
    Clase para representar una ventana.
    
    Esta clase tiene la estructura para construir una ventana que va a 
    recibir y mostrar la infomación detallad sobre una tarea seleccionada
    y guardar el tiempo que el usuario se demora completar una tarea.
    
    Atributos:
        master: Ventana principal de la aplicación.
        tareas (list): Lista de tareas en memoria.
        timer_running (bool): Indica si el temporizador está en marcha.
        timer_thread (threading.Thread): Hilo para el temporizador.
        start_time (float): Tiempo de inicio del temporizador.
        current_task (Tarea): Tarea seleccionada para el temporizador.
    """
    def __init__(self, master):
        
        self.master = master # Ventana principal de la aplicación
        master.title("Gestión de Tareas con Temporizador")
        # master.geometry("600x800")

        # Lista de tareas en memoria
        self.tareas = self.cargar_tareas()

        # Variables para el temporizador
        self.timer_running = False # Indica si el temporizador está en marcha
        self.timer_thread = None # Hilo para el temporizador
        self.start_time = 0 # Tiempo de inicio del temporizador
        self.current_task = None # Tarea seleccionada para el temporizador

        # Frame para agregar tareas
        frame_agregar = tk.LabelFrame(master, text="Agregar Tarea")
        frame_agregar.pack(side="left", fill="y", padx=5, pady=5)

        # Campos para ingresar los datos de la tarea
        tk.Label(frame_agregar, text="Nombre:").grid(row=0, column=0, sticky="e") 
        tk.Label(frame_agregar, text="Conocimiento (1-5):").grid(row=1, column=0, sticky="e")
        tk.Label(frame_agregar, text="Recursos (1-5):").grid(row=2, column=0, sticky="e")
        tk.Label(frame_agregar, text="Dependencia (1-5):").grid(row=3, column=0, sticky="e")
        tk.Label(frame_agregar, text="Estrés (1-5):").grid(row=4, column=0, sticky="e")
        tk.Label(frame_agregar, text="Riesgo (1-5):").grid(row=5, column=0, sticky="e")
        tk.Label(frame_agregar, text="Energía (1-5):").grid(row=6, column=0, sticky="e")
        tk.Label(frame_agregar, text="Tiempo Est. (horas):").grid(row=7, column=0, sticky="e")
        
        # Campos de entrada
        self.entry_nombre = tk.Entry(frame_agregar, width=30)
        self.entry_conocimiento = tk.Entry(frame_agregar, width=5)
        self.entry_recursos = tk.Entry(frame_agregar, width=5)
        self.entry_dependencia = tk.Entry(frame_agregar, width=5)
        self.entry_estres = tk.Entry(frame_agregar, width=5)
        self.entry_riesgo = tk.Entry(frame_agregar, width=5)
        self.entry_energia = tk.Entry(frame_agregar, width=5)
        self.entry_tiempo = tk.Entry(frame_agregar, width=5)
        
        # Posicionar los campos de entrada
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)
        self.entry_conocimiento.grid(row=1, column=1, padx=5, pady=5)
        self.entry_recursos.grid(row=2, column=1, padx=5, pady=5)
        self.entry_dependencia.grid(row=3, column=1, padx=5, pady=5)
        self.entry_estres.grid(row=4, column=1, padx=5, pady=5)
        self.entry_riesgo.grid(row=5, column=1, padx=5, pady=5)
        self.entry_energia.grid(row=6, column=1, padx=5, pady=5)
        self.entry_tiempo.grid(row=7, column=1, padx=5, pady=5)

        # Botón para agregar tarea
        tk.Button(frame_agregar, text="Agregar", command=self.agregar_tarea)\
            .grid(row=9, column=0, columnspan=2, pady=5)

        # Frame para ver las tareas
        frame_tareas = tk.LabelFrame(master, text="Tareas")
        frame_tareas.pack(fill="both", expand="yes", padx=5, pady=5)
        
        
         # Crear el Treeview
        columnas = ("Nombre", "Conocimiento", "Recursos", "Dependencia", "Estrés", "Riesgo", "Energía", "Tiempo Est.", "Tiempo Real")
        self.tree = ttk.Treeview(frame_tareas, columns=columnas, show="headings", height=10)

        # Configurar encabezados y columnas
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Botones de acciones
        frame_botones = tk.Frame(master)
        frame_botones.pack(fill="x", padx=5, pady=5)
        
        btn_eliminar = tk.Button(frame_botones, text="Eliminar Tarea", command=self.eliminar_tarea)
        btn_eliminar.pack(side="left", padx=5)

        self.btn_iniciar = tk.Button(frame_botones, text="Iniciar Temporizador", command=self.iniciar_temporizador)
        self.btn_iniciar.pack(side="left", padx=5)

        self.btn_detener = tk.Button(frame_botones, text="Detener Temporizador", command=self.detener_temporizador)
        self.btn_detener.pack(side="left", padx=5)
        
        # Etiqueta para mostrar el tiempo transcurrido
        self.label_tiempo = tk.Label(master, text="Tiempo: 0s", font=("Helvetica", 12, "bold"))
        self.label_tiempo.pack(pady=5)


        # Agregar datos iniciales al Treeview
        self.actualizar_treeview()
            

    def agregar_tarea(self):
        """
        Agrega una nueva tarea a la lista (y al archivo JSON).
        """
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "El nombre de la tarea no puede estar vacío.")
            return
        
        try:
            # Lista de campos y sus widgets de entrada
            fields = [
                ("conocimiento", self.entry_conocimiento),
                ("recursos", self.entry_recursos),
                ("dependencia", self.entry_dependencia),
                ("estres", self.entry_estres),
                ("riesgo", self.entry_riesgo),
                ("energia", self.entry_energia),
            ]

            # Diccionario para almacenar los valores de los campos
            field_values = {}

            for field_name, entry in fields:
                # Convertir el valor a entero o asignar 0 si está vacío
                value = int(entry.get()) if entry.get() else 0
                if value > 5:
                    messagebox.showerror("Error", f"El valor de {field_name} no puede ser mayor a 5.")
                    return
                elif value < 0:
                    messagebox.showerror("Error", f"El valor de {field_name} no puede ser menor a 0.")
                    return
                else:
                    # Guardar el valor en el diccionario
                    field_values[field_name] = value

            # Obtener el tiempo estimado
            tiempo_estimado = float(self.entry_tiempo.get()) if self.entry_tiempo.get() else 0

        except ValueError:
            messagebox.showerror("Error", "Asegúrate de ingresar números válidos en los campos.")
            return
        nueva_tarea = Tarea(nombre, **field_values, tiempo_estimado=tiempo_estimado)
        nueva_tarea.calcular_dificultad_total()
        self.tareas.append(nueva_tarea)
        self.guardar_tareas()
        
        # Limpiar campos
        self.entry_nombre.delete(0, tk.END)
        self.entry_conocimiento.delete(0, tk.END)
        self.entry_recursos.delete(0, tk.END)
        self.entry_dependencia.delete(0, tk.END)
        self.entry_estres.delete(0, tk.END)
        self.entry_riesgo.delete(0, tk.END)
        self.entry_energia.delete(0, tk.END)
        self.entry_tiempo.delete(0, tk.END)

        # self.actualizar_listbox()
        self.actualizar_treeview()

    def eliminar_tarea(self):
        """
        Elimina la tarea seleccionada en el listbox.
        """
        idx = self.tree.selection()
        if not idx:
            messagebox.showinfo("Info", "Selecciona una tarea para iniciar el temporizador.")
            return

        index = int(self.tree.index(idx[0]))  # Convertir a entero
        
        # Elimina de la lista y del JSON
        self.tareas.pop(index)
        self.guardar_tareas()
        self.actualizar_treeview()
        messagebox.showinfo("Eliminar", "Tarea eliminada correctamente.")

    def iniciar_temporizador(self):
        """
        Inicia el temporizador para la tarea seleccionada.
        """
        idx = self.tree.selection()
        if not idx:
            messagebox.showinfo("Info", "Selecciona una tarea para iniciar el temporizador.")
            return

        index = int(self.tree.index(idx[0]))  # Convertir a entero

        # Si ya hay un temporizador corriendo, evita reiniciarlo
        if self.timer_running:
            messagebox.showwarning("Atención", "Ya hay un temporizador en marcha.")
            return
        
        # Iniciar el temporizador
        self.current_task = self.tareas[index]
        self.start_time = time.time()
        self.timer_running = True

        # Crear un thread para que no se bloquee la interfaz
        self.timer_thread = threading.Thread(target=self.actualizar_tiempo)
        self.timer_thread.daemon = True
        self.timer_thread.start()
        self.label_tiempo.config(text="Tiempo: 00:00")

    def detener_temporizador(self):
        """
        Detiene el temporizador y actualiza el tiempo de la tarea.
        """
        if not self.timer_running:
            messagebox.showinfo("Info", "No hay temporizador en marcha.")
            return

        self.timer_running = False
        tiempo_total = time.time() - self.start_time
        self.current_task.tiempo_real += round(tiempo_total / 3600.0, 3)  # Convertir segundos a horas y redondear a dos cifras significativas
        # tiempo_total_hms = time.strftime("%H:%M:%S", time.gmtime(tiempo_total))
        # self.current_task.tiempo_real += tiempo_total_hms

        self.guardar_tareas()
        self.actualizar_treeview()
        messagebox.showinfo("Info", f"Has registrado {tiempo_total:.2f} segundos más en la tarea.")
        

    def actualizar_tiempo(self):
        """
        Función que corre en un hilo separado para refrescar el tiempo transcurrido.
        """
        while self.timer_running:
            elapsed = time.time() - self.start_time
            # Mostrar en segundos
            self.label_tiempo.config(text=f"Tiempo: {int(elapsed)}s")
            time.sleep(1)  # Actualiza cada 1 segundo       
            
    def actualizar_treeview(self):
        """Limpia el Treeview y agrega todas las tareas de la lista."""
        # Limpiar Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Agregar filas
        for t in self.tareas:
            # Mostrar algo representativo, por ejemplo: 
            self.tree.insert("", "end", values=(t.nombre, t.conocimiento, t.recursos, t.dependencia, t.estres, t.riesgo, t.energia, t.tiempo_estimado, t.tiempo_real))


    def guardar_tareas(self):
        """
        Guarda la lista de tareas en un archivo JSON.
        """
        data = [t.to_dict() for t in self.tareas]
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def cargar_tareas(self):
        """
        Carga la lista de tareas desde un archivo JSON.
        """
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Tarea.from_dict(item) for item in data]
        return []


