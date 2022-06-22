from utils.utils import getRecursiveLookup, setRecursiveLookup
from services.database import DatabaseService
import json


class FormService():
    @staticmethod
    def mapAbsenceForm(form):
        formSchema = DatabaseService.getFormSchemaByName('請假表')
        dataSchema = json.loads(formSchema['data_schema'])
        try:
            for key, value in form.items():

                if value == 'selected':
                    value = True
                elif value == 'unselected':
                    value = False

                if getRecursiveLookup(key, dataSchema) is not None:
                    setRecursiveLookup(key, dataSchema, value)

        except Exception as e:
            print(e)
            pass

        return dataSchema

    @staticmethod
    def addNewFormData(data, name, documentID):
        try:
            formData = DatabaseService.addNewFormData(data, name, documentID)
            return formData
        except Exception as e:
            print(e)
            pass

    @staticmethod
    def updateFormDataByID(id, data):
        try:
            formData = DatabaseService.updateFormDataByID(id, data)
            return formData
        except Exception as e:
            print(e)
            pass
