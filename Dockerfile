FROM python:3.6-slim-stretch

RUN apt-get update && apt-get install -y \
    libzbar0
    
COPY requirements.txt /
RUN pip install -r /requirements.txt

RUN mkdir /webapp
WORKDIR /webapp
COPY *.py /webapp/
COPY *.out /webapp/

RUN mkdir -p /webapp/templates
RUN mkdir -p /webapp/static
COPY ./templates/* /webapp/templates/
COPY ./static/* /webapp/static/


# default flask port
EXPOSE 5000
ENTRYPOINT ["python", "app.py"]
