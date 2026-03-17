import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'segredo_muito_secreto_e_aleatorio')
    DATABASE = 'database.db'
    DIAS_SEMANA = [
        "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"
    ]
    SERVICOS_PADRAO = [
        "Corte", "Barba", "Corte + Barba", "Sobrancelha", "Acabamento"
    ]
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', '19992785209') # Em produção, use um nome de usuário mais seguro!
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "12345678") # Em produção, use senhas hashed!
    BARBER_WHATSAPP_NUMBER = os.environ.get("BARBER_WHATSAPP_NUMBER", "5519992785209") # Número do barbeiro com código do país e DDD
