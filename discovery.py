import os
import re

ommiters = [".pyc",".png",".svg",".gif"]

def get_structure(path):
    """
    >>> get_structure("test/")
    ['test/a/a/x', 'test/a/a/y', 'test/a/a/z', 'test/a/x', 'test/a/y', 'test/a/z', 'test/x', 'test/y', 'test/z']
    """
    path = os.path.dirname(path+os.sep)
    structure = []
    for item in os.listdir(path):
        abs_path = os.path.join(path,item).lower()
        if os.path.isdir(abs_path):
            structure += get_structure(abs_path)
        else:
            name, ext = os.path.splitext(abs_path)
            if ext not in ommiters:
                structure.append(abs_path)
    return structure


pattern = {"django":["/?[A-Za-z0-9-_ ]+/manage.py$",
                     "/?[A-Za-z0-9-_ ]+/urls.py$"],
           "rails": ["/?[A-Za-z0-9-_ ]+/Gemfile$"],
           "nodejs":["/?[A-Za-z0-9-_ ]+/package.json$"]
           }


def get_framework(structure):
    type = "undefined"
    language = {}
    ext = ""
    for x in structure:
        name, ext = os.path.splitext(x)
        if ext in language:
            language[ext] += 1
        else:
            language[ext] = 1

    total = len(structure)
    for k in language:
        print "%s: %d/100" % (k, language[k]*100/total)


    return None


if __name__ == "__main__":
    import doctest
    doctest.testmod()