"""
Autor: AdminhuDev
"""
from pocketoptionapi.ws.objects.base import Base


class Candles(Base):
    """Classe para representar velas financeiras."""

    def __init__(self):
        super(Candles, self).__init__()
        self.__name = "candles"
        self.__candles_data = None

    @property
    def candles_data(self):
        """Propriedade para obter dados das velas.

        :returns: Os dados das velas.
        """
        return self.__candles_data

    @candles_data.setter
    def candles_data(self, candles_data):
        """Método para definir dados das velas.

        :param candles_data: Os dados das velas para definir.
        """
        self.__candles_data = candles_data

    @property
    def candle_open(self):
        """Propriedade para obter o valor de abertura da vela.

        :returns: O valor de abertura da vela.
        """
        return self.candles_data.candle_open

    @property
    def candle_close(self):
        """Propriedade para obter o valor de fechamento da vela.

        :returns: O valor de fechamento da vela.
        """
        return self.candles_data.candle_close

    @property
    def candle_high(self):
        """Propriedade para obter o valor máximo da vela.

        :returns: O valor máximo da vela.
        """
        return self.candles_data.candle_high

    @property
    def candle_low(self):
        """Propriedade para obter o valor mínimo da vela.

        :returns: O valor mínimo da vela.
        """
        return self.candles_data.candle_low

    @property
    def candle_time(self):
        """Propriedade para obter o tempo da vela.

        :returns: O tempo da vela.
        """
        return self.candles_data.candle_time

    def get_candles(self, active_id, period):
        """Método para obter velas.

        :param active_id: O ID do ativo.
        :param period: O período das velas.
        """
        self.send_websocket_request(self.name, {"active_id": active_id,
                                              "period": period,
                                              "count": 100})

    def get_candles_v2(self, active_id, period, count, endtime):
        """Método para obter velas (versão 2).

        :param active_id: O ID do ativo.
        :param period: O período das velas.
        :param count: A quantidade de velas.
        :param endtime: O tempo final.
        """
        self.send_websocket_request(self.name, {"active_id": active_id,
                                              "period": period,
                                              "count": count,
                                              "endtime": endtime})

    def get_candles_from_to_time(self, active_id, period, from_time, to_time):
        """Método para obter velas de um período específico.

        :param active_id: O ID do ativo.
        :param period: O período das velas.
        :param from_time: O tempo inicial.
        :param to_time: O tempo final.
        """
        self.send_websocket_request(self.name, {"active_id": active_id,
                                              "period": period,
                                              "from": from_time,
                                              "to": to_time})
