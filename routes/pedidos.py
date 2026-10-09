from fastapi import APIRouter, Depends, HTTPException, status
from dependencies import sessao_db, verificar_token
from sqlalchemy.orm import Session, selectinload
from schemas import PedidoSchema, ItemPedidoSchema
from models import Pedido, Usuario, PedidoItem

router = APIRouter(prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)])

@router.get("")
async def pedidos():
    """
    Rota padrão de listagem de pedidos.
    """
    
    return {"mensagem": "Acessou rota de pedidos!"}


@router.post("/criar")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(sessao_db)):
    novo_pedido = Pedido(usuario=pedido_schema.usuario)
    session.add(novo_pedido)
    session.commit()
    
    return {"mensagem": f"Pedido criado com sucesso, ID do pedido: {novo_pedido.id}"}


@router.post("/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session: Session = Depends(sessao_db), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    
    if not pedido:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pedido não encontrado.")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Você não tem autorização para essa ação.")
    
    pedido.status = "CANCELADO"
    session.commit()
    
    return {
        "mensagem": f"Pedido N° {pedido.id} cancelado com sucesso.",
        "pedido": pedido
    }
    
    
@router.get("/listar")
async def listar_pedidos(session: Session = Depends(sessao_db), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Você não tem autorização para essa ação.")
    else:
        pedidos = session.query(Pedido).all()
        
        return {
            "pedidos": pedidos
        }
        
        
@router.post("/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int,
                                item_pedido_schema: ItemPedidoSchema,
                                session: Session = Depends(sessao_db),
                                usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    
    if not pedido:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pedido não existente.")
    if not usuario.admin and usuario.id != pedido.usuario:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Você não tem autorização para essa ação.")
        
    item_pedido = PedidoItem(item_pedido_schema.quantidade,
                            item_pedido_schema.sabor,
                            item_pedido_schema.tamanho,
                            item_pedido_schema.preco_unitario,
                            id_pedido)
    
    session.add(item_pedido)
    pedido.calcular_preco()
    session.commit()
    
    return {
        "mensagem": "Item criado com sucesso.",
        "item_id": item_pedido.id,
        "preco_pedido": pedido.preco
    }
    
    
@router.post("/remover-item/{id_pedido_item}")
async def remover_item_pedido(id_pedido_item: int,
                                session: Session = Depends(sessao_db),
                                usuario: Usuario = Depends(verificar_token)):
    pedido_item = session.query(PedidoItem).filter(PedidoItem.id == id_pedido_item).first()
    
    if not pedido_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item do pedido não encontrado.")
    
    pedido = session.query(Pedido).options(selectinload(Pedido.itens)).filter(Pedido.id == pedido_item.pedido).first()
    
    if not pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado.")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Você não tem autorização para essa ação.")
    
    session.delete(pedido_item)
    pedido.calcular_preco()
    session.commit()
    session.refresh(pedido)
    
    return {
        "mensagem": "Item removido com sucesso.",
        "pedido": pedido
    }
    
    
@router.post("/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido: int, session: Session = Depends(sessao_db), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    
    if not pedido:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pedido não encontrado.")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Você não tem autorização para essa ação.")
    
    pedido.status = "FINALIZADO"
    session.commit()
    
    return {
        "mensagem": f"Pedido N° {pedido.id} finalizado com sucesso.",
        "pedido": pedido
    }