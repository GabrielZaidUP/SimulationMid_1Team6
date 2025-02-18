import simpy
import random
from metrics import MetricsCollector

class RelojDigitalFactory:
    def __init__(self, env, metrics):
        self.env = env
        self.metrics = metrics
        
        # Definición de materiales con 25 unidades por contenedor
        self.materiales = {
            'circuitos_base': 25,
            'microcontroladores': 25,
            'pantallas_led': 25,
            'carcasa': 25,
            'baterias': 25
        }
        
        # Dispositivos de reabastecimiento
        self.resupply_devices = 3
        
        # Definición de 6 estaciones de trabajo
        self.estaciones = [
            simpy.Resource(env, capacity=1),  # Estación 1: Preparación de circuitos
            simpy.Resource(env, capacity=1),  # Estación 2: Integración de microcontrolador
            simpy.Resource(env, capacity=1),  # Estación 3: Montaje de pantalla LED
            simpy.Resource(env, capacity=1),  # Estación 4: Ensamblaje de carcasa
            simpy.Resource(env, capacity=1),  # Estación 5: Ensamblaje de carcasa (intercambiable con 4)
            simpy.Resource(env, capacity=1)   # Estación 6: Pruebas y empaque
        ]

        # Iniciar proceso de producción
        self.env.process(self.proceso_produccion())

    def proceso_produccion(self):
        """Genera nuevos relojes digitales de manera continua"""
        while True:
            # Tiempo de llegada de un nuevo producto
            yield self.env.timeout(random.expovariate(1/4))
            self.env.process(self.ensamblar_reloj())

    def ensamblar_reloj(self):
        """Proceso de ensamblaje de un reloj digital"""
        inicio = self.env.now
        
        # Secuencia de estaciones para ensamblar un reloj digital
        secuencia = [
            ('circuitos_base', 0),          # Estación 1
            ('microcontroladores', 1),      # Estación 2
            ('pantallas_led', 2),           # Estación 3
            ('carcasa', random.choice([3, 4])),  # Estación 4 o 5
            ('baterias', 5)                 # Estación 6
        ]

        # Pasar por cada estación de la secuencia
        for material, estacion in secuencia:
            # Verificar si hay suficiente material, si no, reabastecer
            if self.materiales[material] <= 0:
                yield self.env.process(self.reabastecer(material))
            
            # Usar material necesario
            self.materiales[material] -= 1
            self.metrics.record_material_use(material)

            # Solicitar acceso a la estación
            with self.estaciones[estacion].request() as req:
                yield req
                
                # Tiempo de trabajo en la estación
                tiempo_trabajo = max(0, random.gauss(4, 1))
                yield self.env.timeout(tiempo_trabajo)
                self.metrics.record_work_time(estacion, tiempo_trabajo)

                # Verificar probabilidad de falla en la estación
                if random.random() < [0.02, 0.01, 0.05, 0.15, 0.07, 0.06][estacion]:
                    tiempo_reparacion = random.expovariate(1/3)
                    yield self.env.timeout(tiempo_reparacion)
                    self.metrics.record_fixing_time(estacion, tiempo_reparacion)

        # Registrar el tiempo total de producción
        tiempo_total = self.env.now - inicio
        self.metrics.record_production_time(tiempo_total)
        self.metrics.record_production()
        
        # Probabilidad de rechazo por calidad
        if random.random() < 0.05:
            self.metrics.record_faulty()

    def reabastecer(self, material):
        """Proceso de reabastecimiento cuando un material se agota"""
        # Verificar si hay dispositivos disponibles para reabastecer
        if self.resupply_devices > 0:
            self.resupply_devices -= 1  # Ocupa un dispositivo
            tiempo_reabastecimiento =max(0, random.gauss(2, 0.5))   # Tiempo de reabastecimiento
            yield self.env.timeout(tiempo_reabastecimiento)
            
            # Reabastecer el material a 25 unidades
            self.materiales[material] = 25
            self.metrics.record_resupply(material)
            
            # Liberar el dispositivo de reabastecimiento
            self.resupply_devices += 1

