FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md /app/
COPY src /app/src
COPY configs /app/configs
COPY domain-packs /app/domain-packs
RUN pip install --no-cache-dir -e .
CMD ["python", "-m", "didactopus.main", "--domain", "statistics", "--goal", "practical mastery"]
