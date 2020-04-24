from datetime import datetime
import multiprocessing
import time
from tkinter import Tk, Canvas
import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
from Elevator.PersonFile import Person


def single_simulation(algorithm, number_of_people, number_of_floors, animate=True,
                      animation_speed=0.1):
    assert algorithm == "baseline" or algorithm == "mysolution"
    if number_of_floors < 2 or number_of_people < 2:
        return 0  # simulations can't run on less than 2 floors or 2 people

    floor_height = round(
        600 / number_of_floors)  # This is for animating people. Total size is 600px
    total_population = []  # This will hold all the Person objects
    elevator_population = []  # This monitors how many people are in the elevator at any one time
    MAX_ELEVATOR_CAPACITY = 6  # This restricts how many people can be in the elevator at any time
    # This monitors how many people are waiting on each floor for the lift
    floor_population = [0] * (number_of_floors + 1)
    elevator_floor = 0  # starts on ground zero floor
    target_floor = 0  # This is where the lift is going to at any given time
    if animate:  # this sets up the canvas with the elevator and floors etc if animate is true
        animation_speed = 0.1  # This affects how long the animations take. Higher = longer
        arrivals_population = [0] * (number_of_floors + 1)  # This is for animating purposes only
        elevator_animation = [0] * MAX_ELEVATOR_CAPACITY  # This is for people inside the elevator
        tk = Tk()
        canvas = Canvas(tk, width=2000, height=1000)
        tk.title('Elevator - {} algorithm'.format(algorithm))
        canvas.pack()

        def move_slowly(animation, x, y):
            """This function animates people entering and exiting the elevator"""
            for j in range(0, 50):
                canvas.move(animation, x / 50, y / 50)
                tk.update()
                time.sleep(animation_speed / 500)

        # This is the legend in the animation for how many people are where
        canvas.create_oval(85, 70, 95, 80, fill='black')
        canvas.create_oval(85, 90, 95, 100, fill='white')
        canvas.create_oval(85, 110, 95, 120, fill='green')
        waiting_label = canvas.create_text(100, 75, text='Waiting', anchor='w')
        inside_label = canvas.create_text(100, 95, text='Inside elevator', anchor='w')
        delivered_label = canvas.create_text(100, 115, text='Arrived', anchor='w')
        # This next part sets up the drawing of the floors and labeling them
        for k in range(number_of_floors):
            canvas.create_line(50, 200 + (number_of_floors - k) * floor_height, 600,
                               200 + (number_of_floors - k) * floor_height)
            canvas.create_text(5, 200 + (number_of_floors - k) * floor_height,
                               text='Floor ' + str(k), anchor='w')
        canvas.create_rectangle(200, 200, 400, 200 + floor_height * number_of_floors)  # shaft
        elevator = canvas.create_rectangle(203, 200 + floor_height * (number_of_floors - 1),
                                           397, 200 + floor_height * number_of_floors, fill='black')
        tk.update()

    # This section randomly generates people on different floors
    for p in range(number_of_people):
        person = Person(number_of_floors, floor_height)
        s_f = person.start_floor  # s_f is shorthand for start_floor to clean the code
        if animate:
            offset = floor_population[s_f] * 13
            person.animation = canvas.create_oval(185 - offset,  # x start
                                                  190 + (number_of_floors - s_f) * floor_height,
                                                  # y
                                                  195 - offset,  # x finish
                                                  200 + (number_of_floors - s_f) * floor_height,
                                                  # y
                                                  fill='black')
            tk.update()
        floor_population[s_f] += 1
        total_population.append(person)
    elevator_direction = 1  # 1=up, -1=down

    # This is the part which makes the lift move up and down, delivering people to their destination

    # This checks if there are any people who have not arrived
    while sum(floor_population) + len(elevator_population) > 0:
        for person in total_population:
            # This measures the wait time of each person by one unit everytime the lift moves
            # It includes time spent in the lift. It only stops counting when they have arrived
            person.wait_time += 1 if not person.finished else 0

            # This is the routine for a person leaving the elevator on their desired floor
            if person.in_elevator and person.arrived(elevator_floor):
                person.in_elevator = False
                person.finished = True
                elevator_population.remove(person)
                if animate:
                    elevator_animation[person.elevator_spot] = False
                    canvas.itemconfig(person.animation, fill='green')
                    arrivals_population[elevator_floor] += 1
                    move_slowly(person.animation, 390 + arrivals_population[elevator_floor] * 12 -
                                canvas.coords(person.animation)[0], 15 * (person.elevator_spot % 2))
                    canvas.itemconfig(delivered_label,
                                      text='Arrived - ' + str((number_of_people - sum(
                                          floor_population) - len(elevator_population))))
                    canvas.itemconfig(inside_label,
                                      text='Inside elevator - ' + str(len(elevator_population)))
                    canvas.itemconfig(waiting_label,
                                      text='Waiting - ' + str(sum(floor_population)))
        for person in total_population:  # for people to get into the elevator
            if person.waiting() and person.start_floor == elevator_floor and len(
                    elevator_population) < MAX_ELEVATOR_CAPACITY and (
                    (
                            elevator_direction == person.direction or elevator_floor == 0 or elevator_floor == number_of_floors - 1 or elevator_floor == target_floor)):  # person gets in
                elevator_population.append(person)
                person.in_elevator = True
                floor_population[elevator_floor] -= 1
                if animate:
                    # shift person into elevator
                    for spot in range(len(elevator_animation)):
                        if not elevator_animation[spot]:
                            elevator_animation[spot] = True
                            person.elevator_spot = spot
                            move_slowly(person.animation, (275 + (spot % 3) * 15) -
                                        canvas.coords(person.animation)[0], -15 * (spot % 2))
                            break
                    canvas.itemconfig(person.animation, fill='white')
                    canvas.itemconfig(inside_label,
                                      text='Inside elevator - ' + str(len(elevator_population)))
                    canvas.itemconfig(waiting_label,
                                      text='Waiting - ' + str(sum(floor_population)))
        if algorithm == "baseline":
            if elevator_floor == 0:
                elevator_direction = 1
            elif elevator_floor == number_of_floors - 1:
                elevator_direction = -1
        elif algorithm == "mysolution":
            if len(elevator_population) == MAX_ELEVATOR_CAPACITY and target_floor == elevator_floor:
                # if the elevator is full, then conduct a vote of the people inside.
                elevator_buttons = [False] * number_of_floors  # reset elevator buttons
                for person in elevator_population:
                    elevator_buttons[person.target_floor] = True
                directional_vote = sum(
                    [1 if floor > elevator_floor else -1 for floor in elevator_buttons if floor])
                highest_floor = max([i for i in range(number_of_floors) if elevator_buttons[i]])
                lowest_floor = min([i for i in range(number_of_floors) if elevator_buttons[i]])
                if animate:
                    print(
                        "\ndirectional vote is {} with the lowest being {} and the highest {}".format(
                            directional_vote, lowest_floor, highest_floor))
                if directional_vote == 0:
                    assert lowest_floor < elevator_floor, 'lowest_floor={}, elevator_floor={}'.format(
                        lowest_floor, elevator_floor)
                    assert highest_floor > elevator_floor, 'highest_floor={}, elevator_floor={}'.format(
                        highest_floor, elevator_floor)
                    # it goes the shortest distance to get half the people
                    if elevator_floor - lowest_floor < highest_floor - elevator_floor:
                        target_floor = lowest_floor
                    elif elevator_floor - lowest_floor > highest_floor - elevator_floor:
                        target_floor = highest_floor
                    else:  # if they are equal it will go down
                        target_floor = highest_floor
                        print('Biased towards down when people waiting')
                elif directional_vote > 0:
                    target_floor = highest_floor
                elif directional_vote < 0:
                    target_floor = lowest_floor

            elif target_floor == elevator_floor and sum(floor_population) + len(
                    elevator_population) > 0:
                # otherwise, combine a vote of everyone who has not arrived
                elevator_buttons = [False] * number_of_floors  # reset elevator buttons
                for person in elevator_population:
                    elevator_buttons[person.target_floor] = True
                elevator_directional_vote = sum(
                    [1 if floor > elevator_floor else -1 for floor in range(len(elevator_buttons))
                     if
                     elevator_buttons[floor]])
                floor_directional_vote = 0
                for i in range(number_of_floors):
                    if bool(floor_population[i]):  # If the button has been pressed on each floor
                        if i > elevator_floor:
                            floor_directional_vote += 1
                        elif i < elevator_floor:
                            floor_directional_vote -= 1
                directional_vote = elevator_directional_vote + floor_directional_vote
                if animate:
                    print("combined directional vote of", directional_vote, "made up of",
                          elevator_directional_vote, "from people inside the elevator and",
                          floor_directional_vote, "from people waiting on floors")
                floors_people_want_to_go_to = [i for i in range(len(elevator_buttons)) if
                                               elevator_buttons[i]]  # in elevator
                floors_people_want_to_go_to.extend([floor for floor in range(number_of_floors) if
                                                    bool(floor_population[floor])])  # on floors
                highest_floor = max(floors_people_want_to_go_to)
                lowest_floor = min(floors_people_want_to_go_to)
                if directional_vote == 0:
                    assert sum(floor_population) + len(elevator_population) > 0
                    assert lowest_floor < elevator_floor, 'lowest_floor={}, elevator_floor={}. {}(floors={}, people={}) people waiting(onfloors={}, inelevator={})'.format(
                        lowest_floor, elevator_floor, algorithm, number_of_floors, number_of_people,
                        sum(floor_population), len(elevator_population))
                    assert highest_floor > elevator_floor, 'highest_floor={}, elevator_floor={}'.format(
                        highest_floor, elevator_floor)
                    # it goes the shortest distance to get half the people
                    if elevator_floor - lowest_floor < highest_floor - elevator_floor:
                        target_floor = lowest_floor
                    elif elevator_floor - lowest_floor > highest_floor - elevator_floor:
                        target_floor = highest_floor
                    else:  # if they are equal it will go down
                        target_floor = highest_floor
                        # print('Biased towards down when people waiting')
                elif directional_vote > 0:
                    target_floor = highest_floor
                elif directional_vote < 0:
                    target_floor = lowest_floor
            if target_floor <= -1 or target_floor >= number_of_floors:
                print('ERROR: target floor:', target_floor, ', elevator floor:', elevator_floor)
            if (elevator_floor >= number_of_floors or elevator_floor < 0) and animate:
                print('Massive error has occured. Train off rails. Elevator is on floor',
                      elevator_floor)
            if elevator_floor == -2 or elevator_floor == number_of_floors + 2:
                print("elevator is on floor", elevator_floor)
                exit()
            elevator_direction = 1 if target_floor > elevator_floor else -1
        if animate:
            print('Target floor:', target_floor, 'and direction', elevator_direction,
                  'Current floor:', elevator_floor)
            for i in range(floor_height):
                tk.update()
                time.sleep(animation_speed / floor_height)
                canvas.move(elevator, 0, -elevator_direction)  # animate the lift moving
                for person in elevator_population:
                    canvas.move(person.animation, 0,
                                -elevator_direction)  # animate the people moving
            time.sleep(animation_speed)
        elevator_floor += elevator_direction  # The lift moves one floor
    wait_times = []
    for person in total_population:
        if not person.finished:
            print('Somethings gone wrong')
        wait_times.append(person.wait_time)

    longest_wait_time = max(wait_times)
    average_wait_time = sum(wait_times) / number_of_people
    if animate:
        tk.mainloop()
        print('Longest wait', longest_wait_time)
        print('Shortest wait', min(wait_times))
        print('Sum of all wait times', sum(wait_times))
        print(number_of_floors, 'floor building with', number_of_people, 'people')
        print('Average wait time of', average_wait_time, 'when using', algorithm, '\n\n')
    return average_wait_time  # Average wait time per person in this specific simulation


if __name__ == '__main__':
    print("Simulation started at {}".format(datetime.now().strftime("%H:%M:%S")))
    start_time = time.perf_counter()
    # draw_box_plots(20, 20, 1_000)
    # graph_one_simulation_frequency(custom_solution, 10, 20, 100)
    # graph_one_simulation_S_curve(custom_solution, 10, 20, 1_000)
    # graph_both_simulation_S_curve(floors=25, people=100, iterations=15_000)
    # print(*heatmap_comparison_multicored(100, 100, False))
    # interpolate_heatmap(*heatmap_comparison_multicored(100, 100))
    # interpolate_heatmap(*heatmap_comparison_multicored(25, 10))
    # interpolate_heatmap(*heatmap_comparison_multicored(25, 25))
    # heatmap(custom_solution, 20, 20)
    # custom_time = time.perf_counter()
    # print('Custom solution finished in', custom_time-start_time, 'seconds')
    # graph_one_simulation_frequency(baseline_mechanical, 10, 20, 1_000)
    # print('Baseline solution finished in', time.perf_counter()-custom_time, 'seconds')
    # run_many_simulations(baseline_mechanical, max_people=50, max_floors=50)
    #
    # baseline_mechanical(100, 25, True)
    # (custom_solution(100, 20, True))
    # single_simulation("baseline", 50, 10, animation_speed=1)
    single_simulation("mysolution", 50, 10, animation_speed=1)
    # print("Baseline averaged", sum(realise_iterations_multicored(custom_solution, 100, 25, 100_000))/100_000, "for 100 people and 25 floors")
    # single_core_count = 0
    # for m in range(10):  # should take around 500 seconds
    #     single_core_count += sum(realise_iterations(custom_solution, 100, 100, 500))
    # print(single_core_count)
    # custom_time = time.perf_counter()
    # print('Singlecored solution finished in', custom_time-start_time, 'seconds')
    # multi_core_count = 0
    # for m in range(10):  # should take around 60 seconds
    #     multi_core_count += sum(realise_iterations_multicored(custom_solution, 100, 100, 500))
    # print(multi_core_count)
    # print('Multicored solution finished in', time.perf_counter() - custom_time, 'seconds')

    finish_time = time.perf_counter()
    print('Total time taken: {}s'.format(finish_time - start_time))
