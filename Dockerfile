FROM python:3.12-slim
RUN pip install flask wakeonlan
COPY app.py /app/
CMD ["python", "/app/app.py"]