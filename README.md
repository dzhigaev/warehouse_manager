# warehouse_manager
***

* .env.dev
* .env.prod
* .env.prod.db
* .gitignore
* warehouse_manager
   * Dockerfile
   * Dockerfile.prod
   * entrypoint.prod.sh
   * entrypoint.sh
   * api
     * ...
   * files
     * ...
   * main
     * ...
   * core
      * __init__.py
      * asgi.py   
      * settings.py
      * urls.py
      * wsgi.py
   * manage.py
   * requirements.txt
* nginx
  * Dockerfile
  * nginx.conf
* postgres:
  * ...sql
* docker-compose.prod.yml
* docker-compose.yml

1. Create .env.prod and add variables:
    DEBUG=0

    ROSER_LOGIN_POST_URL=

    ROSER_MANIFEST_URL=

    ROSER_LOGIN_CREDS=

    SECRET_KEY=

    DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]

    SQL_ENGINE=django.db.backends.postgresql

    SQL_DATABASE=

    SQL_USER=

    SQL_PASSWORD=

    SQL_HOST=

    SQL_PORT=

    DATABASE=
2. Create .env.prod.db and add variables:
    POSTGRES_USER=user

    POSTGRES_PASSWORD=your_pass
    
    POSTGRES_DB=db_name
3. `chmod +x app/entrypoint.prod.sh`
4. Run these commands:
```commandline
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear
```

In order to see logs: 
```commandline
docker-compose -f docker-compose.prod.yml logs -f
```

Dump postgres:
```commandline
docker exec -i pg_container_name /bin/bash -c "PGPASSWORD=pg_password pg_dump --username pg_username database_name" > /desired/path/on/your/machine/dump.sql
```
Load postgres:
```commandline
docker exec -i pg_container_name /bin/bash -c "PGPASSWORD=pg_password psql --username pg_username database_name" < /path/on/your/machine/dump.sql
```