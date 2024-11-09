from mesa_viz_tornado.ModularVisualization import ModularServer
from mesa_viz_tornado.UserParam import NumberInput, Slider
from mesa_viz_tornado.modules import ChartModule

from roomba_model import mesa, RoombaModel, RoombaAgent, ManchaAgent

def agent_portrayal(agent):
    portrayal = {"Shape": "roomba.png",
                 "Filled": "true",
                 "Layer": 0,
                 "r": 0.5}
    if isinstance(agent, ManchaAgent):
        portrayal["Shape"] = "mancha.png"
        portrayal["r"] = 0.75
        if agent.is_clean:
            portrayal["Shape"] = "circle"
            portrayal["Color"] = "white"

    return portrayal

grid = mesa.visualization.CanvasGrid(agent_portrayal, 10, 10, 500, 500)

steps_chart = ChartModule( [{"Label": "Steps", "Color": "Black"}],
                           data_collector_name='datacollector' )

overlap_chart = ChartModule( [{"Label": "Overlaps", "Color": "Red"}],
                             data_collector_name='datacollector' )

model_params = { "N": NumberInput("Number of Roombas", value=10),
                 "width": Slider("Grid Width", 10, 5, 999, 1),
                 "height": Slider("Grid Height", 10, 5, 999, 1),
                 "sucio": Slider("Percentage of Dirty Spots", 10, 0, 100, 1),
                 "t_max": Slider("Max Steps", 100, 1, 999, 1) }

server = ModularServer(
    RoombaModel,
    [grid, steps_chart, overlap_chart],
    "Roomba Model",
    model_params )
server.port = 8521 # The default
server.launch()