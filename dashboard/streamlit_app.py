import streamlit as st
import requests

st.title("AI Robotic Classroom Control Panel")
BASE_URL = "http://raspberrypi-ip:5000"

col1, col2, col3 = st.columns(3)

def send(cmd):
    requests.get(f"{BASE_URL}/control?cmd={cmd}")

with col1:
    if st.button("⬆ Forward"):
        send("forward")

with col2:
    if st.button("⛔ Stop"):
        send("stop")

with col3:
    if st.button("⬇ Back"):
        send("backward")

st.subheader("Live Classroom Stream")
st.markdown("Connect via WebRTC browser client")