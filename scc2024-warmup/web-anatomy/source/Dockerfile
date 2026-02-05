# Base image using Python 3 on Alpine Linux
FROM python:3-alpine

# Upgrade the pip package installer
RUN python -m pip install --upgrade pip

# Create /app directory for our application
RUN mkdir -p /app

# Set /app as the working directory
WORKDIR /app

# Copy the challenge app files to /app in the container
COPY challenge .

# Install dependencies from the requirements.txt file
RUN pip install -r requirements.txt

# Declare the port the app runs on
EXPOSE 1337

# Prevent Python from generating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Run the application
CMD ["python", "run.py"]
