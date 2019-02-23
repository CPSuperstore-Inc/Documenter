import os
from typing import List
import ast
import _ast
import json


MISSING_DOCSTRING_MESSAGE = "N/A"

def path_to_dot_notation(filename:str, start_dir:str):
    return filename.replace(start_dir, "")[1:].replace(".py", "").replace("/", ".").replace("\\", ".")


def dict2xml(data:dict):
    def get_function(xml, func_json, tab_level_adder=0):
        for func, info in func_json["functions"].items():
            xml += "\t" * (tab_level + tab_level_adder) + "<function name='{}'>\n".format(func)
            xml += "\t" * (tab_level + 1) + "<docstring>{}</docstring>\n".format(info["doc"])
            for arg in info["args"]:
                xml += "\t" * (tab_level + 1 + tab_level_adder) + "<arg name='{}' type='{}'/>\n".format(arg['name'], arg['type'])
            xml += "\t" * (tab_level + tab_level_adder) + "</function>\n"
        return xml

    def get_classes(xml, class_json):
        for class_name, info in class_json["classes"].items():
            xml += "\t" * tab_level + "<class name='{}'>\n".format(class_name)
            xml += "\t" * (tab_level + 1) +"<docstring>{}</docstring>\n".format(info["doc"])
            xml = get_function(xml, {"functions": info["func"]}, 1)
            xml += "\t" * tab_level + "</class>\n"
        return xml

    if "functions" in data:
        data = {"some_unused_string": data}

    tab_level = 0

    xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<docs>\n"

    tab_level += 1
    for fname, d in data.items():
        xml += "\t" * tab_level + "<module name='{}'>\n".format(fname)
        tab_level += 1
        xml = get_classes(xml, d)
        xml = get_function(xml, d)
        tab_level -= 1
        xml += "\t" * tab_level + "</module>\n"

    xml += "</docs>"
    return xml


def file_to_dict(filename:str, start_dir:str):
    if start_dir is None:
        start_dir = filename

    output = {}

    fdata = open(filename, 'r').read()

    filename = path_to_dot_notation(filename, start_dir)

    if fdata == "":
        return None
    tree = ast.parse(fdata)

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
        return MISSING_DOCSTRING_MESSAGE


def parse_class(obj):
    classes = {}
    for c in obj:
        classes[c.name] = {"func": parse_function(c.body), "doc": get_docstring(c.body)}

    return classes


def get_doc_from_file(filename:str, start_dir=None):
    output = file_to_dict(filename, start_dir)
    if output is None:
        return {}
    return output


def get_doc_from_files(files:List[str], start_dir=None):
    output = {}
    for f in files:
        val = get_doc_from_file(f, start_dir)
        if val == {}:
            continue
        output[path_to_dot_notation(f, start_dir)] = val

    return output


def get_doc_from_dir(path:str, start_dir=None):
    output = {}
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            if name.endswith(".py"):
                val = get_doc_from_file(os.path.join(root, name), start_dir)
                if val == {}:
                    continue
                output[path_to_dot_notation(os.path.join(root, name), start_dir)] = val
    return output


def doc_to_txt(doc:dict, filename:str):

    def format_output(mod_data: dict):
        if "functions" in mod_data:
            mod_data = {"some_unused_string": mod_data}
        output = ""
        for fname, mod in mod_data.items():
            functions = mod["functions"]
            classes = mod["classes"]
            name = mod["file"]

            output += name + "\n"

            if len(classes) < 1 and len(functions) < 1:
                output += "\tThis File Does Not Contain Any Functions Or Classes.\n\n"

            if len(classes) > 0:
                output += "\tClasses:\n"

                for name, c in classes.items():
                    output += "\t\t" + name + "\n"
                    if c["doc"] != MISSING_DOCSTRING_MESSAGE:
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

    def display_function(tab_level: int, name, func):
        base_tab = "\t" * tab_level
        output = base_tab + name + "\n"
        if func["doc"] != MISSING_DOCSTRING_MESSAGE:
            output += base_tab + "\tDocstring:\n"
            output += base_tab + "\t\t" + func["doc"].replace("\n", "\n\t\t") + "\n"
        output += base_tab + "\tArguements:\n"

        for arg in func["args"]:
            output += base_tab + "\t\t" + arg["name"] + " (" + arg["type"] + ")" + "\n"
        output += "\n"

        return output

    doc_text = format_output(doc)

    tmp = open(filename, 'w')
    tmp.write(doc_text)
    tmp.close()


def doc_to_json(doc:dict, filename:str):
    output = json.dumps(doc)
    tmp = open(filename, 'w')
    tmp.write(output)
    tmp.close()


def doc_to_xml(doc:dict, filename:str):
    output = dict2xml(doc)
    tmp = open(filename, 'w')
    tmp.write(output)
    tmp.close()
