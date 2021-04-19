import re

def remove_file_extension(name):
    return re.sub("\.[a-zA-z\d]*$", "", name)

def get_extension(name):
    res = re.search("\.[a-zA-z\d]*$", name)
    if (res): 
        return res.group(0)
    else: 
        return ''