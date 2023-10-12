from .mega import MegaApi, MegaListener, MegaRequest, MegaError
import asyncio, inspect, logging, threading


class AppListener(MegaListener):
    def __init__(self, loop: asyncio.AbstractEventLoop, future: asyncio.Future):
        self.loop = loop  # Event loop for asynchronous operations
        self.future = future  # Future object to hold results of async ops
        self.root_node = None  # Initialize root node to None
        super(AppListener, self).__init__()  # Initialize parent class

    # Function to log request start events
    def onRequestStart(self, api: MegaApi, request: MegaRequest):
        logging.info(("onRequestStart", str(request)))

    # Function to handle and log request finish events
    def onRequestFinish(self, api: MegaApi, request: MegaRequest, error: MegaError):
        if error.getErrorCode() != MegaError.API_OK:
            logging.error(("onRequestFinish", str(request), str(error)))
            self.loop.call_soon_threadsafe(
                self.future.set_exception, Exception(error.copy())
            )
            return

        logging.info(("onRequestFinish", str(request)))
        # Check the request type and perform relevant actions
        match request.getType():
            case MegaRequest.TYPE_LOGIN:
                api.fetchNodes()
            case MegaRequest.TYPE_FETCH_NODES:
                self.root_node = api.getRootNode()
            case _:
                self.loop.call_soon_threadsafe(self.future.set_result, request.copy())


# Define an async wrapper class for MegaApi
class AsyncMegaApi(MegaApi):
    def __init__(
        self, appkey: str = "UNSUPPORTED", email: str = None, password: str = None
    ):
        self.api = MegaApi(
            appkey, None, None, "Python Async Wrapper"
        )  # Initialize the MegaApi instance
        self.loop = asyncio.get_event_loop()  # Get the current async event loop
        self._email = email  # Store email for login
        self._password = password  # Store password for login

    # Retrieve attributes and provide async functionality for certain methods
    def __getattribute__(self, name):
        api: MegaApi = super().__getattribute__("api")
        loop: asyncio.AbstractEventLoop = super().__getattribute__("loop")
        target = getattr(api, name)  # Retrieve the attribute from the MegaApi instance

        # Check if the attribute exists
        if not target:
            raise AttributeError(f"{name} does not exist")

        # Check if the attribute is callable and has a 'listener' parameter
        if callable(target) and "listener" in inspect.signature(target).parameters:
            # Define an async function to manage listeners and threading
            async def wrapper(*args):
                logging.info(f"Beginning ({name})")
                future = asyncio.Future()
                listener = AppListener(
                    loop, future
                )  # Create a new AppListener instance
                api.addListener(listener)  # Add the listener to the MegaApi instance
                # Start a new thread to run the MegaApi function
                threading.Thread(target=target, args=args).start()
                # Wait for the future to be set and remove the listener
                try:
                    result = await future
                except Exception as e:
                    api.removeListener(listener)
                    raise future._exception
                api.removeListener(listener)
                logging.info(f"Ending ({name})")
                return result

            return wrapper  # Return the async function
        return target  # Return the attribute directly if not callable with listener

    # Async context manager enter function to perform login
    async def __aenter__(self):
        await self.login(
            super().__getattribute__("_email"),
            super().__getattribute__("_password"),
        )
        return self

    # Async context manager exit function to perform logout
    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.logout()
        return True
