#!/usr/bin/env python

import logging,itertools
import os,fnmatch,sys
import glob,errno
import array
import math as m

plot_dirs = {}

for root,dirs,files in os.walk('./'):
  go = "True"
  for filename in fnmatch.filter(files,'*.html'):
      while go == "True" and root !='./':
        plot_dirs[root] = filename
        go = "False"


htF = open('./RA1_Website_Plots.html','w')
htF.write('Author: Darren Burton \n')
htF.write('<img height=\"50\" style = "float:right" src=\"uob.gif\"><img height=\"50\" style = "float:right" src=\"imp.png\"> <br>\n')
htF.write('Analyser: Chris Lucas <br>\n')
htF.write('<script language="Javascript"> \n document.write("Last Modified: " + document.lastModified + ""); \n </script> \n ')
htF.write('<br><br> \n')
htF.write('<img height=\"60\" style = "float:right" src=\"cms.png\">')
# htF.write('<img height=\"50\" style = "float:right" src=\"uob.gif\"><img height=\"50\" style = "float:right" src=\"imp.png\"> <br>\n')
htF.write('<br><br><br><br><br><br><br> \n')
htF.write('<center>\n <p> \n <font size="16"> -- RA1 Data/MC plot webpage -- </font>\n </p></center>\n')
htF.write('<br>\n<center><img height=\"200\" width=\"480\" src=\"col.png\"></center>')
htF.write('<br><br><br><br> \n')
htF.write('<font size="5"> Choose Plot Category: </font>\n\n')
htF.write('<center>')
for entry in plot_dirs:
  htF.write('<a href=\"'+entry+'/'+plot_dirs[entry]+'\"><font size = "6">    '+ entry.lstrip('./')+'</font></a>')  #(entry.split('_')[0]).lstrip('./')+'</font></a>')
  htF.write('<font size = "6">     |   </font>  ')
htF.write('</center>')  
htF.write('<br><br><br><br> \n')
htF.write('<font style="italics" size="3"> NB: Each Plot is available in .pdf and .C. Simply change .png extension in address bar to relevant format </font>')
