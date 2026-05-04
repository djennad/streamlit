"""Firebase Auth in Streamlit session_state + token refresh."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import streamlit as st

from firebase_client import get_auth


def refresh_if_needed() -> None:
    u = st.session_state.get("fb_user")
    if not u or "refreshToken" not in u:
        return
    try:
        nu = get_auth().refresh(u["refreshToken"])
        u["idToken"] = nu["idToken"]
        if nu.get("refreshToken"):
            u["refreshToken"] = nu["refreshToken"]
    except Exception:
        st.session_state.pop("fb_user", None)


def current_uid() -> str | None:
    u = st.session_state.get("fb_user")
    return u.get("localId") if u else None


def sign_in(email: str, password: str) -> None:
    user = get_auth().sign_in_with_email_and_password(email.strip(), password)
    st.session_state["fb_user"] = user


def sign_up(email: str, password: str) -> dict[str, Any]:
    return get_auth().create_user_with_email_and_password(email.strip(), password)


def sign_out() -> None:
    st.session_state.pop("fb_user", None)
    st.session_state.pop("cart", None)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
