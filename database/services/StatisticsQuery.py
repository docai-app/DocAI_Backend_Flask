from database.models.Labels import Labels
from utils.model import row2dict, rows2dict, countEachLabelDocumentByDate2dict
from ext import db


class StatisticsQueryService():
    @staticmethod
    def countEachLabelDocumentByDate(date):
        data = db.session.execute("SELECT D.label_id, L.name, COUNT(D.id) as count FROM documents AS D LEFT JOIN labels AS L ON D.label_id = L.id WHERE CAST(D.created_at AS DATE) = :date GROUP BY (D.label_id, L.name) ORDER BY COUNT(D.id) DESC", {
                                  'date': date}).fetchall()
        return countEachLabelDocumentByDate2dict(data)
