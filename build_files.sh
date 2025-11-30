# Exit immediately if a command exits with a non-zero status
set -e 

echo "Building the project..."
python3.12 -m pip install -r requirements.txt

echo "Make Migrations..."
python3.12 manage.py makemigrations --noinput
python3.12 manage.py migrate --noinput

echo "Collect Static..."
python3.12 manage.py collectstatic --noinput --clear