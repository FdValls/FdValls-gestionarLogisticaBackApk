FROM python:3.9.5
ENV PYTHONUNBUFFERED=1
# RUN python -m pip install --upgrade pip
RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev && apt-get clean
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./backend_django /app
RUN apt-get update && apt-get -y install vim
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]