import numpy as np
from typing import Dict, List

class MetricsCollector:
    """!
    @brief Class for collecting and managing factory production metrics
    
    This class handles all metric collection for the digital watch factory simulation,
    including production counts, time metrics, and material usage tracking.
    """

    def __init__(self):
        """!
        @brief Initialize the metrics collector with default values
        
        Creates counters and containers for:
        - Production metrics (total and faulty products)
        - Time metrics (work times, downtimes)
        - Material usage
        - Resupply events
        """
        # Production Metrics
        self.production_count = 0  # Total watches produced
        self.faulty_products = 0   # Total faulty watches
        
        # Time Metrics
        self.station_work_times = [0] * 6  # Work times for each station
        self.station_downtimes = [0] * 6   # Downtime for each station
        self.production_times = []          # Total production times per watch
        self.fixing_times = []             # Repair times
        
        # Material Metrics
        self.materials_used = {
            'base_circuits': 0,
            'microcontrollers': 0,
            'led_displays': 0,
            'case': 0,
            'water_sealant': 0,
            'batteries': 0
        }
        
        # Resupply Metrics
        self.resupply_counts = {
            'base_circuits': 0,
            'microcontrollers': 0,
            'led_displays': 0,
            'case': 0,
            'water_sealant': 0,
            'batteries': 0
        }
    
    def record_production(self):
        """!
        @brief Record a successfully produced watch
        """
        self.production_count += 1
    
    def record_faulty(self):
        """!
        @brief Record a faulty watch
        """
        self.faulty_products += 1
    
    def record_work_time(self, station_id: int, time: float):
        """!
        @brief Record working time for a specific station
        
        @param station_id The ID of the station (0-5)
        @param time The amount of time spent working
        """
        self.station_work_times[station_id] += time
    
    def record_fixing_time(self, station_id: int, time: float):
        """!
        @brief Record repair time for a specific station
        
        @param station_id The ID of the station (0-5)
        @param time The amount of time spent on repairs
        """
        self.fixing_times.append(time)
        self.station_downtimes[station_id] += time
    
    def record_production_time(self, time: float):
        """!
        @brief Record total production time for a watch
        
        @param time Total time taken to produce the watch
        """
        self.production_times.append(time)
    
    def record_material_use(self, material: str, quantity: int = 1):
        """!
        @brief Record the use of a specific material
        
        @param material Name of the material used
        @param quantity Amount of material used (default is 1)
        """
        self.materials_used[material] += quantity
    
    def record_resupply(self, material: str):
        """!
        @brief Record a resupply event for a specific material
        
        @param material Name of the material resupplied
        """
        self.resupply_counts[material] += 1

    def get_metrics(self, total_time: float) -> Dict:
        """!
        @brief Calculate and return all collected metrics
        
        @param total_time Total simulation time
        @return Dictionary containing all calculated metrics
        """
        return {
            'production': {
                'total': self.production_count,
                'faulty': self.faulty_products,
                'faulty_rate': self.faulty_products / (self.production_count + self.faulty_products) if self.production_count > 0 else 0
            },
            'station_metrics': {
                'occupancy_rates': [work / total_time for work in self.station_work_times],
                'downtimes': self.station_downtimes
            },
            'time_metrics': {
                'avg_production_time': np.mean(self.production_times) if self.production_times else 0,
                'avg_fixing_time': np.mean(self.fixing_times) if self.fixing_times else 0
            },
            'material_metrics': {
                'materials_used': self.materials_used,
                'resupply_counts': self.resupply_counts
            }
        }