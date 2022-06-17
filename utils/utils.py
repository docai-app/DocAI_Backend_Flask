def getRecursiveLookup(k, d):
    if k in d:
        return d[k]
    for item in d.values():
        if isinstance(item, dict):
            a = getRecursiveLookup(k, item)
            if a is not None:
                return a
    return None
            


def setRecursiveLookup(k, d, v):
    if k in d:
        d[k] = v
    for item in d.values():
        if isinstance(item, dict):
            a = setRecursiveLookup(k, item, v)
            if a is not None:
                return a
    return None


def getExtension(filename):
    return filename.split(".")[-1]
