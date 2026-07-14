import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Table,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


memory_stone_people = Table(
    "memory_stone_people",
    Base.metadata,
    Column(
        "memory_stone_id",
        UUID(as_uuid=True),
        ForeignKey("memory_stones.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "person_id",
        UUID(as_uuid=True),
        ForeignKey("people.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "relationship_type",
        String(50),
        nullable=False,
        server_default=text("'mentioned'"),
    ),
)


class Person(Base):
    __tablename__ = "people"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    display_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    memory_stones: Mapped[list["MemoryStone"]] = relationship(
        secondary=memory_stone_people,
        back_populates="people",
    )


class MemoryStone(Base):
    __tablename__ = "memory_stones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    stone_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="memory",
        server_default=text("'memory'"),
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="user_entry",
        server_default=text("'user_entry'"),
    )

    source_reference: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    remembered_at: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    confidence: Mapped[Decimal] = mapped_column(
        Numeric(4, 3),
        nullable=False,
        default=Decimal("1.000"),
        server_default=text("1.000"),
    )

    is_inferred: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    people: Mapped[list[Person]] = relationship(
        secondary=memory_stone_people,
        back_populates="memory_stones",
    )
