import os
import json
from datetime import date
from tasks.task import Tarea

DATA_FILE = f"data/tasks_{date.today().isoformat()}.json"


class TaskManager:
    def __init__(self, vikunja_api, local_db):
        self.vikunja_api = vikunja_api
        self.local_db = local_db
        self.tareas = []
        self.current_task = None
        self.data_file = DATA_FILE
        
    def load_tasks(self):
        """Carga tareas desde JSON"""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.tareas = [Tarea.from_dict(d) for d in data]
                
    def save_tasks(self, new_task=None):
        """
        Guarda las tareas a JSON y opcionalmente agrega una nueva.
        Args:
            new_task (dict, optional): Datos para crear nueva tarea
        Returns:
            Tarea: La nueva tarea creada (si se proporcionó new_task)
        """
        if new_task:
            task = Tarea(**new_task)
            self.tareas.append(task)

        os.makedirs("data", exist_ok=True)
        data = [t.to_dict() for t in self.tareas]
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        return task if new_task else None
                    
    def delete_task(self, task_name):
        """Elimina tarea por nombre"""
        self.tareas = [t for t in self.tareas if t.nombre != task_name]
        self.save_tasks()
        
    def get_statistics(self):
        """Retorna estadísticas de tareas"""
        return {
            'total': len(self.tareas),
            'completed': sum(1 for t in self.tareas if t.completada),
            'difficulty': sum(t.dificultad_total for t in self.tareas),
            'estimated_time': sum(t.tiempo_estimado for t in self.tareas),
            'real_time': sum(t.tiempo_real for t in self.tareas)
        }

    def create_task(self, task_data):
        """
        Crea una nueva tarea con los datos proporcionados
        Args:
            task_data (dict): Datos de la tarea
        Returns:
            Tarea: La tarea creada
        """
        return self.save_tasks(new_task=task_data)

    def complete_task(self, task_name):
        """Marca una tarea como completada por nombre"""
        for task in self.tareas:
            if task.nombre == task_name:
                task.completada = True
                self.save_tasks()
                return True
        return False
        
    def get_task(self, task_name):
        """Obtiene una tarea por nombre"""
        for task in self.tareas:
            if task.nombre == task_name:
                return task
        return None
    
#--------------------- Funciones de tiempo ---------------------
    def start_timer(self, task_name):
        """Inicia el temporizador de una tarea"""
        task = self.get_task(task_name)
        if task and not task.timer_running:
            task.start_timer()
            return True
        return False
    
    def stop_timer(self, task_name):
        """Detiene el temporizador de una tarea"""
        task = self.get_task(task_name)
        if task and task.timer_running:
            task.stop_timer()
            self.save_tasks()
            return True
        return False

# # ------------------ Sincronización con DB ------------------
#     def sync_to_db(self, dt):
#         """
#         Se llama cada X segundos (ej. 60).
#         Recorre 'self.tareas' y las guarda/actualiza en la DB local.
#         """
#         # Aquí puedes implementar la lógica: 
#         # 1) Checar si la tarea ya existe en DB (por título o ID).
#         # 2) Insertar o actualizar según haga falta.
#         # 3) (Opcional) Podrías también leer la DB para tareas que no estén en self.tareas.

#         for t in self.tareas:
#             # Ejemplo: check si existe por 'title'
#             # Para simplificar, supongamos que no existe y la insertamos.
#             # Ojo: en un caso real, necesitarías un get_task_by_title(t.nombre) etc.
#             self.local_db.add_task(
#                 vikunja_task_id=None,
#                 title=t.nombre,
#                 description="",  # o t.algunaDescripcion
#                 knowledge=t.conocimiento,
#                 resources=t.recursos,
#                 dependency=t.dependencia,
#                 stress=t.estres,
#                 risk=t.riesgo,
#                 estimated_time=t.tiempo_estimado,
#                 difficulty=t.dificultad_total
#             )
#         # Si quisieras evitar duplicados, primero buscarías en DB y harías update.
#         # Pero esto te muestra la idea general.

#         # Mensaje rápido en consola o UI para saber que se sincronizó
#         print("[sync_to_db] Se han sincronizado las tareas con la DB.")
#         # O un Snackbar:
#         # Snackbar(text="Sincronizado con DB").open()

        
#     def create_task(self, instance):
#         """
#         Lógica para crear una tarea en Vikunja (y opcionalmente guardarla
#         en la DB local).
#         """
#         title = self.task_input.text.strip()
#         desc = self.desc_input.text.strip()
#         selected_list = self.spinner.text

#         if not title:
#             self.info_label.text = "El título no puede estar vacío."
#             return

#         # Aquí podrías obtener la ID real de la lista (proyecto) desde Vikunja.
#         # Por ejemplo, si 'Mi Lista 1' corresponde a ID=123, etc.
#         # new_task = self.vikunja_api.create_task(list_id=123, title=title, description=desc)

#         # Si se crea exitosamente:
#         self.info_label.text = f"Tarea '{title}' creada en la lista '{selected_list}'."
#         self.task_input.text = ""
#         self.desc_input.text = ""

#         # También podrías guardar en local_db:
#         # self.local_db.add_task(...)

#         # O refrescar la lista de tareas, etc.
