# Gestión de Tareas con Temporizador 🕒

## Tabla de Contenidos

- [Descripción](#descripción)
- [Características](#características)
- [Arquitectura General](#arquitectura-general)
- [Preparar el Entorno de Vikunja](#preparar-el-entorno-de-vikunja)
- [Estructura y Funcionalidades de la App](#estructura-y-funcionalidades-de-la-app)

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





## 1. Arquitectura General

### **Frontend (Kivy):**
- Desarrollado con **Python** + **Kivy**.
- Funcionalidades principales:
  - Mostrar, añadir, editar y eliminar tareas.
  - Calcular métricas como dificultad, estrés, tiempo estimado, etc.
- Se conecta a la API de **Vikunja** para interactuar con las tareas y listas (proyectos).

### **Backend (Vikunja):**
- **Vikunja** proporciona:
  - Un backend escrito en Go con una API REST documentada.
  - Manejo de usuarios, autenticación, proyectos y tareas.
  - Soporte para bases de datos como **MySQL**, **PostgreSQL** y **SQLite**.
- Opcionalmente puedes personalizar algunos aspectos del backend.

### **Hosting / Infraestructura:**
- Puedes desplegar Vikunja en:
  - Un servidor propio.
  - Plataformas como Docker, Heroku, Render, o un VPS.
- La app Kivy puede conectarse a una instancia local de Vikunja (desarrollo) o remota (producción).
- **Nota:** La sincronización y colaboración se manejan desde Vikunja, mientras que la app Kivy se enfoca en la experiencia de usuario (UX) y cálculos de métricas.

---

## 2. Preparar el Entorno de Vikunja

### **1. Descargar e Instalar Vikunja:**
- Sigue la [documentación oficial de Vikunja](https://vikunja.io/docs/installation/) para la instalación.
- Elige tu base de datos preferida: **MySQL**, **PostgreSQL**, o **SQLite**.
- Arranca el backend de Vikunja en tu entorno local o en un servidor.

### **2. Configurar Vikunja:**
- Asegúrate de que la API esté accesible en: `http://localhost:3456` (puerto por defecto).
- Crea un usuario de prueba para desarrollo.

### **3. Probar la API:**
- Usa herramientas como **Postman** o **cURL** para validar las operaciones de la API.
- Revisa la [API Reference de Vikunja](https://vikunja.io/api/) para entender los endpoints y parámetros disponibles.

---

## 3. Estructura y Funcionalidades de la App

### **Pantalla de Login**
- Permite al usuario autenticarse con las credenciales de Vikunja.
- Almacena el token o sesión para futuras peticiones.

### **Pantalla Principal / Listado de Tareas**
- Listar proyectos o listas (llamados "namespaces" o "lists" en Vikunja).
- Mostrar tareas que provienen de la API.
- Botones para **Crear**, **Editar** y **Eliminar** tareas.

### **Pantalla o Diálogo de Crear/Editar Tareas**
- Campos básicos:
  - Nombre, descripción, fecha límite.
- Campos adicionales para métricas: 
  - Conocimiento, recursos, dependencia, estrés, riesgo, tiempo estimado.
- Opciones para manejar estos campos:
  - Usar **labels** en Vikunja.
  - Almacenar datos en el campo descripción (por ejemplo, en formato JSON embebido).
  - Registrar localmente en un "mini DB" para sincronizar lo esencial con Vikunja.

### **Pantalla de Métricas / Reportes**
- Mostrar métricas como:
  - Dificultad total, riesgo, estrés.
- Filtrar tareas según prioridad o métricas.
- Sincronizar datos con Vikunja o una base de datos local.

### **Pantalla de Ajustes**
- Configurar:
  - URL del servidor de Vikunja.
  - Credenciales del usuario.
  - Otros parámetros necesarios.

---

## Notas Finales
- Este proyecto utiliza **Vikunja** para manejar la sincronización de tareas y colaboración.
- La app Kivy está enfocada en la **interacción con el usuario** y **cálculos personalizados**.
- Puedes personalizar tanto el backend como la app según tus necesidades.

---

## Recursos
- [Documentación de Vikunja](https://vikunja.io/docs/)
- [Referencia de la API de Vikunja](https://vikunja.io/api/)
- [Kivy Documentation](https://kivy.org/doc/stable/)
