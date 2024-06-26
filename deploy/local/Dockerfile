FROM python:3.11-alpine

# Set the working directory to it
WORKDIR /opt/invitations

# Copy the worker files into the container
COPY ./code ./app

# Install cargo package manager (needed for orjson dependency)
RUN apk add cargo gcc musl-dev libffi-dev openssl-dev python3-dev make

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN python3 -m pip install -r ./app/requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]