from database.services.StatisticsQuery import StatisticsQueryService
from flask import Blueprint, jsonify

statistics = Blueprint('statistics', __name__)


@statistics.route('/count/document/<date>', methods=['GET'])
def countEachLabelDocumentByDate(date):
    try:
        res = StatisticsQueryService.countEachLabelDocumentByDate(date)
        print(res)
        return jsonify({'status': True, 'documents': res})
    except Exception as e:
        return jsonify({'status': False, 'message': 'No document found'})
