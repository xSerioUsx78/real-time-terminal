import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

import paramiko
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from utils.connection import ConnectionSSH
from .consts import ErrorCodes


logger = logging.getLogger(__name__)


DEFAULT_CLOSE_CODE = 1000

DEFAULT_SSH_PORT = 22


class TerminalConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        """
        Handles the WebSocket connection event. Initializes instance variables for
        connection instance, executor, and task management.
        """

        await super().connect()

        self.is_receiving = False
        self.executor = None
        self.task = None
        self.connection = None

    async def disconnect(self, close_code):
        """
        Handles the WebSocket disconnection event. Cleans up resources, cancels any
        ongoing tasks, and shuts down the executor if necessary.

        Args:
            close_code (int): The code representing the reason for the disconnection.
        """

        logger.debug("Disconnecting WebSocket with close code: %s", close_code)

        await self.cleanup()
        await self.close(close_code)

    async def receive_json(self, content, **kwargs):
        """
        Receives and processes JSON data from the WebSocket. Delegates command handling
        to the `command_management` method.

        Args:
            content (dict): The JSON data received from the WebSocket.
            **kwargs: Additional keyword arguments.
        """

        await self.command_management(**content)

    async def command_management(self, command: str, data: dict):
        """
        Handles the execution of a specified command by calling the appropriate method.

        Args:
            command (str): The command to be executed. It should be one of the keys in the `commands` dictionary.
            data (dict): The data associated with the command. The structure of this data depends on the command being executed.

        Raises:
            KeyError: If the command is not recognized, an error message is sent to the client.

        Sends:
            A JSON response to the client indicating the result of the command execution.
            If the command is invalid, an error response with the code "invalid_command" and an error message is sent.
        """

        commands = {
            "new_connection": self.new_connection,
            "send_command": self.send_command,
        }
        try:
            await commands[command](data)
        except KeyError:
            logger.warning(f"Received invalid command: {command}")
            await self.send_error(ErrorCodes.INVALID_COMMAND, "Invalid command!")

    async def cleanup(self):
        """
        Cleans up resources associated with the WebSocket connection. This includes stopping
        ongoing tasks, closing connections, and shutting down the executor.

        This method ensures that all resources are properly released to avoid potential leaks.
        """

        self.is_receiving = False

        if self.connection and self.connection.connection:
            self.connection.connection.close()

        if self.task:
            self.task.cancel()
            try:
                # Adding a timeout to prevent hanging
                await asyncio.wait_for(self.task, timeout=5)
            except asyncio.CancelledError:
                pass
            except asyncio.TimeoutError:
                logger.warning("Task did not cancel within the timeout period.")

        # Shut down the executor, waiting for threads to finish if needed
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None

    async def send_error(self, code: int, message: str, **kwargs):
        """
        Sends an error message to the client in response to a failed operation.

        Args:
            code (int): The error code representing the type of error.
            message (str): A brief description of the error.
            **kwargs: Additional key-value pairs to include in the error response.
        """

        error_data = {
            "command": "error",
            "data": {
                "code": code,
                "message": message or "Unable to connect!",
                **kwargs,
            },
        }
        await self.send_json(error_data)

    async def new_connection(self, data: dict):
        """
        Establishes a new connection to a device based on the provided connection details.

        Args:
            data (dict): Contains connection details such as 'host', 'connection_type', 'username', and 'password'.

        Sends:
            A JSON response to the client indicating the result of the connection attempt.
            In case of failure, appropriate error messages are sent.
        """

        host = data.get("host")
        port = data.get("port", DEFAULT_SSH_PORT)
        username = data.get("username")
        password = data.get("password")

        self.connection = ConnectionSSH()

        try:
            self.connection.connect_to_device(host, username, password, port)
        except paramiko.AuthenticationException:
            await self.send_error(ErrorCodes.CONNECTION_FAILED, "Authentication error!")
            return
        except paramiko.BadHostKeyException:
            await self.send_error(ErrorCodes.CONNECTION_FAILED, "Bad host key!")
            return
        except paramiko.SSHException:
            await self.send_error(ErrorCodes.CONNECTION_FAILED, "Could not connect.")
            return
        except OSError:
            await self.send_error(ErrorCodes.CONNECTION_FAILED, "Socket is closed.")
            return

        self.is_receiving = True

        if self.executor:
            self.executor.shutdown(wait=True)
        self.executor = ThreadPoolExecutor(max_workers=1)

        self.task = asyncio.create_task(self.start_receiving_output())

    async def send_command(self, data: dict):
        """
        Sends a command to the connected session and handles any errors that may occur.

        Args:
            data (dict): Contains the command text to be sent.

        Sends:
            A JSON response to the client indicating the result of the command execution.
            In case of error, an appropriate error message is sent and the connection is closed.
        """

        text = data.get("text")

        try:
            self.connection.send_command(text)
        except TimeoutError:
            await self.send_error(ErrorCodes.SEND_COMMAND_ERROR, "Timeout error.")
            await self.disconnect(DEFAULT_CLOSE_CODE)
        except OSError:
            await self.send_error(ErrorCodes.SEND_COMMAND_ERROR, "Socket is closed.")
            await self.disconnect(DEFAULT_CLOSE_CODE)

    async def start_receiving_output(self):
        """
        Continuously receives output from the connected session and sends it to the client.

        This method runs in a separate thread to avoid blocking the main event loop.
        It will terminate if `self.is_receiving` is set to False or if an exception occurs.
        """

        loop = asyncio.get_running_loop()

        try:
            while self.is_receiving:
                # Run the blocking `receive_output` method in the thread pool
                output = await loop.run_in_executor(
                    self.executor, self.connection.receive_output
                )
                if output:
                    await self.send_output(output)
        except Exception as e:
            logger.error(f"Error receiving data: {str(e)}")
        finally:
            await self.send_error(ErrorCodes.RECEIVE_OUTPUT_ERROR, "Socket is closed.")
            await self.disconnect(DEFAULT_CLOSE_CODE)

    async def send_output(self, output):
        """
        Sends the received output to the client in JSON format.

        Args:
            output (str): The output data received from the connected session.

        Sends:
            A JSON response to the client with the command "receive_output" and the output data.
        """

        await self.send_json({"command": "receive_output", "data": {"output": output}})
