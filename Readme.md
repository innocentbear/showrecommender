## Access the Website

You can access the website at [moviepotter.com](https://moviepotter.com/).

## Build and Run Docker Containers

To build and run the Docker containers for the frontend and backend, follow these steps:

1. Build the Docker image for the frontend:
    ```bash
    docker build -t my-frontend .
    ```

2. Run the Docker container for the frontend:
    ```bash
    docker run -p 8080:80 my-frontend
    ```

3. Build the Docker image for the backend:
    ```bash
    docker build -t my-backend -f Dockerfile.backend .
    ```

4. Run the Docker container for the backend:
    ```bash
    docker run -p 5000:5000 -e AZURE_OPENAI_API_KEY=bc3f3f7785941a8afb5421910cdb70c my-backend
    ```

## Flask App APIs

The code defines a Flask app that exposes several functionalities through APIs:

- `/health`: Checks the health of the application and returns "OK" if healthy.
- `/fetch-movie-suggestions`: Retrieves movie suggestions based on a search term using the OMDb API.
- `/get-api-key`: Potentially provides an OMDb API key
- `/api/recommendations`: Generates recommendations for movies and TV shows based on a user's favorite list using AzureOpenAI. This API is rate-limited to 5 requests per minute.
- `/send-email`: Sends an email with a contact message to a predefined recipient.
