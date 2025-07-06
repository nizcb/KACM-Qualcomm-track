import streamlit as st
import json
import io
import asyncio
from agent import VisionAgent, VisionArgs

# Initialize the agent
agent = VisionAgent()

# Page configuration
st.set_page_config(
    page_title="Vision Agent - LLM Intelligence",
    page_icon="🔍",
    layout="wide"
)

# Main title
st.title("🔍 Vision Agent - LLM Intelligence")
st.markdown("Upload an image to get an AI-powered summary and sensitivity analysis using Llama-3")

# Create two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📁 Upload Image")
    
    # Tab for upload vs file path
    tab1, tab2 = st.tabs(["📤 Upload File", "📂 Local File Path"])
    
    with tab1:
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
            help="Upload an image to analyze with the LLM"
        )
        
        if uploaded_file is not None:
            # Display the uploaded image
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
            
            # Analyze button for uploaded file
            if st.button("🚀 Analyze Uploaded Image", type="primary", key="upload_analyze"):
                with st.spinner("🤖 LLM is analyzing the uploaded image..."):
                    try:
                        # Convert uploaded file to bytes
                        image_bytes = uploaded_file.read()
                        
                        # Create VisionArgs with correct signature
                        args = VisionArgs(
                            path=uploaded_file.name,
                            image_bytes=image_bytes
                        )
                        
                        # Analyze the image (async call)
                        result = asyncio.run(agent.analyze_document(args))
                        
                        # Store result in session state
                        st.session_state['analysis_result'] = result
                        st.success("✅ Analysis complete!")
                        
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {str(e)}")
    
    with tab2:
        file_path = st.text_input(
            "Enter image file path",
            placeholder="C:/path/to/your/image.jpg",
            help="Enter the full path to an image file on your system"
        )
        
        if file_path:
            try:
                # Try to display the image from path
                st.image(file_path, caption="Local Image", use_container_width=True)
                
                # Analyze button for file path
                if st.button("🚀 Analyze Local Image", type="primary", key="path_analyze"):
                    with st.spinner("🤖 LLM is analyzing the local image..."):
                        try:
                            # Create VisionArgs with file path only
                            args = VisionArgs(path=file_path)
                            
                            # Analyze the image (async call)
                            result = asyncio.run(agent.analyze_document(args))
                            
                            # Store result in session state
                            st.session_state['analysis_result'] = result
                            st.success("✅ Analysis complete!")
                            
                        except Exception as e:
                            st.error(f"❌ Error during analysis: {str(e)}")
                            
            except Exception as e:
                st.warning(f"Cannot preview image: {str(e)}")
                
                # Still allow analysis even if preview fails
                if st.button("🚀 Analyze (No Preview)", type="secondary", key="path_analyze_no_preview"):
                    with st.spinner("🤖 LLM is analyzing the local image..."):
                        try:
                            # Create VisionArgs with file path only
                            args = VisionArgs(path=file_path)
                            
                            # Analyze the image (async call)
                            result = asyncio.run(agent.analyze_document(args))
                            
                            # Store result in session state
                            st.session_state['analysis_result'] = result
                            st.success("✅ Analysis complete!")
                            
                        except Exception as e:
                            st.error(f"❌ Error during analysis: {str(e)}")

with col2:
    st.header("📊 Analysis Results")
    
    if 'analysis_result' in st.session_state:
        result = st.session_state['analysis_result']
        
        # Display filepath
        st.subheader("📎 File Information")
        st.info(f"**Filepath:** {result.filepath}")
        
        # Display summary
        st.subheader("📝 AI Summary")
        st.markdown(f"**Summary:** {result.summary}")
        
        # Display warning with appropriate styling
        st.subheader("⚠️ Sensitivity Analysis")
        if result.warning:
            st.warning(f"**Warning:** {result.warning}")
        else:
            st.success("**Status:** No sensitive content detected")
        
        # Display JSON output
        st.subheader("🔧 JSON Output")
        json_output = {
            "filepath": result.filepath,
            "summary": result.summary,
            "warning": result.warning
        }
        
        st.json(json_output)
        
        # Download button for JSON
        json_str = json.dumps(json_output, indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"analysis_{uploaded_file.name if 'uploaded_file' in locals() and uploaded_file else 'result'}.json",
            mime="application/json"
        )
    else:
        st.info("👆 Upload an image and click 'Analyze with LLM' to see results here")

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This Vision Agent uses **Llama-3 LLM** for intelligent image analysis:
    
    **Features:**
    - 🖼️ OCR text extraction
    - 🧠 LLM-powered content summarization
    - 🛡️ Automated sensitivity detection
    - 📊 Clean JSON output
    
    **Output Format:**
    - `filepath`: Image file path
    - `summary`: AI-generated summary
    - `warning`: Sensitivity alert (if any)
    """)
    
    st.header("🔧 Technical Details")
    st.markdown("""
    **Pipeline:**
    1. Image → OCR (text extraction)
    2. Text → LLM (Llama-3 analysis)
    3. LLM → Structured JSON response
    
    **LLM Model:** Llama-3
    **OCR Engine:** EasyOCR
    """)

# Footer
st.markdown("---")
st.markdown("🤖 **Powered by Llama-3 LLM** | Built for KACM-Qualcomm Hackathon")
