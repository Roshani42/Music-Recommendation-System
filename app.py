import pickle
import os
import requests
import streamlit as st

st.set_page_config(page_title="Melodia", page_icon="🎧", layout="wide")

# ── Inject custom CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0d0d1a 0%, #1a0a2e 30%, #0d1a2e 60%, #0a1a1a 100%);
    min-height: 100vh;
}

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Hero title */
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 4rem;
    font-weight: 900;
    background: linear-gradient(90deg, #ff6ec7, #a78bfa, #38bdf8, #34d399);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientShift 4s ease infinite;
    margin: 0;
    line-height: 1.1;
}

.hero-sub {
    color: #94a3b8;
    font-size: 1.1rem;
    font-weight: 300;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Selectbox */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(167,139,250,0.4) !important;
    border-radius: 16px !important;
    color: white !important;
    font-family: 'DM Sans', sans-serif !important;
    backdrop-filter: blur(10px);
}

.stSelectbox label {
    color: #a78bfa !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #db2777, #0891b2) !important;
    background-size: 200% 200% !important;
    animation: gradientShift 3s ease infinite !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.75rem 3rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.08em !important;
    cursor: pointer !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
    box-shadow: 0 0 30px rgba(124,58,237,0.5) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) scale(1.03) !important;
    box-shadow: 0 0 50px rgba(219,39,119,0.6) !important;
}

/* Song cards */
.song-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 1.2rem;
    text-align: center;
    backdrop-filter: blur(20px);
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    position: relative;
    overflow: hidden;
}

.song-card::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(167,139,250,0.08), rgba(56,189,248,0.05));
    opacity: 0;
    transition: opacity 0.3s;
}

.song-card:hover::before { opacity: 1; }

.song-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 60px rgba(124,58,237,0.3);
    border-color: rgba(167,139,250,0.4);
}

.song-card img {
    border-radius: 14px;
    width: 100%;
    aspect-ratio: 1;
    object-fit: cover;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}

.song-title {
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.95rem;
    color: #f1f5f9;
    margin-top: 0.9rem;
    margin-bottom: 0.2rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.song-artist {
    font-size: 0.78rem;
    color: #64748b;
    letter-spacing: 0.05em;
    margin-bottom: 0.8rem;
}

.music-link {
    display: inline-block;
    background: linear-gradient(135deg, #7c3aed55, #db277755);
    border: 1px solid rgba(167,139,250,0.3);
    color: #c4b5fd !important;
    text-decoration: none !important;
    border-radius: 50px;
    padding: 0.3rem 1rem;
    font-size: 0.78rem;
    letter-spacing: 0.05em;
    transition: all 0.2s;
}

.music-link:hover {
    background: linear-gradient(135deg, #7c3aed, #db2777);
    color: white !important;
    box-shadow: 0 0 20px rgba(124,58,237,0.5);
}

/* divider */
.fancy-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #7c3aed55, #db277755, transparent);
    margin: 2rem 0;
}

/* Audio player */
audio {
    width: 100%;
    height: 32px;
    margin-top: 0.5rem;
    border-radius: 20px;
    filter: hue-rotate(260deg) saturate(1.5);
}

/* Spinner */
.stSpinner > div { border-top-color: #a78bfa !important; }

/* Noise overlay */
.noise {
    position: fixed;
    inset: 0;
    pointer-events: none;
    opacity: 0.03;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
    z-index: 9999;
}
</style>
<div class="noise"></div>
""", unsafe_allow_html=True)


# ── Data ─────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
music      = pickle.load(open(os.path.join(BASE_DIR, "df"),     "rb"))
similarity = pickle.load(open(os.path.join(BASE_DIR, "similar"), "rb"))


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_song_info(song_name, artist_name):
    try:
        r = requests.get(
            "https://itunes.apple.com/search",
            params={"term": f"{song_name} {artist_name}", "media": "music", "limit": 1},
            timeout=5
        )
        data = r.json()
        if data["resultCount"] > 0:
            res = data["results"][0]
            cover   = res.get("artworkUrl100", "").replace("100x100bb", "400x400bb")
            preview = res.get("previewUrl")
            url     = res.get("trackViewUrl")
            return cover, url, preview
    except Exception:
        pass
    return None, None, None


def recommend(song):
    matches = music[music['song'] == song]
    if matches.empty:
        return []
    pos       = music.index.get_loc(matches.index[0])
    distances = sorted(enumerate(similarity[pos]), reverse=True, key=lambda x: x[1])
    results   = []
    for i in distances[1:6]:
        row             = music.iloc[i[0]]
        cover, url, pre = get_song_info(row.song, row.artist)
        results.append({
            "song":    row.song,
            "artist":  row.artist,
            "cover":   cover or "https://i.postimg.cc/0QNxYz4V/social.png",
            "url":     url,
            "preview": pre,
        })
    return results


# ── Layout ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 3rem 0 2rem;">
  <div class="hero-title">melodia</div>
  <div class="hero-sub">✦ discover your next obsession ✦</div>
</div>
""", unsafe_allow_html=True)

col_l, col_c, col_r = st.columns([1, 3, 1])
with col_c:
    # Filter inappropriate songs
    bad_words = ['fuck', 'shit', 'ass', 'bitch', 'damn']
    pattern = '|'.join(bad_words)
    clean_songs = music[~music['song'].str.contains(pattern, case=False, na=False)]['song'].values

    selected_song = st.selectbox("🎵 Choose a song", clean_songs)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    btn_col = st.columns([1,2,1])
    with btn_col[1]:
        go = st.button("✨ Find My Vibe", use_container_width=True)

st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

if go:
    with st.spinner("✦ Tuning into your frequency..."):
        recs = recommend(selected_song)

    if recs:
        st.markdown("""
        <div style="text-align:center; margin-bottom:1.5rem;">
          <span style="color:#a78bfa; font-size:0.8rem; letter-spacing:0.2em; text-transform:uppercase;">
            ✦ recommended for you ✦
          </span>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(5)
        for col, rec in zip(cols, recs):
            with col:
                link_html = f'<a class="music-link" href="{rec["url"]}" target="_blank">🎵 Apple Music</a>' if rec["url"] else ""
                st.markdown(f"""
                <div class="song-card">
                  <img src="{rec['cover']}" alt="{rec['song']}"/>
                  <div class="song-title">{rec['song']}</div>
                  <div class="song-artist">{rec['artist']}</div>
                  {link_html}
                </div>
                """, unsafe_allow_html=True)
                if rec["preview"]:
                    st.audio(rec["preview"], format="audio/mp3")
    else:
        st.warning("No recommendations found.")

# Footer
st.markdown("""
<div style="text-align:center; padding: 4rem 0 2rem; color: #1e293b; font-size:0.75rem; letter-spacing:0.1em;">
  MELODIA • MUSIC RECOMMENDER
</div>
""", unsafe_allow_html=True)
