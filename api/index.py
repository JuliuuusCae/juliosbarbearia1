# /api/index.py
import sys
import os

# Adiciona o diretório raiz do projeto ao PATH para que app.py possa ser importado
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as application

# O nome 'application' é o que a Vercel espera para o ponto de entrada WSGI
