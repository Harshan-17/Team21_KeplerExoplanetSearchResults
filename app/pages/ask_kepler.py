"""Deterministic natural-language lookups over the Kepler catalog."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.data import load_screening_results
from app.modeling import get_screening_result, predict_selected, get_model_bundle
from src.ask_kepler import answer_question


def _candidate_options(data: pd.DataFrame) -> list[str]:
    return sorted(data["koi_identifier"].fillna(data["rowid"].astype(str)).astype(str).tolist())


def _selected_row(data: pd.DataFrame, selected_id: str) -> pd.Series | None:
    matches = data.loc[data["koi_identifier"].astype(str) == selected_id]
    return None if matches.empty else matches.iloc[0]


def _needs_prediction(question: str) -> bool:
    text = question.lower()
    return "model" in text or "prediction" in text or "probabilit" in text


def _render_message(message: dict) -> None:
    with st.chat_message(message["role"]):
        st.write(message["text"])
        if message.get("results") is not None:
            st.dataframe(message["results"], hide_index=True, use_container_width=True)


def render(data: pd.DataFrame, source_label: str) -> None:
    """Render the small supported ASK KEPLER query interface."""

    st.title("ASK KEPLER")
    st.caption("Ask a small set of catalog, candidate, transit, ML, and screening questions.")

    selected_id = st.selectbox("Selected object for candidate questions", _candidate_options(data))
    row = _selected_row(data, selected_id)
    screening = load_screening_results()
    screening_row = get_screening_result(row, screening) if row is not None else None

    messages = st.session_state.setdefault("ask_kepler_messages", [])
    for message in messages:
        _render_message(message)

    question = st.chat_input("Try: Show candidates with radius below 2 Earth radii.")
    if question:
        messages.append({"role": "user", "text": question})
        prediction = None
        if _needs_prediction(question) and row is not None:
            try:
                prediction = predict_selected(row, get_model_bundle(data))
            except Exception:
                prediction = None

        response = answer_question(
            question,
            data,
            selected_row=row,
            prediction=prediction,
            screening_row=screening_row,
        )
        messages.append(
            {
                "role": "assistant",
                "text": response.text,
                "results": response.results,
            }
        )
        st.rerun()

    st.caption(f"Source: `{source_label}`. Answers are deterministic lookups over the repository data and results.")
