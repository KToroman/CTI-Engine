

class ElegentDark:

    def __init__(self):
        self.style: str
        with open("/common/homes/students/uvhuj_heusinger/Documents/git/cti-engine-prototype/src/view/GUI/StylesheetDark.qss", "r") as file:
            self.style = file.read()
