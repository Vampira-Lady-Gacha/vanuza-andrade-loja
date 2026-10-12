"""Painel da loja: peças, fotos, grade de estoque, categorias, pedidos e configurações."""

import time
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from starlette.datastructures import FormData

from app.db import obter_sessao
from app.models import STATUS_PEDIDO, TAMANHOS_PADRAO, Categoria, Foto, Pedido, Peca, Usuario, Variante
from app.servicos import (
    PADROES,
    ROTULOS_CONFIG,
    apagar_arquivo_foto,
    autenticar,
    conferir_senha,
    gerar_hash,
    ler_centavos,
    ler_config,
    mudar_status,
    salvar_config,
    salvar_foto,
    slug_unico,
    slugificar,
)
from app.web import avisar, render

roteador = APIRouter(prefix="/admin")

ESTOQUE_BAIXO = 2
_tentativas: dict[str, list[float]] = defaultdict(list)


class PrecisaEntrar(Exception):
    pass


def usuario_logado(request: Request, sessao: Session = Depends(obter_sessao)) -> Usuario:
    usuario_id = request.session.get("usuario_id")
    usuario = sessao.get(Usuario, usuario_id) if usuario_id else None
    if usuario is None:
        raise PrecisaEntrar()
    return usuario


async def formulario(request: Request) -> FormData:
    """Lê o formulário e confere o token CSRF de todo POST do painel."""
    dados = await request.form()
    if not request.session.get("csrf") or dados.get("csrf") != request.session["csrf"]:
        raise HTTPException(400, "Formulário expirado. Volte, recarregue a página e tente de novo.")
    return dados


def voltar(url: str) -> RedirectResponse:
    return RedirectResponse(url, status_code=303)


# ---------------------------------------------------------------- acesso


@roteador.get("/entrar")
def tela_entrar(request: Request, sessao: Session = Depends(obter_sessao)):
    return render(request, sessao, "admin/entrar.html", {"erro": None})


@roteador.post("/entrar")
async def entrar(request: Request, sessao: Session = Depends(obter_sessao)):
    dados = await formulario(request)
    ip = request.client.host if request.client else "?"
    agora = time.monotonic()
    _tentativas[ip] = [t for t in _tentativas[ip] if agora - t < 600]
    if len(_tentativas[ip]) >= 8:
        return render(request, sessao, "admin/entrar.html", {"erro": "Muitas tentativas. Espere 10 minutos."}, 429)
    usuario = autenticar(sessao, str(dados.get("email", "")), str(dados.get("senha", "")))
    if usuario is None:
        _tentativas[ip].append(agora)
        return render(request, sessao, "admin/entrar.html", {"erro": "E-mail ou senha não conferem."}, 401)
    _tentativas.pop(ip, None)
    request.session.clear()
    request.session["usuario_id"] = usuario.id
    return voltar("/admin")


@roteador.post("/sair")
async def sair(request: Request):
    await formulario(request)
    request.session.clear()
    return voltar("/admin/entrar")


@roteador.get("/conta")
def tela_conta(request: Request, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(obter_sessao)):
    return render(request, sessao, "admin/conta.html", {"usuario": usuario, "erro": None})


@roteador.post("/conta")
async def salvar_conta(request: Request, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(obter_sessao)):
    dados = await formulario(request)
    atual, nova = str(dados.get("senha_atual", "")), str(dados.get("senha_nova", ""))
    erro = None
    if not conferir_senha(atual, usuario.senha_hash):
        erro = "A senha atual não confere."
    elif len(nova) < 8:
        erro = "A nova senha precisa de pelo menos 8 caracteres."
    elif nova != dados.get("senha_confirma"):
        erro = "A confirmação não é igual à nova senha."
    if erro:
        return render(request, sessao, "admin/conta.html", {"usuario": usuario, "erro": erro}, 422)
    usuario.senha_hash = gerar_hash(nova)
    sessao.commit()
    avisar(request, "Senha alterada.")
    return voltar("/admin/conta")


# ---------------------------------------------------------------- painel


@roteador.get("")
def painel(request: Request, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(obter_sessao)):
    novos = list(
        sessao.scalars(
            select(Pedido).where(Pedido.status == "novo").options(selectinload(Pedido.itens)).order_by(Pedido.id.desc())
        )
    )
    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    vendido_mes = sessao.scalar(
        select(func.coalesce(func.sum(Pedido.total), 0)).where(
            Pedido.status.in_(["confirmado", "separado", "entregue"]), Pedido.criado_em >= inicio_mes
        )
    )
    pedidos_7d = sessao.scalar(
        select(func.count(Pedido.id)).where(Pedido.criado_em >= datetime.now() - timedelta(days=7))
    )
    baixo = list(
        sessao.scalars(
            select(Variante)
            .join(Peca)
            .where(Peca.ativa.is_(True), Variante.estoque <= ESTOQUE_BAIXO)
            .options(selectinload(Variante.peca))
            .order_by(Variante.estoque, Peca.nome)
        )
    )
    loja = ler_config(sessao)
    return render(
        request,
        sessao,
        "admin/painel.html",
        {
            "usuario": usuario,
            "novos": novos,
            "vendido_mes": vendido_mes,
            "pedidos_7d": pedidos_7d,
            "baixo": baixo,
            "whatsapp_padrao": loja["whatsapp"] == PADROES["whatsapp"],
            "sem_trocas": not loja["texto_trocas"],
            "ha_exemplo": not loja["exemplo_revisado"]
            and sessao.scalar(select(func.count(Foto.id)).where(Foto.arquivo.like("inicial-%"))),
        },
    )


@roteador.post("/exemplo-revisado")
async def exemplo_revisado(request: Request, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(obter_sessao)):
    await formulario(request)
    salvar_config(sessao, {"exemplo_revisado": "1"})
    return voltar("/admin")


# ---------------------------------------------------------------- peças


@roteador.get("/pecas")
def lista_pecas(
    request: Request, q: str = "", usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(obter_sessao)
):
    consulta = select(Peca).options(selectinload(Peca.fotos), selectinload(Peca.variantes), selectinload(Peca.categoria))
    if q.strip():
        termo = f"%{q.strip()}%"
        consulta = consulta.where(Peca.nome.ilike(termo) | Peca.referencia.ilike(termo))
    pecas = list(sessao.scalars(consulta.order_by(Peca.ativa.desc(), Peca.ordem, Peca.id.desc())))
    return render(request, sessao, "admin/pecas.html", {"usuario": usuario, "pecas": pecas, "q": q})


def _categorias(sessao: Session) -> list[Categoria]:
    return list(sessao.scalars(select(Categoria).order_by(Categoria.ordem, Categoria.nome)))


@roteador.get("/pecas/nova")
def nova_peca(request: Request, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(obter_sessao)):
    return render(
        request,
        sessao,
        "admin/peca_form.html",
        {"usuario": usuario, "peca": None, "categorias": _categorias(sessao), "erro": None, "dados": {}},
    )


def _aplicar_dados(sessao: Session, peca: Peca, dados: FormData) -> None:
    nome = str(dados.get("nome", "")).strip()
    if len(nome) < 2:
        raise ValueError("Dê um nome para a peça.")
    varejo = ler_centavos(str(dados.get("preco_varejo", "")))
    if not varejo:
        raise ValueError("Informe o preço de varejo.")
    atacado = ler_centavos(str(dados.get("preco_atacado", "")))
    if atacado is not None and atacado > varejo:
        raise ValueError("O preço de atacado não pode ser maior que o de varejo.")
    categoria_id = str(dados.get("categoria_id", ""))
    peca.nome = nome[:120]
    peca.slug = slug_unico(sessao, nome, peca.id)
    peca.referencia = str(dados.get("referencia", "")).strip()[:40]
    peca.tecido = str(dados.get("tecido", "")).strip()[:80]
    peca.descricao = str(dados.get("descricao", "")).strip()
    peca.categoria_id = int(categoria_id) if categoria_id.isdigit() else None
    peca.preco_varejo = varejo
    peca.preco_atacado = atacado
    peca.ativa = dados.get("ativa") == "on"
    peca.destaque = dados.get("destaque") == "on"


@roteador.post("/pecas/nova")
async def criar_peca(request: Request, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(obter_sessao)):
    dados = await formulario(request)
    peca = Peca(preco_varejo=0)
    try:
        _aplicar_dados(sessao, peca, dados)
    except ValueError as erro:
        return render(
            request,
            sessao,
            "admin/peca_form.html",
            {"usuario": usuario, "peca": None, "categorias": _categorias(sessao), "erro": str(erro), "dados": dados},
            422,
        )
    if peca.destaque:
        _tirar_outros_destaques(sessao)
    for tamanho in TAMANHOS_PADRAO:
        peca.variantes.append(Variante(cor="Única", cor_hex="#5b2a86", tamanho=tamanho, estoque=0))
    sessao.add(peca)
    sessao.commit()
    avisar(request, "Peça criada. Agora envie as fotos e preencha o estoque da grade.")
    return voltar(f"/admin/pecas/{peca.id}")


def _tirar_outros_destaques(sessao: Session, manter: int | None = None) -> None:
    for outra in sessao.scalars(select(Peca).where(Peca.destaque.is_(True))):
        if outra.id != manter:
            outra.destaque = False


def _carregar_peca(sessao: Session, peca_id: int) -> Peca:
    peca = sessao.scalar(
        select(Peca).where(Peca.id == peca_id).options(selectinload(Peca.fotos), selectinload(Peca.variantes))
    )
    if peca is None:
        raise HTTPException(404)
    return peca


def _grade(peca: Peca) -> tuple[list[tuple[str, str]], list[str], dict[tuple[str, str], int]]:
    estoque = {(v.cor, v.tamanho): v.estoque for v in peca.variantes}
    return peca.cores, peca.tamanhos, estoque


@roteador.get("/pecas/{peca_id}")
def editar_peca(
    peca_id: int, request: Request, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(obter_sessao)
):
    peca = _carregar_peca(sessao, peca_id)
    cores, tamanhos, estoque = _grade(peca)
    return render(
        request,
        sessao,
        "admin/peca_form.html",
        {
            "usuario": usuario,
            "peca": peca,
            "categorias": _categorias(sessao),
            "erro": None,
            "dados": {},
            "cores": cores,
            "tamanhos": tamanhos,
            "estoque": estoque,
        },
    )


@roteador.post("/pecas/{peca_id}")
async def salvar_peca(
    peca_id: int, request: Request, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(obter_sessao)
):
    dados = await formulario(request)
    peca = _carregar_peca(sessao, peca_id)
    try:
        _aplicar_dados(sessao, peca, dados)
    except ValueError as erro:
        sessao.rollback()
        peca = _carregar_peca(sessao, peca_id)
        cores, tamanhos, estoque = _grade(peca)
        return render(
            request,
            sessao,
            "admin/peca_form.html",
            {
                "usuario": usuario,
                "peca": peca,
                "categorias": _categorias(sessao),
                "erro": str(erro),
                "dados": dados,
                "cores": cores,
                "tamanhos": tamanhos,
                "estoque": estoque,
            },
            422,
        )
    if peca.destaque:
        _tirar_outros_destaques(sessao, peca.id)
    sessao.commit()
    avisar(request, "Dados da peça salvos.")
    return voltar(f"/admin/pecas/{peca.id}")


@roteador.post("/pecas/{peca_id}/grade")
async def salvar_grade(
    peca_id: int, request: Request, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(obter_sessao)
):
    """Recria a grade cor × tamanho mantendo os ids das variantes que continuam."""
    dados = await formulario(request)
    peca = _carregar_peca(sessao, peca_id)
    tamanhos = [t.strip().upper() for t in str(dados.get("tamanhos", "")).replace(";", ",").split(",") if t.strip()]
    tamanhos = list(dict.fromkeys(tamanhos))[:12]
    nomes, hexas = dados.getlist("cor_nome"), dados.getlist("cor_hex")
    if not tamanhos:
        avisar(request, "Informe ao menos um tamanho na grade.")
        return voltar(f"/admin/pecas/{peca.id}#grade")

    existentes = {(v.cor, v.tamanho): v for v in peca.variantes}
    desejadas: set[tuple[str, str]] = set()
    for indice, (nome, hexa) in enumerate(zip(nomes, hexas)):
        nome = str(nome).strip()[:40]
        if not nome or dados.get(f"remover-{indice}") == "on":
            continue
        original = str(dados.get(f"cor_original-{indice}", nome))
        for tamanho in tamanhos:
            campo = f"estoque-{indice}-{tamanho}"
            valor = str(dados.get(campo, "0")).strip()
            qtd = max(0, int(valor)) if valor.lstrip("-").isdigit() else 0
            variante = existentes.get((original, tamanho)) or existentes.get((nome, tamanho))
            if variante is None:
                variante = Variante(tamanho=tamanho)
                peca.variantes.append(variante)
            variante.cor, variante.cor_hex, variante.estoque = nome, str(hexa)[:7] or "#888888", qtd
            desejadas.add((nome, tamanho))
    if not desejadas:
        avisar(request, "A peça precisa de pelo menos uma cor.")
        return voltar(f"/admin/pecas/{peca.id}#grade")
    for variante in list(peca.variantes):
        if (variante.cor, variante.tamanho) not in desejadas:
            peca.variantes.remove(variante)
    sessao.commit()
    avisar(request, "Grade e estoque salvos.")
    return voltar(f"/admin/pecas/{peca.id}#grade")


@roteador.post("/pecas/{peca_id}/fotos")
async def enviar_fotos(
    peca_id: int, request: Request, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(obter_sessao)
):
    dados = await formulario(request)
    peca = _carregar_peca(sessao, peca_id)
    arquivos = [a for a in dados.getlist("fotos") if isinstance(a, UploadFile) and a.filename]
    proxima = max((f.ordem for f in peca.fotos), default=-1) + 1
    erros = []
    for arquivo in arquivos[:12]:
        try:
            nome = salvar_foto(await arquivo.read())
        except ValueError as erro:
            erros.append(f"{arquivo.filename}: {erro}")
            continue
        peca.fotos.append(Foto(arquivo=nome, ordem=proxima))
        proxima += 1
    sessao.commit()
    avisar(request, "; ".join(erros) if erros else f"{len(arquivos)} foto(s) enviada(s).")
    return voltar(f"/admin/pecas/{peca.id}#fotos")


@roteador.post("/pecas/{peca_id}/fotos/{foto_id}/{acao}")
async def acao_foto(
    peca_id: int,
    foto_id: int,
    acao: str,
    request: Request,
    usuario: Usuario = Depends(usuario_logado),
    sessao: Session = Depends(obter_sessao),
):
    await formulario(request)
    peca = _carregar_peca(sessao, peca_id)
    foto = next((f for f in peca.fotos if f.id == foto_id), None)
    if foto is None:
        raise HTTPException(404)
    if acao == "apagar":
        peca.fotos.remove(foto)
        sessao.commit()
        apagar_arquivo_foto(foto.arquivo)
    elif acao == "capa":
        for posicao, f in enumerate([foto] + [f for f in peca.fotos if f is not foto]):
            f.ordem = posicao
        sessao.commit()
    else:
        raise HTTPException(404)
    return voltar(f"/admin/pecas/{peca.id}#fotos")


@roteador.post("/pecas/{peca_id}/apagar")
async def apagar_peca(
    peca_id: int, request: Request, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(obter_sessao)
):
    await formulario(request)
    peca = _carregar_peca(sessao, peca_id)
    arquivos = [f.arquivo for f in peca.fotos]
    sessao.delete(peca)
    sessao.commit()
    for nome in arquivos:
        apagar_arquivo_foto(nome)
    avisar(request, f"“{peca.nome}” apagada. Os pedidos antigos continuam com o registro da peça.")
    return voltar("/admin/pecas")


# ---------------------------------------------------------------- categorias


@roteador.get("/categorias")
def lista_categorias(request: Request, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(obter_sessao)):
    contagem = dict(sessao.execute(select(Peca.categoria_id, func.count(Peca.id)).group_by(Peca.categoria_id)).all())
    return render(
        request,
        sessao,
        "admin/categorias.html",
        {"usuario": usuario, "categorias": _categorias(sessao), "contagem": contagem},
    )


@roteador.post("/categorias")
async def salvar_categorias(
    request: Request, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(obter_sessao)
):
    dados = await formulario(request)
    for categoria in _categorias(sessao):
        if dados.get(f"apagar-{categoria.id}") == "on":
            sessao.delete(categoria)
            continue
        nome = str(dados.get(f"nome-{categoria.id}", categoria.nome)).strip()
        if nome:
            categoria.nome = nome[:80]
        ordem = str(dados.get(f"ordem-{categoria.id}", categoria.ordem))
        categoria.ordem = int(ordem) if ordem.lstrip("-").isdigit() else categoria.ordem
        categoria.ativa = dados.get(f"ativa-{categoria.id}") == "on"
    nova = str(dados.get("nova", "")).strip()
    if nova:
        slug, n = slugificar(nova), 2
        while sessao.scalar(select(Categoria).where(Categoria.slug == slug)):
            slug, n = f"{slugificar(nova)}-{n}", n + 1
        sessao.add(Categoria(nome=nova[:80], slug=slug, ordem=len(_categorias(sessao))))
    sessao.commit()
    avisar(request, "Categorias salvas.")
    return voltar("/admin/categorias")


# ---------------------------------------------------------------- pedidos


@roteador.get("/pedidos")
def lista_pedidos(
    request: Request,
    status: str = "",
    q: str = "",
    usuario: Usuario = Depends(usuario_logado),
    sessao: Session = Depends(obter_sessao),
):
    consulta = select(Pedido).options(selectinload(Pedido.itens)).order_by(Pedido.id.desc())
    if status in STATUS_PEDIDO:
        consulta = consulta.where(Pedido.status == status)
    if q.strip():
        termo = f"%{q.strip()}%"
        consulta = consulta.where(Pedido.nome.ilike(termo) | Pedido.codigo.ilike(termo) | Pedido.whatsapp.ilike(termo))
    contagem = dict(sessao.execute(select(Pedido.status, func.count(Pedido.id)).group_by(Pedido.status)).all())
    return render(
        request,
        sessao,
        "admin/pedidos.html",
        {"usuario": usuario, "pedidos": list(sessao.scalars(consulta.limit(300))), "status": status, "q": q, "contagem": contagem},
    )


@roteador.get("/pedidos/{pedido_id}")
def ver_pedido(
    pedido_id: int, request: Request, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(obter_sessao)
):
    pedido = sessao.scalar(select(Pedido).where(Pedido.id == pedido_id).options(selectinload(Pedido.itens)))
    if pedido is None:
        raise HTTPException(404)
    return render(request, sessao, "admin/pedido.html", {"usuario": usuario, "pedido": pedido})


@roteador.post("/pedidos/{pedido_id}/status")
async def status_pedido(
    pedido_id: int, request: Request, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(obter_sessao)
):
    dados = await formulario(request)
    pedido = sessao.scalar(select(Pedido).where(Pedido.id == pedido_id).options(selectinload(Pedido.itens)))
    novo = str(dados.get("status", ""))
    if pedido is None or novo not in STATUS_PEDIDO:
        raise HTTPException(404)
    mudar_status(sessao, pedido, novo)
    avisar(request, f"Pedido {pedido.codigo}: {STATUS_PEDIDO[novo].lower()}.")
    return voltar(f"/admin/pedidos/{pedido.id}")


# ---------------------------------------------------------------- configurações


@roteador.get("/configuracoes")
def tela_config(request: Request, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(obter_sessao)):
    return render(request, sessao, "admin/configuracoes.html", {"usuario": usuario, "rotulos": ROTULOS_CONFIG})


@roteador.post("/configuracoes")
async def gravar_config(request: Request, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(obter_sessao)):
    dados = await formulario(request)
    salvar_config(sessao, {chave: str(dados.get(chave, "")) for chave in ROTULOS_CONFIG})
    avisar(request, "Configurações salvas.")
    return voltar("/admin/configuracoes")
