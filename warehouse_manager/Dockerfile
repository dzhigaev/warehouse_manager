# pull official base image
FROM python:3.8

# set work directory
WORKDIR /home/dzhig/oursight_dev/warehouse_manager/warehouse_manager

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apt-get update \
    && apt-get install -y postgresql postgresql-contrib gcc python3-dev musl-dev

# install dependencies
RUN pip3 install --upgrade pip
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /home/dzhig/oursight_dev/warehouse_manager/warehouse_manager/entrypoint.sh
RUN chmod +x /home/dzhig/oursight_dev/warehouse_manager/warehouse_manager/entrypoint.sh

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/home/dzhig/oursight_dev/warehouse_manager/warehouse_manager/entrypoint.sh"]
