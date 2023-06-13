import requests
from . import text_processing

session = requests.Session()

def pred(text):
    try:
        text = text_processing.preprocess_text(text)
        
        if text is None:
            return None
        
        response = session.post("https://team-language-detector-languagedetector.hf.space/run/predict", json={"data": [text]}).json()
        print(response)
        if response is not None :
            data = response["data"]
            return data[0]["label"]
        
    except requests.exceptions.RequestException as e:
        # Handle specific exceptions for network or connection errors
        print(f"RequestException: {e}")
    except ValueError as e:
        # Handle specific exception for JSON decoding errors
        print(f"ValueError: {e}")
    except Exception as e:
        # Handle any other exceptions
        print(f"Exception: {e}")
    
    return None
