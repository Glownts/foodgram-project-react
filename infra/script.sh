docker-compose up -d --build
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py load_data
docker-compose exec backend python manage.py createsuperuser --email admin@mail.ru --username admin --first_name admin --last_name admin
