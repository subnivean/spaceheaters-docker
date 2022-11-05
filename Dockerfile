FROM python:3.10

COPY requirements.txt .

RUN python -mpip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# `/app` is mounted to the `src` dir in the
# `docker run` command.
WORKDIR /app
COPY ./src .

COPY ./bash.bashrc /root/.bashrc

RUN mkdir /data

#CMD ["python", "app.py"]
