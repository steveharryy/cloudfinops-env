FROM python:3.10-slim

# Create a non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:${PATH}"
# Force Python to see the 'server' folder as a root package
ENV PYTHONPATH="/app:${PYTHONPATH}"

WORKDIR /app

# Copy requirements and install
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy everything else
COPY --chown=user . .

# HF Spaces run on port 7860
EXPOSE 7860

# Force uvicorn to run from server subpackage
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
