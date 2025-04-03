# setup.py
# Los setup son archivos de configuración de Python que permiten empaquetar y distribuir tu código. 
from setuptools import setup, find_packages

# Leer las dependencias desde requirements.txt
with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="gestor_tareas_vikunja",
    version="0.1.0",
    author="Tu Nombre",
    author_email="tu.correo@example.com",
    description="Gestor de tareas basado en Kivy + Vikunja + DB local",
    long_description=open("Readme.txt", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://tusitio.com/gestor-tareas-vikunja",  # o repositorio Git
    packages=find_packages(where="src"),  # asumiendo que tu código está en /src
    package_dir={"": "src"},              # indica que los packages se buscan en "src"
    include_package_data=False,            # para incluir archivos no-Python (si los declaras en MANIFEST.in)
    install_requires=required,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
