import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src/"))
from app.models import can_message

import inspect

file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models.puml")


file = open(file_name, "w")
file.write(f"@startuml\n")
file.write("skinparam useBetaStyle true\n")
file.write("skinparam linetype ortho\n")
file.write("""
<style>
    classDiagram{
        FontColor Black
        BackgroundColor White
        LineThickness 2
        LineColor Black
        RoundCorner 10
    }
</style>

""")


filter_classes = [
    "Enum",
    "object",
    "Base"
]

def is_class_variable(var, value):
    return type(value) != "function" and not inspect.isclass(value) and not var.startswith("__") and not var.endswith("__")

def find_class_variables(clas):
    if "__table__" in clas.__dict__:
        return clas.__dict__["__table__"].columns
    return []

def find_class_table_name(clas):
    if "__table__" in clas.__dict__:
        return '"' + clas.__name__ + " - " + clas.__dict__["__table__"].name + '"'
    return clas.__name__

def show_class(clas):
    name = find_class_table_name(clas)
    file.write(f"class {name} {{\n")
    columns = find_class_variables(clas)
    for column in columns:
        file.write(f"{column.name}: {column.type}\n")
    file.write(f"}}\n")

    #file.write(f"class {clas.__name__} as {name}\n")

    if inspect.isabstract(clas) or clas.__name__.startswith("Abstract"):
        file.write(f"abstract class {name}\n")
    for base in clas.__bases__:
        #if not is_filtered(base):
        file.write(f"{base.__name__} <|-- {name}\n")

def is_enum(clas):
    for base in clas.__bases__:
        if base.__name__ == "Enum":
            return True

    return False

def is_filtered(clas):
    return ("__table__" not in clas.__dict__ and "__abstract__" not in clas.__dict__) or clas.__name__ in filter_classes

for attr, value in can_message.__dict__.items():
    if inspect.isclass(value) and not is_enum(value) and not is_filtered(value):
        show_class(value)


file.write(f"@enduml")
file.close()
os.system(f"plantuml -tsvg {file_name}")