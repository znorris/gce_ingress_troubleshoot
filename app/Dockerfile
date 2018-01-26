FROM python:3-alpine

COPY requirements.txt .
RUN pip install -r requirements.txt


COPY templates/root.html templates/root.html
COPY server.py .

EXPOSE 5000
CMD ["python", "server.py"]
