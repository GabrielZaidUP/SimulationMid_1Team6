import simpy
import random
from metrics import MetricsCollector

class DigitalWatchFactory:
    """!
    @brief Digital Watch Factory Simulation Class
    
    Simulates a digital watch manufacturing facility with 6 workstations,
    material management, and production flow control.
    """

    def __init__(self, env, metrics):
        """!
        @brief Initialize the factory simulation
        
        @param env SimPy environment instance
        @param metrics MetricsCollector instance for tracking factory performance
        """
        self.env = env
        self.metrics = metrics
        
        # Materials with 25 units per container
        self.materials = {
            'base_circuits': 25,
            'microcontrollers': 25,
            'led_displays': 25,
            'case': 25,
            'water_sealant': 25,
            'batteries': 25
        }
        
        # Resupply devices
        self.resupply_devices = 3
        
        # Work stations definition
        self.stations = [
            simpy.Resource(env, capacity=1),  # Station 1: Circuit preparation
            simpy.Resource(env, capacity=1),  # Station 2: Microcontroller integration
            simpy.Resource(env, capacity=1),  # Station 3: LED display assembly
            simpy.Resource(env, capacity=1),  # Station 4: Case assembly
            simpy.Resource(env, capacity=1),  # Station 5: Case assembly (interchangeable with 4)
            simpy.Resource(env, capacity=1)   # Station 6: Testing and packaging
        ]

        # Start production process
        self.env.process(self.production_process())

    def production_process(self):
        """!
        @brief Main production process that generates new watches continuously
        """
        while True:
            yield self.env.timeout(random.expovariate(1/4))
            self.env.process(self.assemble_watch())

    def process_at_station(self, material: str, station: int):
        """!
        @brief Process a material at a specific station
        
        @param material Material to be processed
        @param station Station ID where processing will occur
        """
        # Check material availability
        if self.materials[material] <= 0:
            yield self.env.process(self.resupply(material))
        
        # Use material
        self.materials[material] -= 1
        self.metrics.record_material_use(material)

        # Request station access
        with self.stations[station].request() as req:
            yield req
            
            # Work time at station
            work_time = max(0, random.gauss(4, 1))
            yield self.env.timeout(work_time)
            self.metrics.record_work_time(station, work_time)

            # Check for station failure
            if random.random() < [0.02, 0.01, 0.05, 0.15, 0.07, 0.06][station]:
                repair_time = random.expovariate(1/3)
                yield self.env.timeout(repair_time)
                self.metrics.record_fixing_time(station, repair_time)

    def assemble_watch(self):
        """!
        @brief Process for assembling a single watch
        
        Handles the complete assembly process through all stations,
        including material usage, processing time, and quality control.
        """
        start = self.env.now
        
        # First 3 sequential steps
        for material, station in [
            ('base_circuits', 0),
            ('microcontrollers', 1),
            ('led_displays', 2)
        ]:
            yield self.env.process(self.process_at_station(material, station))
        
        # Case assembly can be at station 4 or 5
        case_station = random.choice([3, 4])
        yield self.env.process(self.process_at_station('case', case_station))
        
        # Water sealing at the unused station
        next_station = 3 if case_station == 4 else 4
        yield self.env.process(self.process_at_station('water_sealant', next_station))
        
        # Final station
        yield self.env.process(self.process_at_station('batteries', 5))

        # Record total production time
        total_time = self.env.now - start
        self.metrics.record_production_time(total_time)
        self.metrics.record_production()
        
        # Quality control check
        if random.random() < 0.05:
            self.metrics.record_faulty()

    def resupply(self, material):
        """!
        @brief Handle material resupply process
        
        @param material Material to be resupplied
        """
        if self.resupply_devices > 0:
            self.resupply_devices -= 1
            resupply_time = max(0, random.gauss(2, 0.5))
            yield self.env.timeout(resupply_time)
            
            self.materials[material] = 25
            self.metrics.record_resupply(material)
            
            self.resupply_devices += 1