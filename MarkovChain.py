import numpy as np


class MarkovChain(object):
    """
    Class for handling Markov chain generation and sequence generation
    transition_matrix: 2D array containing probabilities of transitioning
    order: integer describing the order of the Markov chain
    states: list of strings which contain the names of the nodes within the Markov chain
    index_dict: dictionary to retrieve a states string name from an integer index ID
    state_dict: dictionary to retrieve a states integer ID from a states name as a string
    initial_probability: probability vector for choosing the initial state of the model
    """
    def __init__(self, order: int, data: list):
        self.transition_matrix = np.atleast_2d
        self.order = order
        self.data = data
        self.states = []
        self.index_dict = {}
        self.state_dict = {}
        self.initial_probability = []

    def create_transition_matrix(self):
        """
        Creates a transition matrix containing probabilities of transitioning from one node
        on a row to a node in the corresponding column. Also creates an initial probability vector.
        :return:
        """
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

        self.initial_probability = np.zeros(shape=number_states)  # Initial state probability vector

        current_state = self.states[0]
        next_state = ""

        for i in range(len(self.data) - self.order):
            next_state = str(self.data[i])
            for j in range(1, self.order):
                next_state = next_state + "|" + str(self.data[i + j])

            current_state_index = self.index_dict[current_state]
            next_state_index = self.index_dict[next_state]
            self.transition_matrix[current_state_index][next_state_index] += 1

            # Add 1 to initial probability vector when current state appears
            self.initial_probability[current_state_index] += 1
            current_state = next_state

        for row in range(self.transition_matrix.shape[0]):
            if np.sum(self.transition_matrix[row]) == 0:  # Node has zero probability so add 1 to each row entry
                self.transition_matrix[row] = 1  # Might change this in future
            self.transition_matrix[row] /= np.sum(self.transition_matrix[row])

        self.initial_probability /= np.sum(self.initial_probability)

        # Invert Probabilities Test
        # self.initial_probability = np.ones(self.initial_probability.shape) - self.initial_probability
        # self.initial_probability /= np.sum(self.initial_probability)

    def next_state(self, current_state: str) -> str:
        """
        Chooses the next state based on the current state
        :param current_state: name of the current node in sequence
        :return next_state: random next state in sequence based on probabilities in the transition matrix
        """
        next_state = np.random.choice(self.states, p=self.transition_matrix[self.index_dict[current_state], :])
        return next_state

    def generate_sequence(self, current_state: str, number_steps: int) -> list:
        current_state = np.random.choice(self.states, p=self.initial_probability)
        state_sequence = [current_state]
        for i in range(number_steps):
            next_state = self.next_state(state_sequence[i])
            state_sequence.append(next_state)
            current_state = next_state
        return state_sequence
