import moderngl
import numpy as np
import glfw
import time
import random
import math
from pyrr import Matrix44
from enum import Enum, auto
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import pandas as pd
from collections import defaultdict
import logging
from datetime import datetime

logging.basicConfig(
    filename=f'simulation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

class QuadTree:
    def __init__(self, boundary, capacity):
        self.boundary = boundary  
        self.capacity = capacity
        self.agents = []
        self.divided = False
        self.northwest = None
        self.northeast = None
        self.southwest = None
        self.southeast = None

    def subdivide(self):
        x, y, w, h = self.boundary
        w_half = w / 2
        h_half = h / 2

        nw = (x - w_half, y + h_half, w_half, h_half)
        ne = (x + w_half, y + h_half, w_half, h_half)
        sw = (x - w_half, y - h_half, w_half, h_half)
        se = (x + w_half, y - h_half, w_half, h_half)

        self.northwest = QuadTree(nw, self.capacity)
        self.northeast = QuadTree(ne, self.capacity)
        self.southwest = QuadTree(sw, self.capacity)
        self.southeast = QuadTree(se, self.capacity)
        self.divided = True

    def insert(self, agent):
        if not self._contains(agent):
            return False

        if len(self.agents) < self.capacity and not self.divided:
            self.agents.append(agent)
            return True

        if not self.divided:
            self.subdivide()

        return (self.northwest.insert(agent) or
                self.northeast.insert(agent) or
                self.southwest.insert(agent) or
                self.southeast.insert(agent))

    def query_range(self, range_rect):
        found = []
        if not self._intersects(range_rect):
            return found

        for agent in self.agents:
            if self._point_in_range(agent.position[:2], range_rect):
                found.append(agent)

        if self.divided:
            found.extend(self.northwest.query_range(range_rect))
            found.extend(self.northeast.query_range(range_rect))
            found.extend(self.southwest.query_range(range_rect))
            found.extend(self.southeast.query_range(range_rect))

        return found

    def _contains(self, agent):
        x, y = agent.position[:2]
        bx, by, bw, bh = self.boundary
        return (x >= bx - bw and x <= bx + bw and
                y >= by - bh and y <= by + bh)

    def _intersects(self, range_rect):
        rx, ry, rw, rh = range_rect
        bx, by, bw, bh = self.boundary
        return not (rx + rw < bx - bw or
                   rx - rw > bx + bw or
                   ry + rh < by - bh or
                   ry - rh > by + bh)

    def _point_in_range(self, point, range_rect):
        px, py = point
        rx, ry, rw, rh = range_rect
        return (px >= rx - rw and px <= rx + rw and
                py >= ry - rh and py <= ry + rh)

class Statistics:
    def __init__(self):
        self.data = defaultdict(list)
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.last_update = time.time()
        self.update_interval = 0.5  

    def update(self, agents):
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return

        strategy_counts = defaultdict(int)
        for agent in agents:
            strategy_counts[agent.strategy.name] += 1

        self.data['time'].append(current_time)
        for strategy in Strategy:
            self.data[strategy.name].append(strategy_counts[strategy.name])

        self._update_plot(strategy_counts)
        self._save_data()
        self.last_update = current_time

    def _update_plot(self, strategy_counts):
        self.ax.clear()
        strategies = list(strategy_counts.keys())
        counts = list(strategy_counts.values())
        colors = ['green', 'red', 'blue', 'yellow', 'purple']
        
        self.ax.bar(strategies, counts, color=colors)
        self.ax.set_ylabel('Número de agentes')
        self.ax.set_title('Población por estrategia')
        plt.xticks(rotation=45)
        self.fig.tight_layout()
        
        self.fig.savefig('population_stats.png')

    def _save_data(self):
        df = pd.DataFrame(self.data)
        df.to_csv('simulation_data.csv', index=False)

class Strategy(Enum):
    COOPERATOR = auto()     
    DEFECTOR = auto()      
    HYBRID = auto()       
    TEMPORAL = auto()
    PROBABILISTIC = auto()  
class Agent:
    def __init__(self, x, y, z, size, strategy):
        self.position = np.array([x, y, z], dtype=np.float32)
        self.size = size
        self.strategy = strategy
        self.velocity = np.array([random.uniform(-0.02, 0.02) for _ in range(3)], dtype=np.float32)
        
        self.birth_time = time.time()
        self.last_interaction_time = self.birth_time
        self.last_strategy_change = self.birth_time
        
        self.interaction_count = 0
        self.successful_interactions = 0
        self.temporal_interval = random.uniform(3.0, 7.0)
        self.cooperation_probability = random.random()
        
        self.is_currently_cooperative = True
        if self.strategy == Strategy.DEFECTOR:
            self.is_currently_cooperative = False
        elif self.strategy == Strategy.TEMPORAL:
            self.is_currently_cooperative = random.choice([True, False])
        elif self.strategy == Strategy.PROBABILISTIC:
            self.is_currently_cooperative = random.random() < self.cooperation_probability
            
        self.base_color = self.get_strategy_color()
        self.current_color = self.base_color.copy()

    def get_strategy_color(self):
        colors = {
            Strategy.COOPERATOR: np.array([0, 1, 0], dtype=np.float32),
            Strategy.DEFECTOR: np.array([1, 0, 0], dtype=np.float32),
            Strategy.HYBRID: np.array([0, 0, 1], dtype=np.float32),
            Strategy.TEMPORAL: np.array([1, 1, 0], dtype=np.float32),
            Strategy.PROBABILISTIC: np.array([1, 0, 1], dtype=np.float32)
        }
        return colors[self.strategy]

    def is_cooperative(self):
        current_time = time.time()
        
        if self.strategy == Strategy.COOPERATOR:
            return True
        elif self.strategy == Strategy.DEFECTOR:
            return False
        elif self.strategy == Strategy.HYBRID:
            if self.interaction_count > 0:
                return (self.successful_interactions / self.interaction_count) > 0.5
            return True
        elif self.strategy == Strategy.TEMPORAL:
            time_since_last_change = current_time - self.last_strategy_change
            if time_since_last_change > self.temporal_interval:
                self.is_currently_cooperative = not self.is_currently_cooperative
                self.last_strategy_change = current_time
            return self.is_currently_cooperative
        elif self.strategy == Strategy.PROBABILISTIC:
            if random.random() < 0.1:
                self.is_currently_cooperative = random.random() < self.cooperation_probability
            return self.is_currently_cooperative
        return False

    def update_color(self):
        current_time = time.time()
        pulse = (math.sin(current_time * 2) + 1) * 0.2

        base_color = self.get_strategy_color()
        
        if self.is_cooperative():
            intensity = 0.5 + pulse
        else:
            intensity = 0.3 + pulse * 0.5

        self.current_color = base_color * intensity

        if self.strategy == Strategy.HYBRID:
            success_rate = self.successful_interactions / max(1, self.interaction_count)
            self.current_color *= (0.5 + success_rate * 0.5)
        elif self.strategy == Strategy.TEMPORAL:
            time_factor = (math.sin(current_time) + 1) * 0.5
            self.current_color *= (0.7 + time_factor * 0.3)
        elif self.strategy == Strategy.PROBABILISTIC:
            prob_factor = (math.sin(current_time * 3) + 1) * 0.5
            self.current_color *= (0.8 + prob_factor * 0.2)

    def move(self):
        self.position += self.velocity
        mask = np.abs(self.position) > 1
        self.velocity[mask] *= -1
        self.update_color()

    def register_interaction(self, success=True):
        self.last_interaction_time = time.time()
        self.interaction_count += 1
        if success:
            self.successful_interactions += 1
            
        if self.strategy == Strategy.PROBABILISTIC:
            if success:
                self.cooperation_probability = min(1.0, self.cooperation_probability + 0.1)
            else:
                self.cooperation_probability = max(0.0, self.cooperation_probability - 0.1)

def create_sphere(radius, segments, rings):
    vertices = []
    indices = []
    
    for i in range(rings + 1):
        lat = math.pi * (-0.5 + float(i) / rings)
        for j in range(segments):
            lon = 2 * math.pi * float(j) / segments
            x = radius * math.cos(lat) * math.cos(lon)
            y = radius * math.sin(lat)
            z = radius * math.cos(lat) * math.sin(lon)
            
            nx = x / radius
            ny = y / radius
            nz = z / radius
            
            vertices.extend([x, y, z, nx, ny, nz])

    for i in range(rings):
        for j in range(segments):
            i1 = i * segments + j
            i2 = i * segments + (j + 1) % segments
            i3 = (i + 1) * segments + j
            i4 = (i + 1) * segments + (j + 1) % segments
            indices.extend([i1, i2, i3, i2, i4, i3])

    return np.array(vertices, dtype='f4'), np.array(indices, dtype='i4')
class Simulation:
    def __init__(self, width=800, height=600):
        if not glfw.init():
            raise RuntimeError("No jalo el GLFW")

        self.window = glfw.create_window(width, height, "Demostracion - Proyecto", None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("No se creo la ventana GLFW")

        glfw.make_context_current(self.window)
        self.ctx = moderngl.create_context()
        
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330
                uniform mat4 mvp;
                uniform vec3 color;
                in vec3 in_position;
                in vec3 in_normal;
                out vec3 v_normal;
                out vec3 v_color;
                void main() {
                    gl_Position = mvp * vec4(in_position, 1.0);
                    v_normal = (mvp * vec4(in_normal, 0.0)).xyz;
                    v_color = color;
                }
            ''',
            fragment_shader='''
                #version 330
                in vec3 v_normal;
                in vec3 v_color;
                out vec4 f_color;
                void main() {
                    vec3 light = normalize(vec3(1.0, 1.0, 1.0));
                    float intensity = max(dot(normalize(v_normal), light), 0.0);
                    f_color = vec4(v_color * (0.3 + 0.7 * intensity), 1.0);
                }
            '''
        )

        vertices, indices = create_sphere(0.1, 32, 16)
        self.vertex_buffer = self.ctx.buffer(vertices.tobytes())
        self.index_buffer = self.ctx.buffer(indices.tobytes())
        
        self.vao = self.ctx.vertex_array(
            self.prog,
            [
                (self.vertex_buffer, '3f 3f', 'in_position', 'in_normal'),
            ],
            self.index_buffer
        )

        self.agents = []
        self.last_spawn_time = 0
        self.spawn_interval = 0.5
        self.statistics = Statistics()
        self.quad_tree = None
        
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)
        self.aspect_ratio = width / height

    def initialize_agents(self, count):
        strategies = list(Strategy)
        for _ in range(count):
            x, y, z = [random.uniform(-1, 1) for _ in range(3)]
            size = 0.1
            strategy = random.choice(strategies)
            self.agents.append(Agent(x, y, z, size, strategy))

    def update_quad_tree(self):
        self.quad_tree = QuadTree((0, 0, 2, 2), 4)  
        for agent in self.agents:
            self.quad_tree.insert(agent)

    def find_nearby_agents(self, agent):
        search_radius = 0.2
        search_area = (agent.position[0], agent.position[1], search_radius, search_radius)
        return self.quad_tree.query_range(search_area)

    def update_agents(self):
        self.update_quad_tree()
        
        for agent in self.agents:
            agent.move()

        interactions_occurred = False
        for agent1 in self.agents:
            nearby_agents = self.find_nearby_agents(agent1)
            for agent2 in nearby_agents:
                if agent1 != agent2:
                    distance = np.linalg.norm(agent1.position - agent2.position)
                    if distance < 0.2:
                        self.interact(agent1, agent2)
                        interactions_occurred = True

        self.agents = [agent for agent in self.agents if agent.size > 0]
        
        if interactions_occurred:
            self.statistics.update(self.agents)
            logging.info(f"Agents count: {len(self.agents)}")

    def interact(self, agent1, agent2):
        current_time = time.time()
        
        agent1_cooperates = agent1.is_cooperative()
        agent2_cooperates = agent2.is_cooperative()
        
        payoff_matrix = {
            (True, True): (3, 3),
            (True, False): (0, 5), 
            (False, True): (5, 0),  
            (False, False): (1, 1)   
        }
        
        payoff1, payoff2 = payoff_matrix[(agent1_cooperates, agent2_cooperates)]
        
        agent1.register_interaction(payoff1 >= 3)
        agent2.register_interaction(payoff2 >= 3)

        logging.info(f"Interaction: {agent1.strategy.name} vs {agent2.strategy.name}, "
                    f"Payoffs: {payoff1}, {payoff2}")

        if payoff1 + payoff2 >= 6 and (current_time - self.last_spawn_time > self.spawn_interval):
            new_pos = (agent1.position + agent2.position) / 2 + np.random.uniform(-0.1, 0.1, 3)
            new_strategy = agent1.strategy if payoff1 > payoff2 else agent2.strategy
            self.agents.append(Agent(new_pos[0], new_pos[1], new_pos[2], 0.1, new_strategy))
            self.last_spawn_time = current_time
            logging.info(f"New agent spawned with strategy: {new_strategy.name}")
        
        if payoff1 == 0:
            agent1.size *= 0.8
        if payoff2 == 0:
            agent2.size *= 0.8

    def render(self):
        self.ctx.clear(0.0, 0.0, 0.0)
        
        proj = Matrix44.perspective_projection(45.0, self.aspect_ratio, 0.1, 100.0)
        view = Matrix44.look_at(
            (0, 0, 5),
            (0, 0, 0),
            (0, 1, 0),
        )

        rotation = Matrix44.from_y_rotation(time.time() * 0.5)
        
        for agent in self.agents:
            model = Matrix44.from_translation(agent.position.tolist())
            mvp = proj * view * rotation * model
            
            self.prog['mvp'].write(mvp.astype('f4').tobytes())
            self.prog['color'].write(agent.current_color.tobytes())
            self.vao.render()

    def run(self):
        self.initialize_agents(20)
        
        while not glfw.window_should_close(self.window):
            self.update_agents()
            self.render()
            
            glfw.swap_buffers(self.window)
            glfw.poll_events()
            time.sleep(0.01)

        glfw.terminate()

if __name__ == "__main__":
    sim = Simulation()
    sim.run()