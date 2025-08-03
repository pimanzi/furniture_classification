#!/usr/bin/env python3
"""
Load Testing Dashboard
Creates a comprehensive dashboard showing load testing results and performance metrics
"""

import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from pathlib import Path
import glob
from datetime import datetime


def load_performance_data():
    """Load performance monitoring data."""
    performance_dir = Path("load_testing/performance_monitoring")
    
    if not performance_dir.exists():
        return None
    
    # Find latest performance data
    json_files = glob.glob(str(performance_dir / "performance_metrics_*.json"))
    
    if not json_files:
        return None
    
    latest_file = max(json_files, key=lambda x: Path(x).stat().st_mtime)
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    return pd.DataFrame(data)


def load_locust_data():
    """Load Locust test results."""
    results_dir = Path("load_testing/results")
    
    if not results_dir.exists():
        return None
    
    # Find latest CSV files
    csv_files = glob.glob(str(results_dir / "*_stats.csv"))
    
    if not csv_files:
        return None
    
    # Load the most recent stats file
    latest_file = max(csv_files, key=lambda x: Path(x).stat().st_mtime)
    
    try:
        return pd.read_csv(latest_file)
    except Exception:
        return None


def create_performance_dashboard():
    """Create the main performance dashboard."""
    st.set_page_config(
        page_title="🧪 Load Testing Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("🧪 Furniture AI - Load Testing Dashboard")
    st.markdown("---")
    
    # Load data
    performance_df = load_performance_data()
    locust_df = load_locust_data()
    
    if performance_df is None and locust_df is None:
        st.error(" No load testing data found. Please run load tests first.")
        st.info("💡 Run `./load_testing/run_load_tests.sh` to generate test data")
        return
    
    # Sidebar with test information
    st.sidebar.title("📊 Test Information")
    
    if performance_df is not None:
        test_duration = performance_df['elapsed_time'].max()
        st.sidebar.metric("Test Duration", f"{test_duration:.1f} seconds")
        st.sidebar.metric("Data Points", len(performance_df))
        
        if 'app_available' in performance_df.columns:
            uptime = performance_df['app_available'].mean() * 100
            st.sidebar.metric("App Uptime", f"{uptime:.1f}%")
    
    # Main dashboard layout
    col1, col2 = st.columns(2)
    
    with col1:
        if performance_df is not None:
            st.subheader("🖥 System Performance")
            
            # CPU and Memory Usage
            fig_system = make_subplots(
                rows=2, cols=1,
                subplot_titles=('CPU Usage (%)', 'Memory Usage (%)'),
                vertical_spacing=0.1
            )
            
            fig_system.add_trace(
                go.Scatter(
                    x=performance_df['elapsed_time'],
                    y=performance_df['cpu_percent'],
                    mode='lines',
                    name='CPU %',
                    line=dict(color='red')
                ),
                row=1, col=1
            )
            
            fig_system.add_trace(
                go.Scatter(
                    x=performance_df['elapsed_time'],
                    y=performance_df['memory_percent'],
                    mode='lines',
                    name='Memory %',
                    line=dict(color='blue')
                ),
                row=2, col=1
            )
            
            fig_system.update_layout(height=400, showlegend=False)
            fig_system.update_xaxes(title_text="Time (seconds)")
            st.plotly_chart(fig_system, use_container_width=True)
    
    with col2:
        if performance_df is not None and 'response_time_ms' in performance_df.columns:
            st.subheader("⚡ Response Time")
            
            fig_response = go.Figure()
            fig_response.add_trace(
                go.Scatter(
                    x=performance_df['elapsed_time'],
                    y=performance_df['response_time_ms'],
                    mode='lines+markers',
                    name='Response Time',
                    line=dict(color='green'),
                    marker=dict(size=4)
                )
            )
            
            # Add threshold lines
            fig_response.add_hline(
                y=1000, line_dash="dash", line_color="orange",
                annotation_text="1s threshold"
            )
            fig_response.add_hline(
                y=5000, line_dash="dash", line_color="red",
                annotation_text="5s threshold"
            )
            
            fig_response.update_layout(
                height=400,
                xaxis_title="Time (seconds)",
                yaxis_title="Response Time (ms)"
            )
            st.plotly_chart(fig_response, use_container_width=True)
    
    # Locust Results Section
    if locust_df is not None:
        st.subheader("🐝 Locust Load Testing Results")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_requests = locust_df['Request Count'].sum() if 'Request Count' in locust_df.columns else 0
            st.metric("Total Requests", f"{total_requests:,}")
        
        with col2:
            failures = locust_df['Failure Count'].sum() if 'Failure Count' in locust_df.columns else 0
            st.metric("Failures", f"{failures:,}")
        
        with col3:
            if 'Average Response Time' in locust_df.columns:
                avg_response = locust_df['Average Response Time'].mean()
                st.metric("Avg Response Time", f"{avg_response:.0f}ms")
        
        with col4:
            if 'Requests/s' in locust_df.columns:
                rps = locust_df['Requests/s'].sum()
                st.metric("Requests/Second", f"{rps:.1f}")
        
        # Request distribution
        if 'Name' in locust_df.columns and 'Request Count' in locust_df.columns:
            fig_requests = px.bar(
                locust_df,
                x='Name',
                y='Request Count',
                title="Requests by Endpoint",
                color='Request Count',
                color_continuous_scale='blues'
            )
            fig_requests.update_layout(height=400)
            st.plotly_chart(fig_requests, use_container_width=True)
    
    # Detailed Metrics Section
    st.subheader("📈 Detailed Performance Metrics")
    
    if performance_df is not None:
        # Performance statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**CPU Statistics**")
            cpu_stats = performance_df['cpu_percent'].describe()
            st.write(f"Mean: {cpu_stats['mean']:.1f}%")
            st.write(f"Max: {cpu_stats['max']:.1f}%")
            st.write(f"Min: {cpu_stats['min']:.1f}%")
            st.write(f"Std: {cpu_stats['std']:.1f}%")
        
        with col2:
            st.markdown("**Memory Statistics**")
            memory_stats = performance_df['memory_percent'].describe()
            st.write(f"Mean: {memory_stats['mean']:.1f}%")
            st.write(f"Max: {memory_stats['max']:.1f}%")
            st.write(f"Min: {memory_stats['min']:.1f}%")
            st.write(f"Std: {memory_stats['std']:.1f}%")
        
        with col3:
            if 'response_time_ms' in performance_df.columns:
                st.markdown("**Response Time Statistics**")
                response_stats = performance_df['response_time_ms'].describe()
                st.write(f"Mean: {response_stats['mean']:.1f}ms")
                st.write(f"Max: {response_stats['max']:.1f}ms")
                st.write(f"Min: {response_stats['min']:.1f}ms")
                st.write(f"95th percentile: {performance_df['response_time_ms'].quantile(0.95):.1f}ms")
    
    # Network and Disk I/O
    if performance_df is not None:
        if 'network_sent_mb' in performance_df.columns and 'disk_read_mb' in performance_df.columns:
            st.subheader("💾 I/O Performance")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_network = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=('Network Sent (MB)', 'Network Received (MB)')
                )
                
                fig_network.add_trace(
                    go.Scatter(
                        x=performance_df['elapsed_time'],
                        y=performance_df['network_sent_mb'],
                        mode='lines',
                        name='Sent',
                        line=dict(color='purple')
                    ),
                    row=1, col=1
                )
                
                fig_network.add_trace(
                    go.Scatter(
                        x=performance_df['elapsed_time'],
                        y=performance_df['network_recv_mb'],
                        mode='lines',
                        name='Received',
                        line=dict(color='orange')
                    ),
                    row=2, col=1
                )
                
                fig_network.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_network, use_container_width=True)
            
            with col2:
                fig_disk = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=('Disk Read (MB)', 'Disk Write (MB)')
                )
                
                fig_disk.add_trace(
                    go.Scatter(
                        x=performance_df['elapsed_time'],
                        y=performance_df['disk_read_mb'],
                        mode='lines',
                        name='Read',
                        line=dict(color='cyan')
                    ),
                    row=1, col=1
                )
                
                fig_disk.add_trace(
                    go.Scatter(
                        x=performance_df['elapsed_time'],
                        y=performance_df['disk_write_mb'],
                        mode='lines',
                        name='Write',
                        line=dict(color='magenta')
                    ),
                    row=2, col=1
                )
                
                fig_disk.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_disk, use_container_width=True)
    
    # Raw Data
    with st.expander("📊 Raw Performance Data"):
        if performance_df is not None:
            st.dataframe(performance_df)
    
    with st.expander("🐝 Raw Locust Data"):
        if locust_df is not None:
            st.dataframe(locust_df)
    
    # Footer
    st.markdown("---")
    st.markdown("🧪 **Load Testing Dashboard** - Real-time performance monitoring for Furniture AI")


if __name__ == "__main__":
    create_performance_dashboard()
