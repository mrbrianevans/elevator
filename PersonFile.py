import random


class Person:
    """
    This is an object used to model each person in the simulation. Each person has various attibutes
    """
    population = 0  # This keeps track of how many people have been generated

    def __init__(self, floors, floorheight):
        self.animation = None  # this stores the canvas object for each person
        self.id = Person.population
        Person.population += 1
        self.start_floor = random.randint(0, floors-1)
        self.target_floor = random.randint(0, floors-1)
        while self.start_floor == self.target_floor:
            self.target_floor = random.randint(0, floors-1)
        self.direction = (1 if self.start_floor < self.target_floor else -1)
        self.distance = floorheight * (self.start_floor - self.target_floor)
        self.finished = False
        self.in_elevator = False
        self.wait_time = 0
        self.elevator_spot = False
    def arrived(self, floor):
        """Returns true if the person has arrived at where they wanted to go"""
        return True if floor == self.target_floor else False

    def waiting(self):
        """
        Returns True if the person is not in the elevator, and they have not got where they are goin
        :return: boolean of whether or not the person is waiting for the lift
        """
        return not self.in_elevator and not self.finished
