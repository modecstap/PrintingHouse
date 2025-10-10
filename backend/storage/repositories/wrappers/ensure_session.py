from functools import wraps
from inspect import signature


def ensure_session(method):
    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        sig = signature(method)
        if 'session' not in sig.parameters:
            raise TypeError(f"Функция {method.__name__} должна принимать аргумент 'session'")

        if 'session' in kwargs and kwargs['session'] is not None:
            return await method(self, *args, **kwargs)

        async with self.db.async_session_maker() as session:
            try:
                return await method(self, *args, session=session, **kwargs)
            finally:
                await session.close()

    return wrapper
