FROM python:3.8-slim

LABEL maintainer="Kyrielight"

ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Python depdencies
RUN apt-get update -y && \
    apt-get install -y git

COPY requirements.txt /opt/requirements.txt
RUN pip3 install -r /opt/requirements.txt && rm /opt/requirements.txt && apt-get remove -y git

COPY *.py /nana/

WORKDIR /nana
ENTRYPOINT ["python3", "main.py"]