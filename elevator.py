
from Elevator.graphs import *

if __name__ == "__main__":
    print("Simulation started at {}".format(datetime.now().strftime("%H:%M:%S")))
    start_time = time.perf_counter()

    # These are examples of simulations you could run. The heatmap ones take a while to calculate

    single_simulation(algorithm="efficient", number_of_people=30, number_of_floors=10)
    heatmap("baseline", 100, 100)
    heatmap_comparison(max_people=47, max_floors=47)
    interpolate_heatmap(*heatmap_comparison(max_people=100, max_floors=100))

    graph_single_algorithm_histogram("baseline", people=30, floors=10, iterations=100_000)
    graph_one_algorithm_frequency_curve("baseline", 30, 10, 10_000)
    graph_both_algorithms_frequency_curve(30, 10, 100_000)
    boxplot_comparison(30, 10, 1_000)

    finish_time = time.perf_counter()
    print('Total time taken: {}s'.format(finish_time - start_time))
