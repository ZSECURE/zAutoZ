# ---------- build stage ----------
FROM python:3.11-slim AS builder
WORKDIR /build

# System packages your modules may need (example adds nmap)
RUN apt-get update && apt-get install -y --no-install-recommends \
        nmap \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# ---------- runtime stage ----------
FROM python:3.11-slim
ENV PATH="/usr/local/bin:/install/bin:${PATH}"
WORKDIR /app

# bring in the pre-installed site-packages from builder
COPY --from=builder /install /install
# copy any tools you installed in build stage (nmap shown as example)
COPY --from=builder /usr/bin/nmap /usr/bin/nmap

# copy project source
COPY . .

# run as non-root
RUN useradd -m web && chown -R web:web /app
USER web

# make sure these exist even if host volumes aren’t mounted yet
RUN mkdir -p /app/jobs /app/logs

EXPOSE 5000
ENV FLASK_APP=app.py
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
