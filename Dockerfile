FROM python:3.10-alpine
WORKDIR /app
COPY ./requirements.txt .
RUN apk add gcc python3-dev musl-dev linux-headers
RUN pip install -r requirements.txt
COPY . .
# CMD [ "python","-m","main" ]
CMD [ "python","-u","app.py" ]
