# The package version is derived from git tags (setuptools-scm), so this
# stage needs the full .git history - it is never copied into the final
# image below.
FROM python:3.14-slim AS builder

# setuptools-scm shells out to git to derive the package version; the
# slim base image doesn't ship it.
RUN apt-get update \
    && apt-get install --no-install-recommends -y git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/local/GlobusAPI
COPY . ./
RUN pip install --upgrade pip build \
    && python -m build --wheel --outdir /tmp/dist .

FROM python:3.14-slim

RUN groupadd --gid 1000 globusapi \
    && useradd --uid 1000 --gid globusapi --no-create-home --shell /usr/sbin/nologin globusapi

WORKDIR /usr/local/GlobusAPI
COPY --from=builder /tmp/dist/*.whl /tmp/dist/
RUN pip install --upgrade pip \
    && pip install /tmp/dist/*.whl \
    && pip check \
    && python -c "import GlobusAPI" \
    && rm -rf /tmp/dist

USER globusapi

ENTRYPOINT ["python", "-m", "GlobusAPI"]
