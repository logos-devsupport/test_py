
#FROM python:3.7
FROM quay.io/silvandrici/qiot-sensor-service-base:1.0.1

# imposta working directory
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copia codice sorgente
COPY src/ .

EXPOSE 5000
# command to run on container start
CMD [ "python", "./main.py" ]

