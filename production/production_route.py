from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from production.production_model import Production
from sqlalchemy.orm import Session
from core.dependencies import CreateSession, templates
from core.security import verify_token
from production.production_schema import create_production
from users.users_model import User


production_router = APIRouter(prefix="/production", tags=["production"])

@production_router.post("/add")
def create_project_in_production(production: create_production, session: Session = Depends(CreateSession), user: str = Depends(verify_token)):

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized, invalid token")
    
    new_production_item = Production(
        project_name=production.project_name,
        client_name=production.client_name,
        description=production.description,
        delivery_date=production.delivery_date,
        status=production.status
    )

    if session.query(Production).filter(Production.project_name == new_production_item.project_name, Production.client_name == new_production_item.client_name).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This production item already exists, please provide different data to create a new production item")
        

    if not new_production_item.project_name or not new_production_item.client_name or not new_production_item.description:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please, check the data provided, all fields are required to create a production item")

    session.add(new_production_item)
    session.commit()
    session.refresh(new_production_item)

    if not new_production_item:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create production item, check the data provided")

    return RedirectResponse(url="/production/add1", status_code=303)

#VIEWS

@production_router.get("/")
def show_production_by_client(request: Request, user: User, session: Session = Depends(CreateSession)):
    
    return templates.TemplateResponse(
        "production/production.html",
        {
            "request": request,
            "user": user
        }
    )