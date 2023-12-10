# Create a python virtual environment in current folder (Optional)
# You can also directly install the requirements without creating a venv.
virtualenv env

# Activate the virtual environment
source ./env/bin/activate

# If permission denied
sudo chmod +x ./env/bin/activate

# Uncompress the Django project file. 
unzip <file_name>.zip

# Now, using pip install the requirements.txt required for Django
pip install -r requirements.txt

# We can now run the Django application locally.
python ./<folder_name>/manage.py runserver

# Open browser and the application is ready
http://localhost:8000/

NOTE: To successfully run, the runserver command must be used together with the environment
where all the requirements are installed.