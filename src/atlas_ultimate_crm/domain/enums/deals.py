from enum import Enum


class DealStatus(str, Enum):
    OPEN = "open"
    WON = "won"
    LOST = "lost"
