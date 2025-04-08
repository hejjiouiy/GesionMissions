from app.config.database import Base, engine
from app.models import Mission

Base.metadata.create_all(engine)