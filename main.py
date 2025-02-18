import simpy
import numpy as np
from simulation import RelojDigitalFactory
from metrics import MetricsCollector

def run_simulation(sim_time: int = 5000, runs: int = 100):
    """Ejecuta múltiples simulaciones y recopila resultados"""
    all_metrics = []

    for run in range(runs):
        # Inicializa el entorno de SimPy y los recolectores de métricas
        env = simpy.Environment()
        metrics = MetricsCollector()
        factory = RelojDigitalFactory(env, metrics)
        
        # Ejecuta la simulación
        env.run(until=sim_time)
        
        # Recopila las métricas de esta corrida
        run_metrics = metrics.get_metrics(sim_time)
        all_metrics.append(run_metrics)

        print(f"Run {run + 1}: Producidos {run_metrics['production']['total']} relojes "
              f"({run_metrics['production']['faulty']} defectuosos)")

    return analyze_results(all_metrics)

def analyze_results(metrics_list):
    """Analiza los datos de todas las corridas para obtener estadísticas"""
    aggregated = {
        'production': {
            'total': [],
            'faulty': [],
            'faulty_rate': []
        },
        'station_metrics': {
            'occupancy_rates': [[] for _ in range(6)],
            'downtimes': [[] for _ in range(6)]
        },
        'time_metrics': {
            'avg_production_time': [],
            'avg_fixing_time': []
        },
        'material_metrics': {
            'circuitos_base': [],
            'microcontroladores': [],
            'pantallas_led': [],
            'carcasa': [],
            'baterias': []
        }
    }
    
    # Agrega datos de cada corrida a las listas correspondientes
    for metrics in metrics_list:
        # Producción
        aggregated['production']['total'].append(metrics['production']['total'])
        aggregated['production']['faulty'].append(metrics['production']['faulty'])
        aggregated['production']['faulty_rate'].append(metrics['production']['faulty_rate'])
        
        # Ocupación y tiempos de inactividad por estación
        for i in range(6):
            aggregated['station_metrics']['occupancy_rates'][i].append(metrics['station_metrics']['occupancy_rates'][i])
            aggregated['station_metrics']['downtimes'][i].append(metrics['station_metrics']['downtimes'][i])
        
        # Tiempos
        aggregated['time_metrics']['avg_production_time'].append(metrics['time_metrics']['avg_production_time'])
        aggregated['time_metrics']['avg_fixing_time'].append(metrics['time_metrics']['avg_fixing_time'])
        
        # Materiales utilizados
        for material in aggregated['material_metrics']:
            aggregated['material_metrics'][material].append(metrics['material_metrics']['materials_used'][material])

    # Calcula promedios y estadísticas
    results = {
        'production': {
            'avg_total': np.mean(aggregated['production']['total']),
            'std_total': np.std(aggregated['production']['total']),
            'avg_faulty': np.mean(aggregated['production']['faulty']),
            'avg_faulty_rate': np.mean(aggregated['production']['faulty_rate'])
        },
        'station_metrics': {
            'avg_occupancy_rates': [np.mean(rates) for rates in aggregated['station_metrics']['occupancy_rates']],
            'avg_downtimes': [np.mean(downs) for downs in aggregated['station_metrics']['downtimes']]
        },
        'time_metrics': {
            'avg_production_time': np.mean(aggregated['time_metrics']['avg_production_time']),
            'avg_fixing_time': np.mean(aggregated['time_metrics']['avg_fixing_time'])
        },
        'material_metrics': {
            'avg_circuitos_base': np.mean(aggregated['material_metrics']['circuitos_base']),
            'avg_microcontroladores': np.mean(aggregated['material_metrics']['microcontroladores']),
            'avg_pantallas_led': np.mean(aggregated['material_metrics']['pantallas_led']),
            'avg_carcasas': np.mean(aggregated['material_metrics']['carcasa']),
            'avg_baterias': np.mean(aggregated['material_metrics']['baterias'])
        }
    }

    return results

if __name__ == "__main__":
    # Ejecuta la simulación y analiza resultados
    results = run_simulation()

    # Muestra los resultados generales
    print("\n=== Resultados de la Simulación ===")
    print(f"\nProducción Promedio: {results['production']['avg_total']:.2f} relojes")
    print(f"Desviación Estándar de Producción: {results['production']['std_total']:.2f}")
    print(f"Promedio de Defectuosos: {results['production']['avg_faulty']:.2f}")
    print(f"Tasa Promedio de Defectos: {results['production']['avg_faulty_rate']:.2%}")

    # Métricas por estación
    print("\n=== Métricas por Estación ===")
    for i in range(6):
        print(f"\nEstación {i+1}:")
        print(f"  Tasa de Ocupación: {results['station_metrics']['avg_occupancy_rates'][i]:.2%}")
        print(f"  Tiempo de Inactividad: {results['station_metrics']['avg_downtimes'][i]:.2f} unidades")

    # Tiempos generales
    print("\n=== Tiempos ===")
    print(f"Tiempo Promedio de Producción: {results['time_metrics']['avg_production_time']:.2f} unidades")
    print(f"Tiempo Promedio de Reparación: {results['time_metrics']['avg_fixing_time']:.2f} unidades")

    # Materiales utilizados
    print("\n=== Materiales Utilizados ===")
    print(f"Circuitos Base: {results['material_metrics']['avg_circuitos_base']:.2f} unidades")
    print(f"Microcontroladores: {results['material_metrics']['avg_microcontroladores']:.2f} unidades")
    print(f"Pantallas LED: {results['material_metrics']['avg_pantallas_led']:.2f} unidades")
    print(f"Carcasas: {results['material_metrics']['avg_carcasas']:.2f} unidades")
    print(f"Baterías: {results['material_metrics']['avg_baterias']:.2f} unidades")