from django.conf import settings
from django.test import TestCase
from channels.testing import WebsocketCommunicator

from terminal.consumers import TerminalConsumer
from terminal.consts import ErrorCodes


SSH_HOST = getattr(settings, "SSH_HOST")
SSH_USER = getattr(settings, "SSH_USER")
SSH_PASS = getattr(settings, "SSH_PASS")
SSH_PORT = getattr(settings, "SSH_PORT")

DEFAULT_TIMEOUT = 5
INVALID_PORT = 52859


class TerminalConsumerTest(TestCase):
    def setUp(self) -> None:
        self.url = "ws/terminal/"

    def create_communicator(self) -> WebsocketCommunicator:
        """
        Create a new WebSocket communicator for the TerminalConsumer.

        Returns:
            WebsocketCommunicator: The communicator instance for the TerminalConsumer.
        """

        communicator = WebsocketCommunicator(TerminalConsumer.as_asgi(), self.url)
        return communicator

    async def test_connect(self) -> None:
        """
        Test the WebSocket connection to ensure it can connect and disconnect successfully.

        Steps:
            1. Create a WebSocket communicator.
            2. Connect to the communicator.
            3. Assert the connection is successful.
            4. Disconnect from the communicator.
        """

        communicator = self.create_communicator()

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_new_connection_success(self) -> None:
        """
        Test establishing a new SSH connection successfully.

        Steps:
            1. Create a WebSocket communicator.
            2. Connect to the communicator.
            3. Send a 'new_connection' command with valid SSH credentials.
            4. Assert that the response is successful and contains the expected output.
            5. Disconnect from the communicator.
        """

        communicator = self.create_communicator()

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to(
            {
                "command": "new_connection",
                "data": {
                    "host": SSH_HOST,
                    "port": SSH_PORT,
                    "username": SSH_USER,
                    "password": SSH_PASS,
                },
            }
        )

        response = await communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)

        self.assertTrue(isinstance(response, dict))
        self.assertTrue("command" in response)
        self.assertTrue("data" in response)
        self.assertTrue("output" in response["data"])

        self.assertEqual(response["command"], "receive_output")

        await communicator.disconnect()

    async def test_new_connection_failed__invalid_password(self) -> None:
        """
        Test the failure of establishing a new SSH connection with an invalid password.

        Steps:
            1. Create a WebSocket communicator.
            2. Connect to the communicator.
            3. Send a 'new_connection' command with an invalid password.
            4. Assert that the response indicates an error with the expected code and message.
            5. Disconnect from the communicator.
        """

        communicator = self.create_communicator()

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to(
            {
                "command": "new_connection",
                "data": {
                    "host": SSH_HOST,
                    "port": SSH_PORT,
                    "username": SSH_USER,
                    "password": "Wrong pass",
                },
            }
        )

        response = await communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)

        self.assertTrue(isinstance(response, dict))
        self.assertTrue("command" in response)
        self.assertTrue("data" in response)
        self.assertTrue("code" in response["data"])
        self.assertTrue("message" in response["data"])

        self.assertEqual(response["command"], "error")
        self.assertEqual(response["data"]["code"], ErrorCodes.CONNECTION_FAILED)

        await communicator.disconnect()

    async def test_new_connection_failed__invalid_username(self) -> None:
        """
        Test the failure of establishing a new SSH connection with an invalid username.

        Steps:
            1. Create a WebSocket communicator.
            2. Connect to the communicator.
            3. Send a 'new_connection' command with an invalid username.
            4. Assert that the response indicates an error with the expected code and message.
            5. Disconnect from the communicator.
        """

        communicator = self.create_communicator()

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to(
            {
                "command": "new_connection",
                "data": {
                    "host": SSH_HOST,
                    "port": SSH_PORT,
                    "username": "Wrong user",
                    "password": SSH_PASS,
                },
            }
        )

        response = await communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)

        self.assertTrue(isinstance(response, dict))
        self.assertTrue("command" in response)
        self.assertTrue("data" in response)
        self.assertTrue("code" in response["data"])
        self.assertTrue("message" in response["data"])

        self.assertEqual(response["command"], "error")
        self.assertEqual(response["data"]["code"], ErrorCodes.CONNECTION_FAILED)

        await communicator.disconnect()

    async def test_new_connection_failed__invalid_port(self) -> None:
        """
        Test the failure of establishing a new SSH connection with an invalid port.

        Steps:
            1. Create a WebSocket communicator.
            2. Connect to the communicator.
            3. Send a 'new_connection' command with an invalid port.
            4. Assert that the response indicates an error with the expected code and message.
            5. Disconnect from the communicator.
        """

        communicator = self.create_communicator()

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to(
            {
                "command": "new_connection",
                "data": {
                    "host": SSH_HOST,
                    "port": INVALID_PORT,
                    "username": SSH_USER,
                    "password": SSH_PASS,
                },
            }
        )

        response = await communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)

        self.assertTrue(isinstance(response, dict))
        self.assertTrue("command" in response)
        self.assertTrue("data" in response)
        self.assertTrue("code" in response["data"])
        self.assertTrue("message" in response["data"])

        self.assertEqual(response["command"], "error")
        self.assertEqual(response["data"]["code"], ErrorCodes.CONNECTION_FAILED)

        await communicator.disconnect()

    async def test_new_connection_failed__invalid_host(self) -> None:
        """
        Test the failure of establishing a new SSH connection with an invalid host.

        Steps:
            1. Create a WebSocket communicator.
            2. Connect to the communicator.
            3. Send a 'new_connection' command with an invalid host.
            4. Assert that the response indicates an error with the expected code and message.
            5. Disconnect from the communicator.
        """

        communicator = self.create_communicator()

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to(
            {
                "command": "new_connection",
                "data": {
                    "host": "Wrong host",
                    "port": SSH_PORT,
                    "username": SSH_USER,
                    "password": SSH_PASS,
                },
            }
        )

        response = await communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)

        self.assertTrue(isinstance(response, dict))
        self.assertTrue("command" in response)
        self.assertTrue("data" in response)
        self.assertTrue("code" in response["data"])
        self.assertTrue("message" in response["data"])

        self.assertEqual(response["command"], "error")
        self.assertEqual(response["data"]["code"], ErrorCodes.CONNECTION_FAILED)

        await communicator.disconnect()

    async def test_new_connection_failed__missing_field(self) -> None:
        """
        Test the failure of establishing a new SSH connection with a missing field.

        Steps:
            1. Create a WebSocket communicator.
            2. Connect to the communicator.
            3. Send a 'new_connection' command with a missing field (e.g., missing 'host').
            4. Assert that the response indicates an error with the expected code and message.
            5. Disconnect from the communicator.
        """

        communicator = self.create_communicator()

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to(
            {
                "command": "new_connection",
                "data": {"port": SSH_PORT, "username": SSH_USER, "password": SSH_PASS},
            }
        )

        response = await communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)

        self.assertTrue(isinstance(response, dict))
        self.assertTrue("command" in response)
        self.assertTrue("data" in response)
        self.assertTrue("code" in response["data"])
        self.assertTrue("message" in response["data"])

        self.assertEqual(response["command"], "error")
        self.assertEqual(response["data"]["code"], ErrorCodes.CONNECTION_FAILED)

        await communicator.disconnect()

    async def test_send_command_success(self) -> None:
        """
        Test sending a command after establishing an SSH connection.

        Steps:
            1. Create a WebSocket communicator.
            2. Connect to the communicator.
            3. Send a 'new_connection' command with valid SSH credentials.
            4. Send a 'send_command' command to execute a simple command (e.g., 'date').
            5. Assert that the response contains the output of the command.
            6. Disconnect from the communicator.
        """

        communicator = self.create_communicator()

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to(
            {
                "command": "new_connection",
                "data": {
                    "host": SSH_HOST,
                    "port": SSH_PORT,
                    "username": SSH_USER,
                    "password": SSH_PASS,
                },
            }
        )
        await communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)

        await communicator.send_json_to(
            {"command": "send_command", "data": {"text": "date"}}
        )

        response = await communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)

        self.assertTrue(isinstance(response, dict))
        self.assertTrue("command" in response)
        self.assertTrue("data" in response)
        self.assertTrue("output" in response["data"])

        self.assertEqual(response["command"], "receive_output")
        self.assertTrue(bool(response["data"]["output"]))

        await communicator.disconnect()

    async def test_send_command_failed(self) -> None:
        """
        Test sending an invalid command.

        Steps:
            1. Create a WebSocket communicator.
            2. Connect to the communicator.
            3. Send a 'new_connection' command with valid SSH credentials.
            4. Send an invalid command (e.g., 'wrong command').
            5. Assert that the response indicates an error with the expected code and message.
            6. Disconnect from the communicator.
        """

        communicator = self.create_communicator()

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to(
            {
                "command": "new_connection",
                "data": {
                    "host": SSH_HOST,
                    "port": SSH_PORT,
                    "username": SSH_USER,
                    "password": SSH_PASS,
                },
            }
        )
        await communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)

        await communicator.send_json_to({"command": "wrong command", "data": None})

        response = await communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)

        self.assertTrue(isinstance(response, dict))
        self.assertTrue("command" in response)
        self.assertTrue("data" in response)
        self.assertTrue("code" in response["data"])
        self.assertTrue("message" in response["data"])

        self.assertEqual(response["command"], "error")
        self.assertEqual(response["data"]["code"], ErrorCodes.INVALID_COMMAND)

        await communicator.disconnect()

    async def test_send_command_failed__null_command(self) -> None:
        """
        Test sending a null command.

        Steps:
            1. Create a WebSocket communicator.
            2. Connect to the communicator.
            3. Send a 'new_connection' command with valid SSH credentials.
            4. Send a null command (None).
            5. Assert that the response indicates an error with the expected code and message.
            6. Disconnect from the communicator.
        """

        communicator = self.create_communicator()

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to(
            {
                "command": "new_connection",
                "data": {
                    "host": SSH_HOST,
                    "port": SSH_PORT,
                    "username": SSH_USER,
                    "password": SSH_PASS,
                },
            }
        )
        await communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)

        await communicator.send_json_to({"command": None, "data": None})

        response = await communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)

        self.assertTrue(isinstance(response, dict))
        self.assertTrue("command" in response)
        self.assertTrue("data" in response)
        self.assertTrue("code" in response["data"])
        self.assertTrue("message" in response["data"])

        self.assertEqual(response["command"], "error")
        self.assertEqual(response["data"]["code"], ErrorCodes.INVALID_COMMAND)

        await communicator.disconnect()

    async def test_send_command_failed__empty_command(self) -> None:
        """
        Test sending an empty command.

        Steps:
            1. Create a WebSocket communicator.
            2. Connect to the communicator.
            3. Send a 'new_connection' command with valid SSH credentials.
            4. Send an empty command string.
            5. Assert that the response indicates an error with the expected code and message.
            6. Disconnect from the communicator.
        """

        communicator = self.create_communicator()

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to(
            {
                "command": "new_connection",
                "data": {
                    "host": SSH_HOST,
                    "port": SSH_PORT,
                    "username": SSH_USER,
                    "password": SSH_PASS,
                },
            }
        )
        await communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)

        await communicator.send_json_to({"command": "", "data": None})

        response = await communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)

        self.assertTrue(isinstance(response, dict))
        self.assertTrue("command" in response)
        self.assertTrue("data" in response)
        self.assertTrue("code" in response["data"])
        self.assertTrue("message" in response["data"])

        self.assertEqual(response["command"], "error")
        self.assertEqual(response["data"]["code"], ErrorCodes.INVALID_COMMAND)

        await communicator.disconnect()

    async def test_send_multiple_commands_quick_succession(self) -> None:
        """
        Test sending multiple commands in quick succession.

        Steps:
            1. Create a WebSocket communicator.
            2. Connect to the communicator.
            3. Send a 'new_connection' command with valid SSH credentials.
            4. Send multiple commands in quick succession.
            5. Assert that each command receives a response containing output.
            6. Disconnect from the communicator.
        """

        communicator = self.create_communicator()

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to(
            {
                "command": "new_connection",
                "data": {
                    "host": SSH_HOST,
                    "port": SSH_PORT,
                    "username": SSH_USER,
                    "password": SSH_PASS,
                },
            }
        )
        await communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)

        commands = ["date", "whoami", "uptime"]
        for command in commands:
            await communicator.send_json_to(
                {"command": "send_command", "data": {"text": command}}
            )

        for _ in commands:
            response = await communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)
            self.assertEqual(response["command"], "receive_output")
            self.assertTrue(bool(response["data"]["output"]))

        await communicator.disconnect()

    async def test_disconnection_during_command(self) -> None:
        """
        Test the behavior when disconnecting during a command execution.

        Steps:
            1. Create a WebSocket communicator.
            2. Connect to the communicator.
            3. Send a 'new_connection' command with valid SSH credentials.
            4. Send a long-running command (e.g., 'sleep 10').
            5. Disconnect from the communicator while the command is running.
            6. Create a new communicator, connect, and establish a new SSH session.
            7. Assert that the new session is established successfully.
            8. Disconnect from the new communicator.
        """

        communicator = self.create_communicator()

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to(
            {
                "command": "new_connection",
                "data": {
                    "host": SSH_HOST,
                    "port": SSH_PORT,
                    "username": SSH_USER,
                    "password": SSH_PASS,
                },
            }
        )
        await communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)

        await communicator.send_json_to(
            {"command": "send_command", "data": {"text": "sleep 10"}}
        )

        await communicator.disconnect()

        new_communicator = self.create_communicator()
        connected, _ = await new_communicator.connect()
        self.assertTrue(connected)

        await new_communicator.send_json_to(
            {
                "command": "new_connection",
                "data": {
                    "host": SSH_HOST,
                    "port": SSH_PORT,
                    "username": SSH_USER,
                    "password": SSH_PASS,
                },
            }
        )
        response = await new_communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)
        self.assertEqual(response["command"], "receive_output")

        await new_communicator.disconnect()

    async def test_cleanup_after_disconnection(self) -> None:
        """
        Test proper cleanup after a disconnection during a long-running command.

        Steps:
            1. Create a WebSocket communicator.
            2. Connect to the communicator.
            3. Send a 'new_connection' command with valid SSH credentials.
            4. Send a long-running command (e.g., 'sleep 10') and then disconnect from the communicator.
            5. Create a new communicator and reconnect to ensure the process is not blocked and cleanup was successful.
            6. Assert that the new session is established successfully.
            7. Disconnect from the new communicator.
        """

        communicator = self.create_communicator()

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to(
            {
                "command": "new_connection",
                "data": {
                    "host": SSH_HOST,
                    "port": SSH_PORT,
                    "username": SSH_USER,
                    "password": SSH_PASS,
                },
            }
        )
        await communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)

        await communicator.send_json_to(
            {"command": "send_command", "data": {"text": "sleep 10"}}
        )

        await communicator.disconnect()

        new_communicator = self.create_communicator()
        connected, _ = await new_communicator.connect()
        self.assertTrue(connected)

        await new_communicator.send_json_to(
            {
                "command": "new_connection",
                "data": {
                    "host": SSH_HOST,
                    "port": SSH_PORT,
                    "username": SSH_USER,
                    "password": SSH_PASS,
                },
            }
        )
        response = await new_communicator.receive_json_from(timeout=DEFAULT_TIMEOUT)
        self.assertEqual(response["command"], "receive_output")

        await new_communicator.disconnect()
