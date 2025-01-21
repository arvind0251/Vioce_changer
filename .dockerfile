# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt into the container at /app
COPY requirements.txt /app/

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app's code into the container
COPY . /app/

# Make port 5000 available to the world outside the container
EXPOSE 5000

# Define environment variable
ENV PYTHONUNBUFFERED 1

# Run the app when the container launches
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
