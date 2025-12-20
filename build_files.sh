# build_files.sh
echo "Building the project..."

# Ensure pip is up to date
python3.9 -m pip install --upgrade pip

# Install dependencies
python3.9 -m pip install -r requirements.txt

# Make migrations (good practice on build)
python3.9 manage.py makemigrations
python3.9 manage.py migrate

# Collect static files
python3.9 manage.py collectstatic --noinput --clear

echo "Build End"