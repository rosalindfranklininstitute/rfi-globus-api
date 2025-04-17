FROM python:3.8

# Install python package
WORKDIR /usr/local/GlobusAPI
COPY . ./
RUN pip install --upgrade pip
RUN pip install -e .[dev]
RUN pip check

ENTRYPOINT ["python", "-m", "GlobusAPI"]
