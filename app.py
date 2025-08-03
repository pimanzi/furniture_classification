import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io
import time
import traceback
from datetime import datetime
import tempfile
import shutil
from PIL import Image

from src.utils.database import FurnitureDB
from src.utils.model_utils import FurniturePredictor, FurnitureModelTrainer

st.set_page_config(
    page_title="Furniture AI",
    page_icon="🪑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern CSS styling
st.markdown("""
<style>
    .stApp {
        background-color: white !important;
        color: #333333 !important;
    }
    
    .main .block-container {
        background-color: white !important;
        padding-top: 2rem;
        color: #333333 !important;
    }
    
    .stMarkdown, .stText, p, div, span, h1, h2, h3, h4, h5, h6 {
        color: #333333 !important;
    }
    
    .stSelectbox label, .stTextInput label, .stFileUploader label, .stSlider label, .stCheckbox label {
        color: #fff !important;
        font-weight: 600;
    }
    
    .stSelectbox > div > div {
        background-color: white !important;
        color: black !important;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        background-color: white !important;
        border: 2px solid #8B6EFF !important;
        border-radius: 8px !important;
        color: black !important;
    }
    
    .stSelectbox div[data-baseweb="select"] > div {
        color: black !important;
        background-color: white !important;
    }
    
    .stSelectbox div[role="listbox"] {
        background-color: white !important;
        border: 2px solid #8B6EFF !important;
        border-radius: 8px !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important;
    }
    
    .stSelectbox div[role="option"] {
        background-color: white !important;
        color: black !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stSelectbox div[role="option"]:hover {
        background-color: #f0f0f0 !important;
        color: black !important;
    }
    
    .stSelectbox div[role="option"][aria-selected="true"] {
        background-color: #8B6EFF !important;
        color: white !important;
    }
    
    .stTextInput > div > div > input {
        background-color: white !important;
        color: #333333 !important;
        border: 2px solid #e5e5e5 !important;
        border-radius: 8px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #8B6EFF !important;
        box-shadow: 0 0 0 1px #8B6EFF !important;
    }
    
    .main-header {
        background: linear-gradient(90deg, #8B6EFF 0%, #7C3AED 100%);
        padding: 1.5rem 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(139, 110, 255, 0.3);
    }
    
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2.5rem;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9) !important;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    .nav-container {
        background: white;
        padding: 1rem 0;
        border-bottom: 2px solid #e5e5e5;
        margin-bottom: 2rem;
    }
    
    .prediction-card {
        background: white;
        border: 2px solid #8B6EFF;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(139, 110, 255, 0.1);
    }
    
    .prediction-card h3 {
        color: #8B6EFF !important;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .result-card {
        background: white;
        color: #333333;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(139, 110, 255, 0.4);
        border: 2px solid #8B6EFF;
    }
    
    .result-card h3 {
        color: #8B6EFF !important;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    
    .predicted-class {
        font-size: 2.5rem;
        font-weight: bold;
        color: #333333 !important;
        text-align: center;
        margin: 1rem 0;
    }
    
    .confidence-score {
        font-size: 1.5rem;
        color: #333333 !important;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .metric-card {
        background: white;
        border: 2px solid #f0f0f0;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: #8B6EFF;
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(139, 110, 255, 0.2);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #8B6EFF !important;
    }
    
    .metric-label {
        color: #666 !important;
        font-size: 0.95rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #8B6EFF 0%, #7C3AED 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(139, 110, 255, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(139, 110, 255, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666 !important;
        border-top: 2px solid #f0f0f0;
        margin-top: 3rem;
        background: #fafafa;
        border-radius: 10px;
    }
    
    .stButton > button[kind="secondary"] {
        background: white !important;
        color: #8B6EFF !important;
        border: 2px solid #8B6EFF !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #f8f6ff !important;
        color: #7C3AED !important;
        border-color: #7C3AED !important;
    }
    
    .stInfo {
        background-color: #f0f8ff !important;
        border: 1px solid #8B6EFF !important;
        border-radius: 10px !important;
    }
    
    .stInfo div {
        color: #333333 !important;
    }
    
    .stSuccess {
        background-color: #f0fff4 !important;
        border: 1px solid #10b981 !important;
        border-radius: 10px !important;
    }
    
    .stSuccess div {
        color: #065f46 !important;
    }
    
    .stError {
        background-color: #fef2f2 !important;
        border: 1px solid #ef4444 !important;
        border-radius: 10px !important;
    }
    
    .stError div {
        color: #991b1b !important;
    }
    
    .stWarning {
        background-color: #fffbeb !important;
        border: 1px solid #f59e0b !important;
        border-radius: 10px !important;
    }
    
    .stWarning div {
        color: #92400e !important;
    }
    
    .stForm {
        border: 2px solid #f0f0f0 !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        background: white !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    
    .stNumberInput > div > div > input {
        background-color: white !important;
        color: #333333 !important;
        border: 2px solid #e5e5e5 !important;
        border-radius: 8px !important;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #8B6EFF !important;
        box-shadow: 0 0 0 1px #8B6EFF !important;
    }
    
    .stForm * {
        color: #333333 !important;
    }
    
    .stForm .stSelectbox div[data-baseweb="select"] > div {
        color: #333333 !important;
        background-color: white !important;
    }
    
    .css-1d391kg {
        background-color: #fafafa !important;
    }
    
    .stFileUploader {
        border: 2px dashed #8B6EFF !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        background: #f8f6ff !important;
    }
    
    .stFileUploader label {
        color: #8B6EFF !important;
        font-weight: bold !important;
    }
    
    .stProgress .progress-bar {
        background: linear-gradient(90deg, #8B6EFF 0%, #7C3AED 100%) !important;
    }
    
    .stSlider .thumb {
        background-color: #8B6EFF !important;
    }
    
    .stSlider .track {
        background-color: #e5e5e5 !important;
    }
    
    .stCheckbox input[type="checkbox"]:checked {
        background-color: #8B6EFF !important;
        border-color: #8B6EFF !important;
    }
    
    .stSelectbox * {
        background-color: white !important;
        color: black !important;
    }
    
    .css-26l3qy-menu {
        background-color: white !important;
    }
    
    .css-4ljt47-MenuList {
        background-color: white !important;
    }
    
    .css-9jq23d-option {
        background-color: white !important;
        color: black !important;
    }
    
    .css-9jq23d-option:hover {
        background-color: #f0f0f0 !important;
        color: black !important;
    }
    
    .css-9jq23d-option--is-selected {
        background-color: #8B6EFF !important;
        color: white !important;
    }
    
    .css-9jq23d-option--is-focused {
        background-color: #f0f0f0 !important;
        color: black !important;
    }
    
    [data-testid="stSelectbox"] * {
        background-color: white !important;
        color: black !important;
    }
    
    [data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: white !important;
        color: black !important;
    }
    
    [data-testid="stSelectbox"] div[data-baseweb="select"] span {
        color: black !important;
    }
    
    .stButton button[key*="remove"] {
        background: #ef4444 !important;
        color: white !important;
        border: none !important;
        border-radius: 50% !important;
        width: 35px !important;
        height: 35px !important;
        padding: 0 !important;
        font-size: 0.8rem !important;
        margin-top: 0.5rem !important;
    }
    
    .stButton button[key*="remove"]:hover {
        background: #dc2626 !important;
        transform: scale(1.1) !important;
    }
    
    .stButton button:contains("Clear All") {
        background: #6b7280 !important;
        color: white !important;
    }
    
    .stButton button:contains("Clear All"):hover {
        background: #4b5563 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize predictor
print("🔄 Initializing predictor...")
try:
    if 'predictor' not in st.session_state:
        print("Creating new FurniturePredictor instance...")
        st.session_state.predictor = FurniturePredictor()
        print("Loading model...")
        success = st.session_state.predictor.load_model()
        if success:
            print("✓ Predictor initialized and model loaded successfully")
        else:
            print("⚠️ Model loading failed, predictions may not work")
    else:
        print("✓ Using existing predictor instance")
except Exception as e:
    print(f"❌ Predictor initialization error: {e}")
    st.error(f"Predictor initialization failed: {e}")

# Initialize trainer
print("🔄 Initializing trainer...")
try:
    if 'trainer' not in st.session_state:
        print("Creating new FurnitureModelTrainer instance...")
        st.session_state.trainer = FurnitureModelTrainer()
        print("✓ Trainer initialized successfully")
    else:
        print("✓ Using existing trainer instance")
except Exception as e:
    print(f"❌ Trainer initialization error: {e}")
    st.error(f"Trainer initialization failed: {e}")

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'

# Initialize training state variables with persistent keys
if 'training_in_progress' not in st.session_state:
    st.session_state.training_in_progress = False
if 'training_completed' not in st.session_state:
    st.session_state.training_completed = False
if 'training_results' not in st.session_state:
    st.session_state.training_results = None
if 'last_training_page' not in st.session_state:
    st.session_state.last_training_page = None
if 'training_session_id' not in st.session_state:
    st.session_state.training_session_id = None

# Check if running in deployment environment
import os
IS_DEPLOYED = (
    'STREAMLIT_SHARING' in os.environ or 
    'RENDER' in os.environ or 
    'HEROKU' in os.environ or
    'RAILWAY' in os.environ
)

# Auto-navigate back to retrain page if training was just completed
if (st.session_state.get('training_completed', False) and 
    st.session_state.get('last_training_page') == 'Retrain' and 
    st.session_state.current_page != 'Retrain'):
    st.session_state.current_page = 'Retrain'

# Recovery mechanism: check for recent training completion from database
if not st.session_state.get('training_completed', False):
    try:
        # Check if there's a recent training session in the database
        recent_sessions = st.session_state.db.get_all_training_sessions()
        if recent_sessions and len(recent_sessions['sessions']) > 0:
            latest_session = recent_sessions['sessions'].iloc[0]  # Most recent session
            session_time = pd.to_datetime(latest_session['created_at'])
            current_time = pd.Timestamp.now()
            
            # If training was completed within the last 10 minutes, try to recover
            if (current_time - session_time).total_seconds() < 600:  # 10 minutes
                st.session_state.training_completed = True
                st.session_state.training_results = {
                    'final_accuracy': latest_session['final_accuracy'],
                    'training_time': latest_session['training_time_minutes'],
                    'total_data_count': latest_session['total_data_count'],
                    'session_name': latest_session['session_name'],
                    'session_id': latest_session['session_name'],
                    'completed_at': latest_session['created_at']
                }
                st.session_state.last_training_page = 'Retrain'
                if st.session_state.current_page == 'Home':
                    st.session_state.current_page = 'Retrain'
    except Exception as recovery_error:
        # Silently handle recovery errors
        pass

def navigation():    
    # Initialize session state if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Home'
    
    # Initialize database connection if not exists
    if 'db' not in st.session_state:
        st.session_state.db = FurnitureDB()
    
    # Prevent navigation during training
    if st.session_state.get('training_in_progress', False):
        st.warning("⏳ Training in progress... Navigation disabled to prevent interruption.")
        return
    
    # Show training completed indicator in navigation
    training_indicator = ""
    if st.session_state.get('training_completed', False):
        training_indicator = " ✅"
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("🏠 Home", key="nav_home"):
            # Only clear training results if explicitly navigating away and training is not just completed
            if (st.session_state.current_page == 'Retrain' and 
                not st.session_state.get('training_completed', False)):
                st.session_state.training_completed = False
                st.session_state.training_results = None
                st.session_state.last_training_page = None
            st.session_state.current_page = 'Home'
            st.rerun()
    
    with col2:
        if st.button("🔮 Predict", key="nav_predict"):
            if (st.session_state.current_page == 'Retrain' and 
                not st.session_state.get('training_completed', False)):
                st.session_state.training_completed = False
                st.session_state.training_results = None
                st.session_state.last_training_page = None
            st.session_state.current_page = 'Predict'
            st.rerun()
    
    with col3:
        if st.button("📊 Analytics", key="nav_analytics"):
            if (st.session_state.current_page == 'Retrain' and 
                not st.session_state.get('training_completed', False)):
                st.session_state.training_completed = False
                st.session_state.training_results = None
                st.session_state.last_training_page = None
            st.session_state.current_page = 'Analytics'
            st.rerun()
    
    with col4:
        nav_button_text = f"🔄 Retrain{training_indicator}"
        
        if st.button(nav_button_text, key="nav_retrain"):
            st.session_state.current_page = 'Retrain'
            st.session_state.last_training_page = 'Retrain'
            if 'selected_files' not in st.session_state:
                st.session_state.selected_files = []
                st.session_state.file_labels = {}
            st.rerun()

def show_home():
    st.markdown("""
    <div class="main-header">
        <h1>🪑 Furniture AI</h1>
        <p>Advanced furniture classification using deep learning</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎯 What is Furniture AI?")
        st.markdown("""
        <div style="color: #333333; font-size: 1.1rem; line-height: 1.6;">
        Furniture AI is a powerful deep learning system that can classify furniture images into five categories with high accuracy.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ✨ Features")
        features = [
            "**Instant Classification** - Upload any furniture image for immediate results",
            "**High Accuracy** - Powered by EfficientNetB0 neural network",
            "**Analytics Dashboard** - Track performance and usage statistics",
            "**Custom Training** - Improve the model with your own data"
        ]
        for feature in features:
            st.markdown(f"""
            <div style="color: #333333; margin: 0.5rem 0; font-size: 1rem;">
            • {feature}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 🪑 Supported Categories")
        categories = ["🗄️ Almirah", "🪑 Chair", "❄️ Fridge", "🪑 Table", "📺 TV"]
        for category in categories:
            st.markdown(f"""
            <div style="color: #333333; margin: 0.3rem 0; font-size: 1rem;">
            • {category}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        try:
            prediction_stats = st.session_state.db.get_prediction_stats()
            training_stats = st.session_state.db.get_training_data_stats()
            
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{prediction_stats["total_predictions"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Predictions</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{len(training_stats["original_data"])}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Training Images</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{len(training_stats["retraining_sessions"])}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Training Sessions</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error loading statistics: {str(e)}")

def show_predict():
    st.markdown("""
    <div class="main-header">
        <h1>🔮 Furniture Prediction</h1>
        <p>Upload a furniture image to classify it instantly</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="prediction-card">', unsafe_allow_html=True)
        st.markdown("### 📸 Upload Image")
        
        st.markdown("""
        <div style="color: #666; margin-bottom: 1rem;">
        Choose a clear furniture image for classification
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a furniture image",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear image of furniture"
        )
        
        if uploaded_file is not None:
            try:
                # Read the uploaded file content
                image_bytes = uploaded_file.read()
                image = Image.open(io.BytesIO(image_bytes))
                
                # Verify it's a valid image
                image.verify()
                
                # Reopen the image since verify() closes it
                image_bytes = uploaded_file.getvalue()
                image = Image.open(io.BytesIO(image_bytes))
            
                display_image = image.copy()
                display_image.thumbnail((250, 250), Image.Resampling.LANCZOS)
                
                st.image(display_image, caption="Uploaded Image", width=250)
                
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    image.save(tmp_file.name, 'JPEG')
                    temp_path = tmp_file.name
            
            except Exception as e:
                st.error(f"Error loading image: {str(e)}")
                st.info("Please try uploading a different image file.")
                return
            
            if st.button("🔍 Classify Image", type="primary"):
                with st.spinner("Analyzing image..."):
                    try:
                        result = st.session_state.predictor.predict_image(temp_path)
                        
                        if result:
                            st.session_state.db.log_prediction(
                                image_path=uploaded_file.name,
                                predicted_class=result['predicted_class'],
                                confidence=result['confidence']
                            )
                            
                            with col2:
                                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                                st.markdown("### 🎯 Predicted Result")
                                st.markdown(f'<div class="predicted-class">{result["predicted_class"]}</div>', unsafe_allow_html=True)
                                st.markdown(f'<div class="confidence-score">Confidence: {result["confidence"]:.1%}</div>', unsafe_allow_html=True)
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                st.markdown("### 📊 Probability Breakdown")
                                prob_data = []
                                for i, class_name in enumerate(result['class_names']):
                                    prob_data.append({
                                        'Category': class_name,
                                        'Probability': result['all_predictions'][i]
                                    })
                                
                                prob_df = pd.DataFrame(prob_data)
                                fig = px.bar(
                                    prob_df,
                                    x='Probability',
                                    y='Category',
                                    orientation='h',
                                    color='Probability',
                                    color_continuous_scale=['#e5e5e5', '#8B6EFF']
                                )
                                fig.update_layout(
                                    showlegend=False,
                                    height=300,
                                    margin=dict(t=20, b=20, l=20, r=20)
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.error("❌ Failed to classify image. Please try again.")
                            
                            # Show debug info in development
                            with st.expander("🔍 Debug Information"):
                                st.write("**Possible causes:**")
                                st.write("- Model or label encoder loading issue")
                                st.write("- Image preprocessing error") 
                                st.write("- TensorFlow/prediction error")
                                st.write("- File path or permissions issue")
                                
                                st.write("**Model status:**")
                                if hasattr(st.session_state, 'predictor'):
                                    st.write(f"- Model loaded: {st.session_state.predictor.model is not None}")
                                    st.write(f"- Label encoder loaded: {st.session_state.predictor.label_encoder is not None}")
                                    if st.session_state.predictor.label_encoder:
                                        st.write(f"- Label encoder classes: {list(st.session_state.predictor.label_encoder.classes_)}")
                    
                    except Exception as e:
                        st.error(f"❌ Prediction Error: {str(e)}")
                        
                        # Show debug info
                        with st.expander("🔍 Error Details"):
                            import traceback
                            st.code(traceback.format_exc())
                            
                            st.write("**System Information:**")
                            try:
                                import tensorflow as tf
                                st.write(f"- TensorFlow version: {tf.__version__}")
                            except:
                                st.write("- TensorFlow: Not available")
                            
                            st.write(f"- Python version: {os.sys.version}")
                            st.write(f"- Image path exists: {os.path.exists(temp_path) if 'temp_path' in locals() else 'Unknown'}")
                            
                        st.info("💡 **Tip**: Try uploading a different image or refresh the page to reload the model.")
                    
                    finally:
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_analytics():
    st.markdown("""
    <div class="main-header">
        <h1>📊 Analytics Dashboard</h1>
        <p>System performance and usage insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        prediction_stats = st.session_state.db.get_prediction_stats()
        training_stats = st.session_state.db.get_training_data_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{prediction_stats["total_predictions"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Predictions</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{len(training_stats["original_data"])}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Training Data</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            user_data_count = len(training_stats['user_data']) if len(training_stats['user_data']) > 0 else 0
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{user_data_count}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">User Data</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{len(training_stats["retraining_sessions"])}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Training Sessions</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        if prediction_stats['total_predictions'] > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                if len(prediction_stats['class_predictions']) > 0:
                    fig = px.bar(
                        prediction_stats['class_predictions'],
                        x='predicted_class',
                        y='count',
                        title="Predictions by Category",
                        color_discrete_sequence=['#8B6EFF']
                    )
                    fig.update_layout(
                        showlegend=False,
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if len(prediction_stats['avg_confidence']) > 0:
                    fig = px.bar(
                        prediction_stats['avg_confidence'],
                        x='predicted_class',
                        y='avg_confidence',
                        title="Average Confidence by Category",
                        color_discrete_sequence=['#7C3AED']
                    )
                    fig.update_layout(
                        showlegend=False,
                        height=400,
                        yaxis=dict(range=[0, 1])
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            if len(prediction_stats['predictions_over_time']) > 0:
                fig = px.line(
                    prediction_stats['predictions_over_time'],
                    x='date',
                    y='count',
                    title="Predictions Over Time",
                    markers=True,
                    color_discrete_sequence=['#8B6EFF']
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📈 Make some predictions to see analytics here!")
        
        # Model Training Overview Section
        st.markdown("---")
        st.markdown("### 🧠 Model Training Overview")
        
        try:
            training_sessions_data = st.session_state.db.get_all_training_sessions()
            sessions_df = training_sessions_data['sessions']
            
            if len(sessions_df) > 0:
                st.markdown("""
                <div style="color: #333333; margin-bottom: 1rem; font-size: 1.1rem;">
                Complete history of all model training sessions and their performance metrics.
                </div>
                """, unsafe_allow_html=True)
                
                # Training sessions summary
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Training sessions table
                    st.markdown("#### 📋 Training Sessions History")
                    
                    # Format the dataframe for display
                    display_df = sessions_df.copy()
                    display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                    display_df['final_accuracy'] = (display_df['final_accuracy'] * 100).round(1).astype(str) + '%'
                    display_df['training_time_minutes'] = display_df['training_time_minutes'].round(1).astype(str) + ' min'
                    
                    # Select and rename columns for display
                    display_columns = {
                        'session_name': 'Session Name',
                        'final_accuracy': 'Accuracy',
                        'training_time_minutes': 'Training Time',
                        'total_data_count': 'Total Images',
                        'user_data_count': 'User Images',
                        'created_at': 'Date Created'
                    }
                    
                    display_df = display_df[list(display_columns.keys())].rename(columns=display_columns)
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Session Name": st.column_config.TextColumn("Session Name", width="medium"),
                            "Accuracy": st.column_config.TextColumn("Accuracy", width="small"),
                            "Training Time": st.column_config.TextColumn("Training Time", width="small"),
                            "Total Images": st.column_config.NumberColumn("Total Images", width="small"),
                            "User Images": st.column_config.NumberColumn("User Images", width="small"),
                            "Date Created": st.column_config.TextColumn("Date Created", width="medium")
                        }
                    )
                
                with col2:
                    # Training statistics
                    st.markdown("#### 📊 Training Statistics")
                    
                    # Total sessions
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-value">{len(sessions_df)}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="metric-label">Total Sessions</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Average accuracy
                    avg_accuracy = sessions_df['final_accuracy'].mean()
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-value">{avg_accuracy:.1%}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="metric-label">Average Accuracy</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Best accuracy
                    best_accuracy = sessions_df['final_accuracy'].max()
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-value">{best_accuracy:.1%}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="metric-label">Best Accuracy</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Total training time
                    total_time = sessions_df['training_time_minutes'].sum()
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-value">{total_time:.1f}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="metric-label">Total Training Time (min)</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Training performance over time
                if len(sessions_df) > 1:
                    st.markdown("#### 📈 Training Performance Over Time")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Accuracy over time
                        sessions_df['created_at'] = pd.to_datetime(sessions_df['created_at'])
                        fig_acc = px.line(
                            sessions_df.sort_values('created_at'),
                            x='created_at',
                            y='final_accuracy',
                            title="Model Accuracy Over Time",
                            markers=True,
                            color_discrete_sequence=['#8B6EFF']
                        )
                        fig_acc.update_layout(
                            height=350,
                            yaxis=dict(range=[0, 1], tickformat='.1%'),
                            xaxis_title="Training Date",
                            yaxis_title="Final Accuracy"
                        )
                        st.plotly_chart(fig_acc, use_container_width=True)
                    
                    with col2:
                        # Training time over sessions
                        fig_time = px.bar(
                            sessions_df.sort_values('created_at'),
                            x='session_name',
                            y='training_time_minutes',
                            title="Training Time by Session",
                            color_discrete_sequence=['#7C3AED']
                        )
                        fig_time.update_layout(
                            height=350,
                            xaxis_title="Session Name",
                            yaxis_title="Training Time (minutes)",
                            xaxis={'tickangle': 45}
                        )
                        st.plotly_chart(fig_time, use_container_width=True)
                
                # Data usage analysis
                st.markdown("#### 📊 Training Data Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Data composition chart
                    sessions_df['original_data_count'] = sessions_df['total_data_count'] - sessions_df['user_data_count']
                    
                    data_composition = pd.DataFrame({
                        'Session': sessions_df['session_name'],
                        'Original Data': sessions_df['original_data_count'],
                        'User Data': sessions_df['user_data_count']
                    })
                    
                    data_melted = data_composition.melt(
                        id_vars='Session',
                        value_vars=['Original Data', 'User Data'],
                        var_name='Data Type',
                        value_name='Count'
                    )
                    
                    fig_data = px.bar(
                        data_melted,
                        x='Session',
                        y='Count',
                        color='Data Type',
                        title="Data Composition by Session",
                        color_discrete_sequence=['#8B6EFF', '#7C3AED']
                    )
                    fig_data.update_layout(
                        height=350,
                        xaxis={'tickangle': 45},
                        xaxis_title="Training Session",
                        yaxis_title="Number of Images"
                    )
                    st.plotly_chart(fig_data, use_container_width=True)
                
                with col2:
                    # Accuracy vs Data Size scatter plot
                    fig_scatter = px.scatter(
                        sessions_df,
                        x='total_data_count',
                        y='final_accuracy',
                        size='user_data_count',
                        hover_data=['session_name', 'training_time_minutes'],
                        title="Accuracy vs Total Data Size",
                        color_discrete_sequence=['#8B6EFF']
                    )
                    fig_scatter.update_layout(
                        height=350,
                        xaxis_title="Total Training Images",
                        yaxis_title="Final Accuracy",
                        yaxis=dict(tickformat='.1%')
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)
                
            else:
                st.info("🧠 No training sessions found. Start by retraining the model to see training analytics here!")
                
        except Exception as training_error:
            st.error(f"Error loading training sessions: {str(training_error)}")
            
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

def show_retrain():
    st.markdown("""
    <div class="main-header">
        <h1>🔄 Model Retraining</h1>
        <p>Upload your own data to improve the model</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show training status if in progress or completed
    if st.session_state.get('training_in_progress', False):
        st.error("⏳ **TRAINING IN PROGRESS - DO NOT NAVIGATE AWAY**")
        st.info("Please wait while the model is being trained. Navigation is disabled to prevent interruption.")
        
        # Show current session info
        if st.session_state.get('training_session_id'):
            st.info(f"🔄 Training Session: {st.session_state.training_session_id}")
        
        if st.button("🛑 Cancel Training", type="secondary"):
            st.session_state.training_in_progress = False
            st.session_state.training_completed = False
            st.rerun()
        return
    
    # Prominent display for completed training
    if st.session_state.get('training_completed', False) and st.session_state.get('training_results'):
        st.balloons()  # Celebration effect
        
        # Large success banner
        st.markdown("""
        <div style="background: linear-gradient(90deg, #10b981 0%, #059669 100%); 
                    padding: 2rem; border-radius: 15px; color: white; text-align: center; 
                    margin: 1rem 0; box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);">
            <h2 style="color: white !important; margin: 0; font-size: 2rem;">
                🎉 TRAINING COMPLETED SUCCESSFULLY! 🎉
            </h2>
            <p style="color: rgba(255, 255, 255, 0.9) !important; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
                Your model has been retrained and is ready to use!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        results = st.session_state.training_results
        
        # Training results metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{results["final_accuracy"]:.1%}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Final Accuracy</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{results["training_time"]:.1f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Training Time (min)</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{results["total_data_count"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Data Used</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{results["session_name"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Session Name</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Action buttons
        st.markdown("### 🚀 What's Next?")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔮 **Test New Model**", type="primary", use_container_width=True):
                st.session_state.current_page = 'Predict'
                st.rerun()
        
        with col2:
            if st.button("📊 **View Analytics**", type="secondary", use_container_width=True):
                st.session_state.current_page = 'Analytics'
                st.rerun()
        
        with col3:
            if st.button("🆕 **New Training Session**", type="secondary", use_container_width=True):
                # Clear training state for new session
                st.session_state.training_completed = False
                st.session_state.training_results = None
                st.session_state.training_session_id = None
                st.session_state.last_training_page = None
                st.session_state.selected_files = []
                st.session_state.file_labels = {}
                st.rerun()
        
        # Show session persistence info
        if results.get('completed_at'):
            st.info(f"🕐 Training completed at: {results['completed_at']}")
        
        st.markdown("---")
        st.markdown("### 📝 Training Session Details")
        
        # Display training session info
        session_info = {
            "Session ID": results.get('session_id', 'N/A'),
            "Session Name": results.get('session_name', 'N/A'),
            "Final Accuracy": f"{results['final_accuracy']:.2%}",
            "Training Duration": f"{results['training_time']:.2f} minutes",
            "Total Training Data": f"{results['total_data_count']} images",
            "Completed At": results.get('completed_at', 'N/A')
        }
        
        for key, value in session_info.items():
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"**{key}:**")
            with col2:
                st.markdown(value)
        
        # Clear results button
        st.markdown("---")
        if st.button("�️ Clear Results and Start Fresh", type="secondary"):
            st.session_state.training_completed = False
            st.session_state.training_results = None
            st.session_state.training_session_id = None
            st.session_state.last_training_page = None
            st.session_state.selected_files = []
            st.session_state.file_labels = {}
            st.rerun()
        
        return  # Don't show the upload interface when results are displayed
    
    st.markdown("### 📤 Upload Training Images")
    st.markdown("""
    <div style="color: #333333; margin-bottom: 1rem; font-size: 1.1rem;">
    Upload furniture images with labels to retrain the model with your data combined with existing training data.
    </div>
    """, unsafe_allow_html=True)
    
    # Show deployment-specific warnings
    if IS_DEPLOYED:
        st.warning("""
        **⚠️ Deployment Environment Detected**
        - Training epochs will be limited to 5 to prevent timeout
        - Use fewer images (5-20) for optimal performance
        - Training may take 2-5 minutes depending on data size
        """)
    
    # Show training requirements
    st.info("""
    **📋 Training Requirements:**
    - Minimum 5 images to upload
    - Each category should have at least 2 images for best results
    - Combined with existing data, total should be at least 10 images
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "Choose furniture images",
            type=['jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            help="Upload multiple images for training"
        )
        
        if uploaded_files:
            # Get current file names to avoid duplicates
            current_file_names = [f.name for f in st.session_state.selected_files]
            
            for file in uploaded_files:
                if file.name not in current_file_names:
                    st.session_state.selected_files.append(file)
                    st.session_state.file_labels[file.name] = 'Chair'
        
        # Display selected files with remove option
        if st.session_state.selected_files:
            st.success(f"📁 Selected {len(st.session_state.selected_files)} images")
            st.markdown("**Selected Images:**")
            
            # Create a grid layout for images
            num_cols = min(4, len(st.session_state.selected_files))
            cols = st.columns(num_cols)
            
            files_to_remove = []
            
            for i, selected_file in enumerate(st.session_state.selected_files):
                col_idx = i % num_cols
                with cols[col_idx]:
                    try:
                        # Read the uploaded file content properly
                        image_bytes = selected_file.read()
                        image = Image.open(io.BytesIO(image_bytes))
                        
                        # Reset file position for later use
                        selected_file.seek(0)
                        
                        image.thumbnail((120, 120), Image.Resampling.LANCZOS)
                        st.image(image, caption=selected_file.name[:15], width=120)
                        
                        if st.button("❌ Remove", key=f"remove_{selected_file.name}_{i}"):
                            files_to_remove.append(i)  # Store index instead of file object
                    except Exception as e:
                        st.error(f"Error loading {selected_file.name}: {str(e)}")
            
            # Remove files by index (in reverse order to maintain correct indices)
            if files_to_remove:
                for index in sorted(files_to_remove, reverse=True):
                    if index < len(st.session_state.selected_files):
                        file_to_remove = st.session_state.selected_files[index]
                        if file_to_remove.name in st.session_state.file_labels:
                            del st.session_state.file_labels[file_to_remove.name]
                        st.session_state.selected_files.pop(index)
                st.rerun()
            
            if len(st.session_state.selected_files) > num_cols:
                remaining = len(st.session_state.selected_files) - num_cols
                st.info(f"... and {remaining} more images (scroll down to see all)")
        
        if st.session_state.selected_files:
            if st.button("🗑️ Clear All Images", type="secondary"):
                st.session_state.selected_files = []
                st.session_state.file_labels = {}
                st.rerun()
    
    with col2:
        st.markdown("### ⚙️ Training Settings")
        
        st.markdown("""
        <div style="color: #666; margin-bottom: 1rem;">
        Configure your training session parameters
        </div>
        """, unsafe_allow_html=True)
        
        session_name = st.text_input(
            "Session Name",
            value=f"Training_{datetime.now().strftime('%m%d_%H%M')}",
            help="Name for this training session"
        )
        
        max_epochs = 5 if IS_DEPLOYED else 20
        epochs = st.slider(
            "Training Epochs",
            min_value=1,
            max_value=max_epochs,
            value=min(10, max_epochs),
            help=f"Number of training epochs (limited to {max_epochs} in deployment)"
        )
        
        clear_user_data = st.checkbox(
            "Clear previous user data",
            value=True,
            help="Remove previously uploaded user data"
        )
    
    if st.session_state.selected_files:
        st.markdown("### 🏷️ Assign Labels")
        
        st.markdown("""
        <div style="color: #666; margin-bottom: 1rem;">
        Select the correct category for each uploaded image
        </div>
        """, unsafe_allow_html=True)
        
        class_names = ['Almirah', 'Chair', 'Fridge', 'Table', 'TV']
        
        with st.form("label_assignment"):
            st.markdown("**Label Assignment:**")
            
            for i, selected_file in enumerate(st.session_state.selected_files):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    try:
                        # Read the uploaded file content properly
                        image_bytes = selected_file.read()
                        image = Image.open(io.BytesIO(image_bytes))
                        
                        # Reset file position for later use
                        selected_file.seek(0)
                        
                        image.thumbnail((100, 100), Image.Resampling.LANCZOS)
                        st.image(image, width=100)
                    except Exception as e:
                        st.error(f"Error loading image: {str(e)}")
                
                with col2:
                    current_label = st.session_state.file_labels.get(selected_file.name, 'Chair')
                    current_index = class_names.index(current_label) if current_label in class_names else 1
                    
                    new_label = st.selectbox(
                        f"Category for {selected_file.name[:25]}...",
                        class_names,
                        index=current_index,
                        key=f"label_{selected_file.name}_{i}"
                    )
                    st.session_state.file_labels[selected_file.name] = new_label
            
            training_button_text = "🚀 Start Training"
            if IS_DEPLOYED:
                training_button_text += f" ({epochs} epochs, ~{len(st.session_state.selected_files) * 0.1:.1f} min)"
            
            if st.form_submit_button(training_button_text, type="primary"):
                if len(st.session_state.selected_files) >= 5:
                    start_retraining(st.session_state.selected_files, st.session_state.file_labels, session_name, epochs, clear_user_data)
                else:
                    st.error("Please select at least 5 images for training.")

def start_retraining(uploaded_files, labels, session_name, epochs, clear_user_data):
    if len(uploaded_files) < 5:
        st.error("⚠️ Minimum 5 images required for training. Please upload more images.")
        return
    
    label_counts = {}
    for label in labels.values():
        label_counts[label] = label_counts.get(label, 0) + 1
    
    min_samples = min(label_counts.values()) if label_counts else 0
    if min_samples < 2:
        st.warning(f"⚠️ Each category should have at least 2 images for proper training. Current minimum: {min_samples}")
        st.write("**Current distribution:**")
        for label, count in label_counts.items():
            st.write(f"• {label}: {count} images")
        
        if not st.checkbox("Continue training anyway (may have reduced accuracy)", key="force_train"):
            return
    
    # Initialize training state
    if 'training_in_progress' not in st.session_state:
        st.session_state.training_in_progress = False
    
    if 'training_completed' not in st.session_state:
        st.session_state.training_completed = False
        
    if 'training_results' not in st.session_state:
        st.session_state.training_results = None
    
    # Prevent multiple training sessions
    if st.session_state.training_in_progress:
        st.warning("⏳ Training is already in progress. Please wait...")
        return
    
    # Show results if training was completed
    if st.session_state.training_completed and st.session_state.training_results:
        st.success("🎉 Model Training Completed!")
        
        results = st.session_state.training_results
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Final Accuracy", f"{results['final_accuracy']:.1%}")
        with col2:
            st.metric("Training Time", f"{results['training_time']:.1f} min")
        with col3:
            st.metric("Total Data Used", results['total_data_count'])
        
        st.info("🔄 Model updated! New predictions will use the retrained model.")
        
        # Reset training state
        if st.button("🔄 Start New Training Session"):
            st.session_state.training_completed = False
            st.session_state.training_results = None
            st.rerun()
        return
    
    # Start training
    st.session_state.training_in_progress = True
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Reduce epochs for deployed environment to prevent timeout
        adjusted_epochs = min(epochs, 5) if 'STREAMLIT_SHARING' in os.environ or 'RENDER' in os.environ else epochs
        if adjusted_epochs < epochs:
            st.warning(f"⚠️ Reducing epochs from {epochs} to {adjusted_epochs} for deployment environment")
        
        if clear_user_data:
            status_text.text("🧹 Clearing previous user data...")
            st.session_state.db.clear_user_data()
            progress_bar.progress(10)
        
        status_text.text("💾 Processing uploaded images...")
        
        temp_dir = tempfile.mkdtemp()
        image_paths = []
        class_names_list = []
        class_ids = []
        
        class_name_to_id = {
            'Almirah': 0, 'Chair': 1, 'Fridge': 2, 'Table': 3, 'TV': 4
        }
        
        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            
            # Reset file position and read content
            uploaded_file.seek(0)
            file_content = uploaded_file.read()
            
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Reset file position again for potential future use
            uploaded_file.seek(0)
            
            image_paths.append(file_path)
            class_name = labels[uploaded_file.name]
            class_names_list.append(class_name)
            class_ids.append(class_name_to_id[class_name])
        
        st.session_state.db.add_user_data(image_paths, class_names_list, class_ids)
        progress_bar.progress(30)
        
        status_text.text("🔄 Preparing training data...")
        combined_data = st.session_state.db.get_combined_training_data()
        
        requirements_met, message = st.session_state.db.check_training_data_requirements()
        if not requirements_met:
            st.error(f"❌ Training failed: {message}")
            progress_bar.progress(0)
            status_text.text("❌ Training requirements not met!")
            st.session_state.training_in_progress = False
            return
        
        progress_bar.progress(40)
        
        status_text.text(f"🧠 Training model ({adjusted_epochs} epochs)...")
        
        model_save_path = f"models/{session_name}.h5"
        os.makedirs("models", exist_ok=True)
        
        # Add timeout protection for training
        import time
        start_time = time.time()
        
        training_results = st.session_state.trainer.train_model(
            combined_data, 
            epochs=adjusted_epochs, 
            model_save_path=model_save_path
        )
        
        elapsed_time = time.time() - start_time
        
        progress_bar.progress(80)
        
        status_text.text("💾 Saving results...")
        
        session_id = st.session_state.db.log_retraining_session(
            session_name=session_name,
            original_count=training_results['original_count'],
            user_count=training_results['user_count'],
            total_count=len(combined_data),
            final_accuracy=training_results['final_accuracy'],
            training_time=training_results['training_time'],
            model_path=model_save_path
        )
        
        metrics = {
            'final_accuracy': training_results['final_accuracy'],
            'training_time_minutes': training_results['training_time']
        }
        st.session_state.db.log_metrics(session_id, metrics)
        
        # Create new predictor instance for retrained model
        try:
            st.session_state.predictor = FurniturePredictor(
                model_path=model_save_path,
                label_encoder_path=model_save_path.replace('.h5', '_label_encoder.pkl')
            )
        except Exception as pred_error:
            st.warning(f"Warning: Could not update predictor: {pred_error}")
        
        # Store results in session state with unique identifier
        training_session_id = f"{session_name}_{int(time.time())}"
        st.session_state.training_session_id = training_session_id
        st.session_state.training_results = {
            'final_accuracy': training_results['final_accuracy'],
            'training_time': training_results['training_time'],
            'total_data_count': len(combined_data),
            'session_name': session_name,
            'session_id': training_session_id,
            'completed_at': datetime.now().isoformat()
        }
        
        progress_bar.progress(100)
        status_text.text("✅ Training completed successfully!")
        
        # Mark training as completed and ensure we stay on retrain page
        st.session_state.training_completed = True
        st.session_state.training_in_progress = False
        st.session_state.last_training_page = 'Retrain'
        st.session_state.current_page = 'Retrain'  # Force stay on retrain page
        
        # Clear the uploaded files after successful training
        st.session_state.selected_files = []
        st.session_state.file_labels = {}
        
        # Add a delay to ensure session state is properly saved
        time.sleep(2)
        
        # Success message before rerun
        st.success("🎉 Training completed! Results will be displayed...")
        
        # Force rerun to show results
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Training failed: {str(e)}")
        
        # Show more specific error information
        if "timeout" in str(e).lower():
            st.error("🕐 Training timed out. Try reducing the number of epochs or images.")
        elif "memory" in str(e).lower():
            st.error("� Out of memory. Try reducing the number of images or using smaller images.")
        else:
            st.error("💥 Unexpected error occurred during training.")
        
        with st.expander("🔍 Error Details"):
            import traceback
            st.code(traceback.format_exc())
        
        progress_bar.progress(0)
        status_text.text("❌ Training failed!")
        st.session_state.training_in_progress = False
        st.session_state.training_completed = False
    
    finally:
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def main():
    navigation()
    
    if st.session_state.current_page == 'Home':
        show_home()
    elif st.session_state.current_page == 'Predict':
        show_predict()
    elif st.session_state.current_page == 'Analytics':
        show_analytics()
    elif st.session_state.current_page == 'Retrain':
        show_retrain()
    
    st.markdown("""
    <div class="footer">
        <p>🪑 Furniture AI - Powered by Deep Learning</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()