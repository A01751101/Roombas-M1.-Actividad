import mesa

from mesa import DataCollector


# Función para obtener el total de pasos dados por los agentes Roomba
def obtenerPasosTotales(modelo):
    """
    Calcula la suma de los pasos dados por todos los agentes Roomba en el modelo.

    Args:
        modelo: El modelo de simulación.

    Returns:
        int: El número total de pasos dados.
    """
    pasosAgentes = [agente.pasosDados for agente in modelo.schedule.agents if isinstance(agente, AgenteRoomba)]
    totalPasos = sum(pasosAgentes)
    return totalPasos


# Función para obtener el promedio de superposiciones de los agentes Roomba
def obtenerPromedioSuperposiciones(modelo):
    """
    Calcula el promedio de veces que los agentes Roomba se superponen en el modelo.

    Args:
        modelo: El modelo de simulación.

    Returns:
        float: El promedio de superposiciones.
    """
    superposicionesAgentes = [agente.vecesSuperposicion for agente in modelo.schedule.agents if
                              isinstance(agente, AgenteRoomba)]
    totalSuperposiciones = sum(superposicionesAgentes)
    return (totalSuperposiciones / len(superposicionesAgentes)) if len(superposicionesAgentes) > 0 else 0


# Función para calcular el porcentaje de manchas limpias
def porcentajeManchasLimpias(modelo):
    """
    Calcula el porcentaje de manchas limpias en el modelo.

    Args:
        modelo: El modelo de simulación.

    Returns:
        float: El porcentaje de manchas limpias.
    """
    estadoManchas = [agente.estaLimpia for agente in modelo.schedule.agents if isinstance(agente, AgenteMancha)]
    totalManchas = len(estadoManchas)
    manchasLimpias = sum(estadoManchas)
    return (manchasLimpias / totalManchas) * 100 if totalManchas > 0 else 0


# Clase que representa un agente Roomba
class AgenteRoomba(mesa.Agent):
    """
    Representa un agente Roomba que se mueve y limpia manchas en la cuadrícula.
    """

    def __init__(self, nombre, modelo):
        """
        Inicializa un nuevo agente Roomba.

        Args:
            nombre: El nombre único del agente.
            modelo: El modelo de simulación.
        """
        # Pasa los parámetros a la clase padre
        super().__init__(nombre, modelo)

        # Inicializa las variables del agente
        self.pasosDados = 0
        self.vecesSuperposicion = 0

    def moverse(self):
        """
        Mueve el agente Roomba a una posición aleatoria adyacente.
        """
        posiblesPasos = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        nuevaPosicion = self.random.choice(posiblesPasos)
        self.model.grid.move_agent(self, nuevaPosicion)

    def limpiar(self):
        """
        Limpia una mancha en la celda actual si hay una.
        """
        companerosCelda = self.model.grid.get_cell_list_contents([self.pos])
        if len(companerosCelda) > 1:
            for agente in companerosCelda:
                if isinstance(agente, AgenteMancha):
                    print("Roomba limpiando")
                    agente.limpiar()
                    break

    def verificarLimpieza(self):
        """
        Verifica si la celda actual está limpia.

        Returns:
            bool: True si la celda está limpia, False en caso contrario.
        """
        companerosCelda = self.model.grid.get_cell_list_contents([self.pos])
        for agente in companerosCelda:
            if isinstance(agente, AgenteMancha):
                if not agente.estaLimpia:
                    return False
        return True

    def verificarSuperposicion(self):
        """
        Verifica si hay otro agente Roomba en la celda actual.

        Returns:
            bool: True si hay superposición, False en caso contrario.
        """
        companerosCelda = self.model.grid.get_cell_list_contents([self.pos])
        for agente in companerosCelda:
            if isinstance(agente, AgenteRoomba) and agente != self:
                return True
        return False

    def step(self):
        """
        Define el comportamiento del agente Roomba en cada paso de la simulación.
        """
        if not self.verificarLimpieza():
            self.limpiar()
        else:
            self.moverse()

        self.pasosDados += 1
        print(f"Pasos: {self.pasosDados}")

        if self.verificarSuperposicion():
            self.vecesSuperposicion += 1
            print(f"Superposición: {self.vecesSuperposicion}")


# Clase que representa un agente Mancha
class AgenteMancha(mesa.Agent):
    """
    Representa una mancha que puede ser limpiada por un agente Roomba.
    """

    def __init__(self, nombre, modelo):
        """
        Inicializa un nuevo agente Mancha.

        Args:
            nombre: El nombre único del agente.
            modelo: El modelo de simulación.
        """
        # Pasa los parámetros a la clase padre
        super().__init__(nombre, modelo)

        # Inicializa la variable del agente
        self.estaLimpia = False

    def limpiar(self):
        """
        Marca la mancha como limpia.
        """
        if not self.estaLimpia:
            self.estaLimpia = True
            print("Mancha limpiada")


# Clase que representa el modelo de simulación
class ModeloRoomba(mesa.Model):
    """
    Representa el modelo de simulación para los agentes Roomba y las manchas.
    """

    def __init__(self, N, ancho, alto, sucio, t_max):
        """
        Inicializa un nuevo modelo de simulación.

        Args:
            N: El número de agentes Roomba.
            ancho: El ancho de la cuadrícula.
            alto: El alto de la cuadrícula.
            sucio: El porcentaje de celdas sucias.
            t_max: El número máximo de pasos de simulación.
        """
        # Llama al constructor de la clase padre
        super().__init__()

        # Inicializa las variables del modelo
        self.num_agents = N
        self.grid = mesa.space.MultiGrid(ancho, alto, True)
        self.p_sucio = sucio
        self.t_max = t_max

        # Crea el programador y lo asigna al modelo
        self.schedule = mesa.time.RandomActivation(self)
        self.running = True

        # Crea el recolector de datos
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Pasos": obtenerPasosTotales,
                "Superposiciones": obtenerPromedioSuperposiciones,
                "ManchasLimpias": porcentajeManchasLimpias
            }
        )

        # Crea los agentes Roomba
        for i in range(self.num_agents):
            agente = AgenteRoomba(i, self)

            # Agrega el agente al programador
            self.schedule.add(agente)

            # Coloca el agente en la celda inicial (1, 1)
            self.grid.place_agent(agente, (1, 1))

        # Crea los agentes Mancha
        for i in range(int(ancho * alto * (self.p_sucio / 100))):
            agente = AgenteMancha(i, self)
            self.schedule.add(agente)

            # Genera una posición aleatoria para la mancha
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            companerosCelda = self.grid.get_cell_list_contents([(x, y)])

            # Asegúrate de que la celda esté vacía
            while not len(companerosCelda) == 0:
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                companerosCelda = self.grid.get_cell_list_contents([(x, y)])

            # Coloca el agente en la celda
            self.grid.place_agent(agente, (x, y))

    def verificarManchas(self):
        """
        Verifica si todas las manchas están limpias.

        Returns:
            bool: True si todas las manchas están limpias, False en caso contrario.
        """
        for agente in self.schedule.agents:
            if isinstance(agente, AgenteMancha):
                if not agente.estaLimpia:
                    return False
        return True

    def step(self):
        """
        Define el comportamiento del modelo en cada paso de la simulación.
        """
        self.datacollector.collect(self)

        if self.schedule.steps >= self.t_max - 1 or self.verificarManchas():
            self.running = False
        else:
            self.schedule.step()