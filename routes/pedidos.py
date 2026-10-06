from fastapi import APIRouter, Depends, HTTPException
from dependencies import sessao_db
from sqlalchemy.orm import Session
from schemas import PedidoSchema
from models import Pedido

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@router.get("")
async def pedidos():
    """
    Rota padrão de listagem de pedidos.
    """
    
    return {"mensagem": "Acessou rota de pedidos!"}


@router.post("")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(sessao_db)):
    novo_pedido = Pedido(usuario=pedido_schema.usuario)
    session.add(novo_pedido)
    session.commit()
    
    return {"mensagem": f"Pedido criado com sucesso, ID do pedido: {novo_pedido.id}"}