from __future__ import annotations

import streamlit as st

from repo import fetch_vendor, list_products
from session_auth import current_uid
from ui import render_auth_sidebar

st.set_page_config(page_title="Shop", page_icon="🏪", layout="wide")
render_auth_sidebar()

uid = current_uid()
if not uid:
    st.warning("Sign in from the sidebar to browse the catalog.")
    st.stop()

st.title("Shop")

vendors_cache: dict[str, dict] = {}


def vendor_label(vid: str) -> str:
    if vid not in vendors_cache:
        v = fetch_vendor(vid)
        vendors_cache[vid] = v or {}
    shop = (vendors_cache[vid] or {}).get("shop_name") or vid[:8]
    return str(shop)


products = list_products()
if not products:
    st.info("No products yet. Ask a vendor to add listings from **Vendor dashboard**.")
else:
    for pid, p in products:
        if int(p.get("stock") or 0) <= 0:
            continue
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.subheader(p.get("name", "Product"))
                st.caption(f"Seller: **{vendor_label(str(p.get('vendor_id')))}**")
                st.write(p.get("description") or "")
                st.write(f"**${float(p.get('price') or 0):.2f}** · Stock: {int(p.get('stock') or 0)}")
            with c2:
                q = st.number_input("Qty", min_value=1, max_value=max(1, int(p.get("stock") or 1)), value=1, key=f"q_{pid}")
                if st.button("Add to cart", key=f"add_{pid}"):
                    cart = st.session_state.get("cart", {})
                    cart[pid] = int(cart.get(pid, 0)) + int(q)
                    st.session_state["cart"] = cart
                    st.success("Added to cart.")
    st.caption("Out-of-stock items are hidden.")
