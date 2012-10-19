import os
import re
import sqlite3

from collections import OrderedDict
from utils import substring

file_ommiters = [".pyc",".png",".svg",".gif",".jpg",".tmp",".ico",""]
dir_ommiters = [".git"]

table_names= {".py":"PYTHON"}
db_queries = {"get_column_names":"PRAGMA table_info(%s)",
              "insert_column":"ALTER TABLE PYTHON ADD %s int default 0",
              "insert_repo":"INSERT INTO %s %s VALUES %s"}

def get_connection():
    connection = sqlite3.connect("data.db")

def closest_framework(results, ext, framework=None):
    connection = sqlite3.connect("data.db")
    cursor = connection.cursor()
    
    #inspect and insert new columns if is neccesary
    columns = cursor.execute(db_queries["get_column_names"] % table_names[ext])
    columns = [x[1] for x in columns.fetchall()]

    for r, v in results.items():
        if ("ct_"+r) not in columns:
            cursor.execute(db_queries["insert_column"] % ("ct_"+r))

    connection.commit()

    if not framework:
        #search the neighbor 
        pass
    else:
        results["v_c"] = 1    

    #insert the results
    results["fw_c"] = framework
    
    names = str(tuple(["ct_"+x for x in results.keys()]))
    values = str(tuple(results.values()))
    cursor.execute(db_queries["insert_repo"] % (table_names[ext],names,values))
    connection.commit()

    return framework


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


def get_python_analysis(structure, deepest=0):
    s="[a-zA-Z0-9\-._\"'/]*"
    q="(^from %s import %s$|^import %s$)+" % (s,s,s)

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

    if "" in libs:
        del(libs[""])
    return libs



def get_javascript_analysis(structure, deepest=0):
    q = "require\([a-zA-Z0-9\-._\"'/]+\)"
    results = []
    for data in structure:
        if data.endswith(".js"):
            f = open(data, 'r')
            results += re.findall(q, f.read(), re.M)
    
    libs = {}
    q = "\".*\"|'.*'"
    p = "[\d\w\-]+$"
    for result in results:
        result = re.findall(q, result)
        if len(result) == 0:
            continue
        result = result[0]
        result = result.replace("'","").replace('"','').replace(".js","")
        result = re.findall(p,result)
        if len(result) == 0:
            continue
        result = result[0]

        if result in libs:
            libs[result] += 1
        else:
            libs[result] = 1

    return libs

def get_ruby_analysis(structure):
    return structure


def get_framework(path, deepest=0, framework=None, save=True):
    """ get_framework
        recieves a filesystem path of a project repository and
        classify into a framework project type.
        path is the filesystem directory
        deepest is how many detail will have the library analysis
        by default the program takes the full detail. zero is only
        for the library name.
        framework is the name of the framework used in the project
        use this only for training proposes
    """

    language = []
    ext = ""
    structure = get_structure(path)
    size = 0
    for x in structure:
        name, ext = os.path.splitext(x)
        if ext not in language:
            language.append(ext)

    result = None

    frameworks = []

    for ext in reversed(language):
        if ext == ".py":
            result = get_python_analysis(structure, deepest=0)
            if save:
                framework = closest_framework(result, ext, framework=framework.lower())
                frameworks.append(framework)
        elif ext == ".rb":
            result = get_ruby_analysis(structure)
        elif ext == ".js":
            result = get_javascript_analysis(structure)
        else:
            result = language

    return frameworks

if __name__ == "__main__":
    import doctest
    doctest.testmod()