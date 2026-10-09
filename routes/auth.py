from fastapi import APIRouter, Depends, HTTPException, status
from models import Usuario
from dependencies import sessao_db, verificar_token
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["auth"])


def criar_token(id_usuario, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dicionario_informacoes = {"sub": str(id_usuario), "data_expiracao": data_expiracao.timestamp()}
    encoded_jwt = jwt.encode(dicionario_informacoes, SECRET_KEY, ALGORITHM)
    
    return encoded_jwt


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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail do usuário já cadastrado.")
    else: 
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_criptografada, usuario_schema.ativo, usuario_schema.admin)
        session.add(novo_usuario)
        session.commit()
        return HTTPException(status_code=status.HTTP_200_OK, detail=f"Novo usuário {usuario_schema.email} cadastrado com sucesso.")
    
    
@router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(sessao_db)):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    
    if not usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário não encontrado ou credenciais inválidas.")
    else:
        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
        }
        
        
# rota para usar no authorize de teste da /docs
@router.post("/login-form")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(sessao_db)):
    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)
    
    if not usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário não encontrado ou credenciais inválidas.")
    else:
        access_token = criar_token(usuario.id)
        
        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }


@router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    access_token = criar_token(usuario.id)
    
    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }


@router.delete("/excluir_usuario")
async def deletar_usuario(id_usuario, session: Session = Depends(sessao_db), usuario: Usuario = Depends(verificar_token)):
    usuario_deletar = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    
    if not usuario.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sem autorização para deletar usuário.")
    if usuario_deletar.admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuários admins não podem ser deletados.")
    
    session.delete(usuario_deletar)
    session.commit()
    
    return HTTPException(status_code=status.HTTP_200_OK, detail=f"Usuario de id {id_usuario} deletado com sucesso.")