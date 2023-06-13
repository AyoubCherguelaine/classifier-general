from gradio_client import Client

client = Client("https://ayoubchlin-ayoubchlin-stable-bart-mnli-cnn.hf.space/",hf_token='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')
result = client.predict(
				"money is the best for politics",	# str  in 'Text' Textbox component
				"tech, power",	# str  in 'Labels' Textbox component
				api_name="/predict"
)
print(result)