from __future__ import annotations

import streamlit as st

from checkout import place_order
from repo import fetch_user, list_products
from session_auth import current_uid
from ui import ensure_cart, render_auth_sidebar

st.set_page_config(page_title="Cart", page_icon="🛒", layout="wide")
render_auth_sidebar()
ensure_cart()

uid = current_uid()
if not uid:
    st.warning("Sign in to view your cart.")
    st.stop()

profile = fetch_user(uid) or {}
role = profile.get("role", "customer")
if role != "customer":
    st.info("Checkout is for **customer** accounts. Switch account or register as customer.")
    st.stop()

st.title("Cart & checkout")

pmap = {pid: p for pid, p in list_products()}
cart: dict[str, int] = st.session_state.get("cart", {})

if not cart:
    st.info("Your cart is empty. Visit **Shop**.")
else:
    rows = []
    subtotal = 0.0
    for pid, qty in list(cart.items()):
        p = pmap.get(pid)
        if not p:
            continue
        unit = float(p.get("price") or 0)
        line = unit * qty
        subtotal += line
        rows.append((p.get("name", pid), qty, unit, line, pid))

    for name, qty, unit, line, pid in rows:
        c1, c2, c3 = st.columns([4, 1, 1])
        with c1:
            st.write(f"**{name}**")
        with c2:
            st.write(f"{qty} × ${unit:.2f}")
        with c3:
            if st.button("Remove", key=f"rm_{pid}"):
                del st.session_state["cart"][pid]
                st.rerun()
        st.caption(f"Line: ${line:.2f}")
        st.divider()

    st.subheader(f"Estimated total: **${subtotal:.2f}**")

    if st.button("Place order", type="primary"):
        ok, msg = place_order(uid, dict(cart))
        if ok:
            st.success(f"Order placed. Order id: `{msg}`")
        else:
            st.error(msg)
