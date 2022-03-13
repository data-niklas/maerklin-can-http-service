import ast
import os
import re
import functools
import utils
from start import SCRIPTS, EXTERNAL_SERVICES

source_dir = "../../src/"
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
general_path = os.path.join(base_dir, "imports.puml")
# patched from src/start.py
ASGI_SERVICES = ["raw_can_recv", "raw_can_send", "high_level_can_recv", "high_level_can_send", "high_level_can", "database_read"]

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


def path_from_import(import_):
    subpath = import_.replace(".", os.sep)
    subpath = os.path.join(source_dir, subpath)
    if not "app" in import_.split("."):
        return None
    if os.path.exists(subpath + ".py"):
        subpath += ".py"
    if not os.path.exists(subpath):
        subpath = os.path.dirname(subpath)
        if os.path.exists(subpath + ".py"):
            subpath += ".py"
    if not os.path.exists(subpath):
        return None
    return subpath


class ImportListVisitor(ast.NodeVisitor):
    def __init__(self):
        super()
        self.imports = set()
        self.current_path = list()
        self.stack = set()

    def visit_Import(self, node):
        self.imports.update(alias.name for alias in node.names)

    def visit_ImportFrom(self, node):
        prefix = ""
        if node.level is not None and node.level > 0:
            prefix += ".".join(self.current_path[:-node.level])
            if len(prefix) > 0:
                prefix += "."
        if node.module is not None:
            prefix += node.module+"."
        self.imports.update(prefix+alias.name for alias in node.names)
    
    @functools.lru_cache(maxsize=None)
    def get_all_imports_from(self, path):
        self.stack = set()
        if os.path.isfile(path):
            return self.get_all_imports_from_file(path)
        else:
            # assume it is a directory
            imports = set()
            for name in os.listdir(path):
                subpath = os.path.join(path, name)
                self.stack.add(subpath)
                subimports = self.get_all_imports_from(subpath,)
                imports.update(subimports)
            return imports
    
    @functools.lru_cache(maxsize=None)
    def get_all_imports_from_file(self, path):
        self.current_path = path[len(source_dir):].replace(os.sep, "/").split("/")
        if path.split(".")[-1] != "py":
            return []
        with open(path, "r") as f:
            root = ast.parse(f.read())
        self.imports = set()
        self.visit(root)
        now_imports = set(self.imports)
        for import_ in now_imports:
            subpath = path_from_import(import_)
            if subpath is None or subpath in self.stack:
                continue
            self.stack.add(subpath)
            subimports = self.get_all_imports_from(subpath)
            self.imports.update(subimports)
        return self.imports

def print_tree(tree, f):
    for key in tree:
        f.write(f"namespace {key} {{\n")
        print_tree(tree[key], f)
        f.write(f"}}\n")

if __name__ == "__main__":
    f = open(general_path, "w")
    f.write(f"@startuml\n")
    f.write("skinparam useBetaStyle true\n")
    f.write("skinparam linetype ortho\n")
    f.write(STYLE)



    interesting_points = {}
    for service in EXTERNAL_SERVICES:
        external_services_path = os.path.join(source_dir, "app", "external_services")
        interesting_points[service] = os.path.join(external_services_path, service)
    for service in ASGI_SERVICES:
        services_path = os.path.join(source_dir, "app", "services")
        interesting_points[service] = os.path.join(services_path, service)
    interesting_points["schemas"] = os.path.join(source_dir, "app", "schemas")
    interesting_points["models"] = os.path.join(source_dir, "app", "models")
    interesting_points["utils"] = os.path.join(source_dir, "app", "utils")
    print(interesting_points)
    visitor = ImportListVisitor()
    def is_interesting(path):
        return any(point in path for point in interesting_points.keys())
    def what_interesting(path):
        return [point for point in interesting_points.keys() if point in path.split(".")][0]


    tree = dict()

    for point, path in interesting_points.items():
        print(point + " depends on:")
        clean_path = path[path.find("app"):].replace("/", ".")
        last_branch = tree
        for part in clean_path.split("."):
            if part not in last_branch:
                last_branch[part] = dict()
            last_branch = last_branch[part]
        print(tree)
        imports = visitor.get_all_imports_from(path)
        # print(set(import_ for import_ in imports if not is_interesting(import_)))
        # print(set(what_interesting(import_) for import_ in imports if is_interesting(import_)))
        for dependency in set(path_from_import(import_)[len(source_dir):].replace(os.sep, ".") for import_ in imports if "app" in import_.split(".")):
            
            f.write(f'{dependency.replace(".py","")} <|-- {clean_path}\n')

    print_tree(tree, f)
        #print(set(path_from_import(import_)[len(source_dir):].replace(os.sep, ".") for import_ in imports if "app" in import_.split(".")))

    f.write(f"@enduml")
    f.close()
    os.system(f"plantuml -tsvg {general_path}")