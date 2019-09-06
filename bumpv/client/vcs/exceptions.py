class WorkingDirectoryIsDirtyException(Exception):
    def __init__(self, message):
        self.message = message


class VCSCommandError(Exception):
    def __init__(self, message, command):
        self.message = f"error attempting VCS command '{' '.join(command)}' {message}"
        self.command = command
