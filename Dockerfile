
FROM python:2.7

MAINTAINER Dave Kludt

ADD . /pitchfork
WORKDIR /pitchfork

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
