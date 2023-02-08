FROM python:3.9

ADD app.py .
ADD requirements.txt .

RUN pip install "./requirements.txt"

ENTRYPOINT ["python", "app.py"]