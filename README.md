# Carcassone web
Juego web desarrollado en python 3.6 con django 2.1.4

## Instalacion
Intalar python3.x y virtualenv  
`sudo apt install python3 virtualenv`   
Clonar el repositorio:  
`git clone https://gitlab.com/cristiancontrera95/carcassonne.git`   
Moverse dentro de la carpeta */carcassonne*, crear un entorno virtual y activarlo:
`virtualenv venv -p python3`    
`. venv/bin/activate`   
Instalar las librerias requeridas   
`pip install -r requeriments.txt`   
Correr el script migrate.sh     
`./migrate.sh`  
Correr el servidor  
`python manage.py runserver`    
Acceder al juego desde un navegador web     
http://127.0.0.1:8000/   


