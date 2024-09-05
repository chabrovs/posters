import uuid
import redis
from django.conf import settings
from typing_extensions import Any
from abc import ABC, abstractmethod
from email_service.tasks import send_verification_code_task


# class SingletonMeta(type):
#     _instances = {}

#     def __call__(cls, *args, **kwargs):
#         if not cls._instance:
#             cls._instance[cls] = super().__call__(*args, **kwargs)
#         return cls._instance


class CodeGenerator(ABC):
    @abstractmethod
    def generate_code(self) -> Any:
        """Generate a random secret code."""
        ...


class UUIDGenerator(CodeGenerator):
    def generate_code(self, code_length: int = 6) -> int:
        """Generate code using UUID."""
        return int(str(uuid.uuid4().int)[:code_length])
    

class LateralGenerator(CodeGenerator):
    def generate_code(self, code_length: int = 12) -> Any:
        """Generate lateral code."""
        raise NotImplementedError("Use UUIDGenerator class for now!")


class VerificationEntryHandler(ABC):
    """
    Verification entry is a key value pair where the key is a credential data,
    like (user's email address, phone number, etc), and the value is a generated secret code.
    The verification entry must be stored ofter the secret code generation on the server side,
    in order to be compare and verified with a user's provided secret code.
    """

    @abstractmethod
    def cache_entry(self, credentials: str, code: int | str, ttl: int = 240) -> None:
        """
        Cache entry {user credentials:generated code} to certain cache backend.
        :Param credentials: User provided email, phone number, account id, etc.
        :Param code: Generated verification code.
        :Param ttl: Time to Live for the entry record.
        """
        ...

    @abstractmethod
    def get_entry(self, credentials: str) -> str | int | None:
        """
        Retrieve a verification entry from a storage. If there is no entry
        or it's expired return None.
        :Param credentials: User provided email, phone number, account id, etc.
        """
        ...


class RedisVerificationEntryHandler(VerificationEntryHandler):
    def __init__(self, redis_client_host: str | None = None) -> None:
        super().__init__()
        if not redis_client_host:
            redis_client_host = settings.CELERY_RESULT_BACKEND

        self.redisClient = redis.StrictRedis(host=redis_client_host)

    def cache_entry(self, credentials: str, code: int | str, ttl: int = 240) -> None:
        self.redisClient.set(credentials, code, ex=ttl)
    

class VerificationCodeSender(ABC):
    """Implement code sending via different services (Email, phone_number, etc.)."""
    def __init__(self, code_generator: CodeGenerator, entry_handler: VerificationEntryHandler) -> None:
        super().__init__()
        self.code_generator: CodeGenerator = code_generator
        self.entry_handler: VerificationEntryHandler = entry_handler


    @abstractmethod
    def send_code(self, credentials: str) -> None:
        """Send verification code."""
        ...


class EmailVerification(VerificationCodeSender):
    def __init__(self, code_generator: CodeGenerator, entry_handler: VerificationEntryHandler) -> None:
        super().__init__(code_generator, entry_handler)
        self.code_generator = code_generator
        self.entry_handler = entry_handler

    def send_code(self, email: str) -> None:
        verification_code = self.code_generator.generate_code()
        self.entry_handler.cache_entry(credentials=email, code=verification_code)
        send_verification_code_task.delay(email, verification_code)


class Auth(ABC):
    """API for authentication logic."""
    def __init__(self) -> None:
        super().__init__()
        self.components = {
            "code_generator": UUIDGenerator(),
            "entry_handler": RedisVerificationEntryHandler()
        }
        self.email_verificator = EmailVerification(
            self.components.get("code_generator"),
            self.components.get("entry_handler")
        )

    def send_code_email() -> None:
        ...