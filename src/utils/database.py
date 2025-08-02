import sqlite3
import pandas as pd
import numpy as np
import os
from datetime import datetime
import pickle
import json

class FurnitureDB:
    def __init__(self, db_path='database/furniture_classification.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path TEXT NOT NULL,
                class_name TEXT NOT NULL,
                class_id INTEGER NOT NULL,
                dataset_type TEXT DEFAULT 'original',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path TEXT NOT NULL,
                class_name TEXT NOT NULL,
                class_id INTEGER NOT NULL,
                uploaded_by TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path TEXT NOT NULL,
                true_class TEXT,
                predicted_class TEXT NOT NULL,
                confidence REAL NOT NULL,
                model_version TEXT DEFAULT 'v1.0',
                prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS retraining_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                original_data_count INTEGER,
                user_data_count INTEGER,
                total_data_count INTEGER,
                final_accuracy REAL,
                training_time_minutes REAL,
                model_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                class_name TEXT,
                FOREIGN KEY (session_id) REFERENCES retraining_sessions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully!")
    
    def populate_original_data(self, paths_train, paths_val, paths_test, 
                             y_train, y_val, y_test, class_names):
        """Populate database with original training data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM training_data WHERE dataset_type = "original"')
        
        data_to_insert = []
        
        # Add training data
        for path, label_onehot in zip(paths_train, y_train):
            class_id = np.argmax(label_onehot)
            class_name = class_names[class_id]
            data_to_insert.append((path, class_name, class_id, 'train'))
        
        # Add validation data
        for path, label_onehot in zip(paths_val, y_val):
            class_id = np.argmax(label_onehot)
            class_name = class_names[class_id]
            data_to_insert.append((path, class_name, class_id, 'val'))
        
        # Add test data
        for path, label_onehot in zip(paths_test, y_test):
            class_id = np.argmax(label_onehot)
            class_name = class_names[class_id]
            data_to_insert.append((path, class_name, class_id, 'test'))
        
        cursor.executemany('''
            INSERT INTO training_data (image_path, class_name, class_id, dataset_type)
            VALUES (?, ?, ?, ?)
        ''', data_to_insert)
        
        conn.commit()
        conn.close()
        print(f"Populated database with {len(data_to_insert)} original training samples")
    
    def add_user_data(self, image_paths, class_names, class_ids, uploaded_by='user'):
        """Add user uploaded data for retraining"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data_to_insert = []
        for path, class_name, class_id in zip(image_paths, class_names, class_ids):
            data_to_insert.append((path, class_name, class_id, uploaded_by))
        
        cursor.executemany('''
            INSERT INTO user_data (image_path, class_name, class_id, uploaded_by)
            VALUES (?, ?, ?, ?)
        ''', data_to_insert)
        
        conn.commit()
        conn.close()
        print(f"Added {len(data_to_insert)} user data samples")
    
    def log_prediction(self, image_path, predicted_class, confidence, 
                      true_class=None, model_version='v1.0'):
        """Log a prediction made by the model"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions (image_path, true_class, predicted_class, confidence, model_version)
            VALUES (?, ?, ?, ?, ?)
        ''', (image_path, true_class, predicted_class, confidence, model_version))
        
        conn.commit()
        conn.close()
    
    def log_retraining_session(self, session_name, original_count, user_count, 
                             total_count, final_accuracy, training_time, model_path):
        """Log a retraining session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO retraining_sessions 
            (session_name, original_data_count, user_data_count, total_data_count, 
             final_accuracy, training_time_minutes, model_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session_name, original_count, user_count, total_count, 
              final_accuracy, training_time, model_path))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id
    
    def log_metrics(self, session_id, metrics_dict):
        """Log performance metrics for a retraining session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data_to_insert = []
        for metric_name, value in metrics_dict.items():
            if isinstance(value, dict):  # Per-class metrics
                for class_name, class_value in value.items():
                    data_to_insert.append((session_id, metric_name, float(class_value), class_name))
            else:  # Overall metrics
                data_to_insert.append((session_id, metric_name, float(value), None))
        
        cursor.executemany('''
            INSERT INTO model_metrics (session_id, metric_name, metric_value, class_name)
            VALUES (?, ?, ?, ?)
        ''', data_to_insert)
        
        conn.commit()
        conn.close()
    
    def get_prediction_stats(self):
        """Get prediction statistics for visualization"""
        conn = sqlite3.connect(self.db_path)
        
        # Total predictions
        total_predictions = pd.read_sql_query(
            'SELECT COUNT(*) as total FROM predictions', conn
        ).iloc[0]['total']
        
        # Predictions by class
        class_predictions = pd.read_sql_query('''
            SELECT predicted_class, COUNT(*) as count 
            FROM predictions 
            GROUP BY predicted_class 
            ORDER BY count DESC
        ''', conn)
        
        # Predictions over time
        predictions_over_time = pd.read_sql_query('''
            SELECT DATE(prediction_time) as date, COUNT(*) as count
            FROM predictions
            GROUP BY DATE(prediction_time)
            ORDER BY date
        ''', conn)
        
        # Average confidence by class
        avg_confidence = pd.read_sql_query('''
            SELECT predicted_class, AVG(confidence) as avg_confidence
            FROM predictions
            GROUP BY predicted_class
        ''', conn)
        
        conn.close()
        
        return {
            'total_predictions': total_predictions,
            'class_predictions': class_predictions,
            'predictions_over_time': predictions_over_time,
            'avg_confidence': avg_confidence
        }
    
    def get_training_data_stats(self):
        """Get training data statistics"""
        conn = sqlite3.connect(self.db_path)
        
        # Original data distribution
        original_data = pd.read_sql_query('''
            SELECT class_name, COUNT(*) as count
            FROM training_data
            WHERE dataset_type IN ('train', 'val', 'test')
            GROUP BY class_name
        ''', conn)
        
        # User data distribution
        user_data = pd.read_sql_query('''
            SELECT class_name, COUNT(*) as count
            FROM user_data
            GROUP BY class_name
        ''', conn)
        
        # Retraining sessions
        retraining_sessions = pd.read_sql_query('''
            SELECT session_name, final_accuracy, training_time_minutes, created_at
            FROM retraining_sessions
            ORDER BY created_at DESC
        ''', conn)
        
        conn.close()
        
        return {
            'original_data': original_data,
            'user_data': user_data,
            'retraining_sessions': retraining_sessions
        }
    
    def get_combined_training_data(self):
        """Get combined training data (original + user) for retraining"""
        conn = sqlite3.connect(self.db_path)
        
        # Get original training data
        original_data = pd.read_sql_query('''
            SELECT image_path, class_name, class_id
            FROM training_data
            WHERE dataset_type = 'train'
        ''', conn)
        
        # Get user data
        user_data = pd.read_sql_query('''
            SELECT image_path, class_name, class_id
            FROM user_data
        ''', conn)
        
        conn.close()
        
        # Combine datasets
        if len(user_data) > 0:
            combined_data = pd.concat([original_data, user_data], ignore_index=True)
        else:
            combined_data = original_data
        
        # Normalize class names and ensure consistent class IDs
        class_mapping = {
            'almirah': ('Almirah', 0),
            'chair': ('Chair', 1), 
            'fridge': ('Fridge', 2),
            'table': ('Table', 3),
            'tv': ('TV', 4),
            # Handle capitalized versions
            'Almirah': ('Almirah', 0),
            'Chair': ('Chair', 1),
            'Fridge': ('Fridge', 2), 
            'Table': ('Table', 3),
            'TV': ('TV', 4)
        }
        
        # Clean and normalize the data
        valid_rows = []
        for idx, row in combined_data.iterrows():
            class_name = str(row['class_name']).strip()
            if class_name in class_mapping:
                normalized_name, correct_id = class_mapping[class_name]
                valid_rows.append({
                    'image_path': row['image_path'],
                    'class_name': normalized_name,
                    'class_id': correct_id
                })
        
        # Create cleaned DataFrame
        cleaned_data = pd.DataFrame(valid_rows)
        
        print(f"Original combined data: {len(combined_data)} samples")  
        print(f"Cleaned data: {len(cleaned_data)} samples")
        
        if len(cleaned_data) > 0:
            print(f"Class distribution after cleaning:")
            print(cleaned_data['class_name'].value_counts())
        
        return cleaned_data
    
    def check_training_data_requirements(self):
        """Check if combined data meets minimum training requirements"""
        combined_data = self.get_combined_training_data()
        
        if len(combined_data) < 10:
            return False, f"Need at least 10 total images, currently have {len(combined_data)}"
        
        # Check class distribution
        class_counts = combined_data['class_name'].value_counts()
        min_samples = class_counts.min()  if len(class_counts) > 0 else 0
        
        if min_samples < 2:
            problematic_classes = class_counts[class_counts < 2].index.tolist() if len(class_counts) > 0 else []
            return False, f"Classes with insufficient data (need ≥2 each): {', '.join(problematic_classes)}"
        
        return True, "Training data requirements met"
    
    def clear_user_data(self):
        """Clear user uploaded data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_data')
        conn.commit()
        conn.close()
