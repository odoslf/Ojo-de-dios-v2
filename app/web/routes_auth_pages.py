"""Authentication HTML pages."""

from __future__ import annotations

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.api.routes_auth import LoginRequest, login
from app.auth.session_manager import SESSION_COOKIE_NAME, revoke_user_session
from app.db.session import get_session

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "auth/login.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse)
def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    response = RedirectResponse("/modules", status_code=303)
    session_iterator = get_session()
    try:
        session = next(session_iterator)
        login(LoginRequest(username=username, password=password), request, response, session)
    except (HTTPException, ValueError):
        return templates.TemplateResponse(request, "auth/login.html", {"request": request, "error": "Usuario o contraseña inválidos."}, status_code=401)
    finally:
        session_iterator.close()
    return response


@router.post("/logout")
def logout_page(request: Request) -> RedirectResponse:
    response = RedirectResponse("/login", status_code=303)
    session_iterator = get_session()
    try:
        session = next(session_iterator)
        revoke_user_session(session, request.cookies.get(SESSION_COOKIE_NAME))
    finally:
        session_iterator.close()
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response
