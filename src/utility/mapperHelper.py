from exceptions import InvalidCommandException

def check_for_duplicate_commands(commands: list[str], module: str) -> None:
    commandsInUse: list[str] = []
    for command in commands:
        if command in commandsInUse:
            raise InvalidCommandException(f"Command {command} is used multiple times in module {module}")
        commandsInUse.append(command)
