"""
app.py
======
Streamlit-based AI learning platform that converts PDF books into an interactive,
adaptive learning system.

Key Features:
- Upload PDFs and automatically extract structured sections
- Chunk and store content in a ChromaDB vector database
- Switch between multiple books with persistent state
- Explore sections with raw text and vector chunks
- Generate adaptive MCQ quizzes using LLMs
- Track user performance and learning progress
- Visual analytics dashboard for mastery insights

Workflow:
Upload → Parse → Chunk → Embed → Store → Explore → Quiz → Analytics

Tech Stack:
Streamlit (UI), ChromaDB (vector DB), LLM (MCQ generation),
Plotly (visualization), Pandas (analysis)

Purpose:
Transforms static PDFs into an intelligent, personalized,
and adaptive learning experience.
"""

import os
import json
import tempfile
import streamlit as st
import pandas as pd
import plotly.express as px

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Adaptive Learning",
    page_icon="🧠",
    layout="wide"
)

# ─────────────────────────────────────────────────────────────
# LAZY IMPORTS  (avoid crash if chroma not ready yet)
# ─────────────────────────────────────────────────────────────

@st.cache_resource
def get_storage():
    from input_processing.storage import (
        store_chunks,
        collection_stats,
        get_section,
    )
    return store_chunks, collection_stats, get_section

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

REGISTRY_FILE   = "books_registry.json"
BOOK_META_FILE  = "book_meta.json"
SECTION_MAPS_DIR = "section_maps"


def load_registry():
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_registry(registry):
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


def safe_filename(name):
    return name.replace(" ", "_").replace("/", "_").replace("\\", "_")


def load_book_sections(book_name):
    """Load section map for a specific book."""
    path = os.path.join(
        SECTION_MAPS_DIR,
        safe_filename(book_name) + ".json"
    )
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def get_active_book():
    return st.session_state.get("active_book", "")


def set_active_book(name):
    st.session_state["active_book"] = name
    with open(BOOK_META_FILE, "w", encoding="utf-8") as f:
        json.dump({"book_name": name}, f, ensure_ascii=False)


def load_active_book_on_startup():
    """On first load, restore active book from book_meta.json."""
    if "active_book" not in st.session_state:
        if os.path.exists(BOOK_META_FILE):
            with open(BOOK_META_FILE, "r", encoding="utf-8") as f:
                meta = json.load(f)
            st.session_state["active_book"] = meta.get("book_name", "")
        else:
            registry = load_registry()
            if registry:
                st.session_state["active_book"] = registry[-1]["book_name"]
            else:
                st.session_state["active_book"] = ""


load_active_book_on_startup()


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────

st.sidebar.title("🧠 AI Learning Platform")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "📤 Upload & Ingest",
        "📖 Book Status",
        "📚 Explore Sections",
        "🧠 Adaptive Quiz",
        "📊 Analytics",
    ]
)

# ── book switcher ──────────────────────────────────────────────
st.sidebar.divider()
st.sidebar.markdown("### 📚 Active Book")

registry = load_registry()

if registry:
    book_names = [b["book_name"] for b in registry]
    active_book = get_active_book()

    # default to last book if active not in list
    default_idx = (
        book_names.index(active_book)
        if active_book in book_names
        else len(book_names) - 1
    )

    selected = st.sidebar.selectbox(
        "Switch active book",
        book_names,
        index=default_idx,
        key="book_switcher"
    )

    if selected != get_active_book():
        set_active_book(selected)
        # clear quiz state when book changes
        for k in [
            "adaptive_mcqs", "adaptive_section",
            "adaptive_submitted", "adaptive_answers",
            "adaptive_session_saved", "prefill_section"
        ]:
            st.session_state.pop(k, None)
        st.rerun()

    st.sidebar.success(f"Active: **{get_active_book()}**")

else:
    st.sidebar.info("No books uploaded yet.")


# ═════════════════════════════════════════════════════════════
# PAGE 1 — UPLOAD & INGEST
# ═════════════════════════════════════════════════════════════

if page == "📤 Upload & Ingest":

    st.title("📤 Upload & Ingest PDF")

    # show existing books
    if registry:
        st.subheader("📚 Already Ingested Books")
        cols = st.columns(min(len(registry), 4))
        for i, book in enumerate(registry):
            cols[i % 4].metric(
                label=f"📘 Book {i+1}",
                value=book["book_name"][:25],
                delta=f"{book['sections']} sections"
            )
        st.divider()

    uploaded = st.file_uploader(
        "Upload a new PDF book",
        type=["pdf"]
    )

    if uploaded:
        st.success(f"✅ File ready: **{uploaded.name}**")

        # warn if already ingested
        existing_names = [b["book_name"] for b in registry]
        if uploaded.name in existing_names:
            st.warning(
                f"⚠️ **{uploaded.name}** is already ingested. "
                "Processing again will overwrite its chunks."
            )

        if st.button("🚀 Process PDF", type="primary"):

            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".pdf"
            ) as tmp:
                tmp.write(uploaded.read())
                pdf_path = tmp.name

            # save book name immediately
            set_active_book(uploaded.name)

            # ── STEP 1: Parse ──────────────────────────────────
            st.subheader("Step 1 — Parsing PDF")
            with st.spinner("Extracting sections..."):
                from input_processing.parser import extract_sections
                sections = extract_sections(pdf_path)

            if not sections:
                st.error("No sections extracted. Check your PDF.")
                st.stop()

            st.success(f"✅ {len(sections)} sections extracted")

            # ── STEP 2: Chunk ──────────────────────────────────
            st.subheader("Step 2 — Chunking")
            with st.spinner("Chunking sections..."):
                from input_processing.chunker import chunk_sections
                chunks = chunk_sections(sections)

            if not chunks:
                st.error("No chunks produced.")
                st.stop()

            st.success(f"✅ {len(chunks)} chunks created")

            # ── STEP 3: Embed + Store ──────────────────────────
            st.subheader("Step 3 — Embedding + Storage")
            with st.spinner("Embedding and storing in ChromaDB..."):
                store_chunks, collection_stats, get_section = get_storage()
                store_chunks(chunks)

            stats = collection_stats()
            st.success("✅ Stored successfully!")

            col1, col2, col3 = st.columns(3)
            col1.metric("Sections", len(sections))
            col2.metric("Chunks", stats["total_chunks"])
            col3.metric("Model", stats["embed_model"].split("/")[-1])

            # ── save per-book section map ──────────────────────
            os.makedirs(SECTION_MAPS_DIR, exist_ok=True)
            per_book_map = [
                {
                    "section_id":  s["section_id"],
                    "title":       s["section_title"],
                    "level":       s["level"],
                    "page_start":  s["page_start"],
                    "page_end":    s["page_end"],
                    "raw_text":    s.get("raw_text", ""),
                    "book_name":   uploaded.name,
                }
                for s in sections
            ]
            map_path = os.path.join(
                SECTION_MAPS_DIR,
                safe_filename(uploaded.name) + ".json"
            )
            with open(map_path, "w", encoding="utf-8") as f:
                json.dump(per_book_map, f, indent=2, ensure_ascii=False)

            # ── update global section_map_full.json ───────────
            with open("section_map_full.json", "w", encoding="utf-8") as f:
                json.dump(per_book_map, f, indent=2, ensure_ascii=False)

            # ── update registry ────────────────────────────────
            reg = load_registry()
            existing = [b["book_name"] for b in reg]
            if uploaded.name in existing:
                for b in reg:
                    if b["book_name"] == uploaded.name:
                        b["sections"] = len(sections)
            else:
                reg.append({
                    "book_name": uploaded.name,
                    "sections":  len(sections),
                })
            save_registry(reg)

            # save to session
            st.session_state["sections"] = sections

            st.info(
                "✅ Done! Use the sidebar to switch books, "
                "or go to **📖 Book Status** to explore."
            )


# ═════════════════════════════════════════════════════════════
# PAGE 2 — BOOK STATUS
# ═════════════════════════════════════════════════════════════

elif page == "📖 Book Status":

    st.title("📖 Book Status")

    active_book = get_active_book()

    if not active_book:
        st.warning("No active book. Please upload a PDF first.")
        st.stop()

    # load sections for active book
    section_map = load_book_sections(active_book)

    if not section_map:
        st.warning(
            f"No section data found for **{active_book}**. "
            "Please re-ingest this book."
        )
        st.stop()

    # get chroma stats
    try:
        _, collection_stats, get_section = get_storage()
        stats = collection_stats()
    except Exception as e:
        st.error(f"Could not load ChromaDB stats: {e}")
        st.stop()

    # ── header card ────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #1e3a5f 0%, #2e6da4 100%);
            border-radius: 14px;
            padding: 32px;
            margin-bottom: 24px;
            color: white;
        ">
            <div style="font-size:12px; opacity:0.7; letter-spacing:2px;
                        text-transform:uppercase; margin-bottom:8px;">
                Active Book
            </div>
            <div style="font-size:28px; font-weight:700; margin-bottom:6px;">
                📘 {active_book}
            </div>
            <div style="font-size:13px; opacity:0.6;">
                ChromaDB · Cosine Similarity · Persistent Store
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ── metrics ────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📄 Sections",       len(section_map))
    c2.metric("🧩 Total Chunks",   stats["total_chunks"])
    c3.metric("🤖 Embed Model",    stats["embed_model"].split("/")[-1])
    c4.metric("🗄️ Collection",     stats["collection"])

    # ── storage details ────────────────────────────────────────
    with st.expander("🗂️ Storage Details"):
        st.write(f"**Storage Path:** `{stats['storage_path']}`")
        st.write(f"**Collection:** `{stats['collection']}`")
        st.write(f"**Full Model Name:** `{stats['embed_model']}`")

    # ── all ingested books ─────────────────────────────────────
    st.divider()
    st.subheader("📚 All Ingested Books")
    reg = load_registry()
    if reg:
        df_books = pd.DataFrame(reg)
        df_books.columns = ["Book Name", "Sections"]
        st.dataframe(df_books, use_container_width=True)

    # ── section explorer ───────────────────────────────────────
    st.divider()
    st.subheader(f"📑 Sections in  '{active_book}'")

    search = st.text_input("🔍 Search sections...", key="status_search")
    filtered = [
        s for s in section_map
        if search.lower() in s["title"].lower()
    ] if search else section_map

    st.caption(f"Showing {len(filtered)} of {len(section_map)} sections")

    for sec in filtered:
        with st.expander(f"§{sec['section_id']} — {sec['title']}"):

            cc1, cc2, cc3 = st.columns(3)
            cc1.metric("Section ID", sec["section_id"])
            cc2.metric("Level",      sec.get("level", "—"))
            cc3.metric("Pages",      f"{sec.get('page_start','?')}–{sec.get('page_end','?')}")

            st.divider()

            if sec.get("raw_text"):
                st.markdown("**📝 Raw Text Preview**")
                st.write(sec["raw_text"][:2000])
                if len(sec["raw_text"]) > 2000:
                    st.caption("… truncated to 2000 chars")
                st.divider()

            chunks = get_section(sec["section_id"])
            if chunks:
                st.markdown(f"**🧩 {len(chunks)} Chunk(s) in Vector Store**")
                for ch in chunks:
                    st.markdown(f"**Chunk {ch['chunk_index']}** "
                                f"· `{ch['chunk_id']}`")
                    st.write(ch["text"])
                    st.divider()
            else:
                st.info("No chunks found for this section.")


# ═════════════════════════════════════════════════════════════
# PAGE 3 — EXPLORE SECTIONS
# ═════════════════════════════════════════════════════════════

elif page == "📚 Explore Sections":

    st.title("📚 Explore Sections")

    active_book = get_active_book()

    if not active_book:
        st.warning("No active book selected. Please upload a PDF first.")
        st.stop()

    section_map = load_book_sections(active_book)

    if not section_map:
        st.warning(
            f"No sections found for **{active_book}**. "
            "Please re-ingest this book."
        )
        st.stop()

    _, _, get_section = get_storage()

    st.info(f"📘 Showing sections for: **{active_book}**")

    search = st.text_input("🔍 Search sections by title...", key="explore_search")
    filtered = [
        s for s in section_map
        if search.lower() in s["title"].lower()
    ] if search else section_map

    st.caption(f"Showing {len(filtered)} of {len(section_map)} sections")

    for sec in filtered:
        with st.expander(f"§{sec['section_id']} — {sec['title']}"):

            c1, c2, c3 = st.columns(3)
            c1.metric("Section ID", sec["section_id"])
            c2.metric("Level",      sec.get("level", "—"))
            c3.metric("Pages",      f"{sec.get('page_start','?')}–{sec.get('page_end','?')}")

            st.divider()

            if sec.get("raw_text"):
                st.markdown("**📝 Raw Text Preview**")
                st.write(sec["raw_text"][:2000])
                if len(sec["raw_text"]) > 2000:
                    st.caption("… truncated")
                st.divider()

            chunks = get_section(sec["section_id"])
            if chunks:
                st.markdown(f"**🧩 {len(chunks)} Chunk(s)**")
                for ch in chunks:
                    st.markdown(f"**Chunk {ch['chunk_index']}** · `{ch['chunk_id']}`")
                    st.write(ch["text"])
                    st.divider()
            else:
                st.info("No chunks found in vector store.")


# ═════════════════════════════════════════════════════════════
# PAGE 4 — ADAPTIVE QUIZ
# ═════════════════════════════════════════════════════════════

elif page == "🧠 Adaptive Quiz":

    st.title("🧠 Adaptive Quiz")

    active_book = get_active_book()

    if not active_book:
        st.warning("No active book. Please upload a PDF first.")
        st.stop()

    section_map = load_book_sections(active_book)

    if not section_map:
        st.warning(
            f"No sections found for **{active_book}**. "
            "Please re-ingest this book."
        )
        st.stop()

    _, _, get_section = get_storage()

    st.info(f"📘 Active Book: **{active_book}**")

    # ── section selector ───────────────────────────────────────
    section_options = {
        s["section_id"]: f"§{s['section_id']} — {s['title']}"
        for s in section_map
    }

    prefill = st.session_state.get("prefill_section", "")
    ids     = list(section_options.keys())
    default_idx = ids.index(prefill) if prefill in ids else 0

    selected_label = st.selectbox(
        "Select Section",
        options=list(section_options.values()),
        index=default_idx,
        key="section_selector"
    )

    # reverse-lookup section_id
    section_id = next(
        k for k, v in section_options.items()
        if v == selected_label
    )

    n_questions = st.slider("Number of Questions", 1, 20, 5)

    # ── show learning profile ──────────────────────────────────
    from adaptivity_processing.knowledge_base import get_weakness_profile

    profile = get_weakness_profile(section_id)

    with st.expander("🧠 Your Learning Profile for this Section"):
        if profile["is_first_time"]:
            st.info("First attempt — balanced questions will be generated.")
        else:
            pc1, pc2, pc3 = st.columns(3)
            pc1.metric("Mastery",   f"{profile['mastery_score']*100:.1f}%")
            pc2.metric("Weakness",  f"{profile['weakness_score']*100:.1f}%")
            pc3.metric("Seen Qs",   len(profile["questions_seen"]))

    # ── generate quiz ──────────────────────────────────────────
    if st.button("🚀 Generate Adaptive Quiz", type="primary"):
        chunks = get_section(section_id)
        if not chunks:
            st.error("No content found for this section.")
        else:
            text = "\n\n".join(c["text"] for c in chunks)
            with st.spinner("Generating adaptive MCQs via Groq LLM..."):
                from adaptivity_processing.adaptive_quiz import (
                    generate_adaptive_mcqs
                )
                mcqs = generate_adaptive_mcqs(
                    section_id=section_id,
                    text=text,
                    n_questions=n_questions
                )

            if not mcqs:
                st.error("Failed to generate MCQs. Try again.")
            else:
                st.session_state["adaptive_mcqs"]      = mcqs
                st.session_state["adaptive_section"]   = section_id
                st.session_state["adaptive_book"]      = active_book
                st.session_state.pop("adaptive_submitted",    None)
                st.session_state.pop("adaptive_answers",      None)
                st.session_state.pop("adaptive_session_saved",None)

    # ── render quiz ────────────────────────────────────────────
    if "adaptive_mcqs" in st.session_state:

        mcqs = st.session_state["adaptive_mcqs"]

        st.divider()
        st.subheader("📘 Quiz")

        answers = {}

        for idx, mcq in enumerate(mcqs):

            st.markdown(f"### Q{idx+1}. {mcq['question']}")

            option_map = mcq["options"]

            # freeze radio after submit
            disabled = st.session_state.get("adaptive_submitted", False)

            selected = st.radio(
                "Choose your answer",
                options=list(option_map.keys()),
                format_func=lambda x, om=option_map: f"{x}.  {om[x]}",
                key=f"q_{idx}",
                disabled=disabled,
                index=list(option_map.keys()).index(
                    st.session_state
                    .get("adaptive_answers", {})
                    .get(idx, list(option_map.keys())[0])
                ) if disabled else 0
            )

            answers[idx] = selected

            # ── inline result (visible after submit) ──────────
            if st.session_state.get("adaptive_submitted"):
                saved = st.session_state["adaptive_answers"]
                user_ans    = saved[idx]
                correct_ans = mcq["correct_answer"]
                correct_txt = option_map[correct_ans]
                user_txt    = option_map[user_ans]

                st.write(f"**Your Answer:** {user_ans}. {user_txt}")

                if user_ans == correct_ans:
                    st.success("✅ Correct")
                else:
                    st.error(
                        f"❌ Wrong — Correct answer: "
                        f"**{correct_ans}. {correct_txt}**"
                    )
                    st.info(f"💡 {mcq['explanation']}")

            st.divider()

        # ── submit button ──────────────────────────────────────
        if not st.session_state.get("adaptive_submitted"):
            if st.button("✅ Submit Quiz", type="primary"):
                st.session_state["adaptive_submitted"] = True
                st.session_state["adaptive_answers"]   = dict(answers)
                st.rerun()

        # ── score + new quiz (after submit) ───────────────────
        else:
            saved  = st.session_state["adaptive_answers"]
            score  = sum(
                1 for i, m in enumerate(mcqs)
                if saved[i] == m["correct_answer"]
            )
            total  = len(mcqs)
            pct    = (score / total) * 100

            st.subheader("📊 Final Score")
            sc1, sc2 = st.columns(2)
            sc1.metric("Score",      f"{score} / {total}")
            sc2.metric("Percentage", f"{pct:.1f}%")

            # save session once
            if not st.session_state.get("adaptive_session_saved"):
                from adaptivity_processing.session_manager import record_session

                results = [
                    {
                        "question": m["question"],
                        "correct":  saved[i] == m["correct_answer"]
                    }
                    for i, m in enumerate(mcqs)
                ]
                record_session(
                    section_id=st.session_state["adaptive_section"],
                    results=results,
                    book_name=st.session_state.get("adaptive_book", "")
                )
                st.session_state["adaptive_session_saved"] = True
                st.success("✅ Session saved to learning profile!")

            # new quiz button
            if st.button("🔄 New Adaptive Quiz"):
                prev_section = st.session_state.get("adaptive_section", "")
                for k in [
                    "adaptive_mcqs", "adaptive_submitted",
                    "adaptive_answers", "adaptive_session_saved"
                ]:
                    st.session_state.pop(k, None)
                st.session_state["prefill_section"] = prev_section
                st.rerun()


# ═════════════════════════════════════════════════════════════
# PAGE 5 — ANALYTICS
# ═════════════════════════════════════════════════════════════

elif page == "📊 Analytics":

    st.title("📊 Learning Analytics")

    from adaptivity_processing.knowledge_base import load_mastery

    mastery = load_mastery()

    if not mastery:
        st.warning("No analytics data yet. Complete a quiz first.")
        st.stop()

    # ── build dataframe ────────────────────────────────────────
    rows = []
    for sec, data in mastery.items():
        total    = data["correct"] + data["wrong"]
        accuracy = (data["correct"] / total) * 100 if total else 0
        rows.append({
            "Book":         data.get("book_name", "Unknown"),
            "Section":      sec,
            "Correct":      data["correct"],
            "Wrong":        data["wrong"],
            "Total":        total,
            "Accuracy (%)": round(accuracy, 1),
        })

    df = pd.DataFrame(rows)


    # ── filter by book ─────────────────────────────────────────
    books = ["All"] + sorted(df["Book"].unique().tolist())
    selected_book = st.selectbox("Filter by Book", books)

    if selected_book != "All":
        df = df[df["Book"] == selected_book]

    st.dataframe(df, use_container_width=True)

    # ── accuracy chart ─────────────────────────────────────────
    fig = px.bar(
        df,
        x="Section",
        y="Accuracy (%)",
        color="Book",
        title="Accuracy by Section",
        text="Accuracy (%)",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode="hide")
    st.plotly_chart(fig, use_container_width=True)

    # ── correct vs wrong chart ─────────────────────────────────
    fig2 = px.bar(
        df,
        x="Section",
        y=["Correct", "Wrong"],
        title="Correct vs Wrong by Section",
        barmode="group",
        color_discrete_map={"Correct": "#2ecc71", "Wrong": "#e74c3c"}
    )
    st.plotly_chart(fig2, use_container_width=True)