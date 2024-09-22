from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import HTMLResponse
from fastapi import Request, status
from app.core.templates import templates  # Adjust the import based on your structure

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        return HTMLResponse(content=templates.get_template('404.html').render(), status_code=status.HTTP_404_NOT_FOUND)
    # You can also handle other specific exceptions or provide a default response
    return {"request": request, "exception": exc}
