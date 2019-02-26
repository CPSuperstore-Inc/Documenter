# region Imports
import os
from typing import List
import ast
import _ast
import json
import sys
# endregion


# region Global Variables
# the message to put in place of a missing docstring
MISSING_DOCSTRING_MESSAGE = "N/A"

HELP_TEXT = """
SYNTAX:
    Documenter FILETYPE FILES... OUTPUT_FILE
"""
# endregion


# region File To Dict Converters (what the user calls)
def get_doc_from_file(filename:str, start_dir=None):
    """
    Generates a documentation dictionary from a single file
    :param filename: the name of the file to generate documentation from
    :param start_dir: the relative path to start the file's display name (in dot notation)
    :return: the documentation dictionary
    """

    # if the start directory is not defined, set it to the path of the specified file
    if start_dir is None:
        start_dir = os.path.dirname(filename)

    # generate the dictionary from the path
    output = file_to_dict(filename, start_dir)

    # if no output is created, set the value to an empty dict
    if output is None:
        return {}

    # return the final file as a dictionary
    # the single key is the filename and path in dot notation
    return {path_to_dot_notation(filename, start_dir): output}


def get_doc_from_files(files:List[str], start_dir=None):
    """
    Generates a documentation dictionary from a list of files
    :param files: the list of the files to generate documentation from
    :param start_dir: the relative path to start each file's display name (in dot notation)
    :return: the documentation dictionary
    """

    output = {}

    # iterate over each file provided
    for f in files:

        # get the documentation from each file
        val = get_doc_from_file(f, start_dir)

        # if no value is specifed, skip the file
        if val == {}:
            continue

        # add the value to the final output
        output.update(val)

    # return the doc dict
    return output


def get_doc_from_dir(path:str, start_dir=None):
    """
    Generates a documentation dictionary from a single path (includes all files in directory, and subdirectories)
    :param path: the path to the files to generate documentation from
    :param start_dir: the relative path to start each file's display name (in dot notation)
    :return: the documentation dictionary
    """

    # if no start dir is specified, set it to the provided path
    if start_dir is None:
        start_dir = path

    output = {}

    # iterate over each file in the dir and subdirs
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:

            # ensure the file is a Python file (other files usualy cause errors)
            if name.endswith(".py"):

                # get a doc dict for the file
                val = get_doc_from_file(os.path.join(root, name), start_dir)

                # if no value is specifed, skip the file
                if val == {}:
                    continue

                # add the value to the final output
                output.update(val)

    # return the doc dict
    return output
# endregion


# region Functions Which Write To Files
def doc_to_txt(doc:dict, filename:str=None):
    """
    outputs the doc dict as a text file (as an ASCII tree format)
    :param doc: the doc dict to write
    :param filename: the output filename - leave blank to have value returned
    """

    # convert the dict to ASCII, and write it to the file
    output = dict2ascii(doc)

    # if no output file is specified, return the value
    if filename is None:
        return output

    tmp = open(filename, 'w')
    tmp.write(output)
    tmp.close()


def doc_to_json(doc:dict, filename:str=None):
    """
    outputs the doc dict as a JSON file
    :param doc: the doc dict to write
    :param filename: the output filename - leave blank to have value returned
    """

    # convert the dict to JSON, and write it to the file
    output = json.dumps(doc)

    # if no output file is specified, return the value
    if filename is None:
        return output

    tmp = open(filename, 'w')
    tmp.write(output)
    tmp.close()


def doc_to_xml(doc:dict, filename:str=None):
    """
    outputs the doc dict as a XML file
    :param doc: the doc dict to write
    :param filename: the output filename - leave blank to have value returned
    """

    # convert the dict to XML, and write it to the file
    output = dict2xml(doc)

    # if no output file is specified, return the value
    if filename is None:
        return output

    tmp = open(filename, 'w')
    tmp.write(output)
    tmp.close()


def doc_to_mysql(doc:dict, filename:str=None):
    """
    outputs the doc dict as a file of MySQL Commands
    :param doc: the doc dict to write
    :param filename: the output filename - leave blank to have value returned
    """

    # convert the dict to MySQL commands, and write it to the file
    output = dict2mysql(doc)

    # if no output file is specified, return the value
    if filename is None:
        return output

    tmp = open(filename, 'w')
    tmp.write(output)
    tmp.close()


def doc_to_html(doc:dict, filename:str=None):
    """
    outputs the doc dict as an HTML file (as an ASCII tree format)
    :param doc: the doc dict to write
    :param filename: the output filename - leave blank to have value returned
    """

    # convert the dict to HTML, and write it to the file
    output = dict2html(doc)

    # if no output file is specified, return the value
    if filename is None:
        return output

    tmp = open(filename, 'w')
    tmp.write(output)
    tmp.close()
# endregion


# region Python File To Dict Notation
def file_to_dict(filename:str, start_dir:str):
    """
    This function converts a file to dictionary notation
    :param filename: the path to the Python file
    :param start_dir: the path to the start location of the dot notation
    :return: the doc dict
    """

    # if no start directory is specified, set it to the provided filename
    if start_dir is None:
        start_dir = filename

    output = {}

    # read the file into memory
    fdata = open(filename, 'r').read()

    # get the dot notation of the filename
    filename = path_to_dot_notation(filename, start_dir)

    # if the file is empty, skip it
    if fdata == "":
        return None

    # parse the Python file
    tree = ast.parse(fdata)

    # parse the functions in the file, and add to the dictionary
    func = [f for f in tree.body if isinstance(f, _ast.FunctionDef)]
    output["functions"] = parse_function(func)

    # parse the classes in the file, and add to the dictionary
    classes = [cls for cls in tree.body if isinstance(cls, _ast.ClassDef)]
    output["classes"] = parse_class(classes)

    # add the dot notation filename to the doc dict
    output["file"] = filename

    # return the result
    return output


def parse_function(func):
    """
    This function converts the functions of a file to dict format
    :param func: The function tree
    :return: dict of function data
    """

    functions = {}

    # iterate over each function
    for f in func:

        # skip all items which are not functions
        if not type(f) is _ast.FunctionDef:
            continue

        # add the function, and the blank function info to the master dictionary
        functions[f.name] = {"args": []}

        # iterate over each arguement
        i = 0
        for a in f.args.args:

            # get the arguement accepted datatype ('any' is the default value)
            data_type = "any"
            if a.annotation is not None:
                if hasattr(a.annotation, 'id'):
                    data_type = a.annotation.id
                else:
                    data_type = "unknown"

            # add the correct information to the arguement
            functions[f.name]["args"].append({"name": a.arg, "type": data_type, "value": None})
        i += 1

        # add the function's docstring (if provided)
        functions[f.name]["doc"] = get_docstring(f.body)

        # get the default arguement values, and reverse the list
        values = f.args.defaults
        values.reverse()

        # iterate over each value
        index = 1
        for val in values:

            # assign each value to the appropriate arguement
            data = ast.literal_eval(val)
            functions[f.name]["args"][index * -1]["value"] = data
            index += 1

    # return the function data
    return functions


def get_docstring(body):
    """
    gets the docstring from the item's body, or returns a default message if is not defined
    :param body: the body to search for the docstring
    :return: the docstring
    """

    # find an element from the body, which has a 'value' attribute, and is type _ast.Str
    for b in body:
        if hasattr(b, 'value'):
            if type(b.value) is _ast.Str:
                # if it is found, return it
                return b.value.s

        # otherwise, return the default message
        return MISSING_DOCSTRING_MESSAGE


def parse_class(obj):
    """
    Parses the classes of a file, and returns a doc dict
    :param obj: the object to parse
    :return: the doc dict of classes
    """
    classes = {}
    for c in obj:
        # for each class, parse the functions, and docstring, and add it to the doc dict
        classes[c.name] = {"func": parse_function(c.body), "doc": get_docstring(c.body)}

    # return it
    return classes
# endregion


# region Dict to Other Format Converters
# region XML
def dict2xml(data:dict):
    """
    this function returns the specified data as an XML string
    :param data: the data to convert to XML
    :return: the data in XML format
    """
    def get_function(xml_text, func_json, tab_level_adder=0):
        """
        this function converts a Python function to XML
        :param xml_text: the current XML string
        :param func_json: the JSON version of the function to convert
        :param tab_level_adder: The number of extra tabs needed for the start of the XML
        :return: 
        """

        # iterate over each function provided
        for func, info in func_json["functions"].items():

            # create the opening tag, which displays the function's name
            xml_text += "\t" * (tab_level + tab_level_adder) + "<function name='{}'>\n".format(func)

            # create the docstring tag
            xml_text += "\t" * (tab_level + 1) + "<docstring>{}</docstring>\n".format(info["doc"])

            # add the arguement tags, which displays the function's name, type, and default value
            for arg in info["args"]:
                xml_text += "\t" * (tab_level + 1 + tab_level_adder) + "<arg name='{}' type='{}' value='{}'/>\n".format(arg['name'], arg['type'], arg['value'])

            # add the closing function tag
            xml_text += "\t" * (tab_level + tab_level_adder) + "</function>\n"

        # return the XML string
        return xml_text

    def get_classes(xml_text, class_json):
        """
        This function converts each class to XML
        :param xml_text: the full XML string
        :param class_json: the JSON object we are working with
        :return: the newly updated XML
        """

        # iterate over each class
        for class_name, info in class_json["classes"].items():

            # create the opening tag, which contains the class name
            xml_text += "\t" * tab_level + "<class name='{}'>\n".format(class_name)

            # create the docstring tag
            xml_text += "\t" * (tab_level + 1) +"<docstring>{}</docstring>\n".format(info["doc"])

            # use the 'get_function' function to generate XML from the classes methods
            xml_text = get_function(xml_text, {"functions": info["func"]}, 1)

            # close the class tag
            xml_text += "\t" * tab_level + "</class>\n"

            # return the XML string
        return xml_text

    # if this function is a single dict, put it in a parent dict
    if "functions" in data:
        data = {"some_unused_string": data}

    tab_level = 0

    # create the XML shema line
    xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<docs>\n"

    # iterate over each module
    tab_level += 1
    for fname, d in data.items():

        # create the opening "module" tag, which contains the name
        xml += "\t" * tab_level + "<module name='{}'>\n".format(fname)
        tab_level += 1

        # generate the functions and classes from the module
        xml = get_classes(xml, d)
        xml = get_function(xml, d)

        tab_level -= 1

        # close the module tag
        xml += "\t" * tab_level + "</module>\n"

    # finish up the XML and return it
    xml += "</docs>"
    return xml
# endregion


# region ASCII (Text)
def dict2ascii(mod_data: dict):
    """
    this function returns the specified data as a text ASCII tree string
    :param mod_data: the data to convert to a text ASCII tree
    :return: the data in a text ASCII tree format
    """
    def display_function(tab_level: int, func_name, func):
        """
        This function displays a function in tree format
        :param tab_level: the number of tabs to place before the function
        :param func_name: the function's display name
        :param func: the function as a dict
        :return: the ASCII tree function
        """

        # generate the base number of tabs
        base_tab = "\t" * tab_level

        # create the function name line
        output_text = base_tab + func_name + "\n"

        # if the function has a docstring, add it to the tree
        # will not display the docstring title if it is not defined
        if func["doc"] != MISSING_DOCSTRING_MESSAGE:
            output_text += base_tab + "\tDocstring:\n"
            output_text += base_tab + "\t\t" + func["doc"].replace("\n", "\n\t\t") + "\n"

        # add the arguements
        output_text += base_tab + "\tArguements:\n"

        # iterate over each arg
        for arg in func["args"]:

            # add the name, type, and value to the string
            output_text += base_tab + "\t\t" + arg["name"] + " (" + arg["type"] + ") = " + str(arg["value"]) + "\n"
        output_text += "\n"

        # return the text
        return output_text

    # ensure the module is not a single module
    if "functions" in mod_data:
        mod_data = {"some_unused_string": mod_data}

    # iterate over each module
    output = ""
    for fname, mod in mod_data.items():

        # extract the functions, classes, and filename
        functions = mod["functions"]
        classes = mod["classes"]
        name = mod["file"]

        output += name + "\n"

        # if the module has no functions, and no classes, output the "no functions or classes" message
        if len(classes) < 1 and len(functions) < 1:
            output += "\tThis File Does Not Contain Any Functions Or Classes.\n\n"

        if len(classes) > 0:
            # if the file has classes, generate the class text
            output += "\tClasses:\n"

            # iterate over each class
            for name, c in classes.items():

                # create the title line
                output += "\t\t" + name + "\n"

                # add a docstring line if the class has a docstring
                if c["doc"] != MISSING_DOCSTRING_MESSAGE:
                    output += "\t\t\tDocstring:\n"
                    output += "\t\t\t\t" + c["doc"].replace("\n", "\n\t\t") + "\n"

                # display the classes functions
                output += "\t\t\tMethods:\n"
                for n, f in c["func"].items():
                    output += display_function(4, n, f)

        # if the file has funcitons, display the functions
        if len(functions) > 0:
            output += "\tFunctions:\n"
            for n, f in functions.items():
                output += display_function(2, n, f)

    # return the output
    return output
# endregion


# region MySQL
def dict2mysql(mod_data: dict):
    """
    this function returns the specified data as a file of MySQL commands
    :param mod_data: the data to convert to a file of MySQL commands
    :return: the data in MySQL command format
    """

    # generate the create statement, and drop tables if they are there
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

    sql = create_statement

    # dictionaries to store the IDs of classes, functions and files
    filenames = {}
    functions = {}
    classes = {}

    # region File Names

    # insert each file name with one command
    sql += "INSERT INTO files (id, name) VALUES "
    index = 1

    # iterate over each file
    for filename, data in mod_data.items():

        # add to the SQL and dict
        sql += "({}, '{}'), ".format(index, filename)
        filenames[filename] = index
        index += 1

    # finish up the SQL statement
    sql = sql[:-2] + ";\n"
    # endregion

    # region Write Functions
    def insert_functions(func, fname, funcs, class_id=None):
        """
        this function adds the SQL commands for each function
        :param func: the function objects
        :param fname: the filename
        :param funcs: the dictionary which stores the function names and IDs
        :param class_id: the ID of the class which the function is in (None for not in a class)
        :return: the function SQL commands
        """

        # if there are no functions, return an empty string
        if len(func) == 0:
            return ""

        # if no class is specified, use null
        if class_id is None:
            class_id = "null"

        # get the file ID
        file_id = filenames[fname]

        # get the initial ID of the function
        try:
            i = max(funcs.values()) + 1
        except ValueError:
            i = 1

        # generate the start of the function and arguement query
        query = "INSERT INTO functions VALUES "
        args_sql = "INSERT INTO args (`functionId`, `order`, `name`, `type`, `value`) VALUES "

        # iterate over each function
        for name, d in func.items():

            # add the ID to the function dict, with the key of filename.func_name
            funcs["{}.{}".format(fname, name)] = i

            # add the function and arg queries
            query += "({}, {}, {}, '{}', '{}'), ".format(i, class_id, file_id, name, d['doc'])
            args_sql += insert_args(d["args"], i)
            i += 1

        # return the func, and arg queries
        return query[:-2] + ";\n" + args_sql[:-2] + ";\n"
    # endregion

    # region Arguements
    def insert_args(args, function_id):
        """
        This function generates the SQL commands for each arguement
        :param args: the list of args
        :param function_id: the affiliated function ID
        :return: the SQL string
        """

        statement = ""

        # iterate over each arguement
        order = 0
        for a in args:

            # if the arguement does not specify a value, set to null
            if a['value'] is None:
                val = 'null'
            else:
                # if the item is a number, do not surround with quotes
                try:
                    int(a['value'])
                    val = a['value']
                except (ValueError, TypeError):
                    val = "'{}'".format(a['value'])

            # add to the SQL statement
            statement += "({}, {}, '{}', '{}', {}), ".format(function_id, order, a['name'], a['type'], val)
            order += 1

        # return the statement
        return statement
    # endregion

    # region Class Writer
    def insert_classes(c, fname, class_list):
        """
        this function generates the SQL for each class
        :param c: the dict of classes
        :param fname: the filename
        :param class_list: the dict of class IDs
        :return: the list of SQL statements for the class
        """

        # if there are no classes, return an empty string
        if len(c) == 0:
            return ""

        statement = "INSERT INTO classes VALUES "

        # get the initial class ID
        try:
            i = max(class_list.values()) + 1
        except ValueError:
            i = 1

        # get the file ID
        file_id = filenames[fname]

        function_query = ""

        # iterate over each class
        for name, d in c.items():

            # add to the SQL statement
            func = d["func"]
            doc = d["doc"]
            statement += "({}, {}, '{}', '{}'), ".format(i, file_id, name, doc)

            # add the ID to the dict in the format filename.class
            class_list["{}.{}".format(fname, name)] = i
            function_query += insert_functions(func, filename, functions, i)
            i += 1

        # finish off the statement, and return it
        statement = statement[:-2] + ";\n" + function_query
        return statement
    # endregion

    # iterate over each file in the doc dict
    for filename, data in mod_data.items():
        # add the function and class SQL to the main statement
        sql += insert_functions(data["functions"], filename, functions)
        sql += insert_classes(data["classes"], filename, classes)

    # return the SQL statement
    return sql

# endregion


# region HTML
def dict2html(mod_data:dict):
    """
    this function returns the specified data as HTML string
    :param mod_data: the data to convert to HTML
    :return: the data in HTML format
    """

    # get an ASCII tree represenation of the doc dict
    mod_data = dict2ascii(mod_data)

    # convert each tab to 4 non-breaking space characters,
    # and each end of line character to a line break tag (<br>)
    mod_data = mod_data.replace("\t", "&nbsp;" * 4).replace("\n", "<br>")

    # return the HTML data between a pair of div tags
    return "<div>{}</div>".format(mod_data)
# endregion

# endregion


# region Misc Functions
def path_to_dot_notation(filename:str, start_dir = None):
    """
    This function returns the file name in dot notation
    :param filename: the name of the file to convert
    :param start_dir: the path to where the path should start
    :return: the path in dot notation
    """

    # convert and return the filename
    return filename.replace(start_dir, "")[1:].replace(".py", "").replace("/", ".").replace("\\", ".")
# endregion


# region Command Line Interface
if __name__ == '__main__':
    # the filetype and function call key value dict
    output_types = {
        "txt": doc_to_txt,
        "json": doc_to_json,
        "xml": doc_to_xml,
        "mysql": doc_to_mysql,
        "html": doc_to_html
    }

    # if an insufficient number of args are specified, display help text, and exit with code -1
    if len(sys.argv) < 4:
        print(HELP_TEXT)
        quit(-1)

    # get the arguemsnts
    output_type = sys.argv[1].lower()   # display type (ex. html, txt, xml)
    input_file = sys.argv[2]            # the input file/directory
    output_file = sys.argv[3]           # the output file

    # if an invalid output type is selected, alert the user, and provide a list of expected inputs
    # also exit with a code of -1
    if output_type not in output_types.keys():
        print("{} Is An Invalid File Type. Please Select One From The Following List:\n{}".format(output_type, ", ".join(output_types.keys())))
        quit(-1)

    doc_dict = {}

    # if path is directory, get doc from dir
    if os.path.isdir(input_file):
        doc_dict = get_doc_from_dir(input_file)

    # create the file
    output_types[output_type](doc_dict, output_file)
# endregion

