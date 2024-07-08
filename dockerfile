FROM python:3.9-slim

WORKDIR /app

COPY src/ ./src/
COPY static/ ./static/
COPY templates/ ./templates/

RUN pip install --no-cache-dir flask flask_sqlalchemy
RUN pip install --no-cache-dir elasticsearch requests
RUN pip install --no-cache-dir Werkzeug

EXPOSE 5000

ENV FLASK_APP src/app.py

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]