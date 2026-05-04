"""Pyrebase initialization from Streamlit secrets."""

from __future__ import annotations

import streamlit as st


def _get_firebase_config() -> dict:
    s = st.secrets
    return {
        "apiKey": s["firebase_api_key"],
        "authDomain": s["firebase_auth_domain"],
        "databaseURL": s["firebase_database_url"],
        "storageBucket": s["firebase_storage_bucket"],
    }


@st.cache_resource
def get_firebase():
    import pyrebase

    return pyrebase.initialize_app(_get_firebase_config())


def get_auth():
    return get_firebase().auth()


def get_db():
    return get_firebase().database()


def get_storage():
    return get_firebase().storage()
