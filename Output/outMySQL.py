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