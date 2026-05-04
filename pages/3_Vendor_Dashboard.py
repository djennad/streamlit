from __future__ import annotations

import streamlit as st

from models import product_payload, vendor_payload
from repo import (
    delete_product,
    fetch_user,
    fetch_vendor,
    list_vendor_products,
    new_product_id,
    save_vendor,
    set_product,
    update_product,
)
from session_auth import current_uid
from ui import render_auth_sidebar

st.set_page_config(page_title="Vendor", page_icon="📦", layout="wide")
render_auth_sidebar()

uid = current_uid()
if not uid:
    st.warning("Sign in as a vendor.")
    st.stop()

profile = fetch_user(uid) or {}
if profile.get("role") != "vendor":
    st.error("This page is for **vendor** accounts.")
    st.stop()

st.title("Vendor dashboard")

vprof = fetch_vendor(uid) or {}
with st.expander("Shop profile", expanded=not vprof.get("shop_name")):
    sn = st.text_input("Shop name", value=vprof.get("shop_name") or "")
    desc = st.text_area("Description", value=vprof.get("description") or "")
    if st.button("Save profile"):
        save_vendor(uid, vendor_payload(sn or "My shop", desc or ""))
        st.success("Profile saved.")

st.subheader("Your products")
existing = list_vendor_products(uid)

with st.form("add_product"):
    st.markdown("**Add product**")
    n = st.text_input("Name")
    d = st.text_area("Description")
    price = st.number_input("Price (USD)", min_value=0.0, value=9.99, step=0.5)
    stock = st.number_input("Stock", min_value=0, value=10, step=1)
    if st.form_submit_button("Publish"):
        if not n.strip():
            st.error("Name is required.")
        else:
            pid = new_product_id()
            set_product(
                pid,
                product_payload(uid, n.strip(), d.strip(), price, stock),
            )
            st.success("Product published.")
            st.rerun()

if not existing:
    st.caption("No products yet.")
else:
    for pid, p in existing:
        with st.expander(p.get("name", pid), expanded=False):
            st.write(p.get("description") or "")
            c1, c2 = st.columns(2)
            with c1:
                np = st.number_input("Price", value=float(p.get("price") or 0), key=f"p_{pid}")
                ns = st.number_input("Stock", value=int(p.get("stock") or 0), min_value=0, key=f"s_{pid}")
                if st.button("Update", key=f"u_{pid}"):
                    update_product(pid, {"price": float(np), "stock": int(ns)})
                    st.success("Updated.")
                    st.rerun()
            with c2:
                if st.button("Delete listing", key=f"d_{pid}"):
                    delete_product(pid)
                    st.success("Deleted.")
                    st.rerun()
