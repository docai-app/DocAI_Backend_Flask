# File Path: routes/api/smart_extraction_schema.py

from database.services.SmartExtractionSchemas import SmartExtractionSchemasQueryService
from services.smart_extraction import SmartExtractionService
from flask import Blueprint, jsonify, request

smart_extraction_schema = Blueprint('smart_extraction_schema', __name__)


@smart_extraction_schema.route('/smart_extraction_schema/views', methods=['POST'])
def createSmartExtractionSchemasViews():
    tenant = request.json['tenant']
    smartExtractionSchema = request.json['smart_extraction_schema']
    print(tenant, smartExtractionSchema)
    try:
        res = SmartExtractionSchemasQueryService.createSmartExtractionSchemasViews(
            tenant, smartExtractionSchema)
        return jsonify({'status': True, 'message': 'Smart Extraction Schema Views Created', 'views': res})
    except Exception as e:
        return jsonify({'status': False, 'message': 'Smart Extraction Schema Views Not Created'})


@smart_extraction_schema.route('/smart_extraction_schema/<id>/views', methods=['GET'])
def getSmartExtractionSchemasViews(id):
    tenant = request.json['tenant']
    dataSchema = request.json['data_schema']
    print("Tenant: ", tenant)
    print("Data Schema: ", dataSchema)
    try:
        res = SmartExtractionSchemasQueryService.getAllDataFromSmartExtractionSchemasViews(
            tenant, id, dataSchema)
        return jsonify({'status': True, 'views': res})
    except Exception as e:
        return jsonify({'status': False, 'message': 'Smart Extraction Schema Views not found'})
    
@smart_extraction_schema.route('/smart_extraction_schema/map_reduce', methods=['POST'])
def smartExtractionSchemaMapReduce():
    storage_url = request.json['storage_url']
    schema = request.json['schema']
    data_schema = request.json['data_schema']
    print("Storage URL: ", storage_url)
    print("Schema: ", schema)
    print("Data Schema: ", data_schema)
    try:
        res = SmartExtractionService.mapReduce(storage_url, schema, data_schema)
        return jsonify({'status': True, 'data': res})
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)})
