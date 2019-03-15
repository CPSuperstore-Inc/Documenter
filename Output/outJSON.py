import json


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