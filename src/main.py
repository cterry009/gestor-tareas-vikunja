# Importaciones estándar
import os
import sys
import time
import subprocess
from threading import Thread
from time import sleep
from kivy.config import Config

# Establecer KIVY_NO_ARGS antes de importar el resto de Kivy
os.environ['KIVY_NO_ARGS'] = '1'

# Configurar dimensiones de la ventana
Config.set('graphics', 'width', '1300')
Config.set('graphics', 'height', '600')

# Importaciones de terceros
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager

# Importaciones locales
from config_loader import load_config
from screens.login_screen import LoginScreen
from screens.task_screen import TaskScreen
from api.vikunja_api import VikunjaAPI
from db.local_db import LocalDB
from utils.logger import AppLogger

logger = AppLogger.get_logger()

class ReloadHandler(FileSystemEventHandler):
    """
    Handler que se ejecuta cuando un archivo cambia.
    """
    def __init__(self, app_instance):
        super().__init__()
        self.app_instance = app_instance
        self.last_modified = 0
        self.cooldown = 1  # segundos entre reinicios

    def on_modified(self, event):
        if not self.app_instance.auto_reload:
            return
            
        current_time = time.time()
        if current_time - self.last_modified < self.cooldown:
            return
        
        if event.src_path.endswith(".py"):
            self.last_modified = current_time
            logger.info(f"Archivo modificado: {event.src_path}")
            logger.info("Reiniciando aplicación...")
            
            try:
                # Obtener la ruta absoluta del script principal
                main_script = os.path.abspath(sys.argv[0])
                
                # Asegurarse de mantener los argumentos de desarrollo
                args = []
                if self.app_instance.dev_mode:
                    args.append('--dev')
                if self.app_instance.auto_reload:
                    args.append('--reload')
                
                # Crear un nuevo proceso con los argumentos preservados
                cmd = [sys.executable, main_script] + args
                
            except Exception as e:
                logger.error(f"Error al reiniciar: {e}")

class MyKivyVikunjaApp(MDApp):
    def __init__(self, **kwargs):
        # Establecer valores por defecto
        self.dev_mode = False
        self.auto_reload = False  # Por defecto desactivado
        
        # Extraer argumentos propios
        try:
            args = sys.argv[:]  # Hacer una copia de los argumentos
            logger.info("Argumentos disponibles:")
            logger.info("  --dev          : Activa el modo desarrollo")
            logger.info("  --reload       : Activa el auto-reload")
            logger.info(f"Argumentos recibidos: {args}")
            
            # Procesar argumentos propios
            self.dev_mode = '--dev' in args
            self.auto_reload = '--reload' in args
            
            logger.info(f"Modo desarrollo: {'activado' if self.dev_mode else 'desactivado'}")
            logger.info(f"Auto-reload: {'activado' if self.auto_reload else 'desactivado'}")
   
        except Exception as e:
            logger.error(f"Error procesando argumentos: {str(e)}")
        
        super().__init__(**kwargs)

    def on_start(self):
        """Se llama cuando la aplicación ha iniciado"""
        logger.info(f"\nEstado de la aplicación:")
        logger.info(f"Modo desarrollo: {'activado' if self.dev_mode else 'desactivado'}")
        logger.info(f"Auto-reload: {'activado' if self.auto_reload else 'desactivado'}")
        
    def toggle_auto_reload(self):
        """Activa/desactiva el auto-reinicio"""
        self.auto_reload = not self.auto_reload
        logger.error(f"Auto-reload {'activado' if self.auto_reload else 'desactivado'}")
        
    def build(self):
        # logger.info(f"Directorio actual: {os.getcwd()}")
        # logger.info(f"Ruta del script: {sys.argv[0]}")
        # logger.info(f"Python executable: {sys.executable}")
        
        # Iniciar el observador en un hilo separado
        Thread(target=self.start_watchdog).start()

        # Cargar la configuración
        config = load_config("config/config.yaml")  # Ruta por defecto u otra

        api_url = config['vikunja']['api_url']
        db_name = config['database']['name']
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # Instanciamos la API de Vikunja
        vikunja_api = VikunjaAPI(base_url=api_url)
        # Instanciamos la DB local, si la usamos
        local_db = LocalDB(db_name=db_name)

        sm = ScreenManager()

        # Creamos pantallas
        login_screen = LoginScreen(vikunja_api, name="login_screen")
        task_screen = TaskScreen(vikunja_api, local_db, name="task_screen")

        sm.add_widget(login_screen)
        sm.add_widget(task_screen)

        # Si estamos en modo desarrollo, cargar configuración adicional
        if self.dev_mode:
            dev_config = load_config("config/dev_config.yaml")
            self.dev_credentials = dev_config.get('development', {}).get('credentials', {})
        
        # Modificar la pantalla inicial según el modo
        if self.dev_mode and dev_config.get('development', {}).get('auto_login', False):
            sm.current = "task_screen"
            # Auto-login en segundo plano
            Thread(target=self._auto_login, args=(vikunja_api,)).start()
        else:
            sm.current = "login_screen"
            
        return sm

    def _auto_login(self, api):
        """Realiza el login automático en segundo plano"""
        try:
            api.login(
                self.dev_credentials.get('username'),
                self.dev_credentials.get('password')
            )
        except Exception as e:
            logger.error(f"Auto-login failed: {e}")

    def start_watchdog(self):
        """
        Configura y ejecuta el observador para monitorear cambios en archivos Python.
        """
        try:
            # Obtener la ruta del directorio src
            base_path = os.path.dirname(os.path.abspath(__file__))
            logger.info(f"Monitoring directory: {base_path}")
            
            event_handler = ReloadHandler(self)
            observer = Observer()
            observer.schedule(event_handler, base_path, recursive=True)
            observer.start()
            
            while True:
                sleep(1)
        except Exception as e:
            logger.error(f"Error en watchdog: {e}")
        finally:
            if 'observer' in locals():
                observer.stop()
                observer.join()


if __name__ == "__main__":
    app = MyKivyVikunjaApp()
    app.run()
