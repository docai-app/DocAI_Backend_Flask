import json


def row2dict(row):
    d = {}
    if row:
        for column in row.__table__.columns:
            if isinstance(getattr(row, column.name), dict):
                d[column.name] = json.dumps(getattr(row, column.name))
            else:
                d[column.name] = str(getattr(row, column.name))
    return d


def rows2dict(rows):
    d = []
    if isinstance(rows, list):
        for row in rows:
            d.append(row2dict(row))
    else:
        d = row2dict(rows)
    return d


def rowsWithRelationship2dict(rows, relationships):
    d = []
    for row in rows:
        item = row2dict(row)
        for relationship in relationships:
            item[relationship] = rows2dict(row.__getattribute__(relationship))
        d.append(item)
    return d


def rowsKeyFromSingleQuotation2doubleQuotation(rows, keys):
    if isinstance(rows, list):
        for row in rows:
            for key in keys:
                tempJSON = json.loads(row[key])
                row[key] = json.dumps(tempJSON)
    else:
        for key in keys:
            tempJSON = json.loads(rows[key])
            rows[key] = json.dumps(tempJSON)
    return rows


def countEachLabelDocumentByDate2dict(rows):
    d = []
    for row in rows:
        item = {}
        item['id'] = row[0]
        item['name'] = row[1]
        item['count'] = row[2]
        d.append(item)
    return d


def getDocumentsLabel2dict(rows):
    d = []
    for row in rows:
        item = {}
        item['id'] = row[0]
        item['name'] = row[1]
        d.append(item)
    return d
