import time

import matplotlib.pyplot as plt
from PersonFile import Person

total_wait_time = 0
people_delivered = 0

current_floor = 5
MAX_CAPACITY = 6
NUMBER_OF_FLOORS = 10
x_values = []
y_values = []
floor_height = round(600 / NUMBER_OF_FLOORS)
people = [0] * NUMBER_OF_FLOORS
arrivals = [0] * NUMBER_OF_FLOORS
arrivals_hundred = 0
peeps = []
buttons = ['none'] * NUMBER_OF_FLOORS


def elevator_down(floors: int = 1):
    global current_floor
    current_floor -= floors


def elevator_up(floors: int = 1):
    global current_floor
    current_floor += floors


def draw_person(person):
    """This is purely for animation purposes, this data is kept secret from the elevator"""
    people[person.start_floor] += 1


def button_press(floor: int, direction: str):
    if buttons[floor] == direction:
        pass
    elif buttons[floor] == 'none':
        buttons[floor] = direction
    else:
        buttons[floor] = 'both'


def populate(population=NUMBER_OF_FLOORS):
    for i in range(population):
        peep = Person(NUMBER_OF_FLOORS-1, floor_height)
        peeps.append(peep)
        draw_person(peep)
        button_press(floor=peep.start_floor, direction=peep.direction)


def stop_elavator(floor):
    global total_wait_time
    global people_delivered
    global x_values
    global y_values
    let_out(floor)
    if buttons[floor] != 'none':
        buttons[floor] = 'none'
        for person in peeps:
            if not person.finished:
                total_wait_time += 1
                x_values.append(people_delivered)
                y_values.append(total_wait_time)
                if person.start_floor == floor and not person.in_elevator:
                    person.in_elevator = True
    else:
        for person in peeps:
            if not person.finished:
                total_wait_time += 1


def let_out(floor):
    global people_delivered
    for person in peeps:
        if person.arrived(floor) and person.in_elevator:
            person.finished = True
            arrivals[floor] += 1
            person.in_elevator = False
            people_delivered += 1
            # print("person", person.id, "started at floor", person.start_floor, "and arrived at", person.target_floor)
            people[person.start_floor] -= 1


def baseline():
    while people_delivered < 10000:
        populate(NUMBER_OF_FLOORS)
        for i in range(NUMBER_OF_FLOORS-1):
            populate(1)
            stop_elavator(NUMBER_OF_FLOORS - i - 1)
            elevator_down()
        for i in range(NUMBER_OF_FLOORS-1):
            populate(1)
            stop_elavator(i)
            elevator_up()
    stop_elavator(NUMBER_OF_FLOORS-1)
    print("Total wait time to deliver", people_delivered, "people was", total_wait_time,
          "time steps")
    print("An average of", total_wait_time / people_delivered, "time steps per person in a building with", NUMBER_OF_FLOORS, "floors")
    return total_wait_time / people_delivered


if __name__ == "__main__":
    start_time = time.perf_counter()
    baseline()
    finish_time = time.perf_counter()
    print("Time taken:", finish_time-start_time, "seconds")
    plt.plot(x_values, y_values)
    plt.ylabel('Time units')
    plt.xlabel('Number of people delivered')
    plt.legend(["Cumulative wait time"])
    plt.title("Elevator simulation of building with "+str(NUMBER_OF_FLOORS)+" floors")
    plt.show()
