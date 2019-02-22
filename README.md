# Documenter
Creates docs for a python project

Document an entire directory:

```python
from Documenter.Documenter import get_doc_from_dir, doc_to_file

doc = get_doc_from_dir("path_to_directory")
doc_to_file(doc, "output_file")
```

Document a set of files:

```python
from Documenter.Documenter import get_doc_from_files, doc_to_file

doc = get_doc_from_files(["file1.py", "file2.py", "file3.py"])
doc_to_file(doc, "output_file")
```


Document a single file:

```python
from Documenter.Documenter import get_doc_from_file, doc_to_file

doc = get_doc_from_file("file.py")
doc_to_file(doc, "output_file")
```

output format:
```
path/to/file.py
    Classes:
        ClassName
            Docstring:
                Your Docstring
            Methods:
                method_name
                    Docstring:
                        Your Docstring
                    Arguements:
                        arg1 (type)
                        arg2 (type)     
    Functions:
        function_name
            Docstring:
                Your Docstring
            Arguements:
                arg1 (type)
                arg2 (type)
```