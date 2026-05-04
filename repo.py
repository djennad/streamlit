"""Realtime Database access (authenticated where needed)."""

from __future__ import annotations

import uuid
from typing import Any

from firebase_client import get_db


def _token() -> str | None:
    import streamlit as st

    u = st.session_state.get("fb_user")
    return u.get("idToken") if u else None


def items_to_fb(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {str(i): x for i, x in enumerate(items)}


def items_from_fb(raw: Any) -> list[dict[str, Any]]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, dict)]
    if isinstance(raw, dict):
        keys = sorted(raw.keys(), key=lambda k: int(k) if str(k).isdigit() else 0)
        out: list[dict[str, Any]] = []
        for k in keys:
            v = raw[k]
            if isinstance(v, dict):
                out.append(v)
        return out
    return []


def fetch_user(uid: str) -> dict[str, Any] | None:
    snap = get_db().child("users").child(uid).get(token=_token())
    return snap.val()


def save_user(uid: str, data: dict[str, Any]) -> None:
    get_db().child("users").child(uid).set(data, token=_token())


def fetch_vendor(uid: str) -> dict[str, Any] | None:
    snap = get_db().child("vendors").child(uid).get(token=_token())
    return snap.val()


def save_vendor(uid: str, data: dict[str, Any]) -> None:
    get_db().child("vendors").child(uid).set(data, token=_token())


def list_products() -> list[tuple[str, dict[str, Any]]]:
    snap = get_db().child("products").get(token=_token())
    if not snap.val():
        return []
    return [(k, v) for k, v in snap.val().items() if isinstance(v, dict)]


def list_vendor_products(vendor_id: str) -> list[tuple[str, dict[str, Any]]]:
    out: list[tuple[str, dict[str, Any]]] = []
    for pid, p in list_products():
        if p.get("vendor_id") == vendor_id:
            out.append((pid, p))
    return out


def set_product(product_id: str, data: dict[str, Any]) -> None:
    get_db().child("products").child(product_id).set(data, token=_token())


def new_product_id() -> str:
    return str(uuid.uuid4())


def update_product(product_id: str, data: dict[str, Any]) -> None:
    get_db().child("products").child(product_id).update(data, token=_token())


def delete_product(product_id: str) -> None:
    get_db().child("products").child(product_id).remove(token=_token())


def set_order(order_id: str, data: dict[str, Any]) -> None:
    get_db().child("orders").child(order_id).set(data, token=_token())


def new_order_id() -> str:
    return str(uuid.uuid4())


def list_customer_orders(customer_id: str) -> list[tuple[str, dict[str, Any]]]:
    snap = get_db().child("orders").get(token=_token())
    if not snap.val():
        return []
    rows: list[tuple[str, dict[str, Any]]] = []
    for oid, o in snap.val().items():
        if isinstance(o, dict) and o.get("customer_id") == customer_id:
            rows.append((oid, o))
    rows.sort(key=lambda x: x[1].get("created_at") or "", reverse=True)
    return rows


def list_vendor_orders(vendor_id: str) -> list[tuple[str, dict[str, Any]]]:
    snap = get_db().child("orders").get(token=_token())
    if not snap.val():
        return []
    rows: list[tuple[str, dict[str, Any]]] = []
    for oid, o in snap.val().items():
        if not isinstance(o, dict):
            continue
        for it in items_from_fb(o.get("items")):
            if it.get("vendor_id") == vendor_id:
                rows.append((oid, o))
                break
    rows.sort(key=lambda x: x[1].get("created_at") or "", reverse=True)
    return rows


def update_order_status(order_id: str, status: str) -> None:
    get_db().child("orders").child(order_id).update({"status": status}, token=_token())


def get_product(product_id: str) -> dict[str, Any] | None:
    snap = get_db().child("products").child(product_id).get(token=_token())
    return snap.val() if snap.val() else None
