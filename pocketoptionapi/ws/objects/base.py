"""
Autor: AdminhuDev
"""


class Base(object):
    """Classe base para objetos websocket."""
    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.__name = None

    @property
    def name(self):
        """Propriedade para obter o nome do objeto.

        :returns: O nome do objeto.
        """
        return self.__name
