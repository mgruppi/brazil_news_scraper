# -*- coding: utf-8 -*-
"""
By: mgruppi
Progress bar
"""
import sys
import tty_colors as TTY
from time import sleep

#TTY colors
def progress_bar_color(count,total,bar_length=50,msg=''):
    tick_ = '='
    void_ = '-'
    p = 100.0*(count)/total
    filled = (count*bar_length/total)
    ticks = tick_ * filled
    unfilled = void_ * (bar_length-filled)
    sys.stdout.write("\r[%s%s%s%s%s]%.1f%s %s\r\t" %(TTY.LIGHTGREEN,ticks,TTY.LIGHTRED,unfilled,TTY.DEFAULT,p,'%',msg))

def progress_bar(count,total,bar_length=50,msg=''):
    tick_ = '='
    void_ = '-'
    p = 100.0*(count)/total
    filled = (count*bar_length/total)
    ticks = tick_ * filled
    unfilled = void_ * (bar_length-filled)
    sys.stdout.write("\r[%s%s]%.1f%s %s\r" %(ticks,unfilled,p,'%',msg))
    
def main():
    #USAGE:
    total = 500
    for i in range(0,total+1):
        sleep(.01)
        progress_bar_color(i,total,msg='color!')
    print ()
    for i in range(0,total+1):
        sleep(.01)
        progress_bar(i,total,10,'shorter, no color')
        
if __name__=='__main__':
    main()
