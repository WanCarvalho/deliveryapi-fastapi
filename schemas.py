from pydantic import BaseModel
from typing import Optional
from models import Usuario

class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    ativo: Optional[bool]
    admin: Optional[bool]
    
    class Config:
        # Permite criar o schema a partir dos atributos de objetos, como modelos ORM.
        from_attributes = True 
        
        
class PedidoSchema(BaseModel):
    usuario: int
    
    class Config:
        from_attributes = True 
        

class LoginSchema(BaseModel):
    email: str
    senha: str
    
    class Config:
        from_attributes = True