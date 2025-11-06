"""
Data Drift Detection Script
Checks for significant drift in model inputs/outputs
"""

import json
import sys
from pathlib import Path

import pandas as pd
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report


def check_drift():
    """Check for data drift and return boolean"""
    
    logs_path = Path("logs/interactions.jsonl")
    
    if not logs_path.exists():
        print("false")
        return False
    
    # Load data
    interactions = []
    with open(logs_path, 'r') as f:
        for line in f:
            interactions.append(json.loads(line))
    
    if len(interactions) < 100:  # Need minimum data
        print("false")
        return False
    
    df = pd.DataFrame(interactions)
    
    # Split into reference and current
    split_point = len(df) // 2
    reference_data = df[:split_point]
    current_data = df[split_point:]
    
    # Create drift report
    report = Report(metrics=[DataDriftPreset()])
    
    try:
        report.run(
            reference_data=reference_data,
            current_data=current_data
        )
        
        # Get drift results
        results = report.as_dict()
        
        # Check if drift detected
        drift_detected = results.get('metrics', [{}])[0].get('result', {}).get('dataset_drift', False)
        
        print("true" if drift_detected else "false")
        return drift_detected
        
    except Exception as e:
        print(f"Error checking drift: {e}", file=sys.stderr)
        print("false")
        return False


if __name__ == "__main__":
    check_drift()
