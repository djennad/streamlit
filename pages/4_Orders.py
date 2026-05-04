from __future__ import annotations

import streamlit as st

from repo import fetch_user, items_from_fb, list_customer_orders, list_vendor_orders, update_order_status
from session_auth import current_uid
from ui import render_auth_sidebar

st.set_page_config(page_title="Orders", page_icon="📋", layout="wide")
render_auth_sidebar()

uid = current_uid()
if not uid:
    st.warning("Sign in to view orders.")
    st.stop()

profile = fetch_user(uid) or {}
role = profile.get("role", "customer")

st.title("Orders")

STATUSES = ["placed", "processing", "shipped", "completed", "cancelled"]


def render_order(oid: str, o: dict, as_vendor: bool) -> None:
    st.subheader(f"Order `{oid[:8]}…`")
    st.caption(f"Status: **{o.get('status', '')}** · Total **${float(o.get('total') or 0):.2f}** · {o.get('created_at', '')}")
    items = items_from_fb(o.get("items"))
    for it in items:
        if as_vendor and it.get("vendor_id") != uid:
            continue
        st.write(
            f"- {it.get('name')} × {it.get('quantity')} @ ${float(it.get('unit_price') or 0):.2f} "
            f"(seller line ${float(it.get('line_total') or 0):.2f})"
        )
    if as_vendor:
        new_s = st.selectbox(
            "Set status (your store)",
            STATUSES,
            index=STATUSES.index(o["status"]) if o.get("status") in STATUSES else 0,
            key=f"st_{oid}",
        )
        if st.button("Save status", key=f"sv_{oid}"):
            update_order_status(oid, new_s)
            st.success("Updated.")
            st.rerun()
    st.divider()


if role == "vendor":
    st.markdown("### Incoming orders (lines for your store)")
    vo = list_vendor_orders(uid)
    if not vo:
        st.info("No orders yet.")
    else:
        for oid, o in vo:
            render_order(oid, o, as_vendor=True)

st.markdown("### Your purchases")
co = list_customer_orders(uid)
if not co:
    st.caption("No purchases yet.")
else:
    for oid, o in co:
        render_order(oid, o, as_vendor=False)
