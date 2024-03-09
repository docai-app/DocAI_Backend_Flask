import requests


class SimpleAPIRequester:
    def __init__(self, url, method='GET', body=None, headers=None):
        self.url = url
        self.method = method.upper()
        self.body = body
        self.headers = headers if headers is not None else {}
        # import pdb
        # pdb.set_trace()

    def send_request(self):
        try:
            # import pdb
            # pdb.set_trace()
            response = requests.request(method=self.method, url=self.url, json=self.body, headers=self.headers)
            response.raise_for_status()  # Raises HTTPError, if one occurred
            return response.json()  # Assuming the response is JSON
        except requests.exceptions.HTTPError as http_err:
            return f'HTTP error occurred: {http_err}'  # Return the HTTP error
        except Exception as err:
            return f'Other error occurred: {err}'  # Return any other error
