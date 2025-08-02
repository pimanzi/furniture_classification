# Furniture Classification System

A comprehensive deep learning application for classifying furniture images with advanced performance monitoring and load testing capabilities.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Model Performance](#model-performance)
- [Load Testing Results](#load-testing-results)
- [Database Schema](#database-schema)
- [API Documentation](#api-documentation)
- [Technology Stack](#technology-stack)
- [Development](#development)
- [Performance Monitoring](#performance-monitoring)
- [Deployment](#deployment)
- [Contributing](#contributing)

## Overview

This project implements a modern furniture classification system using deep learning techniques. The system can classify furniture images into five categories: Almirah, Chair, Fridge, Table, and TV. Built with EfficientNetB0 architecture and transfer learning, it provides high accuracy classification with a user-friendly web interface.

**Demo Link**: [Insert Demo Link Here]

**Deployed Application**: [Insert Deployment Link Here]

## Features

### Core Functionality

- **Real-time Image Classification**: Upload and classify furniture images instantly
- **Five Furniture Categories**: Almirah, Chair, Fridge, Table, TV
- **Model Retraining**: Upload custom datasets to improve model accuracy
- **Analytics Dashboard**: Comprehensive performance metrics and usage statistics
- **Prediction History**: Track all classification results with confidence scores

### Advanced Features

- **Load Testing Suite**: Comprehensive performance testing with Locust
- **Real-time Monitoring**: System resource and application performance monitoring
- **Database Management**: SQLite database for data persistence and analytics
- **REST API**: FastAPI endpoints for programmatic access
- **Responsive UI**: Modern interface with dark/light theme support

## Project Structure

```
furniture_classification/
├── app.py                          # Main Streamlit application
├── simple_api.py                   # FastAPI server for load testing
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── src/                            # Source code modules
│   ├── __init__.py
│   ├── models/
│   │   └── furniture_predictor.py  # Model prediction logic
│   └── utils/
│       ├── database.py             # Database management
│       └── model_utils.py          # Model utilities
├── database/                       # Database files
│   └── furniture_classification.db # SQLite database
├── scripts/                        # Shell scripts
│   ├── run_app.sh                  # Application launcher
│   └── check_requirements.py      # Dependency checker
├── notebooks/                      # Jupyter notebooks
│   ├── furniture_model_classification.ipynb
│   └── processing.ipynb
├── models/                         # Trained model files
├── load_testing/                   # Load testing suite
│   ├── locustfile.py              # Locust test scenarios
│   ├── performance_monitor.py      # Real-time monitoring
│   ├── dashboard.py               # Results visualization
│   ├── run_load_tests.sh          # Automated test runner
│   ├── demo.py                    # Simple load test demo
│   ├── results/                   # Test results and reports
│   └── README.md                  # Load testing documentation
├── Data/                          # Training datasets
└── processed_data/               # Processed training data
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git

### Step-by-Step Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/pimanzi/furniture_classification.git
   cd furniture_classification
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install load testing dependencies**

   ```bash
   cd load_testing
   pip install -r requirements.txt
   cd ..
   ```

5. **Verify installation**

   ```bash
   python scripts/check_requirements.py
   ```

6. **Initialize database**
   ```bash
   python -c "from src.utils.database import FurnitureDB; FurnitureDB()"
   ```

## Usage

### Running the Main Application

1. **Start the Streamlit application**

   ```bash
   streamlit run app.py --server.port 8515
   ```

2. **Access the application**
   Open your browser and navigate to: `http://localhost:8515`

### Using the API Server

1. **Start the FastAPI server**

   ```bash
   python simple_api.py
   ```

2. **API endpoints available at**
   - `http://localhost:8517/` - Health check
   - `http://localhost:8517/predict` - Image classification
   - `http://localhost:8517/analytics` - Usage analytics

### Running the Automated Script

```bash
chmod +x scripts/run_app.sh
./scripts/run_app.sh
```

## Model Performance

### Architecture

- **Base Model**: EfficientNetB0
- **Transfer Learning**: Pre-trained on ImageNet
- **Fine-tuning**: Custom classification head for furniture categories
- **Input Size**: 224x224 RGB images
- **Output**: 5-class classification with confidence scores

### Performance Metrics

- **Test Accuracy**: 99.80%
- **Weighted Precision**: 99.80%
- **Weighted Recall**: 99.80%
- **Weighted F1-Score**: 99.80%
- **Average Inference Time**: 2-4ms per image
- **Model Size**: 21.2 MB

### Class-wise Performance

| Category | Precision | Recall | F1-Score |
| -------- | --------- | ------ | -------- |
| Almirah  | 1.0000    | 1.0000 | 1.0000   |
| Chair    | 1.0000    | 0.9899 | 0.9949   |
| Fridge   | 1.0000    | 1.0000 | 1.0000   |
| Table    | 0.9900    | 1.0000 | 0.9950   |
| TV       | 1.0000    | 1.0000 | 1.0000   |

## Load Testing Results

### Test Configuration

- **Testing Framework**: Locust
- **Test Duration**: 90 seconds
- **Virtual Users**: 15 concurrent users
- **Spawn Rate**: 3 users per second

### Performance Results

- **Total Requests**: 1,409
- **Average Response Time**: 2ms
- **95th Percentile Response Time**: 4ms
- **99th Percentile Response Time**: 8ms
- **Request Rate**: 15.77 requests/second
- **Success Rate**: 100% (API endpoints)
- **Throughput**: Sustained 15+ RPS under load

### Load Testing Scenarios

1. **Normal Users** (Weight: 3): 2-5 second wait times
2. **Heavy Load Users** (Weight: 2): 0.5-2 second wait times
3. **Stress Test Users** (Weight: 1): 0.1-0.5 second wait times

### System Resource Usage

- **CPU Usage**: < 15% during peak load
- **Memory Usage**: < 1.2GB
- **Response Time Stability**: Consistent under load
- **No Memory Leaks**: Detected during extended testing

## Database Schema

### Core Tables

- **training_data**: Stores original training dataset information including image paths and class labels
- **predictions**: Logs all model predictions with confidence scores and timestamps
- **retraining_sessions**: Tracks model retraining sessions with performance metrics
- **model_metrics**: Stores detailed performance metrics for each training session
- **user_data**: Manages user-uploaded images for model improvement

## API Documentation

### FastAPI Endpoints

#### GET /

- **Description**: Health check endpoint
- **Response**: Application status and health information

#### POST /predict

- **Description**: Classify uploaded furniture image
- **Parameters**:
  - `file`: Image file (multipart/form-data)
- **Response**:
  ```json
  {
    "prediction": "chair",
    "confidence": 0.95,
    "filename": "image.jpg",
    "status": "success"
  }
  ```

#### GET /analytics

- **Description**: Retrieve usage analytics and metrics
- **Response**: Analytics data including prediction counts and accuracy metrics

## Technology Stack

### Core Technologies

- **Python 3.8+**: Programming language
- **TensorFlow 2.16+**: Deep learning framework
- **Streamlit 1.28+**: Web application framework
- **FastAPI**: REST API framework
- **SQLite3**: Database management

### Machine Learning

- **EfficientNetB0**: Base neural network architecture
- **Transfer Learning**: Pre-trained weights from ImageNet
- **scikit-learn**: Model evaluation and metrics
- **OpenCV**: Image processing
- **Pillow**: Image manipulation

### Data Handling

- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Matplotlib/Seaborn**: Data visualization
- **Plotly**: Interactive visualizations

### Testing and Monitoring

- **Locust**: Load testing framework
- **psutil**: System monitoring
- **requests**: HTTP client for testing

## Development

### Setting up Development Environment

1. **Install development dependencies**

   ```bash
   pip install -r requirements.txt
   pip install jupyter notebook
   ```

2. **Run Jupyter notebooks**

   ```bash
   jupyter notebook
   ```

3. **Code structure guidelines**
   - Follow PEP 8 style guidelines
   - Use type hints where applicable
   - Document functions with docstrings
   - Maintain modular code structure

### Adding New Features

1. **Model improvements**: Modify `src/models/furniture_predictor.py`
2. **Database changes**: Update `src/utils/database.py`
3. **UI enhancements**: Modify `app.py` and add CSS in the styling section
4. **API extensions**: Update `simple_api.py`

## Performance Monitoring

### Load Testing Suite

The project includes a comprehensive load testing suite located in `load_testing/`:

#### Running Load Tests

```bash
cd load_testing
chmod +x run_load_tests.sh
./run_load_tests.sh
```

#### Real-time Monitoring

```bash
python load_testing/performance_monitor.py --duration 300
```

#### Results Dashboard

```bash
streamlit run load_testing/dashboard.py --server.port 8516
```

### Monitoring Metrics

- **Application Performance**: Response times, throughput, error rates
- **System Resources**: CPU, memory, disk, network usage
- **Model Performance**: Inference time, accuracy under load
- **Database Performance**: Query execution times

## Deployment

### Local Deployment

```bash
streamlit run app.py --server.port 8515
```

### Environment Variables

```bash
export STREAMLIT_SERVER_PORT=8515
export DATABASE_PATH=database/furniture_classification.db
export MODEL_PATH=models/
```

## Contributing

### Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Reporting Issues

- Use the GitHub issue tracker
- Provide detailed reproduction steps
- Include system information and error logs
- Attach relevant screenshots or examples

---

**Project Status**: Active Development  
**License**: MIT  
**Maintainer**: [Your Name]  
**Contact**: [Your Email]
