import uuid
from pgvector.sqlalchemy import VECTOR
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Table,
    Text,
    func,
    text,
    UniqueConstraint
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


memory_stone_places = Table(
    "memory_stone_places",
    Base.metadata,
    Column(
        "memory_stone_id",
        UUID(as_uuid=True),
        ForeignKey("memory_stones.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "place_id",
        UUID(as_uuid=True),
        ForeignKey("places.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "relationship_type",
        String(50),
        nullable=False,
        server_default=text("'location'"),
    ),
)


memory_stone_events = Table(
    "memory_stone_events",
    Base.metadata,
    Column(
        "memory_stone_id",
        UUID(as_uuid=True),
        ForeignKey("memory_stones.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "event_id",
        UUID(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "relationship_type",
        String(50),
        nullable=False,
        server_default=text("'related'"),
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
    aliases: Mapped[list["PersonAlias"]] = relationship(
        back_populates="person",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Place(Base):
    __tablename__ = "places"

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

    latitude: Mapped[Decimal | None] = mapped_column(
        Numeric(9, 6),
        nullable=True,
    )

    longitude: Mapped[Decimal | None] = mapped_column(
        Numeric(9, 6),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    memory_stones: Mapped[list["MemoryStone"]] = relationship(
        secondary=memory_stone_places,
        back_populates="places",
    )


class Event(Base):
    __tablename__ = "events"

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

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    memory_stones: Mapped[list["MemoryStone"]] = relationship(
        secondary=memory_stone_events,
        back_populates="events",
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
    source_text_hash: Mapped[str | None] = mapped_column(
    String(64),
    nullable=True,
    unique=True,
    index=True,
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
    embedding: Mapped[list[float] | None] = mapped_column(
        VECTOR(1536),
        nullable=True,
    )

    embedding_model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    embedded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    embedding_source_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
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

    places: Mapped[list[Place]] = relationship(
        secondary=memory_stone_places,
        back_populates="memory_stones",
    )

    events: Mapped[list[Event]] = relationship(
        secondary=memory_stone_events,
        back_populates="memory_stones",
    )
class PersonAlias(Base):
    __tablename__ = "person_aliases"
    __table_args__ = (
        UniqueConstraint(
            "normalized_alias",
            name="uq_person_aliases_normalized_alias",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    person_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("people.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    alias: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    normalized_alias: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    person: Mapped["Person"] = relationship(
        back_populates="aliases",
    )