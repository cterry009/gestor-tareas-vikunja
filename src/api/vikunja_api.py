import requests
import time
from utils.logger import AppLogger

class VikunjaAPI:
    def __init__(self, base_url):
        self.logger = AppLogger.get_logger()
        self.base_url = base_url
        self.token = None
        self.username = None
        self.password = None
        self.token_acquired_time = None
        self.token_validity_secs = 3600
        self.logger.info(f"VikunjaAPI initialized with base_url: {base_url}")

    def login(self, username, password):
        """Realiza login en Vikunja y guarda el token."""
        try:
            endpoint = f"{self.base_url}/login"
            self.logger.info(f"Attempting login for user: {username}")
            
            response = requests.post(
                endpoint,
                json={"username": username, "password": password}
            )
            
            # Primero verificamos si el login fue exitoso por el status code
            if response.status_code == 200:
                # El login fue exitoso aunque la respuesta no sea JSON
                self.username = username
                self.password = password
                self.token_acquired_time = time.time()
                self.logger.info(f"Login successful for user: {username}")
                
                # Intentamos obtener el token si hay respuesta JSON
                try:
                    if response.text:
                        response_data = response.json()
                        self.token = response_data.get('token')
                except ValueError:
                    # Si no hay JSON, no es un error crítico
                    self.logger.debug("No JSON response, but login successful")
                    
                return True
            else:
                self.logger.error(f"Login failed with status {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error during login: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during login: {str(e)}")
            return False

    def _get_headers(self):
        """Obtiene los headers para las peticiones."""
        if not self.token:
            self.logger.debug("No token available for request headers")
            return {}
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        # self.logger.debug("Request headers prepared with token")
        return headers

    def _check_token_validity(self):
        """Verifica si el token es válido."""
        if not self.token:
            self.logger.debug("No token present")
            return False
        
        elapsed = time.time() - self.token_acquired_time
        is_valid = elapsed < self.token_validity_secs
        
        if not is_valid:
            self.logger.debug("Token has expired")
        
        return is_valid

    def _ensure_auth(self):
        """Asegura que haya un token válido."""
        try:
            if not self._check_token_validity():
                self.logger.info("Token invalid or expired, attempting re-login")
                if self.username and self.password:
                    login_success = self.login(self.username, self.password)
                    if not login_success:
                        self.logger.error("Re-login failed")
                        raise Exception("Re-login failed")
                else:
                    self.logger.error("No credentials available for re-login")
                    raise Exception("No credentials for re-login")
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            raise

    def _make_request(self, method, endpoint, **kwargs):
        """Método centralizado para hacer requests."""
        try:
            self._ensure_auth()
            url = f"{self.base_url}{endpoint}"
            headers = self._get_headers()
            
            self.logger.debug(f"Making {method} request to: {url}")
            response = requests.request(method, url, headers=headers, **kwargs)
            
            if response.status_code == 401:
                self.logger.warning("Token rejected, attempting one more time")
                self._ensure_auth()
                headers = self._get_headers()
                response = requests.request(method, url, headers=headers, **kwargs)
            
            # self.logger.debug(f"Response status: {response.status_code}")
            return response
            
        except Exception as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise

    # Métodos CRUD
    def get_lists(self):
        """Obtiene todas las listas."""
        try:
            self.logger.info("Fetching all lists")
            response = self._make_request("GET", "/lists")
            if response.status_code == 200:
                lists = response.json()
                self.logger.info(f"Successfully retrieved {len(lists)} lists")
                return lists
            else:
                self.logger.error(f"Failed to get lists: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Error getting lists: {str(e)}")
            return []

    def get_tasks_by_list(self, list_id):
        response = self._make_request("GET", f"/lists/{list_id}/tasks")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[ERROR] get_tasks_by_list: {response.status_code} - {response.text}")
            return []

    def create_task(self, list_id, title, description=""):
        payload = {"title": title, "listId": list_id, "description": description}
        response = self._make_request("POST", "/tasks", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[ERROR] create_task: {response.status_code} - {response.text}")
            return None

    def update_task(self, task_id, data):
        """
        data puede incluir 'title', 'description', 'done', 'dueDate' etc.
        """
        response = self._make_request("PUT", f"/tasks/{task_id}", json=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[ERROR] update_task: {response.status_code} - {response.text}")
            return None

    def delete_task(self, task_id):
        response = self._make_request("DELETE", f"/tasks/{task_id}")
        if response.status_code == 200:
            return True
        else:
            print(f"[ERROR] delete_task: {response.status_code} - {response.text}")
            return False
