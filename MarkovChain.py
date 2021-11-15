import numpy as np


class MarkovChain(object):
    def __init__(self, order: int, data: list):
        self.transition_matrix = np.atleast_2d
        self.order = order
        self.data = data
        self.states = []
        self.index_dict = {}
        self.state_dict = {}

    def create_transition_matrix(self):
        for i in range(len(self.data) - self.order):
            state_name = str(self.data[i])
            for j in range(1, self.order):
                state_name = state_name + "|" + str(self.data[i+j])

            if state_name not in self.states:
                self.states.append(state_name)

        number_states = len(self.states)
        self.index_dict = {self.states[index]: index for index in range(number_states)}
        self.state_dict = {index: self.states[index] for index in range(number_states)}
        self.transition_matrix = np.zeros(shape=(number_states, number_states))

        current_state = self.states[0]
        next_state = ""

        for i in range(len(self.data) - self.order):
            next_state = str(self.data[i])
            for j in range(1, self.order):
                next_state = next_state + "|" + str(self.data[i + j])

            current_state_index = self.index_dict[current_state]
            next_state_index = self.index_dict[next_state]
            self.transition_matrix[current_state_index][next_state_index] += 1
            current_state = next_state

        for row in range(self.transition_matrix.shape[0]):
            if np.sum(self.transition_matrix[row]) == 0:  # Node has zero probability so add 1 to each row entry
                self.transition_matrix[row] = 1  # Might change this in future
            self.transition_matrix[row] /= np.sum(self.transition_matrix[row])
        print(self.states)
        print(self.transition_matrix)

    def next_state(self, current_state: str) -> str:
        next_state = np.random.choice(self.states, p=self.transition_matrix[self.index_dict[current_state], :])
        return next_state

    def generate_sequence(self, current_state: str, number_steps: int) -> list:
        current_state = self.states[0]  # TEMPORARY _______________________________________
        state_sequence = [current_state]
        for i in range(number_steps):
            next_state = self.next_state(state_sequence[i])
            state_sequence.append(next_state)
            current_state = next_state
        return state_sequence
