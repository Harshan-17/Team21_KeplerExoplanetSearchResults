"""ASK KEPLER, a small natural-language interface for the catalog."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.ask_kepler import AskResponse, answer_query
from src.ml import load_saved_ml_results


def _label(row: pd.Series) -> str:
    kepoi = str(row.get("kepoi_name", "Unknown object"))
    kepid = row.get("kepid")
    if pd.isna(kepid):
        return kepoi
    return f"{kepoi} · Kepler ID {int(kepid)}"


def _display_message(message: dict) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        results = message.get("results")
        if isinstance(results, pd.DataFrame):
            st.dataframe(results, hide_index=True, width="stretch")


def render(data: pd.DataFrame, source_label: str) -> None:
    """Render the compact ASK KEPLER chat surface."""

    st.title("ASK KEPLER")
    st.caption("Ask in plain language. I will search the cleaned catalog or use the existing project results.")

    objects = data.sort_values("kepoi_name", na_position="last")
    candidate_indices = objects.index[objects["koi_disposition"].eq("CANDIDATE")].tolist()
    default_index = 0
    if candidate_indices:
        default_candidate = candidate_indices[0]
        try:
            saved_ids = set(load_saved_ml_results().candidate_predictions["rowid"].astype(int))
            available_candidates = [
                index
                for index in candidate_indices
                if int(float(objects.loc[index, "rowid"])) in saved_ids
            ]
            default_candidate = available_candidates[0] if available_candidates else default_candidate
        except (KeyError, OSError, TypeError, ValueError):
            pass
        default_index = objects.index.get_loc(default_candidate)
    selected_index = st.selectbox(
        "Selected object for candidate questions",
        options=objects.index.tolist(),
        index=default_index,
        format_func=lambda index: _label(objects.loc[index]),
        help="Dataset searches do not use this selection. Candidate, transit, model, and screening questions do.",
    )
    selected_row = objects.loc[selected_index]
    st.caption(
        f"Current object: {_label(selected_row)}. Try: “Tell me about this candidate.”"
    )

    if "ask_kepler_messages" not in st.session_state:
        st.session_state.ask_kepler_messages = [
            {
                "role": "assistant",
                "content": "Ask me to filter the catalog, explain the selected object, check its next transit, view model results, or check screening.",
            }
        ]

    for message in st.session_state.ask_kepler_messages:
        _display_message(message)

    prompt = st.chat_input("Ask Kepler a question")
    if prompt:
        st.session_state.ask_kepler_messages.append({"role": "user", "content": prompt})
        response: AskResponse = answer_query(prompt, data, selected_row)
        st.session_state.ask_kepler_messages.append(
            {"role": "assistant", "content": response.text, "results": response.results}
        )
        st.rerun()

    st.caption(f"Source: `{source_label}`")
