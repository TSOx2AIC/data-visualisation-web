FROM python:3.8

WORKDIR /app

# Install dependenvies
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

# Copy source
COPY . .

# Entrypoint
EXPOSE 8501
CMD [ "streamlit", "run", "main.py" ]