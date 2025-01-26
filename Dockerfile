FROM python:3-alpine

WORKDIR /network-monitoring

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY LICENSE .
COPY README.md .

COPY network-monitoring.py .

CMD ["python","-u","network-monitoring.py"]
