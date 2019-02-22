import os
from typing import List
import ast
import _ast


def file_to_dict(filename:str):
    output = {}
    tree = ast.parse(open(filename, 'r').read())

    func = [f for f in tree.body if isinstance(f, _ast.FunctionDef)]
    output["functions"] = parse_function(func)

    classes = [cls for cls in tree.body if isinstance(cls, _ast.ClassDef)]
    output["classes"] = parse_class(classes)

    output["file"] = filename
    return output


def parse_function(func):
    functions = {}
    for f in func:
        if not type(f) is _ast.FunctionDef:
            continue
        functions[f.name] = {"args": []}
        for a in f.args.args:
            data_type = "any"
            if a.annotation is not None:
                data_type = a.annotation.id
            functions[f.name]["args"].append({"name": a.arg, "type": data_type})

        functions[f.name]["doc"] = get_docstring(f.body)

    return functions


def get_docstring(body):
    for b in body:
        if hasattr(b, 'value'):
            if type(b.value) is _ast.Str:
                return b.value.s
        return "No Docstring Defined"


def parse_class(obj):
    classes = {}
    for c in obj:
        classes[c.name] = {"func": parse_function(c.body), "doc": get_docstring(c.body)}

    return classes


def format_output(mod:dict):
    functions = mod["functions"]
    classes = mod["classes"]
    name = mod["file"]

    output = name + "\n"

    if len(classes) < 1 and len(functions) < 1:
        output += "\tThis File Does Not Contain Any Functions Or Classes.\n\n"

    if len(classes) > 0:
        output += "\tClasses:\n"

        for name, c in classes.items():
            output += "\t\t" + name + "\n"
            output += "\t\t\tDocstring:\n"
            output += "\t\t\t\t" + c["doc"].replace("\n", "\n\t\t") + "\n"
            output += "\t\t\tMethods:\n"
            for n, f in c["func"].items():
                output += display_function(4, n, f)

    if len(functions) > 0:
        output += "\tFunctions:\n"
        for n, f in functions.items():
            output += display_function(2, n, f)
    return output


def display_function(tab_level:int, name, func):
    base_tab = "\t" * tab_level
    output = base_tab + name + "\n"
    output += base_tab + "\tDocstring:\n"
    output += base_tab + "\t\t" + func["doc"].replace("\n", "\n\t\t") + "\n"
    output += base_tab + "\tArguements:\n"

    for arg in func["args"]:
        output += base_tab + "\t\t" + arg["name"] + " (" + arg["type"] + ")" + "\n"
    output += "\n"

    return output


def get_doc_from_file(filename:str):
    return format_output(file_to_dict(filename))


def get_doc_from_files(files:List[str]):
    output = ""
    for f in files:
        output += get_doc_from_file(f)

    return output


def get_doc_from_dir(path:str):
    output = ""
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            if name.endswith(".py"):
                output += get_doc_from_file(os.path.join(root, name))
    return output


def doc_to_file(doc_text, filename):
    tmp = open(filename, 'w')
    tmp.write(doc_text)
    tmp.close()
