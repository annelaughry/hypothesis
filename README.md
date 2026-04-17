# Pippit
## Setup

python -m venv .venv
source .venv/bin/active # Linux/macOS
.venv\Scripts\activate # Windows
pip install -r requirements.txt

## Database Setup

python manage.py makemigrations
python manage.py migrate

## Run the project

pyton3 manage.py runserver