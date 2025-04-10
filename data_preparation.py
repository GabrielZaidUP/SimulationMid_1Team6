import json
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class DataPreparation:
    """
    Simple data preparation for the Digital Watch Factory simulation.
    """
    
    def __init__(self, output_path="dashboard_data"):
        """Initialize the data preparation module"""
        self.output_path = output_path
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)
    
    def process_simulation_data(self, metrics_list, days_per_run=1):
        """Process simulation data into useful formats for visualization"""
        # Create time-based data (daily production)
        self._create_time_series(metrics_list, days_per_run)
        
        # Process station data
        self._process_station_data(metrics_list)
        
        # Process material usage
        self._process_material_data(metrics_list)
    
    def _create_time_series(self, metrics_list, days_per_run):
        """Create time series data for production over time"""
        # Start date (just use today - days_per_run * len(metrics_list))
        start_date = datetime.now() - timedelta(days=days_per_run * len(metrics_list))
        
        # Create DataFrame
        data = []
        for i, metrics in enumerate(metrics_list):
            current_date = start_date + timedelta(days=i * days_per_run)
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'production': metrics['production']['total'],
                'faulty': metrics['production']['faulty'],
                'faulty_rate': metrics['production']['faulty_rate'],
                'avg_downtime': sum(metrics['station_metrics']['downtimes']) / len(metrics['station_metrics']['downtimes']),
                'avg_production_time': metrics['time_metrics']['avg_production_time']
            })
        
        # Save to CSV
        df = pd.DataFrame(data)
        df.to_csv(os.path.join(self.output_path, 'production_data.csv'), index=False)
        
    def _process_station_data(self, metrics_list):
        """Process station-specific data"""
        # Define station names
        station_names = [
            "Circuit Preparation", 
            "Microcontroller Integration", 
            "LED Display Assembly", 
            "Case Assembly", 
            "Water Sealing", 
            "Testing & Packaging"
        ]
        
        # Aggregate station data across all runs
        occupancy_rates = np.zeros(6)
        downtimes = np.zeros(6)
        
        for metrics in metrics_list:
            for i in range(6):
                occupancy_rates[i] += metrics['station_metrics']['occupancy_rates'][i]
                downtimes[i] += metrics['station_metrics']['downtimes'][i]
        
        # Average values
        occupancy_rates /= len(metrics_list)
        downtimes /= len(metrics_list)
        
        # Create DataFrame
        station_data = []
        for i in range(6):
            station_data.append({
                'station_id': i,
                'station_name': station_names[i],
                'occupancy_rate': occupancy_rates[i],
                'downtime': downtimes[i]
            })
        
        # Save to CSV
        station_df = pd.DataFrame(station_data)
        station_df.to_csv(os.path.join(self.output_path, 'station_data.csv'), index=False)
    
    def _process_material_data(self, metrics_list):
        """Process material usage data"""
        # Get material names
        materials = list(metrics_list[0]['material_metrics']['materials_used'].keys())
        
        # Aggregate material usage across all runs
        material_usage = {material: 0 for material in materials}
        resupply_counts = {material: 0 for material in materials}
        
        for metrics in metrics_list:
            for material in materials:
                material_usage[material] += metrics['material_metrics']['materials_used'][material]
                resupply_counts[material] += metrics['material_metrics']['resupply_counts'][material]
        
        # Create DataFrame
        material_data = []
        for material in materials:
            display_name = material.replace('_', ' ').title()
            material_data.append({
                'material': material,
                'display_name': display_name,
                'total_usage': material_usage[material],
                'total_resupply': resupply_counts[material],
                'avg_usage': material_usage[material] / len(metrics_list),
                'avg_resupply': resupply_counts[material] / len(metrics_list)
            })
        
        # Save to CSV
        material_df = pd.DataFrame(material_data)
        material_df.to_csv(os.path.join(self.output_path, 'material_data.csv'), index=False)