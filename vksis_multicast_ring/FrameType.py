from enum import Enum,unique

@unique
class FrameType(Enum):
    Data = 0
    GreetingRequest = 1
    GreetingReply = 2
    Leaving = 3