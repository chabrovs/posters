FROM python:3.10-slim 

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN adduser --disabled-password serverus

WORKDIR /posters

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gettext \
    vim \
    curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

RUN python3 posters/manage.py collectstatic --noinput

WORKDIR /posters/posters

USER serverus

CMD ["gunicorn", "posters.wsgi:application", "--bind", "0.0.0.0:8000"]