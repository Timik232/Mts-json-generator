FROM python:3.10-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-root
COPY json_generator ./json_generator
COPY data ./data
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
CMD ["python", "-m", "json_generator"]
