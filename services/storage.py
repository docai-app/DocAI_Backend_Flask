import os
import pickle
from unittest import result
import uuid
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings
from services.database import DatabaseService
from services.ocr import OCRService

connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')


class StorageService:
    @staticmethod
    def upload(file, filename):
        try:
            blob_service_client = BlobServiceClient.from_connection_string(
                connect_str)
            blob_client = blob_service_client.get_blob_client(
                container='document-storage', blob=filename)
            blob_client.upload_blob(file, content_settings=ContentSettings(file.content_type))
            content = OCRService.getText(blob_client.url)
            document = DatabaseService.addNewDocument(filename, blob_client.url, content)
            return blob_client.url
        except Exception as e:
            return e

    @staticmethod
    def list():
        blob_service_client = BlobServiceClient.from_connection_string(
            connect_str)
        container_client = blob_service_client.get_container_client(
            "document-storage")
        try:
            for blob in container_client.list_blobs():
                print("Found blob: ", blob.name)
        except ResourceNotFoundError:
            print("Container not found.")

        labels = DatabaseService.getAllLabel()

        return labels
