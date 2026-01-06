import math
import pandas as pd  
import streamlit as st


from frontend.client import ( 
    create_boardgame,
    delete_boardgame,
    list_boardgames,
    update_boardgame,
)

st.set_page_config(page_title="BoardGameHub Dashboard", layout="wide")
st.title("🎲 BoardGameHub Dashboard")
st.caption("Streamlit UI that talks to FastAPI via httpx")

PAGE_SIZE = 15


@st.cache_data(ttl=15)
def cached_games() -> list[dict]:
    return list_boardgames()


def normalize_name(s: str) -> str:
    return (s or "").strip().lower()


col_left, col_right = st.columns([2, 1])

# ================= LEFT: TABLE + DELETE =================
with col_left:
    st.subheader("📋 Games")

    try:
        games = cached_games()
    except RuntimeError as e:
        st.error(f"API error: {e}")
        st.stop()

    total = len(games)
    st.metric("Total games", total)

    if games:
        df = pd.DataFrame(games)

        # ---- Pagination ----
        total_pages = max(1, math.ceil(total / PAGE_SIZE))
        if "page" not in st.session_state:
            st.session_state.page = 1

        nav = st.columns([1, 2, 1])
        with nav[0]:
            if st.button("⬅ Prev", disabled=(st.session_state.page <= 1)):
                st.session_state.page -= 1
                st.rerun()

        with nav[1]:
            st.write(f"Page **{st.session_state.page}** / **{total_pages}**")

        with nav[2]:
            if st.button("Next ➡", disabled=(st.session_state.page >= total_pages)):
                st.session_state.page += 1
                st.rerun()

        start = (st.session_state.page - 1) * PAGE_SIZE
        end = start + PAGE_SIZE
        page_df = df.iloc[start:end]

        st.dataframe(page_df, use_container_width=True)

        # ---- Delete ----
        st.markdown("---")
        st.subheader("🗑️ Delete")

        selected_game = st.selectbox(
            "Select a game to delete",
            options=games,
            index=None,
            placeholder="Choose a game...",
            format_func=lambda g: f"{g.get('name', 'Unnamed')} (id={g.get('id')})",
        )

        if selected_game:
            with st.container(border=True):
                st.markdown(f"### {selected_game.get('name', '')}")

                r1 = st.columns([2, 1, 1])
                r1[0].write(f"**Designer:** {selected_game.get('designer') or '—'}")
                r1[1].write(f"**Year:** {selected_game.get('year_published', 0)}")
                r1[2].write(f"**ID:** {selected_game.get('id', '—')}")

                r2 = st.columns(4)
                r2[0].write(
                    f"**Players:** {selected_game.get('min_players', 0)}–{selected_game.get('max_players', 0)}"
                )
                r2[1].write(f"**Play time:** {selected_game.get('play_time_min', 0)} min")
                r2[2].write(f"**Complexity:** {selected_game.get('complexity', 0)}")
                r2[3].write(f"**Rating:** {selected_game.get('rating', 0)}")

            if st.button("🗑️ Delete selected"):
                try:
                    delete_boardgame(int(selected_game["id"]))
                    cached_games.clear()
                    st.success("Deleted successfully.")
                    st.rerun()
                except RuntimeError as e:
                    st.error(str(e))

    else:
        st.info("No games yet. Add one from the form →")


# ================= RIGHT: ADD + EDIT =================
with col_right:
    # ---- Add ----
    st.subheader("➕ Add game")

    with st.form("create_form"):
        name = st.text_input("Name*", value="")
        designer = st.text_input("Designer", value="")

        year_published = st.number_input("Year published", min_value=0, max_value=2100, value=0)
        min_players = st.number_input("Min players", min_value=0, max_value=20, value=0)
        max_players = st.number_input("Max players", min_value=0, max_value=20, value=0)
        play_time_min = st.number_input("Play time (min)", min_value=0, max_value=600, value=0)
        complexity = st.number_input("Complexity", min_value=0.0, max_value=5.0, value=0.0, step=0.1)
        rating = st.number_input("Rating", min_value=0.0, max_value=10.0, value=0.0, step=0.1)

        submitted = st.form_submit_button("Create")

    if submitted:
        name_clean = name.strip()

        if not name_clean:
            st.error("Name is required.")
        else:
            # Client-side duplicate check (server will enforce too)
            existing_names = {normalize_name(g.get("name")) for g in games}
            if normalize_name(name_clean) in existing_names:
                st.error("A game with this name already exists.")
            elif min_players > max_players and max_players != 0:
                st.error("Min players cannot be greater than Max players.")
            else:
                payload = {
                    "name": name_clean,
                    "designer": designer.strip() or None,
                    "year_published": int(year_published),
                    "min_players": int(min_players),
                    "max_players": int(max_players),
                    "play_time_min": int(play_time_min),
                    "complexity": float(complexity),
                    "rating": float(rating),
                }
                try:
                    created = create_boardgame(payload)
                    cached_games.clear()
                    st.success(f"Created: {created.get('name')}")
                    st.rerun()
                except RuntimeError as e:
                    st.error(str(e))

    # ---- Edit ----
    st.markdown("---")
    st.subheader("✏️ Edit game")

    game_to_edit = st.selectbox(
        "Select a game to edit",
        options=games,
        index=None,
        placeholder="Choose a game...",
        format_func=lambda g: f"{g.get('name', 'Unnamed')} (id={g.get('id')})",
    )

    if game_to_edit:
        with st.form("edit_form"):
            edit_name = st.text_input("Name*", value=game_to_edit.get("name", ""))
            edit_designer = st.text_input("Designer", value=game_to_edit.get("designer") or "")

            edit_year = st.number_input(
                "Year published",
                min_value=0,
                max_value=2100,
                value=int(game_to_edit.get("year_published", 0)),
            )
            edit_min_p = st.number_input(
                "Min players",
                min_value=0,
                max_value=20,
                value=int(game_to_edit.get("min_players", 0)),
            )
            edit_max_p = st.number_input(
                "Max players",
                min_value=0,
                max_value=20,
                value=int(game_to_edit.get("max_players", 0)),
            )
            edit_time = st.number_input(
                "Play time (min)",
                min_value=0,
                max_value=600,
                value=int(game_to_edit.get("play_time_min", 0)),
            )
            edit_complexity = st.number_input(
                "Complexity",
                min_value=0.0,
                max_value=5.0,
                value=float(game_to_edit.get("complexity", 0.0)),
                step=0.1,
            )
            edit_rating = st.number_input(
                "Rating",
                min_value=0.0,
                max_value=10.0,
                value=float(game_to_edit.get("rating", 0.0)),
                step=0.1,
            )

            updated = st.form_submit_button("Update")

        if updated:
            new_name = edit_name.strip()

            if not new_name:
                st.error("Name is required.")
            elif edit_min_p > edit_max_p and edit_max_p != 0:
                st.error("Min players cannot be greater than Max players.")
            else:
                # Prevent renaming to an existing name (belonging to another game)
                name_to_id = {
                    normalize_name(g.get("name")): g.get("id")
                    for g in games
                    if g.get("id") is not None
                }
                existing_id = name_to_id.get(normalize_name(new_name))
                if existing_id is not None and existing_id != game_to_edit["id"]:
                    st.error("Another game with this name already exists.")
                else:
                    payload = {
                        "name": new_name,
                        "designer": edit_designer.strip() or None,
                        "year_published": int(edit_year),
                        "min_players": int(edit_min_p),
                        "max_players": int(edit_max_p),
                        "play_time_min": int(edit_time),
                        "complexity": float(edit_complexity),
                        "rating": float(edit_rating),
                    }
                    try:
                        update_boardgame(int(game_to_edit["id"]), payload)
                        cached_games.clear()
                        st.success("Updated successfully.")
                        st.rerun()
                    except RuntimeError as e:
                        st.error(str(e))
