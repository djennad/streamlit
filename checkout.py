"""Place orders and adjust stock (MVP, not transactional)."""

from __future__ import annotations

from typing import Any

import streamlit as st

from models import order_item_payload
from repo import (
    get_product,
    items_to_fb,
    list_products,
    new_order_id,
    set_order,
    update_product,
)
from session_auth import utc_now_iso


def _product_map() -> dict[str, dict[str, Any]]:
    return {pid: p for pid, p in list_products()}


def place_order(customer_id: str, cart: dict[str, int]) -> tuple[bool, str]:
    if not cart:
        return False, "Cart is empty."

    pmap = _product_map()
    lines: list[dict[str, Any]] = []
    total = 0.0

    for pid, qty in cart.items():
        if qty <= 0:
            continue
        p = pmap.get(pid) or get_product(pid)
        if not p:
            return False, f"Product no longer available: {pid}"
        stock = int(p.get("stock") or 0)
        if stock < qty:
            return False, f"Not enough stock for “{p.get('name', pid)}” (have {stock}, need {qty})."
        unit = float(p.get("price") or 0)
        lines.append(
            order_item_payload(
                product_id=pid,
                vendor_id=str(p.get("vendor_id")),
                name=str(p.get("name") or "Item"),
                unit_price=unit,
                quantity=qty,
            )
        )
        total += unit * qty

    if not lines:
        return False, "Nothing to order."

    oid = new_order_id()
    order = {
        "customer_id": customer_id,
        "status": "placed",
        "created_at": utc_now_iso(),
        "total": round(total, 2),
        "items": items_to_fb(lines),
    }
    set_order(oid, order)

    for line in lines:
        pid = line["product_id"]
        p = pmap.get(pid) or get_product(pid)
        if not p:
            continue
        new_stock = int(p.get("stock") or 0) - int(line["quantity"])
        update_product(pid, {"stock": max(0, new_stock)})

    st.session_state["cart"] = {}
    return True, oid
