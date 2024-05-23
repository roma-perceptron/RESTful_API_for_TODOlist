# dockerfile
FROM python:3.10-slim

COPY . /RESTful_API_for_TODOlist
COPY requirements.txt /RESTful_API_for_TODOlist/requirements.txt

RUN pip install -r /RESTful_API_for_TODOlist/requirements.txt

WORKDIR /RESTful_API_for_TODOlist

EXPOSE 5000

CMD ["python", "-u", "main.py"]
