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

DEFAULT_VALUES:dict[ImageEnum,float] = {
     ImageEnum.Brightness: 1.0,
     ImageEnum.Gaus: 0,
}
