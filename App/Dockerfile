FROM python:3.9

WORKDIR /App

COPY ./requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /App

EXPOSE 3000

CMD ["uvicorn", "main:app", "--reload", "--port=3000", "--host=0.0.0.0" ]