FROM python:3.11-slim
WORKDIR /app
RUN pip install requests
COPY anonaddy2sieve.py .
CMD ["python", "-u", "anonaddy2sieve.py"]