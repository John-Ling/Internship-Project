FROM python:3.10-alpine
WORKDIR /app
COPY src/api/ ./api/
COPY requirements.txt .
RUN pip3 install -r requirements.txt
EXPOSE 8080
CMD ["python3", "./api/main.py"]