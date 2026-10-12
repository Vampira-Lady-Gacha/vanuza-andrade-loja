"""Templates e utilidades compartilhadas entre a loja e o painel."""

import secrets
from typing import Any

from fastapi import Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import config
from app.models import ENTREGAS, STATUS_PEDIDO
from app.servicos import formatar_telefone, link_whatsapp, ler_config, reais

templates = Jinja2Templates(directory=str(config.RAIZ / "app" / "templates"))
templates.env.filters["reais"] = reais
templates.env.filters["telefone"] = formatar_telefone
templates.env.globals.update(
    link_whatsapp=link_whatsapp,
    ENTREGAS=ENTREGAS,
    STATUS_PEDIDO=STATUS_PEDIDO,
    # Linha de graduação de cada tamanho no molde: cor e traço fixos no site todo.
    LINHAS_TAMANHO={"P": "p", "M": "m", "G": "g", "GG": "gg"},
)


def token_csrf(request: Request) -> str:
    token = request.session.get("csrf")
    if not token:
        token = secrets.token_urlsafe(24)
        request.session["csrf"] = token
    return token


CABECALHO_ESTATICO = "x-exportar-estatico"


def eh_exportacao(request: Request) -> bool:
    """Pedido feito pelo exportador da vitrine estática (GitHub Pages)."""
    return request.headers.get(CABECALHO_ESTATICO) == "1"


def render(request: Request, sessao: Session, nome: str, contexto: dict[str, Any] | None = None, status: int = 200):
    estatico = eh_exportacao(request)
    url_publica = config.URL_PUBLICA or str(request.base_url).rstrip("/")
    if estatico and request.headers.get("x-url-publica"):
        url_publica = request.headers["x-url-publica"].rstrip("/")
    dados = {
        "request": request,
        "loja": ler_config(sessao),
        "csrf": token_csrf(request),
        "estatico": estatico,
        "url_publica": url_publica,
        "aviso": request.session.pop("aviso", None),
    }
    dados.update(contexto or {})
    return templates.TemplateResponse(request, nome, dados, status_code=status)


def avisar(request: Request, texto: str) -> None:
    request.session["aviso"] = texto
