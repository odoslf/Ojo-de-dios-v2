"""HTML page route for the LaIA chat tab."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/chat", response_class=HTMLResponse)
def laia_chat_page(request: Request) -> HTMLResponse:
    """Render the local LaIA chat page."""
    return templates.TemplateResponse(request, "chat.html", {"request": request})
