
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, Response
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
from jinja2.exceptions import TemplateNotFound

def use_autorouter(
        router: APIRouter,
        templates:Jinja2Templates, 
        prefix:str = "",
        exclude:list[str]=[]
    ):
    """
    Creates an automatic router that serves HTML templates based on the requested path.

    ### Args
        templates:
            Instance of `Jinja2Templates` used to load and render templates.

        prefix:
            Prefix applied to the template
            directory structure.

        exclude:
            List of path that should not be handled by the autorouter. 
            This will cause HTTP 404 error.

    ### Example

    Instead of defining a route for every template:

    ```python
    home_router = APIRouter(prefix="/home", tags=["home"])

    @home_router.get("/login")
    def login_page(request: Request):
        return templates.TemplateResponse("home/login.html", {"request": request})

    @home_router.get("/signup")
    def signup_page(request: Request):
        return templates.TemplateResponse("home/signup.html", {"request": request})

    @home_router.get("/verify-email")
    def verify_email_page(request: Request):
        return templates.TemplateResponse("home/verify_email.html", {"request": request})
    ```

    You can generate the router automatically:

    ```python
    home_router = APIRouter(prefix="/home", tags=["home"])
    use_autorouter(home_router, templates, prefix="/home")
    ```

    Requests such as /home/login, /home/signup, or /home/verify-email
    will automatically render their corresponding templates inside
    templates/home/.
    """

    @router.get("/{path:path}")
    def autorouter(request:Request, path:str = ""):

        if path.endswith('.html'):
            return RedirectResponse(f"{router.prefix}/{path.removesuffix('.html')}")
        
        if path and not path.endswith("/"):
            return RedirectResponse(f"{router.prefix}/{path}/")
        
        if path in exclude:
            raise HTTPException(status_code=404)
        
        if path.endswith("/"):
            path = path.removesuffix("/")

        path = f"{prefix}/{path}.html"

        try:
            print(f"Trying template '{path}'")
            response = templates.TemplateResponse(path, {"request": request})
            return response
        except TemplateNotFound:
            print(f"AutoRouterError: The template '{path}' does not exists.")
            raise HTTPException(status_code=404)
        
        except Exception as e:
            print(f"AutoRouterError: {e}")
            raise HTTPException(status_code=500)
