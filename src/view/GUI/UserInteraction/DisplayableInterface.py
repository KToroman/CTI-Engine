from typing import Protocol, List
from src.view.GUI.UserInteraction.Displayable import Displayable


class DisplayableInterface(Protocol):

    def get_sub_disp(self) -> List["DisplayableInterface"]:
        pass

    def get_disp(self) -> "Displayable":
        pass
