from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail, Message
import os
import time  # Import time module to calculate response time
from openai import AzureOpenAI

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "6b727570616b6172737261767961")
CORS(app)



# Initialize AzureOpenAI client with your Azure OpenAI endpoint and API key
client = AzureOpenAI(
    azure_endpoint="https://playground1329.openai.azure.com/",
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-15-preview"
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

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK"})

@app.route('/api/recommendations', methods=['POST'])
@limiter.limit("5 per minute")  # Limit this endpoint to 5 requests per minute
def generate_recommendations():
    try:
        start_time = time.time()  # Record the start time
        # Get user favorites from request
        favorites = request.json.get('favorites', [])

        # Construct message text for AzureOpenAI
        message_text = [
            {
                "role": "system",
                "content": """
                You are a helpful assistant that suggests movies and TV series based on users preferences. 
                Description should make the viewer to watch movie immediately.
                Your task is to provide recommendations in a structured JSON-like format. 
                The format should be as follows: 
                "movies": [ 
                    { 
                        "title": "movie name1", 
                        "description": "description1 in single line", 
                        "imdb": "imdb link1",
                    }
                ], 
                "tvSeries": [ 
                    { 
                        "title": "tv series name1", 
                        "description": "description1", 
                        "imdb": "imdb link1",
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
            response_format={ "type": "json_object" },
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

        end_time = time.time()  # Record the end time (after API response)
        total_time = end_time - start_time  # Compute the total response time
        app.logger.info(f'Recommendation API call took {total_time:.2f} seconds.')
        # Return recommendations as JSON response
        return jsonify({'recommendations': recommendations})

    except Exception as e:
        end_time = time.time()
        total_time = end_time - start_time
        app.logger.error(f'Recommendation API call failed after {total_time:.2f} seconds with error: {str(e)}')
        return jsonify({'error': str(e)}), 500

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
