from models import db
from sqlalchemy.orm import sessionmaker

# retorna sessão para persistência no banco de dados
def sessao_db():
    try: 
        Session = sessionmaker(bind=db)
        session = Session()
        
        yield session
    finally:
        session.close()