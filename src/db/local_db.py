# local_db.py
import sqlite3
from typing import Optional, List, Tuple

from config_loader import load_config
# Cargar la configuración
config = load_config("config/config.yaml")

db_name = config['database']['name']

class LocalDB:
    def __init__(self, db_name=db_name):
        self.db_name = db_name
        self._create_tables()
        # OPCIONAL: crear índice único en 'title' para reforzar la no-duplicación
        self._create_unique_index_on_title()

    def _create_tables(self):
        """
        Crea la tabla principal de tareas si no existe.
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                local_id INTEGER PRIMARY KEY AUTOINCREMENT,
                vikunja_task_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                knowledge INTEGER DEFAULT 0,
                resources INTEGER DEFAULT 0,
                dependency INTEGER DEFAULT 0,
                stress INTEGER DEFAULT 0,
                risk INTEGER DEFAULT 0,
                estimated_time REAL DEFAULT 0,
                difficulty REAL DEFAULT 0,
                time_real REAL DEFAULT 0,
                completed BOOLEAN DEFAULT 0,
                local_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def _create_unique_index_on_title(self):
        """
        Crea un índice único para 'title' a fin de evitar duplicados.
        (Si no quieres forzar la unicidad a nivel DB, comenta este método.)
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        try:
            c.execute("CREATE UNIQUE INDEX idx_unique_title ON tasks (title)")
            conn.commit()
        except sqlite3.OperationalError:
            # Significa que el índice ya existe
            pass
        conn.close()

    # ---------------------------------------------------------------------
    # Métodos CRUD
    # ---------------------------------------------------------------------

    def get_task_by_title(self, title: str):
        """
        Retorna un diccionario con la tarea que coincide con 'title' o None si no existe.
        """
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("SELECT * FROM tasks WHERE title = ?", (title,))
        row = c.fetchone()
        conn.close()
        if row:
            return dict(row)  # convierte Row en dict
        return None

    def add_task(self, 
                 vikunja_task_id: Optional[int],
                 title: str,
                 description: str,
                 knowledge: int,
                 resources: int,
                 dependency: int,
                 stress: int,
                 risk: int,
                 estimated_time: float,
                 difficulty: float,
                 time_real: float = 0.0,
                 completed: bool = False
                ):
        """
        Inserta una tarea nueva. 
        Asume que no hay otra con el mismo 'title' (usar get_task_by_title antes).
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            INSERT INTO tasks
            (vikunja_task_id, title, description, knowledge, resources, dependency,
             stress, risk, estimated_time, difficulty, time_real, completed, local_updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (vikunja_task_id, title, description, knowledge, resources, dependency,
              stress, risk, estimated_time, difficulty, time_real, completed))
        conn.commit()
        conn.close()

    def update_task(self,
                    title: str,
                    description: str,
                    knowledge: int,
                    resources: int,
                    dependency: int,
                    stress: int,
                    risk: int,
                    estimated_time: float,
                    difficulty: float,
                    time_real: float,
                    completed: bool):
        """
        Actualiza la tarea con 'title' dado. 
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            UPDATE tasks
            SET description = ?,
                knowledge = ?,
                resources = ?,
                dependency = ?,
                stress = ?,
                risk = ?,
                estimated_time = ?,
                difficulty = ?,
                time_real = ?,
                completed = ?,
                local_updated_at = CURRENT_TIMESTAMP
            WHERE title = ?
        """, (description, knowledge, resources, dependency, stress, risk,
              estimated_time, difficulty, time_real, completed, title))
        conn.commit()
        conn.close()

    def add_or_update_task(self,
                           vikunja_task_id: Optional[int],
                           title: str,
                           description: str,
                           knowledge: int,
                           resources: int,
                           dependency: int,
                           stress: int,
                           risk: int,
                           estimated_time: float,
                           difficulty: float,
                           time_real: float = 0.0,
                           completed: bool = False):
        """
        Verifica si ya existe una tarea con 'title'.
        - Si no existe, la inserta.
        - Si sí existe, la actualiza (mantiene el 'vikunja_task_id' previo si no lo sobreescribes).
        Evita duplicados en 'title'.
        """
        existing = self.get_task_by_title(title)
        if existing:
            # Ya existe → actualizamos
            # Nota: si deseas mantener el 'vikunja_task_id' anterior, 
            #       podrías rescatarlo de existing. Ej:
            if vikunja_task_id is None:
                vikunja_task_id = existing["vikunja_task_id"]

            # Llamamos a update_task
            self.update_task(
                title=title,
                description=description,
                knowledge=knowledge,
                resources=resources,
                dependency=dependency,
                stress=stress,
                risk=risk,
                estimated_time=estimated_time,
                difficulty=difficulty,
                time_real=time_real if time_real != 0.0 else existing["time_real"],
                completed=completed
            )
        else:
            # No existe → insertamos
            self.add_task(
                vikunja_task_id=vikunja_task_id,
                title=title,
                description=description,
                knowledge=knowledge,
                resources=resources,
                dependency=dependency,
                stress=stress,
                risk=risk,
                estimated_time=estimated_time,
                difficulty=difficulty,
                time_real=time_real,
                completed=completed
            )

    def delete_task_by_title(self, title: str):
        """
        Elimina la tarea cuyo 'title' coincida con el proporcionado.
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE title = ?", (title,))
        conn.commit()
        conn.close()

    def get_all_tasks(self) -> List[dict]:
        """
        Retorna todas las tareas como una lista de dicts.
        """
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM tasks")
        rows = c.fetchall()
        conn.close()

        # Convertir cada row en un dict
        return [dict(r) for r in rows]
