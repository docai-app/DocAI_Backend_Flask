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
    def addNewFormData(data, name):
        try:
            formData = DatabaseService.addNewFormData(data, name)
            return formData
        except Exception as e:
            print(e)
            pass