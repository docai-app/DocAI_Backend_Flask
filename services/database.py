from database.services.FormSchemas import FormSchemasQueryService
from utils.model import row2dict
from database.models.FormSchemas import FormSchemas
from ext import db


class DatabaseService():
    @staticmethod
    def searchFormByLabelAndDate(label, date):
        formSchema = FormSchemas.query.filter(
            FormSchemas.name == label).first()
        formData = db.session.execute(
            "SELECT F, D.storage_url FROM forms_data AS F JOIN documents AS D ON F.document_id = D.id WHERE F.schema_id==:id AND CAST(F.created_at AS DATE) = :date", {"id": formSchema.id, "date": date}).all()
        return {'form_schema': row2dict(formSchema), 'form_data': formData}
