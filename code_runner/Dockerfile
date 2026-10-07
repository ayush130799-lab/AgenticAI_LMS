FROM python:3.11-slim

# Non-root user; the sandbox subprocesses inherit it.
RUN useradd --system --no-create-home --uid 10001 runner
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py sandbox.py ./

USER runner
EXPOSE 9000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9000"]
