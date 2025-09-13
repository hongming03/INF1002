# Use an official lightweight Python image
FROM python:3.11-slim

# Set work directory inside the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your project files into the container
COPY . .

# Expose port Flask will run on
EXPOSE 5000

# Run the Flask app
CMD ["python", "src/app.py"]
