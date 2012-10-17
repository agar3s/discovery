import os
import re

from collections import OrderedDict
from utils import substring

file_ommiters = [".pyc",".png",".svg",".gif",".jpg",".tmp",".ico",""]
dir_ommiters = [".git"]

def get_structure(path):
    """
    >>> get_structure("test/")
    ['test/a/a/x', 'test/a/a/y', 'test/a/a/z', 'test/a/x', 'test/a/y', 'test/a/z', 'test/x', 'test/y', 'test/z']
    """
    path = os.path.dirname(path+os.sep)
    structure = []
    for item in os.listdir(path):
        abs_path = os.path.join(path,item)
        name, ext = os.path.splitext(abs_path.lower())
        if os.path.isdir(abs_path):
            if item not in dir_ommiters:
                structure += get_structure(abs_path)
        else:
            if ext not in file_ommiters:
                structure.append(abs_path)
    return structure


def get_python_analysis(structure, deepest=-1):
    q="(^from .* import .*$|^import .*$)+"

    results = []
    for data in structure:
        if data.endswith(".py"):
            f = open(data, 'r')
            results += re.findall(q, f.read(), re.M)

    libs = {}

    for result in results:
        temps = []
        if result.startswith("import"):
            temps = result.replace("import ", "").replace(" ","").split(",")

        elif result.startswith("from"):
            result = result.replace("from ","")
            package, imports = result.split(" import ")
            package = package.strip()
            imports = imports.replace(" ","").split(",")
            for imp in imports:
                temps.append(package+"."+imp)

        for tmp in temps:
            if deepest > -1:
                tmp = substring(tmp, ".",deepest)
            if tmp in libs:
                libs[tmp] += 1
            else:
                libs[tmp] = 1

    return libs



def get_javascript_analysis(structure, deepest=-1):
    q = "require\(.*\)"
    results = []
    for data in structure:
        if data.endswith(".js"):
            f = open(data, 'r')
            results += re.findall(q, f.read(), re.M)
    
    libs = {}
    q = "\".*\"|'.*'"
    for result in results:
        result = re.findall(q, result)[0]
        result = result.replace("'","").replace('"','')

        if result in libs:
            libs[result] += 1
        else:
            libs[result] = 1

    return libs

def get_ruby_analysis(structure):
    return structure


def get_framework(path, deepest=-1):
    
    language = {}
    ext = ""
    structure = get_structure(path)

    for x in structure:
        name, ext = os.path.splitext(x)
        if ext in language:
            language[ext] += 1
        else:
            language[ext] = 1

    max_language = OrderedDict(sorted(language.items(), key=lambda t:t[1]))

    result = None
    ext = max_language.keys()[-1]
    if ext == ".py":
        result = get_python_analysis(structure, deepest)
    elif ext == ".rb":
        result = get_ruby_analysis(structure)
    elif ext == ".js":
        result = get_javascript_analysis(structure)
    else:
        result = max_language

    return result

if __name__ == "__main__":
    import doctest
    doctest.testmod()