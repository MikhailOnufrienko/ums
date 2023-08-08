## ums
### A user management system with Django, JWT-tokens, PostgreSQL and Redis (test project for a python dev. position).

1. Clone this repo.
2. Create a virtual environment and install dependencies from requirements.txt:

```
   pip install -r requirements.txt
```

3. Run Docker containers with PostgreSQL and Redis:

```
   docker run --name intime_pg -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=pgpass -e POSTGRES_DB=intime_auth_db -p 5432:5432 -d postgres:15
```

```
   docker run --name intime_rd -p 6379:6379 -d redis:latest
```

4. Create an .env-file from .env.example.
5. Apply migrations: move to the directory "intime_auth" and run the command:

     ```
     python manage.py migrate
     ```

6. Run the Django debug server: move to the directory "intime_auth" and run the command:
   
   ```
     python manage.py runserver 127.0.0.1:8001
   ```

10. The browser version of the application:

   ```
   http://127.0.0.1:8001/auth/register/
   ```

11. API endpoints prefix:
   
    ```
   http://127.0.0.1:8001/api/v1/auth/
   ```
