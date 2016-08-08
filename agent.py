import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import itertools

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.gamma = 0.4
        self.epsilon = 0.3
        self.alpha = 0.8
        self.trials = 0.0 # used to reduce epsilon value
        #Initialize Q table	
        valid_states = list(itertools.product(self.env.valid_actions, # waypoint
					 ('red', 'green'), 	# traffic light
					 self.env.valid_actions, # oncoming
					 self.env.valid_actions, # left
					 self.env.valid_actions))# right

        valid_actions = [0,0,0,0]  # Q values of valid_actions: None, 'forward'
                                     # 'left', 'right'
        self.q = {state: list(valid_actions) for state in valid_states} # create Q table

    def reset(self, destination=None):
        self.planner.route_to(destination)
        self.trials += 1
        self.epsilon = self.epsilon/(1 + ((self.trials - 1) /100)) # gradually declines as agent learns
        
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = (self.next_waypoint, inputs["light"], inputs["oncoming"], inputs["left"], 		     
                                      inputs["right"]) 

        # TODO: Select action according to your policy
	# Select action from Q function/matrix based on highest Q value/random action based on 		
    # epsilon
        action_vector = self.q[self.state]

        if random.random() < self.epsilon:
            action = random.choice(self.env.valid_actions) # if number less than epsilon, choose random action
        else:
            max_q = max(action_vector)          # otherwise choose highest-valued action from Q table
            count = action_vector.count(max_q)  # if multiple same max values, choose one at random
            if count > 1:
                best = [i for i in range(len(action_vector)) if action_vector[i] == max_q]
                max_i = random.choice(best)
            else:
                max_i = action_vector.index(max_q)
            action = self.env.valid_actions[max_i]

        q_index = self.env.valid_actions.index(action) # locate chosen action in valid_actions

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
	   # Update Q table
        next_waypoint = self.planner.next_waypoint() # self.env.sense and next_waypoint have been
						     # updated to new values
        next_inputs = self.env.sense(self)
        next_state = (next_waypoint, next_inputs["light"], next_inputs["oncoming"],  # new state information
			         next_inputs["left"], next_inputs["right"])                      # for Q value calculation
        next_action_vector = self.q[next_state]

	# Q(s,a) = Q(s,a) + alpha(R(s,a) + gamma(max(Q values of new state, action)) - Q(s,a))
        action_vector[q_index] += self.alpha * (reward + self.gamma * max(next_action_vector) 
                                                - action_vector[q_index])

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.5, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
