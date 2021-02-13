FROM alpine

RUN apk update && \
    apk add python3 curl && \
    curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | python3 && \
    apk del curl

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt

COPY app.py /app.py

CMD [ "python3", "/app.py" ]