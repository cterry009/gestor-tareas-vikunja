# screens/task_screen.py (extracto para edición y eliminación)
import os
import json
import time
import datetime

from threading import Thread

from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.clock import Clock
from kivymd.uix.datatables import MDDataTable
from kivy.core.window import Window
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp

from task import Tarea
from local_db import LocalDB
from config_loader import load_config  # Changed import

fecha_actual = datetime.date.today().isoformat()
DATA_FILE = f"data/tasks_{fecha_actual}.json"
config = load_config("config/config.yaml")

db_name = config['database']['name']
class TaskScreen(Screen):
    def __init__(self, vikunja_api, local_db, **kwargs):
        super().__init__(**kwargs)
        self.vikunja_api = vikunja_api
        self.local_db = LocalDB(db_name=db_name)
        self.tareas = self.load_to_json()
        
        self.current_task = None
        self.timer_thread = None
        self.selected_row = None
        
        #Inicializa la intefaz de usuario
        self.setup_layout()
        self.bind_events()
        self.actualizar_registro()

      
        # (Opcional) Llamada automática a sync_to_db cada X segundos
        # Clock.schedule_interval(self.sync_to_db, 60)  # cada 60s

#------------------ Métodos de diseño ------------------
    def setup_layout(self):   
        "Inicializa el diseño de la pantalla"
        
        # Define el layout principal y guárdalo en una variable (o en self.)
        self.root_layout = MDBoxLayout(orientation="vertical", spacing=10, padding=10)
        self.add_widget(self.root_layout)
        
        # Layout principal con ScrollView
        scroll_view = MDScrollView(size_hint=(1, 1))
        self.root_layout = MDBoxLayout(orientation="vertical", spacing=10, padding=10, size_hint_y=None)
        self.root_layout.bind(minimum_height=self.root_layout.setter("height"))  # Ajuste dinámico
        scroll_view.add_widget(self.root_layout)
        self.add_widget(scroll_view)

        
        
        # Título
        title_label = MDLabel(
            text="Panel de Tareas",
            halign="center",
            font_style="H5",
            size_hint=(1, None),
            height=dp(40),
        )
        self.root_layout.add_widget(title_label)


        # Panel central
        central_layout = MDBoxLayout(orientation="horizontal", spacing=10, size_hint=(1, None), height=dp(500))
        self.root_layout.add_widget(central_layout)

        # Panel izquierdo (Agregar Tarea)
        left_panel = MDBoxLayout(orientation="vertical", spacing=8, size_hint=(0.4, 1))
        self.add_inputs_to_panel(left_panel)
        central_layout.add_widget(left_panel)

        # Panel derecho (Tabla y botones)
        right_panel = MDBoxLayout(orientation="vertical", spacing=8, size_hint=(0.6, 1))
        self.add_table_to_panel(right_panel)
        central_layout.add_widget(right_panel)

        # Etiquetas inferiores
        self.label_tiempo = MDLabel(text="Tiempo: 0s", halign="center", size_hint=(1, None), height=dp(30))
        self.root_layout.add_widget(self.label_tiempo)
        self.label_registro = MDLabel(text="Estadísticas...", halign="center", size_hint=(1, None), height=dp(30))
        self.root_layout.add_widget(self.label_registro)

       

    def add_inputs_to_panel(self, panel):
        """Agrega los campos de entrada al panel izquierdo."""
         # Título del panel
        panel.add_widget(MDLabel(
            text="Nueva Tarea",
            halign="center",
            font_style="H6",
            size_hint_y=None,
            height=dp(40)
        ))

        # Campos de entrada
        campos = [
            ("Nombre:", "Nombre de la tarea", "text"),
            ("Conocimiento (1-5):", "1-5", "number"),
            ("Recursos (1-5):", "1-5", "number"),
            ("Dependencia (1-5):", "1-5", "number"),
            ("Estrés (1-5):", "1-5", "number"),
            ("Riesgo (1-5):", "1-5", "number"),
            ("Tiempo Est. (horas):", "Ej: 2.5", "number")
        ]

        for label_text, hint_text, input_type in campos:
            # Contenedor para cada campo
            field_container = MDBoxLayout(
                orientation="horizontal",
                size_hint=(1, None),
                size_hint_y=0.5,
                size_hint_x=1,
                height=dp(50),
                pos_hint={"center_x": 0.5, "center_y": 0.5}
            )

            # Label
            field_container.add_widget(MDLabel(
                text=label_text,
                size_hint_y=None,
                height=dp(20),
                font_style="Caption"
            ))

            # Input
            text_field = MDTextField(
                hint_text=hint_text,
                mode="rectangle",
                size_hint_y=None,
                height=dp(40),
                helper_text="Campo requerido",
                helper_text_mode="on_error"
            )

            if input_type == "number":
                text_field.input_filter = "float"

            field_container.add_widget(text_field)
            panel.add_widget(field_container)

            # Botones
            buttons_container = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(50),
                spacing=10,
                padding=[10, 10, 10, 10]
            )

        buttons_container.add_widget(MDRaisedButton(
            text="Agregar Tarea",
            size_hint_x=1,
            on_release=self.add_to_json
        ))

        panel.add_widget(buttons_container)

    def add_table_to_panel(self, panel):
        """Agrega la tabla y botones al panel derecho."""
        
        # Obtén el ancho total disponible
        total_width = Window.width
        
        self.columnas = [
                ("Nombre", dp(total_width * 0.3)),  # 20% del ancho total
                ("Conoc.", dp(total_width * 0.1)),  # 10% del ancho total
                ("Rec.", dp(total_width * 0.1)),
                ("Dep.", dp(total_width * 0.1)),
                ("Estrés", dp(total_width * 0.1)),
                ("Riesgo", dp(total_width * 0.1)),
                ("Dif.", dp(total_width * 0.)),
                ("Est.", dp(total_width * 0.1)),
                ("Real", dp(total_width * 0.1)),
                ("Comp.", dp(total_width * 0.1))
        ]
        self.filas = []
        self.data_table = MDDataTable(
            size_hint=(1, 0.8),
            column_data=self.columnas,
            row_data=self.filas,
            use_pagination=False
        )
        panel.add_widget(self.data_table)

        # Botones
        btn_layout = MDBoxLayout(orientation="horizontal", spacing=5, size_hint=(1, None), height=dp(50))
        btn_layout.add_widget(MDRaisedButton(text="Completar", size_hint=(1, None), height=dp(50)))
        btn_layout.add_widget(MDRaisedButton(text="Eliminar", size_hint=(1, None), height=dp(50)))
        btn_layout.add_widget(MDRaisedButton(text="Iniciar Timer", size_hint=(1, None), height=dp(50)))
        btn_layout.add_widget(MDRaisedButton(text="Detener Timer", size_hint=(1, None), height=dp(50)))
        panel.add_widget(btn_layout)
        
            # ------------------ Generar filas para MDDataTable ------------------
    def generar_filas(self):
        filas = []
        for t in self.tareas:
            filas.append([
                t.nombre,
                str(t.conocimiento),
                str(t.recursos),
                str(t.dependencia),
                str(t.estres),
                str(t.riesgo),
                str(t.dificultad_total),
                str(t.tiempo_estimado),
                str(t.tiempo_real),
                str(t.completada)
            ])
        return filas

    def actualizar_tabla(self):
        self.filas = self._generar_filas()
        self.data_table.update_row_data(None, self.filas)

    def actualizar_registro(self):
        total = len(self.tareas)
        completadas = sum(t.completada for t in self.tareas)
        pendientes = total - completadas
        dif_total = sum(t.dificultad_total for t in self.tareas)
        t_est = sum(t.tiempo_estimado for t in self.tareas)
        t_real = sum(t.tiempo_real for t in self.tareas)
        self.label_registro.text = (
            f"Total: {total} | Dificultad: {dif_total} | "
            f"Est: {t_est}h | Real: {t_real:.2f}h | "
            f"Completas: {completadas} | Pend: {pendientes}"
        )

    # ------------------ Eventos al hacer clic en la tabla ------------------
    def on_row_press(self, table, row):
        self.selected_row = row.table_row

    # ------------------ Métodos CRUD (completar, eliminar, etc.) ------------------
    def completar_tarea(self, instance):
        if not self.selected_row:
            Snackbar(text="Ninguna fila seleccionada").open()
            return
        data = self.selected_row.row_data
        nombre = data[0]
        for t in self.tareas:
            if t.nombre == nombre:
                t.completada = True
                self.add_to_json()  # guardamos inmediatamente
                self.actualizar_tabla()
                self.actualizar_registro()
                Snackbar(text=f"Tarea '{nombre}' completada").open()
                break

    def eliminar_tarea(self, instance):
        if not self.selected_row:
            Snackbar(text="Ninguna fila seleccionada").open()
            return
        data = self.selected_row.row_data
        nombre = data[0]
        idx = None
        for i, t in enumerate(self.tareas):
            if t.nombre == nombre:
                idx = i
                break
        if idx is not None:
            self.tareas.pop(idx)
            self.add_to_json()
            self.actualizar_tabla()
            self.actualizar_registro()
            Snackbar(text=f"Eliminada '{nombre}'").open()
        
# ------------------ Evento de cambio de tamaño de ventana ------------------

    def bind_events(self):
        """Vincula los eventos de redimensionamiento de ventana."""
        Window.bind(on_resize=self.on_window_resize)
        self.bind(size=self.on_window_resize)
        
    def on_window_resize(self, instance, *args):
        """Manejador de redimensionamiento de ventana mejorado"""
        
        
        num_columns = len(self.columnas)
        
        width = Window.width
        height = Window.height
        
        # Calcular factores de escala
        width_scale = width / 1024  # base width
        height_scale = height / 768  # base height
        # height_scale = height / num_columns  # base height
        
         # Adjust table
        if hasattr(self, 'data_table'):
            table_height = min(height * 0.8, height * 0.7)  # 70-80% of height
            self.data_table.size_hint = (0.95, table_height/height)
        
        # Adjust left panel
        if hasattr(self, 'left_panel'):
            panel_width = 0.3 if width > 800 else 0.4
            self.left_panel.size_hint = (panel_width, 1)
            
            # Scale input fields
            for widget in self.left_panel.walk():
                if isinstance(widget, MDTextField):
                    widget.size_hint = (0.9, None)
                    widget.height = dp(40 * height_scale)
        
        # Update layout
        self.root_layout.do_layout()
        
        # Ajustar tamaño de etiquetas
        label_height = dp(30 * height_scale)
        
        # Ajustar proporciones generales (opcional)
        if width < instance.width:
            self.label_tiempo.height = label_height
            self.label_tiempo.font_size = dp(12 * width_scale)
            self.label_registro.height = label_height
            self.label_registro.font_size = dp(12 * width_scale)
            self.label_registro.text = "Vista compacta"
        else:
            self.label_tiempo.height = label_height
            self.label_tiempo.font_size = dp(14 * width_scale)
            self.label_registro.height = label_height
            self.label_registro.font_size = dp(14 * width_scale)
            self.label_registro.text = (
                f"Total: {len(self.tareas)} | "
                f"Dificultad: {self.tareas.calcular_dificultad_total():.1f} | "
                f"Est: {self.tareas.calcular_tiempo_estimado():.1f}h | "
                f"Real: {self.calcular_tiempo_real():.1f}h | "
                f"Completas: {self.contar_completas()} | "
                f"Pend: {len(self.tareas) - self.contar_completas()}"
            )
# ------------------ Cargar y guardar JSON ------------------
    def load_to_json(self):
        """Carga la lista de tareas desde el archivo JSON (si existe)."""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Tarea.from_dict(d) for d in data]
        return []

    def add_to_json(self):
        """Guarda self.tareas al archivo JSON."""
        data = [t.to_dict() for t in self.tareas]
        if not os.path.exists("data"):
            os.makedirs("data")
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

# ------------------ Sincronización con DB ------------------
    def sync_to_db(self, dt):
        """
        Se llama cada X segundos (ej. 60).
        Recorre 'self.tareas' y las guarda/actualiza en la DB local.
        """
        # Aquí puedes implementar la lógica: 
        # 1) Checar si la tarea ya existe en DB (por título o ID).
        # 2) Insertar o actualizar según haga falta.
        # 3) (Opcional) Podrías también leer la DB para tareas que no estén en self.tareas.

        for t in self.tareas:
            # Ejemplo: check si existe por 'title'
            # Para simplificar, supongamos que no existe y la insertamos.
            # Ojo: en un caso real, necesitarías un get_task_by_title(t.nombre) etc.
            self.local_db.add_task(
                vikunja_task_id=None,
                title=t.nombre,
                description="",  # o t.algunaDescripcion
                knowledge=t.conocimiento,
                resources=t.recursos,
                dependency=t.dependencia,
                stress=t.estres,
                risk=t.riesgo,
                estimated_time=t.tiempo_estimado,
                difficulty=t.dificultad_total
            )
        # Si quisieras evitar duplicados, primero buscarías en DB y harías update.
        # Pero esto te muestra la idea general.

        # Mensaje rápido en consola o UI para saber que se sincronizó
        print("[sync_to_db] Se han sincronizado las tareas con la DB.")
        # O un Snackbar:
        # Snackbar(text="Sincronizado con DB").open()

        
    def create_task(self, instance):
        """
        Lógica para crear una tarea en Vikunja (y opcionalmente guardarla
        en la DB local).
        """
        title = self.task_input.text.strip()
        desc = self.desc_input.text.strip()
        selected_list = self.spinner.text

        if not title:
            self.info_label.text = "El título no puede estar vacío."
            return

        # Aquí podrías obtener la ID real de la lista (proyecto) desde Vikunja.
        # Por ejemplo, si 'Mi Lista 1' corresponde a ID=123, etc.
        # new_task = self.vikunja_api.create_task(list_id=123, title=title, description=desc)

        # Si se crea exitosamente:
        self.info_label.text = f"Tarea '{title}' creada en la lista '{selected_list}'."
        self.task_input.text = ""
        self.desc_input.text = ""

        # También podrías guardar en local_db:
        # self.local_db.add_task(...)

        # O refrescar la lista de tareas, etc.
        


# ------------------ Temporizador ------------------
    def iniciar_temporizador(self, instance):
        if not self.selected_row:
            Snackbar(text="Ninguna fila seleccionada").open()
            return
            
        nombre = self.selected_row.row_data[0]
        tarea = next((t for t in self.tareas if t.nombre == nombre), None)
        
        if tarea and tarea.iniciar_temporizador():
            self.current_task = tarea
            self._iniciar_actualizacion_ui()
            Snackbar(text=f"Iniciando tiempo para '{nombre}'").open()
        
    def _iniciar_actualizacion_ui(self):
        """Inicia el hilo de actualización de UI"""
        self.timer_thread = Thread(target=self._actualizar_tiempo_ui)
        self.timer_thread.daemon = True
        self.timer_thread.start()
        
    def _actualizar_tiempo_ui(self):
        """Actualiza la UI con el tiempo transcurrido"""
        while self.current_task and self.current_task.timer_running:
            elapsed = self.current_task.get_tiempo_transcurrido()
            self.label_tiempo.text = f"Tiempo: {elapsed}s"
            time.sleep(1)

    def detener_temporizador(self, instance):
        if not self.current_task:
            Snackbar(text="No hay temporizador activo").open()
            return
            
        if self.current_task.detener_temporizador():
            self.add_to_json()
            self.actualizar_tabla()
            Snackbar(text=f"Timer detenido para '{self.current_task.nombre}'").open()
            self.current_task = None
            self.label_tiempo.text = "Tiempo: 0s"


