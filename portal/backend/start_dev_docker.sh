python3 manage.py makemigrations
python3 manage.py migrate --no-input
python3 manage.py collectstatic --noinput
python3 manage.py runsslserver --certificate ./cert/development.crt --key ./cert/development.key 0.0.0.0:8899
