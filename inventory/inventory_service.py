from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.dependencies import CreateSession
from inventory.inventory_model import Inventory, InventoryLogs as InventoryLogsModel
from inventory.inventory_schema import ItemCreate, InvLog as InvLogSchema
from users.users_model import User
from core.security import verify_token
from datetime import datetime
from typing import Optional

def _create_inventory_log(session: Session, inventory_item: Inventory, user: User, action: str, quantity_before: Optional[int] = None, quantity_after: Optional[int] = None) -> InventoryLogsModel:
    if action == "Create Item" and quantity_before is None:
        quantity_before = 0
    elif quantity_before is None:
        quantity_before = inventory_item.quantity

    if quantity_after is None:
        quantity_after = inventory_item.quantity

    log = InventoryLogsModel(
        inventory_id=inventory_item.id,
        user_id=user.id,
        action=action,
        timestamp=datetime.utcnow(),
        quantity_before=quantity_before,
        quantity_after=quantity_after
    )
    session.add(log)
    return log

def create_inventory_item(item_data: ItemCreate, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    existing_item = session.query(Inventory).filter(Inventory.item_name == item_data.item_name).first()
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Inventory item with name '{item_data.item_name}' already exists."
        )

    new_item = Inventory(
        item_name=item_data.item_name,
        description=item_data.description,
        quantity=item_data.quantity,
        owner_id=user.id
    )

    session.add(new_item)
    session.flush()

    _create_inventory_log(
        session=session,
        inventory_item=new_item,
        user=user,
        action="Create Item",
        quantity_before=0,
        quantity_after=new_item.quantity 
    )

    session.commit()
    session.refresh(new_item)

    return {
        "message": "Inventory item created successfully",
        "item": new_item,
    }

def edit_inventory_item(item_name: str, item_update: ItemCreate, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    item = session.query(Inventory).filter(Inventory.item_name == item_name).first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")

    quantity_before = item.quantity

    item.item_name = item_update.item_name
    item.description = item_update.description
    item.quantity = item_update.quantity

    action = "Update"
    if item_update.quantity > quantity_before:
        action = "Add"
    elif item_update.quantity < quantity_before:
        action = "Reduce"
    elif item_update.quantity == 0 and quantity_before > 0:
        action = "Delete (Quantity Zero)"

    _create_inventory_log(
        session=session,
        inventory_item=item,
        user=user,
        action=action,
        quantity_before=quantity_before,
        quantity_after=item.quantity
    )

    session.add(item)
    session.commit()
    session.refresh(item)

    return {
        "message": "Inventory item updated successfully",
        "item": item,
    }

def delete_inventory_item(item_name: str, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    item_to_delete = session.query(Inventory).filter(Inventory.item_name == item_name).first()

    if not item_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")

    _create_inventory_log(
        session=session,
        inventory_item=item_to_delete,
        user=user,
        action="Delete Item",
        quantity_before=item_to_delete.quantity,
        quantity_after=0
    )

    session.delete(item_to_delete)
    session.commit()

    return {
        "message": "Inventory item deleted successfully",
        "item_name": item_name
    }

def create_inventory_log_endpoint(inv_log_data: InvLogSchema, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):

    inventory_item = session.query(Inventory).get(inv_log_data.inventory_id)
    if not inventory_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item for log not found")

    log = InventoryLogsModel(
        inventory_id=inv_log_data.inventory_id,
        user_id=user.id,
        action=inv_log_data.action,
        timestamp=datetime.utcnow(),
        quantity_before=inv_log_data.quantity_before,
        quantity_after=inv_log_data.quantity_after
    )
    session.add(log)
    session.commit()
    session.refresh(log)

    return {"message": "Inventory log created successfully", "log": log}