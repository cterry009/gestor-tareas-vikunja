# src/tasks.py
import time

class Tarea:
    def __init__(self, nombre, conocimiento=0, recursos=0, dependencia=0,
                 estres=0, riesgo=0, tiempo_estimado=0, tiempo_real=0, completada=False):
        self.nombre = nombre
        self.conocimiento = float(conocimiento)
        self.recursos = float(recursos)
        self.dependencia = float(dependencia)
        self.estres = float(estres)
        self.riesgo = float(riesgo)
        self.tiempo_estimado = float(tiempo_estimado)
        self.tiempo_real = float(tiempo_real)
        self.completada = completada
        self.dificultad_total = 0.0
        self.calcular_dificultad_total()
        
        self.timer_running = False
        self.start_time = 0.0

#---------------------- Funciones de temporizador ----------------------#
    def iniciar_temporizador(self):
        """Inicia el temporizador de la tarea"""
        if not self.timer_running:
            self.timer_running = True
            self.start_time = time.time()
            return True
        return False
        
    def detener_temporizador(self):
        """Detiene el temporizador y actualiza el tiempo real"""
        if self.timer_running:
            elapsed = time.time() - self.start_time
            self.tiempo_real += round(elapsed / 3600, 3)  # Convertir a horas
            self.timer_running = False
            self.start_time = 0
            return True
        return False
            
    def get_tiempo_transcurrido(self):
        """Obtiene el tiempo transcurrido en segundos"""
        if self.timer_running:
            return int(time.time() - self.start_time)
        return 0

#---------------------- Funciones de dificultad ----------------------#
    def calcular_dificultad_total(self):
        # Ejemplo sencillo
        self.dificultad_total = (self.conocimiento + self.recursos +
                                 self.dependencia + self.estres + self.riesgo)


#---------------------- Funciones para pasar a JSON ----------------------#
    def to_dict(self):
        return {
            "nombre": self.nombre,
            "conocimiento": self.conocimiento,
            "recursos": self.recursos,
            "dependencia": self.dependencia,
            "estres": self.estres,
            "riesgo": self.riesgo,
            "dificultad_total": self.dificultad_total,
            "tiempo_estimado": self.tiempo_estimado,
            "tiempo_real": self.tiempo_real,
            "completada": self.completada,
        }

    @classmethod
    def from_dict(cls, data):
        """Crea una instancia de Tarea desde un diccionario"""
        return cls(
            nombre=data["nombre"],
            conocimiento=data["conocimiento"],
            recursos=data["recursos"],
            dependencia=data["dependencia"],
            estres=data["estres"],
            riesgo=data["riesgo"],
            tiempo_estimado=data["tiempo_estimado"],
            tiempo_real=data.get("tiempo_real", 0.0),
            completada=data["completada"]
        )
