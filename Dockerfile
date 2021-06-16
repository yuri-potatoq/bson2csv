FROM python:3

ENV PROJECT="json2csv"

RUN apt update

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5500

CMD ["python", "./"]