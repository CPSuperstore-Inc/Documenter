from Documenter.Output.outTxt import dict2ascii


def doc_to_md(doc:dict, filename:str=None):
    """
    outputs the doc dict as a markdown file (as an ASCII tree format)
    :param doc: the doc dict to write
    :param filename: the output filename - leave blank to have value returned
    """

    # convert the dict to HTML, and write it to the file
    output = dict2md(doc)

    # if no output file is specified, return the value
    if filename is None:
        return output

    tmp = open(filename, 'w')
    tmp.write(output)
    tmp.close()


def dict2md(mod_data:dict):
    """
    this function returns the specified data as markdown string
    :param mod_data: the data to convert to markdown
    :return: the data in HTML format
    """

    # get an ASCII tree represenation of the doc dict
    mod_data = dict2ascii(mod_data)

    # convert each tab to 4 non-breaking space characters,
    # and each end of line character to a line break tag (<br>)
    mod_data = mod_data.replace("\t", "&nbsp;" * 4).replace("\n", "\n\n")

    # return the HTML data between a pair of div tags
    return mod_data
