from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from pgvector.sqlalchemy import Vector

from app.db.session import Base

EMBEDDING_DIM = (
    2048  # must match the embedding model actually used (verify via a real API call)
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    geolife_id = Column(String, nullable=False, unique=True)  # e.g. "000"

    trajectories = relationship(
        "Trajectory", back_populates="user", cascade="all, delete-orphan"
    )


class Trajectory(Base):
    __tablename__ = "trajectories"
    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    mode = Column(String, nullable=True)  # walk / bike / car / bus / subway / train ...
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    distance_m = Column(Float, nullable=True)
    duration_s = Column(Integer, nullable=True)
    avg_speed_mps = Column(Float, nullable=True)
    geom = Column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=False)

    user = relationship("User", back_populates="trajectories")
    points = relationship(
        "TrajectoryPoint", back_populates="trajectory", cascade="all, delete-orphan"
    )


class TrajectoryPoint(Base):
    __tablename__ = "trajectory_points"
    id = Column(Integer, primary_key=True)
    trajectory_id = Column(
        Integer, ForeignKey("trajectories.id", ondelete="CASCADE"), nullable=False
    )
    seq = Column(Integer, nullable=False)  # order of the point within the trajectory
    timestamp = Column(DateTime(timezone=True), nullable=False)
    altitude_m = Column(Float, nullable=True)
    geom = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)

    trajectory = relationship("Trajectory", back_populates="points")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    source = Column(String, nullable=False)
    source_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chunks = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True)
    document_id = Column(
        Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)

    document = relationship("Document", back_populates="chunks")
