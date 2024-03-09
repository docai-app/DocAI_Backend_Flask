import re, json

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

def cleansingContentFromGpt(content):
    json_regex = r'\{[\s\S]*?\}'
    json_match = re.search(json_regex, content)

    if json_match:
        json_str = json_match.group()
        print(f"json_str: {json_str}")
        try:
            json_obj = json.loads(json_str)
            print(f"json_obj: {json_obj}")
            return json_obj
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return {}
    else:
        print('No JSON found in the paragraph')
        return {}