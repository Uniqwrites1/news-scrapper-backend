from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), index=True)
    link = Column(String(500), unique=True, index=True)
    summary = Column(Text)
    source = Column(String(100), index=True)
    published_date = Column(DateTime, index=True)
    extracted_date = Column(DateTime, default=datetime.utcnow)
    is_security_related = Column(Boolean, default=False)
    locations = Column(Text)  # Comma-separated
    incident_type = Column(String(100))
    
    def __repr__(self):
        return f"<Article(title='{self.title}', source='{self.source}')>"
