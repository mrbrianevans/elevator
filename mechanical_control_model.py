from datetime import datetime
import multiprocessing
import time
from tkinter import Tk, Canvas
import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
from Elevator.PersonFile import Person


def baseline_mechanical(number_of_people, number_of_floors, animate=True):
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

    if animate:  # this sets up the canvas with the elevator and floors etc if animate is true
        ANIMATION_SPEED = 0.1  # This affects how long the animations take. Higher = longer
        arrivals_population = [0] * (number_of_floors + 1)  # This is for animating purposes only
        elevator_animation = [0] * MAX_ELEVATOR_CAPACITY  # This is for people inside the elevator
        tk = Tk()
        canvas = Canvas(tk, width=2000, height=1000)
        tk.title('Elavator - baseline algorithm')
        canvas.pack()

        def move_slowly(animation, x, y):
            """This function animates people entering and exiting the elevator"""
            for j in range(0, 50):
                canvas.move(animation, x / 50, y / 50)
                tk.update()
                time.sleep(ANIMATION_SPEED / 500)

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
        elevator_floor += elevator_direction  # The lift moves one floor
        if animate:
            print('Direction', elevator_direction, 'Current floor:', elevator_floor)
            for i in range(floor_height):
                tk.update()
                time.sleep(ANIMATION_SPEED / floor_height)
                canvas.move(elevator, 0, -elevator_direction)  # animate the lift moving
                for person in elevator_population:
                    canvas.move(person.animation, 0, -elevator_direction)  # move the people 1 floor
            time.sleep(ANIMATION_SPEED)  # delay on each floor for people to get in or out
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
        for person in total_population:
            if person.waiting() and person.start_floor == elevator_floor and len(
                    elevator_population) < MAX_ELEVATOR_CAPACITY and (
                    (
                            elevator_direction == person.direction or elevator_floor == 0 or elevator_floor == number_of_floors - 1)):  # person gets in
                elevator_population.append(person)
                person.in_elevator = True
                floor_population[elevator_floor] -= 1
                if animate:
                    # shift person into elevator
                    print(elevator_animation)
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
        # if animate:
        #     time.sleep(animation_speed)
        if elevator_floor == 0:
            elevator_direction = 1
        elif elevator_floor == number_of_floors - 1:
            elevator_direction = -1
    wait_times = []
    for person in total_population:
        if not person.finished:
            print('Somethings gone wrong')
        wait_times.append(person.wait_time)

    # longest_wait_time = max(wait_times)
    average_wait_time = sum(wait_times) / number_of_people
    if animate:
        tk.mainloop()
        print('Longest wait', max(wait_times))
        print('Shortest wait', min(wait_times))
        print('Sum of all wait times', sum(wait_times))
        print(number_of_floors, 'floor building with', number_of_people, 'people')
        print('Average wait time of', average_wait_time, '\n\n')
    return average_wait_time  # Average wait time of the baseline


def worse_solution(number_of_people, number_of_floors, animate=True):
    if number_of_floors < 2 or number_of_people < 2:
        return 0
    floor_height = round(600 / number_of_floors)
    total_population = []  # This will hold Person objects
    elevator_population = []  # This monitors how many people are in the elevator
    MAX_ELEVATOR_CAPACITY = 6  # This restricts how many people can be in the elevator at any time
    floor_population = [0] * (
            number_of_floors + 1)  # This monitors how many people are waiting on each floor for the lift
    elevator_floor = 0  # starts on ground zero
    button_presses = [0] * number_of_floors
    if animate:  # this sets up the canvas with the elevator and floors etc
        tk = Tk()
        canvas = Canvas(tk, width=2000, height=1000)
        tk.title('Elavator - custom algorithm')
        canvas.pack()
        # legend
        canvas.create_oval(85, 70, 95, 80, fill='black')
        canvas.create_oval(85, 90, 95, 100, fill='white')
        canvas.create_oval(85, 110, 95, 120, fill='green')
        waiting_label = canvas.create_text(100, 75, text='Waiting', anchor='w')
        inside_label = canvas.create_text(100, 95, text='Inside elevator', anchor='w')
        delivered_label = canvas.create_text(100, 115, text='Arrived', anchor='w')
        # This next part sets up the drawing of the floors and labeling them
        for k in range(number_of_floors):
            canvas.create_line(50, 200 + (number_of_floors - k) * floor_height, 2000,
                               200 + (number_of_floors - k) * floor_height)
            canvas.create_text(5, 200 + (number_of_floors - k) * floor_height,
                               text='Floor ' + str(k), anchor='w')
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
                                                  fill='black')
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
                    elevator_population) < MAX_ELEVATOR_CAPACITY and (
                    (elevator_direction == 1 and person.target_floor < target_floor) or (
                    elevator_direction == -1 and person.target_floor > target_floor) or elevator_floor == target_floor):  # person gets in
                elevator_population.append(person)
                person.in_elevator = True
                floor_population[elevator_floor] -= 1
                if animate:
                    canvas.itemconfig(person.animation, fill='white')
                    canvas.itemconfig(inside_label,
                                      text='Inside elevator - ' + str(len(elevator_population)))
                    canvas.itemconfig(waiting_label,
                                      text='Waiting - ' + str(sum(floor_population)))
            elif person.in_elevator and person.arrived(elevator_floor):  # person gets out
                person.in_elevator = False
                person.finished = True
                elevator_population.remove(person)
                if animate:
                    canvas.itemconfig(person.animation, fill='green')
                    canvas.itemconfig(delivered_label,
                                      text='Arrived - ' + str((number_of_people - sum(
                                          floor_population) - len(elevator_population))))
                    canvas.itemconfig(waiting_label,
                                      text='Waiting - ' + str(sum(floor_population)))
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
                            'Directional vote < 0 and sum(floor_population)>0. decided to go down to floor',
                            target_floor)
                elif directional_vote > 0:
                    elevator_direction = 1
                    target_floor = highest_floor
                    if animate:
                        print(
                            'Directional vote > 0 and sum(floor_population)>0. decided to go up to floor',
                            target_floor)
                elif directional_vote == 0:  # there is equal number of people above and below
                    assert lowest_floor < elevator_floor, 'lowest_floor={}, elevator_floor={}'.format(
                        lowest_floor, elevator_floor)
                    assert highest_floor > elevator_floor, 'highest_floor={}, elevator_floor={}'.format(
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
                        print('Biased towards down when people waiting')
        elif target_floor == elevator_floor and len(
                elevator_population) > 0:  # the elevator is populated
            directional_vote = sum([1 if person.target_floor > elevator_floor else -1 for person in
                                    elevator_population])
            lowest_floor = min([person.target_floor for person in elevator_population])
            highest_floor = max([person.target_floor for person in elevator_population])
            if directional_vote == 0:
                assert lowest_floor < elevator_floor, '2lowest_floor={}, elevator_floor={}'.format(
                    lowest_floor, elevator_floor)
                assert highest_floor > elevator_floor, '2highest_floor={}, elevator_floor={}'.format(
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
                    print('Biased towards down when people in elevator')
            elif directional_vote > 0:
                elevator_direction = 1
                target_floor = highest_floor
            elif directional_vote < 0:
                elevator_direction = -1
                target_floor = lowest_floor
            if animate:
                print('The directional vote was', 'equal' if directional_vote == 0 else (
                    'to go ' + 'up' if directional_vote > 1 else 'down'))

        if (target_floor == -1 or target_floor == number_of_floors):
            print('ERROR: target floor:', target_floor, '- elevator floor:', elevator_floor)
        # elevator_direction = 1 if target_floor == -1 else elevator_direction
        # elevator_direction = -1 if target_floor == number_of_floors else elevator_direction
        # target_floor = elevator_floor + elevator_direction if target_floor == elevator_floor else target_floor
        # print('Elevator on floor', elevator_floor)
        if animate:
            print('Target floor:', target_floor, 'and direction', elevator_direction,
                  'Current floor:', elevator_floor)
            for i in range(floor_height):
                tk.update()
                time.sleep(0.2 / floor_height)
                canvas.move(elevator, 0, -elevator_direction)  # animate the lift moving
            time.sleep(0.2)
        elevator_floor += elevator_direction
        if elevator_floor > number_of_floors or elevator_floor < 0:
            print('Massive error has occured. Train off rails. Elevator is on floor',
                  elevator_floor)
        if (elevator_floor == -2 or elevator_floor == number_of_floors + 2):
            exit()
    # This processes the wait times at the end of the simulation

    wait_times = []
    for person in total_population:
        if not person.finished:
            print('Somethings gone wrong')
        wait_times.append(person.wait_time)

    longest_wait_time = max(wait_times)
    average_wait_time = sum(wait_times) / number_of_people
    if animate:
        print('Longest wait', max(wait_times))
        print('Shortest wait', min(wait_times))
        print('Sum of all wait times', sum(wait_times))
        print(number_of_floors, 'floor building with', number_of_people, 'people')
        print('Average wait time of', average_wait_time, '\n\n')
        tk.mainloop()
    return average_wait_time  # Average wait time of the custom solution


def custom_solution(number_of_people, number_of_floors, animate=True):
    if number_of_floors < 2 or number_of_people < 2:
        return 0
    floor_height = round(600 / number_of_floors)
    total_population = []  # This will hold Person objects
    elevator_population = []  # This monitors how many people are in the elevator
    MAX_ELEVATOR_CAPACITY = 6  # This restricts how many people can be in the elevator at any time
    floor_population = [0] * (
            number_of_floors + 1)  # This monitors how many people are waiting on each floor for the lift
    elevator_floor = 0  # starts on ground zero
    if animate:  # this sets up the canvas with the elevator and floors etc
        ANIMATION_SPEED = 0.1
        arrivals_population = [0] * (number_of_floors + 1)
        elevator_animation = [0] * MAX_ELEVATOR_CAPACITY
        tk = Tk()
        canvas = Canvas(tk, width=2000, height=1000)
        tk.title('Elavator - custom algorithm')
        canvas.pack()

        def move_slowly(animation, x, y):
            for j in range(0, 50):
                canvas.move(animation, x / 50, y / 50)
                tk.update()
                time.sleep(ANIMATION_SPEED / 500)

        # legend
        canvas.create_oval(85, 70, 95, 80, fill='black')
        canvas.create_oval(85, 90, 95, 100, fill='white')
        canvas.create_oval(85, 110, 95, 120, fill='green')
        waiting_label = canvas.create_text(100, 75, text='Waiting', anchor='w')
        inside_label = canvas.create_text(100, 95, text='Inside elevator', anchor='w')
        delivered_label = canvas.create_text(100, 115, text='Arrived', anchor='w')
        # This next part sets up the drawing of the floors and labeling them
        for k in range(number_of_floors):
            canvas.create_line(50, 200 + (number_of_floors - k) * floor_height, 2000,
                               200 + (number_of_floors - k) * floor_height)
            canvas.create_text(5, 200 + (number_of_floors - k) * floor_height,
                               text='Floor ' + str(k), anchor='w')
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
                                                  fill='black')
            tk.update()
        floor_population[person.start_floor] += 1
        total_population.append(person)
    elevator_direction = 1  # 1=up, -1=down

    target_floor = 0  # This is where the lift is going to at any given time
    # this checks if there are any people who have not arrived
    while sum(floor_population) + len(elevator_population) > 0:
        for person in total_population:
            person.wait_time += 1 if not person.finished else 0
            if person.in_elevator and person.arrived(elevator_floor):  # person gets out
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
        for person in total_population:
            if person.waiting() and person.start_floor == elevator_floor and len(
                    elevator_population) < MAX_ELEVATOR_CAPACITY and (
                    (elevator_direction == 1 and person.target_floor < target_floor) or (
                    elevator_direction == -1 and person.target_floor > target_floor) or elevator_floor == target_floor):  # person gets in
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
        # This is the newest version
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
                print("\ndirectional vote is {} with the lowest being {} and the highest {}".format(
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
                [1 if floor > elevator_floor else -1 for floor in range(len(elevator_buttons)) if
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
                    # print('Biased towards down when people waiting')
            elif directional_vote > 0:
                target_floor = highest_floor
            elif directional_vote < 0:
                target_floor = lowest_floor
        elevator_direction = 1 if target_floor > elevator_floor else -1
        if target_floor <= -1 or target_floor >= number_of_floors:
            print('ERROR: target floor:', target_floor, '- elevator floor:', elevator_floor)
        if animate:
            print('Target floor:', target_floor, 'and direction', elevator_direction,
                  'Current floor:', elevator_floor)
            for i in range(floor_height):
                tk.update()
                time.sleep(ANIMATION_SPEED / floor_height)
                canvas.move(elevator, 0, -elevator_direction)  # animate the lift moving
                for person in elevator_population:
                    canvas.move(person.animation, 0,
                                -elevator_direction)  # animate the people moving
            time.sleep(ANIMATION_SPEED)
        elevator_floor += elevator_direction
        if (elevator_floor >= number_of_floors or elevator_floor < 0) and animate:
            print('Massive error has occured. Train off rails. Elevator is on floor',
                  elevator_floor)
        if elevator_floor == -2 or elevator_floor == number_of_floors + 2:
            print("elevator is on floor", elevator_floor)
            exit()

    # This processes the wait times at the end of the simulation

    wait_times = []
    for person in total_population:
        if not person.finished:
            print('Somethings gone wrong')
        wait_times.append(person.wait_time)

    longest_wait_time = max(wait_times)
    average_wait_time = sum(wait_times) / number_of_people
    if animate:
        print('Longest wait', max(wait_times))
        print('Shortest wait', min(wait_times))
        print('Sum of all wait times', sum(wait_times))
        print(number_of_floors, 'floor building with', number_of_people, 'people')
        print('Average wait time of', average_wait_time, '\n\n')
        tk.mainloop()
    return average_wait_time  # Average wait time of the custom solution


def realise_iterations(algorithm, people, floors, iterations):
    starting_time = time.perf_counter()
    results = [algorithm(people, floors, False) for j in range(round(iterations / 2))]
    print("Half way there on {}(foors={}, people={}) in {}s".format(algorithm.__name__, floors,
                                                                    people, round(
            time.perf_counter() - starting_time)))
    results.extend([algorithm(people, floors, False) for j in range(round(iterations / 2))])
    return results


def realise_iterations_multicored(algorithm, people, floors, iterations):
    starting_time = time.perf_counter()
    p = multiprocessing.Pool(multiprocessing.cpu_count() - 4)
    args = [(people, floors, False) for j in range(round(iterations / 2))]
    results = p.starmap(algorithm, args)
    p.close()
    p.join()
    print("Half way there on {}(foors={}, people={}) in {}s".format(algorithm.__name__, floors,
                                                                    people, round(
            time.perf_counter() - starting_time)))

    p = multiprocessing.Pool(multiprocessing.cpu_count() - 4)
    results.extend(p.starmap(algorithm, args))
    p.close()
    p.join()
    print("Finished {}(foors={}, people={}) in {}s".format(algorithm.__name__, floors, people,
                                                           round(
                                                               time.perf_counter() - starting_time)))
    return results


def heatmap(algorithm, max_people, max_floors):
    starting_time = time.perf_counter()
    results = np.zeros(shape=(max_floors, max_people))
    for i in range(max_floors):
        for j in range(max_people):
            result = realise_iterations_multicored(algorithm, j, i, 500)
            results[i, j] = sum(result) / len(result)
        print('With', i, 'floors, data is', results[i])
        print(
            'Simulation {}% complete in {} seconds'.format(round((i - 2) / (max_floors - 2) * 100),
                                                           round(
                                                               time.perf_counter() - starting_time)))
    print(results)
    plt.style.use('fivethirtyeight')
    plt.figure(figsize=(12.80, 7.20))
    plt.pcolormesh(results, cmap='YlOrRd', norm=matplotlib.colors.DivergingNorm(vcenter=max_floors))
    plt.xlabel('Number of people')
    plt.ylabel('Number of floors')
    plt.xlim(2, max_people)
    plt.ylim(2, max_floors)
    plt.title('Heatmap showing the relative efficiency of {} algorithm'.format(algorithm.__name__))
    plt.colorbar()
    plt.show()
    return results


def heatmap_comparison(max_people, max_floors):
    starting_time = time.perf_counter()
    results = np.zeros(shape=(max_floors, max_people))
    for i in range(2, max_floors):
        for j in range(2, max_people):
            baseline_results = realise_iterations_multicored(baseline_mechanical, j, i, 15000)
            custom_results = realise_iterations_multicored(custom_solution, j, i, 15000)
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
    plt.pcolormesh(results, cmap='RdYlGn', norm=matplotlib.colors.DivergingNorm(vcenter=0))
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
    baseline_results = realise_iterations(baseline_mechanical, people, floor, 15000)
    custom_results = realise_iterations(custom_solution, people, floor, 15000)
    return sum(baseline_results) / len(baseline_results) - sum(custom_results) / len(
        custom_results)


def work_out_whole_floor(floor, people):
    print("Starting to work out floor {} at {}".format(floor, datetime.now().strftime("%H:%M:%S")))
    interval = 1 if people < 20 else round(people / 20)
    starting_time = time.perf_counter()
    row = [work_out_one_cell(floor, p) for p in range(0, people + 1, interval)]
    print("Finished floor {} in {}s".format(floor, round(time.perf_counter() - starting_time)))
    return row


def heatmap_comparison_multicored(max_people, max_floors, draw_heatmap: bool = True):
    starting_time = time.perf_counter()
    interval = 1 if max_floors < 20 else round(max_floors / 20)
    top_args = [(i, max_people) for i in range(0, max_floors + 1, interval)]
    cpus = multiprocessing.cpu_count()
    print("Your computer has {} cpus".format(cpus))
    p = multiprocessing.Pool(cpus)
    results = p.starmap(work_out_whole_floor, top_args)
    p.close()
    p.join()
    finishing_time = time.perf_counter()
    print("Calculation took {} seconds".format(round(finishing_time - starting_time)))
    print(results)
    if draw_heatmap:
        plt.style.use('fivethirtyeight')
        plt.figure(figsize=(12.80, 7.20))
        plt.pcolormesh(results, cmap='RdYlGn', norm=matplotlib.colors.DivergingNorm(vcenter=0))
        plt.xlabel('Number of people')
        plt.ylabel('Number of floors')
        plt.xlim(2, len(results[0]) - 1)
        plt.ylim(2, len(results) - 1)
        plt.xticks(np.arange(0, len(results[0]), 1), [str(int(round(i))) for i in
                                                      np.arange(0, max_people,
                                                                (max_people + 1) / len(
                                                                    results[0]))])
        plt.yticks(np.arange(0, len(results), 1), [str(int(round(i))) for i in
                                                   np.arange(0, max_floors,
                                                             (max_floors + 1) / len(results))])
        plt.title('Difference in efficiency between the baseline and my algorithm')
        colourbar = plt.colorbar()
        colourbar.set_label("Difference in average wait time", fontname='Cambria')
        plt.savefig("heatmap-{}s.png".format(round(finishing_time - starting_time)), format="png")
        plt.show()
    return results, max_people, max_floors


def interpolate_heatmap(results, people, floors):
    plt.style.use('fivethirtyeight')
    plt.figure(figsize=(12.80, 7.20))
    norm = matplotlib.colors.DivergingNorm(vcenter=0)
    plt.contourf(results, levels=600, cmap='RdYlGn', norm=norm)
    plt.xlabel('Number of people', fontname='Cambria')
    plt.ylabel('Number of floors', fontname='Cambria')
    plt.xlim(2, len(results[0]) - 1)
    plt.ylim(2, len(results) - 1)
    plt.xticks(np.arange(0, len(results[0]), 1),
               [str(int(round(i))) for i in np.arange(0, people + 1, (people) / len(results[0]))])
    plt.yticks(np.arange(0, len(results), 1),
               [str(int(round(i))) for i in np.arange(0, floors + 1, (floors) / len(results))])
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
        '{} algorithm ({} floors, {} people)\n{} simulations'.format(algorithm.__name__, floors,
                                                                     people, iterations))
    plt.show()


def graph_both_simulation_S_curve(people, floors, iterations):
    baseline_args = (baseline_mechanical, people, floors, iterations)
    custom_args = (custom_solution, people, floors, iterations)
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
    plt.plot(*custom_points, label="Custom algorithm")
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
    results = realise_iterations(algorithm, people, floors, iterations)
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
        '{} algorithm ({} floors, {} people)\n{} simulations'.format(algorithm.__name__, floors,
                                                                     people, iterations))

    plt.show()


def draw_box_plots(people, floors, iterations):
    custom_results = realise_iterations(custom_solution, people, floors, iterations)
    basline_results = realise_iterations(baseline_mechanical, people, floors, iterations)
    plt.style.use('fivethirtyeight')
    plt.figure(figsize=(16, 6))
    plt.boxplot(x=(custom_results, basline_results), vert=False, notch=False,
                labels=(['Custom algorithm', 'Basline algorithm']), autorange=True)
    plt.xlabel('Average wait time')
    plt.title('Average wait times with {} floors and {} people'.format(floors, people))
    plt.show()


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
    single_simulation("mysolution", 50, 10, animation_speed=0.5)
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
