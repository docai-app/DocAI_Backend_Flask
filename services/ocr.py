import os
import time
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("AZURE_COMPUTER_VISION_KEY")
endpoint = os.getenv("AZURE_COMPUTER_VISION_ENDPOINT")

# Set credentials
credentials = CognitiveServicesCredentials(key)
# Create client
client = ComputerVisionClient(endpoint, credentials)


class OCRService:
    @staticmethod
    def azureOCR(filePath):
        # Async SDK call that "reads" the image
        response = client.read(str(filePath), raw=True)
        print("Response: ", response)
        # Get ID from returned headers
        operation_location = response.headers["Operation-Location"]
        operation_id = operation_location.split("/")[-1]

        # SDK call that gets what is read
        while True:
            time.sleep(1)
            result = client.get_read_result(operation_id)
            if result.status.lower() not in ['notstarted', 'running']:
                break
            print('Waiting for result...')
        return result

    @staticmethod
    def getText(filePath):
        text = ''
        result = OCRService.azureOCR(filePath)
        if result.status == OperationStatusCodes.succeeded:
            for readResult in result.analyze_result.read_results:
                for line in readResult.lines:
                    text += line.text
                print(text)
        return text
