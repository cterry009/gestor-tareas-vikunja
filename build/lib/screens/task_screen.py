# screens/task_screen.py (extracto para edición y eliminación)
import os
import json
import datetime
import time
import threading

from kivy.uix.screenmanager import Screen
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.clock import Clock
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.snackbar import Snackbar
from kivy.metrics import dp

from src.task import Tarea
from src.db.local_db import LocalDB  # Asegúrate de importar tu clase DB
import config

fecha_actual = datetime.date.today().isoformat()
DATA_FILE = f"data/tasks_{fecha_actual}.json"

class TaskScreen(Screen):
    def __init__(self, vikunja_api, local_db, **kwargs):
        super().__init__(**kwargs)
        self.vikunja_api = vikunja_api
        self.local_db = LocalDB(db_name=config.DB_PATH)
        self.tareas = self.cargar_desde_json()
        
        self.timer_running = False
        self.current_task = None
        self.start_time = 0
        self.timer_thread = None
        self.selected_row = None

        # Título
        title_label = MDLabel(
            text="Panel de Tareas",
            halign="center",
            font_style="H5",
            size_hint=(1, None),
            height=dp(40),
        )
        root_layout.add_widget(title_label)

        # Definir columnas para MDDataTable
        self.columnas = [
            ("Nombre", dp(100)),
            ("Conoc.", dp(70)),
            ("Rec.", dp(60)),
            ("Dep.", dp(60)),
            ("Estrés", dp(60)),
            ("Riesgo", dp(60)),
            ("Dif.", dp(50)),
            ("Est.", dp(50)),
            ("Real", dp(50)),
            ("Comp.", dp(60)),
        ]
        self.filas = self.generar_filas()

        self.data_table = MDDataTable(
            size_hint=(1, 0.65),
            column_data=self.columnas,
            row_data=self.filas,
            use_pagination=False
        )
        self.data_table.bind(on_row_press=self.on_row_press)
        root_layout.add_widget(self.data_table)

        # Botones
        btn_layout = MDBoxLayout(orientation="horizontal", spacing=5, size_hint=(1, None), height=dp(50))
        root_layout.add_widget(btn_layout)

        self.btn_completar = MDRaisedButton(text="Completar", on_release=self.completar_tarea)
        self.btn_eliminar = MDRaisedButton(text="Eliminar", on_release=self.eliminar_tarea)
        self.btn_iniciar = MDRaisedButton(text="Iniciar Timer", on_release=self.iniciar_temporizador)
        self.btn_detener = MDRaisedButton(text="Detener Timer", on_release=self.detener_temporizador)

        btn_layout.add_widget(self.btn_completar)
        btn_layout.add_widget(self.btn_eliminar)
        btn_layout.add_widget(self.btn_iniciar)
        btn_layout.add_widget(self.btn_detener)

        # Label de tiempo
        self.label_tiempo = MDLabel(text="Tiempo: 0s", halign="center")
        root_layout.add_widget(self.label_tiempo)

        # Label de estadísticas
        self.label_registro = MDLabel(text="Estadísticas...", halign="center")
        root_layout.add_widget(self.label_registro)

        self.actualizar_registro()

     # ------------------ Cargar y guardar JSON ------------------
    def cargar_desde_json(self):
        """Carga la lista de tareas desde el archivo JSON (si existe)."""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Tarea.from_dict(d) for d in data]
        return []

    def guardar_a_json(self):
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
        
      # ------------------ Generar filas para MDDataTable ------------------
    def _generar_filas(self):
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
                self.guardar_a_json()  # guardamos inmediatamente
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
            self.guardar_a_json()
            self.actualizar_tabla()
            self.actualizar_registro()
            Snackbar(text=f"Eliminada '{nombre}'").open()

    # ------------------ Temporizador ------------------
    def iniciar_temporizador(self, instance):
        if self.timer_running:
            Snackbar(text="Temporizador en marcha").open()
            return
        if not self.selected_row:
            Snackbar(text="Selecciona una tarea").open()
            return
        data = self.selected_row.row_data
        nombre = data[0]
        for t in self.tareas:
            if t.nombre == nombre:
                self.current_task = t
                break
        if not self.current_task:
            Snackbar(text="No se encontró la tarea").open()
            return

        self.timer_running = True
        self.start_time = time.time()
        self.timer_thread = threading.Thread(target=self._timer_bg)
        self.timer_thread.daemon = True
        self.timer_thread.start()
        Snackbar(text=f"Timer iniciado: {nombre}").open()

    def detener_temporizador(self, instance):
        if not self.timer_running:
            Snackbar(text="No hay temporizador activo").open()
            return
        self.timer_running = False
        elapsed = time.time() - self.start_time
        horas = round(elapsed / 3600, 3)
        if self.current_task:
            self.current_task.tiempo_real += horas
            self.guardar_a_json()
            self.actualizar_tabla()
            Snackbar(text=f"Se sumaron {horas}h a '{self.current_task.nombre}'").open()
        self.current_task = None

    def _timer_bg(self):
        """Hilo que actualiza cada segundo la etiqueta de tiempo."""
        while self.timer_running:
            elapsed = time.time() - self.start_time
            self.label_tiempo.text = f"Tiempo: {int(elapsed)}s"
            time.sleep(1)