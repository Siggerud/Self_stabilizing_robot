from exceptions import InvalidCommandException

def check_for_duplicate_commands(commands: list[str], module: str) -> None:
    commandsInUse: list[str] = []
    for command in commands:
        if command in commandsInUse:
            raise InvalidCommandException(f"Command {command} is used multiple times in module {module}")
        commandsInUse.append(command)

def extractAndMatchCommandsToDescriptions(commands: dict[str: str], descriptions: dict[str: str]) -> dict[str: str]:
    # match the commands with their descriptions
    commandsToDescriptions: dict[str: str] = {commandValue: descValue for
                                              (commandKey, commandValue, descKey, descValue) in
                                              zip(commands.keys(), commands.values(), descriptions.keys(),
                                                  descriptions.values()) if commandKey == descKey}

    return commandsToDescriptions
