FROM python:3.11-slim
#starts a lightweight python 3.11 image

WORKDIR /app
#sets /app as the working directory inside the container

COPY requirements.txt .
#copies the dependency list into the image

RUN pip install --no-cache-dir -r requirements.txt
#installs the required python packages

COPY src/ ./src/
#copies the ETL source code into the image

COPY sql/ ./sql/
#includes the SQL files in case the applications need them

CMD ["python", "-m", "src.etl.pipeline"]
#defines the command to execute when the container starts