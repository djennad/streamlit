"""Multi-vendor marketplace — Streamlit + Pyrebase (Firebase Auth + Realtime DB)."""

from __future__ import annotations

import streamlit as st

from ui import render_auth_sidebar

st.set_page_config(page_title="Marketplace", page_icon="🛒", layout="wide")

render_auth_sidebar()

st.title("Multi-vendor marketplace")
st.markdown(
    "Browse **Shop**, manage **Vendor dashboard** (vendor accounts), and track **Orders**. "
    "Configure Firebase in `.streamlit/secrets.toml` (see `.streamlit/secrets.toml.example`)."
)

st.divider()
st.subheader("Pages")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.page_link("pages/1_Shop.py", label="Shop", icon="🏪")
with c2:
    st.page_link("pages/2_Cart_Checkout.py", label="Cart & checkout", icon="🛒")
with c3:
    st.page_link("pages/3_Vendor_Dashboard.py", label="Vendor dashboard", icon="📦")
with c4:
    st.page_link("pages/4_Orders.py", label="Orders", icon="📋")
