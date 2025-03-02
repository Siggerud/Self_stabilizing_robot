class InvalidPinException(Exception):
    def __init__(self, message):
        super().__init__(message)

class OutOfRangeException(Exception):
    def __init__(self, message):
        super().__init__(message)

class InvalidCommandException(Exception):
    def __init__(self, message):
        super().__init__(message)

class X11ForwardingException(Exception):
    pass

class MicrophoneException(Exception):
    pass