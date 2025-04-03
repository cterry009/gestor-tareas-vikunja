# screens/task_screen.py (extracto para edición y eliminación)

# Importaciones estándar
import datetime

# Importaciones de terceros
# Kivy imports
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp

# Local imports

from screens.task_screen_ui import TaskScreenUI
from tasks.task_manager import TaskManager



class TaskScreen(Screen):
    def __init__(self, vikunja_api, local_db, **kwargs):
        super().__init__(**kwargs)
        
        # Crear el gestor de tareas
        self.task_manager = TaskManager(vikunja_api, local_db)
        
        # Crear la UI y pasarle el gestor
        self.ui = TaskScreenUI(self.task_manager)
        self.add_widget(self.ui)
        
        # Inicializar
        self.task_manager.load_tasks()
        self.ui.update_all()


