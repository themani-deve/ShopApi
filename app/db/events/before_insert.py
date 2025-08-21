from db.models import Product
from sqlalchemy import event, func, select
from sqlalchemy.orm import Session
from utils.generators import slugify


@event.listens_for(Product, "before_insert")
def set_slug(mapper, connection, target):
    if not target.slug and target.name:
        base_slug = slugify(target.name)
        session = Session(bind=connection)

        max_suffix = session.execute(select(func.max(Product.slug)).where(Product.slug.like(f"{base_slug}%"))).scalar()

        if not max_suffix:
            target.slug = base_slug

        elif max_suffix == base_slug:
            target.slug = f"{base_slug}-1"

        else:
            try:
                num = int(max_suffix.split("-")[-1])
                target.slug = f"{base_slug}-{num+1}"
            except ValueError:
                target.slug = f"{base_slug}-1"
