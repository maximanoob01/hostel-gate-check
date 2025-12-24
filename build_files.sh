echo "Building the project..."

# 1. Install Dependencies
python3.9 -m pip install -r requirements.txt

# 2. DEBUG: List installed packages to console (so we can see if Django is there)
echo "Checking installed packages..."
python3.9 -m pip list

# 3. Collect Static Files
echo "Collecting static files..."
python3.9 manage.py collectstatic --noinput --clear

echo "Build End"
