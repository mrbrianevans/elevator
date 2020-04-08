import gc
import multiprocessing
import time
from tkinter import Tk, Canvas
from typing import List
import numpy as np
import matplotlib.pyplot as plt
from PersonFile import Person


def baseline_mechanical(number_of_people, number_of_floors, animate: bool = True):
    floor_height = round(600 / number_of_floors)
    total_population: List[Person] = []  # This will hold Person objects
    elevator_population = []  # This monitors how many people are in the elevator
    floor_population = [0] * (
            number_of_floors + 1)  # This monitors how many people are waiting on each floor for the lift
    elevator_floor = 0  # starts on ground zero

    if animate:  # this sets up the canvas with the elevator and floors etc
        tk = Tk()
        canvas = Canvas(tk, width=2000, height=1000)
        tk.title("Elavator - baseline mechanical algorithm")
        canvas.pack()
        # legend
        canvas.create_oval(85, 70, 95, 80, fill="black")
        canvas.create_oval(85, 90, 95, 100, fill="white")
        canvas.create_oval(85, 110, 95, 120, fill="green")
        waiting_label = canvas.create_text(100, 75, text="Waiting", anchor='w')
        inside_label = canvas.create_text(100, 95, text="Inside elevator", anchor='w')
        delivered_label = canvas.create_text(100, 115, text="Arrived", anchor='w')
        # This next part sets up the drawing of the floors and labeling them
        for k in range(number_of_floors):
            canvas.create_line(50, 200 + (number_of_floors - k) * floor_height, 2000,
                               200 + (number_of_floors - k) * floor_height)
            canvas.create_text(5, 200 + (number_of_floors - k) * floor_height,
                               text="Floor " + str(k), anchor='w')
        shaft = canvas.create_rectangle(200, 200, 400, 200 + floor_height * number_of_floors)
        # This needs to be changed so that the elevator starts at the bottom of the shaft
        elevator = canvas.create_rectangle(203, 200 + floor_height * (number_of_floors - 1),
                                           397, 200 + floor_height * number_of_floors, fill='black')
        tk.update()

    # This section randomly generates people on each floor
    for p in range(number_of_people):
        person = Person(number_of_floors, floor_height)
        if animate:
            offset = floor_population[person.start_floor] * 13
            person.animation = canvas.create_oval(185 - offset,
                                                  190 + (
                                                          number_of_floors - person.start_floor) * floor_height,
                                                  195 - offset,
                                                  200 + (
                                                          number_of_floors - person.start_floor) * floor_height,
                                                  fill="black")
            tk.update()
        floor_population[person.start_floor] += 1
        total_population.append(person)
    elevator_direction = 1  # 1=up, -1=down
    # This is the part which makes the lift move up and down, delivering people to their destination
    while sum(floor_population) + len(
            elevator_population) > 0:  # this checks if there are any people who have not arrived

        elevator_floor += elevator_direction  # The lift moves one floor
        if animate:
            for i in range(floor_height):
                tk.update()
                time.sleep(0.2 / floor_height)
                canvas.move(elevator, 0, -elevator_direction)  # animate the lift moving
        for person in total_population:
            person.wait_time += 1 if not person.finished else 0
            if person.waiting() and person.start_floor == elevator_floor and len(
                    elevator_population) < 6:  # person gets in
                elevator_population.append(person)
                person.in_elevator = True
                floor_population[elevator_floor] -= 1
                if animate:
                    canvas.itemconfig(person.animation, fill="white")
                    canvas.itemconfig(inside_label,
                                      text="Inside elevator - " + str(len(elevator_population)))
                    canvas.itemconfig(waiting_label,
                                      text="Waiting - " + str(sum(floor_population)))
            elif person.in_elevator and person.arrived(elevator_floor):  # person gets out
                person.in_elevator = False
                person.finished = True
                elevator_population.remove(person)
                if animate:
                    canvas.itemconfig(person.animation, fill="green")
                    canvas.itemconfig(delivered_label,
                                      text="Arrived - " + str((number_of_people - sum(
                                          floor_population) - len(elevator_population))))
                    canvas.itemconfig(waiting_label,
                                      text="Waiting - " + str(sum(floor_population)))
        if animate:
            time.sleep(0.2)
        if elevator_floor == 0:
            elevator_direction = 1
        elif elevator_floor == number_of_floors - 1:
            elevator_direction = -1
    wait_times = []
    for person in total_population:
        if not person.finished:
            print("Somethings gone wrong")
        wait_times.append(person.wait_time)

    longest_wait_time = max(wait_times)
    average_wait_time = sum(wait_times) / number_of_people
    if animate:
        tk.mainloop()
        print("Longest wait", max(wait_times))
        print("Shortest wait", min(wait_times))
        print("Sum of all wait times", sum(wait_times))
        print(number_of_floors, "floor building with", number_of_people, "people")
        print("Average wait time of", average_wait_time, "\n\n")
    return average_wait_time  # Average wait time of the baseline


def smart_solution(number_of_people, number_of_floors, animate: bool = True):
    floor_height = round(600 / number_of_floors)
    total_population: List[Person] = []  # This will hold Person objects
    elevator_population = []  # This monitors how many people are in the elevator
    floor_population = [0] * (
            number_of_floors + 1)  # This monitors how many people are waiting on each floor for the lift
    elevator_floor = 0  # starts on ground zero
    button_presses = [0] * number_of_floors
    if animate:  # this sets up the canvas with the elevator and floors etc
        tk = Tk()
        canvas = Canvas(tk, width=2000, height=1000)
        tk.title("Elavator - efficient algorithm")
        canvas.pack()
        # legend
        canvas.create_oval(85, 70, 95, 80, fill="black")
        canvas.create_oval(85, 90, 95, 100, fill="white")
        canvas.create_oval(85, 110, 95, 120, fill="green")
        waiting_label = canvas.create_text(100, 75, text="Waiting", anchor='w')
        inside_label = canvas.create_text(100, 95, text="Inside elevator", anchor='w')
        delivered_label = canvas.create_text(100, 115, text="Arrived", anchor='w')
        # This next part sets up the drawing of the floors and labeling them
        for k in range(number_of_floors):
            canvas.create_line(50, 200 + (number_of_floors - k) * floor_height, 2000,
                               200 + (number_of_floors - k) * floor_height)
            canvas.create_text(5, 200 + (number_of_floors - k) * floor_height,
                               text="Floor " + str(k), anchor='w')
        shaft = canvas.create_rectangle(200, 200, 400, 200 + floor_height * number_of_floors)
        # This needs to be changed so that the elevator starts at the bottom of the shaft
        elevator = canvas.create_rectangle(203, 200 + floor_height * (number_of_floors - 1),
                                           397, 200 + floor_height * number_of_floors, fill='black')
        tk.update()

    # This section randomly generates people on each floor
    for p in range(number_of_people):
        person = Person(number_of_floors, floor_height)
        if animate:
            offset = floor_population[person.start_floor] * 13
            person.animation = canvas.create_oval(185 - offset,
                                                  190 + (
                                                          number_of_floors - person.start_floor) * floor_height,
                                                  195 - offset,
                                                  200 + (
                                                          number_of_floors - person.start_floor) * floor_height,
                                                  fill="black")
            tk.update()
        floor_population[person.start_floor] += 1
        total_population.append(person)
    elevator_direction = 1  # 1=up, -1=down

    target_floor = 0  # This is where the lift is going to at any given time
    # this checks if there are any people who have not arrived
    while sum(floor_population) + len(elevator_population) > 0:

        for person in total_population:
            person.wait_time += 1 if not person.finished else 0
            if person.waiting() and person.start_floor == elevator_floor and len(
                    elevator_population) < 6 and (
                    (elevator_direction == 1 and person.target_floor < target_floor) or (
                    elevator_direction == -1 and person.target_floor > target_floor) or elevator_floor == target_floor):  # person gets in
                elevator_population.append(person)
                person.in_elevator = True
                floor_population[elevator_floor] -= 1
                if animate:
                    canvas.itemconfig(person.animation, fill="white")
                    canvas.itemconfig(inside_label,
                                      text="Inside elevator - " + str(len(elevator_population)))
                    canvas.itemconfig(waiting_label,
                                      text="Waiting - " + str(sum(floor_population)))
            elif person.in_elevator and person.arrived(elevator_floor):  # person gets out
                person.in_elevator = False
                person.finished = True
                elevator_population.remove(person)
                if animate:
                    canvas.itemconfig(person.animation, fill="green")
                    canvas.itemconfig(delivered_label,
                                      text="Arrived - " + str((number_of_people - sum(
                                          floor_population) - len(elevator_population))))
                    canvas.itemconfig(waiting_label,
                                      text="Waiting - " + str(sum(floor_population)))
        # This is the new version
        if target_floor == elevator_floor and len(
                elevator_population) == 0:  # the elevator is empty
            if sum(floor_population) == 0:  # the elevator's job is finished
                break
            else:  # This indicates there are people waiting for the lift
                directional_vote = 0
                lowest_floor = min(
                    [floor for floor in range(number_of_floors) if bool(floor_population[floor])])
                highest_floor = max(
                    [floor for floor in range(number_of_floors) if bool(floor_population[floor])])
                for i in range(number_of_floors):
                    if bool(floor_population[i]):  # If the button has been pressed on each floor
                        if i > elevator_floor:
                            directional_vote += 1
                        elif i < elevator_floor:
                            directional_vote -= 1
                if directional_vote < 0:
                    elevator_direction = -1
                    target_floor = lowest_floor
                    if animate:
                        print(
                            "Directional vote < 0 and sum(floor_population)>0. decided to go down to floor",
                            target_floor)
                elif directional_vote > 0:
                    elevator_direction = 1
                    target_floor = highest_floor
                    if animate:
                        print(
                            "Directional vote > 0 and sum(floor_population)>0. decided to go up to floor",
                            target_floor)
                elif directional_vote == 0:  # there is equal number of people above and below
                    assert lowest_floor < elevator_floor, "lowest_floor={}, elevator_floor={}".format(
                        lowest_floor, elevator_floor)
                    assert highest_floor > elevator_floor, "highest_floor={}, elevator_floor={}".format(
                        highest_floor, elevator_floor)
                    if elevator_floor - lowest_floor < highest_floor - elevator_floor:
                        elevator_direction = -1
                        target_floor = lowest_floor
                    elif elevator_floor - lowest_floor > highest_floor - elevator_floor:
                        elevator_direction = 1
                        target_floor = highest_floor
                    else:  # if they are equal it will go down
                        elevator_direction = -1
                        target_floor = lowest_floor
                        print("Biased towards down when people waiting")
        elif target_floor == elevator_floor and len(
                elevator_population) > 0:  # the elevator is populated
            directional_vote = sum([1 if person.target_floor > elevator_floor else -1 for person in
                                    elevator_population])
            lowest_floor = min([person.target_floor for person in elevator_population])
            highest_floor = max([person.target_floor for person in elevator_population])
            if directional_vote == 0:
                assert lowest_floor < elevator_floor, "2lowest_floor={}, elevator_floor={}".format(
                    lowest_floor, elevator_floor)
                assert highest_floor > elevator_floor, "2highest_floor={}, elevator_floor={}".format(
                    highest_floor, elevator_floor)
                if elevator_floor - lowest_floor < highest_floor - elevator_floor:
                    elevator_direction = -1
                    target_floor = lowest_floor
                elif elevator_floor - lowest_floor > highest_floor - elevator_floor:
                    elevator_direction = 1
                    target_floor = highest_floor
                else:  # if they are equal it will go down
                    elevator_direction = -1
                    target_floor = lowest_floor
                    print("Biased towards down when people in elevator")
            elif directional_vote > 0:
                elevator_direction = 1
                target_floor = highest_floor
            elif directional_vote < 0:
                elevator_direction = -1
                target_floor = lowest_floor
            if animate:
                print("The directional vote was", "equal" if directional_vote == 0 else (
                    "to go " + "up" if directional_vote > 1 else "down"))

        # This is the broken version
        # if target_floor == elevator_floor and sum(floor_population) > 0:
        #     in_elevator_buttons = [False] * number_of_floors
        #     directional_vote = 0
        #     for person in elevator_population:
        #         in_elevator_buttons[person.target_floor] = True
        #         directional_vote += 1 if person.target_floor > elevator_floor else -1
        #     if directional_vote == 0:
        #         buttons_above_pressed = [floor for floor in
        #                                  range(elevator_floor + 1, number_of_floors) if
        #                                  bool(floor_population[floor])]
        #         buttons_below_pressed = [floor for floor in range(elevator_floor) if
        #                                  bool(floor_population[floor])]
        #         elevator_direction = 1 if len(buttons_above_pressed) > len(
        #             buttons_below_pressed) else -1
        #         target_floor = (min(buttons_below_pressed) if elevator_direction == -1 else max(
        #             buttons_above_pressed)) if not buttons_above_pressed == buttons_below_pressed else elevator_floor + elevator_direction
        #         print("The elevator is full" if len(
        #             elevator_population) == 6 else "The elevator has spare capacity to pick people up")
        #         print("Directional vote == 0 and sum(floor_population)>0. Decided to go",
        #               "down" if elevator_direction == -1 else "up", "to floor", target_floor,
        #               "because there are", floor_population[target_floor], "people on floor",
        #               target_floor)
        #         print(floor_population, buttons_below_pressed, buttons_above_pressed)
        #     elif directional_vote < 0:
        #         elevator_direction = -1
        #         furthest_floor = min([person.target_floor for person in elevator_population])
        #         target_floor = furthest_floor
        #         print("Directional vote < 0 and sum(floor_population)>0")
        #     elif directional_vote > 0:
        #         elevator_direction = 1
        #         furthest_floor = max([person.target_floor for person in elevator_population])
        #         target_floor = furthest_floor
        #         print("Directional vote > 0 and sum(floor_population)>0")
        # elif target_floor == elevator_floor and len(elevator_population) > 0:
        #     in_elevator_buttons = [False] * number_of_floors
        #     directional_vote = 0
        #     for person in elevator_population:
        #         in_elevator_buttons[person.target_floor] = True
        #         directional_vote += 1 if person.target_floor > elevator_floor else -1
        #     if directional_vote == 0:
        #         elevator_direction = 1 if elevator_floor < number_of_floors / 2 else -1
        #         target_floor = elevator_floor + elevator_direction
        #         print("CYCLICAL MIDDLE ERROR")
        #     elif directional_vote < 0:
        #         elevator_direction = -1
        #         furthest_floor = min([person.target_floor for person in elevator_population])
        #         target_floor = furthest_floor
        #         print("Directional vote < 0 and sum(elevator_population)>0")
        #     elif directional_vote > 0:
        #         elevator_direction = 1
        #         furthest_floor = max([person.target_floor for person in elevator_population])
        #         target_floor = furthest_floor
        #         print("Directional vote > 0 and sum(elevator_population)>0")
        # elif target_floor == elevator_floor:
        #     print("reached the end")
        #     break
        if (target_floor == -1 or target_floor == number_of_floors):
            print("ERROR: target floor:", target_floor, "- elevator floor:", elevator_floor)
        # elevator_direction = 1 if target_floor == -1 else elevator_direction
        # elevator_direction = -1 if target_floor == number_of_floors else elevator_direction
        # target_floor = elevator_floor + elevator_direction if target_floor == elevator_floor else target_floor
        # print("Elevator on floor", elevator_floor)
        if animate:
            print("Target floor:", target_floor, "and direction", elevator_direction,
                  "Current floor:", elevator_floor)
            for i in range(floor_height):
                tk.update()
                time.sleep(0.2 / floor_height)
                canvas.move(elevator, 0, -elevator_direction)  # animate the lift moving
            time.sleep(0.2)
        elevator_floor += elevator_direction
        if elevator_floor > number_of_floors or elevator_floor < 0:
            print("Massive error has occured. Train off rails. Elevator is on floor",
                  elevator_floor)
        if (elevator_floor == -2 or elevator_floor == number_of_floors + 2):
            exit()
    # This processes the wait times at the end of the simulation

    wait_times = []
    for person in total_population:
        if not person.finished:
            print("Somethings gone wrong")
        wait_times.append(person.wait_time)

    longest_wait_time = max(wait_times)
    average_wait_time = sum(wait_times) / number_of_people
    if animate:
        print("Longest wait", max(wait_times))
        print("Shortest wait", min(wait_times))
        print("Sum of all wait times", sum(wait_times))
        print(number_of_floors, "floor building with", number_of_people, "people")
        print("Average wait time of", average_wait_time, "\n\n")
        tk.mainloop()
    return average_wait_time  # Average wait time of the efficient solution


def realise_iterations(algorithm, people, floors, iterations):
    results = [algorithm(people, floors, False) for j in range(iterations)]
    return results


def run_many_simulations(algorithm, max_people, max_floors):
    results = np.zeros(shape=(max_floors, max_people))
    for i in range(2, max_floors):
        for j in range(2, max_people):
            result = realise_iterations(algorithm, j, i, 500)
            results[i, j] = sum(result) / len(result)
        # print("With", i, "floors, data is", results[i])
    print(results)
    plt.style.use("fivethirtyeight")
    plt.figure(figsize=(12.80, 7.20))
    plt.pcolormesh(results, cmap="YlOrRd")
    plt.xlabel("Number of people")
    plt.ylabel("Number of floors")
    plt.xlim(2, max_people)
    plt.ylim(2, max_floors)
    plt.title("Heatmap showing the relative efficiency of {} algorithm".format(algorithm.__name__))
    plt.colorbar()
    plt.show()
    return results


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
    print("X", x_axis)
    print("Y", y_axis)
    plt.plot(x_axis, y_axis)
    plt.xlabel("Wait time")
    plt.ylabel("Cumulative frequency")
    plt.legend()
    plt.title(
        "{} algorithm ({} floors, {} people)\n{} simulations".format(algorithm.__name__, floors,
                                                                     people, iterations))
    plt.show()


def graph_one_simulation_frequency(algorithm, people, floors, iterations):
    results = realise_iterations(algorithm, people, floors, iterations)
    maximum = round(max(results)) + 1
    minimum = round(min(results)) - 1
    average = sum(results) / len(results)
    x_axis = np.arange(minimum, maximum, 0.1)
    plt.style.use("fivethirtyeight")
    plt.figure(figsize=(12.80, 7.20))
    plt.hist(x=results, bins=x_axis, density=True, color="#eb4034")
    plt.plot([average, average], [0, plt.ylim()[1]], color="#591208",
             label="Average=" + str(average))
    plt.xlim(xmin=0, xmax=people * floors / 3)
    plt.xlabel("Wait time")
    plt.ylabel("Frequency density")
    plt.legend()
    plt.grid()
    plt.title(
        "{} algorithm ({} floors, {} people)\n{} simulations".format(algorithm.__name__, floors,
                                                                     people, iterations))

    plt.show()


def draw_box_plots(people, floors, iterations):
    custom_results = realise_iterations(smart_solution, people, floors, iterations)
    basline_results = realise_iterations(baseline_mechanical, people, floors, iterations)
    plt.style.use("fivethirtyeight")
    plt.figure(figsize=(16, 6))
    plt.boxplot(x=(custom_results, basline_results), vert=False, notch=False,
                labels=(["Custom algorithm", "Basline algorithm"]), autorange=True)
    plt.xlim(xmin=0)
    plt.xlabel("Average wait time")
    plt.title("Average wait times with {} floors and {} people".format(floors, people))
    plt.show()

if __name__ == "__main__":
    start_time = time.perf_counter()
    draw_box_plots(20, 20, 1_000)
    # graph_one_simulation_frequency(smart_solution, 10, 20, 1_000)
    # custom_time = time.perf_counter()
    # print("Custom solution finished in", custom_time-start_time, "seconds")
    # graph_one_simulation_frequency(baseline_mechanical, 10, 20, 1_000)
    # print("Baseline solution finished in", time.perf_counter()-custom_time, "seconds")
    # run_many_simulations(baseline_mechanical, max_people=50, max_floors=50)

    # baseline_mechanical(20, 10, False)
    # (smart_solution(20, 10, True))

    finish_time = time.perf_counter()
    print("Total time taken: {}s".format(finish_time - start_time))
