# Gestión de Tareas con Temporizador 🕒

## Tabla de Contenidos

- [Descripción](#descripción)
- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)

## Deescripción
Esta aplicación está diseñada para evaluar el nivel de dificultad de una 
tarea junto con la energía invertida en realizarla. Su objetivo es ayudar 
a optimizar el trabajo al identificar posibles obstáculos y priorizar las 
tareas de manera eficiente. Al responder las preguntas proporcionadas, 
los usuarios pueden analizar mejor sus recursos y estrategias para 
minimizar el estrés y los errores mientras maximizan la productividad.

## Características
- Registro de tareas con atributos como conocimiento, recursos, y riesgo.
- Temporizador para medir el tiempo invertido en cada tarea.
- Cálculo de dificultad total y eficiencia.
- Guardado automático de tareas en un archivo JSON.
- Interfaz gráfica sencilla y funcional con `Tkinter`.

- Tiempo estimado: ¿Cuánto tiempo crees que te tomará completar la tarea?
- Conocimiento especializado: ¿Requieres habilidades o conocimientos especí
ficos que aún no dominas al 100%?
- Recursos necesarios: ¿La tarea implica coordinación de recursos humanos, 
materiales o tecnológicos que no tienes a mano?
- Dependencias: ¿La finalización de la tarea depende de otras personas, 
equipos o tareas previas?
- Nivel de estrés o presión: ¿Es una tarea que, por su importancia o urgencia,
 te genera mayor ansiedad o presión?
- Riesgos o posibilidad de error: ¿Implica un riesgo alto de que tengas que 
repetir parte del trabajo si algo sale mal?


## Requisitos
- Python 3.8 o superior
- Bibliotecas: 
  - `tkinter` (incluido con Python)
  - `json`
- Sistema operativo: Windows, macOS o Linux


## Instalación
1. Clona este repositorio:
   ```bash
   git clone https://github.com/usuario/gestion-tareas.git

2. cd Gestor  de Tareas
3. pip install -r requirements.txt
4. python src/main.py