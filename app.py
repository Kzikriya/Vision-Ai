import streamlit as st
import requests
from PIL import Image
import io
import base64
import json

# App UI
st.set_page_config(page_title="Vision AI", page_icon="👁️", layout="wide")
st.title("👁️ Multi-Model Vision AI with OpenRouter")
st.markdown("Upload images and get detailed descriptions using multiple AI models")

# API key input
api_key = st.sidebar.text_input("Enter your OpenRouter API Key:", type="password")
if not api_key:
    st.info("👈 Please enter your OpenRouter API key in the sidebar to continue")
    st.stop()

# Model selection
available_models = [
    "google/gemini-pro-vision",
    "openai/gpt-4-vision-preview",
    "anthropic/claude-3-sonnet", 
    "anthropic/claude-3-opus",
    "anthropic/claude-3-haiku",
    "meta-llama/llama-3-70b-vision"
]

selected_model = st.sidebar.selectbox(
    "Choose AI Model:",
    available_models,
    index=0  # Default to Gemini Pro Vision
)

# File upload
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    # Analysis options
    col1, col2 = st.columns(2)
    with col1:
        detail_level = st.selectbox(
            "Description Detail:",
            ["Brief", "Detailed", "Technical", "Creative", "Comprehensive"]
        )
    with col2:
        analysis_type = st.selectbox(
            "Analysis Type:",
            [
                "General Description", 
                "Object Detection", 
                "Scene Analysis",
                "Color & Composition",
                "Text Extraction",
                "Emotional Analysis"
            ]
        )
    
    # Custom prompt option
    custom_prompt = st.text_area(
        "Custom Instructions (optional):",
        placeholder="Add specific things you want the AI to focus on...",
        height=100
    )
    
    if st.button("Analyze Image", type="primary"):
        with st.spinner(f"Analyzing with {selected_model}..."):
            try:
                # Convert image to base64
                buffered = io.BytesIO()
                image.save(buffered, format=image.format or "PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                media_type = f"image/{image.format.lower()}" if image.format else "image/png"
                
                # Create the prompt
                prompt = f"""
                Please provide a {detail_level.lower()} {analysis_type.lower()} of this image.
                Be comprehensive, analytical, and descriptive in your response.
                """
                
                if custom_prompt:
                    prompt += f"\n\nAdditional instructions: {custom_prompt}"
                
                # Prepare OpenRouter API request
                url = "https://openrouter.ai/api/v1/chat/completions"
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8501",  # Required by OpenRouter
                    "X-Title": "Vision AI App"  # Required by OpenRouter
                }
                
                # Different payload structures for different models
                if "gpt-4" in selected_model or "claude" in selected_model:
                    # For OpenAI and Anthropic models
                    payload = {
                        "model": selected_model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:{media_type};base64,{img_base64}"
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": prompt
                                    }
                                ]
                            }
                        ],
                        "max_tokens": 4000
                    }
                else:
                    # For other models (Gemini, Llama, etc.)
                    payload = {
                        "model": selected_model,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt + f"\n\n[Image: {media_type}, base64 encoded]"
                            }
                        ],
                        "max_tokens": 4000
                    }
                
                # Make API request
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                # Parse response
                result = response.json()
                analysis_result = result['choices'][0]['message']['content']
                
                # Display results
                st.success(f"🎯 Analysis Results from {selected_model}:")
                st.markdown(analysis_result)
                
                # Show usage info
                usage = result.get('usage', {})
                st.sidebar.info(f"**Model:** {selected_model}")
                if usage:
                    st.sidebar.info(f"**Input tokens:** {usage.get('prompt_tokens', 'N/A')}")
                    st.sidebar.info(f"**Output tokens:** {usage.get('completion_tokens', 'N/A')}")
                
            except requests.exceptions.HTTPError as e:
                if response.status_code == 401:
                    st.error("❌ Invalid OpenRouter API key. Please check your key.")
                elif response.status_code == 429:
                    st.error("⚠️ Rate limit exceeded. Please try again later.")
                else:
                    st.error(f"API error: HTTP {response.status_code}")
            except Exception as e:
                st.error(f"Error analyzing image: {str(e)}")

# Model information
with st.sidebar.expander("ℹ️ Model Information"):
    st.write("""
    **Available Models:**
    
    - **Google Gemini Pro Vision**: Best for general vision tasks
    - **OpenAI GPT-4 Vision**: Most advanced vision capabilities  
    - **Anthropic Claude 3**: Excellent for complex reasoning
    - **Meta Llama 3 Vision**: Open-source alternative
    
    **OpenRouter Benefits:**
    - Single API key for all models
    - Competitive pricing
    - Easy model switching
    """)

# Footer
st.markdown("---")
st.caption("Powered by OpenRouter • Multiple AI Models • Containerized with Docker")