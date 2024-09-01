import paramiko


class ConnectionSSH:
    def __init__(self) -> None:
        self.connection = None
        self.channel = None

    def connect_to_device(
        self, host: str, username: str, password: str, port: int = 22, *args, **kwargs
    ):
        self.connection = paramiko.SSHClient()
        self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connection.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            *args,
            **kwargs
        )

        # Open a new channel
        self.channel = self.connection.invoke_shell()

    def receive_output(self, timeout: float = 1):
        self.channel.settimeout(timeout)
        if self.channel.recv_ready():
            return self.channel.recv(1024).decode("utf-8")

    def send_command(self, command: str):
        self.channel.send(command)

    def close(self):
        self.channel.close()
        self.connection.close()
