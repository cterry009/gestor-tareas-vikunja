# Nombre del archivo donde se guardarán las tareas
DATA_FILE = 'tareas.json'

class Tarea:
    
    """
    Clase para representar una tarea.
    
    Esta clase proporciona un método para convertir la tarea a un diccionario
    y otro método para crear una tarea a partir de un diccionario.
    
    Atributos:
        nombre (str): Nombre de la tarea.
        recursos (int): Nivel de recursos requeridos.
        dependencia (int): Nivel de dependencia de otras tareas u otras personas.
        estres (int): Nivel de estrés que genera la tarea.
        riesgo (int): Nivel de riesgo asociado a la tarea.
        dificultad_total (int): Nivel de dificultad total de la tarea.
        energia (int): Nivel de energía requerido para la tarea (1-5).
        tiempo_estimado (float): Tiempo estimado en horas para completar la tarea.
        tiempo_real (float): Tiempo real en horas que ha tomado completar la tarea.
    """
    def __init__(self, nombre, conocimiento=0, recursos=0, dependencia=0, estres=0, riesgo=0,
                 energia=0, tiempo_estimado=0):
        """
        Incializa una nueva tarea con los atributos especificados.

    """
        self.nombre = nombre # Nombre de la tarea
        
        # Nivel de dificultad 
        self.conocimiento = conocimiento
        self.recursos = recursos
        self.dependencia = dependencia
        self.estres = estres
        self.riesgo = riesgo
        self.dificultad_total = 0  # Nivel de dificultad total
        
        self.energia = energia # Nivel de energía requerido (subjetivo)
        self.tiempo_estimado = tiempo_estimado # Tiempo estimado 
        self.tiempo_real = 0  # Para registrar el tiempo real con el temporizador

    def calcular_dificultad_total(self):
        """Calcula la dificultad total como la suma de los criterios."""
        self.dificultad_total = self.conocimiento #+ self.recursos + self.dependencia + self.estres + self.riesgo


    def to_dict(self):
        """
        Convierte la tarea a un diccionario.

        Returns:
            dict: Diccionario con los atributos de la tarea
        """
        return {
            'nombre': self.nombre,
            'conocimiento': self.conocimiento,
            'recursos': self.recursos,
            'dependencia': self.dependencia,
            'estres': self.estres,
            'riesgo': self.riesgo,
            'dificultad_total': self.dificultad_total,
            'energia': self.energia,
            'tiempo_estimado': self.tiempo_estimado,
            'tiempo_real': self.tiempo_real
        }

    @staticmethod
    def from_dict(data):
        t = Tarea(
            data['nombre'], 
            data.get('conocimiento', 0), 
            data.get('recursos', 0),
            data.get('dependencia', 0),
            data.get('estres', 0),
            data.get('riesgo', 0),
            data.get('energia', 0),
            data.get('tiempo_estimado', 0),
        )
        t.tiempo_real = data.get('tiempo_real', 0)
        return t
