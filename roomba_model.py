import mesa
from mesa import DataCollector

def getSteps(model):
    agentSteps = [agent.stepsGiven for agent in model.schedule.agents if isinstance(agent, RoombaAgent)]
    B = sum(agentSteps)
    return (B/len(agentSteps))

def getOverlaps(model):
    agentOverlaps = [agent.overlapTimes for agent in model.schedule.agents if isinstance(agent, RoombaAgent)]
    B = sum(agentOverlaps)
    return (B/len(agentOverlaps))

class RoombaAgent(mesa.Agent):
    def __init__(self, name, model):
        # Pass the parameters to the parent class.
        super().__init__(name, model)

        # Create the agent's variable and set the initial values.
        self.stepsGiven = 0
        self.overlapTimes = 0

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def clean(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            for agent in cellmates:
                if isinstance(agent, ManchaAgent):
                    print("clean roomba")
                    agent.clean()
                    break

    def checkClean(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        for agent in cellmates:
            if isinstance(agent, ManchaAgent):
                if not agent.is_clean:
                    return False
        return True

    def checkOverlap(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        for agent in cellmates:
            if isinstance(agent, RoombaAgent) and agent != self:
                    return True
        return False

    def step(self):
        if not self.checkClean():
            self.clean()
        else:
            self.move()
        self.stepsGiven += 1
        print(f"steps {self.stepsGiven}")

        if self.checkOverlap():
            self.overlapTimes += 1
            print(f"overlap {self.overlapTimes}" )

class ManchaAgent(mesa.Agent):
    def __init__(self, name, model):
        # Pass the parameters to the parent class.
        super().__init__(name, model)

        # Create the agent's variable and set the initial values.
        self.is_clean = False

    def clean(self):
        if not self.is_clean:
            self.is_clean = True
            print('Mancha cleaned')

class RoombaModel(mesa.Model):
    def __init__(self, N, width, height, sucio, t_max):
        super().__init__()
        self.num_agents = N
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.p_sucio = sucio
        self.t_max = t_max
        # Create scheduler and assign it to the model
        self.schedule = mesa.time.RandomActivation(self)
        self.running = True

        self.datacollector = mesa.DataCollector(
            model_reporters={"Steps": getSteps, "Overlaps": getOverlaps}
        )

        # Create agents
        for i in range(self.num_agents):
            a = RoombaAgent(i, self)
            # Add the agent to the scheduler
            self.schedule.add(a)
            # Add the agent to the starting grid cell (1, 1)
            self.grid.place_agent(a, (1, 1))

        for i in range(int(width * height * (self.p_sucio/100))):
            a = ManchaAgent(i, self)
            self.schedule.add(a)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            cellmates = self.grid.get_cell_list_contents([(x, y)])
            while not len (cellmates) == 0:
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                cellmates = self.grid.get_cell_list_contents([(x, y)])
            self.grid.place_agent(a, (x, y))

    def checkManchas(self):
        for agent in self.schedule.agents:
            if isinstance(agent, ManchaAgent):
                if not agent.is_clean:
                    return False
        return True

    def step(self):
        self.datacollector.collect(self)
        if self.schedule.steps >= self.t_max-1 or self.checkManchas():
            self.running = False
        else:
            self.schedule.step()