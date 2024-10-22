#Django
FROM python:3.8
RUN apt-get update
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app
RUN pip install -r requirements.txt
#RUN python manage.py makemigrations
#RUN python manage.py migrate
#EXPOSE 8000
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
