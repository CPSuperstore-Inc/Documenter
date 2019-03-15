import ast
import _ast

from Documenter.GlobalVariable import MISSING_DOCSTRING_MESSAGE
from Documenter.misc import path_to_dot_notation


def file_to_dict(filename:str, start_dir:str, ignore_no_docstr:bool):
    """
    This function converts a file to dictionary notation
    :param filename: the path to the Python file
    :param start_dir: the path to the start location of the dot notation,
    :param ignore_no_docstr: If the system will ignore functions and classes without docstrings (allows private)
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
    output["functions"] = parse_function(func, ignore_no_docstr)

    # parse the classes in the file, and add to the dictionary
    classes = [cls for cls in tree.body if isinstance(cls, _ast.ClassDef)]
    output["classes"] = parse_class(classes, ignore_no_docstr)

    # add the dot notation filename to the doc dict
    output["file"] = filename

    # return the result
    return output


def parse_function(func, ignore_no_docstr:bool):
    """
    This function converts the functions of a file to dict format
    :param func: The function tree
    :param ignore_no_docstr: If the system will ignore functions and classes without docstrings (allows private)
    :return: dict of function data
    """

    functions = {}

    # iterate over each function
    for f in func:

        # skip all items which are not functions
        if not type(f) is _ast.FunctionDef:
            continue

        if get_docstring(f.body) == MISSING_DOCSTRING_MESSAGE and ignore_no_docstr is True:
            continue

        # add the function, and the blank function info to the master dictionary
        functions[f.name] = {"args": []}

        # iterate over each arguement
        i = 0
        for a in f.args.args:

            if a.arg == "self":
                continue

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
                return b.value.s[1:-1].replace("\n", "\n\t\t\t\t")

        # otherwise, return the default message
        return MISSING_DOCSTRING_MESSAGE


def parse_class(obj, ignore_no_docstr:bool):
    """
    Parses the classes of a file, and returns a doc dict
    :param obj: the object to parse
    :param ignore_no_docstr: If the system will ignore functions and classes without docstrings (allows private)
    :return: the doc dict of classes
    """
    classes = {}
    for c in obj:

        if get_docstring(c.body) == MISSING_DOCSTRING_MESSAGE and ignore_no_docstr is True:
            continue

        # for each class, parse the functions, and docstring, and add it to the doc dict
        classes[c.name] = {"func": parse_function(c.body, ignore_no_docstr), "doc": get_docstring(c.body)}

    # return it
    return classes