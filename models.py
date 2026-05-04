"""Typed-ish helpers for Realtime Database payloads."""

from __future__ import annotations

from typing import Any


def user_payload(email: str, role: str, display_name: str) -> dict[str, Any]:
    return {
        "email": email,
        "role": role,
        "display_name": display_name,
    }


def vendor_payload(shop_name: str, description: str) -> dict[str, Any]:
    return {"shop_name": shop_name, "description": description}


def product_payload(
    vendor_id: str,
    name: str,
    description: str,
    price: float,
    stock: int,
) -> dict[str, Any]:
    return {
        "vendor_id": vendor_id,
        "name": name,
        "description": description,
        "price": float(price),
        "stock": int(stock),
    }


def order_item_payload(
    product_id: str,
    vendor_id: str,
    name: str,
    unit_price: float,
    quantity: int,
) -> dict[str, Any]:
    return {
        "product_id": product_id,
        "vendor_id": vendor_id,
        "name": name,
        "unit_price": float(unit_price),
        "quantity": int(quantity),
        "line_total": float(unit_price) * int(quantity),
    }
