import os
from typing import List
import ast
import _ast
import json


MISSING_DOCSTRING_MESSAGE = "N/A"


# region File To Dict Converters (what the user calls)
def get_doc_from_file(filename:str, start_dir=None):
    if start_dir is None:
        start_dir = os.path.dirname(filename)
    output = file_to_dict(filename, start_dir)
    if output is None:
        return {}
    return {path_to_dot_notation(filename, start_dir): output}


def get_doc_from_files(files:List[str], start_dir=None):
    output = {}
    for f in files:
        val = get_doc_from_file(f, start_dir)
        if val == {}:
            continue
        output.update(val)
    return output


def get_doc_from_dir(path:str, start_dir=None):
    if start_dir is None:
        start_dir = path
    output = {}
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            if name.endswith(".py"):
                val = get_doc_from_file(os.path.join(root, name), start_dir)
                if val == {}:
                    continue
                output.update(val)
    return output
# endregion


# region Functions Which Write To Files
def doc_to_txt(doc:dict, filename:str):
    doc_text = dict2ascii(doc)
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


def doc_to_mysql(doc:dict, filename:str):
    output = dict2mysql(doc)
    tmp = open(filename, 'w')
    tmp.write(output)
    tmp.close()


def doc_to_html(doc:dict, filename:str):
    output = dict2html(doc)
    tmp = open(filename, 'w')
    tmp.write(output)
    tmp.close()
# endregion


# region Python File To Dict Notation
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
        i = 0
        for a in f.args.args:
            data_type = "any"

            if a.annotation is not None:
                if hasattr(a.annotation, 'id'):
                    data_type = a.annotation.id
                else:
                    data_type = "unknown"
            functions[f.name]["args"].append({"name": a.arg, "type": data_type, "value": None})
        i += 1
        functions[f.name]["doc"] = get_docstring(f.body)

        values = f.args.defaults
        values.reverse()
        index = 1
        for val in values:
            data = ast.literal_eval(val)
            functions[f.name]["args"][index * -1]["value"] = data
            index += 1
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
# endregion


# region Dict to Other Format Converters
# region XML
def dict2xml(data:dict):
    def get_function(xml_text, func_json, tab_level_adder=0):
        for func, info in func_json["functions"].items():
            xml_text += "\t" * (tab_level + tab_level_adder) + "<function name='{}'>\n".format(func)
            xml_text += "\t" * (tab_level + 1) + "<docstring>{}</docstring>\n".format(info["doc"])
            for arg in info["args"]:
                xml_text += "\t" * (tab_level + 1 + tab_level_adder) + "<arg name='{}' type='{}' value='{}'/>\n".format(arg['name'], arg['type'], arg['value'])
            xml_text += "\t" * (tab_level + tab_level_adder) + "</function>\n"
        return xml_text

    def get_classes(xml_text, class_json):
        for class_name, info in class_json["classes"].items():
            xml_text += "\t" * tab_level + "<class name='{}'>\n".format(class_name)
            xml_text += "\t" * (tab_level + 1) +"<docstring>{}</docstring>\n".format(info["doc"])
            xml_text = get_function(xml_text, {"functions": info["func"]}, 1)
            xml_text += "\t" * tab_level + "</class>\n"
        return xml_text

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
# endregion


# region ASCII (Text)
def dict2ascii(mod_data: dict):
    def display_function(tab_level: int, func_name, func):
        base_tab = "\t" * tab_level
        output_text = base_tab + func_name + "\n"
        if func["doc"] != MISSING_DOCSTRING_MESSAGE:
            output_text += base_tab + "\tDocstring:\n"
            output_text += base_tab + "\t\t" + func["doc"].replace("\n", "\n\t\t") + "\n"
        output_text += base_tab + "\tArguements:\n"

        for arg in func["args"]:
            output_text += base_tab + "\t\t" + arg["name"] + " (" + arg["type"] + ") = " + str(arg["value"]) + "\n"
        output_text += "\n"

        return output_text

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
# endregion


# region MySQL
def dict2mysql(mod_data: dict):
    create_statement = """
        DROP TABLE IF EXISTS `files`;
        DROP TABLE IF EXISTS `classes`;
        DROP TABLE IF EXISTS `functions`;
        DROP TABLE IF EXISTS `args`;
        CREATE TABLE `files` (
            `id` INT(11) NOT NULL AUTO_INCREMENT,
            `name` VARCHAR(50) NULL DEFAULT NULL,
            PRIMARY KEY (`id`)
        );
        CREATE TABLE `classes` (
            `id` INT(11) NOT NULL AUTO_INCREMENT,
            `fileId` INT(11) NOT NULL,
            `name` VARCHAR(50) NOT NULL,
            `docstring` LONGTEXT NULL,
            PRIMARY KEY (`id`)
        );
        CREATE TABLE `functions` (
            `id` INT(11) NOT NULL AUTO_INCREMENT,
            `classId` INT(11) NULL DEFAULT NULL,
            `fileId` INT(11) NOT NULL,
            `name` VARCHAR(50) NOT NULL,
            `docstring` LONGTEXT NULL,
            PRIMARY KEY (`id`)
        );
        CREATE TABLE `args` (
            `id` INT(11) NOT NULL AUTO_INCREMENT,
            `functionId` INT(11) NOT NULL,
            `order` INT(11) NOT NULL,
            `name` TEXT NOT NULL,
            `type` VARCHAR(50) NULL DEFAULT NULL,
            `value` VARCHAR(50) NULL DEFAULT NULL,
            PRIMARY KEY (`id`)
        );
    """

    filenames = {}
    functions = {}
    classes = {}

    # region File Names
    sql = create_statement
    sql += "INSERT INTO files (id, name) VALUES "
    index = 1
    for filename, data in mod_data.items():
        sql += "({}, '{}'), ".format(index, filename)
        filenames[filename] = index
        index += 1
    sql = sql[:-2] + ";\n"
    # endregion

    # region Write Functions
    def insert_functions(func, fname, functions, class_id=None):

        if len(func) == 0:
            return ""

        if class_id is None:
            class_id = "null"

        file_id = filenames[fname]

        try:
            i = max(functions.values()) + 1
        except ValueError:
            i = 1

        sql = "INSERT INTO functions VALUES "
        args_sql = "INSERT INTO args (`functionId`, `order`, `name`, `type`, `value`) VALUES "
        for name, d in func.items():
            functions["{}.{}".format(fname, name)] = i
            sql += "({}, {}, {}, '{}', '{}'), ".format(i, class_id, file_id, name, d['doc'])
            args_sql += insert_args(d["args"], i)
            i += 1

        return sql[:-2] + ";\n" + args_sql[:-2] + ";\n"
    # endregion

    # region Arguements
    def insert_args(args, function_id):

        statement = ""

        order = 0
        for a in args:
            if a['value'] is None:
                val = 'null'
            else:
                try:
                    val = float(a['value'])
                except (ValueError, TypeError):
                    val = "'{}'".format(a['value'])
            statement += "({}, {}, '{}', '{}', {}), ".format(function_id, order, a['name'], a['type'], val)
            order += 1

        return statement
    # endregion

    # region Class Writer
    def insert_classes(c, fname, classes):
        if len(c) == 0:
            return ""

        statement = "INSERT INTO classes VALUES "

        try:
            i = max(classes.values()) + 1
        except ValueError:
            i = 1

        file_id = filenames[fname]

        function_query = ""

        for name, d in c.items():
            func = d["func"]
            doc = d["doc"]
            statement += "({}, {}, '{}', '{}'), ".format(i, file_id, name, doc)
            classes["{}.{}".format(fname, name)] = i
            function_query += insert_functions(func, filename, functions, i)
            i += 1

        statement = statement[:-2] + ";\n" + function_query

        return statement
    # endregion

    for filename, data in mod_data.items():
        sql += insert_functions(data["functions"], filename, functions)
        sql += insert_classes(data["classes"], filename, classes)

    return sql

# endregion

# region HTML
def dict2html(mod_data:dict):
    mod_data = dict2ascii(mod_data)
    mod_data = mod_data.replace("\t", "&nbsp;" * 4).replace("\n", "<br>")
    return "<div>{}</div>".format(mod_data)
# endregion

# endregion


# region Misc Functions
def path_to_dot_notation(filename:str, start_dir = None):
    return filename.replace(start_dir, "")[1:].replace(".py", "").replace("/", ".").replace("\\", ".")
# endregion
