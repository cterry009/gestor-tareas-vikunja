# Importaciones de terceros
import time
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp
from threading import Thread
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.scrollview import MDScrollView


class TaskScreenUI(MDBoxLayout):
    def __init__(self, task_manager, **kwargs):
        super().__init__(**kwargs)
        self.task_manager = task_manager
        self.orientation = 'vertical'
        self.selected_row = None
        self.current_task = None
        self.timer_thread = None
        self.columnas = self.get_column_data()
        self.text_fields = []  # Lista para campos de texto
        self.setup_ui()
        self.bind_events()

    def setup_ui(self):
        """Configura todos los elementos de la UI"""
        # Contenedor principal
        self.main_layout = MDBoxLayout(
            orientation="vertical",
            spacing=10,
            padding=10,
            size_hint=(1, 1)
        )
    
        
        # Título más compacto
        title_label = MDLabel(
            text="Panel de Tareas",
            halign="center",
            font_style="H5",
            size_hint=(1, None),
            height=dp(40)  # Reducida altura del título
        )
        self.main_layout.add_widget(title_label)

        # Panel central con más espacio
        central_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=10,
            size_hint=(1, 1),
            padding=[5, 5, 5, 5]  # Padding reducido
        )

        # Panel izquierdo más compacto
        left_panel = MDBoxLayout(
            orientation="vertical",
            spacing=5,
            size_hint=(0.45, 1)  # Reducido el ancho del panel izquierdo
        )
        self.add_inputs_to_panel(left_panel)
        
        # Panel derecho más amplio
        right_panel = MDBoxLayout(
            orientation="vertical",
            spacing=5,
            size_hint=(0.65, 1)  # Aumentado el ancho del panel derecho
        )
        self.add_table_to_panel(right_panel)

        # Agregar paneles al layout central
        central_layout.add_widget(left_panel)
        central_layout.add_widget(right_panel)
        
        # Agregar layout central al main layout
        self.main_layout.add_widget(central_layout)

        # Etiquetas inferiores en un contenedor separado
        bottom_layout = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=dp(80),
            padding=[0, 10, 0, 10]
        )
        
        self.label_tiempo = MDLabel(
            text="Tiempo: 0s",
            halign="center",
            size_hint=(1, None),
            height=dp(30)
        )
        self.label_registro = MDLabel(
            text="Estadísticas...",
            halign="center",
            size_hint=(1, None),
            height=dp(30)
        )
        
        bottom_layout.add_widget(self.label_tiempo)
        bottom_layout.add_widget(self.label_registro)
        
        # Agregar bottom layout al main layout
        self.main_layout.add_widget(bottom_layout)

        # Agregar el main layout al widget raíz
        self.add_widget(self.main_layout)

    def add_inputs_to_panel(self, left_panel):  # Agregado self como primer parámetro
        """Panel izquierdo con campos de entrada"""
        # Título del panel
        left_panel.add_widget(MDLabel(
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

        self.text_fields = []  # Lista para almacenar referencias

        for label_text, hint_text, input_type in campos:
            # Contenedor para cada campo
            field_container = MDBoxLayout(
                orientation="horizontal",
                size_hint=(1, None),
                size_hint_y=0.6,
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
                helper_text_mode="on_error",
                multiline=False,  # Importante para el manejo de Tab
                write_tab=False   # No insertar Tab como texto
            )

            if input_type == "number":
                text_field.input_filter = "float"

            field_container.add_widget(text_field)
            left_panel.add_widget(field_container)
            self.text_fields.append(text_field)  # Guardar referencia

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
            on_release=self.on_create_task  # Cambiado a método local
        ))

        left_panel.add_widget(buttons_container)
        return left_panel

    def on_create_task(self, instance):
        """Maneja la creación de una nueva tarea"""
        try:
            # Mapeo de hint_text a nombres de atributos de Tarea
            field_mapping = {
                "Nombre de la tarea": "nombre",
                "1-5": None,  # Se asignará según el label
                "Ej: 2.5": "tiempo_estimado"
            }

            # Recolectar datos de los campos
            task_data = {}
            
            for field, label in zip(self.text_fields, [
                "nombre", "conocimiento", "recursos", "dependencia", 
                "estres", "riesgo", "tiempo_estimado"
            ]):
                value = field.text.strip()
                
                if not value:
                    Snackbar(text=f"El campo {field.hint_text} es requerido").open()
                    return

                # Convertir a float si es numérico
                if field.input_filter == 'float':
                    try:
                        value = float(value)
                        if label != "tiempo_estimado" and not (1 <= value <= 5):
                            Snackbar(text=f"El valor debe estar entre 1 y 5").open()
                            return
                    except ValueError:
                        Snackbar(text=f"Valor inválido para {field.hint_text}").open()
                        return

                task_data[label] = value

            # Crear la tarea
            new_task = self.task_manager.create_task(task_data)
            if new_task:
                # Limpiar campos
                for field in self.text_fields:
                    field.text = ""
                # Actualizar UI
                self.update_all()
                Snackbar(text="Tarea creada exitosamente").open()
            else:
                Snackbar(text="Error al crear la tarea").open()

        except Exception as e:
            Snackbar(text=f"Error: {str(e)}").open()
            print(f"Error detallado: {e}")  # Para debug

    def update_all(self):
        """Actualiza todos los elementos de la UI"""
        self.update_table()
        self.update_stats()
        
    def update_table(self):
        """Actualiza la tabla de tareas"""
        rows = []
        for task in self.task_manager.tareas:
            rows.append([
                task.nombre,
                task.conocimiento,
                task.recursos,
                task.dependencia,
                task.estres,
                task.riesgo,
                task.dificultad_total,
                task.tiempo_estimado,
                task.tiempo_real,
                task.completada
            ])
            
        if hasattr(self, 'data_table'):
            self.data_table = MDDataTable(
                size_hint=(1, 0.8),
                column_data=self.columnas,
                row_data=rows,
                use_pagination=False
            )
            self.data_table.bind(on_row_press=self.on_row_press)
        else:
            self.data_table.update_row_data(None, rows)
    
    def on_window_resize(self, instance, *args):
        """Actualiza las columnas al redimensionar"""
        if hasattr(self, 'data_table'):
            self.data_table.column_data = self.get_column_data()
        
        num_columns = len(self.columnas)
        width = Window.width
        height = Window.height
        
        # Calcular factores de escala
        width_scale = width / 1024
        height_scale = height / 768
        
        # Adjust table
        if hasattr(self, 'data_table'):
            table_height = min(height * 0.8, height * 0.7)
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
        
        # Update layout (cambiado root_layout por main_layout)
        self.main_layout.do_layout()
        
        # Ajustar tamaño de etiquetas
        label_height = dp(30 * height_scale)
        
        # Ajustar proporciones generales
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
            # Actualizamos también el acceso a las estadísticas
            stats = self.task_manager.get_statistics()
            self.label_registro.text = (
                f"Total: {stats['total']} | "
                f"Dificultad: {stats['difficulty']:.1f} | "
                f"Est: {stats['estimated_time']:.1f}h | "
                f"Real: {stats['real_time']:.1f}h | "
                f"Completas: {stats['completed']} | "
                f"Pend: {stats['total'] - stats['completed']}"
            )
    
    def update_stats(self):
        """Actualiza estadísticas"""
        stats = self.task_manager.get_statistics()
        self.label_registro.text = (
            f"Total: {stats['total']} | "
            f"Completadas: {stats['completed']} | "
            f"Tiempo Est: {stats['estimated_time']}h"
        )

    def add_table_to_panel(self, panel):
        """Agrega la tabla y botones al panel derecho"""
        # Contenedor para la tabla con ScrollView
        table_container = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, 0.9)  # 90% del espacio para la tabla
        )
        
        self.data_table = MDDataTable(
            size_hint=(1, 1),
            column_data=self.get_column_data(),
            row_data=[],
            # check=True,
            background_color_header="#2196F3",
            background_color_selected_cell="#90CAF9"
        )
        self.data_table.bind(on_row_press=self.on_row_press)
        table_container.add_widget(self.data_table)
        panel.add_widget(table_container)

        # Botones en contenedor separado
        btn_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=5,
            size_hint=(1, 0.1),  # 10% del espacio para botones
            padding=[2, 2, 2, 2]
        )
        
        actions = [
            ("Completar", self.on_complete_task),
            ("Eliminar", self.on_delete_task),
            ("Iniciar Timer", self.on_start_timer),
            ("Detener Timer", self.on_stop_timer)
        ]
        
        # Crear botones
        for text, callback in actions:
            btn_layout.add_widget(
                MDRaisedButton(
                    text=text,
                    size_hint=(1, None),
                    height=dp(40),
                    on_release=callback
                )
            )
        panel.add_widget(btn_layout)

    def get_column_data(self):
        """Retorna la configuración de columnas ajustada"""
        # Definimos las proporciones relativas
        column_proportions = {
            "Nombre": 0.20,
            "Conoc.": 0.01,
            "Rec.": 0.01,
            "Dep.": 0.01,
            "Estrés": 0.01,
            "Riesgo": 0.01,
            "Dif.": 0.01,
            "Est.": 0.05,
            "Real": 0.05,
            "Comp.": 0.05
        }
        
        return [
            (name, dp(15))  # Inicialmente asignamos un ancho mínimo
            for name in column_proportions.keys()
        ]

    # Manejadores de eventos
    def on_row_press(self, instance_table, instance_row):
        """Maneja la selección de fila"""
        self.selected_row = instance_row

    def on_complete_task(self, instance):
        """Marca una tarea como completada"""
        if not self.selected_row:
            Snackbar(text="Selecciona una tarea primero").open()
            return
        
        task_name = self.selected_row.text
        if self.task_manager.complete_task(task_name):
            self.update_all()
            Snackbar(text=f"Tarea '{task_name}' completada").open()

    def on_delete_task(self, instance):
        """Elimina la tarea seleccionada"""
        if not self.selected_row:
            Snackbar(text="Selecciona una tarea primero").open()
            return
            
        task_name = self.selected_row.text
        self.task_manager.delete_task(task_name)
        self.update_all()
        Snackbar(text=f"Tarea '{task_name}' eliminada").open()

    def on_start_timer(self, instance):
        """Inicia el temporizador para la tarea seleccionada"""
        if not self.selected_row:
            Snackbar(text="Selecciona una tarea primero").open()
            return
            
        task_name = self.selected_row.text
        if self.task_manager.start_timer(task_name):
            self.current_task = self.task_manager.get_task(task_name)
            self._start_timer_updates()
            Snackbar(text=f"Timer iniciado para '{task_name}'").open()

    def on_stop_timer(self, instance):
        """Detiene el temporizador actual"""
        if not self.current_task:
            Snackbar(text="No hay temporizador activo").open()
            return
            
        task_name = self.current_task.nombre
        if self.task_manager.stop_timer(task_name):
            self.current_task = None
            self.update_all()
            Snackbar(text=f"Timer detenido para '{task_name}'").open()

    def _start_timer_updates(self):
        """Inicia las actualizaciones del temporizador en UI"""
        if self.timer_thread & self.timer_thread.is_alive():
            return
            
        self.timer_thread = Thread(target=self._update_timer_ui)
        self.timer_thread.daemon = True
        self.timer_thread.start()

    def _update_timer_ui(self):
        """Actualiza la UI del temporizador"""
        while self.current_task & self.current_task.timer_running:
            elapsed = self.current_task.get_tiempo_transcurrido()
            Clock.schedule_once(lambda dt: self._set_timer_label(elapsed))
            time.sleep(1)
            
    def _set_timer_label(self, elapsed):
        """Actualiza la etiqueta del temporizador"""
        self.label_tiempo.text = f"Tiempo: {elapsed}s"

    def bind_events(self):
        """Vincula eventos de la ventana y teclado"""
        Window.bind(on_resize=self.on_window_resize)
        Window.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        """Manejador global de eventos de teclado"""
        if keycode == 9:  # Tab
            if self.text_fields:
                try:
                    # Buscar el campo actual con foco
                    current_field = None
                    for field in self.text_fields:
                        if field.focus:
                            current_field = field
                            break

                    if current_field:
                        # Obtener índice del campo actual
                        idx = self.text_fields.index(current_field)
                        # Calcular siguiente índice
                        next_idx = (idx + 1) % len(self.text_fields)
                        # Dar foco al siguiente campo
                        Clock.schedule_once(
                            lambda dt: setattr(self.text_fields[next_idx], 'focus', True)
                        )
                    else:
                        # Si ningún campo tiene foco, empezar por el primero
                        Clock.schedule_once(
                            lambda dt: setattr(self.text_fields[0], 'focus', True)
                        )
                except Exception as e:
                    print(f"Error en navegación de campos: {e}")
                return True
        return False
