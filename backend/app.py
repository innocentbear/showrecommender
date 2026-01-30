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
from openai import AzureOpenAI

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24))
CORS(app)
# CORS(app, origins=["https://moviepotter.com", "https://www.moviepotter.com"])

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
app.logger.setLevel(logging.INFO)


api_key = os.getenv("AZURE_OPENAI_API_KEY")
model_name = os.getenv("AZURE_OPENAI_MODEL_NAME", "gpt-4.1-nano")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", model_name)
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT","https://empower-test-foundry.openai.azure.com/")
api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")

# Initialize Azure OpenAI client using the documented pattern so the SDK manages auth and routing.
client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=azure_endpoint,
    api_key=api_key,
)

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
                "content": """You are a helpful assistant that suggests movies and TV series. Return ONLY valid JSON (no markdown, no extra text) with exactly this structure:
{
  "movies": [
    {"title": "name", "imdb": "https://www.imdb.com/title/...", "description": "...", "country": "..."}
  ],
  "tvSeries": [
    {"title": "name", "imdb": "https://www.imdb.com/title/...", "description": "...", "country": "..."}
  ]
}
Return at least 4 items in each category. Nothing else."""
            },
        ]
        # Add user's favorite movies or series and request for recommendations in a single message
        favorites_text = ", ".join(favorites) if favorites else "movies and TV series"
        user_message = f"I enjoy watching {favorites_text}. Based on these, can you suggest other movies or series that I might also enjoy, grouped into a 'Movies' category and a 'TV Series' category, along with a short description and an IMDb link for each?"
        message_text.append({"role": "user", "content": user_message})

        # Make API call to Azure OpenAI
        completion = client.chat.completions.create(
            model=deployment,
            messages=message_text,
            max_completion_tokens=16384,
            stream=False,
            frequency_penalty=0,
            presence_penalty=0,
            timeout=30,
        )
        # Extract recommendations from Azure OpenAI response
        if not completion.choices or not completion.choices[0].message.content:
            raise ValueError("Empty response from Azure OpenAI")
        
        recommendations_content = completion.choices[0].message.content
        # Parse response string into JSON
        try:
            dataJson = json.loads(recommendations_content)
        except json.JSONDecodeError as json_error:
            app.logger.error(f'Failed to parse JSON response: {json_error}')
            raise ValueError(f"Invalid JSON response from Azure OpenAI: {json_error}")
        
        # Validate the JSON structure
        if not isinstance(dataJson, dict) or 'movies' not in dataJson or 'tvSeries' not in dataJson:
            app.logger.error(f'Unexpected JSON structure: {dataJson}')
            raise ValueError("Response does not contain expected 'movies' and 'tvSeries' categories")

        # Check the country of each movie and series and update the IMDb link if necessary
        for category in ['movies', 'tvSeries']:
            if category not in dataJson or not isinstance(dataJson[category], list):
                app.logger.warning(f'Category "{category}" missing or not a list, skipping...')
                continue
            
            for item in dataJson[category]:
                if not isinstance(item, dict):
                    app.logger.warning(f'Invalid item format in {category}, skipping...')
                    continue
                    
                if item.get('country', '') == 'India':
                    imdb_id = get_imdb_id_from_omdb(item.get('title', ''))
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
    """Fetch the IMDb ID for a given title from the OMDb API."""
    if not title:
        return None
        
    omdb_api_key = os.getenv('OMDB_API_KEY')
    if not omdb_api_key:
        app.logger.error('OMDB_API_KEY not found in environment variables')
        return None
    
    try:
        response = requests.get(f"http://www.omdbapi.com/?t={title}&apikey={omdb_api_key}", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('Response') == 'False':
            app.logger.warning(f'Movie/series "{title}" not found in OMDb')
            return None
            
        imdb_id = data.get('imdbID')
        return imdb_id
    except requests.RequestException as e:
        app.logger.error(f'Failed to fetch IMDb ID for "{title}": {str(e)}')
        return None
    except (KeyError, ValueError) as e:
        app.logger.error(f'Error parsing OMDb response for "{title}": {str(e)}')
        return None

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
