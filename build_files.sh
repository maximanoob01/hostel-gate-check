# build_files.sh
echo "Building the project..."

# 1. Install Dependencies
python3.9 -m pip install --upgrade pip
python3.9 -m pip install -r requirements.txt

# 2. Migrations (DISABLED for Vercel Build)
# We disable these because Vercel build environments often lack 
# access to DB variables, causing the build to crash. 
# python3.9 manage.py makemigrations
# python3.9 manage.py migrate

# 3. Collect Static Files
echo "Collecting static files..."
python3.9 manage.py collectstatic --noinput --clear

echo "Build End"
