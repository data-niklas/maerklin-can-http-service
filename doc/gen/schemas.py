import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src/"))
from app.schemas import can_commands

import inspect

file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemas.puml")


file = open(file_name, "w")
file.write(f"@startuml")

def show_class(clas):
    for base in clas.__bases__:
        file.write(f"{base.__name__} <|-- {clas.__name__}\n")

for attr, value in can_commands.__dict__.items():
    if inspect.isclass(value):
        show_class(value)


file.write(f"@enduml")
file.close()
os.system(f"plantuml -tsvg {file_name}")