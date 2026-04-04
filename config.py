import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'segredo_muito_secreto_e_aleatorio')
    DATABASE = 'database.db'
    DIAS_SEMANA = [
        "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"
    ]

    # Nova estrutura para horários pré-programados por dia da semana
    # Formato: {"Dia da Semana": [("HH:MM_inicio", "HH:MM_fim"), ...]}
    # Exemplo: {"Segunda": [("09:00", "12:00"), ("14:00", "18:00")]}
    HORARIOS_POR_DIA = {
        "Segunda": [("18:00", "20:00")],
        "Terça": [("18:00", "20:00")],
        "Quarta": [("18:00", "20:00")],
        "Quinta": [("18:00", "20:00")],
        "Sexta": [("18:00", "20:00")], # Exemplo de mais de um bloco
        "Sábado": [("07:00", "16:30")],
        "Domingo": [] # Fechado ou sem horários pré-definidos
    }
    SERVICOS_PADRAO = [
        "Corte Degradê R$30,00", "Corte Social R$30,00", "Barba Completa R$20,00", "Barba Desenho R$15,00", "Corte + Barba R$45,00", "Sobrancelha R$5,00", "Corte + Barba + Sobrancelha R$50,00", "Pesinho R$10,00"
    ]
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', '19992785209')
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "12345678") # Em produção, use senhas hashed!
    BARBER_WHATSAPP_NUMBER = os.environ.get("BARBER_WHATSAPP_NUMBER", "5519992785209") # Número do barbeiro com código do país e DDD