FROM python:3
ENV PYTHONPATH ./code
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY ./requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . /code

EXPOSE 7000
