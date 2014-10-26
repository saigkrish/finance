#!/usr/bin/env python

def is_palindrome(str):
   if len(str) < 2:
      return True
   if ((str[0] == str[-1]) and is_palindrome(str[1:-1])):
      return True
   else:
      return False



