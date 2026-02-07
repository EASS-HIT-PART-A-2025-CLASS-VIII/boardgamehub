from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

if __name__ == "__main__":
    import sys
    password = "admin"
    if len(sys.argv) > 1:
        password = sys.argv[1]
    
    print(f"Generating hash for password: '{password}'")
    hashed_password = get_password_hash(password)
    print(f"Hash: {hashed_password}")
