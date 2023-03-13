FROM python:3.10-slim AS base
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends curl git build-essential \
    && apt-get autoremove -y
ENV POETRY_HOME="/opt/poetry"
RUN curl -sSL https://install.python-poetry.org | python3 -

FROM base AS install
WORKDIR /home/code

# allow controlling the poetry installation of dependencies via external args
ARG INSTALL_ARGS="--no-root --only main"
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
COPY pyproject.toml poetry.lock ./

# install without virtualenv, since we are inside a container
RUN poetry config virtualenvs.create false \
    && poetry install $INSTALL_ARGS

# cleanup
RUN curl -sSL https://install.python-poetry.org | python3 - --uninstall
RUN apt-get purge -y curl git build-essential \
    && apt-get clean -y \
    && rm -rf /root/.cache \
    && rm -rf /var/apt/lists/* \
    && rm -rf /var/cache/apt/*

FROM install as app-image

COPY api api
COPY .env ./

# create a non-root user and switch to it, for security.
RUN addgroup --system --gid 1001 "scrapers-house"
RUN adduser --system --uid 1001 "scrapers-house"
USER "scrapers-house"
CMD ["uvicorn", "api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8989"]
# pull crawlab
FROM crawlabteam/crawlab-backend:latest AS backend-build

FROM crawlabteam/crawlab-frontend:latest AS frontend-build

FROM crawlabteam/crawlab-public-plugins:latest AS public-plugins-build

# images
FROM crawlabteam/crawlab-base:latest

# add files
COPY ./backend/conf /app/backend/conf
COPY ./nginx /app/nginx
COPY ./bin /app/bin

# copy backend files
RUN mkdir -p /opt/bin
COPY --from=backend-build /go/bin/crawlab /opt/bin
RUN cp /opt/bin/crawlab /usr/local/bin/crawlab-server

# copy frontend files
COPY --from=frontend-build /app/dist /app/dist

# copy public-plugins files
COPY --from=public-plugins-build /app/plugins /app/plugins

# copy nginx config files
COPY ./nginx/crawlab.conf /etc/nginx/conf.d

# start backend
CMD ["/bin/bash", "/app/bin/docker-init.sh"]

