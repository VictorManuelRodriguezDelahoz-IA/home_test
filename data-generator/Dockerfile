FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy data generator script
COPY data_generator.py .

# Make script executable
RUN chmod +x data_generator.py

CMD ["python", "data_generator.py"]