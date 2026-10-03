# blog-api

url: http://127.0.0.1:8001/

Activate the virtual environment and apply migrations:

```powershell
.\venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver
```
Run the API tests with:

```powershell
python manage.py test apps.blog
```
