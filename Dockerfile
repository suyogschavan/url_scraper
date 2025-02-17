# Use the official Python image from the Docker Hub
FROM python:3-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies

# Copy the rest of the application code into the container
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["hypercorn", "realmain:app", "--bind", "::"]
