from typing import List

from src.view.GUI.UserInteraction.Displayable import Displayable
from src.view.GUI.UserInteraction.DisplayableInterface import DisplayableInterface


class DisplayableHolder(DisplayableInterface):
    def __init__(self, disp: Displayable, header_list: List[DisplayableInterface]):
        self.displayable = disp
        self.disp_list = header_list

    def get_disp(self) -> Displayable:
        return self.displayable

    def get_sub_disp(self):
        return self.disp_list
