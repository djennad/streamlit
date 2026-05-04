"""Shared layout: auth sidebar + cart init."""

from __future__ import annotations

import streamlit as st

from repo import fetch_user, save_user
from session_auth import current_uid, refresh_if_needed, sign_in, sign_out, sign_up, utc_now_iso
from models import user_payload, vendor_payload
from repo import fetch_vendor, save_vendor


def ensure_cart() -> None:
    if "cart" not in st.session_state:
        st.session_state["cart"] = {}


def _secrets_ok() -> bool:
    try:
        _ = st.secrets["firebase_api_key"]
        _ = st.secrets["firebase_database_url"]
        return True
    except Exception:
        return False


def render_auth_sidebar() -> None:
    if not _secrets_ok():
        st.sidebar.error(
            "Add Firebase web config to `.streamlit/secrets.toml` "
            "(copy from `.streamlit/secrets.toml.example`)."
        )
        return

    refresh_if_needed()
    ensure_cart()

    st.sidebar.title("Account")
    uid = current_uid()

    if uid:
        st.sidebar.success("Signed in")
        if st.sidebar.button("Sign out"):
            sign_out()
            st.rerun()

        try:
            profile = fetch_user(uid)
            role = (profile or {}).get("role", "customer")
            st.sidebar.caption(f"Role: **{role}**")
            if profile:
                st.sidebar.caption(profile.get("display_name") or profile.get("email", ""))
        except Exception as e:
            st.sidebar.error(f"Could not load profile: {e}")
        return

    tab_login, tab_reg = st.sidebar.tabs(["Sign in", "Register"])

    with tab_login:
        le = st.text_input("Email", key="login_email")
        lp = st.text_input("Password", type="password", key="login_pw")
        if st.button("Sign in", key="btn_login"):
            if not le or not lp:
                st.warning("Enter email and password.")
            else:
                try:
                    sign_in(le, lp)
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    with tab_reg:
        re = st.text_input("Email", key="reg_email")
        rp = st.text_input("Password", type="password", key="reg_pw")
        rp2 = st.text_input("Confirm password", type="password", key="reg_pw2")
        name = st.text_input("Display name", key="reg_name")
        role = st.radio("Account type", ["customer", "vendor"], horizontal=True, key="reg_role")
        if st.button("Create account", key="btn_reg"):
            if not re or not rp:
                st.warning("Email and password required.")
            elif rp != rp2:
                st.warning("Passwords do not match.")
            else:
                try:
                    sign_up(re, rp)
                    sign_in(re, rp)
                    u = st.session_state["fb_user"]
                    uid2 = u.get("localId")
                    if uid2:
                        save_user(uid2, user_payload(re, role, name or re.split("@")[0]))
                        if role == "vendor":
                            save_vendor(
                                uid2,
                                vendor_payload(shop_name=name or "My shop", description=""),
                            )
                    st.success("Account created. You are signed in.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
