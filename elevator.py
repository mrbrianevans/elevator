import random
import time
from tkinter import Tk, Canvas

from PersonFile import Person

tk = Tk()
canvas = Canvas(tk, width=1000, height=1000)
tk.title("Elavator")
canvas.pack()

shaft = canvas.create_rectangle(200, 197, 400, 803)
elavator = canvas.create_rectangle(203, 200, 397, 300, fill='black')
status = canvas.create_text(200, 150, text="STATUS")
current_floor = 5
MAX_CAPACITY = 6
NUMBER_OF_FLOORS = 5

# floors setup
floor0 = canvas.create_line(50, 803, 550, 803)
floor1 = canvas.create_line(50, 700, 550, 700)
floor2 = canvas.create_line(50, 600, 550, 600)
floor3 = canvas.create_line(50, 500, 550, 500)
floor4 = canvas.create_line(50, 400, 550, 400)
floor5 = canvas.create_line(50, 300, 550, 300)
# labels
floor0sign = canvas.create_text(50, 790, text="Ground floor")
floor1sign = canvas.create_text(50, 690, text="Floor 1")
floor2sign = canvas.create_text(50, 590, text="Floor 2")
floor3sign = canvas.create_text(50, 490, text="Floor 3")
floor4sign = canvas.create_text(50, 390, text="Floor 4")
floor5sign = canvas.create_text(50, 290, text="Floor 5")

tk.update()

people = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
peeps = []
buttons = {0: 'none', 1: 'none', 2: 'none', 3: 'none', 4: 'none', 5: 'none'}


def set_status(message: str):
    canvas.itemconfig(status, text=message)


def elevator_down(floors: int = 1):
    global current_floor
    set_status("Lift going down")
    for i in range(floors * 100):
        canvas.move(elavator, 0, 1)
        tk.update()
        time.sleep(0.01)
    set_status("Lift stopped")
    current_floor -= floors


def elevator_up(floors: int = 1):
    global current_floor
    set_status("Lift going up")
    for i in range(floors * 100):
        canvas.move(elavator, 0, -1)
        tk.update()
        time.sleep(0.01)
    set_status("Lift stopped")
    current_floor += floors


def draw_person(person):
    """This is purely for animation purposes, this data is kept secret from the elevator"""
    offset = people[person.start_floor] * 13
    person.animation = canvas.create_oval(185 - offset, 790 - 100 * person.start_floor,
                                          195 - offset, 800 - 100 * person.start_floor,
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


def populate(population=5):
    for i in range(population):
        peep = Person(NUMBER_OF_FLOORS)
        peeps.append(peep)
        draw_person(peep)
        button_press(floor=peep.start_floor, direction=peep.direction)
        time.sleep(0.2)


def stop_elavator(floor):
    time.sleep(1)
    for peep in peeps:
        if peep.arrived(floor):
            peep.finished = True
            canvas.delete(peep.animation)


def baseline():
    while True:
        for i in range(5):
            if not buttons[5 - i] == 'none':
                stop_elavator(5 - i)
            elevator_down()
        for i in range(5):
            if not buttons[i] == 'none':
                stop_elavator(i)
            elevator_up()


if __name__ == "__main__":
    populate()
    baseline()
    tk.mainloop()
