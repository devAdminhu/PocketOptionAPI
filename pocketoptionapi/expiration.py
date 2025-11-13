"""
Utilitários para manipulação de datas e timestamps.
"""
import time
from datetime import datetime, timedelta

def date_to_timestamp(date):
    """Converte um objeto datetime para timestamp."""
    return int(date.timestamp())

def get_expiration_time(timestamp, duration):
    """
    Calcula o tempo de expiração mais próximo baseado em um timestamp dado e uma duração.
    O tempo de expiração sempre terminará no segundo :30 do minuto.

    :param timestamp: O timestamp inicial para o cálculo.
    :param duration: A duração desejada em minutos.
    """
    # Converter o timestamp dado para um objeto datetime
    now_date = datetime.fromtimestamp(timestamp)

    # Ajustar os segundos para :30 se não estiverem já, caso contrário, passar para o próximo :30
    if now_date.second < 30:
        exp_date = now_date.replace(second=30, microsecond=0)
    else:
        exp_date = (now_date + timedelta(minutes=1)).replace(second=30, microsecond=0)

    # Calcular o tempo de expiração considerando a duração
    if duration > 1:
        # Se a duração for mais de um minuto, calcular o tempo final adicionando a duração
        # menos um minuto, já que já ajustamos para terminar em :30 segundos.
        exp_date += timedelta(minutes=duration - 1)

    # Adicionar duas horas ao tempo de expiração
    exp_date += timedelta(hours=2)
    # Converter o tempo de expiração para timestamp
    expiration_timestamp = date_to_timestamp(exp_date)

    return expiration_timestamp

def get_remaning_time(timestamp):
    """
    Calcula os tempos de expiração restantes.
    
    :param timestamp: O timestamp inicial para o cálculo.
    :return: Lista de tuplas com (duração, tempo restante).
    """
    now_date = datetime.fromtimestamp(timestamp)
    exp_date = now_date.replace(second=0, microsecond=0)
    if (int(date_to_timestamp(exp_date+timedelta(minutes=1)))-timestamp) > 30:
        exp_date = exp_date+timedelta(minutes=1)
    else:
        exp_date = exp_date+timedelta(minutes=2)
    
    exp = []
    for _ in range(5):
        exp.append(date_to_timestamp(exp_date))
        exp_date = exp_date+timedelta(minutes=1)
    
    idx = 11
    index = 0
    now_date = datetime.fromtimestamp(timestamp)
    exp_date = now_date.replace(second=0, microsecond=0)
    
    while index < idx:
        if int(exp_date.strftime("%M")) % 15 == 0 and (int(date_to_timestamp(exp_date))-int(timestamp)) > 60*5:
            exp.append(date_to_timestamp(exp_date))
            index = index+1
        exp_date = exp_date+timedelta(minutes=1)

    remaning = []

    for idx, t in enumerate(exp):
        if idx >= 5:
            dr = 15*(idx-4)
        else:
            dr = idx+1
        remaning.append((dr, int(t)-int(time.time())))

    return remaning