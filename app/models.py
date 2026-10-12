"""Tabelas da loja. Valores em centavos (inteiros) para não errar arredondamento."""

import secrets
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

TAMANHOS_PADRAO = ["P", "M", "G", "GG"]

STATUS_PEDIDO = {
    "novo": "Novo",
    "confirmado": "Confirmado",
    "separado": "Separado",
    "entregue": "Entregue",
    "cancelado": "Cancelado",
}

ENTREGAS = {
    "retirada": "Retirada na loja",
    "excursao": "Excursão",
    "transportadora": "Transportadora",
}


class Categoria(Base):
    __tablename__ = "categoria"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(80))
    slug: Mapped[str] = mapped_column(String(90), unique=True)
    ordem: Mapped[int] = mapped_column(Integer, default=0)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)

    pecas: Mapped[list["Peca"]] = relationship(back_populates="categoria")


class Peca(Base):
    __tablename__ = "peca"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(140), unique=True)
    descricao: Mapped[str] = mapped_column(Text, default="")
    tecido: Mapped[str] = mapped_column(String(80), default="")
    referencia: Mapped[str] = mapped_column(String(40), default="")
    categoria_id: Mapped[int | None] = mapped_column(ForeignKey("categoria.id", ondelete="SET NULL"))
    preco_varejo: Mapped[int] = mapped_column(Integer)
    preco_atacado: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)
    destaque: Mapped[bool] = mapped_column(Boolean, default=False)
    ordem: Mapped[int] = mapped_column(Integer, default=0)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    categoria: Mapped[Categoria | None] = relationship(back_populates="pecas")
    fotos: Mapped[list["Foto"]] = relationship(
        back_populates="peca", cascade="all, delete-orphan", order_by="Foto.ordem"
    )
    variantes: Mapped[list["Variante"]] = relationship(
        back_populates="peca", cascade="all, delete-orphan", order_by="Variante.id"
    )

    @property
    def foto_capa(self) -> "Foto | None":
        return self.fotos[0] if self.fotos else None

    @property
    def estoque_total(self) -> int:
        return sum(v.estoque for v in self.variantes)

    @property
    def cores(self) -> list[tuple[str, str]]:
        vistas: dict[str, str] = {}
        for v in self.variantes:
            vistas.setdefault(v.cor, v.cor_hex)
        return list(vistas.items())

    @property
    def tamanhos(self) -> list[str]:
        presentes = {v.tamanho for v in self.variantes}
        ordem = [t for t in TAMANHOS_PADRAO if t in presentes]
        return ordem + sorted(presentes - set(ordem))

    @property
    def variantes_json(self) -> list[dict]:
        return [{"id": v.id, "cor": v.cor, "tamanho": v.tamanho, "estoque": v.estoque} for v in self.variantes]

    def tamanhos_disponiveis(self) -> set[str]:
        return {v.tamanho for v in self.variantes if v.estoque > 0}


class Foto(Base):
    __tablename__ = "foto"

    id: Mapped[int] = mapped_column(primary_key=True)
    peca_id: Mapped[int] = mapped_column(ForeignKey("peca.id", ondelete="CASCADE"))
    arquivo: Mapped[str] = mapped_column(String(200))
    ordem: Mapped[int] = mapped_column(Integer, default=0)

    peca: Mapped[Peca] = relationship(back_populates="fotos")


class Variante(Base):
    __tablename__ = "variante"
    __table_args__ = (UniqueConstraint("peca_id", "cor", "tamanho"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    peca_id: Mapped[int] = mapped_column(ForeignKey("peca.id", ondelete="CASCADE"))
    cor: Mapped[str] = mapped_column(String(40))
    cor_hex: Mapped[str] = mapped_column(String(7), default="#888888")
    tamanho: Mapped[str] = mapped_column(String(10))
    estoque: Mapped[int] = mapped_column(Integer, default=0)

    peca: Mapped[Peca] = relationship(back_populates="variantes")


class Pedido(Base):
    __tablename__ = "pedido"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    # Vai no link de acompanhamento para ninguém abrir o pedido de outra pessoa pelo código.
    token: Mapped[str] = mapped_column(String(32), default=lambda: secrets.token_urlsafe(12))
    nome: Mapped[str] = mapped_column(String(120))
    whatsapp: Mapped[str] = mapped_column(String(20))
    cidade: Mapped[str] = mapped_column(String(80), default="")
    entrega: Mapped[str] = mapped_column(String(20))
    detalhe_entrega: Mapped[str] = mapped_column(String(200), default="")
    observacao: Mapped[str] = mapped_column(Text, default="")
    atacado: Mapped[bool] = mapped_column(Boolean, default=False)
    total: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="novo")
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    itens: Mapped[list["ItemPedido"]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan", order_by="ItemPedido.id"
    )

    @property
    def quantidade_pecas(self) -> int:
        return sum(i.quantidade for i in self.itens)


class ItemPedido(Base):
    """Guarda uma cópia de nome, cor, tamanho e preço: a peça pode mudar depois."""

    __tablename__ = "item_pedido"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedido.id", ondelete="CASCADE"))
    variante_id: Mapped[int | None] = mapped_column(ForeignKey("variante.id", ondelete="SET NULL"))
    nome: Mapped[str] = mapped_column(String(120))
    referencia: Mapped[str] = mapped_column(String(40), default="")
    cor: Mapped[str] = mapped_column(String(40))
    tamanho: Mapped[str] = mapped_column(String(10))
    quantidade: Mapped[int] = mapped_column(Integer)
    preco_unitario: Mapped[int] = mapped_column(Integer)

    pedido: Mapped[Pedido] = relationship(back_populates="itens")

    @property
    def subtotal(self) -> int:
        return self.quantidade * self.preco_unitario


class Configuracao(Base):
    __tablename__ = "configuracao"

    chave: Mapped[str] = mapped_column(String(60), primary_key=True)
    valor: Mapped[str] = mapped_column(Text, default="")


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(160), unique=True)
    nome: Mapped[str] = mapped_column(String(80))
    senha_hash: Mapped[str] = mapped_column(String(200))
