from database.services.FormsSchema import FormsSchemaQueryService
from utils.model import row2dict

from database.models.FormsData import FormsData
from database.models.FormsSchema import FormsSchema
from database.models.Labels import Labels
from ext import db


class DatabaseService():
    @staticmethod
    def searchFormByLabelAndDate(label, date):
        # formSchema = query_db(
        #     "SELECT * FROM forms_schema WHERE name LIKE ?", ['%' + label + '%'], one=True)
        formSchema = FormsSchema.query.filter(
            FormsSchema.name.like(f'%{label}%')).first()
        print(formSchema)
        # formData = query_db(
        #     "SELECT *, D.storage FROM forms_data AS F JOIN documents AS D ON F.document_id = D.id WHERE F.schema_id==? AND F.created_at LIKE ?", [formSchema['id'], '%'+date+'%'])
        formData = db.session.execute(
            "SELECT F, D.storage_url FROM forms_data AS F JOIN documents AS D ON F.document_id = D.id WHERE F.schema_id==:id AND CAST(F.created_at AS DATE) = :date", {"id": formSchema.id, "date": date}).all()
        print(formData)
        return {'form_schema': row2dict(formSchema), 'form_data': formData}
