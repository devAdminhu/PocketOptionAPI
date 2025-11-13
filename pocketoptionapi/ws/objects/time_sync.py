"""
Módulo para sincronização de tempo com o servidor da PocketOption.
Fornece funcionalidades para manter o tempo local sincronizado com o servidor.
"""
from datetime import datetime, timezone

class TimeSynchronizer:
    def __init__(self):
        self.server_time_reference = None
        self.local_time_reference = None

    def synchronize(self, server_timestamp):
        """
        Sincroniza o tempo local com o timestamp do servidor.
        
        :param server_timestamp: O timestamp do servidor em segundos.
        """
        self.server_time_reference = server_timestamp
        self.local_time_reference = datetime.now(timezone.utc).timestamp()

    def get_synced_datetime(self):
        """
        Retorna o datetime atual sincronizado com o servidor.
        
        :return: Um objeto datetime sincronizado com o servidor.
        :raises ValueError: Se o tempo não foi sincronizado ainda.
        """
        if self.server_time_reference is None or self.local_time_reference is None:
            raise ValueError("O tempo ainda não foi sincronizado.")

        # Calcula o tempo decorrido desde a última sincronização
        time_elapsed = datetime.now(timezone.utc).timestamp() - self.local_time_reference

        # Ajusta o timestamp do servidor com o tempo decorrido
        synced_timestamp = self.server_time_reference + time_elapsed

        # Converte para datetime
        return datetime.fromtimestamp(synced_timestamp, timezone.utc)
