import numpy as np
from typing import Dict, List

class MetricsCollector:
    def __init__(self):
        # Métricas de Producción
        self.production_count = 0  # Total de relojes producidos
        self.faulty_products = 0  # Total de relojes defectuosos
        
        # Métricas de Tiempo
        self.station_work_times = [0] * 6  # Tiempos de trabajo en cada estación
        self.station_downtimes = [0] * 6  # Tiempos de inactividad en cada estación
        self.production_times = []  # Tiempos totales de producción por reloj
        self.fixing_times = []  # Tiempos de reparación
        
        # Métricas de Materiales
        self.materials_used = {
            'circuitos_base': 0,
            'microcontroladores': 0,
            'pantallas_led': 0,
            'carcasa': 0,
            'baterias': 0
        }
        
        # Reabastecimiento
        self.resupply_counts = {
            'circuitos_base': 0,
            'microcontroladores': 0,
            'pantallas_led': 0,
            'carcasa': 0,
            'baterias': 0
        }
    
    # --- MÉTODOS PARA REGISTRAR MÉTRICAS ---
    
    def record_production(self):
        """Registra un reloj producido"""
        self.production_count += 1
    
    def record_faulty(self):
        """Registra un reloj defectuoso"""
        self.faulty_products += 1
    
    def record_work_time(self, station_id: int, time: float):
        """Registra tiempo de trabajo en una estación"""
        self.station_work_times[station_id] += time
    
    def record_fixing_time(self, station_id: int, time: float):
        """Registra tiempo de reparación en una estación"""
        self.fixing_times.append(time)
        self.station_downtimes[station_id] += time
    
    def record_production_time(self, time: float):
        """Registra el tiempo total de producción de un reloj"""
        self.production_times.append(time)
    
    def record_material_use(self, material: str, quantity: int = 1):
        """Registra el uso de un material"""
        self.materials_used[material] += quantity
    
    def record_resupply(self, material: str):
        """Registra un evento de reabastecimiento"""
        self.resupply_counts[material] += 1

    # --- MÉTODO PARA OBTENER MÉTRICAS ---
    
    def get_metrics(self, total_time: float) -> Dict:
        """Devuelve un diccionario con todas las métricas recopiladas"""
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