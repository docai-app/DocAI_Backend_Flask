import os
import pickle
from unittest import result
import uuid
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings
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
            document = DatabaseService.addNewDocument(
                documentID, filename, blob_client.url, content)
            return document
        except Exception as e:
            return e

    @staticmethod
    def list():
        blob_service_client = BlobServiceClient.from_connection_string(
            connect_str)
        container_client = blob_service_client.get_container_client(
            container)
        try:
            for blob in container_client.list_blobs():
                print("Found blob: ", blob.name)
        except ResourceNotFoundError:
            print("Container not found.")

        labels = DatabaseService.getAllLabel()

        return labels
