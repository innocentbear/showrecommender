from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from openai import AzureOpenAI

app = Flask(__name__)
CORS(app)

# Initialize AzureOpenAI client with your Azure OpenAI endpoint and API key
client = AzureOpenAI(
    azure_endpoint="https://playground1329.openai.azure.com/",
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-15-preview"
)


@app.route('/api/recommendations', methods=['POST'])
def generate_recommendations():
    try:
        # Get user favorites from request
        favorites = request.json.get('favorites', [])

        # Construct message text for AzureOpenAI
        message_text = [
            {"role": "system", "content": "You are an AI assistant that helps people find information about movies or series."}
        ]

        # Add user's favorite movies or series to the message text
        for favorite in favorites:
            message_text.append({"role": "user", "content": f"I enjoy watching {favorite}."})

        # Add request for recommendations to the message text
        message_text.append({"role": "user", "content": "Based on these, can you suggest other movies or series that I might also enjoy, grouped into a 'Movies' category and a 'TV Series' category, along with a short description and an IMDb link for each?"})

        # Make API call to Azure OpenAI
        completion = client.chat.completions.create(
            model="recommendations",  # replace this with your model name
            messages=message_text,
            temperature=0.7,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )

        # Extract recommendations from Azure OpenAI response
        recommendations = [choice.message.content for choice in completion.choices]

        # Return recommendations as JSON response
        return jsonify({'recommendations': recommendations})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
