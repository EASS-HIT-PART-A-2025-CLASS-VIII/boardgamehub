from slowapi import Limiter
from slowapi.util import get_remote_address

# Define the limiter centrally so it can be used in routers
limiter = Limiter(key_func=get_remote_address, headers_enabled=True)
