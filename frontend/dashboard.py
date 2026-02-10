import sys
import os

# Add project root to sys.path so we can import 'frontend'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import streamlit as st

from frontend.client import ( 
    create_boardgame,
    delete_boardgame,
    list_boardgames,
    update_boardgame,
    upload_csv,
    login,
    set_auth_token,
)

st.set_page_config(page_title="The Board Room", layout="wide", page_icon="🎲")
st.title("🎲 The Board Room")
st.markdown("Your curated collection of tabletop experiences.")

PAGE_SIZE = 50

# Ensure the client has the token if we are logged in
if "token" in st.session_state:
    set_auth_token(st.session_state.token)
else:
    set_auth_token(None)

# ================= SIDEBAR: AUTHENTICATION =================
with st.sidebar:
    st.header("🔐 Admin Access")
    if "token" not in st.session_state:
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                try:
                    token = login(u, p)
                    st.session_state.token = token
                    st.success("Logged in!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {e}")
    else:
        st.write(f"Logged in as **Admin**")
        if st.button("Logout"):
            del st.session_state.token
            st.rerun()

    st.markdown("---")


@st.cache_data(ttl=15)
def cached_games(page: int, page_size: int, search: str | None = None, min_players: int | None = None, max_players: int | None = None) -> dict:
    return list_boardgames(
        page=page, 
        page_size=page_size, 
        search=search, 
        min_players=min_players, 
        max_players=max_players
    )


def normalize_name(s: str) -> str:
    return (s or "").strip().lower()


# ---------- Create-form state helpers ----------
def init_create_form_state() -> None:
    defaults = {
        "create_name": "",
        "create_designer": "",
        "create_year_published": 0,
        "create_min_players": 0,
        "create_max_players": 0,
        "create_play_time_min": 0,
        "create_complexity": 0.0,
        "create_rating": 0.0,
        "reset_create_form": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def apply_create_form_reset_if_needed() -> None:
    if st.session_state.get("reset_create_form"):
        st.session_state["create_name"] = ""
        st.session_state["create_designer"] = ""
        st.session_state["create_year_published"] = 0
        st.session_state["create_min_players"] = 0
        st.session_state["create_max_players"] = 0
        st.session_state["create_play_time_min"] = 0
        st.session_state["create_complexity"] = 0.0
        st.session_state["create_rating"] = 0.0
        st.session_state["reset_create_form"] = False


# ================= LOGIC: INITIALIZE SEARCH & FILTERS =================
if "page" not in st.session_state:
    st.session_state.page = 1

# Retrieve filter values from session state (set by widgets below)
search_query = st.session_state.get("search_input", "")
filter_solo = st.session_state.get("filter_solo", False)
filter_duel = st.session_state.get("filter_duel", False)

# Map filters to API parameters
api_min_players = 1 if filter_solo else None
api_max_players = 2 if filter_duel else None

# Reset page if filters change
if "last_search" not in st.session_state or st.session_state.last_search != search_query or \
   "last_solo" not in st.session_state or st.session_state.last_solo != filter_solo or \
   "last_duel" not in st.session_state or st.session_state.last_duel != filter_duel:
    st.session_state.page = 1
    st.session_state.last_search = search_query
    st.session_state.last_solo = filter_solo
    st.session_state.last_duel = filter_duel

try:
    # Fetch data with server-side filtering
    data = cached_games(
        page=st.session_state["page"], 
        page_size=PAGE_SIZE,
        search=search_query,
        min_players=api_min_players,
        max_players=api_max_players
    )
    games = data.get("items", [])
    total = data.get("total", 0)
except RuntimeError as e:
    st.error(f"API error: {e}")
    st.stop()

if games:
    df = pd.DataFrame(games)
    
    # 1. Key Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Games", total)
    
    # Highest Rated Game Logic
    top_game = df.loc[df['rating'].idxmax()] if not df.empty else None
    if top_game is not None:
        m2.metric("🏆 Highest Rated", f"{top_game['rating']} - {top_game['name']}")
    else:
        m2.metric("🏆 Highest Rated", "—")
        
    m3.metric("Avg Complexity", f"{df['complexity'].mean():.1f}")
    m4.metric("Avg Playtime", f"{df['play_time_min'].mean():.0f} min")
    
    import altair as alt

    # 2. Visualizations
    st.caption("📈 Rating vs Complexity")
    
    chart = alt.Chart(df).mark_circle(opacity=0.9, stroke="white", strokeWidth=1).encode(
        x=alt.X("rating", scale=alt.Scale(domain=[0, 10], clamp=True), title="Rating (0-10)"),
        y=alt.Y("complexity", scale=alt.Scale(domain=[0, 5], clamp=True), title="Complexity (0-5)"),
        size=alt.Size("play_time_min", title="Playtime (min)", scale=alt.Scale(range=[100, 800]), legend=alt.Legend(orient='top', direction='horizontal')),
        color=alt.Color("max_players", title="Max Players", scale=alt.Scale(scheme="orangered"), legend=alt.Legend(orient='top', direction='horizontal')),
        tooltip=["name", "designer", "rating", "complexity", "play_time_min", "max_players"]
    ).properties(
        height=500,
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )

    st.altair_chart(chart, use_container_width=True)

st.markdown("---")

col_left, col_right = st.columns([2, 1])

# ================= LEFT: TABLE + DELETE =================
with col_left:
    st.subheader("📋 Games List")

    if games:
        # 1. Search Bar
        st.text_input("🔍 Search", placeholder="Type name, designer...", key="search_input", label_visibility="collapsed")
        
        # 2. Filters & Export Row
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            st.checkbox("👤 Solo Mode (1 Player)", key="filter_solo")
        with c2:
            st.checkbox("⚔️ 1 vs 1 (Duel)", key="filter_duel")
        
        with c3:
            st.download_button(
                "📥 Export CSV",
                df.to_csv(index=False).encode("utf-8"),
                "boardgames.csv",
                "text/csv",
                key='download-csv'
            )

        with c3:
            with st.expander("📤 Upload CSV", expanded=False):
                st.caption("Upload 'bgg_dataset.csv' format")
                uploaded_file = st.file_uploader("Choose a CSV file", type="csv", label_visibility="collapsed")
                
                if uploaded_file is not None:
                    if st.button("Start Upload", key="btn_upload"):
                        with st.spinner("Uploading games... This may take a while."):
                            try:
                                bytes_data = uploaded_file.getvalue()
                                result = upload_csv(bytes_data, uploaded_file.name)
                                st.success(result.get("message", "Upload complete"))
                                if result.get("errors"):
                                    with st.expander("Show Errors"):
                                        st.write(result["errors"])
                                cached_games.clear()
                            except Exception as e:
                                st.error(f"Upload failed: {e}")

        # Polished Data Table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=600,
            column_order=["name", "rating", "year_published", "min_players", "max_players", "complexity", "play_time_min", "designer"],
            column_config={
                "name": st.column_config.TextColumn("Game Name", width="medium"),
                "rating": st.column_config.ProgressColumn(
                    "Rating", help="Score 0-10", min_value=0, max_value=10, format="%.1f"
                ),
                "year_published": st.column_config.NumberColumn("Year", format="%d"),
                "complexity": st.column_config.NumberColumn("Complexity", format="%.1f"),
                "play_time_min": st.column_config.NumberColumn("Time", format="%d m"),
            }
        )

        # Pagination Controls
        if total > PAGE_SIZE:
            total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
            
            c_prev, c_info, c_next = st.columns([1, 2, 1])
            
            with c_prev:
                if st.button("⬅️ Previous", disabled=st.session_state.page <= 1, key="btn_prev"):
                    st.session_state.page -= 1
                    st.rerun()
            
            with c_info:
                st.markdown(f"<div style='text-align: center; padding-top: 5px;'>Page <b>{st.session_state.page}</b> of <b>{total_pages}</b></div>", unsafe_allow_html=True)
            
            with c_next:
                if st.button("Next ➡️", disabled=st.session_state.page >= total_pages, key="btn_next"):
                    st.session_state.page += 1
                    st.rerun()

        # ---- Delete ----
        st.markdown("---")
        st.subheader("🗑️ Delete Game")
        st.warning("⚠️ Warning: Deleting a game is permanent.")

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
        st.info("No games found. Add some from the right sidebar! 👉")


# ================= RIGHT: ADD + EDIT =================
with col_right:
    # ---- Add ----
    st.subheader("➕ Add game")

    # ✅ init + reset BEFORE widgets are created
    init_create_form_state()
    apply_create_form_reset_if_needed()

    with st.form("create_form"):
        name = st.text_input("Name*", key="create_name")
        designer = st.text_input("Designer", key="create_designer")

        year_published = st.number_input(
            "Year published", min_value=0, max_value=2100, key="create_year_published"
        )
        min_players = st.number_input(
            "Min players", min_value=0, max_value=20, key="create_min_players"
        )
        max_players = st.number_input(
            "Max players", min_value=0, max_value=20, key="create_max_players"
        )
        play_time_min = st.number_input(
            "Play time (min)", min_value=0, max_value=600, key="create_play_time_min"
        )
        complexity = st.number_input(
            "Complexity", min_value=0.0, max_value=5.0, step=0.1, key="create_complexity"
        )
        rating = st.number_input(
            "Rating", min_value=0.0, max_value=10.0, step=0.1, key="create_rating"
        )

        c1, c2 = st.columns(2)
        submitted = c1.form_submit_button("Create")
        cleared = c2.form_submit_button("Clear form")

    # ✅ Clear form: set a flag and rerun (reset happens BEFORE widget instantiation next run)
    if cleared:
        st.session_state["reset_create_form"] = True
        st.rerun()

    if submitted:
        name_clean = (name or "").strip()

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
                    "designer": (designer or "").strip() or None,
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

                    # ✅ Reset after success (flag + rerun)
                    st.session_state["reset_create_form"] = True

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

            c1, c2 = st.columns(2)
            with c1:
                edit_year = st.number_input(
                    "Year published", min_value=0, max_value=2100, value=int(game_to_edit.get("year_published", 0))
                )
            with c2:
                edit_time = st.number_input(
                    "Play time (min)", min_value=0, max_value=600, value=int(game_to_edit.get("play_time_min", 0))
                )

            c3, c4 = st.columns(2)
            with c3:
                edit_min_p = st.number_input(
                    "Min players", min_value=0, max_value=20, value=int(game_to_edit.get("min_players", 0))
                )
            with c4:
                edit_max_p = st.number_input(
                    "Max players", min_value=0, max_value=20, value=int(game_to_edit.get("max_players", 0))
                )

            c5, c6 = st.columns(2)
            with c5:
                edit_complexity = st.number_input(
                    "Complexity", min_value=0.0, max_value=5.0, step=0.1,
                    value=float(game_to_edit.get("complexity", 0.0))
                )
            with c6:
                edit_rating = st.number_input(
                    "Rating", min_value=0.0, max_value=10.0, step=0.1,
                    value=float(game_to_edit.get("rating", 0.0))
                )

            updated = st.form_submit_button("Update")

        if updated:
            new_name = (edit_name or "").strip()

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
                        "designer": (edit_designer or "").strip() or None,
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
