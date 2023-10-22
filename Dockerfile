FROM python:3.11

WORKDIR /CCS_back

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .