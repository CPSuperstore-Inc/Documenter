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
