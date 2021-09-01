# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8

WORKDIR /app
# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "main.py"]
