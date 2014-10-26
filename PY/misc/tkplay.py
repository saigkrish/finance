#!/usr/bin/env python

from swampy.TurtleWorld import *
from math import pi

def setup_canvas(numturtles):
   canvas = TurtleWorld()
   turtles = [canvas]
   angle = 360.0/float(numturtles)

   for i in range(numturtles):
      bob=Turtle()
      bob.delay = 0
      turtles.append(bob)
      pu(bob)
      lt(bob,angle*i)
      fd(bob, 100)
      pd(bob)

   return turtles

def draw_polygon(turtle, edge_len, numsides, angle):
   turtle.delay = 0
   turn_degree = 360.0/numsides
   numsides=angle/360.0*numsides

   for i in range(int(numsides)):
      fd(turtle, edge_len)
      lt(turtle, turn_degree)

def draw_arc(turtle,r,angle):
   edge_len = 2*pi*r/60
   draw_polygon(turtle, edge_len, 60, angle)

def draw_concentric_circles(turtle, r, n):
   for i in range(n):
      draw_arc (turtle, r-i*float(r)/n, 360)
      pu(turtle)
      lt(turtle)
      fd(turtle, float(r)/n)
      rt(turtle)
      pd(turtle)

def draw_concentric_3d_polygon(turtle, edge_len, numsides, n):
   for i in range(n):
      draw_polygon(turtle, edge_len-i*float(edge_len)/n, numsides, 360)
      pu(turtle)
      lt(turtle)
      fd(turtle, float(edge_len)/n)
      rt(turtle)
      pd(turtle)

def draw_concentric_polygon(turtle, edge_len, numsides, n):
   ext_angle = 360.0/numsides
   int_angle = 180.0 - ext_angle
   for i in range(n):
      draw_polygon(turtle, edge_len-i*float(edge_len)/n, numsides, 360)
      pu(turtle)
      lt(turtle, int_angle/2)
      fd(turtle, float(edge_len)/(2*n))
      rt(turtle, int_angle/2)
      pd(turtle)

def draw_asterisk (turtle, size):
   lt(turtle,30)
   for i in range(5):
      draw_arc(turtle, size, 45)
      lt(turtle,180)
   rt(turtle,30)

def draw_chakra (t, size, arms):
   for i in range(arms):
	   pd(t)
	   draw_arc(t, size, 180)
	   pu(t)
	   draw_arc(t, size, 180)
	   lt(t, 360.0/arms)
   pd(t)

def draw_flower (t, size, petals):
   pd(t)
   for i in range(petals):
      draw_arc(t, size, 90)
      pu(t)
      draw_arc(t, size, 180)
      pd(t)
      draw_arc(t, size, 90)
      lt(t, 360.0/petals)

def koch (t, x):
   if (x < 3):
      fd(t, x)
      return
   else:
      m = x/3.0
      koch(t, m)
      lt(t,60)
      koch(t, m)
      rt(t,120)
      koch(t, m)
      lt(t,60)
      koch(t, m)

def snowflake (t, x):
   t.delay = 0
   for i in range(3):
      koch(t, x)
      rt(t, 120)

def draw (t, len, n):
   t.delay = 0
   if n == 0:
      return
   angle = 50
   fd(t, len*n)
   lt(t, angle)
   draw(t, len, n-1)
   rt(t, 2*angle)
   draw(t, len, n-1)
   lt(t, angle)
   bk(t, len*n)

def rd(t, n):
   for i in range(len(t)-1):
      t[i+1].redraw()
