# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on (default for Flask is 5000)
EXPOSE 5000

# Define the command to run the app using Gunicorn:
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "fix_log_analyzer:app"]
