FROM python:3.12.7

RUN apt-get install wget
RUN pip install pandas sqlalchemy psycopg2

WORKDIR /app
COPY load-data.py load-data.py 

ENTRYPOINT [ "python", "load-data.py" ]