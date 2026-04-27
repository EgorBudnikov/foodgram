FROM python
RUN pip install --upgrade pip
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . . 
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]
