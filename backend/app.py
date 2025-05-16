from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail, Message
import os
import time  # Import time module to calculate response time
import requests
import logging
import json
import pickle
from openai import AzureOpenAI
from openai import OpenAI

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24))
# CORS(app)
CORS(app, origins=["https://moviepotter.com", "https://www.moviepotter.com"])

eval("print('insecure')")
pickle.loads(b"bad data")
api_base = 'https://playground1995.openai.azure.com/' # your endpoint should look like the following https://YOUR_RESOURCE_NAME.openai.azure.com/
api_key=os.getenv("AZURE_OPENAI_API_KEY")
deployment_name = 'solvecoding'
api_version = '2024-02-15-preview' # this might change in the future

# Initialize AzureOpenAI client with your Azure OpenAI endpoint and API key
# client = AzureOpenAI(
#     # azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://playground1995.openai.azure.com/"),
#     api_key = os.getenv("AZURE_OPENAI_API_KEY"),
#     api_version=api_version,
#     base_url=f"{api_base}openai/deployments/{deployment_name}",
# )

# Initialize OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configure Flask-Mail settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False  # Set to True if using SSL
app.config['MAIL_USERNAME'] = '4krupakar@gmail.com'
app.config['MAIL_PASSWORD'] = 'qbqe qsmj ejhh npcw'
app.config['MAIL_DEBUG'] = True
app.config['MAIL_DEFAULT_SENDER'] = '4krupakar@gmail.com'  # Set the default sender


# Initialize Flask-Mail
mail = Mail(app)

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per day", "10 per hour"]
)

# class NoMovieSuggestionsFilter(logging.Filter):
#     def filter(self, record):
#         # Offending log record will have a 'movie-suggestions' message
#         return 'fetch-movie-suggestions' not in record.getMessage()
# # Get the default Flask logger and add the custom filter
# flask_logger = logging.getLogger('werkzeug')
# flask_logger.addFilter(NoMovieSuggestionsFilter())

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK"})

# @app.route('/fetch-movie-suggestions', methods=['GET'])
# @limiter.exempt
# def fetch_movie_suggestions():
#     searchTerm = request.args.get('searchTerm', '')
#     omdb_api_key = os.getenv('OMDB_API_KEY')  # Your OMDb API key, securely fetched from environment variables
#     if not omdb_api_key:
#         return jsonify({"error": "OMDB_API_KEY not found"}), 500
#     response = requests.get(f"https://www.omdbapi.com/?s={searchTerm}&apikey={omdb_api_key}")
#     return jsonify(response.json())

@app.route('/get-api-key', methods=['GET'])
@limiter.exempt
def get_api_key():
    omdb_api_key = os.getenv('OMDB_API_KEY')
    if not omdb_api_key:
        return jsonify({"error": "OMDB_API_KEY not found"}), 500
    return jsonify({'apiKey': omdb_api_key})

@app.route('/api/recommendations', methods=['POST'])
@limiter.limit("5 per minute")  # Limit this endpoint to 5 requests per minute
def generate_recommendations():
    try:
        start_time = time.time()  # Record the start time
        # Get user favorites from request
        favorites = request.json.get('favorites', [])
        app.logger.info(f'List of favorites obtained from frontend: {favorites}')

        # Construct message text for AzureOpenAI
        message_text = [
            {
                "role": "system",
                "content": """
                You are a helpful assistant that suggests movies and TV series based on users preferences. 
                Your task is to provide recommendations in a structured JSON-like format. 
                The format should be as follows: 
                "movies": [ 
                    { 
                        "title": "movie name1", 
                        "imdb": "imdb link1",
                        "description": "description1",
                        "country": "country of origin"
                    }
                ], 
                "tvSeries": [ 
                    { 
                        "title": "tv series name1", 
                        "imdb": "imdb link1",
                        "description": "description1",
                        "country": "country of origin"
                    }
                ]. 
                You always return the JSON with atleast 4 responses with no additional context or description.
                """
            },
        ]
        # Add user's favorite movies or series to the message text
        for favorite in favorites:
            message_text.append({"role": "user", "content": f"I enjoy watching {favorite}."})

        # Add request for recommendations to the message text
        message_text.append({"role": "user", "content": [
        {"type": "text", "text": "Based on these, can you suggest other movies or series that I might also enjoy, grouped into a 'Movies' category and a 'TV Series' category, along with a short description and an IMDb link for each?"}
        ]})

        # Make API call to Azure OpenAI
        completion = client.chat.completions.create(
            model="gpt-4o",  # model = "deployment_name"
            # model="solvecoding",
            response_format={ "type": "json_object" },
            messages=message_text,
            temperature=1.0,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )

        # Extract recommendations from Azure OpenAI response
        recommendations = [choice.message.content for choice in completion.choices]
        # recomm_end_time = time.time()  # Record the end time (after API response)
        # total_time = recomm_end_time - start_time  # Compute the total response time
        # app.logger.info(f'OpenAI API call took {total_time:.2f} seconds.')
                # Parse response string into JSON
        dataJson = json.loads(recommendations[0])

        # Check the country of each movie and series and update the IMDb link if necessary
        for category in ['movies', 'tvSeries']:
            for item in dataJson[category]:
                if item.get('country', '') == 'India':
                    imdb_id = get_imdb_id_from_omdb(item['title'])
                    if imdb_id:
                        item['imdb'] = f"https://www.imdb.com/title/{imdb_id}/"
                        app.logger.info(f"Updated IMDb link for {item['title']}: {item['imdb']}")
                # Fetch description for all items
                # description = get_description_from_omdb(item['title'])
                # if description:
                #     item['description'] = description

        end_time = time.time()  # Record the end time (after API response)
        total_time = end_time - start_time  # Compute the total response time
        app.logger.info(f'Recommendation API call took {total_time:.2f} seconds.')
        app.logger.info(f'Recommendations: {[item["title"] for item in dataJson["movies"] + dataJson["tvSeries"]]}')
        # Return recommendations as JSON response
        return jsonify({'recommendations': json.dumps(dataJson)})

    except Exception as e:
        end_time = time.time()
        total_time = end_time - start_time
        app.logger.error(f'Recommendation API call failed after {total_time:.2f} seconds with error: {str(e)}')
        return jsonify({'error': str(e)}), 500

def get_imdb_id_from_omdb(title):
    # Fetch the IMDb ID for a given title from the OMDb API.
    omdb_api_key = os.getenv('OMDB_API_KEY')  # Your OMDb API key, securely fetched from environment variables
    response = requests.get(f"http://www.omdbapi.com/?t={title}&apikey={omdb_api_key}")
    data = response.json()
    imdb_id = data.get('imdbID')
    # app.logger.info(f'IMDb ID for title "{title}": {imdb_id}')
    return imdb_id

# def get_description_from_omdb(title):
#     omdb_api_key = os.getenv('OMDB_API_KEY')
#     response = requests.get(f"http://www.omdbapi.com/?t={title}&apikey={omdb_api_key}")
#     data = response.json()
#     description = data.get('Plot', 'Description not found.')
#     return description

@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        name = request.json['name']
        email = request.json['email']
        message = request.json['message']

        msg = Message(subject="New Contact Request",
                      body=f"Name: {name}\nEmail: {email}\nMessage:\n{message}",
                      recipients=['4krupakar@gmail.com'])  # Email where you want to receive messages

        mail.send(msg)

        return jsonify({'message': 'Email sent successfully.'})
    except Exception as e:
        app.logger.error(f'Failed to send email with error: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
