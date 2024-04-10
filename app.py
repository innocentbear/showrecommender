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
            {
                "role": "system",
                "content": """
                You are a helpful assistant that suggests movies and TV series based on users preferences. 
                Description shou
                Your task is to provide recommendations in a structured JSON-like format. 
                The format should be as follows: 
                "movies": [ 
                    { 
                        "title": "movie name1", 
                        "description": "An intriguing movie that will keep you on the edge of your seat.", 
                        "imdb": "imdb link1" 
                    }, 
                    { 
                        "title": "movie name2", 
                        "description": "A captivating movie that will leave you wanting more.", 
                        "imdb": "imdb link2" 
                    },
                    { 
                        "title": "movie name3", 
                        "description": "A thrilling movie that will keep you guessing until the end.", 
                        "imdb": "imdb link3" 
                    },
                    { 
                        "title": "movie name4", 
                        "description": "A heartwarming movie that will touch your soul.", 
                        "imdb": "imdb link4" 
                    }
                ], 
                "tvSeries": [ 
                    { 
                        "title": "tv series name1", 
                        "description": "An addictive TV series that will have you binge-watching all night.", 
                        "imdb": "imdb link1" 
                    }, 
                    { 
                        "title": "tv series name2", 
                        "description": "A gripping TV series that will keep you hooked from start to finish.", 
                        "imdb": "imdb link2" 
                    },
                    { 
                        "title": "tv series name3", 
                        "description": "A suspenseful TV series that will leave you craving for more episodes.", 
                        "imdb": "imdb link3" 
                    },
                    { 
                        "title": "tv series name4", 
                        "description": "An enchanting TV series that will transport you to a whole new world.", 
                        "imdb": "imdb link4" 
                    }
                ]. 
                You always return the JSON with no additional context or description.
                """
            },
        ]
        # Add user's favorite movies or series to the message text
        for favorite in favorites:
            message_text.append({"role": "user", "content": f"I enjoy watching {favorite}."})

        # Add request for recommendations to the message text
        message_text.append({"role": "user", "content": "Based on these, can you suggest other movies or series that I might also enjoy, grouped into a 'Movies' category and a 'TV Series' category, along with a short description and an IMDb link for each?"})

        # Make API call to Azure OpenAI
        completion = client.chat.completions.create(
            model="recommendations",  # model = "deployment_name"
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
