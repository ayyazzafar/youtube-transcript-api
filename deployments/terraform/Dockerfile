# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Download and install the CA certificate and curl
RUN apt-get update && \
    apt-get install -y ca-certificates curl && \
    curl -o /usr/local/share/ca-certificates/ca.crt https://raw.githubusercontent.com/luminati-io/luminati-proxy/master/bin/ca.crt && \
    update-ca-certificates

# Copy the SSL certificate to a known location
COPY ca.crt /usr/local/share/ca-certificates/ca.crt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
