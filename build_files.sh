echo "Building the project..."

# 1. Install Dependencies (Verbose mode to see errors)
python3.9 -m pip install -r requirements.txt
echo "Install complete."

# 2. DEBUG: List installed packages (Check logs for 'Django')
echo "---- INSTALLED PACKAGES ----"
python3.9 -m pip list
echo "----------------------------"

# 3. Collect Static Files
echo "Collecting static files..."
python3.9 manage.py collectstatic --noinput --clear

echo "Build End"
