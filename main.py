import simpy
import numpy as np
import os
from simulation import DigitalWatchFactory
from metrics import MetricsCollector
from data_preparation import DataPreparation

def run_simulation(sim_time=1000, runs=40, prepare_data=True):
    """Run multiple simulation iterations and collect results"""
    all_metrics = []

    for run in range(runs):
        # Initialize SimPy environment and metrics collectors
        env = simpy.Environment()
        metrics = MetricsCollector()
        factory = DigitalWatchFactory(env, metrics)
        
        # Run simulation
        env.run(until=sim_time)
        
        # Collect metrics from this run
        run_metrics = metrics.get_metrics(sim_time)
        all_metrics.append(run_metrics)

        print(f"Run {run + 1}: Produced {run_metrics['production']['total']} watches "
              f"({run_metrics['production']['faulty']} faulty)")

    # Process the data for visualization if requested
    if prepare_data:
        data_prep = DataPreparation(output_path="dashboard_data")
        data_prep.process_simulation_data(all_metrics)
    
    return analyze_results(all_metrics)

def analyze_results(metrics_list):
    """Analyze data from all simulation runs"""
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
            'base_circuits': [],
            'microcontrollers': [],
            'led_displays': [],
            'case': [],
            'water_sealant': [],
            'batteries': []
        }
    }
    
    # Aggregate data from each run
    for metrics in metrics_list:
        # Production metrics
        aggregated['production']['total'].append(metrics['production']['total'])
        aggregated['production']['faulty'].append(metrics['production']['faulty'])
        aggregated['production']['faulty_rate'].append(metrics['production']['faulty_rate'])
        
        # Station metrics
        for i in range(6):
            aggregated['station_metrics']['occupancy_rates'][i].append(
                metrics['station_metrics']['occupancy_rates'][i])
            aggregated['station_metrics']['downtimes'][i].append(
                metrics['station_metrics']['downtimes'][i])
        
        # Time metrics
        aggregated['time_metrics']['avg_production_time'].append(
            metrics['time_metrics']['avg_production_time'])
        aggregated['time_metrics']['avg_fixing_time'].append(
            metrics['time_metrics']['avg_fixing_time'])
        
        # Material metrics
        for material in aggregated['material_metrics']:
            aggregated['material_metrics'][material].append(
                metrics['material_metrics']['materials_used'][material])

    # Calculate final statistics
    results = {
    'production': {
            'avg_total': np.mean(aggregated['production']['total']),
            'std_total': np.std(aggregated['production']['total']),
            'avg_faulty': np.mean(aggregated['production']['faulty']),
            'avg_faulty_rate': np.mean(aggregated['production']['faulty_rate']),
            'production_range': max(aggregated['production']['total']) - min(aggregated['production']['total'])
        },
        'station_metrics': {
            'avg_occupancy_rates': [np.mean(rates) for rates in aggregated['station_metrics']['occupancy_rates']],
            'avg_downtimes': [np.mean(downs) for downs in aggregated['station_metrics']['downtimes']],
            'avg_downtime_per_day': np.mean([sum(downs) / len(downs) for downs in aggregated['station_metrics']['downtimes']])
        },
        'time_metrics': {
            'avg_production_time': np.mean(aggregated['time_metrics']['avg_production_time']),
            'avg_fixing_time': np.mean(aggregated['time_metrics']['avg_fixing_time'])
        },
        'material_metrics': {
            'avg_base_circuits': np.mean(aggregated['material_metrics']['base_circuits']),
            'avg_microcontrollers': np.mean(aggregated['material_metrics']['microcontrollers']),
            'avg_led_displays': np.mean(aggregated['material_metrics']['led_displays']),
            'avg_cases': np.mean(aggregated['material_metrics']['case']),
            'avg_water_sealant': np.mean(aggregated['material_metrics']['water_sealant']),
            'avg_batteries': np.mean(aggregated['material_metrics']['batteries'])
        }
    }

    return results

if __name__ == "__main__":
    """Main execution entry point"""
    # Create dashboard data directory if it doesn't exist
    if not os.path.exists("dashboard_data"):
        os.makedirs("dashboard_data")
    
    # Run simulation and analyze results
    results = run_simulation(sim_time=1000, runs=40, prepare_data=True)

    # Display general results
    print("\n=== Simulation Results ===")
    print(f"\nAverage Production: {results['production']['avg_total']:.2f} watches")
    print(f"\nProduction Range: {results['production']['production_range']} watches")
    print(f"Production Standard Deviation: {results['production']['std_total']:.2f}")
    print(f"Average Faulty Products: {results['production']['avg_faulty']:.2f}")
    print(f"Average Fault Rate: {results['production']['avg_faulty_rate']:.2%}")
    print(f"\nAverage Downtime per Day: {results['station_metrics']['avg_downtime_per_day']:.2f} units")

    # Station metrics
    print("\n=== Station Metrics ===")
    for i in range(6):
        print(f"\nStation {i+1}:")
        print(f"  Occupancy Rate: {results['station_metrics']['avg_occupancy_rates'][i]:.2%}")
        print(f"  Downtime: {results['station_metrics']['avg_downtimes'][i]:.2f} units")

    # Time metrics
    print("\n=== Time Metrics ===")
    print(f"Average Production Time: {results['time_metrics']['avg_production_time']:.2f} units")
    print(f"Average Repair Time: {results['time_metrics']['avg_fixing_time']:.2f} units")

    # Material usage
    print("\n=== Materials Used ===")
    print(f"Base Circuits: {results['material_metrics']['avg_base_circuits']:.2f} units")
    print(f"Microcontrollers: {results['material_metrics']['avg_microcontrollers']:.2f} units")
    print(f"LED Displays: {results['material_metrics']['avg_led_displays']:.2f} units")
    print(f"Cases: {results['material_metrics']['avg_cases']:.2f} units")
    print(f"Water Sealant: {results['material_metrics']['avg_water_sealant']:.2f} units")
    print(f"Batteries: {results['material_metrics']['avg_batteries']:.2f} units")
    
    print("\n=== Dashboard ===")
    print("Data has been prepared for visualization.")
    print("Run 'python dashboard.py' to view the dashboard.")