# Use an official Python runtime as the base image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/requirements.txt

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    libcairo2 \
    libcairo2-dev \
    libpango1.0-0 \
    libpangocairo-1.0-0 \
    libffi-dev \
    libgdk-pixbuf2.0-0 \
    libgdk-pixbuf2.0-dev \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*


# Upgrade setuptools and wheel
RUN pip install --upgrade setuptools wheel

# Install Python package backports.zoneinfo
RUN pip install --upgrade backports.zoneinfo

# Install Python dependencies
RUN pip install --no-cache-dir --timeout=600 -r /app/requirements.txt

# Copy the entire project into the container
COPY . /app

# Create the staticfiles directory in the container
RUN mkdir -p /app/flexibees_finance/static

# Create the staticfiles directory in the container
RUN mkdir -p /app/flexibees_finance/staticfiles

# Run collectstatic to gather static files
RUN python manage.py collectstatic --noinput

# Expose the ports for the application
EXPOSE 8000 8001 8002

# Command to run the Django application
CMD ["gunicorn", "flexibees_finance.wsgi:application", "--bind", "0.0.0.0:8000"]
