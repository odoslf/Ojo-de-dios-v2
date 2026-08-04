from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.web.routes_chat_pages import laia_chat_page


def _render_chat_template() -> str:
    env = Environment(loader=FileSystemLoader("app/templates"), autoescape=select_autoescape())
    template = env.get_template("chat.html")
    return template.render(request={})


def test_chat_template_extends_shell_and_targets_backend_endpoint() -> None:
    html = _render_chat_template()

    assert "Chat con LaIA" in html
    assert 'id="laia-chat-form"' in html
    assert 'data-chat-endpoint="/api/ai/laia/chat"' in html
    assert 'id="laia-chat-log"' in html
    assert '/static/js/laia_chat.js' in html
    assert "no ejecuta módulos" in html


def test_base_navigation_links_to_chat_page() -> None:
    base = Path("app/templates/base.html").read_text(encoding="utf-8")

    assert '<a href="/chat">Chat LaIA</a>' in base


def test_chat_javascript_posts_execute_local_ai_payload() -> None:
    script = Path("app/static/js/laia_chat.js").read_text(encoding="utf-8")

    assert "fetch(endpoint" in script
    assert "execute_local_ai: true" in script
    assert "ui_chat_tab" in script
    assert "textContent" in script
    assert "innerHTML" not in script


def test_chat_page_route_returns_chat_template_name() -> None:
    class _Request:
        scope = {"type": "http"}

    response = laia_chat_page(_Request())

    assert getattr(response, "template").name == "chat.html"
