import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import joblib
import plotly.graph_objects as go
import plotly.express as px
import os
import random
import math
from groq import Groq

# =====================================================================
# 🎃 HAUNTED CHURN ORACLE — Halloween Edition 🎃
# 1) A ghost GATE asks "Do you really want to predict?"
# 2) Inside: spooky tantra/occult vibes (rotating ritual mandala,
#    candles, bats, fog, full moon).
# =====================================================================

st.set_page_config(
    page_title="🎃 Haunted Churn Oracle | Bank of the Dead",
    page_icon="👻",
    layout="wide",
)

# ---------------------------------------------------------------------
# Query-param helper (works on new + old Streamlit versions)
# ---------------------------------------------------------------------
def _qp(name):
    try:
        v = st.query_params.get(name)
    except Exception:
        v = st.experimental_get_query_params().get(name)
    if isinstance(v, list):
        return v[0] if v else None
    return v

# ---------------------------------------------------------------------
# 🎃 HALLOWEEN + TANTRA/OCCULT CSS
# ---------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Creepster&family=Special+Elite&display=swap');

/* --- Midnight graveyard background --- */
.stApp {
    background:
        radial-gradient(circle at 85% 8%, rgba(255, 214, 120, 0.16) 0 70px, transparent 140px),
        radial-gradient(circle at 15% 20%, rgba(139, 47, 201, 0.22), transparent 340px),
        radial-gradient(circle at 80% 85%, rgba(255, 107, 26, 0.12), transparent 320px),
        linear-gradient(180deg, #07030f 0%, #12071f 45%, #1c0b24 100%);
    color: #F7E8FF;
}

/* Headings in spooky font */
h1, h2, h3, h4 {
    font-family: 'Creepster', 'Georgia', serif !important;
    color: #FF8C1A !important;
    letter-spacing: 2px;
    text-shadow: 0 0 14px rgba(255, 107, 26, 0.55), 2px 2px 4px rgba(0,0,0,0.8);
}
p, li, label, span { color: #EFE6FF; }

/* --- Form = dark ritual card --- */
div[data-testid="stForm"] {
    background: rgba(22, 10, 38, 0.92);
    border: 1px solid #8B2FC9;
    border-radius: 16px;
    padding: 26px;
    box-shadow: 0 0 32px rgba(139, 47, 201, 0.45), inset 0 0 40px rgba(0,0,0,0.6);
}

/* Inputs */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
    background-color: #241238 !important;
    color: #FFE9C9 !important;
    border: 1px solid #8B2FC9 !important;
}
div[data-baseweb="select"] > div {
    background-color: #241238 !important;
    border: 1px solid #8B2FC9 !important;
    color: #FFE9C9 !important;
}

/* Buttons = pumpkin orange */
.stButton>button, .stFormSubmitButton>button, .stDownloadButton>button {
    background: linear-gradient(135deg, #FF6B1A, #B34700);
    color: #FFF3E0 !important;
    border-radius: 10px;
    border: 1px solid #FFB347;
    padding: 10px 24px;
    font-size: 16px;
    font-weight: bold;
    width: 100%;
    box-shadow: 0 0 16px rgba(255, 107, 26, 0.5);
    transition: 0.25s;
}
.stButton>button:hover, .stFormSubmitButton>button:hover, .stDownloadButton>button:hover {
    background: linear-gradient(135deg, #8B2FC9, #5B1A86);
    box-shadow: 0 0 22px rgba(139, 47, 201, 0.8);
    color: white !important;
}

/* Sidebar = haunted crypt */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #140826, #0A0514);
    border-right: 1px solid #8B2FC9;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #D9C6FF !important;
    font-weight: bold;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #FF8C1A !important;
}
div[data-baseweb="tab-highlight"] { background-color: #FF6B1A !important; }

/* --- Header banner --- */
.header-banner {
    background: radial-gradient(circle at 50% -30%, rgba(255,140,26,0.35), transparent 60%),
                linear-gradient(135deg, #2A0A45, #4A0E12 70%, #2A0A45);
    padding: 28px 40px;
    border-radius: 16px;
    color: white;
    text-align: center;
    margin-bottom: 25px;
    border: 1px solid #FF6B1A;
    box-shadow: 0 0 34px rgba(255, 107, 26, 0.35), 0 0 60px rgba(139, 47, 201, 0.3);
    position: relative;
    overflow: hidden;
}
.candle { display: inline-block; animation: flicker 1.6s infinite; font-size: 1.6rem; }
@keyframes flicker {
    0%, 100% { opacity: 1; transform: scale(1) rotate(-2deg); }
    40% { opacity: 0.65; transform: scale(1.08) rotate(2deg); }
    70% { opacity: 0.9; transform: scale(0.96) rotate(-1deg); }
}

/* --- Ambient decor: moon, bats, fog, rotating tantra mandala --- */
.moon {
    position: fixed; top: 56px; right: 26px; font-size: 54px; z-index: 0;
    filter: drop-shadow(0 0 22px rgba(255, 230, 150, 0.9));
    pointer-events: none; animation: Moon 4s ease-in-out infinite;
}
@keyframes Moon { 0%,100% { transform: scale(1); } 50% { transform: scale(1.06); } }

.bat {
    position: fixed; top: 70px; font-size: 30px; z-index: 0; pointer-events: none;
    animation: batFly 14s linear infinite;
}
.bat2 { top: 120px; font-size: 22px; animation-duration: 19s; animation-delay: 4s; }
.bat3 { top: 40px;  font-size: 26px; animation-duration: 23s; animation-delay: 9s; }
@keyframes batFly {
    0%   { left: -6%;  transform: translateY(0) scaleX(-1); }
    25%  { transform: translateY(26px) scaleX(-1); }
    50%  { transform: translateY(-14px) scaleX(-1); }
    75%  { transform: translateY(20px) scaleX(-1); }
    100% { left: 104%; transform: translateY(0) scaleX(-1); }
}

.fog {
    position: fixed; bottom: -40px; width: 60vw; height: 150px; z-index: 0;
    background: radial-gradient(ellipse at center, rgba(220, 200, 255, 0.20), transparent 70%);
    filter: blur(12px); pointer-events: none; animation: fogDrift 16s ease-in-out infinite alternate;
}
.fog-a { left: -10vw; } .fog-b { right: -10vw; animation-delay: 5s; }
@keyframes fogDrift { from { transform: translateX(0); } to { transform: translateX(9vw); } }

.mandala {
    position: fixed; left: 50%; top: 54%; width: 620px; height: 620px;
    margin-left: -310px; margin-top: -310px; z-index: 0; opacity: 0.13;
    pointer-events: none; animation: spinSlow 70s linear infinite;
}
@keyframes spinSlow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

/* --- 👻 THE GATE --- */
.gate-wrap { text-align: center; padding-top: 4vh; position: relative; z-index: 5; }
.gate-ghost { animation: floaty 3s ease-in-out infinite; filter: drop-shadow(0 0 26px rgba(200,180,255,0.85)); }
@keyframes floaty { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-18px); } }
.gate-title {
    font-family: 'Creepster', Georgia, serif; font-size: 3rem; color: #FF8C1A;
    text-shadow: 0 0 18px rgba(255,107,26,0.7), 3px 3px 0 #4A0E12; margin: 8px 0 0 0; letter-spacing: 3px;
}
.gate-sub { font-family: 'Special Elite', monospace; color: #D9C6FF; font-size: 1.05rem; margin-top: 6px; }
.gate-stage {
    position: relative; height: 250px; max-width: 720px; margin: 10px auto 0 auto;
    border: 1px dashed rgba(139,47,201,0.55); border-radius: 16px;
    background: rgba(20, 8, 38, 0.55);
}
.yes-btn {
    position: absolute; left: 16%; top: 92px; display: inline-block;
    background: linear-gradient(135deg, #FF6B1A, #C1440E); color: #FFF3E0 !important;
    font-family: 'Creepster', Georgia, serif; font-size: 1.7rem; letter-spacing: 2px;
    padding: 14px 42px; border-radius: 12px; border: 2px solid #FFB347; text-decoration: none !important;
    box-shadow: 0 0 22px rgba(255,107,26,0.75); transition: 0.2s; animation: yesPulse 1.8s infinite;
}
.yes-btn:hover { transform: scale(1.09) rotate(-1.5deg); background: linear-gradient(135deg, #8B2FC9, #5B1A86); }
@keyframes yesPulse { 0%,100% { box-shadow: 0 0 16px rgba(255,107,26,0.55);} 50% { box-shadow: 0 0 34px rgba(255,140,26,0.95);} }
.no-btn {
    position: absolute; left: 58%; top: 100px; cursor: not-allowed;
    font-family: 'Creepster', Georgia, serif; letter-spacing: 3px;
    font-size: 1.35rem; color: #FFB3A0 !important;
    padding: 15px 42px 13px 56px;
    background:
        radial-gradient(circle at 25px 46%, #ff2a1a 0 4px, rgba(255,42,26,.55) 7px, transparent 12px),
        radial-gradient(circle at 40px 46%, #ff2a1a 0 4px, rgba(255,42,26,.55) 7px, transparent 12px),
        linear-gradient(160deg, #1a0410, #2b0a1e 55%, #0d0208);
    border: 2px solid #7a1020; border-radius: 14px 14px 18px 18px;
    box-shadow: 0 0 18px rgba(255,30,20,.35), inset 0 0 18px rgba(122,16,32,.55), 0 10px 22px rgba(0,0,0,.6);
    text-shadow: 0 0 9px rgba(255,60,30,.8), 2px 2px 0 #000;
    transition: left 0.16s ease, top 0.16s ease, transform 0.16s ease;
    white-space: nowrap;
    animation: noTremble 2.6s ease-in-out infinite, noEyePulse 1.9s ease-in-out infinite alternate;
}
.no-btn::after {
    content: '☠'; position: absolute; right: 12px; top: 7px;
    font-size: .85rem; color: #ff6b4a; text-shadow: 0 0 8px rgba(255,60,30,.9);
}
@keyframes noTremble { 0%, 88%, 100% { rotate: 0deg; } 90% { rotate: -2.2deg; } 93% { rotate: 2deg; } 96% { rotate: -1.4deg; } }
@keyframes noEyePulse {
    from { box-shadow: 0 0 12px rgba(255,30,20,.28), inset 0 0 14px rgba(122,16,32,.5), 0 10px 22px rgba(0,0,0,.6); }
    to   { box-shadow: 0 0 30px rgba(255,30,20,.65), inset 0 0 24px rgba(180,20,40,.75), 0 10px 22px rgba(0,0,0,.6); }
}
/* CSS fallback in case JS is blocked: NO still hops away on hover */
.no-btn:hover { transform: translate(90px, -46px) rotate(9deg) scale(0.9); }
.gate-hint { font-family: 'Special Elite', monospace; color: #9D8BC7; font-size: 0.9rem; margin-top: 12px; }

/* --- 👻 Ghost CHATBOT docked bottom-right (keyed containers) --- */
.st-key-ghost_bot_closed, .st-key-ghost_bot_open {
    position: fixed; right: 18px; bottom: 14px; z-index: 99995;
    max-width: 92vw;
}
.st-key-ghost_bot_closed { width: 205px; }
.st-key-ghost_bot_open {
    width: 345px;
    /* FIX for clipped top on deployed/small screens: never taller
       than the viewport; scrolls internally instead of overflowing */
    max-height: calc(100vh - 84px);
    max-height: calc(100dvh - 84px);
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: #8B2FC9 transparent;
}
.st-key-ghost_bot_open [data-testid="stVerticalBlock"],
.st-key-ghost_panel [data-testid="stVerticalBlock"] { gap: 0.4rem; }
.ghost-panel-head { display: flex; align-items: center; justify-content: center; gap: 10px; }
.ghost-panel-head .ghost-panel-title { text-align: left; }
.ghost-panel-head .ghost-panel-sub { text-align: left; margin-bottom: 0; }
.ghost-head { text-align: center; animation: floaty 3.4s ease-in-out infinite; }
.st-key-ghost_panel {
    background: rgba(18, 7, 34, 0.97);
    border: 1px solid #8B2FC9; border-radius: 16px;
    padding: 12px 12px 6px 12px; margin-bottom: 8px;
    box-shadow: 0 0 26px rgba(139,47,201,0.55), 0 10px 30px rgba(0,0,0,0.65);
}
.ghost-panel-title {
    font-family: 'Creepster', Georgia, serif; color: #FF8C1A;
    font-size: 1.35rem; letter-spacing: 2px; text-align: center;
    text-shadow: 0 0 12px rgba(255,107,26,0.55);
}
.ghost-panel-sub {
    font-family: 'Special Elite', monospace; color: #D9C6FF;
    font-size: 0.75rem; text-align: center; margin-bottom: 4px;
}
.watcher-bubble {
    background: rgba(20, 8, 38, 0.92); border: 1px solid #8B2FC9; color: #FFE9C9;
    font-family: 'Special Elite', monospace; font-size: 0.78rem; border-radius: 12px;
    padding: 6px 10px; margin: 0 auto 6px auto; box-shadow: 0 0 14px rgba(139,47,201,0.6);
    max-width: 195px;
}
.pupil { transform-box: fill-box; transform-origin: center; animation: lookAround 5s ease-in-out infinite; }
@keyframes lookAround {
    0%, 100% { transform: translate(0px, 0px); }
    25% { transform: translate(3.5px, 1px); }
    55% { transform: translate(-3.5px, 2px); }
    80% { transform: translate(0px, -2.5px); }
}

/* --- 🏰 Entry: coded moonlit gothic castle (SVG, no image file) --- */
.gothic-scene {
    position: fixed; inset: 0; z-index: 99999; overflow: hidden;
    background: linear-gradient(180deg, #05020c, #3d1a66);
    animation: gothicOut 3.8s ease forwards;
}
@keyframes gothicOut { 0%, 86% { opacity: 1; } 100% { opacity: 0; visibility: hidden; } }
.gothic-scene svg.scene-svg { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
/* moon breathing glow (6s) */
.moon-glow { transform-box: fill-box; transform-origin: center; animation: moonBreathe 6s ease-in-out infinite alternate; }
@keyframes moonBreathe { from { transform: scale(1); opacity: .55; } to { transform: scale(1.13); opacity: .88; } }
.moon-core { filter: drop-shadow(0 0 26px rgba(255,70,30,.90)); }
.win-flicker { animation: winFlicker 3.4s linear infinite; }
@keyframes winFlicker { 0%,100% {opacity:.95;} 8% {opacity:.30;} 12% {opacity:.9;} 44% {opacity:.5;} 48% {opacity:.95;} 71% {opacity:.25;} 75% {opacity:.85;} }
/* clouds: seamless right-to-left parallax drift (speed = inline duration) */
.drift { animation-name: cloudDrift; animation-timing-function: linear; animation-iteration-count: infinite; will-change: transform; }
@keyframes cloudDrift { from { transform: translateX(0); } to { transform: translateX(-2300px); } }
/* mountains: subtle sway */
.sway-a { animation: swayA 22s ease-in-out infinite alternate; }
.sway-b { animation: swayB 27s ease-in-out infinite alternate; }
@keyframes swayA { from { transform: translateX(-8px); } to { transform: translateX(8px); } }
@keyframes swayB { from { transform: translateX(10px); } to { transform: translateX(-10px); } }
/* mist at castle base / valley */
.mist-drift-a { animation: mistA 13s ease-in-out infinite alternate; }
.mist-drift-b { animation: mistA 17s ease-in-out infinite alternate-reverse; }
@keyframes mistA { from { transform: translateX(-26px); } to { transform: translateX(26px); } }
/* 🕷️ Entry spiderfall: small, medium and very large spiders descend
   from the top on silk threads. The complete entry ends in 3.8s. */
.entry-spider-layer { position: absolute; inset: 0; z-index: 7; overflow: hidden; pointer-events: none; }
.entry-spider {
    position: absolute; top: -8px; width: var(--size); height: var(--drop);
    margin-left: calc(var(--size) / -2); opacity: 0;
    transform: translate3d(0, calc(-1 * var(--drop)), 0);
    animation-name: entrySpiderFall; animation-timing-function: cubic-bezier(.2,.72,.28,1);
    animation-fill-mode: both; will-change: transform, opacity;
}
.entry-spider::before {
    content: ''; position: absolute; left: 50%; top: 0;
    bottom: calc(var(--size) * .72); width: 1px; transform: translateX(-.5px);
    background: linear-gradient(180deg, rgba(255,255,255,0), rgba(237,233,255,.88) 16%, rgba(237,233,255,.50));
    box-shadow: 0 0 5px rgba(217,198,255,.45);
}
.entry-spider-body {
    position: absolute; left: 50%; bottom: 0; width: var(--size);
    transform: translateX(-50%) rotate(-5deg); transform-origin: 50% -18%;
    animation: entrySpiderSwing 1.1s ease-in-out infinite alternate;
    filter: drop-shadow(0 8px 10px rgba(0,0,0,.62)) drop-shadow(0 0 7px rgba(157,107,255,.38));
}
.entry-spider-body svg { display: block; width: 100%; height: auto; overflow: visible; }
/* old-school spider legs: one jointed fan that wiggles
   (also reused by the walking data-spider on the dashboard) */
.spider-legs { transform-box: fill-box; transform-origin: center; animation: spiderLegWiggle .28s ease-in-out infinite alternate; }
@keyframes spiderLegWiggle { from { transform: scale(1,.96); } to { transform: scale(1.035,1.04); } }
@keyframes entrySpiderFall {
    0% { opacity: 0; transform: translate3d(0, calc(-1 * var(--drop)), 0); }
    8% { opacity: 1; }
    72% { opacity: 1; transform: translate3d(0, 11px, 0); }
    84% { transform: translate3d(0, -5px, 0); }
    100% { opacity: 1; transform: translate3d(0, 0, 0); }
}
@keyframes entrySpiderSwing {
    from { transform: translateX(-50%) rotate(-5deg); }
    to { transform: translateX(-50%) rotate(5deg); }
}

.gothic-caption {
    position: absolute; left: 50%; bottom: 11vh; z-index: 9;
    width: min(880px, 88vw); text-align: center; pointer-events: none;
    font-family: 'Special Elite', monospace; color: #F3EAFF;
    font-size: clamp(1rem, 2.3vw, 1.55rem); line-height: 1.6; letter-spacing: 1.5px;
    text-shadow: 0 2px 14px #000, 0 0 26px rgba(157,107,255,.55);
    opacity: 0; animation: captionRise 3.8s ease forwards;
}
.gothic-caption span { display: block; }
@keyframes captionRise {
    0%, 55% { opacity: 0; transform: translate(-50%, 16px); }
    70%, 90% { opacity: 1; transform: translate(-50%, 0); }
    100% { opacity: 0; transform: translate(-50%, 0); }
}
@media (prefers-reduced-motion: reduce) {
    .gothic-scene *, .gothic-scene { animation-duration: .1s !important; }
    .moon-glow, .drift, .sway-a, .sway-b, .mist-drift-a, .mist-drift-b, .win-flicker, .entry-spider, .entry-spider-body, .spider-legs, .gothic-caption { animation: none !important; }
}

/* --- 🕷️ Spider dock: the data-spider patrols only the full rectangular
   page border. The invisible click button moves with the spider. --- */
.st-key-spider_dock {
    position: fixed; top: 30px; left: 20px; width: 128px; z-index: 99994;
    text-align: center;
    animation: spiderPatrol 46s ease-in-out 3.65s infinite;
    will-change: transform;
}
.spider-walk { animation: spiderBob .3s ease-in-out infinite alternate; }
.spider-walk svg {
    width: 112px; height: auto; display: block; margin: 0 auto;
    filter: drop-shadow(0 0 10px rgba(139,47,201,0.8));
    animation: spiderHeading 46s ease-in-out 3.65s infinite;
    will-change: transform;
}
@keyframes spiderPatrol {
    0%   { transform: translate(0, 0); }
    31%  { transform: translate(calc(100vw - 172px), 0); }
    34%  { transform: translate(calc(100vw - 172px), 0); }
    48%  { transform: translate(calc(100vw - 172px), calc(100vh - 172px)); }
    51%  { transform: translate(calc(100vw - 172px), calc(100vh - 172px)); }
    82%  { transform: translate(0, calc(100vh - 172px)); }
    85%  { transform: translate(0, calc(100vh - 172px)); }
    97%  { transform: translate(0, 0); }
    100% { transform: translate(0, 0); }
}
@keyframes spiderHeading {
    0%, 31%  { transform: rotate(90deg); }
    34%, 48% { transform: rotate(180deg); }
    51%, 82% { transform: rotate(270deg); }
    85%, 97% { transform: rotate(360deg); }
    100%     { transform: rotate(450deg); }
}
@keyframes spiderBob { from { transform: translateY(0); } to { transform: translateY(2.5px); } }
.spider-hint {
    font-family: 'Special Elite', monospace; font-size: 0.68rem; color: #D9C6FF;
    animation: flicker 2.2s infinite; margin-top: 2px;
}
@media (prefers-reduced-motion: reduce) {
    .st-key-spider_dock, .spider-walk, .spider-walk svg, .no-btn { animation: none !important; }
}
/* invisible native button laid OVER the spider = the spider itself is clickable */
.st-key-spider_click { position: absolute !important; left: 2px; right: 2px; top: 0; height: 118px; }
.st-key-spider_click button {
    width: 100% !important; height: 118px !important; opacity: 0 !important;
    background: transparent !important; border: none !important; box-shadow: none !important;
    cursor: pointer;
}
.st-key-spider_panel {
    position: fixed; left: 14px; top: 272px; width: 338px; max-width: 92vw; z-index: 99994;
    max-height: calc(100vh - 292px); max-height: calc(100dvh - 292px); overflow-y: auto;
    scrollbar-width: thin; scrollbar-color: #8B2FC9 transparent;
    background: rgba(18, 7, 34, 0.97); border: 1px solid #8B2FC9; border-radius: 16px;
    padding: 14px 14px 8px 14px;
    box-shadow: 0 0 26px rgba(139,47,201,0.55), 0 10px 30px rgba(0,0,0,0.65);
}
.spider-panel-title {
    font-family: 'Creepster', Georgia, serif; color: #FF8C1A; font-size: 1.4rem;
    letter-spacing: 2px; text-shadow: 0 0 12px rgba(255,107,26,0.55);
}

/* --- 🔥 HELL jumpscare overlay --- */
.hell-overlay {
    position: fixed; inset: 0; z-index: 99999; pointer-events: none;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    background: radial-gradient(circle at center, rgba(120,0,0,0.35), rgba(10,0,0,0.88) 75%);
    animation: hellFade 5.5s ease forwards;
}
@keyframes hellFade { 0% {opacity: 0;} 6% {opacity: 1;} 82% {opacity: 1;} 100% {opacity: 0; visibility: hidden;} }
.hell-ghost { font-size: 170px; filter: drop-shadow(0 0 40px rgba(255,40,40,0.95)); animation: hellZoom 5.5s ease forwards; }
@keyframes hellZoom {
    0% { transform: scale(0.25) rotate(0deg); opacity: 0; }
    12% { transform: scale(1.15) rotate(-4deg); opacity: 1; }
    20% { transform: scale(1.05) rotate(3deg); }
    30% { transform: scale(1.25) rotate(-3deg); }
    45% { transform: scale(1.35) translateY(-8px) rotate(2deg); }
    80% { transform: scale(1.6) rotate(0deg); opacity: 1; }
    100% { transform: scale(2.1); opacity: 0; }
}
.hell-text {
    font-family: 'Creepster', Georgia, serif; font-size: 2.6rem; color: #FF3B1F; text-align: center;
    text-shadow: 0 0 22px rgba(255,60,20,0.95), 3px 3px 0 #1A0000; letter-spacing: 3px;
    animation: shakeIt 0.45s infinite; padding: 0 20px;
}
@keyframes shakeIt {
    0% { transform: translate(1px, 1px) rotate(0deg); } 25% { transform: translate(-2px, 1px) rotate(-0.6deg); }
    50% { transform: translate(2px, -1px) rotate(0.6deg); } 75% { transform: translate(-1px, 2px) rotate(0deg); }
    100% { transform: translate(1px, -2px) rotate(0deg); }
}
.flames { position: absolute; bottom: 6px; width: 100%; text-align: center; font-size: 44px; animation: flicker 1.2s infinite; }

.happy-ending {
    background: linear-gradient(135deg, #3B1D5E, #6B3410);
    border: 2px solid #FFB347; border-radius: 16px; padding: 20px; text-align: center;
    box-shadow: 0 0 28px rgba(255, 179, 71, 0.55); animation: happyBounce 1.6s ease-in-out infinite;
}
@keyframes happyBounce { 0%,100% { transform: scale(1); } 50% { transform: scale(1.015); } }
.happy-ending h2 { color: #FFD98A !important; margin: 0; font-size: 2rem; }

.doom-banner {
    background: linear-gradient(135deg, #2A0000, #4A0E12);
    border: 2px solid #FF3B1F; border-radius: 16px; padding: 18px; text-align: center;
    box-shadow: 0 0 28px rgba(255, 59, 31, 0.5);
}
.doom-banner h2 { color: #FF6B4A !important; margin: 0; font-size: 1.9rem; }



/* --- 🎃 Laughing pumpkins: bouncing squash, chattering mouth, glowing eyes --- */
.laughing-pumpkin {
    display: inline-block; width: 57px; height: 57px; margin: 0 7px;
    vertical-align: -13px; transform-origin: 50% 82%;
    animation: pumpkinLaugh 1.65s ease-in-out infinite;
    filter: drop-shadow(0 0 13px rgba(255,124,26,.58));
}
.laughing-pumpkin svg { width: 100%; height: 100%; display: block; overflow: visible; }
.pumpkin-eye {
    transform-box: fill-box; transform-origin: center;
    filter: drop-shadow(0 0 5px #ffd23f) drop-shadow(0 0 11px rgba(255,145,0,.92));
    animation: pumpkinEyeGlow 1.08s ease-in-out infinite alternate;
}
.pumpkin-mouth {
    transform-box: fill-box; transform-origin: 50% 18%;
    filter: drop-shadow(0 0 6px rgba(255,172,26,.72));
    animation: pumpkinMouthChatter .36s ease-in-out infinite alternate;
}
.pumpkin-flame {
    transform-box: fill-box; transform-origin: 50% 100%;
    animation: pumpkinFlameDance .42s ease-in-out infinite alternate;
}
.pumpkin-ha {
    fill: #ffd98a; font-family: 'Creepster', Georgia, serif; font-size: 13px;
    letter-spacing: 1px; opacity: 0; transform-box: fill-box; transform-origin: center;
    text-shadow: 0 0 8px rgba(255,145,0,.85);
    animation: pumpkinHaFloat 1.65s ease-in-out infinite;
}
.pumpkin-ha.two { animation-delay: .44s; font-size: 10px; }
@keyframes pumpkinLaugh {
    0%, 100% { transform: translateY(0) rotate(-2deg) scale(1, 1); }
    16% { transform: translateY(-6px) rotate(2.5deg) scale(1.045, .955); }
    32% { transform: translateY(1px) rotate(-2.5deg) scale(.97, 1.035); }
    48% { transform: translateY(-5px) rotate(2deg) scale(1.035, .965); }
    64% { transform: translateY(0) rotate(-1.5deg) scale(.985, 1.02); }
    80% { transform: translateY(-3px) rotate(1.5deg) scale(1.02, .985); }
}
@keyframes pumpkinEyeGlow {
    from { opacity: .68; transform: scale(.91); }
    to { opacity: 1; transform: scale(1.10); }
}
@keyframes pumpkinMouthChatter {
    from { transform: scaleY(.68) rotate(-.6deg); }
    to { transform: scaleY(1.14) rotate(.6deg); }
}
@keyframes pumpkinFlameDance {
    from { transform: scale(.88, .82) rotate(-3deg); opacity: .78; }
    to { transform: scale(1.05, 1.12) rotate(3deg); opacity: 1; }
}
@keyframes pumpkinHaFloat {
    0%, 100% { opacity: 0; transform: translateY(5px) rotate(-5deg) scale(.82); }
    24%, 56% { opacity: 1; transform: translateY(-2px) rotate(3deg) scale(1); }
    76% { opacity: 0; transform: translateY(-7px) rotate(6deg) scale(.94); }
}
@media (prefers-reduced-motion: reduce) {
    .laughing-pumpkin, .pumpkin-eye, .pumpkin-mouth, .pumpkin-flame, .pumpkin-ha { animation: none !important; }
    .pumpkin-ha { opacity: 1; }
}

/* --- ⚰️ CSV upload = The Coffin of Souls portal --- */
.st-key-csv_coffin {
    position: relative; overflow: visible;
    border: 1px solid rgba(190,139,255,.72); border-radius: 24px;
    padding: 20px 20px 16px 20px; margin: 8px 0 18px 0;
    background:
        radial-gradient(circle at 12% 0%, rgba(255,140,26,.20), transparent 240px),
        radial-gradient(circle at 90% 15%, rgba(157,107,255,.26), transparent 270px),
        linear-gradient(145deg, rgba(35,13,61,.98), rgba(12,5,24,.98) 58%, rgba(48,18,20,.96));
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.045), inset 0 0 45px rgba(0,0,0,.55),
                0 0 32px rgba(139,47,201,.30), 0 18px 36px rgba(0,0,0,.26);
}
.st-key-csv_coffin::before {
    content: '🕸️'; position: absolute; top: -8px; left: 12px; z-index: 0;
    font-size: 52px; opacity: .34; transform: rotate(-12deg); pointer-events: none;
}
.st-key-csv_coffin::after {
    content: '🦇  🦇'; position: absolute; top: 12px; right: 20px; z-index: 0;
    font-size: 24px; letter-spacing: 14px; opacity: .52; pointer-events: none;
    animation: csvBatBob 2.8s ease-in-out infinite alternate;
}
@keyframes csvBatBob { from { transform: translateY(-2px) rotate(-2deg); } to { transform: translateY(5px) rotate(2deg); } }
.st-key-csv_coffin > div { position: relative; z-index: 1; }
.csv-portal-head {
    display: flex; align-items: center; justify-content: center; gap: 18px;
    text-align: center; margin: 2px auto 14px auto; max-width: 900px;
}
.csv-portal-icon {
    font-size: 54px; line-height: 1; filter: drop-shadow(0 0 14px rgba(255,140,26,.66));
    animation: csvCoffinFloat 3.2s ease-in-out infinite;
}
.csv-portal-icon.mirror { animation-delay: -1.1s; }
@keyframes csvCoffinFloat { 0%,100% { transform: translateY(2px) rotate(-2deg); } 50% { transform: translateY(-6px) rotate(2deg); } }
.csv-portal-kicker {
    font-family: 'Special Elite', monospace; font-size: .72rem; letter-spacing: 3px;
    color: #c9a7ff; text-transform: uppercase;
}
.csv-portal-title {
    font-family: 'Creepster', Georgia, serif; font-size: clamp(2rem, 4.4vw, 3.25rem);
    line-height: .95; letter-spacing: 3px; color: #ffb347;
    text-shadow: 0 0 18px rgba(255,107,26,.62), 3px 3px 0 #260315;
    margin: 3px 0 6px 0;
}
.csv-portal-sub { font-family: 'Special Elite', monospace; color: #eadfff; font-size: .94rem; }
.csv-portal-steps {
    display: flex; flex-wrap: wrap; justify-content: center; align-items: center;
    gap: 9px; margin: 12px auto 16px auto;
}
.csv-portal-steps span {
    display: inline-flex; align-items: center; gap: 6px; padding: 7px 12px;
    border: 1px solid rgba(201,167,255,.46); border-radius: 999px;
    background: rgba(255,255,255,.055); color: #ffe9c9;
    font-family: 'Special Elite', monospace; font-size: .76rem;
    box-shadow: inset 0 0 14px rgba(157,107,255,.13);
}
.csv-portal-steps b { color: #ff9a3c; font-size: .9rem; }
.st-key-csv_coffin [data-testid="stFileUploader"] { position: relative; z-index: 2; }
.st-key-csv_coffin [data-testid="stFileUploader"] label,
.st-key-csv_coffin [data-testid="stFileUploader"] label p {
    color: #ffd98a !important; font-family: 'Special Elite', monospace !important;
    font-size: 1rem !important; letter-spacing: .4px;
}
.st-key-csv_coffin [data-testid="stFileUploaderDropzone"],
.st-key-csv_coffin [data-testid="stFileUploadDropzone"],
.st-key-csv_coffin [data-testid="stFileUploader"] section {
    position: relative; min-height: 150px; overflow: hidden;
    border: 2px dashed rgba(255,179,71,.82) !important;
    clip-path: polygon(9% 0, 91% 0, 100% 22%, 96% 100%, 4% 100%, 0 22%);
    background:
        radial-gradient(circle at 50% 42%, rgba(255,140,26,.18), transparent 190px),
        radial-gradient(circle at 18% 18%, rgba(201,167,255,.16), transparent 150px),
        linear-gradient(180deg, rgba(43,18,72,.96), rgba(18,7,30,.98)) !important;
    box-shadow: inset 0 0 0 5px rgba(10,4,18,.58), inset 0 0 38px rgba(139,47,201,.40),
                0 0 26px rgba(255,107,26,.16);
    transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
}
.st-key-csv_coffin [data-testid="stFileUploaderDropzone"]:hover,
.st-key-csv_coffin [data-testid="stFileUploadDropzone"]:hover,
.st-key-csv_coffin [data-testid="stFileUploader"] section:hover,
.st-key-csv_coffin [data-testid="stFileUploader"]:focus-within section {
    border-color: #ffd23f !important; transform: translateY(-2px);
    box-shadow: inset 0 0 0 5px rgba(10,4,18,.58), inset 0 0 48px rgba(255,140,26,.30),
                0 0 36px rgba(255,140,26,.38);
}
.st-key-csv_coffin [data-testid="stFileUploaderDropzone"]::before,
.st-key-csv_coffin [data-testid="stFileUploadDropzone"]::before,
.st-key-csv_coffin [data-testid="stFileUploader"] section::before {
    content: '👻'; position: absolute; left: 50%; top: 9px; z-index: 0;
    transform: translateX(-50%); font-size: 34px; opacity: .24; pointer-events: none;
    animation: csvGhostFloat 3s ease-in-out infinite;
}
.st-key-csv_coffin [data-testid="stFileUploaderDropzone"]::after,
.st-key-csv_coffin [data-testid="stFileUploadDropzone"]::after,
.st-key-csv_coffin [data-testid="stFileUploader"] section::after {
    content: ''; position: absolute; inset: -35% auto -35% -18%; width: 90px; z-index: 0;
    transform: rotate(13deg); pointer-events: none;
    background: linear-gradient(90deg, transparent, rgba(201,167,255,.15), transparent);
    animation: csvPortalScan 4.8s ease-in-out infinite;
}
@keyframes csvGhostFloat { 0%,100% { margin-top: 0; } 50% { margin-top: -7px; } }
@keyframes csvPortalScan { 0%, 58%, 100% { left: -18%; opacity: 0; } 68% { opacity: 1; } 86% { left: 108%; opacity: 0; } }
.st-key-csv_coffin [data-testid="stFileUploader"] section > div { position: relative; z-index: 2; }
.st-key-csv_coffin [data-testid="stFileUploader"] button {
    background: linear-gradient(135deg, #ff7a1a, #9d2dff) !important;
    border: 1px solid #ffd23f !important; color: #fff8e8 !important;
    border-radius: 999px !important; padding: 9px 22px !important;
    font-family: 'Special Elite', monospace !important; font-weight: bold !important;
    box-shadow: 0 0 20px rgba(255,122,26,.48), inset 0 0 12px rgba(255,255,255,.12) !important;
}
.st-key-csv_coffin [data-testid="stFileUploader"] button:hover {
    background: linear-gradient(135deg, #9d2dff, #ff7a1a) !important;
    transform: translateY(-1px) scale(1.02);
}
.csv-column-chips { display: flex; flex-wrap: wrap; justify-content: center; gap: 6px; margin-top: 12px; }
.csv-column-chips span {
    padding: 4px 8px; border-radius: 7px; border: 1px solid rgba(201,167,255,.30);
    background: rgba(8,3,16,.52); color: #cdbcec; font-family: monospace; font-size: .68rem;
}
.csv-empty, .csv-success {
    border-radius: 16px; padding: 15px 18px; margin: 8px 0 16px 0;
    font-family: 'Special Elite', monospace; text-align: center;
}
.csv-empty { border: 1px dashed rgba(201,167,255,.45); background: rgba(25,10,44,.62); color: #d9c6ff; }
.csv-success {
    border: 1px solid rgba(255,210,63,.70); color: #fff0c2;
    background: linear-gradient(135deg, rgba(73,38,5,.72), rgba(52,18,78,.78));
    box-shadow: 0 0 24px rgba(255,140,26,.20), inset 0 0 25px rgba(255,140,26,.08);
}
.csv-success strong { color: #ffd23f; }
@media (max-width: 720px) {
    .csv-portal-head { gap: 9px; }
    .csv-portal-icon { font-size: 38px; }
    .csv-portal-steps b { display: none; }
    .st-key-csv_coffin::after { display: none; }
}

/* --- 🪦 Four performance metrics carved into tombstones --- */
.metric-tombs-title {
    margin: 24px 0 2px 0; text-align: center;
    font-family: 'Creepster', Georgia, serif; font-size: 1.65rem;
    letter-spacing: 2.5px; color: #ffb347;
    text-shadow: 0 0 16px rgba(255,107,26,.48), 2px 2px 0 #210315;
}
.metric-tombs {
    display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 19px 16px; margin: 16px 2px 10px 2px; width: 100%;
}
.metric-tomb {
    --tilt: 0deg; position: relative; min-height: 182px; overflow: hidden;
    padding: 30px 15px 23px 15px; text-align: center; color: #f3ead2;
    transform: rotate(var(--tilt)); transition: transform .28s ease, box-shadow .28s ease, filter .28s ease;
    border: 2px solid #1d1a24; border-bottom: 8px solid #14111a;
    border-radius: 120px 120px 14px 14px / 96px 96px 14px 14px;
    background:
        radial-gradient(circle at 20% 10%, rgba(255,255,255,.17), transparent 105px),
        radial-gradient(circle at 86% 78%, rgba(0,0,0,.22), transparent 115px),
        repeating-linear-gradient(93deg, rgba(255,255,255,.025) 0 3px, transparent 3px 11px),
        linear-gradient(180deg, #858292 0%, #5d5a68 42%, #35323f 100%);
    box-shadow: inset 0 0 0 3px rgba(238,231,210,.10), inset 0 -22px 30px rgba(0,0,0,.38),
                inset 12px 0 24px rgba(255,255,255,.06), 0 15px 24px rgba(0,0,0,.38);
}
.metric-tomb::before {
    content: ''; position: absolute; inset: 9px; pointer-events: none;
    border: 1px solid rgba(238,231,210,.30); border-radius: inherit;
    box-shadow: inset 0 0 18px rgba(0,0,0,.18);
}
.metric-tomb::after {
    content: ''; position: absolute; left: -4%; right: -4%; bottom: -2px; height: 22px;
    pointer-events: none; opacity: .96;
    background:
        radial-gradient(ellipse 28px 18px at 8% 100%, #26351d 60%, transparent 62%),
        radial-gradient(ellipse 42px 22px at 31% 105%, #31451f 60%, transparent 62%),
        radial-gradient(ellipse 36px 19px at 58% 100%, #26351d 60%, transparent 62%),
        radial-gradient(ellipse 48px 23px at 84% 105%, #31451f 60%, transparent 62%),
        linear-gradient(180deg, transparent 30%, #1c2a17 100%);
}
.metric-tomb:hover {
    transform: rotate(var(--tilt)) translateY(-6px) scale(1.018);
    filter: brightness(1.07);
    box-shadow: inset 0 0 0 3px rgba(238,231,210,.12), inset 0 -22px 30px rgba(0,0,0,.38),
                0 20px 30px rgba(0,0,0,.46), 0 0 26px rgba(157,107,255,.28);
}
.metric-tomb-moon { position: absolute; top: 12px; right: 19px; color: rgba(243,234,210,.55); font-size: 1rem; }
.metric-tomb-icon { position: relative; z-index: 2; font-size: 1.72rem; line-height: 1; filter: drop-shadow(0 3px 4px rgba(0,0,0,.48)); }
.metric-tomb-label {
    position: relative; z-index: 2; min-height: 2.15em; margin-top: 8px;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Special Elite', monospace; font-size: .72rem; line-height: 1.25;
    letter-spacing: 1.15px; text-transform: uppercase; color: #ddd2b8;
    text-shadow: 0 2px 3px rgba(0,0,0,.62);
}
.metric-tomb-value {
    position: relative; z-index: 2; margin-top: 3px;
    font-family: 'Creepster', Georgia, serif; font-size: clamp(2rem, 4vw, 2.65rem);
    line-height: 1; letter-spacing: 1.5px; color: #fff7dc;
    text-shadow: 0 2px 0 rgba(255,255,255,.14), 0 4px 7px rgba(0,0,0,.68), 0 0 16px rgba(255,214,120,.16);
}
.metric-tomb-rune { position: relative; z-index: 2; margin-top: 8px; color: rgba(238,231,210,.62); font-family: 'Special Elite', monospace; font-size: .62rem; letter-spacing: 1.4px; text-transform: uppercase; }
.metric-tomb-crack { position: absolute; z-index: 1; left: 17px; top: 38px; width: 38px; height: 86px; opacity: .46; }
@media (max-width: 1050px) { .metric-tombs { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 540px) { .metric-tombs { grid-template-columns: 1fr; } }

.escape-link { color: #9D8BC7 !important; text-decoration: none; font-family: 'Special Elite', monospace; font-size: 0.85rem; }
.escape-link:hover { color: #FF8C1A !important; }

.app-footer { text-align:center; margin:36px auto 8px; padding-top:14px; border-top:1px solid rgba(157,107,255,.25); font-family:'Special Elite',monospace; font-size:.78rem; letter-spacing:2.5px; color:#9D8BC7; }
</style>
""", unsafe_allow_html=True)

# The Death Note is rendered as a fresh embedded component for every
# prediction run, so its CSS travels with that component.
DEATH_BOOK_CSS = r'''
/* --- 📓 DEATH NOTE result book: black cover, fast page turns, ink writing --- */
.death-book-stage {
    position: relative; margin: 16px auto 28px auto; padding: 18px 4px 30px 4px;
    perspective: 1900px; overflow: visible;
}
.death-book-glow {
    position: absolute; inset: 7% 3% 3% 3%; pointer-events: none;
    background: radial-gradient(circle at 50% 45%, rgba(157,107,255,.34), rgba(255,107,26,.12) 38%, transparent 70%);
    filter: blur(24px); opacity: .65; animation: bookGlowPulse 2.8s ease-in-out infinite alternate;
}
@keyframes bookGlowPulse { from { opacity: .43; transform: scale(.985); } to { opacity: .72; transform: scale(1.015); } }
.death-book {
    position: relative; z-index: 2; width: min(1010px, 98%); height: 640px;
    margin: 0 auto; transform-style: preserve-3d;
    animation: bookArrive 1.45s cubic-bezier(.2,.75,.25,1) .35s both;
}
.death-book * { box-sizing: border-box; }
@keyframes bookArrive {
    0% { opacity: 0; transform: translateX(-23%) scale(.91) rotateX(5deg); }
    18% { opacity: 1; }
    100% { opacity: 1; transform: translateX(0) scale(1) rotateX(0deg); }
}
.death-book-shadow {
    position: absolute; left: 4%; right: 2%; bottom: -24px; height: 38px; z-index: 0;
    background: radial-gradient(ellipse at center, rgba(0,0,0,.78), transparent 70%); filter: blur(8px);
}
.book-cover-back {
    position: absolute; inset: -10px -8px -12px -8px; z-index: 1; opacity: 0;
    border-radius: 18px 12px 14px 18px; border: 1px solid #342a40;
    background: linear-gradient(90deg, #030304, #17111e 47%, #020203 51%, #17111e 55%, #030304);
    box-shadow: inset 0 0 0 4px #07060a, inset 0 0 55px #000, 0 28px 55px rgba(0,0,0,.62);
    animation: pageMaterialize .5s ease 1.08s both;
}
.book-page {
    position: absolute; top: 8px; bottom: 8px; z-index: 3; width: calc(50% - 7px);
    overflow: hidden; color: #2d180f;
    background:
        radial-gradient(circle at 18% 13%, rgba(117,72,28,.20), transparent 135px),
        radial-gradient(circle at 83% 82%, rgba(117,72,28,.15), transparent 150px),
        repeating-linear-gradient(180deg, transparent 0 30px, rgba(99,64,30,.052) 31px),
        linear-gradient(105deg, #d8bd82, #efdfb4 24%, #e5cf9d 68%, #c8a96d);
}
.book-page::before {
    content: ''; position: absolute; inset: 0; z-index: 0; pointer-events: none;
    background: repeating-linear-gradient(90deg, transparent 0 8px, rgba(90,58,24,.035) 9px);
}
.book-page > * { position: relative; z-index: 1; }
.book-page-left {
    left: 7px; border-radius: 13px 3px 5px 15px; padding: 36px 42px 28px 44px; opacity: 0;
    box-shadow: inset -30px 0 38px rgba(81,43,10,.30), inset 0 0 46px rgba(101,62,24,.16);
    animation: pageMaterialize .48s ease 1.24s both;
}
.book-page-right {
    right: 7px; border-radius: 3px 13px 15px 5px; padding: 36px 44px 28px 42px;
    box-shadow: inset 30px 0 38px rgba(81,43,10,.28), inset 0 0 46px rgba(101,62,24,.16);
}
@keyframes pageMaterialize { from { opacity: 0; } to { opacity: 1; } }
.book-spine {
    position: absolute; left: 50%; top: 3px; bottom: 3px; width: 24px; z-index: 12;
    transform: translateX(-50%); pointer-events: none;
    background: linear-gradient(90deg, transparent, rgba(64,35,12,.34), rgba(20,8,3,.66), rgba(64,35,12,.32), transparent);
}
.death-cover {
    position: absolute; left: 50%; top: -8px; bottom: -10px; width: calc(50% + 7px); z-index: 45;
    transform-origin: left center; transform-style: preserve-3d; backface-visibility: hidden;
    border-radius: 5px 17px 17px 5px; border: 1px solid #3b3144;
    background:
        radial-gradient(circle at 74% 18%, rgba(157,107,255,.16), transparent 180px),
        radial-gradient(circle at 20% 86%, rgba(255,255,255,.045), transparent 150px),
        linear-gradient(135deg, #1d1823, #020202 52%, #15101b);
    box-shadow: inset 0 0 0 4px #08070b, inset 0 0 48px #000, 18px 24px 38px rgba(0,0,0,.55);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    animation: coverOpen 1.05s cubic-bezier(.25,.75,.3,1) .72s both;
}
.death-cover::before {
    content: ''; position: absolute; inset: 22px; border: 1px solid rgba(213,183,112,.42);
    box-shadow: inset 0 0 0 5px rgba(213,183,112,.07); pointer-events: none;
}
@keyframes coverOpen {
    0% { transform: rotateY(0deg); }
    55% { transform: rotateY(-104deg); }
    100% { transform: rotateY(-180deg); }
}
.death-cover-skull { font-size: 104px; line-height: 1; color: #d8c596; text-shadow: 0 0 24px rgba(216,197,150,.28); margin-bottom: 18px; }
.death-cover-title {
    font-family: 'Creepster', Georgia, serif; font-size: clamp(2.7rem, 6vw, 4.6rem);
    line-height: .92; text-align: center; letter-spacing: 7px; color: #eee5cf;
    text-shadow: 0 3px 0 #000, 0 0 24px rgba(216,197,150,.20);
}
.death-cover-sub { margin-top: 20px; font-family: 'Special Elite', monospace; font-size: .78rem; letter-spacing: 4px; color: #bda875; }
.turn-page {
    position: absolute; left: 50%; top: 10px; bottom: 10px; width: calc(50% - 11px); z-index: 20;
    transform-origin: left center; transform-style: preserve-3d; backface-visibility: hidden;
    border-radius: 3px 11px 13px 3px; overflow: hidden;
    background:
        repeating-linear-gradient(180deg, transparent 0 27px, rgba(99,64,30,.09) 28px),
        radial-gradient(circle at 78% 18%, rgba(117,72,28,.18), transparent 120px),
        linear-gradient(100deg, #c9ab72, #eedcae 28%, #ddc28d 72%, #bb985e);
    box-shadow: inset 22px 0 28px rgba(81,43,10,.22), -8px 0 18px rgba(0,0,0,.18);
    animation: turnPage .52s cubic-bezier(.32,.65,.35,1) both;
}
.turn-page::after {
    content: ''; position: absolute; inset: 52px 42px;
    background: repeating-linear-gradient(180deg, rgba(61,36,17,.30) 0 2px, transparent 2px 23px);
    opacity: .30; transform: rotate(-.5deg);
}
.turn-page > span {
    position: absolute; right: 28px; bottom: 22px; z-index: 2;
    color: rgba(74,39,16,.58) !important; font-size: 32px;
}
.turn-peek {
    position: absolute; inset: 44px 34px 38px 42px; z-index: 1;
    transform: rotate(-1.1deg);
    font-family: 'Special Elite', monospace; color: rgba(61,36,17,.80);
}
.turn-peek .peek-head {
    font-family: 'Creepster', Georgia, serif; font-size: 1.02rem; letter-spacing: 2px;
    color: rgba(53,22,13,.72); text-align: center;
    border-bottom: 2px solid rgba(61,36,17,.35); padding-bottom: 5px; margin-bottom: 9px;
}
.turn-peek .peek-row {
    display: flex; justify-content: space-between; gap: 10px;
    font-size: .64rem; line-height: 1.55;
    border-bottom: 1px solid rgba(93,57,24,.20); padding: 3px 0;
}
.turn-peek .peek-row b.doom { color: #7a1020; }
.turn-peek .peek-row b.safe { color: #3f6212; }
.turn-peek .peek-foot { margin-top: 9px; font-size: .6rem; font-style: italic; opacity: .75; text-align: right; }
@keyframes turnPage {
    0% { transform: rotateY(0deg); }
    54% { transform: rotateY(-96deg) skewY(-1.2deg); }
    100% { transform: rotateY(-180deg); }
}
.book-kicker {
    font-family: 'Special Elite', monospace; font-size: .70rem; letter-spacing: 3px;
    color: #76552a !important; text-align: center; text-transform: uppercase;
}
.death-book .book-page h3 span { color: #35160d !important; text-shadow: none !important; }
.death-book .book-page h3 {
    font-family: 'Creepster', Georgia, serif !important; color: #35160d !important;
    font-size: 2rem; line-height: 1.05; text-align: center; letter-spacing: 2px;
    text-shadow: none !important; margin: 5px 0 21px 0;
}
.book-ink { opacity: 0; animation: inkAppear .55s ease both; }
@keyframes inkAppear { from { opacity: 0; filter: blur(3px); } to { opacity: 1; filter: blur(0); } }
.book-lines { display: flex; flex-direction: column; gap: 12px; }
.book-line {
    display: flex; justify-content: space-between; align-items: baseline; gap: 18px;
    border-bottom: 1px solid rgba(93,57,24,.28); padding: 0 1px 7px 1px;
    opacity: 0; clip-path: inset(0 100% 0 0); transform: translateY(5px);
    animation: inkWrite .62s steps(16,end) both;
}
@keyframes inkWrite {
    0% { opacity: 0; clip-path: inset(0 100% 0 0); transform: translateY(5px); }
    18% { opacity: 1; }
    90%, 100% { opacity: 1; clip-path: inset(0 0 0 0); transform: translateY(0); }
}
.book-line span {
    font-family: 'Special Elite', monospace; font-size: .74rem; letter-spacing: 1.1px;
    text-transform: uppercase; color: #704c26 !important; white-space: nowrap;
}
.book-line b { font-family: Georgia, serif; font-size: 1rem; color: #211006; text-align: right; transform: rotate(-.35deg); }
.book-oracle-note {
    margin-top: 31px; border: 1px solid rgba(93,57,24,.36); background: rgba(101,62,24,.09);
    padding: 17px 18px; color: #321b0d; font-family: 'Special Elite', monospace;
    font-size: .90rem; line-height: 1.5; transform: rotate(-.7deg);
    box-shadow: 0 8px 18px rgba(73,43,13,.12); opacity: 0;
    animation: noteAppear .65s ease 4.02s both;
}
.book-oracle-note b { display: block; color: #650d0d; font-family: Georgia, serif; font-size: 1.02rem; margin-bottom: 7px; }
@keyframes noteAppear { from { opacity: 0; transform: translateY(9px) rotate(-.7deg); } to { opacity: 1; transform: translateY(0) rotate(-.7deg); } }
.fate-visual { position: relative; height: 219px; margin-top: 13px; opacity: 0; animation: inkAppear .45s ease 3.42s both; }
.fate-visual svg { width: 100%; height: 100%; display: block; overflow: visible; }
.meter-svg { width:100%; height:100%; display:block; overflow:visible; }
.meter-title-svg { font-family:'Creepster',Georgia,serif; font-size:18px; letter-spacing:3px; fill:#8b4c11; }
.meter-track { fill:none; stroke:url(#churnZones); stroke-width:25; stroke-linecap:butt; }
.meter-progress { fill:none; stroke:#c27b1a; stroke-width:8; stroke-linecap:round; stroke-dashoffset:100; animation:meterSweep .9s ease 3.66s forwards; }
@keyframes meterSweep { to { stroke-dashoffset:0; } }
.meter-tick { stroke:#6e5337; stroke-width:1.5; }
.meter-tick-label { font:10px Georgia,serif; fill:#6c543a; }
.meter-threshold { stroke:#d43b28; stroke-width:3.2; }
.meter-needle { fill:#fff1cf; stroke:#492818; stroke-width:2; filter:drop-shadow(0 1px 2px #27170f88); }
.meter-number { font:bold 30px 'Creepster',Georgia,serif; fill:#311b10; paint-order:stroke; stroke:#f0dfb8; stroke-width:2px; }
.fate-verdict {
    text-align: center; font-family: 'Creepster', Georgia, serif; font-size: 1.48rem;
    letter-spacing: 1.6px; line-height: 1.1; margin-top: 1px; opacity: 0;
    animation: inkAppear .6s ease 4.34s both;
}
.fate-verdict.safe { color: #216b37; }
.fate-verdict.doom { color: #76100d; }
@media (max-width: 820px) {
    .death-book-stage { overflow-x: auto; padding-bottom: 38px; }
    .death-book { width: 760px; height: 625px; }
    .book-page { padding-left: 30px; padding-right: 30px; }
    .death-cover-title { font-size: 3.2rem; }
}
@media (prefers-reduced-motion: reduce) {
    .death-book, .death-cover, .turn-page, .book-cover-back, .book-page-left,
    .book-ink, .book-line, .book-oracle-note, .fate-visual, .fate-verdict,
    .meter-progress { animation-duration: .01s !important; animation-delay: 0s !important; }
    .death-cover, .turn-page { display: none !important; }
    .book-cover-back, .book-page-left, .book-ink, .book-line, .book-oracle-note,
    .fate-visual, .fate-verdict { opacity: 1 !important; clip-path: none !important; }
    .meter-progress { stroke-dashoffset: 0 !important; }
}
'''

# ---------------------------------------------------------------------
# Keyed-container helpers: st.container(key=...) gives a CSS class
# (st-key-<key>) used to dock the spider (top-left) & ghost (bottom-right).
# Needs Streamlit >= ~1.36; older versions fall back gracefully.
# ---------------------------------------------------------------------
def _keyed_box(key):
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()

def _scroll_box(height=250):
    try:
        return st.container(height=height)
    except TypeError:
        return st.container()

# ---------------------------------------------------------------------
# Ghost SVG builder (pupils have IDs so JS can move them)
# ---------------------------------------------------------------------
def ghost_svg(width, pupil_prefix):
    # NOTE: returned as ONE line on purpose — multi-line indented HTML inside
    # st.markdown can be misread as a Markdown code block and shown as text.
    return (
        f'<svg width="{width}" viewBox="0 0 100 120" xmlns="http://www.w3.org/2000/svg">'
        '<ellipse cx="14" cy="72" rx="10" ry="6" fill="#EDE9FF" transform="rotate(-24 14 72)"/>'
        '<ellipse cx="86" cy="72" rx="10" ry="6" fill="#EDE9FF" transform="rotate(24 86 72)"/>'
        '<path d="M50 5 C25 5 12 28 12 55 L12 112 L24 100 L33 112 L42 100 L50 112 '
        'L58 100 L67 112 L76 100 L88 112 L88 55 C88 28 75 5 50 5 Z" '
        'fill="#F5F3FF" stroke="#C9B8FF" stroke-width="1.5"/>'
        '<ellipse cx="35" cy="50" rx="9" ry="12" fill="#FFFFFF" stroke="#1A0B2E" stroke-width="1.6"/>'
        '<ellipse cx="65" cy="50" rx="9" ry="12" fill="#FFFFFF" stroke="#1A0B2E" stroke-width="1.6"/>'
        f'<circle id="{pupil_prefix}pupil-l" class="pupil" cx="35" cy="52" r="4.2" fill="#1A0B2E"/>'
        f'<circle id="{pupil_prefix}pupil-r" class="pupil" cx="65" cy="52" r="4.2" fill="#1A0B2E"/>'
        '<ellipse cx="50" cy="72" rx="6" ry="8" fill="#1A0B2E"/>'
        '<circle cx="24" cy="66" r="5" fill="#FFB6C1" opacity="0.75"/>'
        '<circle cx="76" cy="66" r="5" fill="#FFB6C1" opacity="0.75"/>'
        '</svg>'
    )

# ---------------------------------------------------------------------
# Ambient decor: moon + bats + fog + rotating tantra/occult mandala
# ---------------------------------------------------------------------
def render_ambient():
    mandala_svg = """
    <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
      <circle cx="100" cy="100" r="96" fill="none" stroke="#FF8C1A" stroke-width="1.2"/>
      <circle cx="100" cy="100" r="86" fill="none" stroke="#B388FF" stroke-width="0.8" stroke-dasharray="4 4"/>
      <circle cx="100" cy="100" r="58" fill="none" stroke="#FF8C1A" stroke-width="0.8"/>
      <polygon points="100,14 120,76 186,76 132,114 152,178 100,138 48,178 68,114 14,76 80,76"
               fill="none" stroke="#FF6B1A" stroke-width="1.4"/>
      <polygon points="100,44 143,79 127,132 73,132 57,79" fill="none" stroke="#B388FF" stroke-width="1"/>
      <circle cx="100" cy="14" r="4" fill="#FF8C1A"/><circle cx="186" cy="76" r="4" fill="#B388FF"/>
      <circle cx="152" cy="178" r="4" fill="#FF8C1A"/><circle cx="48" cy="178" r="4" fill="#B388FF"/>
      <circle cx="14" cy="76" r="4" fill="#FF8C1A"/>
      <text x="100" y="104" text-anchor="middle" font-size="15" fill="#FFCC99">ॐ ☽ ✦ ☾</text>
    </svg>
    """
    st.markdown(f"""
    <div class="mandala">{mandala_svg}</div>
    <div class="moon">🌕</div>
    <div class="bat">🦇</div><div class="bat bat2">🦇</div><div class="bat bat3">🦇</div>
    <div class="fog fog-a"></div><div class="fog fog-b"></div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------
# JS injection (via a 0-height component):
#  - makes ghost PUPILS follow the cursor anywhere on the page
#  - makes the gate NO button flee BEFORE the cursor can reach it
# ---------------------------------------------------------------------
def inject_haunted_js():
    components.html("""
    <script>
    try {
      const doc = window.parent.document;
      const win = window.parent;
      if (!win.__hauntedInit) {
        win.__hauntedInit = true;
        win.__noScale = 1;
        const taunts = ["NO... NEVER! ☠", "Too slow, mortal 👻", "The spirits forbid it!",
                        "Run while you can...", "He he he... YES is fate", "You cannot escape 🕸️", "👻💨"];

        win.__fleeNo = function(no) {
          const stage = no.parentElement;
          if (!stage) return;
          const maxX = Math.max(stage.clientWidth - no.offsetWidth - 12, 10);
          const maxY = Math.max(stage.clientHeight - no.offsetHeight - 12, 10);
          no.style.left = (6 + Math.random() * maxX) + "px";
          no.style.top  = (6 + Math.random() * maxY) + "px";
          win.__noScale = Math.max(win.__noScale * 0.92, 0.55);
          no.style.transform = "rotate(" + (Math.random() * 24 - 12) + "deg) scale(" + win.__noScale + ")";
          no.textContent = taunts[Math.floor(Math.random() * taunts.length)];
        };

        win.addEventListener("mousemove", function(e) {
          // 👀 pupils follow cursor
          ["pupil-l", "pupil-r", "gpupil-l", "gpupil-r"].forEach(function(id) {
            const p = doc.getElementById(id);
            if (!p) return;
            p.style.animation = "none";
            const r = p.getBoundingClientRect();
            const dx = e.clientX - (r.left + r.width / 2);
            const dy = e.clientY - (r.top + r.height / 2);
            const a = Math.atan2(dy, dx);
            const m = id.charAt(0) === "g" ? 5 : 3.6;
            p.style.transform = "translate(" + (Math.cos(a) * m) + "px," + (Math.sin(a) * m) + "px)";
          });
          // 🏃 NO button flees when cursor gets within 115px
          const no = doc.getElementById("runaway-no");
          if (no) {
            const r = no.getBoundingClientRect();
            const d = Math.hypot(e.clientX - (r.left + r.width / 2), e.clientY - (r.top + r.height / 2));
            if (d < 115) win.__fleeNo(no);
          }
        });

        // NO can never be clicked / tapped / tabbed-to either
        doc.addEventListener("click", function(e) {
          if (e.target && e.target.id === "runaway-no") { e.preventDefault(); e.stopPropagation(); win.__fleeNo(e.target); }
        }, true);
        doc.addEventListener("touchstart", function(e) {
          if (e.target && e.target.id === "runaway-no") { e.preventDefault(); win.__fleeNo(e.target); }
        }, true);
        doc.addEventListener("focusin", function(e) {
          if (e.target && e.target.id === "runaway-no") { e.target.blur(); win.__fleeNo(e.target); }
        }, true);

        // 🏰 click/tap anywhere to skip the entry castle cinematic
        doc.addEventListener("click", function(e) {
          const s = (e.target && e.target.closest) ? e.target.closest(".castle-scene, .gothic-scene") : null;
          if (s) { s.style.display = "none"; }
        }, true);
      }
    } catch (err) { /* if JS injection is blocked, CSS fallbacks still work */ }
    </script>
    """, height=0)

# ---------------------------------------------------------------------
# 🔥 Huddy Buddy jumpscare (churn probability >= 50%)
# ---------------------------------------------------------------------
def hell_effect():
    flames = "🔥" * 18
    st.markdown(f"""
    <div class="hell-overlay">
        <div class="hell-ghost">👻</div>
        <div class="hell-text">HUDDY BUDDY GHOST WANTS TO<br>TAKE YOU TO HELL!</div>
        <div class="flames">{flames}</div>
    </div>
    """, unsafe_allow_html=True)

def gothic_scene_svg():
    # Purple scary castle under a blood-red eclipse moon: layered
    # ridges, a rocky crag, right-to-left drifting clouds, mist,
    # flickering windows and foreground pines. Runtime HTML is one line.
    rand = random.Random(42)
    stars = ''.join(
        f'<circle cx="{rand.randint(15, 1585)}" cy="{rand.randint(18, 330)}" '
        f'r="{rand.choice([1, 1.3, 1.7, 2.2])}" fill="#f3eaff" opacity="{rand.uniform(.22, .82):.2f}"/>'
        for _ in range(92)
    )
    cloud_specs = [
        (92, 1.18, .58, 25, -7.0, .82), (154, .92, .48, 31, -17.0, .94),
        (222, 1.38, .64, 21, -13.0, .76), (66, .64, .34, 39, -25.0, .62),
        (292, .72, .38, 35, -9.0, .70),
    ]
    clouds = ''.join(
        f'<g transform="translate(1650,{y}) scale({sx},{sy})" opacity="{op}">'
        f'<g class="drift" style="animation-duration:{dur}s;animation-delay:{delay}s">'
        '<use href="#realCloud" filter="url(#softBlur)"/></g></g>'
        for y, sx, sy, dur, delay, op in cloud_specs
    )
    battlements = ''.join(
        f'<rect x="{x}" y="289" width="13" height="15" fill="#211832"/>'
        for x in range(724, 897, 24)
    ) + ''.join(
        f'<rect x="{x}" y="333" width="11" height="12" fill="#1b1429"/>'
        for x in range(666, 980, 27)
    )
    win_positions = [
        (808, 238), (826, 272), (797, 318), (838, 348), (752, 336), (866, 318),
        (697, 286), (714, 352), (905, 282), (924, 344), (645, 342), (963, 336),
        (776, 389), (856, 405), (735, 414), (891, 421),
    ]
    windows = ''.join(
        f'<path d="M{x} {y + 11} V{y + 4} Q{x + 4} {y} {x + 8} {y + 4} V{y + 11} Z" '
        f'fill="#ffb04a" opacity="{.58 + (i % 4) * .11:.2f}"/>'
        for i, (x, y) in enumerate(win_positions)
    )
    pines = []
    for x, h in [(42, 96), (92, 72), (145, 116), (216, 78), (1188, 84), (1248, 122),
                 (1320, 76), (1390, 108), (1460, 82), (1528, 118)]:
        pines.append(
            f'<g transform="translate({x},806)"><rect x="-4" y="-15" width="8" height="28" fill="#05030a"/>'
            f'<path d="M0 {-h} L28 -42 L13 -42 L34 -8 L-34 -8 L-13 -42 L-28 -42 Z" fill="#070410"/></g>'
        )
    parts = [
        '<svg class="scene-svg" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><defs>',
        '<linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#03020a"/><stop offset="34%" stop-color="#150826"/><stop offset="66%" stop-color="#2a1150"/><stop offset="100%" stop-color="#3d1a66"/></linearGradient>',
        '<radialGradient id="moonGlowGrad" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#ffd0b8" stop-opacity=".82"/><stop offset="55%" stop-color="#ff7a52" stop-opacity=".30"/><stop offset="100%" stop-color="#ff7a52" stop-opacity="0"/></radialGradient>',
        '<clipPath id="moonClip"><circle cx="1292" cy="168" r="84"/></clipPath>',
        '<linearGradient id="farRidge" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#51306f"/><stop offset="100%" stop-color="#2b1747"/></linearGradient>',
        '<linearGradient id="nearRidge" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#27113e"/><stop offset="100%" stop-color="#0d0620"/></linearGradient>',
        '<linearGradient id="castleWall" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#3a2c4c"/><stop offset="52%" stop-color="#1d152d"/><stop offset="100%" stop-color="#090612"/></linearGradient>',
        '<linearGradient id="castleRoof" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#251a3d"/><stop offset="100%" stop-color="#070410"/></linearGradient>',
        '<linearGradient id="cragGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#2c1c44"/><stop offset="55%" stop-color="#160b2a"/><stop offset="100%" stop-color="#05030d"/></linearGradient>',
        '<radialGradient id="mistGrad" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#eee7ff" stop-opacity=".52"/><stop offset="68%" stop-color="#c4aef5" stop-opacity=".18"/><stop offset="100%" stop-color="#c4aef5" stop-opacity="0"/></radialGradient>',
        '<radialGradient id="vignetteGrad" cx="50%" cy="45%" r="72%"><stop offset="56%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".42"/></radialGradient>',
        '<pattern id="castleStone" width="27" height="19" patternUnits="userSpaceOnUse"><rect x="1" y="2" width="15" height="7" rx="2" fill="#4a3862" opacity=".52"/><rect x="18" y="1" width="12" height="8" rx="2" fill="#38294e" opacity=".48"/><rect x="7" y="11" width="16" height="7" rx="2" fill="#433158" opacity=".44"/></pattern>',
        '<filter id="softBlur" x="-12%" y="-35%" width="124%" height="170%"><feGaussianBlur stdDeviation="4.2"/></filter>',
        '<path id="realCloud" d="M18 62 C60 30 120 22 175 34 C215 12 290 10 335 28 C395 16 465 26 500 52 C520 66 505 82 460 84 L70 86 C28 86 2 78 18 62 Z" fill="#1c0b30" stroke="#9d6bff" stroke-width="5" stroke-linejoin="round"/>',
        '</defs><rect width="1600" height="900" fill="url(#skyGrad)"/>', stars,
        '<circle class="moon-glow" cx="1292" cy="168" r="205" fill="url(#moonGlowGrad)"/><circle class="moon-core" cx="1292" cy="168" r="84" fill="#e83a24"/><g clip-path="url(#moonClip)"><g fill="#a3160f" opacity=".35"><circle cx="1322" cy="142" r="15"/><circle cx="1298" cy="188" r="9"/><circle cx="1340" cy="190" r="7"/></g><circle cx="1248" cy="145" r="79" fill="#0d0618" opacity=".88"/></g>',
        clouds,
        '<path class="sway-a" fill="url(#farRidge)" opacity=".94" d="M-30 628 L105 548 L180 594 L286 500 L372 578 L470 522 L590 610 L705 540 L810 606 L935 522 L1044 590 L1166 506 L1260 572 L1378 520 L1484 592 L1630 538 L1630 920 L-30 920 Z"/>',
        '<path fill="#e9dcff" opacity=".13" d="M286 500 L326 540 L292 536 L258 548 Z M935 522 L972 556 L940 552 L910 564 Z M1166 506 L1200 540 L1170 536 L1142 548 Z"/>',
        '<g class="mist-drift-a"><ellipse cx="360" cy="604" rx="520" ry="58" fill="url(#mistGrad)"/><ellipse cx="1220" cy="610" rx="500" ry="52" fill="url(#mistGrad)"/></g>',
        '<path class="sway-b" fill="url(#nearRidge)" d="M-30 760 C115 676 205 650 330 684 C465 720 570 758 740 716 C900 676 1010 632 1160 676 C1310 720 1450 764 1630 712 L1630 920 L-30 920 Z"/>',
        '<path fill="url(#cragGrad)" d="M455 900 C545 775 606 646 650 522 L676 472 L962 472 L995 544 C1048 656 1102 790 1190 900 Z"/>',
        '<path fill="none" stroke="rgba(192,154,255,.24)" stroke-width="4" d="M686 486 C720 590 700 700 620 828 M956 490 C1005 590 1050 710 1120 842 M812 500 C790 620 820 740 900 865"/>',
        '<path fill="none" stroke="rgba(0,0,0,.36)" stroke-width="7" d="M646 540 L716 620 L680 724 M986 552 L922 642 L968 758 M788 528 L842 626 L806 748"/>',
        '<g stroke="rgba(210,180,255,.34)" stroke-width="1.6">',
        '<path fill="url(#castleWall)" d="M724 474 V300 H906 V474 Z"/><path fill="url(#castleStone)" opacity=".34" d="M724 474 V300 H906 V474 Z"/>',
        '<path fill="url(#castleWall)" d="M782 474 V206 H854 V474 Z"/><path fill="url(#castleStone)" opacity=".30" d="M782 474 V206 H854 V474 Z"/>',
        '<path fill="url(#castleWall)" d="M678 474 V244 H738 V474 Z"/><path fill="url(#castleWall)" d="M884 474 V234 H948 V474 Z"/>',
        '<path fill="url(#castleWall)" d="M632 474 V304 H674 V474 Z"/><path fill="url(#castleWall)" d="M950 474 V294 H992 V474 Z"/>',
        '<path fill="#171126" d="M650 474 L676 430 L724 474 Z M906 474 L946 426 L986 474 Z M724 474 L782 420 L854 474 Z"/>',
        '</g>',
        '<g fill="url(#castleRoof)" stroke="rgba(216,180,255,.38)" stroke-width="1.7"><path d="M774 210 L818 112 L862 210 Z"/><path d="M672 248 L708 158 L744 248 Z"/><path d="M878 238 L916 146 L954 238 Z"/><path d="M626 308 L653 238 L680 308 Z"/><path d="M944 298 L971 228 L998 298 Z"/></g>',
        '<g stroke="#0a0614" stroke-width="3"><line x1="818" y1="112" x2="818" y2="90"/><line x1="708" y1="158" x2="708" y2="140"/><line x1="916" y1="146" x2="916" y2="128"/><line x1="653" y1="238" x2="653" y2="224"/><line x1="971" y1="228" x2="971" y2="214"/></g>',
        '<path d="M818 91 L842 99 L818 108 Z" fill="#7a1020"/><path d="M916 129 L936 136 L916 144 Z" fill="#5d0d20"/>',
        battlements,
        '<path d="M796 474 V424 Q818 398 840 424 V474 Z" fill="#05030a" stroke="rgba(216,180,255,.35)"/><path d="M806 474 V430 Q818 414 830 430 V474" fill="none" stroke="#ff9a3c" stroke-width="2" opacity=".55"/>',
        '<g class="win-flicker">', windows, '</g>',
        '<path d="M724 474 H992" stroke="#05030a" stroke-width="12"/><path fill="#080512" d="M600 486 C665 458 960 458 1030 486 C960 510 665 510 600 486 Z"/>',
        '<path fill="none" stroke="#77609a" stroke-width="5" stroke-linecap="round" stroke-dasharray="13 10" opacity=".58" d="M818 492 C780 565 850 620 790 690 C735 754 800 820 860 884"/>',
        '<g class="mist-drift-b"><ellipse cx="735" cy="512" rx="330" ry="48" fill="url(#mistGrad)"/><ellipse cx="1030" cy="535" rx="275" ry="38" fill="url(#mistGrad)"/></g>',
        '<path fill="#05030a" opacity=".94" d="M0 802 C250 772 510 820 820 792 C1130 766 1390 816 1600 786 L1600 900 L0 900 Z"/>',
        ''.join(pines),
        '<path d="M74 826 C82 746 68 704 38 650 M76 748 C112 716 140 716 172 682 M72 780 C42 744 20 738 -6 706 M82 700 C104 682 116 662 118 634" fill="none" stroke="#030208" stroke-width="13" stroke-linecap="round"/>',
        '<path d="M1518 830 C1510 754 1528 706 1564 654 M1514 756 C1478 722 1448 720 1418 686 M1522 786 C1550 750 1576 742 1604 716" fill="none" stroke="#030208" stroke-width="12" stroke-linecap="round"/>',
        '<g class="mist-drift-a"><ellipse cx="300" cy="826" rx="560" ry="68" fill="url(#mistGrad)"/><ellipse cx="1170" cy="842" rx="610" ry="62" fill="url(#mistGrad)"/></g>',
        '<rect width="1600" height="900" fill="url(#vignetteGrad)"/></svg>',
    ]
    return ''.join(parts)

def _mini_spider_svg():
    return ('<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
            '<path class="spider-legs" d="M37 47 L16 31 L5 40 M34 57 L10 52 L1 62 M36 68 L15 76 L8 89 M41 76 L27 88 L23 97 M63 47 L84 31 L95 40 M66 57 L90 52 L99 62 M64 68 L85 76 L92 89 M59 76 L73 88 L77 97" stroke="#12081f" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            '<ellipse cx="50" cy="61" rx="20" ry="25" fill="#17101f" stroke="#9d6bff" stroke-width="2"/>'
            '<path d="M50 47 L56 60 L50 73 L44 60 Z" fill="#ff6b1a" opacity=".94"/>'
            '<circle cx="50" cy="36" r="13" fill="#12081f" stroke="#9d6bff" stroke-width="2"/>'
            '<circle cx="45.5" cy="34" r="2.4" fill="#ff3b1f"/><circle cx="54.5" cy="34" r="2.4" fill="#ff3b1f"/>'
            '<circle cx="41.5" cy="38.5" r="1.4" fill="#ff3b1f"/><circle cx="58.5" cy="38.5" r="1.4" fill="#ff3b1f"/>'
            '<path d="M45 45 L48 51 L50 45 L52 51 L55 45" stroke="#fff3e0" stroke-width="1.7" fill="none" stroke-linejoin="round"/></svg>')

def _entry_spiders_html():
    # 20 spiders distributed across the screen: 8 tiny, 7 medium,
    # 5 huge. They fall on silk threads and finish before 3.8s.
    sizes = ([random.randint(20, 34) for _ in range(8)]
             + [random.randint(40, 64) for _ in range(7)]
             + [random.randint(78, 112) for _ in range(5)])
    random.shuffle(sizes)
    spider = _mini_spider_svg()
    parts = []
    for i, size in enumerate(sizes):
        left = 3 + (94 * i / max(1, len(sizes) - 1)) + random.uniform(-1.5, 1.5)
        delay = random.uniform(0.05, 0.80)
        duration = random.uniform(1.65, 2.70)
        if delay + duration > 3.55:
            duration = 3.55 - delay
        drop = random.uniform(26, 84)
        swing = random.uniform(0.90, 1.45)
        z = 9 if size >= 78 else (7 if size >= 40 else 6)
        parts.append(
            f'<span class="entry-spider" style="left:{left:.1f}%;--size:{size}px;'
            f'--drop:{drop:.1f}vh;animation-delay:{delay:.2f}s;'
            f'animation-duration:{duration:.2f}s;z-index:{z}">'
            f'<span class="entry-spider-body" style="animation-duration:{swing:.2f}s">{spider}</span></span>'
        )
    return '<div class="entry-spider-layer">' + ''.join(parts) + '</div>'

def entry_gothic_scene():
    # 3.8-second cinematic: purple castle, spiderfall, and — right at
    # the end — the oracle's line rises through the mist. (Clicking
    # still skips it, but the noisy "skip" hint text is gone.)
    st.markdown(
        '<div class="gothic-scene">' + gothic_scene_svg()
        + _entry_spiders_html()
        + '<div class="gothic-caption"><span>Through the mist. Beyond the gates.</span>'
          '<span>The oracle can see which customers won’t return.</span></div></div>',
        unsafe_allow_html=True,
    )

def _book_line(label, value, delay):
    return (
        f'<div class="book-line" style="animation-delay:{delay:.2f}s">'
        f'<span>{label}</span><b>{value}</b></div>'
    )

def _fate_visual_html(prediction, probability):
    """Render the original semicircular churn meter inside the open book."""
    value = max(0.0, min(100.0, float(probability) * 100))
    is_churn = value >= 50
    cx, cy, radius = 160, 184, 120
    angle = math.pi * (1 - value / 100)
    px = cx + radius * math.cos(angle)
    py = cy - radius * math.sin(angle)
    ticks = []
    for tick in (0, 25, 50, 75, 100):
        theta = math.pi * (1 - tick / 100)
        x1, y1 = cx + 105 * math.cos(theta), cy - 105 * math.sin(theta)
        x2, y2 = cx + 121 * math.cos(theta), cy - 121 * math.sin(theta)
        tx, ty = cx + 139 * math.cos(theta), cy - 139 * math.sin(theta) + 4
        ticks.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="meter-tick"/>'
            f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" class="meter-tick-label">{tick}</text>'
        )
    svg = (
        '<svg class="meter-svg" viewBox="0 0 320 235" role="img" '
        f'aria-label="Churn meter: {value:.1f} percent">'
        '<defs><linearGradient id="churnZones" x1="40" y1="0" x2="280" y2="0" gradientUnits="userSpaceOnUse">'
        '<stop offset="0%" stop-color="#2e6b28"/><stop offset="30%" stop-color="#2e6b28"/>'
        '<stop offset="30%" stop-color="#a87522"/><stop offset="50%" stop-color="#a87522"/>'
        '<stop offset="50%" stop-color="#a33b1b"/><stop offset="75%" stop-color="#a33b1b"/>'
        '<stop offset="75%" stop-color="#68141a"/><stop offset="100%" stop-color="#68141a"/>'
        '</linearGradient></defs>'
        '<text x="160" y="24" text-anchor="middle" class="meter-title-svg">CHURN METER</text>'
        '<path d="M40 184 A120 120 0 0 1 280 184" class="meter-track"/>'
        '<path d="M40 184 A120 120 0 0 1 280 184" pathLength="100" class="meter-progress" '
        f'stroke="{"#d92c20" if is_churn else "#c27b1a"}" stroke-dasharray="{value:.2f} 100"/>'
        + ''.join(ticks) +
        '<line x1="160" y1="47" x2="160" y2="72" class="meter-threshold"/>'
        f'<circle cx="{px:.1f}" cy="{py:.1f}" r="6" class="meter-needle"/>'
        f'<text x="160" y="176" text-anchor="middle" class="meter-number">{value:.1f}%</text>'
        '</svg>'
    )
    if prediction == 0:
        return ('<div class="fate-visual">' + svg + '</div>'
                + '<div class="fate-verdict safe">SAFE — THE SOUL STAYS</div>')
    return ('<div class="fate-visual">' + svg + '</div>'
            + '<div class="fate-verdict doom">CHURN — THE SOUL DEPARTS</div>')

def death_note_result(prediction, probability, credit_score, age, gender,
                      geography, tenure, balance, estimated_salary,
                      num_products, has_card, is_active,
                      recommendation_title, recommendation, run_id=1):
    # Left and right record lines share the same delay for each row, so
    # the invisible hand writes on both open pages at the same time.
    left_rows = [
        ('Credit Score', f'{credit_score}'),
        ('Age', f'{age} years'),
        ('Gender', gender),
        ('Geography', geography),
        ('Years with Bank', f'{tenure} years'),
    ]
    right_rows = [
        ('Balance', f'${balance:,.2f}'),
        ('Estimated Salary', f'${estimated_salary:,.2f}'),
        ('Bank Services', f'{num_products} held'),
        ('Credit Card', has_card),
        ('Active Member', is_active),
    ]
    left_lines = ''.join(_book_line(label, value, 2.96 + i * 0.17)
                         for i, (label, value) in enumerate(left_rows))
    right_lines = ''.join(_book_line(label, value, 2.96 + i * 0.17)
                          for i, (label, value) in enumerate(right_rows))
    symbols = ['☠', '♰', '☾', '✦', '♱']
    # 📜 Peek-a-page: the turning pages are NOT blank — like any old
    # notebook, they are already filled with earlier souls' records.
    # You only glimpse them for a heartbeat as each page flips past.
    peek_pages = [
        ("OLD ENTRIES · 1897", [
            ("Soul 041 — R. Alvarez", "Credit 512", "doom", "LEFT ☠"),
            ("Soul 042 — E. Laurent", "Balance $0", "doom", "LEFT ☠"),
            ("Soul 043 — M. Schmidt", "2 services", "safe", "STAYED ✦"),
            ("Soul 044 — A. Laurent", "Silent 3 yrs", "doom", "LEFT ☠"),
        ], "…the ink never lies."),
        ("THE VANISHED · 1903", [
            ("<s>J. Moreau</s>", "Age 61", "doom", "GONE"),
            ("<s>K. Weber</s>", "4 products", "doom", "GONE"),
            ("L. Petit", "Active member", "safe", "REMAINS"),
            ("<s>H. Braun</s>", "Credit 480", "doom", "GONE"),
        ], "crossed out, every one."),
        ("KEPT SOULS · 1911", [
            ("C. Laurent", "Balance $82k", "safe", "STAYED ✦"),
            ("F. Dubois", "Loyal 9 yrs", "safe", "STAYED ✦"),
            ("O. Silva", "Credit 731", "safe", "STAYED ✦"),
            ("N. Khan", "Silent 1 yr", "doom", "LEFT ☠"),
        ], "not all pages are dark."),
        ("DOOMED LEDGER · 1924", [
            ("Soul 512 — P. Gerard", "Germany", "doom", "LEFT ☠"),
            ("Soul 513 — S. Roux", "No card", "doom", "LEFT ☠"),
            ("Soul 514 — D. Meyer", "Age 58", "doom", "LEFT ☠"),
            ("Soul 515 — I. Fontaine", "Active", "safe", "REMAINS"),
        ], "the graveyard filled fast."),
        ("LAST WEEK'S SOULS", [
            ("Soul 998 — ???", "Credit 640", "safe", "STAYED ✦"),
            ("Soul 999 — ???", "Balance $120k", "doom", "LEFT ☠"),
            ("Soul 1000 — ???", "Too quiet…", "doom", "LEFT ☠"),
            ("Soul 1001 — YOU?", "summoning…", "doom", "?"),
        ], "one blank line remains…"),
    ]
    def _peek_html(head, rows, foot):
        body = ''.join(
            f'<div class="peek-row"><span>{n}</span><span>{d}</span>'
            f'<b class="{c}">{v}</b></div>' for n, d, c, v in rows)
        return (f'<div class="turn-peek"><div class="peek-head">{head}</div>'
                f'{body}<div class="peek-foot">{foot}</div></div>')
    turn_pages = ''.join(
        f'<div class="turn-page" style="z-index:{24 - i};animation-delay:{1.32 + i * 0.23:.2f}s">'
        + _peek_html(*peek_pages[i])
        + f'<span>{symbols[i]}</span></div>'
        for i in range(5)
    )
    html = (
        f'<div class="death-book-stage" id="death-book-anchor-{run_id}" data-prediction-run="{run_id}"><div class="death-book-glow"></div>'
        '<div class="death-book" role="img" aria-label="An old black Death Note opens and writes the prediction">'
        '<div class="book-cover-back"></div>'
        '<section class="book-page book-page-left">'
        '<h3 class="book-ink" style="animation-delay:2.86s">THE SOUL&apos;S RECORD</h3>'
        '<div class="book-lines">' + left_lines + '</div>'
        '<div class="book-oracle-note"><b>' + recommendation_title + '</b>' + recommendation + '</div>'
        '</section>'
        '<section class="book-page book-page-right">'
        '<div class="book-kicker book-ink" style="animation-delay:2.82s">The page has spoken</div>'
        '<h3 class="book-ink" style="animation-delay:2.86s">THE FINAL FATE</h3>'
        '<div class="book-lines">' + right_lines + '</div>'
        + _fate_visual_html(prediction, probability) +
        '</section><div class="book-spine"></div>' + turn_pages +
        '<div class="death-cover"><div class="death-cover-skull">☠</div>'
        '<div class="death-cover-title">DEATH<br>NOTE</div>'
        '<div class="death-cover-sub">THE BOOK OF FATES</div></div>'
        '<div class="death-book-shadow"></div></div></div>'
    )
    # A parent-page anchor lets the embedded book scroll itself into view.
    st.markdown(
        f'<div id="death-book-parent-anchor-{run_id}" '
        f'data-death-book-run="{run_id}"></div>',
        unsafe_allow_html=True,
    )
    _scroll_script = (
        '<script>(function(){'
        'function bringBookIntoView(){try{'
        'var parentDoc=window.parent.document;'
        f'var runId="{run_id}";'
        'var anchor=parentDoc.getElementById("death-book-parent-anchor-"+runId);'
        'var target=anchor||window.frameElement;'
        'if(target&&target.scrollIntoView){target.scrollIntoView({behavior:"smooth",block:"center"});}'
        '}catch(e){}}'
        'setTimeout(bringBookIntoView,180);setTimeout(bringBookIntoView,650);'
        '})();</script>'
    )
    _component_html = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<!-- Death Note prediction run {run_id}: this changes on every '
        'Summon click, forcing a fresh book and a fresh opening animation. -->'
        '<style>@import url("https://fonts.googleapis.com/css2?family=Creepster&family=Special+Elite&display=swap");'
        'html,body{margin:0;padding:0;background:transparent;overflow:hidden;font-family:Georgia,serif;}'
        + DEATH_BOOK_CSS +
        '.death-book-stage{margin:0 auto;}</style></head><body>'
        + html + _scroll_script + '</body></html>'
    )
    components.html(_component_html, height=704, scrolling=False)

def laughing_pumpkin_svg(uid, delay=0.0, flip=False):
    # A jack-o'-lantern that bounces/squashes while its triangular eyes
    # flare and its jagged mouth chatters open and closed.
    flip_attr = ' transform="translate(110 0) scale(-1 1)"' if flip else ''
    return (
        f'<span class="laughing-pumpkin" style="animation-delay:-{delay:.2f}s">'
        f'<svg viewBox="0 0 110 104" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
        f'<defs><radialGradient id="pumpkinBody{uid}" cx="40%" cy="28%" r="78%">'
        '<stop offset="0%" stop-color="#ffb347"/><stop offset="52%" stop-color="#ff7a1a"/>'
        '<stop offset="100%" stop-color="#b34700"/></radialGradient>'
        f'<radialGradient id="pumpkinGlow{uid}" cx="50%" cy="55%" r="55%">'
        '<stop offset="0%" stop-color="#fff7ae"/><stop offset="55%" stop-color="#ffd23f"/>'
        '<stop offset="100%" stop-color="#ff7a1a"/></radialGradient></defs>'
        f'<text class="pumpkin-ha" style="animation-delay:-{delay:.2f}s" x="2" y="17">HA!</text>'
        f'<text class="pumpkin-ha two" style="animation-delay:-{delay + 0.35:.2f}s" x="83" y="27">HA!</text>'
        f'<g{flip_attr}>'
        '<path d="M55 22 C52 12 57 5 68 3 C66 12 64 18 60 23 Z" fill="#315c24"/>'
        '<path d="M61 15 C73 5 86 7 91 10 C84 19 71 21 61 15 Z" fill="#3f7a2d"/>'
        f'<ellipse cx="32" cy="62" rx="25" ry="34" fill="url(#pumpkinBody{uid})"/>'
        f'<ellipse cx="78" cy="62" rx="25" ry="34" fill="url(#pumpkinBody{uid})"/>'
        f'<ellipse cx="55" cy="62" rx="34" ry="37" fill="url(#pumpkinBody{uid})"/>'
        '<path d="M35 30 C27 49 27 75 35 94 M75 30 C83 49 83 75 75 94 M46 27 C40 49 40 76 46 97 M64 27 C70 49 70 76 64 97" fill="none" stroke="rgba(122,45,0,.34)" stroke-width="2.4"/>'
        f'<g class="pumpkin-eye" style="animation-delay:-{delay:.2f}s">'
        f'<path d="M29 55 L43 40 L49 58 C42 52 35 51 29 55 Z" fill="url(#pumpkinGlow{uid})"/>'
        f'<path d="M81 55 L67 40 L61 58 C68 52 75 51 81 55 Z" fill="url(#pumpkinGlow{uid})"/>'
        '<ellipse class="pumpkin-flame" cx="39" cy="50" rx="4.2" ry="6.2" fill="#fff3a3"/>'
        '<ellipse class="pumpkin-flame" cx="71" cy="50" rx="4.2" ry="6.2" fill="#fff3a3"/></g>'
        f'<path d="M55 56 L49 66 H61 Z" fill="url(#pumpkinGlow{uid})" class="pumpkin-eye"/>'
        f'<g class="pumpkin-mouth" style="animation-delay:-{delay:.2f}s">'
        '<path d="M24 69 L34 77 L41 70 L48 80 L55 71 L63 80 L70 70 L77 77 L87 68 L82 84 C74 94 62 96 55 91 C48 96 35 94 28 84 Z" fill="#381100" stroke="#ffd23f" stroke-width="1.4"/>'
        '<path class="pumpkin-flame" d="M55 91 C49 84 52 78 55 73 C58 78 62 84 55 91 Z" fill="#ffd23f"/>'
        '<path d="M35 77 L39 84 L43 77 M67 77 L71 84 L75 77" fill="#fff3d6"/></g>'
        '</g></svg></span>'
    )

def metric_tombs_html(acc, prec, rec, f1):
    # The four headline metrics, carved into slightly crooked tombstones.
    items = [
        ('🎯', 'Accuracy', acc, '-1.15deg'),
        ('🔮', 'Precision', prec, '0.9deg'),
        ('👻', 'Recall (churners caught)', rec, '-0.75deg'),
        ('⚖️', 'F1-Score', f1, '1.1deg'),
    ]
    crack = ('<svg class="metric-tomb-crack" viewBox="0 0 38 86" aria-hidden="true">'
             '<path d="M20 2 L14 18 L23 29 L12 45 L20 57 L13 84" fill="none" '
             'stroke="rgba(12,10,16,.72)" stroke-width="2"/></svg>')
    tombs = []
    for icon, label, value, tilt in items:
        tombs.append(
            f'<div class="metric-tomb" style="--tilt:{tilt}">'
            f'<div class="metric-tomb-moon">☾</div>{crack}'
            f'<div class="metric-tomb-icon">{icon}</div>'
            f'<div class="metric-tomb-label">{label}</div>'
            f'<div class="metric-tomb-value">{value * 100:.2f}%</div>'
            '<div class="metric-tomb-rune">✦ carved in stone ✦</div></div>'
        )
    return '<div class="metric-tombs">' + ''.join(tombs) + '</div>'

# ---------------------------------------------------------------------
# 🚪 THE GATE — "Do you really want to predict?"
# ---------------------------------------------------------------------
if _qp("entered") == "true":
    st.session_state.entered = True
elif _qp("entered") == "false":
    st.session_state.entered = False
    st.session_state.entry_shown = False   # replay the castle scene on next entry

if not st.session_state.get("entered", False):
    render_ambient()
    st.markdown(f"""
    <div class="gate-wrap">
        <div class="gate-ghost">{ghost_svg(190, "g")}</div>
        <div class="gate-title">DO YOU REALLY WANT TO PREDICT?</div>
        <div class="gate-sub">🕯️ The spirits already know who will abandon your bank... 🕯️<br>
        Enter, mortal — if you dare.</div>
        <div class="gate-stage">
            <a class="yes-btn" href="?entered=true" target="_self">YES, I DARE! 👻</a>
            <button type="button" id="runaway-no" class="no-btn">NO... NEVER! ☠</button>
        </div>
        <div class="gate-hint">( psst... try clicking "No". The ghost won't let you. 😈 )</div>
    </div>
    """, unsafe_allow_html=True)
    inject_haunted_js()

    # Backup YES in case a browser blocks the styled link above
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        if st.button("👻 YES — open the haunted gates (backup button)"):
            st.session_state.entered = True
            st.session_state.entry_shown = False
            st.rerun()
    st.stop()

# =====================================================================
# 🏦 INSIDE THE HAUNTED BANK
# =====================================================================
render_ambient()

# 🏰 Gothic castle cinematic plays ONCE, right after entering through
# the gate: moonlit SVG castle, crow crossing, then fade into the app.
if not st.session_state.get("entry_shown", False):
    entry_gothic_scene()
    st.session_state.entry_shown = True

st.markdown(
    '<div class="header-banner"><span class="candle">🕯️</span>'
    '<h1 style="color:#FFB347 !important; margin:0; font-size: 2.6rem; display:inline;">'
    + laughing_pumpkin_svg("left", 0.0)
    + ' THE HAUNTED CHURN ORACLE '
    + laughing_pumpkin_svg("right", 0.34, flip=True)
    + '</h1><span class="candle">🕯️</span>'
    + "<p style=\"margin:8px 0 0 0; font-size:1.05rem; color:#FFE9C9; font-family:'Special Elite', monospace;\">Bank Customer Retention Séance &nbsp;•&nbsp; Powered by XGBoost... and dark magic 🔮</p>"
    '<p style="margin:2px 0 0 0; font-size:0.95rem; color:#D9C6FF;">'
    'ॐ &nbsp; ☽ &nbsp; ✦ &nbsp; the ritual circle is drawn — speak, and the spirits shall answer &nbsp; ✦ &nbsp; ☾ &nbsp; ॐ</p></div>',
    unsafe_allow_html=True,
)

# --- LOAD MODEL ---
model, scaler = None, None
try:
    model = joblib.load('churn_xgb_model.pkl')
    scaler = joblib.load('scaler.pkl')
except Exception as e:
    st.error(f"👻 The spirits cannot find your model files! Please ensure 'churn_xgb_model.pkl' and 'scaler.pkl' are in the same folder. ({e})")

# --- INITIALIZE GROQ CLIENT ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    client = None

# --- MODEL PERFORMANCE NUMBERS ---
# Synced with the REAL confusion matrix from the training notebook
# (TN 1,484 · FP 109 · FN 148 · TP 259  ->  87.15% acc, 66.84% F1).
# Used by the spider panel below AND the "Battle of Algorithms" chart.
MODEL_ACCURACY_PCT = 87.15
MODEL_F1_PCT = 66.84

# --- FEATURE IMPORTANCE DATA (for the spider panel) ---
# NOTE: all 11 model features (the original list had 10, so it never
# matched len(model.feature_importances_) and always fell back)
fallback_features = ['CreditScore', 'Gender', 'Age', 'Tenure', 'Balance',
                     'NumOfProducts', 'HasCrCard', 'IsActiveMember',
                     'EstimatedSalary', 'Geography_Germany', 'Geography_Spain']
fallback_importances = [0.02, 0.04, 0.39, 0.03, 0.08, 0.24, 0.01, 0.11, 0.02, 0.05, 0.01]

try:
    if hasattr(model, "feature_importances_"):
        imp = model.feature_importances_
        if len(imp) == len(fallback_features):
            features, importances = fallback_features, list(imp)
        else:
            features, importances = fallback_features, fallback_importances
    else:
        features, importances = fallback_features, fallback_importances
except Exception:
    features, importances = fallback_features, fallback_importances

df_eda = pd.DataFrame({'Feature': features, 'Importance': importances}).sort_values('Importance')

fig_eda = px.bar(
    df_eda, x='Importance', y='Feature', orientation='h',
    color='Importance', color_continuous_scale=['#8B2FC9', '#FF6B1A']
)
fig_eda.update_layout(
    height=270, margin=dict(l=4, r=8, t=8, b=4),
    yaxis={'categoryorder': 'total ascending'},
    coloraxis_showscale=False,
    font=dict(color="#F7E8FF"),
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
)

# =====================================================================
# 🕷️ THE SPIDER — once the gothic entry scene has faded, the data
# spider patrols the full page rectangle (see spiderPatrol CSS).
# Click the spider to reveal Model Information + the Dark Forces
# (feature importance) panel. Click again to hide it.
# =====================================================================
def spider_svg():
    # No silk thread any more: this spider walks on the page.
    return _mini_spider_svg()

st.session_state.setdefault("spider_open", False)

with _keyed_box("spider_dock"):
    st.markdown(
        f'<div class="spider-walk">{spider_svg()}'
        '<div class="spider-hint">👆 click me!</div></div>',
        unsafe_allow_html=True,
    )
    # Invisible native button laid over the spider (see CSS) — so
    # clicking the spider itself toggles the panel, no JS needed.
    if st.button("spider", key="spider_click",
                 help="🕷️ Click the spider to reveal Model Information & the Dark Forces behind churn!"):
        st.session_state.spider_open = not st.session_state.spider_open
        st.rerun()

if st.session_state.spider_open:
    with _keyed_box("spider_panel"):
        st.markdown('<div class="spider-panel-title">🪦 MODEL INFORMATION</div>',
                    unsafe_allow_html=True)
        st.write("**Algorithm:** XGBoost Classifier")
        st.write(f"**Accuracy:** {MODEL_ACCURACY_PCT:.2f}%")
        st.write(f"**F1-Score:** {MODEL_F1_PCT:.2f}%")
        st.write("---")
        st.markdown('<div class="spider-panel-title">🔮 DARK FORCES BEHIND CHURN</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(fig_eda, use_container_width=True)
        st.write("---")
        st.markdown('<a class="escape-link" href="?entered=false" target="_self">🚪 Escape back to the ghost gate...</a>',
                    unsafe_allow_html=True)
        if st.button("✖ Hide (send the spider away)", key="spider_close", use_container_width=True):
            st.session_state.spider_open = False
            st.rerun()

# --- TABS ---
tab1, tab2, tab3 = st.tabs([
    "🔮 Single Soul Prediction",
    "⚰️ Batch of Souls (CSV)",
    "📜 Ancient Model Scrolls (EDA)"
])

# ==========================================
# TAB 1: SINGLE CUSTOMER PREDICTION + CHATBOT
# ==========================================
with tab1:
    st.session_state.setdefault("prediction_run_id", 0)
    with st.form("prediction_form", clear_on_submit=False):
        st.markdown("<h4>🕯️ Whisper the customer's details into the ritual circle:</h4>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            credit_score = st.number_input("Credit Score", min_value=300, max_value=850, value=650,
                                           key="pred_credit_score", help="The customer's credit score (300-850).")
            age = st.number_input("Age", min_value=18, max_value=100, value=35,
                                  key="pred_age", help="The customer's age in years.")
            tenure = st.number_input("Tenure (Years)", min_value=0, max_value=10, value=5,
                                     key="pred_tenure", help="Number of years the customer has been with the bank.")
            balance = st.number_input("Account Balance ($)", min_value=0.0, value=75000.0,
                                      key="pred_balance", help="The current balance in the customer's account.")

        with col2:
            estimated_salary = st.number_input("Estimated Salary ($)", min_value=0.0, value=50000.0,
                                               key="pred_estimated_salary", help="The estimated annual salary of the customer.")
            geography = st.selectbox("Geography", ["France", "Spain", "Germany"],
                                     key="pred_geography", help="The country where the customer resides.")
            gender = st.selectbox("Gender", ["Female", "Male"],
                                  key="pred_gender", help="The customer's gender.")

        with col3:
            num_products = st.selectbox("Number of Products", [1, 2, 3, 4],
                                        key="pred_num_products", help="The number of bank products the customer uses.")
            has_card = st.selectbox("Has Credit Card?", ["Yes", "No"],
                                    key="pred_has_card", help="Does the customer have a bank credit card?")
            is_active = st.selectbox("Is Active Member?", ["Yes", "No"],
                                     key="pred_is_active", help="Is the customer actively using their account?")

        st.write("")
        submitted = st.form_submit_button("🔮 SUMMON THE PREDICTION 👻", key="summon_prediction_button")

    if submitted:
        if model is None or scaler is None:
            st.error("Model not loaded — the séance cannot begin.")
        else:
            input_data = pd.DataFrame({
                'CreditScore': [credit_score],
                'Gender': [1 if gender == "Male" else 0],
                'Age': [age],
                'Tenure': [tenure],
                'Balance': [balance],
                'NumOfProducts': [num_products],
                'HasCrCard': [1 if has_card == "Yes" else 0],
                'IsActiveMember': [1 if is_active == "Yes" else 0],
                'EstimatedSalary': [estimated_salary],
                'Geography_Germany': [1 if geography == "Germany" else 0],
                'Geography_Spain': [1 if geography == "Spain" else 0]
            })

            num_cols = ['CreditScore', 'Age', 'Tenure', 'Balance', 'EstimatedSalary']
            input_data[num_cols] = scaler.transform(input_data[num_cols])

            prediction = model.predict(input_data)[0]
            probability = model.predict_proba(input_data)[0][1]

            # Every Summon click gets a brand-new run number. The Death
            # Note component below is rebuilt from this number + the new
            # values, so the cover/pages/writing/meter REOPEN each time.
            _run_id = int(st.session_state.get("prediction_run_id", 0)) + 1
            st.session_state.prediction_run_id = _run_id

            if prediction == 1:
                _rec_title = "⚠️ A warning from the dark"
                if age > 50:
                    _recommendation = ("Older customers have a high churn rate. "
                                       "Offer a dedicated senior account manager.")
                elif num_products >= 3:
                    _recommendation = ("This customer holds too many services. Schedule a call "
                                       "to simplify their banking experience.")
                elif is_active == "No":
                    _recommendation = ("The customer is inactive. Send a re-engagement email "
                                       "with a small cash bonus.")
                else:
                    _recommendation = "Offer a short-term retention discount on their account fees."
            else:
                _rec_title = "🍫 The oracle is pleased"
                _recommendation = ("This soul is likely to stay. Maintain regular engagement "
                                   "and offer suitable cross-selling opportunities.")

            st.session_state.last_prediction = {
                "credit_score": credit_score,
                "age": age, "balance": balance, "tenure": tenure,
                "estimated_salary": estimated_salary, "geography": geography,
                "gender": gender, "num_products": num_products,
                "has_card": has_card, "is_active": is_active,
                "prediction": int(prediction), "probability": float(probability),
                "recommendation_title": _rec_title,
                "recommendation": _recommendation,
                "run_id": _run_id,
            }
            # The ghost (bottom-right chatbot) greets you with the verdict
            _verdict = ("🔥 **HIGH RISK** — this soul is likely to churn" if prediction == 1
                        else "🍫 **SAFE** — this soul is likely to stay")
            st.session_state.messages = [{
                "role": "assistant",
                "content": (f"👻 Boo! I have read this soul's fate: {_verdict} "
                            f"(churn probability: {probability*100:.1f}%).\n\n"
                            "Ask me **why**, or what offer we should give them!")
            }]

            # Only a churn-risk result (50%+) brings Huddy Buddy's jumpscare.
            if probability >= 0.5:
                hell_effect()


    # 📓 Render the latest Death Note outside the one-click submit branch.
    # A new Summon click increments run_id and changes the embedded book's
    # HTML, so it always reopens from the black cover with updated data.
    _result = st.session_state.get("last_prediction")
    if _result:
        _fallback_title = ("⚠️ A warning from the dark" if _result["prediction"] == 1
                           else "🍫 The oracle is pleased")
        _fallback_rec = ("Act quickly with a personalised retention ritual for this soul."
                         if _result["prediction"] == 1 else
                         "This soul is likely to stay. Maintain regular engagement.")
        death_note_result(
            _result["prediction"], _result["probability"], _result["credit_score"],
            _result["age"], _result["gender"], _result["geography"], _result["tenure"],
            _result["balance"], _result["estimated_salary"], _result["num_products"],
            _result["has_card"], _result["is_active"],
            _result.get("recommendation_title", _fallback_title),
            _result.get("recommendation", _fallback_rec),
            run_id=int(_result.get("run_id", st.session_state.get("prediction_run_id", 1)) or 1),
        )

    # NOTE: The chatbot now lives INSIDE the ghost at the bottom-right
    # corner of the screen (see "THE GHOST CHATBOT" at the end of this file).
# ==========================================
# TAB 2: BATCH PREDICTION
# ==========================================
with tab2:
    _required_csv_cols = ['CreditScore', 'Geography', 'Gender', 'Age', 'Tenure',
                          'Balance', 'NumOfProducts', 'HasCrCard',
                          'IsActiveMember', 'EstimatedSalary']

    with _keyed_box("csv_coffin"):
        st.markdown(
            '<div class="csv-portal-head"><div class="csv-portal-icon">⚰️</div><div>'
            '<div class="csv-portal-kicker">Batch Prediction Ritual</div>'
            '<div class="csv-portal-title">THE COFFIN OF SOULS</div>'
            '<div class="csv-portal-sub">Feed the coffin a CSV scroll, peek at the captured souls, then let the Oracle judge every fate.</div>'
            '</div><div class="csv-portal-icon mirror">👻</div></div>'
            '<div class="csv-portal-steps"><span>📜 <b>1</b> Drop the CSV scroll</span><b>➜</b>'
            '<span>👀 <b>2</b> Preview the souls</span><b>➜</b>'
            '<span>🔮 <b>3</b> Judge them all</span></div>',
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "📜 Feed the coffin a CSV scroll of souls",
            type="csv",
            key="souls_csv_uploader",
            help="Drop a customer CSV here. The coffin accepts .csv scrolls only.",
        )
        st.markdown(
            '<div class="csv-column-chips">'
            + ''.join(f'<span>{_c}</span>' for _c in _required_csv_cols)
            + '</div>',
            unsafe_allow_html=True,
        )

    batch_data = None
    if uploaded_file is None:
        st.markdown(
            '<div class="csv-empty">⚰️ The coffin is empty and hungry… drop in a CSV to summon the batch-preview spirits. 👻</div>',
            unsafe_allow_html=True,
        )
    else:
        try:
            batch_data = pd.read_csv(uploaded_file)
        except Exception as _csv_err:
            st.error(f"💀 The coffin choked on that scroll: {_csv_err}")
            batch_data = None

        if batch_data is not None:
            _missing_cols = [_c for _c in _required_csv_cols if _c not in batch_data.columns]
            if _missing_cols:
                st.error("🧟 This scroll is missing required column(s): " + ", ".join(_missing_cols))
                batch_data = None
            else:
                _safe_name = (uploaded_file.name.replace('&', '&amp;')
                                                .replace('<', '&lt;')
                                                .replace('>', '&gt;'))
                st.markdown(
                    f'<div class="csv-success">⚰️✨ The coffin has swallowed <strong>{_safe_name}</strong> — '
                    f'<strong>{len(batch_data):,}</strong> soul(s) across <strong>{len(batch_data.columns)}</strong> column(s) are ready for judgement.</div>',
                    unsafe_allow_html=True,
                )
                st.write("👀 A ghostly preview of the souls inside:")
                st.dataframe(batch_data.head())

    if batch_data is not None:
        if st.button("🔮 Judge All Souls (Run Batch Prediction)"):
            if model is None or scaler is None:
                st.error("Model not loaded — cannot run the batch ritual.")
            else:
                try:
                    df_processed = batch_data.copy()
                    df_processed['Gender'] = df_processed['Gender'].apply(lambda x: 1 if x == 'Male' else 0)
                    df_processed['Geography_Germany'] = df_processed['Geography'].apply(lambda x: 1 if x == 'Germany' else 0)
                    df_processed['Geography_Spain'] = df_processed['Geography'].apply(lambda x: 1 if x == 'Spain' else 0)
                    df_processed = df_processed.drop('Geography', axis=1)

                    feature_order = ['CreditScore', 'Gender', 'Age', 'Tenure', 'Balance',
                                     'NumOfProducts', 'HasCrCard', 'IsActiveMember',
                                     'EstimatedSalary', 'Geography_Germany', 'Geography_Spain']
                    df_features = df_processed[feature_order].copy()

                    num_cols = ['CreditScore', 'Age', 'Tenure', 'Balance', 'EstimatedSalary']
                    df_features[num_cols] = df_features[num_cols].astype(float)
                    df_features.loc[:, num_cols] = scaler.transform(df_features[num_cols])

                    predictions = model.predict(df_features)
                    probabilities = model.predict_proba(df_features)[:, 1]

                    batch_data['Churn_Prediction'] = predictions
                    batch_data['Churn_Probability'] = probabilities

                    doomed = int((predictions == 1).sum())
                    blessed = int((predictions == 0).sum())

                    st.success("⚰️ The batch ritual is complete! The spirits have spoken.")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("👻 Total Souls Judged", len(batch_data))
                    m2.metric("🔥 Doomed (Likely to Churn)", doomed)
                    m3.metric("🍫 Blessed (Likely to Stay)", blessed)

                    if doomed > 0:
                        st.warning(f"👻 The ghost buddy is eyeing **{doomed} soul(s)** for the underworld. "
                                   "Sort by Churn_Probability (highest first) and start your retention rituals there!")

                    st.dataframe(batch_data)

                    csv = batch_data.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📜 Download the Book of Fates (CSV)",
                        data=csv,
                        file_name='churn_predictions.csv',
                        mime='text/csv',
                    )

                except Exception as e:
                    st.error(f"💀 The ritual failed: {e}. Please ensure the CSV format matches the instructions.")

# ==========================================
# TAB 3: MODEL INSIGHTS & EDA
# ==========================================
with tab3:
    st.markdown("<h3>📜 Ancient Model Scrolls — Performance Insights</h3>", unsafe_allow_html=True)
    st.write("Visual evaluation runes of the XGBoost spell used in this haunted application.")

    col_cm, col_comp = st.columns(2)

    with col_cm:
        st.markdown("#### 🪦 Confusion Matrix")
        st.write("Evaluates the accuracy of predictions on the 2,000 test customers.")

        # ---------------------------------------------------------------
        # REAL counts from the XGBoost training notebook:
        #     confusion_matrix(y_test, y_pred) on 2,000 test customers
        #         TN = 1,484    FP = 109
        #         FN =   148    TP = 259
        # (edit these 4 numbers if you ever retrain the model)
        # ---------------------------------------------------------------
        CM_TN, CM_FP, CM_FN, CM_TP = 1484, 109, 148, 259

        # --- Haunted heatmap graph (counts + % of each actual class) ---
        _z = [[CM_TN, CM_FP], [CM_FN, CM_TP]]
        _row_tot = [CM_TN + CM_FP, CM_FN + CM_TP]
        _cell_names = [["🍫 True Stay (TN)", "🎃 False Alarm (FP)"],
                       ["👻 Missed Churner (FN)", "🔥 Caught Churner (TP)"]]
        _annotations = []
        for _i in range(2):
            for _j in range(2):
                _pct = (_z[_i][_j] / _row_tot[_i] * 100) if _row_tot[_i] else 0
                _annotations.append(dict(
                    x=["Predicted: Stay 🍫", "Predicted: Churn 🔥"][_j],
                    y=["Actual: Stay 🍫", "Actual: Churn 👻"][_i],
                    text=f"{_cell_names[_i][_j]}<br><b>{_z[_i][_j]:,}</b><br>{_pct:.1f}%",
                    showarrow=False,
                    font=dict(color="#FFF3E0", size=13),
                ))

        fig_cm = go.Figure(go.Heatmap(
            z=_z,
            x=["Predicted: Stay 🍫", "Predicted: Churn 🔥"],
            y=["Actual: Stay 🍫", "Actual: Churn 👻"],
            colorscale=[[0.0, "#241238"], [0.45, "#8B2FC9"], [1.0, "#FF6B1A"]],
            showscale=False, xgap=5, ygap=5,
            hovertemplate="%{y}<br>%{x}<br>Customers: %{z:,}<extra></extra>",
        ))
        fig_cm.update_layout(
            height=360, margin=dict(l=10, r=10, t=10, b=10),
            annotations=_annotations,
            font=dict(color="#F7E8FF"),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(autorange='reversed'),
        )
        st.plotly_chart(fig_cm, use_container_width=True)

        # --- Metrics derived from the matrix (always consistent) ---
        _tot = CM_TN + CM_FP + CM_FN + CM_TP
        _acc = (CM_TP + CM_TN) / _tot if _tot else 0
        _prec = CM_TP / (CM_TP + CM_FP) if (CM_TP + CM_FP) else 0
        _rec = CM_TP / (CM_TP + CM_FN) if (CM_TP + CM_FN) else 0
        _f1 = (2 * _prec * _rec / (_prec + _rec)) if (_prec + _rec) else 0
    with col_comp:
        st.markdown("#### ⚔️ Battle of the Algorithms")
        st.write("Why XGBoost was crowned the champion spell.")

        models = ['Logistic Regression', 'Decision Tree', 'Random Forest', 'XGBoost']
        accuracy = [71.8, 80.3, 80.9, MODEL_ACCURACY_PCT]

        fig_comp = px.bar(
            x=models, y=accuracy,
            labels={'x': 'Algorithm', 'y': 'Accuracy (%)'},
            color=accuracy,
            color_continuous_scale=['#8B2FC9', '#FF6B1A'],
            text_auto=True
        )
        fig_comp.update_layout(coloraxis_showscale=False, height=350,
                               font=dict(color="#F7E8FF"),
                               paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig_comp.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
        st.plotly_chart(fig_comp, use_container_width=True)

    # Four metric tombstones standing shoulder-to-shoulder across the
    # full width of Ancient Model Scrolls (no empty graveyard on the right).
    st.markdown('<div class="metric-tombs-title">🪦 THE FOUR STONES OF JUDGEMENT 🪦</div>',
                unsafe_allow_html=True)
    st.markdown(metric_tombs_html(_acc, _prec, _rec, _f1),
                unsafe_allow_html=True)

# =====================================================================
# 👻 THE GHOST CHATBOT — floats bottom-right, its eyes follow your
# cursor, and clicking "Chat with the Ghost!" opens a chat panel that
# pops out of the ghost itself. It knows the latest prediction.
# (rendered last so it reacts to the newest prediction)
# =====================================================================
def ghost_reply(user_prompt):
    """Ask Groq — with the latest customer's prediction as context."""
    if client is None:
        return ("⚠️ **Groq API Key not found.** Please add it to your "
                "`.streamlit/secrets.toml` file to awaken me, mortal.")

    cust = st.session_state.get("last_prediction")
    if cust:
        context = f"""
        You are an expert banking retention assistant talking to a bank employee.
        Here is the customer's profile and the machine learning model's prediction:
        - Age: {cust['age']}
        - Geography: {cust['geography']}
        - Gender: {cust['gender']}
        - Account Balance: ${cust['balance']:,.2f}
        - Number of Products: {cust['num_products']}
        - Active Member: {cust['is_active']}
        - Tenure: {cust['tenure']} years
        - Estimated Salary: ${cust['estimated_salary']:,.2f}
        - Churn Prediction: {'HIGH RISK' if cust['prediction'] == 1 else 'LOW RISK'}
        - Churn Probability: {cust['probability']*100:.1f}%

        Answer the employee's question directly using this data. Be concise, professional, and helpful.
        If they ask for an offer or strategy, suggest something specific based on this customer's risk factors.
        """
    else:
        context = """
        You are a helpful assistant inside a Halloween-themed bank customer churn
        prediction app (XGBoost model). No customer has been predicted yet in this
        session. Answer general questions about bank customer churn and retention
        concisely and helpfully. If the employee asks about a specific customer,
        tell them to first enter the customer's details and click
        "SUMMON THE PREDICTION", after which you will know that customer's fate.
        """

    msgs = [{"role": "system", "content": context}]
    msgs += st.session_state.messages[-6:]          # a little short-term memory
    msgs.append({"role": "user", "content": user_prompt})

    try:
        chat_completion = client.chat.completions.create(
            messages=msgs,
            model="openai/gpt-oss-20b",
            temperature=0.7,
            max_tokens=300,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Sorry, I couldn't reach the spirit world. Error: {e}"

def ask_ghost(prompt_text):
    with st.spinner("👻 The ghost is consulting the spirits..."):
        reply = ghost_reply(prompt_text)
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

st.session_state.setdefault("ghost_open", False)
st.session_state.setdefault("messages", [])
_is_open = st.session_state.ghost_open
_lp = st.session_state.get("last_prediction")

if _lp and _lp.get("prediction") == 1:
    _bubble = "That one is MINE! 😈🔥 Click 💬 — ask me how to save them!"
elif _lp:
    _bubble = "A blessed soul! 🍫 Click 💬 to chat with me!"
else:
    _bubble = "I am watching you type... 👁️ Click 💬 to chat with me!"

with _keyed_box("ghost_bot_open" if _is_open else "ghost_bot_closed"):

    if _is_open:
        with _keyed_box("ghost_panel"):
            # Compact header: mini ghost (eyes still follow you!) + title.
            # Keeping the panel SHORT is what fixes the clipped top.
            st.markdown(
                '<div class="ghost-panel-head">' + ghost_svg(46, "") +
                '<div><div class="ghost-panel-title">GHOST ASSISTANT</div>'
                '<div class="ghost-panel-sub">I have seen the data... ask me anything 🕯️</div></div></div>',
                unsafe_allow_html=True,
            )

            with _scroll_box(200):
                if not st.session_state.messages:
                    with st.chat_message("assistant", avatar="👻"):
                        st.markdown(
                            "Boo! 👻 I'm the Bank Ghost. Summon a prediction and I'll "
                            "read that soul's fate — or ask me any general churn "
                            "question right now!"
                        )
                for _m in st.session_state.messages:
                    with st.chat_message(_m["role"], avatar="👻" if _m["role"] == "assistant" else "🎃"):
                        st.markdown(_m["content"])

            if _lp:
                _q1, _q2 = st.columns(2)
                with _q1:
                    if st.button("🔮 Why this verdict?", key="ghost_q_why", use_container_width=True):
                        ask_ghost("Why did the model give this verdict for this customer? "
                                  "Explain the main risk (or safety) factors.")
                with _q2:
                    if st.button("🎁 Best offer?", key="ghost_q_offer", use_container_width=True):
                        ask_ghost("What is the single best retention offer or next step "
                                  "for this specific customer, and why?")

            with st.form("ghost_chat_form", clear_on_submit=True):
                _fc1, _fc2 = st.columns([2.3, 1])
                with _fc1:
                    _q = st.text_input(
                        "Ask the ghost", key="ghost_q_input", label_visibility="collapsed",
                        placeholder="Ask me... e.g. Why is this customer risky?",
                    )
                with _fc2:
                    _send = st.form_submit_button("Send", use_container_width=True)
            if _send and _q and _q.strip():
                ask_ghost(_q.strip())

    # Big floating ghost only when the chat is CLOSED — when open, the
    # mini ghost lives in the panel header (saves vertical space and
    # keeps the pupils' IDs unique for the eye-tracking JS).
    if not _is_open:
        st.markdown(
            f'<div class="ghost-head"><div class="watcher-bubble">{_bubble}</div>{ghost_svg(105, "")}</div>',
            unsafe_allow_html=True,
        )

    if st.button("✖ Hide the ghost chat" if _is_open else "💬 Chat with the Ghost!",
                 key="ghost_toggle", use_container_width=True):
        st.session_state.ghost_open = not _is_open
        st.rerun()

# ⚖️ Final line of the page
st.markdown('<div class="app-footer">&copy; 2026 THE BLACK LEDGER · ALL VERDICTS ARE PROBABILISTIC</div>', unsafe_allow_html=True)

inject_haunted_js()
