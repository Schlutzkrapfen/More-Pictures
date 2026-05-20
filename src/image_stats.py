from enum import Enum
from dataclasses import dataclass 

class ImageEnum(Enum):
    Brightness = 0,
    Gaus = 1,
    Mirrored = 2,

@dataclass
class PictureEntry:
    brightness: float =  1
    mirrored: bool = False
    gaus: float = 0
