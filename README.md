# OpenGL-2022
 Progetto di Grafica 3D in Python - ISIS Andrea Ponti 2022

1. scaricare python dal sito web https://www.python.org/ oppure, se si è sul Sistema Operativo windows, dal Microsoft Store.
si suggerisce di scaricare anche l'applicativo "Terminale Windows", ma non è essenziale ai fini del corso.

2. creare sul proprio sistema una directory per il progetto 

3. dal terminale accedere alla directory e creare il virtual environment:
python -m venv venv

4. attivare il venv:
.\venv\Scripts\activate.bat  --OPPURE--  .\venv\Scripts\Activate.ps1
(per disattivarlo: deactivate )

5. Aggiornare pip con:
python -m pip install --upgrade pip

6. Per vedere i pacchetti installati:
pip list

7. Scaricare le librerie necessarie manualmente (oppure utilizzando il punto 9):
installare numpy, pygame, pyglet, PyWavefront, PyGLM (e le altre librerie necessarie)
Dal sito https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyopengl prendere le librerie
PyOpenGL e PyOpenGL_accelerate (cpXX indica la versione di python, e scegliere la versione a 32 o 64 bit in accordo con la versione di python, da vedere con python --version )

8. Una volta installate tutte le librerie, documentare il progetto con:
pip freeze > requirements.txt

9. Per ripristinarlo:
pip install -r requirements.txt

10. Per i modelli usare: https://archive3d.net/
