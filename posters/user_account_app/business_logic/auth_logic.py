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
    (e.g. user's email address, phone number, etc.) and the value is a generated secret code.
    The verification entry must be stored after the secret code generation on the server side,
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

    @abstractmethod
    def clear_entry(self, key: str) -> None:
        """Clear entry after user is verified (authenticated)."""
        ...


class RedisVerificationEntryHandler(VerificationEntryHandler):
    def __init__(self, redis_url: str | None = None) -> None:
        """
        Connect to redis via a redis link.
        :Param redis_url: A URL to redis. Correct format example is "redis://localhost:6379/3".
        """
        super().__init__()
        if not redis_url:
            redis_url = settings.REDIS_LOCATION

        self.redisClient = redis.Redis.from_url(redis_url)

    def cache_entry(self, credentials: str, code: int | str, ttl: int = 240) -> None:
        try:
            self.redisClient.set(credentials, code, ex=ttl)
        except redis.RedisError as e:
            # NOTE: Log error here
            print(f"ERROR: Validation entry was not cached!")
            pass

    def get_entry(self, credentials: str) -> str | int | None:
        return self.redisClient.get(credentials)

    def clear_entry(self, key: str) -> None:
        self.redisClient.delete(key)


class VerificationCodeSender(ABC):
    #NOTE: Change the name of this class to sth. like VerificationCodeManager
    """Implement code sending via different services (Email, phone_number, etc.)."""

    def __init__(self, code_generator: CodeGenerator, entry_handler: VerificationEntryHandler) -> None:
        """
        Initialize the sender with a code generator and an entry handler.
        :Param code_generator: The strategy for generating the verification code.
        :Param entry_handler: Where the code will be cached for later verification.
        """
        super().__init__()
        self.code_generator: CodeGenerator = code_generator
        self.entry_handler: VerificationEntryHandler = entry_handler

    @abstractmethod
    def send_code(self, credentials: str) -> None:
        """
        Send verification code.
        :Param credentials: User provided email, phone number, account id, etc.
        """
        ...

    @abstractmethod
    def verify_user(self, credentials: str, client_code: str) -> bool:
        """
        Verify the client provided credentials and verification code.
        :Param credentials: User provided email, phone number, account id, etc.
        :Param client_code: User provided code, that is compared to the originally generated code
        stored on the server side.
        """
        ...


class EmailVerification(VerificationCodeSender):
    def __init__(self, code_generator: CodeGenerator, entry_handler: VerificationEntryHandler) -> None:
        super().__init__(code_generator, entry_handler)
        self.code_generator = code_generator
        self.entry_handler = entry_handler

    def send_code(self, email: str) -> None:
        verification_code = self.code_generator.generate_code()
        self.entry_handler.cache_entry(
            credentials=email, code=verification_code)
        send_verification_code_task.delay(email, verification_code)

    def verify_user(self, email: str, client_code: str) -> bool:
        server_code = self.entry_handler.get_entry(email)
        authentication_result = True if server_code == client_code.encode() else False
        if authentication_result:
            self.entry_handler.clear_entry(email)
        return authentication_result


class VerificationFactory:
    @staticmethod
    def get_method(method: str) -> VerificationCodeSender:
        match method:
            case 'email':
                return EmailVerification(
                    UUIDGenerator(),
                    RedisVerificationEntryHandler(redis_url="redis://localhost:6379/2"))
            case _:
                raise ValueError(
                    f"Verification method ({method}) is not supported!")


class Auth:
    """API for authentication logic."""

    def send_verification(method: str, credentials: str) -> None:
        sender: VerificationCodeSender = VerificationFactory.get_method(method)
        sender.send_code(credentials)

    def verify_user(method: str, credentials: str, client_code: str) -> bool:
        verifier: VerificationCodeSender = VerificationFactory.get_method(
            method)
        return verifier.verify_user(str(credentials), str(client_code))
