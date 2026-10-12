"""Cria as tabelas, o usuário do painel e o catálogo inicial.

Uso: uv run python -m app.seed            (só cria o que falta)
     uv run python -m app.seed --senha    (gera uma nova senha para o painel)
"""

import os
import secrets
import shutil
import sys

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import config
from app.db import Base, SessaoLocal, engine
from app.models import Categoria, Foto, Peca, Usuario, Variante
from app.servicos import gerar_hash, slugificar

PASTA_FOTOS_INICIAIS = config.RAIZ / "static" / "img" / "catalogo"

# Nomes, referências, preços e estoque são de exemplo: as fotos vieram do Instagram
# da loja, mas o perfil não publica esses dados. Revise tudo no painel.
CATALOGO_INICIAL = [
    {
        "nome": "Vestido Midi Felino",
        "referencia": "VA-101",
        "categoria": "Vestidos midi",
        "tecido": "Viscolinho",
        "descricao": "Vestido midi sem manga com estampa felina em preto sobre laranja queimado. Saia evasê com barra em camada e caimento leve de viscolinho.",
        "preco_varejo": 15990,
        "preco_atacado": 11990,
        "destaque": True,
        "fotos": ["p03.jpg", "p01.jpg"],
        "cores": [("Laranja felino", "#c8551f")],
    },
    {
        "nome": "Vestido Longo Mosaico Azul",
        "referencia": "VA-102",
        "categoria": "Vestidos longos",
        "tecido": "Viscose premium",
        "descricao": "Vestido longo de alcinha com estampa geométrica azul e areia. Saia em três camadas com bastante roda.",
        "preco_varejo": 18990,
        "preco_atacado": 13990,
        "destaque": False,
        "fotos": ["p05.jpg", "p06.jpg", "p04.jpg"],
        "cores": [("Azul mosaico", "#3d6fd1")],
    },
    {
        "nome": "Vestido Longo Folhagem Pêssego",
        "referencia": "VA-103",
        "categoria": "Vestidos longos",
        "tecido": "Viscose premium",
        "descricao": "Vestido longo de alcinha com estampa de folhagens verdes e flores laranja sobre fundo pêssego. Elástico na cintura e saia com camada.",
        "preco_varejo": 18990,
        "preco_atacado": 13990,
        "destaque": False,
        "fotos": ["p10.jpg", "p12.jpg", "p08.jpg"],
        "cores": [("Folhagem pêssego", "#f0a77a")],
    },
]

ESTOQUE_INICIAL = {"P": 4, "M": 6, "G": 6, "GG": 3}


def criar_tabelas() -> None:
    Base.metadata.create_all(engine)


def garantir_admin(sessao: Session, nova_senha: bool = False) -> str | None:
    """Cria o usuário do painel. Devolve a senha quando ela foi gerada agora."""
    email = os.environ.get("ADMIN_EMAIL", "admin@vanuzaandrade.com.br").strip().lower()
    usuario = sessao.scalar(select(Usuario).where(Usuario.email == email))
    if usuario and not nova_senha:
        return None
    senha = os.environ.get("ADMIN_SENHA") or secrets.token_urlsafe(9)
    if usuario is None:
        usuario = Usuario(email=email, nome="Vanuza", senha_hash=gerar_hash(senha))
        sessao.add(usuario)
    else:
        usuario.senha_hash = gerar_hash(senha)
    sessao.commit()
    if os.environ.get("ADMIN_SENHA"):
        return None
    arquivo = config.PASTA_DADOS / "acesso-painel.txt"
    arquivo.write_text(f"E-mail: {email}\nSenha: {senha}\nTroque a senha em /admin/conta.\n", encoding="utf-8")
    return str(arquivo)


def popular_catalogo(sessao: Session) -> bool:
    if sessao.scalar(select(Peca.id).limit(1)) is not None:
        return False
    config.PASTA_UPLOADS.mkdir(parents=True, exist_ok=True)
    categorias: dict[str, Categoria] = {}
    for ordem, nome in enumerate(["Vestidos longos", "Vestidos midi"]):
        categorias[nome] = Categoria(nome=nome, slug=slugificar(nome), ordem=ordem)
        sessao.add(categorias[nome])

    for ordem, dados in enumerate(CATALOGO_INICIAL):
        peca = Peca(
            nome=dados["nome"],
            slug=slugificar(dados["nome"]),
            referencia=dados["referencia"],
            categoria=categorias[dados["categoria"]],
            tecido=dados["tecido"],
            descricao=dados["descricao"],
            preco_varejo=dados["preco_varejo"],
            preco_atacado=dados["preco_atacado"],
            destaque=dados["destaque"],
            ordem=ordem,
        )
        for posicao, arquivo in enumerate(dados["fotos"]):
            destino = f"inicial-{arquivo}"
            shutil.copyfile(PASTA_FOTOS_INICIAIS / arquivo, config.PASTA_UPLOADS / destino)
            peca.fotos.append(Foto(arquivo=destino, ordem=posicao))
        for cor, hexa in dados["cores"]:
            for tamanho, qtd in ESTOQUE_INICIAL.items():
                peca.variantes.append(Variante(cor=cor, cor_hex=hexa, tamanho=tamanho, estoque=qtd))
        sessao.add(peca)
    sessao.commit()
    return True


def preparar(nova_senha: bool = False, catalogo: bool = True) -> str | None:
    criar_tabelas()
    with SessaoLocal() as sessao:
        arquivo = garantir_admin(sessao, nova_senha)
        if catalogo:
            popular_catalogo(sessao)
    return arquivo


if __name__ == "__main__":
    gerado = preparar(nova_senha="--senha" in sys.argv)
    if gerado:
        print(f"Acesso ao painel salvo em {gerado}")
    print("Banco pronto.")
