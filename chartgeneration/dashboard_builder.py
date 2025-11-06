import streamlit as st

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("📊 My Dashboard")

if "dashboard_charts" not in st.session_state or not st.session_state["dashboard_charts"]:
    st.warning("No charts added yet. Go back to generate one.")
    st.write(st.session_state)

else:
    for chart in st.session_state["dashboard_charts"]:
        st.subheader(chart["title"])
        try:
            st.write(st.session_state)
            st.image(chart["figure"])
            st.pyplot(chart["figure"].figure_)
        except Exception:
            st.write("⚠️ Could not render this chart (maybe session lost state).")
