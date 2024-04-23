# Use an official Nginx runtime as the base image
FROM nginx:alpine

# Copy the frontend directory contents into the container at /usr/share/nginx/html
COPY frontend/ /usr/share/nginx/html

# Make port 80 available to the world outside this container
EXPOSE 80

# Run Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]