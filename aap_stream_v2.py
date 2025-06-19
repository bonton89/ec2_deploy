import streamlit as st
from PyPDF2 import PdfReader
from test_aws import call_bedrock
#from prompt_temp import system_prompt
from prompt_v2 import system_prompt
import time
import base64

# Set page configuration
st.set_page_config(
    page_title="Fixed Income - Quarter back Demo",
    page_icon="📊",
    layout="wide",
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        font-weight: 700;
        margin-top: 0.5em;    
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        font-weight: 600;
        margin-top: 0;
        margin-bottom: 0;
    }
    .disclaimer {
        font-size: 0.8rem;
        color: #757575;
        font-style: italic;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        font-weight: 500;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #0D47A1;
        border-color: #0D47A1;
    }
    .response-area {
        background-color: #f5f7f9;
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid #1E88E5;
        margin-top: 10px;
    }
    /* Custom CSS for dividers to minimize top and bottom margins */
    hr {
        margin-top: 1px !important;
        margin-bottom: 1px !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    /* Target Streamlit's divider class specifically */
    .css-9ycgxx {   /* This is Streamlit's divider class */
        margin-top: 1px !important;
        margin-bottom: 1px !important;
    }
    /* Additional classes to ensure divider margins are minimal */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    div.css-1544g2n.e1fqkh3o4 {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Function to display animated progress bar
def show_progress_animation(message="Processing..."):
    progress_placeholder = st.empty()
    progress_bar = progress_placeholder.progress(0)
    status_text = st.empty()
    
    for percent in range(0, 101, 2):
        time.sleep(0.05)  # Simulate processing time
        progress_bar.progress(percent)
        status_text.text(f"{message} ({percent}%)")
    
    progress_placeholder.empty()
    status_text.empty()
    return True

# Custom divider with minimal margins
def tight_divider():
    st.markdown("<hr style='margin-top: 0; margin-bottom: 0; padding: 0;'>", unsafe_allow_html=True)

# Header section
st.markdown('<div class="main-header">Fixed Income - Quarter back Demo 📊</div>', unsafe_allow_html=True)
st.markdown("AI-powered analysis tool for financial documents and communications")
tight_divider()

# Layout with columns for better organization
col1, col2 = st.columns(2)

# Email section
with col1:
    st.markdown('<div class="sub-header">Email Text Input</div>', unsafe_allow_html=True)
    st.markdown("Paste the email content here. The AI model will use this for context.")
    email_doc_text = st.text_area("", "", height=200, placeholder="Paste your email text here...")

# PDF Upload section
with col2:
    st.markdown('<div class="sub-header">Document Selection</div>', unsafe_allow_html=True)
    st.markdown('<div class="disclaimer">* Disclaimer: Documents selected are not uploaded/stored and are only processed for analysis.</div>', 
                unsafe_allow_html=True)
    
    pdf_text = ""
    uploaded_file = st.file_uploader('Choose your .pdf file', type="pdf")
    
    if uploaded_file is not None:
        file_details = {"Filename": uploaded_file.name, "File size": f"{round(uploaded_file.size / 1024, 2)} KB"}
        st.write(f"**Selected file:** {file_details['Filename']}")
        
        with st.spinner("Processing PDF..."):
            # Show progress animation for PDF processing
            upload_progress_placeholder = st.empty()
            upload_progress = upload_progress_placeholder.progress(0)
            upload_status = st.empty()
            
            # Process PDF file
            reader = PdfReader(uploaded_file)
            total_pages = len(reader.pages)
            
            for i, page in enumerate(reader.pages):
                # Update progress bar
                percent = int((i + 1) / total_pages * 100)
                upload_progress.progress(percent)
                upload_status.text(f"Processing page {i+1} of {total_pages} ({percent}%)")
                
                # Extract text
                pdf_text += page.extract_text()
                time.sleep(0.1)  # Small delay for visual feedback
                
            #st.write(pdf_text)
            upload_progress_placeholder.empty()
            upload_status.empty()
            st.success(f"✅ Successfully processed {total_pages} pages")

tight_divider()

# Analysis section
st.markdown('<div class="sub-header">Generate AI Analysis</div>', unsafe_allow_html=True)

# Check if there's any input to analyze
if not email_doc_text and not pdf_text:
    st.warning("⚠️ Please enter email text or upload a PDF document to generate a response.")
else:
    # Combine text for analysis
    email_pdf_text = f"Email Text\n: {email_doc_text}\nPDF Text \n: {str(pdf_text)}"
    #email_pdf_text = email_doc_text + pdf_text
    #st.write(email_pdf_text)
    # Generate response button
    if st.button("Generate Response", key="generate_btn"):
        with st.container():
            # Show progress animation
            show_progress_animation("Analyzing content")
            
            # Call the model to get the response
            with st.spinner("Finalizing results..."):
                if email_doc_text is None:
                    resp = call_bedrock(system_prompt, pdf_text)
                else:
                    resp = call_bedrock(system_prompt, email_doc_text)
            
            # Display the response in a formatted container
            st.markdown('<div class="sub-header">Analysis Results</div>', unsafe_allow_html=True)
            #st.markdown('<div class="response-area">', unsafe_allow_html=True)
            st.markdown(resp)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Add timestamp for when the response was generated
            st.caption(f"Response generated at {time.strftime('%Y-%m-%d %H:%M:%S')}")

# Footer
tight_divider()
st.caption("© 2025 Fixed Income Analysis Tool - For demonstration purposes only")