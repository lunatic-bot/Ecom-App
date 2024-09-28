from sqlalchemy import Column, Integer, UUID, ForeignKey 
from sqlalchemy.orm import relationship
from base import Base
import uuid

class ShoppingCart(Base):
    __tablename__ = 'shopping_carts'

    cart_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    user = relationship("User", back_populates="shopping_cart")


class CartItem(Base):
    __tablename__ = 'cart_items'

    cart_item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id = Column(UUID(as_uuid=True), ForeignKey('shopping_carts.cart_id'), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.product_id'), nullable=False)
    quantity = Column(Integer, nullable=False)
