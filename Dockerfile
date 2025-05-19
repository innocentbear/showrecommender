# Use Node.js to obfuscate JavaScript files
FROM node:14 as build-stage
WORKDIR /app
COPY frontend/js/ ./js
RUN npm install --global javascript-obfuscator
RUN for jsfile in $(find ./js -name "*.js"); do javascript-obfuscator $jsfile --output $jsfile; done

# Use an official Nginx runtime as the base image
FROM nginx:alpine
# Copy the frontend directory contents into the container at /usr/share/nginx/html
COPY frontend/ /usr/share/nginx/html
# Copy obfuscated JavaScript files from the build stage
COPY --from=build-stage /app/js /usr/share/nginx/html/js
# Make port 80 available to the world outside this container
EXPOSE 80
# Run Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]
