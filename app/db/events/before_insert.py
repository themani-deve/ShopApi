import uuid

from db.models import Product
from sqlalchemy import event
from utils.generators import slugify


@event.listens_for(Product, "before_insert")
def set_slug(mapper, connection, target):
    if not target.slug and target.name:
        base_slug = slugify(target.name)
        target.slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
