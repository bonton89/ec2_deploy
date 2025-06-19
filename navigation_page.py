import streamlit as st
# Set page configuration
st.set_page_config(
    page_title="Bedrock Model Demo",
    page_icon="📊",
    layout="wide",
)

# --- PAGE SETUP ---
project_2_page = st.Page(
    "aap_stream_v2.py",
    title="Fixed Income - Quarter Back",
    icon=":material/account_circle:",
    default=True,

)

project_1_page = st.Page(
    "aap_stream_vg_screen.py",
    title="Plan Audit Demo",
    icon=":material/smart_toy:",
)




# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
# pg = st.navigation(pages=[about_page, project_1_page, project_2_page])

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        
        "Use Case": [project_1_page, project_2_page],
      
       
    }
)


# --- SHARED ON ALL PAGES ---
#st.logo("assets/logo1.png")
st.sidebar.markdown(" :blue[ © infosys bpm ] ")
#st.sidebar.markdown(" **Crafted with  🤎 in India** ")


# --- RUN NAVIGATION ---
pg.run()