from . import text_processing
import json
from gradio_client import Client
from . import config

client = Client("https://ayoubchlin-ayoubchlin-stable-bart-mnli-cnn.hf.space/", hf_token='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')


def pred(text):
    try:
        labels = ", ".join(config.labels)  # Assuming `config.labels` is imported from the `config` module

        preprocessed_text = text_processing.preprocess_text(text)
        result = client.predict(
            preprocessed_text,
            labels,
            api_name="/predict"
        )
        
        with open(result, 'r') as file:
            json_data = json.load(file)
        
        print(json_data)
        return json_data["label"]

    except Exception as e:
        # Handle specific exceptions and provide appropriate responses or error messages
        print(f"Exception: {e}")
        return None
