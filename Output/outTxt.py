from Documenter.GlobalVariable import MISSING_DOCSTRING_MESSAGE


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

        # if func_name == "__init__":
        #     base_tab = "\t" * (tab_level - 1)
        # else:
        #     # generate the base number of tabs
        #     base_tab = "\t" * tab_level
        #
        #     # create the function name line
        #     output_text = base_tab + func_name + "\n"

        # generate the base number of tabs
        base_tab = "\t" * tab_level

        # create the function name line
        output_text = base_tab + func_name + "\n"

        display_params = not(":param " in func["doc"] or ":return:" in func["doc"])
        doc = func["doc"]

        # if the function has a docstring, add it to the tree
        # will not display the docstring title if it is not defined
        if func["doc"] != MISSING_DOCSTRING_MESSAGE:
            if display_params:
                output_text += base_tab + "\tDocstring:\n"
            for i in doc.split("\n"):
                if ":param " in i or ":return:" in i:
                    output_text += base_tab + "\t\t" + i.replace("\t", "").replace(":param ", "").replace(":return:", "") + "\n"
                else:
                    output_text += base_tab + "\t\t" + i.replace("\t", "").replace("\n", "\n\t\t") + "\n"

        if len(func["args"]) > 0:
            if display_params:
                # add the arguements
                output_text += base_tab + "\tArguements:\n"

                # iterate over each arg
                for arg in func["args"]:

                    # add the name, type, and value to the string
                    output_text += base_tab + "\t\t" + arg["name"]
                    if arg["type"] != "any":
                        output_text += " (" + arg["type"] + ")"
                    if arg["value"] is not None:
                        output_text += " = " + str(arg["value"])
                    output_text += "\n"

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
