#  Importing necessary modules from FastAPI, SQLAlchemy, Starlette, and other packages
from fastapi import Depends, HTTPException, status, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request  # Handling HTTP requests
from fastapi.security import OAuth2PasswordRequestForm  # OAuth2 form for login
from datetime import datetime, timedelta, timezone  # Handling date and time operations
from email_validator import validate_email, EmailNotValidError  # Validating email addresses
from sqlalchemy.future import select

# Importing CRUD operations, templates, database utilities, authentication methods, and utility functions
import crud.users as crud
from db.database import get_db
from core.auth import create_access_token, get_current_user, get_password_hash, verify_token
from utlis.utils import generate_reset_token, send_email
from db.models.user import User  # User model
from schemas.users import UserResponse, Token, TokenResponse, UserUpdate # Pydantic models for user response and token

# Defining an API router for managing user routes
from fastapi import APIRouter
router = APIRouter()


## get users active cart
@router.get("/cart", response_model=Order)
async def get_cart(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = await db.execute(
        select(Order).filter(
            Order.user_id == current_user.user_id,
            Order.status == OrderStatus.CART
        )
    )
    cart = cart.scalars().first()
    if not cart:
        cart = Order(user_id=current_user.user_id, status=OrderStatus.CART)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
    return cart

# Add or update an item in the user's cart.
@router.post("/cart/items")
async def add_item_to_cart(
    product_id: UUID,
    quantity: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch active cart or create one
    cart = await db.execute(
        select(Order).filter(
            Order.user_id == current_user.user_id,
            Order.status == OrderStatus.CART
        )
    )
    cart = cart.scalars().first()
    if not cart:
        cart = Order(user_id=current_user.user_id, status=OrderStatus.CART)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)

    # Check if item already exists
    order_item = await db.execute(
        select(OrderItem).filter(
            OrderItem.order_id == cart.order_id,
            OrderItem.product_id == product_id
        )
    )
    order_item = order_item.scalars().first()

    if order_item:
        # Update quantity if item exists
        order_item.quantity += quantity
    else:
        # Add new item
        product = await db.execute(select(Product).filter(Product.product_id == product_id))
        product = product.scalars().first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        order_item = OrderItem(order_id=cart.order_id, product_id=product_id, quantity=quantity, price=product.price)
        db.add(order_item)

    # Recalculate total amount
    cart.total_amount = sum(item.quantity * item.price for item in cart.order_items)
    await db.commit()
    await db.refresh(cart)

    return cart


# Convert the cart into a finalized order
@router.post("/cart/checkout")
async def checkout(
    shipping_address: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch active cart
    cart = await db.execute(
        select(Order).filter(
            Order.user_id == current_user.user_id,
            Order.status == OrderStatus.CART
        )
    )
    cart = cart.scalars().first()
    if not cart or not cart.order_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Update cart to a finalized order
    cart.status = OrderStatus.PENDING
    cart.shipping_address = shipping_address
    await db.commit()

    return {"message": "Order placed successfully", "order_id": cart.order_id}

# Add Product to Wishlist
@router.post("/wishlist/add")
async def add_to_wishlist(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get the user's wishlist
    wishlist = await db.execute(
        select(Wishlist).filter(Wishlist.user_id == current_user.user_id)
    )
    wishlist = wishlist.scalars().first()

    # If wishlist does not exist, create one
    if not wishlist:
        wishlist = Wishlist(user_id=current_user.user_id)
        db.add(wishlist)
        await db.commit()
        await db.refresh(wishlist)

    # Check if the product is already in the wishlist
    product = await db.execute(
        select(Product).filter(Product.product_id == product_id)
    )
    product = product.scalars().first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product in wishlist.products:
        raise HTTPException(status_code=400, detail="Product is already in the wishlist")

    # Add product to wishlist
    wishlist.products.append(product)
    await db.commit()
    await db.refresh(wishlist)

    return {"message": "Product added to wishlist", "wishlist_id": wishlist.wishlist_id}


# Remove Product from Wishlist
@router.delete("/wishlist/remove")
async def remove_from_wishlist(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get the user's wishlist
    wishlist = await db.execute(
        select(Wishlist).filter(Wishlist.user_id == current_user.user_id)
    )
    wishlist = wishlist.scalars().first()

    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    # Check if the product exists in the wishlist
    product = await db.execute(
        select(Product).filter(Product.product_id == product_id)
    )
    product = product.scalars().first()

    if not product or product not in wishlist.products:
        raise HTTPException(status_code=404, detail="Product not found in wishlist")

    # Remove product from wishlist
    wishlist.products.remove(product)
    await db.commit()
    await db.refresh(wishlist)

    return {"message": "Product removed from wishlist"}


# Move Product from Wishlist to Cart
@router.post("/wishlist/move-to-cart")
async def move_to_cart(
    product_id: UUID,
    quantity: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get the user's wishlist
    wishlist = await db.execute(
        select(Wishlist).filter(Wishlist.user_id == current_user.user_id)
    )
    wishlist = wishlist.scalars().first()

    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    # Check if the product exists in the wishlist
    product = await db.execute(
        select(Product).filter(Product.product_id == product_id)
    )
    product = product.scalars().first()

    if not product or product not in wishlist.products:
        raise HTTPException(status_code=404, detail="Product not found in wishlist")

    # Get or create the user's active cart
    cart = await db.execute(
        select(Order).filter(
            Order.user_id == current_user.user_id,
            Order.status == OrderStatus.CART
        )
    )
    cart = cart.scalars().first()

    if not cart:
        cart = Order(user_id=current_user.user_id, status=OrderStatus.CART)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)

    # Add product to cart
    order_item = await db.execute(
        select(OrderItem).filter(
            OrderItem.order_id == cart.order_id,
            OrderItem.product_id == product_id
        )
    )
    order_item = order_item.scalars().first()

    if order_item:
        order_item.quantity += quantity
    else:
        order_item = OrderItem(order_id=cart.order_id, product_id=product_id, quantity=quantity, price=product.price)
        db.add(order_item)

    # Remove product from wishlist
    wishlist.products.remove(product)
    await db.commit()
    await db.refresh(cart)

    return {"message": "Product moved to cart", "cart_id": cart.order_id}

