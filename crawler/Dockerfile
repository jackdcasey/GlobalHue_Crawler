FROM python:3.8

# Install dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg

# Copy app
COPY . /app
WORKDIR /app

# Install python dependencies
RUN pip install -r requirements.txt

# Start
CMD python ./main.py

