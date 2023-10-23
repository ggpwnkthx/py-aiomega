from .listener import Listener
from .mega import MegaApi
import asyncio, inspect, logging, threading


# Define an async wrapper class for MegaApi
class AsyncMegaApi(MegaApi):
    def __init__(
        self, appkey: str = "UNSUPPORTED", email: str = None, password: str = None
    ):
        self.__api = MegaApi(appkey, None, None, "Python Async Wrapper")
        self.__loop = asyncio.get_event_loop()
        self.__email = email
        self.__password = password

    def __get_target_method(self, name):
        """Retrieve the attribute from the MegaApi instance using super to avoid recursion."""
        target = self.__api
        method = getattr(target, name, None)
        if not method:
            raise AttributeError(f"{name} does not exist")
        return method

    async def __wrap_target_with_listener(self, name, target, *args):
        """Define an async function to manage listeners and threading."""
        logging.info(f"Beginning ({name})")
        future = asyncio.Future()
        listener = Listener(self.__loop, future)
        self.__api.addListener(listener)
        threading.Thread(target=target, args=args).start()

        try:
            result = await future
        except Exception as e:
            self.__api.removeListener(listener)
            raise future._exception
        self.__api.removeListener(listener)
        logging.info(f"Ending ({name})")
        return result

    def __getattribute__(self, name):
        # If accessing internal attributes or methods, use super to avoid recursion
        if name.startswith("_{}__".format(type(self).__name__)):
            return super().__getattribute__(name)

        target = self.__get_target_method(name)
        if callable(target) and "listener" in inspect.signature(target).parameters:

            async def wrapper(*args):
                return await self.__wrap_target_with_listener(name, target, *args)

            return wrapper
        return target

    async def __aenter__(self):
        await self.login(self.__email, self.__password)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.logout()
        return True
