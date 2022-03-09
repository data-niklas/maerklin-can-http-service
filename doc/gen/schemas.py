import os
from utils import write_uml_file, is_valid_class
from app.schemas import can_commands

SUBDIAGRAM_CLASSES = [ \
    can_commands.AbstractLocIDCommand, \
    can_commands.AbstractSystemCommand,  \
    can_commands.AbstractMfxCommand \
]

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
general_path = os.path.join(base_dir, "schemas.puml")
subdiagram_paths = {clas.__name__ : os.path.join(base_dir, f"{clas.__name__}.puml") \
    for clas in SUBDIAGRAM_CLASSES}

def belongs_to_subdiagram(clas):
    return any(issubclass(clas, c) and not clas is c for c in SUBDIAGRAM_CLASSES)

if __name__ == "__main__":
    general = list()
    subdiagrams = {clas.__name__:list() for clas in SUBDIAGRAM_CLASSES}
    for attr, value in can_commands.__dict__.items():
        if not is_valid_class(value):
            continue
        if not belongs_to_subdiagram(value):
            general.append(value)
        for clas in SUBDIAGRAM_CLASSES:
            if issubclass(value, clas):
                subdiagrams[clas.__name__].append(value)
    write_uml_file(general_path, general)
    for clas in SUBDIAGRAM_CLASSES:
        write_uml_file(subdiagram_paths[clas.__name__], subdiagrams[clas.__name__])
