"""Regras da loja: configurações, preço varejo/atacado, pedidos, estoque e WhatsApp."""

import hashlib
import hmac
import re
import secrets
import unicodedata
import uuid
from dataclasses import dataclass, field
from io import BytesIO
from urllib.parse import quote

from PIL import Image, ImageOps
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import config
from app.models import ENTREGAS, Configuracao, ItemPedido, Pedido, Peca, Usuario, Variante

# ---------------------------------------------------------------- configurações

PADROES = {
    "nome_loja": "Vanuza Andrade",
    "bordao": "Conforto e estilo você encontra aqui",
    "whatsapp": "5562900000000",
    "instagram": "vanuzaandradeloja",
    "endereco": "Mega Moda Shopping · Entrada 8 · Rua Alameda dos Eventos · Loja 263",
    "cidade": "Goiânia (GO)",
    "horario": "",
    "atacado_minimo": "6",
    "texto_atacado": "O preço de atacado vale para pedidos a partir da quantidade mínima de peças, que podem ser sortidas entre modelos, cores e tamanhos.",
    "texto_entrega": "Retire na loja 263 do Mega Moda Shopping ou informe sua excursão ou transportadora. O frete e o envio são combinados pelo WhatsApp.",
    "exemplo_revisado": "",
    # Política de trocas ainda não confirmada pela loja: fica vazia (e oculta) até ser preenchida no painel.
    "texto_trocas": "",
}

ROTULOS_CONFIG = {
    "nome_loja": "Nome da loja",
    "bordao": "Frase de apresentação",
    "whatsapp": "WhatsApp que recebe os pedidos (com 55 e DDD, só números)",
    "instagram": "Usuário do Instagram (sem @)",
    "endereco": "Endereço da loja",
    "cidade": "Cidade",
    "horario": "Horário de funcionamento",
    "atacado_minimo": "Peças mínimas para preço de atacado",
    "texto_atacado": "Texto: como funciona o atacado",
    "texto_entrega": "Texto: entrega e retirada",
    "texto_trocas": "Texto: política de trocas (vazio = não aparece na loja)",
}


def ler_config(sessao: Session) -> dict[str, str]:
    valores = dict(PADROES)
    for item in sessao.scalars(select(Configuracao)):
        valores[item.chave] = item.valor
    return valores


def salvar_config(sessao: Session, novos: dict[str, str]) -> None:
    for chave, valor in novos.items():
        if chave not in PADROES:
            continue
        valor = valor.strip()
        if chave == "whatsapp":
            valor = so_digitos(valor)
        if chave == "atacado_minimo":
            valor = str(max(1, int(so_digitos(valor) or "1")))
        if chave == "instagram":
            valor = valor.lstrip("@")
        item = sessao.get(Configuracao, chave)
        if item is None:
            sessao.add(Configuracao(chave=chave, valor=valor))
        else:
            item.valor = valor
    sessao.commit()


# ---------------------------------------------------------------- utilidades


def so_digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto or "")


def slugificar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-") or "peca"


def slug_unico(sessao: Session, texto: str, ignorar_id: int | None = None) -> str:
    base = slugificar(texto)
    slug, n = base, 2
    while True:
        existente = sessao.scalar(select(Peca).where(Peca.slug == slug))
        if existente is None or existente.id == ignorar_id:
            return slug
        slug, n = f"{base}-{n}", n + 1


def reais(centavos: int | None) -> str:
    if centavos is None:
        return ""
    inteiro, cent = divmod(abs(centavos), 100)
    milhar = f"{inteiro:,}".replace(",", ".")
    return f"{'-' if centavos < 0 else ''}R$ {milhar},{cent:02d}"


def ler_centavos(texto: str) -> int | None:
    """Aceita '189,90', '189.90', 'R$ 1.189,90' ou '189'. Vazio vira None."""
    texto = (texto or "").replace("R$", "").strip()
    if not texto:
        return None
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        valor = round(float(texto) * 100)
    except ValueError as erro:
        raise ValueError(f"Preço inválido: {texto!r}") from erro
    if valor < 0:
        raise ValueError("Preço não pode ser negativo")
    return valor


def formatar_telefone(digitos: str) -> str:
    d = so_digitos(digitos)
    if d.startswith("55") and len(d) in (12, 13):
        d = d[2:]
    if len(d) == 11:
        return f"({d[:2]}) {d[2:7]}-{d[7:]}"
    if len(d) == 10:
        return f"({d[:2]}) {d[2:6]}-{d[6:]}"
    return digitos


# ---------------------------------------------------------------- senhas


def gerar_hash(senha: str) -> str:
    sal = secrets.token_bytes(16)
    chave = hashlib.scrypt(senha.encode(), salt=sal, n=2**14, r=8, p=1)
    return f"scrypt${sal.hex()}${chave.hex()}"


def conferir_senha(senha: str, guardado: str) -> bool:
    try:
        _, sal, chave = guardado.split("$")
    except ValueError:
        return False
    calculado = hashlib.scrypt(senha.encode(), salt=bytes.fromhex(sal), n=2**14, r=8, p=1)
    return hmac.compare_digest(calculado.hex(), chave)


def autenticar(sessao: Session, email: str, senha: str) -> Usuario | None:
    usuario = sessao.scalar(select(Usuario).where(Usuario.email == email.strip().lower()))
    if usuario and conferir_senha(senha, usuario.senha_hash):
        return usuario
    return None


# ---------------------------------------------------------------- fotos


def salvar_foto(conteudo: bytes) -> str:
    """Normaliza a foto (orientação, tamanho, JPEG) e devolve o nome do arquivo."""
    if len(conteudo) > config.TAMANHO_MAX_FOTO:
        raise ValueError("Foto maior que 8 MB")
    try:
        imagem = Image.open(BytesIO(conteudo))
        imagem = ImageOps.exif_transpose(imagem).convert("RGB")
    except Exception as erro:  # Pillow levanta vários tipos
        raise ValueError("Arquivo não é uma imagem válida (use JPG, PNG ou WebP)") from erro
    imagem.thumbnail((config.LADO_MAX_FOTO, config.LADO_MAX_FOTO))
    config.PASTA_UPLOADS.mkdir(parents=True, exist_ok=True)
    nome = f"{uuid.uuid4().hex}.jpg"
    imagem.save(config.PASTA_UPLOADS / nome, "JPEG", quality=84, optimize=True, progressive=True)
    return nome


def apagar_arquivo_foto(nome: str) -> None:
    caminho = config.PASTA_UPLOADS / nome
    if caminho.is_file():
        caminho.unlink()


# ---------------------------------------------------------------- pedido


class ErroPedido(ValueError):
    pass


@dataclass
class Linha:
    variante: Variante
    quantidade: int
    preco_unitario: int
    disponivel: int

    @property
    def subtotal(self) -> int:
        return self.quantidade * self.preco_unitario


@dataclass
class Cotacao:
    linhas: list[Linha] = field(default_factory=list)
    atacado: bool = False
    minimo_atacado: int = 6
    removidos: list[int] = field(default_factory=list)

    @property
    def quantidade(self) -> int:
        return sum(l.quantidade for l in self.linhas)

    @property
    def total(self) -> int:
        return sum(l.subtotal for l in self.linhas)

    @property
    def total_varejo(self) -> int:
        return sum(l.quantidade * l.variante.peca.preco_varejo for l in self.linhas)

    @property
    def faltam_para_atacado(self) -> int:
        return max(0, self.minimo_atacado - self.quantidade)


def cotar(sessao: Session, itens: list[tuple[int, int]], minimo_atacado: int) -> Cotacao:
    """Calcula preços a partir de (variante_id, quantidade). O servidor é a fonte do preço."""
    quantidades: dict[int, int] = {}
    for variante_id, qtd in itens:
        if qtd > 0:
            quantidades[variante_id] = quantidades.get(variante_id, 0) + qtd

    variantes = {
        v.id: v
        for v in sessao.scalars(
            select(Variante)
            .where(Variante.id.in_(quantidades))
            .options(selectinload(Variante.peca).selectinload(Peca.fotos))
        )
    }
    cotacao = Cotacao(minimo_atacado=minimo_atacado)
    for variante_id, qtd in quantidades.items():
        variante = variantes.get(variante_id)
        if variante is None or not variante.peca.ativa:
            cotacao.removidos.append(variante_id)
            continue
        cotacao.linhas.append(Linha(variante, min(qtd, 999), variante.peca.preco_varejo, variante.estoque))

    cotacao.atacado = cotacao.quantidade >= minimo_atacado and any(
        l.variante.peca.preco_atacado is not None for l in cotacao.linhas
    )
    if cotacao.atacado:
        for linha in cotacao.linhas:
            if linha.variante.peca.preco_atacado is not None:
                linha.preco_unitario = linha.variante.peca.preco_atacado
    return cotacao


def proximo_codigo(sessao: Session) -> str:
    ultimo = sessao.scalar(select(Pedido.id).order_by(Pedido.id.desc()).limit(1)) or 0
    return f"VA-{ultimo + 1:04d}"


def criar_pedido(
    sessao: Session,
    itens: list[tuple[int, int]],
    *,
    nome: str,
    whatsapp: str,
    cidade: str,
    entrega: str,
    detalhe_entrega: str,
    observacao: str,
    minimo_atacado: int,
) -> Pedido:
    nome = nome.strip()
    telefone = so_digitos(whatsapp)
    if len(nome) < 2:
        raise ErroPedido("Informe seu nome.")
    if len(telefone) < 10:
        raise ErroPedido("Informe um WhatsApp com DDD.")
    if entrega not in ENTREGAS:
        raise ErroPedido("Escolha como vai receber o pedido.")
    if entrega != "retirada" and not detalhe_entrega.strip():
        raise ErroPedido("Informe o nome da excursão ou da transportadora.")

    cotacao = cotar(sessao, itens, minimo_atacado)
    if not cotacao.linhas:
        raise ErroPedido("Seu pedido está vazio.")
    faltando = [l for l in cotacao.linhas if l.quantidade > l.variante.estoque]
    if faltando:
        l = faltando[0]
        raise ErroPedido(
            f"{l.variante.peca.nome} ({l.variante.cor}, {l.variante.tamanho}): "
            f"só temos {l.variante.estoque} em estoque."
        )

    pedido = Pedido(
        codigo=proximo_codigo(sessao),
        nome=nome[:120],
        whatsapp=telefone[:20],
        cidade=cidade.strip()[:80],
        entrega=entrega,
        detalhe_entrega=detalhe_entrega.strip()[:200],
        observacao=observacao.strip()[:2000],
        atacado=cotacao.atacado,
        total=cotacao.total,
    )
    for linha in cotacao.linhas:
        v = linha.variante
        v.estoque -= linha.quantidade
        pedido.itens.append(
            ItemPedido(
                variante_id=v.id,
                nome=v.peca.nome,
                referencia=v.peca.referencia,
                cor=v.cor,
                tamanho=v.tamanho,
                quantidade=linha.quantidade,
                preco_unitario=linha.preco_unitario,
            )
        )
    sessao.add(pedido)
    sessao.commit()
    return pedido


def mudar_status(sessao: Session, pedido: Pedido, novo: str) -> None:
    """Cancelar devolve as peças ao estoque; sair de cancelado retira de novo."""
    if novo == pedido.status:
        return
    if novo == "cancelado":
        sinal = 1
    elif pedido.status == "cancelado":
        sinal = -1
    else:
        sinal = 0
    if sinal:
        for item in pedido.itens:
            if item.variante_id and (v := sessao.get(Variante, item.variante_id)):
                v.estoque = max(0, v.estoque + sinal * item.quantidade)
    pedido.status = novo
    sessao.commit()


def mensagem_whatsapp(pedido: Pedido, loja: dict[str, str]) -> str:
    linhas = [
        f"Olá, {loja['nome_loja']}! Quero fazer o pedido *{pedido.codigo}*:",
        "",
    ]
    for item in pedido.itens:
        ref = f" (ref. {item.referencia})" if item.referencia else ""
        linhas.append(
            f"• {item.quantidade}x {item.nome}{ref} · {item.cor} · {item.tamanho} · {reais(item.preco_unitario)} cada"
        )
    linhas += [
        "",
        f"*Total: {reais(pedido.total)}* ({pedido.quantidade_pecas} peças, preço de {'atacado' if pedido.atacado else 'varejo'})",
        f"Entrega: {ENTREGAS[pedido.entrega]}" + (f" · {pedido.detalhe_entrega}" if pedido.detalhe_entrega else ""),
        f"Nome: {pedido.nome}",
    ]
    if pedido.cidade:
        linhas.append(f"Cidade: {pedido.cidade}")
    if pedido.observacao:
        linhas.append(f"Obs.: {pedido.observacao}")
    return "\n".join(linhas)


def link_whatsapp(numero: str, texto: str = "") -> str:
    base = f"https://wa.me/{so_digitos(numero)}"
    return f"{base}?text={quote(texto)}" if texto else base
