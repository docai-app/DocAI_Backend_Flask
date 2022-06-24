def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))
    return d

def rows2dict(rows):
    d = []
    for row in rows:
        d.append(row2dict(row))
    return d

def countEachLabelDocumentByDate2dict(rows):
    d = []
    for row in rows:
        item = {}
        item['id'] = row[0]
        item['name'] = row[1]
        item['count'] = row[2]
        d.append(item)
    return d