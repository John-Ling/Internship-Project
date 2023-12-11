FROM python:3.10-alpine
WORKDIR /app
COPY src/api/ .
RUN pip3 install -r requirements.txt
EXPOSE 8080
CMD ["python3", "main.py"]