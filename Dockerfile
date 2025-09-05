FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    locales \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-por \
    && rm -rf /var/lib/apt/lists/*

RUN echo "pt_BR.UTF-8 UTF-8" >> /etc/locale.gen && \
    locale-gen pt_BR.UTF-8 && \
    update-locale LANG=pt_BR.UTF-8

ENV LANG pt_BR.UTF-8
ENV LANGUAGE pt_BR:pt
ENV LC_ALL pt_BR.UTF-8

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

COPY . .

RUN pip install poetry
RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi

RUN poetry run spacy download pt_core_news_lg

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "--host", "0.0.0.0", "arrange.app:app"]
