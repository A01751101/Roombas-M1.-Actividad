from mesa_viz_tornado.ModularVisualization import ModularServer
from mesa_viz_tornado.UserParam import NumberInput, Slider
from mesa_viz_tornado.modules import ChartModule

from roomba_model import mesa, ModeloRoomba, AgenteRoomba, AgenteMancha


# Define la representación visual de los agentes
def representacionAgente(agente):
    """
    Define cómo se visualizará un agente en la cuadrícula.

    Args:
        agente: El agente a visualizar.

    Returns:
        dict: Un diccionario con las propiedades visuales del agente.
    """
    representacion = {
        "Shape": "roomba.png",
        "Filled": "true",
        "Layer": 0,
        "r": 0.5
    }
    if isinstance(agente, AgenteMancha):
        representacion["Shape"] = "mancha.png"
        representacion["r"] = 0.75
        if agente.estaLimpia:
            representacion["Shape"] = "circle"
            representacion["Color"] = "white"
    return representacion


# Define las dimensiones de la cuadrícula
ANCHO = 10
ALTO = 10

# Crea la cuadrícula de visualización
cuadrícula = mesa.visualization.CanvasGrid(representacionAgente, ANCHO, ALTO, 500, 500)

# Crea los gráficos para visualizar los datos
graficoPasos = ChartModule(
    [{"Label": "Pasos", "Color": "Black"}],
    data_collector_name="datacollector"
)
graficoSuperposiciones = ChartModule(
    [{"Label": "Superposiciones", "Color": "Red"}],
    data_collector_name="datacollector"
)
graficoManchas = ChartModule(
    [{"Label": "ManchasLimpias", "Color": "Green"}],
    data_collector_name="datacollector"
)

# Define los parámetros del modelo
parametrosModelo = {
    "N": NumberInput("Número de Roombas", value=10),
    "ancho": ANCHO,
    "alto": ALTO,
    "sucio": Slider("Porcentaje de Manchas", 10, 0, 100, 1),
    "t_max": Slider("Pasos Máximos", 100, 1, 999, 1)
}

# Crea el servidor para ejecutar la simulación
servidor = ModularServer(
    ModeloRoomba,
    [cuadrícula, graficoPasos, graficoSuperposiciones, graficoManchas],
    "Modelo Roomba",
    parametrosModelo
)

# Define el puerto del servidor
servidor.port = 8521

# Inicia el servidor
servidor.launch()