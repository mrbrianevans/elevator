import multiprocessing
import time
from datetime import datetime
import numpy as np
from matplotlib import colors
from matplotlib import pyplot as plt

from mechanical_control_model import single_simulation


def realise_iterations(algorithm, people, floors, iterations):
    """This method runs many simulations on 1 set of (floors, people) to find an average"""
    starting_time = time.perf_counter()
    results = [single_simulation(algorithm, people, floors, 6, False) for j in
               range(round(iterations / 2))]
    print("Half way there on {}(foors={}, people={}) in {}s".format(algorithm, floors,
                                                                    people, round(
            time.perf_counter() - starting_time)))
    results.extend(
        [single_simulation(algorithm, people, floors, 6, False) for j in
         range(round(iterations / 2))])
    return results


def realise_iterations_multicored(algorithm, people, floors, iterations):
    """
    This is just a multicored version of realise_iterations(). It is designed to be used as a
    helper method for the graphing functions, and should not be directly called
    """
    starting_time = time.perf_counter()
    p = multiprocessing.Pool(multiprocessing.cpu_count() - 4)
    args = [(algorithm, people, floors, 6, False) for j in range(round(iterations / 2))]
    results = p.starmap(single_simulation, args)
    p.close()
    p.join()
    print("Half way there on {}(foors={}, people={}) in {}s".format(algorithm, floors,
                                                                    people, round(
            time.perf_counter() - starting_time)))

    p = multiprocessing.Pool(multiprocessing.cpu_count() - 4)
    results.extend(p.starmap(single_simulation, args))
    p.close()
    p.join()
    print("Finished {}(foors={}, people={}) in {}s".format(algorithm, floors, people,
                                                           round(
                                                               time.perf_counter() - starting_time)))
    return results


def work_out_one_cell(algorithm, floor, people):
    """This is a helper method for the heatmaping function"""
    cell_result = realise_iterations(algorithm, people, floor, 20000)
    return sum(cell_result) / len(cell_result)


def work_out_whole_floor(algorithm, floor, people):
    """This is a helper method for the heatmap comparison function"""
    print("Starting to work out floor {} at {}".format(floor, datetime.now().strftime("%H:%M:%S")))
    inner_starting_time = time.perf_counter()
    row = [work_out_one_cell(algorithm, floor, person) for person in range(people)]
    print(
        "Finished floor {} in {}s".format(floor, round(time.perf_counter() - inner_starting_time)))
    return row



def heatmap(algorithm, max_people, max_floors):
    """This function draws a heatmap for a single algorithm
    from 0-max_people on the x-axis and
    from 0-max_floors on the y-axis
    It will print the results, return the results and draw the graph
    :returns the data in a form that can be drawn with the interpolate_heatmap() function"""
    starting_time = time.perf_counter()

    args = [(algorithm, i, max_people) for i in range(max_floors)]

    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    results = p.starmap(work_out_whole_floor, args)
    p.close()
    p.join()

    # results = [[0]*max_people] * max_floors
    # for i in range(max_floors):
    #     for j in range(max_people):
    #         result = realise_iterations_multicored(algorithm, j, i, 500)
    #         results[i][j] = sum(result) / len(result)
    #     # print('With', i, 'floors, data is', results[i])
    #     time_taken = round(time.perf_counter() - inner_starting_time)
    #     print(
    #         'Simulation {}% complete in {} seconds'.format(round(i / max_floors * 100), time_taken))

    print(results)
    plt.style.use('fivethirtyeight')
    plt.figure(figsize=(12.80, 7.20))
    plt.pcolormesh(results, cmap='YlOrRd', norm=colors.DivergingNorm(vcenter=max_floors))
    plt.xlabel('Number of people')
    plt.ylabel('Number of floors')
    plt.xlim(2, max_people)
    plt.ylim(2, max_floors)
    plt.title('Heatmap showing the average wait time of {} algorithm'.format(algorithm),
              fontname='Cambria', fontsize=24)
    plt.colorbar()
    plt.show()
    return results, max_people, max_floors


def work_out_one_cell_comparison(floor, people):
    """This is a helper method for the heatmaping function"""
    baseline_results = realise_iterations('baseline', people, floor, 20000)
    efficient_results = realise_iterations('efficient', people, floor, 20000)
    return sum(baseline_results) / len(baseline_results) - sum(efficient_results) / len(
        efficient_results)


def work_out_whole_floor_comparison(floor, people):
    """This is a helper method for the heatmap comparison function"""
    print("Starting to work out floor {} at {}".format(floor, datetime.now().strftime("%H:%M:%S")))
    interval = 1 if people < 20 else round(people / 10)
    starting_time = time.perf_counter()
    row = [work_out_one_cell_comparison(floor, p) for p in range(0, people + 1, interval)]
    print("Finished floor {} in {}s".format(floor, round(time.perf_counter() - starting_time)))
    return row


def heatmap_comparison(max_people, max_floors, draw_heatmap: bool = True):
    """
    This function graphs a heatmap showing the difference in average wait time of the baseline and
    my efficient algorithm where green represents the efficient algorithm having a lower average
    wait time than the baseline, and red represents the baseline having a lower average wait time.
    :param max_people:  the upper limit of the number of people.
                        If 50, then the function will graph from zero to fifty people at intervals
    :param max_floors:  the upper limit of the number of floors.
                        If 30 then the the function will calculate and graph from 0 - 30 floors
    :param draw_heatmap: whether or not to draw the heatmap. You can switch off and just get the data
    :return: the results in a form which can be graphed by the interpolate_heatmap() function
    """
    starting_time = time.perf_counter()

    interval = 1 if max_floors < 20 else round(max_floors / 10)
    top_args = [(i, max_people) for i in range(0, max_floors + 1, interval)]
    cpus = multiprocessing.cpu_count() - 4
    # Set this to a lower number if you want to use your computer for something else while simulating
    # By default it will use all available cores
    print("Your computer has {} cpus".format(cpus))
    print("Working out heatmap for {}-{} floors in steps of {}".format(0, max_floors, interval))
    p = multiprocessing.Pool(cpus)
    results = p.starmap(work_out_whole_floor_comparison, top_args)
    p.close()
    p.join()
    finishing_time = time.perf_counter()
    print("Calculation took {} seconds".format(round(finishing_time - starting_time)))
    print(results)
    if draw_heatmap:
        plt.style.use('fivethirtyeight')
        plt.figure(figsize=(12.80, 7.20))
        plt.pcolormesh(results, cmap='RdYlGn', norm=colors.DivergingNorm(vcenter=0))
        plt.xlabel('Number of people')
        plt.ylabel('Number of floors')
        plt.xlim(2, len(results[0]) - 1)
        plt.ylim(2, len(results) - 1)
        plt.xticks(np.arange(0, len(results[0]), 1), [str(int(round(i))) for i in
                                                      np.arange(0, max_people,
                                                                (max_people) / len(
                                                                    results[0]) + 1)])
        plt.yticks(np.arange(0, len(results), 1), [str(int(round(i))) for i in
                                                   np.arange(0, max_floors,
                                                             (max_floors) / len(results) + 1)])
        plt.title('Difference in efficiency between the baseline and my algorithm',
                  fontname='Cambria', fontsize=24)
        colourbar = plt.colorbar()
        colourbar.set_label("Difference in average wait time", fontname='Cambria')
        plt.savefig("heatmap-{}s.png".format(round(finishing_time - starting_time)), format="png")
        plt.show()
    return results, max_people, max_floors


def interpolate_heatmap(results, people, floors):
    """
    This function can be used to interpolate and graph data returned by the heatmap()
    and heatmap_comparison() functions. It will display and save the plot to file
    :param results: This is an array in the form: [[x, x, x], [x, x, x,], [x, x, x]] for 3x3 etc
    :param people: this is the upper limit of the number of people in the data (used to scale axis)
    :param floors: this is the upper limit of the number of floors in the data (used to scale axis)
    """
    plt.style.use('fivethirtyeight')
    plt.figure(figsize=(12.80, 7.20))
    norm = colors.DivergingNorm(vcenter=0)
    plt.contourf(results, levels=600, cmap='RdYlGn', norm=norm)
    plt.xlabel('Number of people', fontname='Cambria')
    plt.ylabel('Number of floors', fontname='Cambria')
    plt.xlim(2, len(results[0]) - 1)
    plt.ylim(2, len(results) - 1)
    plt.xticks(np.arange(0, len(results[0]), 1),
               [str(int(round(i))) for i in
                np.arange(0, people + 1, round(people / len(results[0]) + 1))])
    plt.yticks(np.arange(0, len(results), 1),
               [str(int(round(i))) for i in
                np.arange(0, floors + 1, round(floors / len(results) + 1))])
    plt.title('Difference in efficiency between the baseline and my algorithm',
              fontname='Cambria', fontsize=24)
    colourbar = plt.colorbar()
    colourbar.set_label("Difference in average wait time", fontname='Cambria')
    plt.show()
    plt.savefig("contourmap-{}.png".format(datetime.now().strftime("%H%M%S")), format="png")


def graph_one_algorithm_frequency_curve(algorithm, people, floors, iterations):
    """
    This function graphs a frequency curve for the results of iterations number of realisations of
    the specified algorithm on a system with people and floors.
    :param algorithm: the algorithm to use. Pick from 'baseline', 'inefficient' and 'efficient'
    :param people: the number of people to be generated at the start of every simulation
    :param floors: the number of floors in every simulation
    :param iterations: the total number of simulations to run. generally about 10,000 is good
    """
    results = realise_iterations(algorithm, people, floors, iterations)
    maximum = max(results)
    minimum = min(results)
    average = sum(results) / len(results)
    x_axis = np.arange(minimum, maximum, 0.1)
    y_axis = {x: 0 for x in x_axis}
    for x in x_axis:
        for re in results:
            if re < x:
                y_axis[x] += 1
    y_axis = [y_axis[x] for x in x_axis]
    plt.style.use('fivethirtyeight')
    plt.figure(figsize=(12.80, 7.20))
    plt.plot(x_axis, y_axis)
    plt.plot([average, average], [0, plt.ylim()[1]], color='#2466c9',
             label='Average=' + str(round(average, 1)))
    plt.xlim(xmin=0)
    plt.legend()
    plt.xlabel('Wait time')
    plt.ylabel('Cumulative frequency')
    plt.title(
        '{} algorithm ({} floors, {} people)\n{} simulations'.format(algorithm, floors,
                                                                     people, iterations))
    plt.show()


def graph_both_algorithms_frequency_curve(people, floors, iterations):
    """
    This function graphs the frequency curves for the baseline and efficient algorithms
    on the same axis, with average lines also drawn in. This is useful for comparing their
    performance on a particular number of floors and people.
    :param iterations: the number of iterations of each algorithm to run. Higher = more accurate
     """
    baseline_args = ('baseline', people, floors, iterations)
    efficient_args = ('efficient', people, floors, iterations)
    baseline_results = realise_iterations_multicored(*baseline_args)
    efficient_results = realise_iterations_multicored(*efficient_args)
    print("Finished simulations, calculating graph at", datetime.now().strftime("%H:%M:%S"))

    baseline_average = sum(baseline_results) / len(baseline_results)
    efficient_average = sum(efficient_results) / len(efficient_results)

    def find_data_points(results):
        """This gets the results into a form which can be easily graphed"""
        maximum = max(results)
        minimum = min(results)
        x_axis = np.arange(minimum, maximum, (maximum - minimum) / 1000)
        y_axis = {x: 0 for x in x_axis}
        for x in x_axis:
            for re in results:
                if re < x:
                    y_axis[x] += 1
        y_axis = [y_axis[x] for x in x_axis]
        return x_axis, y_axis

    plt.style.use('fivethirtyeight')
    plt.figure(figsize=(12.80, 7.20))
    baseline_points = find_data_points(baseline_results)
    efficient_points = find_data_points(efficient_results)
    plt.plot(*baseline_points, label="Baseline algorithm")
    plt.plot(*efficient_points, label="Efficient algorithm")
    ylim = plt.ylim()[1]
    plt.plot([baseline_average, baseline_average], [0, ylim], color='#2466c9',
             label='Baseline average=' + str(round(baseline_average, 1)))
    plt.plot([efficient_average, efficient_average], [0, ylim], color='#c94824',
             label='Efficient average=' + str(round(efficient_average, 1)))
    plt.legend()

    def find_axis_limits(x1_values, y1_values, x2_values, y2_values):
        """Takes off the top and bottom 1% of results from the axis limits to remove anomalies"""
        anomaly_threshold = 0.01
        x1_min, x1_max = min(x1_values), max(x1_values)
        x2_min, x2_max = min(x2_values), max(x2_values)
        for x in range(len(x1_values)):
            if y1_values[x] > (1 - anomaly_threshold) * iterations:
                x1_max = x1_values[x]
                break
            if y1_values[x] < anomaly_threshold * iterations:
                x1_min = x1_values[x]
        for x in range(len(x2_values)):
            if y2_values[x] > (1 - anomaly_threshold) * iterations:
                x2_max = x2_values[x]
                break
            if y2_values[x] < anomaly_threshold * iterations:
                x2_min = x2_values[x]
        x_min = min(x1_min, x2_min)
        x_max = max(x1_max, x2_max)
        return x_min, x_max

    plt.xlim(find_axis_limits(*baseline_points, *efficient_points))
    plt.xlabel('Wait time')
    plt.ylabel('Cumulative frequency')
    plt.title(
        'Comparing average wait time with {} floors, {} people\n{} simulations'.format(floors,
                                                                                       people,
                                                                                       iterations))
    plt.show()


def graph_single_algorithm_histogram(algorithm, people, floors, iterations):
    """
    This function graphs a histogram of the results of iterations number of realisations of a
    specified algorithm. This can be helpful to see the spread/variance or
    distribution of the wait times of a particular algorithm
    :param algorithm: the algorithm to use. Pick from 'baseline', 'inefficient' and 'efficient'
    :param people: the number of people to be generated at the start of every simulation
    :param floors: the number of floors in every simulation
    :param iterations: the total number of simulations to run. generally about 10,000 is good
    """
    results = realise_iterations_multicored(algorithm, people, floors, iterations)
    maximum = round(max(results)) + 1
    minimum = round(min(results)) - 1
    average = sum(results) / len(results)
    x_axis = np.arange(minimum, maximum, 1)
    plt.figure(figsize=(12.80, 7.20))
    plt.hist(x=results, bins=x_axis, density=True, color='#eb4034')
    plt.plot([average, average], [0, plt.ylim()[1]], color='#591208',
             label='Average=' + str(round(average, 1)))
    plt.xlim(xmin=0, xmax=30)  # round(plt.xlim()[1] + 5.1, -1)
    print("Bins are", x_axis)
    plt.xlabel('Wait time')
    plt.ylabel('Frequency density')
    plt.legend()
    plt.grid()
    plt.title(
        '{} algorithm ({} floors, {} people)\n{} simulations'.format(algorithm, floors,
                                                                     people, iterations))

    plt.show()


def boxplot_comparison(people, floors, iterations):
    """
    This function graphs two boxplots to compare the distribution of results after iterations
    number of reaslisations of the baseline and my efficient algorithm.
    The center yellow line is the median, and the outer box is the interquartile range.
    :param people: the number of people to be generated at the start of every simulation
    :param floors: the number of floors in every simulation
    :param iterations: the total number of simulations to run. generally about 1,000 is good
    Too many iterations causes the outliers to look bad, so try keep this number below 1,000
    """
    efficient_results = realise_iterations_multicored('efficient', people, floors, iterations)
    basline_results = realise_iterations_multicored('baseline', people, floors, iterations)
    plt.style.use('fivethirtyeight')
    plt.figure(figsize=(16, 6))
    plt.boxplot(x=(efficient_results, basline_results), vert=False, notch=False,
                labels=(['Efficient algorithm', 'Baseline algorithm']), autorange=True)
    plt.xlabel('Average wait time')
    plt.title('Average wait times with {} floors and {} people'.format(floors, people))
    plt.show()
