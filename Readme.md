# Build the Docker image
docker build -t my-frontend .

# Run the Docker container
docker run -p 8080:80 my-frontend

# Build the Docker image
docker build -t my-backend -f Dockerfile.backend .

# Run the Docker container
docker run -p 5000:5000 -e AZURE_OPENAI_API_KEY=bc3f3f7785f941a8afb5421910cdb70c my-backend