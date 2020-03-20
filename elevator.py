import random
import time
from tkinter import Tk, Canvas
import matplotlib.pyplot as plt
from PersonFile import Person

tk = Tk()
canvas = Canvas(tk, width=2000, height=1000)
tk.title("Elavator")
canvas.pack()
total_wait_time = 0
people_delivered = 0

status = canvas.create_text(200, 150, text="STATUS")
time_cost = canvas.create_text(400, 150, text="Accumulated Wait Time: ")
arrivals_sign = canvas.create_text(400, 170, text="Total people delivered: ")
current_floor = 5
MAX_CAPACITY = 6
people_per_row = 120
NUMBER_OF_FLOORS = 6
speed = 0.2  # lower number for faster animation (zero for fastest simulation)
x_values = []
y_values = []
floor_height = round(600 / NUMBER_OF_FLOORS)
for k in range(NUMBER_OF_FLOORS):
    canvas.create_line(50, 800-floor_height*k, 2000, 800-floor_height*k)
    canvas.create_text(5, 800-floor_height*k, text="Floor "+str(k), anchor='w')
shaft = canvas.create_rectangle(200, 200, 400, 200+floor_height*(NUMBER_OF_FLOORS))
elavator = canvas.create_rectangle(203, 200, 397, 200+floor_height, fill='black')
# legend
canvas.create_oval(185, 70, 195, 80, fill="black")
canvas.create_oval(185, 90, 195, 100, fill="white")
canvas.create_oval(185, 110, 195, 120, fill="green")
canvas.create_text(200, 75, text="Waiting", anchor='w')
canvas.create_text(200, 95, text="Inside elevator", anchor='w')
canvas.create_text(200, 115, text="Arrived", anchor='w')
tk.update()

people = [0] * NUMBER_OF_FLOORS
arrivals = [0] * NUMBER_OF_FLOORS
peeps = []
buttons = ['none'] * NUMBER_OF_FLOORS


def set_status(message: str):
    canvas.itemconfig(status, text=message)


def set_wait_time():
    global total_wait_time
    canvas.itemconfig(time_cost, text="Accumulated Wait Time: " + str(total_wait_time))
    canvas.itemconfig(arrivals_sign, text="Total people delivered: " + str(people_delivered))


def elevator_down(floors: int = 1):
    global current_floor
    set_status("Lift going down")
    set_wait_time()
    for i in range(floors * floor_height):
        canvas.move(elavator, 0, 1)
        tk.update()
        time.sleep(speed / 100)
    set_status("Lift stopped")
    current_floor -= floors


def elevator_up(floors: int = 1):
    global current_floor
    set_wait_time()
    set_status("Lift going up")
    for i in range(floors * floor_height):
        canvas.move(elavator, 0, -1)
        tk.update()
        time.sleep(speed / 100)
    set_status("Lift stopped")
    current_floor += floors


def draw_person(person):
    """This is purely for animation purposes, this data is kept secret from the elevator"""
    offset = people[person.start_floor] * 13
    person.animation = canvas.create_oval(185 - offset, 790 - floor_height * person.start_floor,
                                          195 - offset, 800 - floor_height * person.start_floor,
                                          fill="black")
    people[person.start_floor] += 1
    tk.update()


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
        time.sleep(speed / 10)


def stop_elavator(floor):
    global total_wait_time
    global people_delivered
    global x_values
    global y_values
    let_out(floor)
    if buttons[floor] != 'none':
        time.sleep(speed / 10)

        buttons[floor] = 'none'

        for person in peeps:
            if not person.finished:
                total_wait_time += 1
                x_values.append(people_delivered)
                y_values.append(total_wait_time)
                if person.start_floor == floor and not person.in_elevator:
                    person.in_elevator = True
                    canvas.itemconfig(person.animation, fill='white')
                    tk.update()
                    time.sleep(speed / 10)
        time.sleep(speed / 10)
    else:
        for person in peeps:
            if not person.finished:
                total_wait_time += 1


def let_out(floor):
    global people_delivered
    global people_per_row
    for person in peeps:
        if person.arrived(floor) and person.in_elevator:
            time.sleep(speed / 10)
            person.finished = True
            arrivals[floor] += 1
            person.in_elevator = False
            people_delivered += 1
            pos = canvas.coords(person.animation)
            # print("person", person.id, "started at floor", person.start_floor, "and arrived at", person.target_floor)
            canvas.move(person.animation, 403 + arrivals[floor]%people_per_row * 12 - pos[2]+(arrivals[floor]//people_per_row)*17, person.distance-(arrivals[floor]//people_per_row)*10)
            canvas.itemconfig(person.animation, fill='green')
            people[person.start_floor] -= 1
            tk.update()


def baseline():
    while people_delivered < 500:
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
    print("An average of", total_wait_time / people_delivered, "time steps per person")


if __name__ == "__main__":
    baseline()
    plt.plot(x_values, y_values)
    plt.ylabel('Time units')
    plt.xlabel('Number of people delivered')
    plt.legend(["Cumulative wait time"])
    plt.title("Elevator simulation of building with "+str(NUMBER_OF_FLOORS)+" floors")
    plt.show()
    tk.mainloop()
