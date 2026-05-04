from connection import Base, engine
import models

Base.metadata.create_all(engine)
print("Tabelas criadas com sucesso!")