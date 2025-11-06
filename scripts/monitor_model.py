"""
Model Monitoring Script
Monitors model performance and generates reports using Evidently
"""

import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from evidently import ColumnMapping
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from evidently.report import Report


def load_interaction_data(days=7):
    """Load recent interaction data from logs"""
    logs_path = Path("logs/interactions.jsonl")
    
    if not logs_path.exists():
        print("No interaction logs found")
        return None
    
    interactions = []
    with open(logs_path, 'r') as f:
        for line in f:
            interactions.append(json.loads(line))
    
    df = pd.DataFrame(interactions)
    
    # Filter for recent data
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    cutoff_date = datetime.now() - pd.Timedelta(days=days)
    df = df[df['timestamp'] >= cutoff_date]
    
    return df


def generate_monitoring_report(current_data, reference_data=None):
    """Generate Evidently monitoring report"""
    
    # Define column mapping
    column_mapping = ColumnMapping()
    
    # Create report
    report = Report(metrics=[
        DataDriftPreset(),
        DataQualityPreset(),
    ])
    
    # Run report
    if reference_data is not None:
        report.run(
            reference_data=reference_data,
            current_data=current_data,
            column_mapping=column_mapping
        )
    else:
        report.run(
            reference_data=current_data[:len(current_data)//2],
            current_data=current_data[len(current_data)//2:],
            column_mapping=column_mapping
        )
    
    # Save report
    report_path = Path("monitoring/reports")
    report_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_path / f"monitoring_report_{timestamp}.html"
    report.save_html(str(report_file))
    
    print(f"Report saved to {report_file}")
    
    return report


def extract_metrics(data):
    """Extract key metrics from interaction data"""
    
    if data is None or len(data) == 0:
        return {}
    
    metrics = {
        "total_interactions": len(data),
        "avg_response_time": data.get('response_time', pd.Series()).mean(),
        "avg_confidence": data.get('confidence', pd.Series()).mean(),
        "unique_users": data.get('user_id', pd.Series()).nunique(),
        "timestamp": datetime.now().isoformat()
    }
    
    return metrics


def save_metrics(metrics):
    """Save metrics to file"""
    metrics_path = Path("monitoring/metrics")
    metrics_path.mkdir(parents=True, exist_ok=True)
    
    metrics_file = metrics_path / "latest_metrics.json"
    
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Metrics saved to {metrics_file}")


def main():
    print("Starting model monitoring...")
    
    # Load interaction data
    current_data = load_interaction_data(days=7)
    
    if current_data is None or len(current_data) == 0:
        print("No data available for monitoring")
        return
    
    # Generate monitoring report
    print("Generating Evidently report...")
    report = generate_monitoring_report(current_data)
    
    # Extract and save metrics
    print("Extracting metrics...")
    metrics = extract_metrics(current_data)
    save_metrics(metrics)
    
    print("Monitoring complete!")


if __name__ == "__main__":
    main()
