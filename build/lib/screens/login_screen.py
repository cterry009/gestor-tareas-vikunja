# screens/login_screen.py (versión KivyMD)
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder

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

class LoginScreen(MDScreen):
    def __init__(self, vikunja_api, **kwargs):
        Builder.load_string(login_kv)
        super().__init__(**kwargs)
        self.vikunja_api = vikunja_api
    
    def do_login(self):
        username = self.ids.username_field.text
        password = self.ids.password_field.text
        success = self.vikunja_api.login(username, password)
        if success:
            self.ids.status_label.text = "Login exitoso"
            self.manager.current = "task_screen"
        else:
            self.ids.status_label.text = "Error en credenciales"
