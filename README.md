# Documenter
Creates docs for a python project

Document an entire directory:

```python
from Documenter.Documenter import get_doc_from_dir, doc_to_txt

doc = get_doc_from_dir("path/to/directory")
doc_to_txt(doc, "output_file")
```

Document a set of files:

```python
from Documenter.Documenter import get_doc_from_files, doc_to_txt

doc = get_doc_from_files(["file1.py", "file2.py", "file3.py"])
doc_to_txt(doc, "output_file")
```


Document a single file:

```python
from Documenter.Documenter import get_doc_from_file, doc_to_txt

doc = get_doc_from_file("file.py")
doc_to_txt(doc, "output_file")
```

output format:
```
path.to.file.py
    Classes:
        ClassName
            Docstring:
                Your Docstring
            Methods:
                method_name
                    Docstring:
                        Your Docstring
                    Arguements:
                        arg1 (type) = defaultValue
                        arg2 (type) = defaultValue
    Functions:
        function_name
            Docstring:
                Your Docstring
            Arguements:
                arg1 (type) = defaultValue
                arg2 (type) = defaultValue
```

`doc_to_txt` is not the only output mode! Here are the other output modes you can use:

`doc_to_txt` - Outputs as an ASCII text tree
 
`doc_to_json` - Outputs as JSON

`doc_to_xml` - Outputs as XML

`doc_to_mysql` - Outputs as a file of MySQL queries to run on a MySQL database

`doc_to_sqlite` - Outputs as a file of SQLite3 queries to run on a SQLite3 database

`doc_to_html` - Outputs as an HTML file. All output is placed inside a `<div>` tag, with no other tags or styles
