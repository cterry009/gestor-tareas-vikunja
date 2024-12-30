from tasks import Tarea
from app import Ventana
from config import tk

if __name__ == "__main__":
    root = tk.Tk()
    app = Ventana(root)
    root.mainloop()
