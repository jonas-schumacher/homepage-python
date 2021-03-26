import numpy as np
from numpy.random import default_rng
import matplotlib.pyplot as plt

# Set constants
LOWER_BOUND = -20.0
UPPER_BOUND = 20.0
DIMENSIONS = 2
POP_SIZE = 20
EPOCHS = 200
RECOMBINATION_PROB = 0.3
MUTATION_PROB = 0.5
MUTATION_MEAN = 0.0
MUTATION_STD = 2.0

rng = default_rng()


class FunctionA():
    """
    Simple polynomial function
    """

    def __init__(self):
        pass

    def evaluate_fitness(self, x, y):
        return -np.power(x, 2) - np.power(y, 2)

    def plot(self, x, y):
        plt.scatter(x, y)
        plt.xlim(LOWER_BOUND, UPPER_BOUND)
        plt.ylim(LOWER_BOUND, UPPER_BOUND)
        plt.show()


class FunctionB():
    """
    More complicated landscape with three peaks as potential local maxima
    """

    def __init__(self):
        resolution = 50
        self.x = np.outer(np.linspace(LOWER_BOUND, UPPER_BOUND, resolution), np.ones(resolution))
        self.y = self.x.copy().T  # transpose

        self.peaks = np.array([[-10, -10, 10, 0.5],
                               [10, -10, 10, 0.5],
                               [-5, 10, 5, 1.5]])

    def evaluate_fitness(self, x, y):
        result = 5 * np.sin(.5 * x) * np.cos(.6 * y) + 7 * np.sin(.7 * x) * np.cos(.8 * y)
        for p in self.peaks:
            result += p[3] * np.maximum(0,
                                        np.maximum(0, (p[2] - np.abs(x - p[0]))) * np.maximum(0, (
                                                p[2] - np.abs(y - p[1]))))
        return result

    def plot(self, x, y):
        fig = plt.figure(figsize=(20, 15))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(self.x, self.y, self.evaluate_fitness(self.x, self.y) + 2.0, cmap='plasma', edgecolor='none',
                        alpha=.7)

        ax.scatter(x, y, self.evaluate_fitness(x, y), marker='o', s=100, c='black', alpha=1.0)

        ax.set_title('Optimization Landscape')
        plt.xlabel('x axis')
        plt.ylabel('y axis')
        fig.savefig('plot.png')
        plt.show()


def initialize_population():
    """
    Initialize a random population
    :return: random population
    """
    initial_pop = np.zeros((POP_SIZE, DIMENSIONS + 1))
    initial_pop[:, 0:DIMENSIONS] = rng.uniform(LOWER_BOUND, UPPER_BOUND, (POP_SIZE, DIMENSIONS))
    return initial_pop


def select_parents(pop):
    """
    fitness proportional selection
    :param pop: whole population
    :return: selected parents
    """
    fitness_proportional = (pop[:, DIMENSIONS] - pop[-1, DIMENSIONS]) / (pop[0, DIMENSIONS] - pop[-1, DIMENSIONS])
    fitness_proportional = fitness_proportional / fitness_proportional.sum()

    parents_indices = rng.choice(POP_SIZE, POP_SIZE, replace=True, p=fitness_proportional)
    parents = pop[parents_indices, :]

    return parents


def recombination(parents):
    """
    Perform recombination of parent chromosomes
    :param parents:
    :return: recombined children
    """
    # Check if recombination should be done or not
    mask = rng.uniform(0.0, 1.0, len(parents)//2) < RECOMBINATION_PROB
    # permutate parents
    parents = parents[np.random.permutation(len(parents))]
    children = np.copy(parents)
    for p in range(len(parents)//2):
        # Only recombine in certain number of cases
        if mask[p]:
            # Blend param should lie in [-0.5, 1.5]
            blend_param = 2 * rng.uniform(0.0, 1.0, DIMENSIONS) - 0.5
            for i in range(DIMENSIONS):
                # First child (for blend_param = 1 identical to first parent):
                children[2*p, i] = blend_param[i]*parents[2*p, i] + (1-blend_param[i])*parents[2*p+1, i]
                # Second child (for blend_param = 1 identical to second parent):
                children[2*p+1, i] = blend_param[i]*parents[2*p+1, i] + (1-blend_param[i])*parents[2*p, i]

    # Keep values in a healthy range:
    for i in range(DIMENSIONS):
        children[:, i] = np.clip(children[:, i], LOWER_BOUND, UPPER_BOUND)

    return children


def mutation(parents):
    """
    add normally distributed noise to real valued genes
    but only in Mutation_Prob percent of the cases
    :param parents:
    :return: mutated parents
    """
    children = np.copy(parents)

    for i in range(DIMENSIONS):
        children[:, i] = np.add(children[:, i],
                                rng.normal(MUTATION_MEAN, MUTATION_STD, len(parents)),
                                where=rng.uniform(0.0, 1.0, len(parents)) < MUTATION_PROB)

    # Keep the values in a healthy range:
    for i in range(DIMENSIONS):
        children[:, i] = np.clip(children[:, i], LOWER_BOUND, UPPER_BOUND)
    return children


def training_loop():
    """
    Iteratively evaluate, select, recombine and mutate individuals
    :return: None
    """
    fitness_history = np.zeros((EPOCHS, 2))

    # Initialize population
    pop = initialize_population()

    # Set function to be used
    function = FunctionB()

    for i in range(EPOCHS):

        # Plot current population
        if i % 20 == 0:
            function.plot(pop[:, 0], pop[:, 1])

        # 1: Evaluate population
        pop[:, DIMENSIONS] = function.evaluate_fitness(pop[:, 0], pop[:, 1])
        pop = pop[pop[:, DIMENSIONS].argsort()[::-1]]
        elite_fitness = pop[0, DIMENSIONS]
        elite_solution = pop[0, :DIMENSIONS]
        avg_fitness = pop[:, -1].mean()
        fitness_history[i, 0] = elite_fitness
        fitness_history[i, 1] = avg_fitness
        print("Best individual: {} with fitness: {} (average: {})".format(elite_solution, elite_fitness, avg_fitness))

        # Select parents among population
        parents = select_parents(pop)

        # Recombine parents
        children = recombination(parents)

        # Mutate parents
        children = mutation(children)

        # Build new population from children and best parent
        children[:, DIMENSIONS] = function.evaluate_fitness(children[:, 0], children[:, 1])
        children = children[children[:, DIMENSIONS].argsort()[::-1]]
        children[-1, :] = pop[0, :]
        pop = children

    print(pop)
    # Show fitness improvement of best individual
    plt.plot(fitness_history[:, 0])
    plt.xlabel("Generation")
    plt.ylabel("Fitness of best individual in population")
    plt.show()


if __name__ == '__main__':
    training_loop()
