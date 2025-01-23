import bcrypt

class PasswordHasher:
    @staticmethod
    def hash_password(password: str) -> bytes:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt)

    @staticmethod
    def verify_password(password: str, hashed: bytes) -> bool:
        return bcrypt.checkpw(password.encode(), hashed)