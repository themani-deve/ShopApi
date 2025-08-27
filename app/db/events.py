import uuid

from db.models import CartItem, Product
from sqlalchemy import event
from sqlalchemy.orm import Session
from utils.generators import slugify


@event.listens_for(Product, "before_insert")
def set_slug(mapper, connection, target: Product):
    if not target.slug and target.name:
        base_slug = slugify(target.name)
        target.slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"


@event.listens_for(Session, "before_flush")
def update_cart_amount(session, flush_context, instances):
    for obj in session.new.union(session.dirty).union(session.deleted):
        if isinstance(obj, CartItem) and obj.cart:
            obj.cart.amount = sum(item.product.get_price * item.quantity for item in obj.cart.items)
