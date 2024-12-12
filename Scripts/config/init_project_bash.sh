
#!/bin/bash
operation_failed(){
  echo $1
  exit 1
}

echo -e "\n----tart Django project initialization----\n"
MIN_ALLOWABLE_PYTHON_VERSION="3.9.1"
echo "Activating Python environment"
if [ -d "./env/" ]; then
  source ./env/Scripts/activate
  echo "Env activated"
else
  echo "Environment not create already"
  current_python_version=$(python --version 2>&1 | awk '{print $2}')
  if [[ $(echo -e "$current_python_version\n$MIN_ALLOWABLE_PYTHON_VERSION" | sort -V | head -n1) == "$MIN_ALLOWABLE_PYTHON_VERSION" ]]; then
      echo "Python version is equal or greater. That's good :0"
      python -m venv env
      echo "Environment created. Let's activated it "
      source ./env/Scripts/activate
  else
    operation_failed "Python version $current_python_version is too low. Update it or download it in page: https://www.python.org/downloads/"
  fi
fi
echo -e "\n----Checking whether env is activated----\n"
current_python=$(which python)
if [[ "$current_python" == *"env/Scripts/python"* ]]; then
    echo -e "Env is activated: $current_python.\n Downloading dependencies"
    pip install -r Docs/requirements.txt
    pip list
else
  operation_failed "Env is not activated. Something went wrong"
fi

echo -e "\n----Checking whether migrations folder exists----\n"
migrations_dir="./webStore/migrations"
if [ ! -d "$migrations_dir" ]; then
  echo "Migrations folder not exists. Creating one.. "
  mkdir -p "$migrations_dir"
  touch "$migrations_dir/__init__.py"
else
  echo "Migrations folder exists. Cleaning if necessary"
  find "$migrations_dir" -type f ! -name "__init__.py" -delete
fi

echo -e "\n----Creating migrations----\n"
python manage.py makemigrations

echo -e "\n----Creating Database if migrations succeeded----\n"
extra_files=$(find "$migrations_dir" -type f ! -name "__init__.py")
if [ -n "$extra_files" ]; then
    echo -e "Found additional migration files: \n Creating sqlite3 database"
    python manage.py migrate
    echo "$extra_files"
    if [ -f "./db.sqlite3" ]; then
      echo -e "Migration has been successfully.\n Creating superuser"
      python Scripts/create_superuser.py
    else
      echo "Migrations failed"
      exit 1
    fi
else
    echo "No additional migration files found."
fi

echo -e "\n----Running server----\n"
python manage.py runserver



