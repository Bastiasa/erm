from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.dependencies import CreateSession
from inventory.inventory_model import Inventory, InventoryLogs
from inventory.inventory_schema import ItemCreate
from users.users_model import User
from core.security import verify_token
from datetime import datetime

def edit_inventory_item(item_name: str, item_update: ItemCreate, user: User, session: Session = Depends(CreateSession)):

    if not user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="User not authenticated")
    
    item = session.query(Inventory).filter(Inventory.item_name == item_name).first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")

    item.item_name = item_update.item_name
    item.description = item_update.description
    item.quantity = item_update.quantity
    item.owner_id = item.owner_id

    session.commit()
    session.refresh(item)

    return {
        "message": "Inventory item updated successfully",
        "item": item,
    }

def delete_inventory_item(item_name: str, user: User, session: Session = Depends(CreateSession)): 
    
    if not user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="User not authenticated")

    item_to_delete = session.query(Inventory).filter(Inventory.item_name == item_name).first()

    if not item_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")

    log = InventoryLogs(
        inventory_id = item_to_delete.id,
        user_id = user.id,
        item_name = item_name,
        action = 'Delete',
    )

    session.delete(item_to_delete)
    session.commit()

    return {
        "message": "Inventory item deleted successfully",
        "item": item_to_delete
    }