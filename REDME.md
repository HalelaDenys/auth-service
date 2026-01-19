auth-service/
 ├── src/
 │   ├── main.py
 │   ├── core/
 │   │   ├── config.py
 │   │   └── security.py
 │   ├── infrastructure/
 │   │   ├── db/
 │   │   │   └── models/
 │   │   │       └── users.py
 │   │   ├── repo/
 │   │       └── user_repo.py
 │   ├── schemas/
 │   │   └── user.py
 │   ├── service/
 │   │   └── user_service.py
 │   └── api/
 │       └── auth.py
 ├── .env
 └── uv.toml