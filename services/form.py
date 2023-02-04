from database.services.FormSchemas import FormSchemasQueryService
from utils.utils import getRecursiveLookup, setRecursiveLookup
from services.database import DatabaseService
import json


class FormService():
    @staticmethod
    def mapAbsenceForm(form):
        formSchema = FormSchemasQueryService.getFormSchemasByName('請假表')
        dataSchema = json.loads(formSchema['data_schema'])
        try:
            for key, value in form.items():

                if value == ':selected:':
                    value = True
                elif value == ':unselected:':
                    value = False

                if getRecursiveLookup(key, dataSchema) is not None:
                    setRecursiveLookup(key, dataSchema, value)

        except Exception as e:
            print(e)
            pass

        return dataSchema

    @staticmethod
    def mapForm(form, model_id):
        formSchema = FormSchemasQueryService.getFormSchemasByModelId(model_id)
        dataSchema = json.loads(formSchema['data_schema'])
        try:
            for key, value in form.items():

                if value == ':selected:':
                    value = True
                elif value == ':unselected:':
                    value = False

                if getRecursiveLookup(key, dataSchema) is not None:
                    setRecursiveLookup(key, dataSchema, value)

        except Exception as e:
            print(e)
            pass

        return dataSchema

    @staticmethod
    def addNewDocumentsApproval(documentID, approvedBy):
        try:
            return DatabaseService.addNewDocumentsApproval(documentID, approvedBy)
        except Exception as e:
            print(e)
            pass
