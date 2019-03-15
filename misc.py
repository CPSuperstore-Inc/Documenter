def path_to_dot_notation(filename:str, start_dir = None):
    """
    This function returns the file name in dot notation
    :param filename: the name of the file to convert
    :param start_dir: the path to where the path should start
    :return: the path in dot notation
    """

    # convert and return the filename
    return filename.replace(start_dir, "")[1:].replace(".py", "").replace("/", ".").replace("\\", ".")