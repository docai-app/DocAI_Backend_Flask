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