from database.models.Labels import Labels
from utils.model import row2dict, rows2dict

class LabelsQueryService():
    @staticmethod
    def getAll():
        data = Labels.query.all()
        return rows2dict(data)
    
    @staticmethod
    def getSpecific(id):
        data = Labels.query.filter_by(id=id).first()
        return row2dict(data)