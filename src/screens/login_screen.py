# screens/login_screen.py (versión KivyMD)
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
import logging

# Configuración del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

# Declaramos el layout en kv language (recomendado para KivyMD)
login_kv = '''
<LoginScreen>:
    MDBoxLayout:
        orientation: "vertical"
        spacing: "24dp"
        padding: "24dp"
        
        MDLabel:
            text: "Iniciar Sesión"
            halign: "center"
            font_style: "H4"
        
        MDTextField:
            id: username_field
            hint_text: "Usuario de Vikunja"
            helper_text: "Ingresa tu usuario"
            helper_text_mode: "on_focus"
            icon_right: "account"
        
        MDTextField:
            id: password_field
            hint_text: "Contraseña"
            helper_text: "Ingresa tu contraseña"
            helper_text_mode: "on_focus"
            icon_right: "lock"
            password: True
        
        MDRaisedButton:
            text: "Login"
            pos_hint: {"center_x": 0.5}
            on_release: root.do_login()
        
        MDLabel:
            id: status_label
            text: ""
            halign: "center"
            theme_text_color: "Error"
'''

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LoginScreen(MDScreen):
    def __init__(self, vikunja_api, **kwargs):
        Builder.load_string(login_kv)
        super().__init__(**kwargs)
        self.vikunja_api = vikunja_api
    def do_login(self):
        try:
            username = self.ids.username_field.text
            password = self.ids.password_field.text
            
            if not username or not password:
                self.update_status("Usuario y contraseña son requeridos", "error")
                return
            
            success = self.vikunja_api.login(username, password)
            
            if success:
                self.update_status("Login exitoso", "success")
                self.manager.current = "task_screen"
            else:
                self.update_status("Credenciales inválidas", "error")
                
        except Exception as e:
            self.update_status(f"Error de conexión: {str(e)}", "error")

    def update_status(self, message, status_type="info"):
        """Update status label with message and appropriate color"""
        self.ids.status_label.text = message
        if status_type == "error":
            self.ids.status_label.theme_text_color = "Error"
        elif status_type == "success":
            self.ids.status_label.theme_text_color = "Custom"
            self.ids.status_label.text_color = (0, 1, 0, 1)  # RGBA => verde
        else:
            self.ids.status_label.theme_text_color = "Primary"