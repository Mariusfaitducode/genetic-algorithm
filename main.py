import time
from collections import namedtuple
from functools import partial
from random import choices, randint, randrange, random
from typing import List, Callable, Tuple


Genome = List[int]
Population = List[Genome]

#Types des fonctions permettant de réaliser un algorithme génétique
#Callable['parameters', 'return']
FitnessFunc = Callable[[Genome], int]
PopulateFunc = Callable[[], Population]
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
MutationFunc = Callable[[Genome], Genome]

Thing = namedtuple('Thing', ['name', 'value', 'weight'])

things = [
    Thing('laptop', 500, 2200),
    Thing('smartphone', 400, 300),
    Thing('solar cream', 60, 100),
    Thing('skateboard', 600, 5000),
    Thing('mug', 100, 500),
    Thing('cap', 120, 350),
    Thing('headphones', 300, 250),
]

more_things = [
    Thing('notepad', 40, 333),
    Thing('water bottle', 30, 192),
    Thing('mints', 5, 25),
    Thing('socks', 10, 38),
    Thing('tissues', 15, 80)
] + things

# Définitions des fonctions


# Génère des génomes aléatoires

def generate_genome(length: int) -> Genome:
    return choices([0, 1], k=length)


# Génère une population de genomes aléatoires

def generate_population(size: int, genome_length: int) -> Population:
    return [generate_genome(genome_length) for _ in range(size)]


# Evalue un génome en fonction des objets qu'il représente,
# retourne la valeur de tous les objets choisis si le poids est bon

def fitness(genome: Genome, things: [Thing], weight_limit: int) -> int:
    if len(genome) != len(things):
        raise ValueError("genome and things must be of the same length")
    weight = 0
    value = 0

    for i, thing in enumerate(things):
        if genome[i] == 1:
            weight += thing.weight
            value += thing.value

            if weight > weight_limit:
                return 0
    return value


# Selectionne 2 génomes qui seront retenue pour créer la prochaine génération
def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:

    non_zero_population = []
    non_zero_weights = []

    for genome in population:
        weight = fitness_func(genome)
        if weight != 0:
            non_zero_population += [genome]
            non_zero_weights += [weight]

    print(non_zero_weights)

    if not non_zero_population:
        raise ValueError("Tous les poids sont égaux à zéro.")


    # retourne 2 éléments en privilégiant ceux avec la meilleure évaluation

    return choices(
        population=non_zero_population,
        weights=non_zero_weights,
        k=2
    )


# echanger des parties du génome

def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:

    if len(a) != len(b):
        raise ValueError("Genomes a and b must be of the same length")

    length = len(a)
    if length < 2:
        return a, b

    p = randint(1, length-1)
    return a[0:p] + b[p:], b[0:p] + a[p:]


# modifie un chromosome du génome aléatoirement

def mutation(genome: Genome, num: int = 1, probability: float = 0.5) -> Genome:
    for _ in range(num):
        index = randrange(len(genome))
        genome[index] = genome[index] if random() > probability else abs(genome[index] - 1)
    return genome


def run_evolution(
        populate_func: PopulateFunc,
        fitness_func: FitnessFunc,
        fitness_limit: int,
        selection_func: SelectionFunc = selection_pair,
        crossover_func: CrossoverFunc = single_point_crossover,
        mutation_func: MutationFunc = mutation,
        generation_limit: int = 100
) -> Tuple[Population, int]:
    population = populate_func()

    # boucle parcourant les différentes générations
    for i in range(generation_limit):
        population = sorted(
            population,
            key=lambda genome: fitness_func(genome),
            reverse=True
        )

        #On vérifie si on a trouvé la solution optimale
        #if fitness_func(population[0]) >= fitness_limit:
        #    break

        #On garde nos 2 meilleurs solutions
        next_generation = population[0:2]

        #On seletionne autant de couple aléatoire que la moitié des personnes
        #Passage à la nouvelle génération

        for j in range(int(len(population) / 2) - 1):
            parents = selection_func(population, fitness_func)
            offspring_a, offspring_b = crossover_func(parents[0], parents[1])
            offspring_a = mutation_func(offspring_a)
            offspring_b = mutation_func(offspring_b)
            next_generation += [offspring_a, offspring_b]

        population = next_generation

    population = sorted(
        population,
        key=lambda genome: fitness_func(genome),
        reverse=True
    )
    return population, i


def genome_to_things(genome: Genome, things: [Thing]) -> [Thing]:
    result = []
    value = 0
    weight = 0
    for i, thing in enumerate(things):
        if genome[i] == 1:
            result += [thing.name]
            value += thing.value
            weight += thing.weight
    return result, value, weight


if __name__ == '__main__':

    print("hello world")

    start = time.time()
    population, generations = run_evolution(
        populate_func=partial(
            generate_population, size=50, genome_length=len(more_things)
        ),
        fitness_func=partial(
            fitness, things=more_things, weight_limit=3000
        ),
        fitness_limit=5000,
        generation_limit=100
    )
    end = time.time()

    print(f"number of generations: {generations}")
    print(f"time: {end - start}s")
    print(f"best solution: {genome_to_things(population[0], things)}")







