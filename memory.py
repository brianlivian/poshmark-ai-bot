from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, Boolean, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, sessionmaker
from config import SQLITE_PATH

Base = declarative_base()
engine = create_engine(f"sqlite:///{SQLITE_PATH}")
Session = sessionmaker(bind=engine)


class Listing(Base):
    __tablename__ = "listings"
    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    source = Column(String, default="poshmark")

    price = Column(Float, nullable=True)
    vision_is_modern = Column(Boolean, default=False)
    vision_style = Column(Float, default=0)
    vision_condition = Column(Float, default=0)
    score = Column(Float, default=0)

    brand_detected = Column(String, default="")

    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('url', name='uq_url'),)


def init_db():
    Base.metadata.create_all(engine)


def upsert_listing(data: Dict) -> bool:
    """Insert or update by URL. Returns True if new row was created."""
    session = Session()
    try:
        row = session.query(Listing).filter_by(url=data["url"]).one_or_none()
        now = datetime.utcnow()
        if row:
            row.title = data.get("title", row.title)
            row.image_url = data.get("image_url", row.image_url)
            if data.get("price") is not None:
                row.price = data.get("price")
            if data.get("vision"):
                v = data["vision"]
                row.vision_is_modern = bool(v.get("is_modern"))
                row.vision_style = float(v.get("style_score", 0))
                row.vision_condition = float(v.get("condition_score", 0))
            if data.get("score") is not None:
                row.score = float(data.get("score"))
            row.brand_detected = data.get("brand_detected", row.brand_detected)
            row.last_seen = now
            session.add(row)
            session.commit()
            return False
        else:
            v = data.get("vision", {})
            row = Listing(
                url=data["url"],
                title=data.get("title", ""),
                image_url=data.get("image_url", ""),
                source=data.get("source", "poshmark"),
                price=float(data.get("price", 0) or 0),
                vision_is_modern=bool(v.get("is_modern", False)),
                vision_style=float(v.get("style_score", 0)),
                vision_condition=float(v.get("condition_score", 0)),
                score=float(data.get("score", 0)),
                brand_detected=data.get("brand_detected", ""),
                first_seen=now,
                last_seen=now,
            )
            session.add(row)
            session.commit()
            return True
    finally:
        session.close()