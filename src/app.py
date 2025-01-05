from tkinter import ttk, messagebox
from tkinter import messagebox
from tasks import Tarea
from config import tk
import threading
import datetime
import time
import json
import os

fecha_actual = datetime.date.today().isoformat()
DATA_FILE = 'data/tareas ' + fecha_actual + '.json'


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
        self.entry_nombre = tk.Entry(frame_agregar, width=15)
        self.entry_conocimiento = tk.Entry(frame_agregar, width=3)
        self.entry_recursos = tk.Entry(frame_agregar, width=3)
        self.entry_dependencia = tk.Entry(frame_agregar, width=3)
        self.entry_estres = tk.Entry(frame_agregar, width=3)
        self.entry_riesgo = tk.Entry(frame_agregar, width=3)
        self.entry_energia = tk.Entry(frame_agregar, width=3)
        self.entry_tiempo = tk.Entry(frame_agregar, width=3)
        
        # Posicionar los campos de entrada
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=10)
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
        
        
        
        # Crear la tabla con las tareas (Treeview)
        columnas = ["Nombre", "Conocimiento", "Recursos", "Dependencia", "Estrés", "Riesgo", "Energía", "Tiempo Est.", "Tiempo Real", "Completada"]
 
        self.tree = ttk.Treeview(frame_tareas, columns=columnas, show="headings", height=10)
        
        
        # Configurar encabezados y columnas
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Hacer que las celdas sean editables
        self.tree.bind("<Double-1>", self.editar_celda)
        
        # Eventos para arrastrar y soltar
        self.tree.bind("<Button-1>", self.seleccionar_fila)  # Detectar clic en una fila
        self.tree.bind("<B1-Motion>", self.arrastrar_fila)  # Detectar movimiento con clic presionado
        self.tree.bind("<ButtonRelease-1>", self.soltar_fila)  # Detectar cuando se suelta el clic
        
        # Botones de acciones
        frame_botones = tk.Frame(master)
        frame_botones.pack(fill="x", padx=5, pady=5)
        
        self.btn_completar = tk.Button(frame_botones, text="Completar Tarea", command=self.completar_tarea)
        self.btn_completar.pack(side="left", padx=5, pady=5)
        
        btn_eliminar = tk.Button(frame_botones, text="Eliminar Tarea", command=self.eliminar_tarea)
        btn_eliminar.pack(side="left", padx=5)


        self.btn_detener = tk.Button(frame_botones, text="Detener Temporizador", command=self.detener_temporizador)
        self.btn_detener.pack(side="right", padx=5)
        
        self.btn_iniciar = tk.Button(frame_botones, text="Iniciar Temporizador", command=self.iniciar_temporizador)
        self.btn_iniciar.pack(side="right", padx=5)
        
        # Etiqueta para mostrar el tiempo transcurrido
        self.label_tiempo = tk.Label(master, text="Tiempo: 0s", font=("Helvetica", 12, "bold"))
        self.label_tiempo.pack(pady=5)

         # Etiqueta para mostrar el registro de tareas
        self.label_registro = tk.Label(master, text="Total tareas: 0 | Total dificultad: 0 | Total tiempo estimado: 0 | Total tiempo real: 0 | Completadas: 0 | Pendientes: 0", font=("Helvetica", 12))
        self.label_registro.pack(pady=5)

        # Actualizar el registro al iniciar
        self.actualizar_registro()
        
        # Agregar datos iniciales al Treeview
        self.actualizar_tabla()
            
#------------ Métodos de la clase Ventana ------------

#------------ Métodos de validación ------------
    def validar_rango(self,valor, min_val=0, max_val=5):
        """Valida que el valor esté dentro de un rango."""
        try:
            print("Tipo de valor", type(valor))
            valor = float(valor)
            if min_val <= valor <= max_val:
                return True
            else:
                return False
        except ValueError:
            return False


    def validar_numerico(self, valor):
        """Valida que el valor sea numérico."""
        try:
            float(valor)
            return True
        except ValueError:
            return False
    
    def validar_valor(self, columna, valor):
        """Valida un valor dependiendo de la columna."""
        if columna in ["Conocimiento", "Recursos", "Dependencia", "Estrés", "Riesgo", "Energía"]:
            if not self.validar_rango(valor):
                return False, f"El valor para '{columna}' debe estar entre 0 y 5."
        elif columna in ["Tiempo Est.", "Tiempo Real"]:
            if not self.validar_numerico(valor):
                return False, f"El valor para '{columna}' debe ser numérico."
        return True, None
    
        

#------------ Métodos para la gestión de tareas ------------
                          
    def agregar_tarea(self):
        """
        Agrega una nueva tarea a la lista (y al archivo JSON).
        """
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "El nombre de la tarea no puede estar vacío.")
            return
        
        # Diccionario para almacenar los valores de los campos
        field_values = {}
        
        # Lista de campos y sus widgets de entrada
        fields = [
            ("conocimiento", self.entry_conocimiento),
            ("recursos", self.entry_recursos),
            ("dependencia", self.entry_dependencia),
            ("estres", self.entry_estres),
            ("riesgo", self.entry_riesgo),
            ("energia", self.entry_energia),
        ]

        for field_name, entry in fields:
            value = float(self.entry_tiempo.get()) if self.entry_tiempo.get() else 0
            val, msg = self.validar_valor(field_name, valor=value)
            if val:
                field_values[field_name] = value
            else:
                messagebox.showerror("Error", msg)
                return
    

        # Obtener el tiempo estimado
        tiempo_estimado = float(self.entry_tiempo.get()) if self.entry_tiempo.get() else 0
            
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

        # Actualizar la tabla
        self.actualizar_tabla()
        
        # Actualizar el registro
        self.actualizar_registro()

    def eliminar_tarea(self):
        """Elimina una tarea tras confirmar su estado."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Selecciona una tarea para eliminar.")
            return

        index = int(self.tree.index(selected_item[0]))
        self.tareas.pop(index)
        self.guardar_tareas()
        self.actualizar_tabla()
        messagebox.showinfo("Eliminar", "Tarea eliminada correctamente.")
        
        
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

    def actualizar_registro(self):
        """
        Actualiza la etiqueta que muestra el número de tareas totales, completadas y no completadas.
        """
        total = len(self.tareas)
        completadas = sum(t.completada for t in self.tareas)
        pendientes = total - completadas
        dificultad_total = sum(t.dificultad_total for t in self.tareas)
        tiempo_estimado = sum(t.tiempo_estimado for t in self.tareas)
        tiempo_real = sum(t.tiempo_real for t in self.tareas)

        # Limites
        LIMITE_DIFICULTAD = 25
        LIMITE_ENERGIA = 50
        LIMITE_TIEMPO_ESTIMADO = 8
        # self.label_registro = tk.Label(master, text="Total tareas: 0 | Total dificultad: 0 | Total tiempo estimado: 0 | Total tiempo real: 0 | Completadas: 0 | Pendientes: 0", font=("Helvetica", 12))
        self.label_registro.config(text=f"Total tareas: {total} | Total difcultad: { dificultad_total } | Total tiempo estimado: {tiempo_estimado} | Total tiempo real: {tiempo_real} | Completadas: {completadas} | Pendientes: {pendientes}", font=("Helvetica", 12))

        if dificultad_total > LIMITE_DIFICULTAD or tiempo_estimado > LIMITE_TIEMPO_ESTIMADO:
            for entry in [self.entry_nombre, self.entry_conocimiento, self.entry_recursos, 
                          self.entry_dependencia, self.entry_estres, self.entry_riesgo, 
                          self.entry_energia, self.entry_tiempo]:
                entry.config(state='disabled')
            messagebox.showwarning("Límite alcanzado", "No se pueden agregar más tareas. Se ha alcanzado el límite de dificultad o tiempo estimado.")
            return False
        return True
        
    
    def completar_tarea(self):
        """
        Marca una tarea como completada.
        """
        idx = self.tree.selection()
        if not idx:
            messagebox.showinfo("Info", "Selecciona una tarea para marcar como completada.")
            return

        index = int(self.tree.index(idx[0]))
        self.tareas[index].completada = True
        self.guardar_tareas()
        self.actualizar_tabla()
        self.actualizar_registro()
        messagebox.showinfo("Info", "La tarea ha sido marcada como completada.")

#------------ Métodos para iniciar y detener temporizador ------------

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
        self.actualizar_tabla()
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

#------------ Métodos para actualizar la tabla ------------
    def actualizar_tabla(self):
        """Limpia el Treeview y agrega todas las tareas de la lista."""
        # Limpiar Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Agregar filas
        for t in self.tareas:
            #Se inserta una fila en el Treeview con los valores de la tarea
            self.tree.insert("", "end", values=tuple(t.to_dict().values()))

    def editar_celda(self, event):
        """Permite editar celdas del Treeview, restringiendo múltiples ventanas."""
        if hasattr(self, "ventana_edicion") and self.ventana_edicion.winfo_exists():
            # Si ya existe una ventana de edición activa, no hacer nada
            return

        # Obtener el valor actual de la celda
        item_id = self.tree.selection()[0]
        col = self.tree.identify_column(event.x)
        col_index = int(col.replace("#", "")) - 1
        nombre_columna = self.tree["columns"][col_index]
        valor_actual = self.tree.item(item_id)["values"][col_index]

        # Crear la ventana de edición
        self.ventana_edicion = tk.Toplevel(self.master)
        self.ventana_edicion.title("Editar Celda")
        self.ventana_edicion.geometry("300x100")
        self.ventana_edicion.grab_set()  # Bloquea la interacción con la ventana principal

        tk.Label(self.ventana_edicion, text="Nuevo valor de " + nombre_columna).pack(pady=5)
        entrada = tk.Entry(self.ventana_edicion)
        entrada.insert(0, str(valor_actual))
        entrada.pack(pady=5)
        
        def guardar_cambio():
            nuevo_valor = entrada.get()
            value = float(nuevo_valor) if nuevo_valor else 0
            val, msg = self.validar_valor(nombre_columna, nuevo_valor)
            
            if val:
                tarea = self.tareas[self.tree.index(item_id)]
                setattr(tarea, nombre_columna.lower().replace(" ", "_"), value) # Actualizar el valor del atributo, la función setattr() permite cambiar el valor de un atributo de un objeto
                self.guardar_tareas()
                self.actualizar_tabla()
                self.ventana_edicion.destroy()
            else:
                messagebox.showerror("Error", msg)
                return
            
        tk.Button(self.ventana_edicion, text="Guardar", command=guardar_cambio).pack(pady=5)

        # Esperar a que la ventana se cierre antes de continuar
        self.master.wait_window(self.ventana_edicion)

        
    def seleccionar_fila(self, event):
        """Seleccionar una fila para arrastrar."""
        item = self.tree.identify_row(event.y)
        if item:
            self.dragged_item = item

    def arrastrar_fila(self, event):
        """Mover la fila seleccionada mientras se arrastra."""
        if self.dragged_item:
            item_below = self.tree.identify_row(event.y)
            if item_below and item_below != self.dragged_item:
                # Intercambia las posiciones de las filas
                idx_dragged = self.tree.index(self.dragged_item)
                idx_below = self.tree.index(item_below)
                self.tree.move(self.dragged_item, "", idx_below)
                self.tree.move(item_below, "", idx_dragged)

    def soltar_fila(self, event):
        """Actualizar las tareas en memoria después de soltar la fila."""
        if self.dragged_item:
            # Obtener el orden actualizado de los elementos
            items = self.tree.get_children()
            new_order = [self.tree.item(i)["values"][0] for i in items]
            
            # Actualizar el orden de las tareas
            self.tareas = [t for t in self.tareas if t.nombre in new_order]
            # Guardar el nuevo orden en el archivo
            self.guardar_tareas()
            self.dragged_item = None


