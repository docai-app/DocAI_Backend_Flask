import os
import pickle
from unittest import result
import uuid
from azure.storage.blob import BlobServiceClient, ContentSettings
from database.services.Documents import DocumentsQueryService
from services.database import DatabaseService
from services.ocr import OCRService
from utils.utils import getExtension

connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
container = os.getenv('AZURE_STORAGE_CONTAINER')


class StorageService:
    @staticmethod
    def upload(file, filename):
        try:
            documentID = uuid.uuid4()
            file.filename = str(documentID) + '.' + getExtension(filename)
            blob_service_client = BlobServiceClient.from_connection_string(
                connect_str)
            blob_client = blob_service_client.get_blob_client(
                container=container, blob=file.filename)
            blob_client.upload_blob(
                file, content_settings=ContentSettings(file.content_type))
            content = OCRService.getText(blob_client.url)
            document = DocumentsQueryService.insert(
                documentID, filename, blob_client.url, content)
            return document
        except Exception as e:
            return e

    @staticmethod
    def uploadBulkWithSameLabel(file, filename, label_id):
        try:
            documentID = uuid.uuid4()
            file.filename = str(documentID) + '.' + getExtension(filename)
            blob_service_client = BlobServiceClient.from_connection_string(
                connect_str)
            blob_client = blob_service_client.get_blob_client(
                container=container, blob=file.filename)
            blob_client.upload_blob(
                file, content_settings=ContentSettings(file.content_type))
            content = OCRService.getText(blob_client.url)
            document = DocumentsQueryService.insert(
                documentID, filename, blob_client.url, content, label_id, status='confirmed')
            return document
        except Exception as e:
            return e
