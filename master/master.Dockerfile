FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r ../http.reqs.txt -r ../amqp.reqs.txt
COPY ./main.py ./invokes.py ../amqp_connection.py ./
CMD [ "python", "./main.py" ]

