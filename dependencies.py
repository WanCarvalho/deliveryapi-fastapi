from fastapi import Depends, HTTPException
from main import SECRET_KEY, ALGORITHM, ouath2_schema
from models import db, Usuario
from sqlalchemy.orm import sessionmaker, Session

from jose import jwt, JWTError

# retorna sessão para persistência no banco de dados
def sessao_db():
    try: 
        Session = sessionmaker(bind=db)
        session = Session()
        
        yield session
    finally:
        session.close()


def verificar_token(token: str = Depends(ouath2_schema), session: Session = Depends(sessao_db)):
    try:
        dicionario_informacoes = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_usuario = dicionario_informacoes.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Acesso negado, verifique a validade do token.")
    
    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso inválido.")
    
    return usuario