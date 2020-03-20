import time

import matplotlib.pyplot as plt
from PersonFile import Person

total_wait_time = 0
people_delivered = 0

wait_times = []
MAX_CAPACITY = 6
current_capacity = 0
global NUMBER_OF_FLOORS
x_values = []
y_values = []
a_values = []
b_values = []
floor_height = round(600 / NUMBER_OF_FLOORS)
people = [0] * NUMBER_OF_FLOORS
arrivals = [0] * NUMBER_OF_FLOORS
arrivals_hundred = 0
peeps = []
buttons = ['none'] * NUMBER_OF_FLOORS


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
    global total_wait_time, current_capacity
    global people_delivered
    global x_values
    global y_values
    let_out(floor)
    if buttons[floor] != 'none':
        buttons[floor] = 'none'
        for person in peeps:
            if not person.finished:
                person.wait_time += 1
                total_wait_time += 1
                if person.start_floor == floor and not person.in_elevator:
                    person.in_elevator = True
                    current_capacity += 1
    else:
        for person in peeps:
            if not person.finished:
                total_wait_time += 1
    x_values.append(people_delivered)
    y_values.append(total_wait_time)


def let_out(floor):
    global people_delivered, wait_times, current_capacity
    for person in peeps:
        if person.arrived(floor) and person.in_elevator:
            current_capacity -= 1
            person.finished = True
            arrivals[floor] += 1
            person.in_elevator = False
            people_delivered += 1
            # print("person", person.id, "started at floor", person.start_floor, "and arrived at", person.target_floor)
            people[person.start_floor] -= 1
            wait_times.append(person.wait_time)


def baseline(p):
    populate(p)
    while people_delivered < p:
        for i in range(NUMBER_OF_FLOORS-1):
            stop_elavator(NUMBER_OF_FLOORS - i - 1)
            elevator_down()
        for i in range(NUMBER_OF_FLOORS-1):
            stop_elavator(i)
            elevator_up()
    stop_elavator(current_floor)
    print("Total wait time to deliver", people_delivered, "people was", total_wait_time,
          "time steps")
    print("An average of", total_wait_time / people_delivered, "time steps per person in a building with", NUMBER_OF_FLOORS, "floors")
    return total_wait_time / people_delivered

def reset():
    global x_values, y_values, total_wait_time, people_delivered, people, arrivals, arrivals_hundred
    global peeps, buttons
    x_values = []
    y_values = []
    total_wait_time = 0
    people_delivered = 0
    people = [0] * NUMBER_OF_FLOORS
    arrivals = [0] * NUMBER_OF_FLOORS
    arrivals_hundred = 0
    peeps = []
    buttons = ['none'] * NUMBER_OF_FLOORS


def plot_graph():
    global x_values, y_values, NUMBER_OF_FLOORS
    plt.style.use("Solarize_Light2")
    plt.plot(x_values, y_values, color="#f56942")
    plt.ylabel('Time units')
    plt.xlabel('Number of people delivered')
    plt.legend(["Cumulative wait time"], loc="upper left")
    plt.title("Elevator simulation of building with " + str(NUMBER_OF_FLOORS) + " floors")
    plt.show()


if __name__ == "__main__":
    reset()
    NUMBER_OF_FLOORS = 8
    start_time = time.perf_counter()
    baseline(10)
    finish_time = time.perf_counter()
    print("Time taken:", finish_time-start_time, "seconds\n\n")
    plot_graph()

    reset()
    NUMBER_OF_FLOORS = 10
    start_time = time.perf_counter()
    baseline(10)
    finish_time = time.perf_counter()
    print("Time taken:", finish_time - start_time, "seconds\n\n")
    plot_graph()
