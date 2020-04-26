import multiprocessing
import time
from datetime import datetime
from Elevator.mechanical_control_model import single_simulation
import numpy as np
from matplotlib import colors
from matplotlib import pyplot as plt


def realise_iterations(algorithm, people, floors, iterations):
    """This method runs many simulations on 1 set of floors, people to find an average"""
    starting_time = time.perf_counter()
    results = [single_simulation(algorithm, people, floors, False) for j in
               range(round(iterations / 2))]
    print("Half way there on {}(foors={}, people={}) in {}s".format(algorithm, floors,
                                                                    people, round(
            time.perf_counter() - starting_time)))
    results.extend(
        [single_simulation(algorithm, people, floors, False) for j in range(round(iterations / 2))])
    return results


def realise_iterations_multicored(algorithm, people, floors, iterations):
    """This is just a multicored version of realise_iterations()"""
    starting_time = time.perf_counter()
    p = multiprocessing.Pool(multiprocessing.cpu_count() - 4)
    args = [(algorithm, people, floors, False) for j in range(round(iterations / 2))]
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


def heatmap(algorithm, max_people, max_floors):
    """This function draws a heatmap for a single algorithm
    from 0-max_people on the x-axis and
    from 0-max_floors on the y-axis
    :returns the data in a form that can be drawn with the interpolate_heatmap() function"""
    starting_time = time.perf_counter()
    results = np.zeros(shape=(max_floors, max_people))
    for i in range(max_floors):
        for j in range(max_people):
            result = realise_iterations_multicored(algorithm, j, i, 500)
            results[i, j] = sum(result) / len(result)
        # print('With', i, 'floors, data is', results[i])
        print(
            'Simulation {}% complete in {} seconds'.format(round(i / max_floors * 100),
                                                           round(
                                                               time.perf_counter() - starting_time)))
    print(results)
    plt.style.use('fivethirtyeight')
    plt.figure(figsize=(12.80, 7.20))
    plt.pcolormesh(results, cmap='YlOrRd', norm=colors.DivergingNorm(vcenter=max_floors))
    plt.xlabel('Number of people')
    plt.ylabel('Number of floors')
    plt.xlim(2, max_people)
    plt.ylim(2, max_floors)
    plt.title('Heatmap showing the relative efficiency of {} algorithm'.format(algorithm))
    plt.colorbar()
    plt.show()
    return results, max_people, max_floors


def heatmap_comparison(max_people, max_floors):
    starting_time = time.perf_counter()
    results = np.zeros(shape=(max_floors, max_people))
    for i in range(2, max_floors):
        for j in range(2, max_people):
            baseline_results = realise_iterations_multicored('baseline', j, i, 15000)
            custom_results = realise_iterations_multicored('efficient', j, i, 15000)
            results[i, j] = sum(baseline_results) / len(baseline_results) - sum(
                custom_results) / len(
                custom_results)
        print(
            'Simulation {}% complete in {} seconds'.format(round((i - 2) / (max_floors - 2) * 100),
                                                           round(
                                                               time.perf_counter() - starting_time)))

    print(results)
    plt.style.use('fivethirtyeight')
    plt.figure(figsize=(12.80, 7.20))
    plt.pcolormesh(results, cmap='RdYlGn', norm=colors.DivergingNorm(vcenter=0))
    plt.xlabel('Number of people')
    plt.ylabel('Number of floors')
    plt.xlim(2, max_people)
    plt.ylim(2, max_floors)
    plt.title('Difference in efficiency between the baseline and my algorithm')
    plt.colorbar()
    plt.savefig("heatmap.png", format="png")
    plt.show()
    print(results)


def work_out_one_cell(floor, people):
    baseline_results = realise_iterations('baseline', people, floor, 20000)
    custom_results = realise_iterations('newsolution', people, floor, 20000)
    return sum(baseline_results) / len(baseline_results) - sum(custom_results) / len(
        custom_results)


def work_out_whole_floor(floor, people):
    print("Starting to work out floor {} at {}".format(floor, datetime.now().strftime("%H:%M:%S")))
    interval = 1 if people < 20 else round(people / 10)
    starting_time = time.perf_counter()
    row = [work_out_one_cell(floor, p) for p in range(0, people + 1, interval)]
    print("Finished floor {} in {}s".format(floor, round(time.perf_counter() - starting_time)))
    return row


def heatmap_comparison_multicored(max_people, max_floors, draw_heatmap: bool = True):
    starting_time = time.perf_counter()
    interval = 1 if max_floors < 20 else round(max_floors / 10)
    top_args = [(i, max_people) for i in range(0, max_floors + 1, interval)]
    cpus = multiprocessing.cpu_count()
    print("Your computer has {} cpus".format(cpus))
    print("Working out heatmap for {}-{} floors in steps of {}".format(0, max_floors, interval))
    p = multiprocessing.Pool(cpus - 4)
    results = p.starmap(work_out_whole_floor, top_args)
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
                np.arange(0, people + 1, round((people) / len(results[0]) + 1))])
    plt.yticks(np.arange(0, len(results), 1),
               [str(int(round(i))) for i in
                np.arange(0, floors + 1, round((floors) / len(results) + 1))])
    plt.title('Difference in efficiency between the baseline and my algorithm',
              fontname='Cambria', fontsize=24)
    colourbar = plt.colorbar()
    colourbar.set_label("Difference in average wait time", fontname='Cambria')
    plt.show()
    plt.savefig("contourmap-{}.png".format(datetime.now().strftime("%H%M%S")), format="png")


def graph_one_simulation_S_curve(algorithm, people, floors, iterations):
    results = realise_iterations(algorithm, people, floors, iterations)
    maximum = max(results)
    minimum = min(results)
    x_axis = np.arange(minimum, maximum, 0.1)
    y_axis = {x: 0 for x in x_axis}
    for x in x_axis:
        for re in results:
            if re < x:
                y_axis[x] += 1
    y_axis = [y_axis[x] for x in x_axis]
    print('X', x_axis)
    print('Y', y_axis)
    plt.style.use('fivethirtyeight')
    plt.figure(figsize=(12.80, 7.20))
    plt.plot(x_axis, y_axis)
    plt.xlim(xmin=0)
    plt.xlabel('Wait time')
    plt.ylabel('Cumulative frequency')
    plt.title(
        '{} algorithm ({} floors, {} people)\n{} simulations'.format(algorithm, floors,
                                                                     people, iterations))
    plt.show()


def graph_both_simulation_S_curve(people, floors, iterations):
    # Need to add a average line to these plots ASAP!

    baseline_args = ('baseline', people, floors, iterations)
    custom_args = ('newsolution', people, floors, iterations)
    # args = [baseline_args, custom_args]
    # baseline_results, custom_results = multiprocessing.Pool().starmap(realise_iterations, args)
    baseline_results = realise_iterations_multicored(*baseline_args)
    custom_results = realise_iterations_multicored(*custom_args)
    print("Finished simulations, calculating graph at", datetime.now().strftime("%H:%M:%S"))

    def find_data_points(results):
        maximum = max(results)
        minimum = min(results)
        x_axis = np.arange(minimum, maximum, (maximum - minimum) / 1000)
        print("Stepping in steps of", (maximum - minimum) / 1000)
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
    custom_points = find_data_points(custom_results)
    plt.plot(*baseline_points, label="Baseline algorithm")
    plt.plot(*custom_points, label="Efficient algorithm")
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

    plt.xlim(find_axis_limits(*baseline_points, *custom_points))
    plt.xlabel('Wait time')
    plt.ylabel('Cumulative frequency')
    plt.title(
        'Comparing averge wait time with {} floors, {} people\n{} simulations'.format(floors,
                                                                                      people,
                                                                                      iterations))
    plt.show()


def graph_one_simulation_frequency(algorithm, people, floors, iterations):
    results = realise_iterations_multicored(algorithm, people, floors, iterations)
    maximum = round(max(results)) + 1
    minimum = round(min(results)) - 1
    average = sum(results) / len(results)
    x_axis = np.arange(minimum, maximum, 0.1)
    plt.figure(figsize=(12.80, 7.20))
    plt.hist(x=results, bins=x_axis, density=True, color='#eb4034')
    plt.plot([average, average], [0, plt.ylim()[1]], color='#591208',
             label='Average=' + str(average))
    plt.xlim(xmin=0, xmax=people * floors / 3)
    plt.xlabel('Wait time')
    plt.ylabel('Frequency density')
    plt.legend()
    plt.grid()
    plt.title(
        '{} algorithm ({} floors, {} people)\n{} simulations'.format(algorithm, floors,
                                                                     people, iterations))

    plt.show()


def draw_box_plots(people, floors, iterations):
    custom_results = realise_iterations('mysolution', people, floors, iterations)
    basline_results = realise_iterations('baseline', people, floors, iterations)
    plt.style.use('fivethirtyeight')
    plt.figure(figsize=(16, 6))
    plt.boxplot(x=(custom_results, basline_results), vert=False, notch=False,
                labels=(['Custom algorithm', 'Basline algorithm']), autorange=True)
    plt.xlabel('Average wait time')
    plt.title('Average wait times with {} floors and {} people'.format(floors, people))
    plt.show()
