from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

Base = declarative_base()
engine = create_engine("sqlite:///items.db")
Session = sessionmaker(bind=engine)

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

Base.metadata.create_all(engine)

@view_config(route_name="get_items", request_method="GET", renderer="json")
def get_items(request):
    session = Session()
    items = session.query(Item).all()
    return [{"id": item.id, "name": item.name} for item in items]

@view_config(route_name="post_item", request_method="POST", renderer="json")
def post_item(request):
    session = Session()
    data = request.json_body
    name = data.get("name")
    new_item = Item(name=name)
    session.add(new_item)
    session.commit()
    return {"message": "Item added", "id": new_item.id, "name": new_item.name}

if __name__ == "__main__":
    with Configurator() as config:
        config.add_route("get_items", "/api/items")
        config.add_route("post_item", "/api/item")
        config.scan()
        app = config.make_wsgi_app()

    server = make_server("0.0.0.0", 8080, app)
    server.serve_forever()
