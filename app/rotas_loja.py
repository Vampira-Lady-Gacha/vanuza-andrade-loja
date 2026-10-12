"""Páginas públicas da loja e a API do pedido."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.db import obter_sessao
from app.models import Categoria, Pedido, Peca, Variante
from app.servicos import ErroPedido, cotar, criar_pedido, ler_config, link_whatsapp, mensagem_whatsapp, reais
from app.web import render

roteador = APIRouter()

ORDENS = {
    "novidades": (Peca.criado_em.desc(), Peca.id.desc()),
    "menor-preco": (Peca.preco_varejo.asc(),),
    "maior-preco": (Peca.preco_varejo.desc(),),
}


def consulta_pecas():
    return (
        select(Peca)
        .where(Peca.ativa.is_(True))
        .options(selectinload(Peca.fotos), selectinload(Peca.variantes), selectinload(Peca.categoria))
    )


def categorias_com_pecas(sessao: Session) -> list[Categoria]:
    return list(
        sessao.scalars(
            select(Categoria)
            .where(Categoria.ativa.is_(True), Categoria.pecas.any(Peca.ativa.is_(True)))
            .order_by(Categoria.ordem, Categoria.nome)
        )
    )


@roteador.get("/")
def inicio(request: Request, sessao: Session = Depends(obter_sessao)):
    pecas = list(sessao.scalars(consulta_pecas().order_by(Peca.destaque.desc(), Peca.ordem, Peca.id)))
    destaque = pecas[0] if pecas else None
    return render(
        request,
        sessao,
        "loja/inicio.html",
        {"destaque": destaque, "pecas": pecas[1:], "todas": pecas, "categorias": categorias_com_pecas(sessao)},
    )


@roteador.get("/catalogo")
def catalogo(
    request: Request,
    categoria: str = "",
    tamanho: str = "",
    q: str = "",
    ordem: str = "novidades",
    sessao: Session = Depends(obter_sessao),
):
    consulta = consulta_pecas()
    cat_atual = None
    if categoria:
        cat_atual = sessao.scalar(select(Categoria).where(Categoria.slug == categoria))
        if cat_atual is None:
            raise HTTPException(404)
        consulta = consulta.where(Peca.categoria_id == cat_atual.id)
    if tamanho:
        consulta = consulta.where(Peca.variantes.any((Variante.tamanho == tamanho) & (Variante.estoque > 0)))
    if q.strip():
        termo = f"%{q.strip()}%"
        consulta = consulta.where(
            or_(Peca.nome.ilike(termo), Peca.tecido.ilike(termo), Peca.referencia.ilike(termo), Peca.descricao.ilike(termo))
        )
    consulta = consulta.order_by(*ORDENS.get(ordem, ORDENS["novidades"]))
    pecas = list(sessao.scalars(consulta))
    return render(
        request,
        sessao,
        "loja/catalogo.html",
        {
            "pecas": pecas,
            "categorias": categorias_com_pecas(sessao),
            "cat_atual": cat_atual,
            "filtro": {"categoria": categoria, "tamanho": tamanho, "q": q, "ordem": ordem},
        },
    )


@roteador.get("/peca/{slug}")
def peca(slug: str, request: Request, sessao: Session = Depends(obter_sessao)):
    item = sessao.scalar(consulta_pecas().where(Peca.slug == slug))
    if item is None:
        raise HTTPException(404)
    outras = list(
        sessao.scalars(consulta_pecas().where(Peca.id != item.id).order_by(Peca.destaque.desc(), Peca.ordem).limit(4))
    )
    return render(request, sessao, "loja/peca.html", {"peca": item, "outras": outras})


@roteador.get("/pedido")
def pagina_pedido(request: Request, sessao: Session = Depends(obter_sessao)):
    return render(request, sessao, "loja/pedido.html")


@roteador.get("/pedido/{codigo}")
def pedido_enviado(codigo: str, t: str, request: Request, sessao: Session = Depends(obter_sessao)):
    pedido = sessao.scalar(
        select(Pedido).where(Pedido.codigo == codigo).options(selectinload(Pedido.itens))
    )
    if pedido is None or pedido.token != t:
        raise HTTPException(404)
    loja = ler_config(sessao)
    url = link_whatsapp(loja["whatsapp"], mensagem_whatsapp(pedido, loja))
    return render(request, sessao, "loja/pedido_enviado.html", {"pedido": pedido, "url_whatsapp": url})


@roteador.get("/como-comprar")
def como_comprar(request: Request, sessao: Session = Depends(obter_sessao)):
    return render(request, sessao, "loja/como_comprar.html")


# ---------------------------------------------------------------- API do pedido


class ItemEntrada(BaseModel):
    variante_id: int
    quantidade: int = Field(ge=1, le=999)


class CotacaoEntrada(BaseModel):
    itens: list[ItemEntrada] = Field(max_length=200)


class PedidoEntrada(CotacaoEntrada):
    nome: str = Field(max_length=120)
    whatsapp: str = Field(max_length=30)
    cidade: str = Field(default="", max_length=80)
    entrega: str
    detalhe_entrega: str = Field(default="", max_length=200)
    observacao: str = Field(default="", max_length=2000)


def _minimo(sessao: Session) -> int:
    return int(ler_config(sessao)["atacado_minimo"] or 1)


@roteador.post("/api/cotacao")
def api_cotacao(entrada: CotacaoEntrada, sessao: Session = Depends(obter_sessao)):
    cotacao = cotar(sessao, [(i.variante_id, i.quantidade) for i in entrada.itens], _minimo(sessao))
    return {
        "linhas": [
            {
                "variante_id": l.variante.id,
                "peca": l.variante.peca.nome,
                "slug": l.variante.peca.slug,
                "referencia": l.variante.peca.referencia,
                "foto": f"/media/{l.variante.peca.foto_capa.arquivo}" if l.variante.peca.foto_capa else None,
                "cor": l.variante.cor,
                "cor_hex": l.variante.cor_hex,
                "tamanho": l.variante.tamanho,
                "quantidade": l.quantidade,
                "disponivel": l.disponivel,
                "preco": l.preco_unitario,
                "preco_varejo": l.variante.peca.preco_varejo,
                "subtotal": l.subtotal,
                "subtotal_fmt": reais(l.subtotal),
                "preco_fmt": reais(l.preco_unitario),
            }
            for l in cotacao.linhas
        ],
        "removidos": cotacao.removidos,
        "quantidade": cotacao.quantidade,
        "atacado": cotacao.atacado,
        "minimo_atacado": cotacao.minimo_atacado,
        "faltam_para_atacado": cotacao.faltam_para_atacado,
        "total": cotacao.total,
        "total_fmt": reais(cotacao.total),
        "economia_fmt": reais(cotacao.total_varejo - cotacao.total) if cotacao.atacado else "",
    }


@roteador.post("/api/pedidos")
def api_criar_pedido(entrada: PedidoEntrada, sessao: Session = Depends(obter_sessao)):
    try:
        pedido = criar_pedido(
            sessao,
            [(i.variante_id, i.quantidade) for i in entrada.itens],
            nome=entrada.nome,
            whatsapp=entrada.whatsapp,
            cidade=entrada.cidade,
            entrega=entrada.entrega,
            detalhe_entrega=entrada.detalhe_entrega,
            observacao=entrada.observacao,
            minimo_atacado=_minimo(sessao),
        )
    except ErroPedido as erro:
        sessao.rollback()
        return JSONResponse({"erro": str(erro)}, status_code=422)
    loja = ler_config(sessao)
    return {
        "codigo": pedido.codigo,
        "url": f"/pedido/{pedido.codigo}?t={pedido.token}",
        "url_whatsapp": link_whatsapp(loja["whatsapp"], mensagem_whatsapp(pedido, loja)),
    }


# ---------------------------------------------------------------- SEO


@roteador.get("/robots.txt", response_class=PlainTextResponse)
def robots(request: Request):
    return f"User-agent: *\nDisallow: /admin\nDisallow: /api\nSitemap: {str(request.base_url).rstrip('/')}/sitemap.xml\n"


@roteador.get("/sitemap.xml")
def sitemap(request: Request, sessao: Session = Depends(obter_sessao)):
    base = str(request.base_url).rstrip("/")
    hoje = date.today().isoformat()
    urls = [f"{base}/", f"{base}/catalogo", f"{base}/como-comprar"]
    urls += [f"{base}/catalogo?categoria={c.slug}" for c in categorias_com_pecas(sessao)]
    urls += [f"{base}/peca/{p.slug}" for p in sessao.scalars(select(Peca).where(Peca.ativa.is_(True)))]
    corpo = "".join(f"<url><loc>{u.replace('&', '&amp;')}</loc><lastmod>{hoje}</lastmod></url>" for u in urls)
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{corpo}</urlset>'
    return Response(xml, media_type="application/xml")
