from functools import wraps
from typing import List
from ..roles import Role

def required_roles(roles: List[Role]):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Store required roles on the function
            wrapper.required_roles = roles
            return await func(self, *args, **kwargs)
        return wrapper
    return decorator