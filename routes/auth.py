from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependencies import sessao_db
from main import bcrypt_context
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])


def criar_token(id_usuario):
    token = f"fnsyubf7s8fs9{id_usuario}" 
    
    return token


def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    
    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha):
        return False
    
    return usuario


@router.get("")
async def home():
    """
    Rota padrão de Autenticação do sistema.
    """
    
    return {"mensagem": "Você acessou rota padrão de autenticação", "autenticado": False}


@router.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(sessao_db)):
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    
    if usuario: 
        raise HTTPException(status_code=400, detail="E-mail do usuário já cadastrado.")
    else: 
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_criptografada, usuario_schema.ativo, usuario_schema.admin)
        session.add(novo_usuario)
        session.commit()
        return HTTPException(status_code=200, detail=f"Novo usuário {usuario_schema.email} cadastrado com sucesso.")
    
    
@router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(sessao_db)):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas.")
    else:
        access_token = criar_token(usuario.id)
        
        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }
        

@router.delete("/excluir_usuario")
async def deletar_usuario(id_usuario, session: Session = Depends(sessao_db)):
    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    
    session.delete(usuario)
    session.commit()
    
    return HTTPException(status_code=200, detail=f"Usuario de id {id_usuario} deletado com sucesso.")