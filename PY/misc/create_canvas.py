#!/usr/bin/env python

from swampy.TurtleWorld import *
def setup_canvas(numturtles):
   canvas = TurtleWorld()
   turtles = []
   for i in range(numturtles):
      bob=Turtle()
      turtles.append(bob)
   return turtles


   



