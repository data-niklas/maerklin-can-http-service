import os
import sys
import inspect

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src/"))


FILTER_CLASSES = [
    "Enum",
    "object",
    "Representation",
    "Base"
]

STYLE = """
<style>
    classDiagram{
        FontColor Black
        BackgroundColor White
        LineThickness 2
        LineColor Black
        RoundCorner 10
    }
</style>

"""

def is_class_variable(var, value):
    return type(value) != "function" and not inspect.isclass(value) and not var.startswith("__") and not var.endswith("__")


def find_class_variables(clas):
    if "__table__" in clas.__dict__:
        return clas.__dict__["__table__"].columns
    if "__fields__" in clas.__dict__:
        return [vardef for var, vardef in clas.__dict__["__fields__"].items()]
    return []


def find_class_table_name(clas):
    if "__table__" in clas.__dict__:
        return '"' + clas.__name__ + " - " + clas.__dict__["__table__"].name + '"'
    return clas.__name__

def is_enum(clas):
    for base in clas.__bases__:
        if base.__name__ == "Enum":
            return True

    return False


def write_class(f, clas, classes):
    name = find_class_table_name(clas)
    f.write(f"class {name} {{\n")
    for vardef in find_class_variables(clas):
        if hasattr(vardef, "type_"):
            f.write(f"{vardef.name}: {vardef.type_.__name__}\n")
        else:
            f.write(f"{vardef.name}: {vardef.type}\n")
    f.write(f"}}\n")

    if inspect.isabstract(clas) or clas.__name__.startswith("Abstract"):
        f.write(f"abstract class {name}\n")
    for base in clas.__bases__:
        if not base in classes:
            continue
        f.write(f"{base.__name__} <|-- {name}\n")


def is_table(clas):
    return ("__table__" in clas.__dict__ or "__abstract__" in clas.__dict__)


def is_valid_class(clas):
    return inspect.isclass(clas) and not (is_enum(clas) or clas.__name__ in FILTER_CLASSES)


def write_uml_file(filename, classes):
    f = open(filename, "w")
    f.write(f"@startuml\n")
    f.write("skinparam useBetaStyle true\n")
    f.write("skinparam linetype ortho\n")
    f.write(STYLE)

    for clas in classes:
        write_class(f, clas, classes)

    f.write(f"@enduml")
    f.close()
    os.system(f"plantuml -tsvg {filename}")