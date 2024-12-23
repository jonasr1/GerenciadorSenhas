import string, secrets
import hashlib
import base64
from pathlib import Path
from typing import Union
from cryptography.fernet import Fernet, InvalidToken

class FernetHasher:
    RANDOM_STRING_CHARS = string.ascii_letters  # Contém todas as letras minúsculas e maiúsculas do alfabeto (a-z, A-Z)
    BASE_DIR = Path(__file__).resolve().parent.parent
    KEY_DIR = BASE_DIR / 'keys'

    def __init__(self, key: str):
        """
        Inicializa o FernetHasher com uma chave.
        
        Args:
            key (Union[str, bytes, bytearray, memoryview]): Chave de criptografia
        """
        if isinstance(key, (bytes, bytearray, memoryview)):
            key_bytes = bytes(key)
        else:
            key_bytes = key.encode()
        try:
            self.fernet = Fernet(key_bytes)
        except Exception as e:
            raise ValueError("Chave de criptografia inválida") from e

    @classmethod
    def _get_random_string(cls, length: int = 25) -> str:
        return ''.join(secrets.choice(cls.RANDOM_STRING_CHARS) for _ in range(length))

    @classmethod
    def create_key(cls, archive: bool = False):
        """
        Args:
            archive (bool): Se `True`, salva a chave em um arquivo no diretório `keys`.
                            Caso contrário, a chave é apenas retornada sem ser armazenada.
        Returns:
            tuple: Retorna uma tupla com a chave gerada (`bytes`) e o caminho do arquivo (`Path`) onde a chave foi arquivada,
                    ou `None` se `archive` for `False`.
        """
        value = cls._get_random_string()
        hasher = hashlib.sha256(value.encode('utf-8')).digest()
        key = base64.b64encode(hasher)
        if archive:
            return key, cls.archive_key(key)
        return key, None

    @classmethod
    def archive_key(cls, key: bytes) -> Path:
        file = 'key.key'
        while Path(cls.KEY_DIR / file).exists():
            file = f'key_{cls._get_random_string(5)}.key'
        with open(cls.KEY_DIR / file, 'wb') as arq:
            arq.write(key)
        return cls.BASE_DIR / file

    def encrypt(self, value: Union[str, bytes]) -> bytes:
        if isinstance(value, str):
            value = value.encode()
        return self.fernet.encrypt(value)

    def decrypt(self, value: Union[str, bytes]) -> str:
        if isinstance(value, str):
            value = value.encode()
        try:
            return self.fernet.decrypt(value).decode()
        except InvalidToken:
            return 'Token inválido'

