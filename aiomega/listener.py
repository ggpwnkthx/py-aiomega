from .mega import (
    MegaApi,
    MegaContactRequestList,
    MegaListener,
    MegaRequest,
    MegaError,
    MegaEvent,
    MegaNodeList,
    MegaScheduledCopy,
    MegaSetElementList,
    MegaSetList,
    MegaTextChatList,
    MegaTransfer,
    MegaUserAlertList,
    MegaUserList,
)
import asyncio, logging

class AiomegaError(Exception):
    """Base exception for aiomega module."""
    pass

class MegaApiError(AiomegaError):
    """Exception raised for errors related to MegaApi."""
    pass


class Listener(MegaListener):
    """
    A subclass of MegaListener designed to handle MegaApi events asynchronously.

    This class overrides various methods to provide logging and other custom behavior
    when certain events occur in the MegaApi.

    Attributes
    ----------
    loop : asyncio.AbstractEventLoop
        The event loop in which asynchronous operations will be performed.
    future : asyncio.Future
        A future object that represents a potential result from an asynchronous operation.
    root_node : object
        Represents the root node in the user's MEGA account file system hierarchy.
        It's initially None and gets assigned after successful fetch operation.

    Methods
    -------
    onRequestStart(api: MegaApi, request: MegaRequest)
        Called when a request is about to start, logs the event.
    onRequestFinish(api: MegaApi, request: MegaRequest, error: MegaError)
        Called when a request finishes, handles potential errors and logs the event.
    onRequestUpdate(api: MegaApi, request: MegaRequest)
        Logs updates that occur related to a request.
    onRequestTemporaryError(api: MegaApi, request: MegaRequest, error: MegaError)
        Logs temporary errors that occur related to a request.
    onTransferStart(api: MegaApi, transfer: MegaTransfer)
        Logs the start of a file transfer.
    onTransferFinish(api: MegaApi, transfer: MegaTransfer, error: MegaError)
        Logs the completion of a file transfer.
    onTransferUpdate(api: MegaApi, transfer: MegaTransfer)
        Logs updates that occur during a file transfer.
    onTransferTemporaryError(api: MegaApi, transfer: MegaTransfer, error: MegaError)
        Logs temporary errors that occur during a file transfer.
    onUsersUpdate(api: MegaApi, users: MegaUserList)
        Logs when the users list is updated.
    onUserAlertsUpdate(api: MegaApi, alerts: MegaUserAlertList)
        Logs when the user alerts list is updated.
    onNodesUpdate(api: MegaApi, nodes: MegaNodeList)
        Logs when the nodes list is updated.
    onAccountUpdate(api: MegaApi)
        Logs when the account details are updated.
    onSetsUpdate(api: MegaApi, sets: MegaSetList)
        Logs when the sets list is updated.
    onSetElementsUpdate(api: MegaApi, elements: MegaSetElementList)
        Logs when the set elements list is updated.
    onContactRequestsUpdate(api: MegaApi, requests: MegaContactRequestList)
        Logs when the contact requests list is updated.
    onReloadNeeded(api: MegaApi)
        Logs when a reload is required.
    onBackupStateChanged(api: MegaApi, backup: MegaScheduledCopy)
        Logs when the state of a backup changes.
    onBackupStart(api: MegaApi, backup: MegaScheduledCopy)
        Logs when a backup starts.
    onBackupFinish(api: MegaApi, backup: MegaScheduledCopy, error: MegaError)
        Logs when a backup finishes, with error details if applicable.
    onBackupUpdate(api: MegaApi, backup: MegaScheduledCopy)
        Logs when there's an update in an ongoing backup.
    onBackupTemporaryError(api: MegaApi, backup: MegaScheduledCopy, error: MegaError)
        Logs temporary errors during a backup process.
    onChatUpdate(api: MegaApi, chats: MegaTextChatList)
        Logs when the chat list is updated.
    onEvent(api: MegaApi, event: MegaEvent)
        Logs other events.
    """

    def __init__(self, loop: asyncio.AbstractEventLoop, future: asyncio.Future):
        """
        Initialize Listener.

        Parameters
        ----------
        loop : asyncio.AbstractEventLoop
            Event loop for asynchronous operations.
        future : asyncio.Future
            Future object to hold results of async operations.
        """
        self.loop = loop
        self.future = future
        self.root_node = None
        super(Listener, self).__init__()

    def onRequestStart(self, api: MegaApi, request: MegaRequest):
        """
        Log request start events.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        request : MegaRequest
            The request being started.
        """
        logging.info(("onRequestStart", str(request)))

    def onRequestFinish(self, api: MegaApi, request: MegaRequest, error: MegaError):
        """
        Handle and log request finish events.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        request : MegaRequest
            The request being finished.
        error : MegaError
            Any error associated with the request.
        """
        if error.getErrorCode() != MegaError.API_OK:
            logging.error(("onRequestFinish", str(request), str(error)))
            self.loop.call_soon_threadsafe(
                self.future.set_exception, MegaApiError(error.copy())
            )
            return

        logging.info(("onRequestFinish", str(request)))
        match request.getType():
            case MegaRequest.TYPE_LOGIN:
                if not self.root_node:
                    api.fetchNodes()
            case MegaRequest.TYPE_FETCH_NODES:
                self.root_node = api.getRootNode()
            case _:
                self.loop.call_soon_threadsafe(self.future.set_result, request.copy())

    def onRequestUpdate(self, api: MegaApi, request: MegaRequest):
        """
        Logs the progress of a request.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        request : MegaRequest
            The request being updated.
        """
        logging.debug(("onRequestUpdate", str(request)))

    def onRequestTemporaryError(
        self, api: MegaApi, request: MegaRequest, error: MegaError
    ):
        """
        Logs temporary errors related to a request.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        request : MegaRequest
            The request with a temporary error.
        error : MegaError
            The associated error details.
        """
        logging.error(("onRequestTemporaryError", str(request), str(error)))

    def onTransferStart(self, api: MegaApi, transfer: MegaTransfer):
        """
        Logs the initiation of a transfer.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        transfer : MegaTransfer
            The transfer being initiated.
        """
        logging.info(("onTransferStart", str(transfer), transfer.getFileName()))

    def onTransferFinish(self, api: MegaApi, transfer: MegaTransfer, error: MegaError):
        """
        Logs the completion of a transfer.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        transfer : MegaTransfer
            The transfer being completed.
        error : MegaError
            Any error associated with the transfer.
        """
        logging.info(
            ("onTransferFinish", str(transfer), transfer.getFileName(), str(error))
        )
        # self.continue_event.set()

    def onTransferUpdate(self, api: MegaApi, transfer: MegaTransfer):
        """
        Logs updates related to a transfer.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        transfer : MegaTransfer
            The transfer being updated.
        """
        logging.debug(
            (
                "onTransferUpdate",
                transfer,
                transfer.getFileName(),
                transfer.getTransferredBytes() / 1024,
                transfer.getTotalBytes() / 1024,
                transfer.getSpeed() / 1024,
            )
        )

    def onTransferTemporaryError(
        self, api: MegaApi, transfer: MegaTransfer, error: MegaError
    ):
        """
        Logs temporary errors related to a request.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        request : MegaRequest
            The request with a temporary error.
        error : MegaError
            The associated error details.
        """
        logging.error(
            (
                "onTransferTemporaryError",
                str(transfer),
                transfer.getFileName(),
                str(error),
            )
        )

    def onUsersUpdate(self, api: MegaApi, users: MegaUserList):
        """
        Logs when the users list is updated.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        users : MegaUserList
            Updated list of users.
        """
        if users != None:
            logging.debug(("onUsersUpdate", users.size()))

    def onUserAlertsUpdate(self, api: MegaApi, alerts: MegaUserAlertList):
        """
        Logs when the user alerts list is updated.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        alerts : MegaUserAlertList
            Updated list of user alerts.
        """
        if alerts != None:
            logging.debug(("onUserAlertsUpdate", alerts.size()))

    def onNodesUpdate(self, api: MegaApi, nodes: MegaNodeList):
        """
        Logs when the nodes list is updated.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        nodes : MegaNodeList
            Updated list of nodes.
        """
        if nodes != None:
            logging.debug(("onNodesUpdate", nodes.size()))

    def onAccountUpdate(self, api: MegaApi):
        """
        Logs when the account details are updated.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        """
        logging.debug(("onAccountUpdate",))

    def onSetsUpdate(self, api: MegaApi, sets: MegaSetList):
        """
        Logs when the sets list is updated.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        sets : MegaSetList
            Updated list of sets.
        """
        if sets != None:
            logging.debug(("onSetsUpdate", sets.size()))

    def onSetElementsUpdate(self, api: MegaApi, elements: MegaSetElementList):
        """
        Logs when the set elements list is updated.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        elements : MegaSetElementList
            Updated list of set elements.
        """
        if elements != None:
            logging.debug(("onSetElementsUpdate", elements.size()))

    def onContactRequestsUpdate(self, api: MegaApi, requests: MegaContactRequestList):
        """
        Logs when the contact requests list is updated.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        requests : MegaContactRequestList
            Updated list of contact requests.
        """
        if requests != None:
            logging.debug(("onContactRequestsUpdate", requests.size()))

    def onReloadNeeded(self, api: MegaApi):
        """
        Logs when a reload is required by the MegaApi instance.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        """
        logging.debug(("onReloadNeeded",))

    def onBackupStateChanged(self, api: MegaApi, backup: MegaScheduledCopy):
        """
        Logs when the state of a backup changes.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        backup : MegaScheduledCopy
            The backup whose state has changed.
        """
        logging.debug(("onBackupStateChanged",))

    def onBackupStart(self, api: MegaApi, backup: MegaScheduledCopy):
        """
        Logs when a backup starts.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        backup : MegaScheduledCopy
            The backup that has started.
        """
        logging.info(("onBackupStart",))

    def onBackupFinish(self, api: MegaApi, backup: MegaScheduledCopy, error: MegaError):
        """
        Logs when a backup finishes.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        backup : MegaScheduledCopy
            The backup that has finished.
        error : MegaError
            Any error associated with the backup.
        """
        if error != None:
            logging.error(("onBackupFinish", error))
        else:
            logging.info(("onBackupFinish",))

    def onBackupUpdate(self, api: MegaApi, backup: MegaScheduledCopy):
        """
        Logs updates related to a backup.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        backup : MegaScheduledCopy
            The backup being updated.
        """
        logging.debug(("onBackupUpdate",))

    def onBackupTemporaryError(
        self, api: MegaApi, backup: MegaScheduledCopy, error: MegaError
    ):
        """
        Logs temporary errors related to a backup.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        backup : MegaScheduledCopy
            The backup with a temporary error.
        error : MegaError
            The associated error details.
        """
        logging.error(("onBackupTemporaryError", error))

    def onChatUpdate(self, api: MegaApi, chats: MegaTextChatList):
        """
        Logs when the chat list is updated.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        chats : MegaTextChatList
            Updated list of chats.
        """
        if chats != None:
            logging.debug(("onChatUpdate", chats.size()))

    def onEvent(self, api: MegaApi, event: MegaEvent):
        """
        Logs other events related to the MegaApi instance.

        Parameters
        ----------
        api : MegaApi
            The associated MegaApi instance.
        event : MegaEvent
            The event being logged.
        """
        logging.debug(("onEvent", event.getEventString(), event.getText()))
