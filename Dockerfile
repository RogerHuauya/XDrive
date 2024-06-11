FROM python:3.10


WORKDIR /usr/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y --no-install-recommends openssl libssl-dev swig libc6 libpq-dev git npm\
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN apt-get update \
    && apt-get install -y libgtk2.0-0 libgtk-3-0 libgbm-dev libnotify-dev libnss3 libxss1 libasound2 libxtst6 xauth xvfb


RUN pip install --upgrade pip
COPY ./requirements.txt /usr/app
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
