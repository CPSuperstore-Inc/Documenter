# region Imports
import os
import sys
from typing import List

from Documenter.GlobalVariable import HELP_TEXT
from Documenter.Output.outHTML import doc_to_html
from Documenter.Output.outJSON import doc_to_json
from Documenter.Output.outMySQL import doc_to_mysql
from Documenter.Output.outTxt import doc_to_txt
from Documenter.Output.outXML import doc_to_xml
from Documenter.Py2Dict import file_to_dict
from Documenter.misc import path_to_dot_notation
# endregion


# region File To Dict Converters (what the user calls)
def get_doc_from_file(filename:str, start_dir=None, ignore_no_docstr:bool=False):
    """
    Generates a documentation dictionary from a single file
    :param filename: the name of the file to generate documentation from
    :param start_dir: the relative path to start the file's display name (in dot notation)
    :param ignore_no_docstr: If the system will ignore functions and classes without docstrings (allows private)
    :return: the documentation dictionary
    """

    # if the start directory is not defined, set it to the path of the specified file
    if start_dir is None:
        start_dir = os.path.dirname(filename)

    # generate the dictionary from the path
    output = file_to_dict(filename, start_dir, ignore_no_docstr)

    # if no output is created, set the value to an empty dict
    if output is None:
        return {}

    # return the final file as a dictionary
    # the single key is the filename and path in dot notation
    return {path_to_dot_notation(filename, start_dir): output}


def get_doc_from_files(files:List[str], start_dir=None, ignore_no_docstr:bool=False):
    """
    Generates a documentation dictionary from a list of files
    :param files: the list of the files to generate documentation from
    :param start_dir: the relative path to start each file's display name (in dot notation)
    :param ignore_no_docstr: If the system will ignore functions and classes without docstrings (allows private)
    :return: the documentation dictionary
    """

    output = {}

    # iterate over each file provided
    for f in files:

        # get the documentation from each file
        val = get_doc_from_file(f, start_dir, ignore_no_docstr)

        # if no value is specifed, skip the file
        if val == {}:
            continue

        # add the value to the final output
        output.update(val)

    # return the doc dict
    return output


def get_doc_from_dir(path:str, start_dir=None, ignore_no_docstr:bool=False):
    """
    Generates a documentation dictionary from a single path (includes all files in directory, and subdirectories)
    :param path: the path to the files to generate documentation from
    :param start_dir: the relative path to start each file's display name (in dot notation)
    :param ignore_no_docstr: If the system will ignore functions and classes without docstrings (allows private)
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
                val = get_doc_from_file(os.path.join(root, name), start_dir, ignore_no_docstr)

                # if no value is specifed, skip the file
                if val == {}:
                    continue

                # add the value to the final output
                output.update(val)

    # return the doc dict
    return output
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
