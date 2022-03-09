import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src/"))
from app.schemas import can_commands

import inspect

file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemas.puml")


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
    "Representation"
]

def is_class_variable(var, value):
    return type(value) != "function" and not inspect.isclass(value) and not var.startswith("__") and not var.endswith("__")

def find_class_variables(clas):
    if "__fields__" in clas.__dict__:
        return [vardef for var, vardef in clas.__dict__["__fields__"].items()]
    return []

def show_class(clas):
    file.write(f"class {clas.__name__}{{\n")
    for vardef in find_class_variables(clas):
        file.write(f"{vardef.name}: {vardef.type_.__name__}\n")
    file.write(f"}}\n")

    if inspect.isabstract(clas) or clas.__name__.startswith("Abstract"):
        file.write(f"abstract class {clas.__name__}\n")
    for base in clas.__bases__:
        if not is_filtered(base):
            file.write(f"{base.__name__} <|-- {clas.__name__}\n")

def is_enum(clas):
    for base in clas.__bases__:
        if base.__name__ == "Enum":
            return True

    return False

def is_filtered(clas):
    return clas.__name__ in filter_classes

for attr, value in can_commands.__dict__.items():
    if inspect.isclass(value) and not is_enum(value) and not is_filtered(value):
        show_class(value)


file.write(f"@enduml")
file.close()
os.system(f"plantuml -tsvg {file_name}")