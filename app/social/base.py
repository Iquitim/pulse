from abc import ABC, abstractmethod

class BaseSocialNetwork(ABC):
    @abstractmethod
    def connect(self) -> bool:
        """
        Estabelece a conexão ou sessão com a rede social.
        Retorna True se for bem sucedido, False caso contrário.
        """
        pass

    @abstractmethod
    def publish(self, content: str) -> dict:
        """
        Publica um post na rede social.
        Retorna um dicionário contendo informações da publicação (status, uri, cid, etc).
        Raises an exception on failure.
        """
        pass

    @abstractmethod
    def check_connection(self) -> bool:
        """
        Verifica se a credencial e a sessão atuais estão válidas.
        """
        pass
