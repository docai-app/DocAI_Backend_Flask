from utils.model import row2dict, rows2dict, rowsWithRelationship2dict
from ext import db


class SmartExtractionSchemasQueryService():
    @staticmethod
    def createSmartExtractionSchemasViews(tenant, smartExtractionSchema):
        selectString = ""
        try:
            print("Smart Extraction Schema Data Schema Keys: ",
                  smartExtractionSchema['data_schema'].keys())
            for schema in smartExtractionSchema['data_schema'].keys():
                # Quoting column names
                selectString += f"data->>'{schema}' AS \"{schema}\", "
            print("Select String: ", selectString)

            # Quoting table and view names
            query = (
                f'CREATE VIEW "{tenant}"."smart_extraction_schema_{smartExtractionSchema["id"]}"'
                f' AS SELECT {selectString[:-2]} FROM "{tenant}"."document_smart_extraction_data";'
            )

            print("Query: ", query)

            views = db.session.execute(query)
            print("Views: ", views)
            return True
        except Exception as e:
            print(e)
            pass

    @staticmethod
    def getAllDataFromSmartExtractionSchemasViews(tenant, id, smartExtractionSchemaDataSchema):
        try:
            query = (
                f'SELECT * FROM "{tenant}"."smart_extraction_schema_{id}";'
            )
            print("Query: ", query)

            data = db.session.execute(query)
            print(data)
            for row in data:
                print(row)
            return rowsWithRelationship2dict(data, smartExtractionSchemaDataSchema)
        except Exception as e:
            print(e)
            pass
