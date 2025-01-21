from app.db.init_db import init_db
from app.db.session import SessionLocal

def main() -> None:
    db = SessionLocal()
    init_db(db)

if __name__ == "__main__":
    main()
    print("Base de dados inicializada com sucesso!") 