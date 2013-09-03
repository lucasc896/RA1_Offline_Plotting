#!/usr/bin/env python
from ROOT import *
import ROOT as r
import logging,itertools
import os,fnmatch,sys
import glob, errno
from time import strftime
from optparse import OptionParser
import array, ast
import math as m
#from plottingUtils import *
from Btag_8TeV_Plots import *


'''
Setting Intrustions

dirs - HT bins
Plots - Plots to produce Histograms for
Lumo - Scale Factor for MC
----- Webpage arguments
Webpage - Webpage mode, just keep as btag
Category - "Photon_","OneMuon","DiMuon" Used in string search when producing webpage
WebBinning - Bins that you want to show information for on website.
'''

settings = {
  "dirs":["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"],
  "Plots":[ "PhotonPt_all", "AlphaT_all","HT_all","PhotonPFIso_all","PhotonNeutralIso_all","PhotonChargedIso_all","JetMultiplicity_all","Number_Btags_all","JetPt_all","JetEta_all","Number_verticies_all","Number_Good_verticies_all" ] ,
  "Lumo" : 203.40,
  "Webpage":"btag",
  "Category":"Photon",
  "WebBinning":["375_upwards"],
  "Misc":[],
  "Trigger":{"200":1.0,"275":1.0,"325":1.0,"375":1.0,"475":1.0,"575":1.0,"675":1.0,"775":1.0,"875":1.0,"975":1.0,"1075":1.0}
      }


'''
Sample Instructions

1st argument - Path to root File
2nd argument - Prefix to ht bin, "Photon_","OneMuon_","DiMuon_"
3rd argument - MC Type, ( WJets,TTbar,Zinv,DY,Di-Boson,QCD,Single_Top)
4th argument - Sample Type, "Photon","Muon","DiMuon"
5th argument - Btag type, "Inclusive"(Baseline),"One","Two" etc

'''

photon_plots = {
     "nMuon":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data.root","Photon_","Data","Photon","Inclusive"), 
     "mc9":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC.root","Photon_","Photon","Photon","Inclusive"),
    
    }

photon_one_btag_plots = {
     "nbMuon":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data.root","btag_one_Photon_","Data","Photon","One"), 
     "mcb7":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC.root","btag_one_Photon_","Photon","Photon","One"),
        
    }


photon_two_btag_plots = {
     "nbMuon":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data.root","btag_two_Photon_","Data","Photon","Two"), 
     "mcb7":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC.root","btag_two_Photon_","Photon","Photon","Two"), 
    }


photon_zero_btag_plots = {
     "nbMuon":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data.root","btag_zero_Photon_","Data","Photon","Zero"), 
     "mcb7":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC.root","btag_zero_Photon_","Photon","Photon","Zero"),
        
    }

photon_morethanzero_btag_plots = {
     "nbMuon":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data.root","btag_morethanzero_Photon_","Data","Photon","Zero"), 
     "mcb2":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC.root","btag_morethanzero_Photon_","Photon","Photon","Zero"),
    }


'''

Plotter Instructions

Imported from Btag_plots.py
Plotter will produce all plots specified in settings["Plots"]. Option file for rebinning etc found in Btag_Plots. 

Additionally
-----------
make_ratio - Makes Data/MC ratio and fits straight line to it
jet_multiplicity - produces all different jet multiplicity categories. Otherwise just makes inclusive
'''

if __name__=="__main__":
  a = Plotter(settings,photon_plots,jet_multiplicity = "True",make_ratio="True")
  #b = Plotter(settings,photon_morethanzero_btag_plots,jet_multiplicity = "True",make_ratio="True")
  #c = Plotter(settings,photon_two_btag_plots,jet_multiplicity = "True",make_ratio="True")
  d = Plotter(settings,photon_zero_btag_plots,jet_multiplicity = "True",make_ratio="True")
  #e = Plotter(settings,photon_one_btag_plots,jet_multiplicity = "True",make_ratio="True")

  finish = Webpage_Maker(settings["Plots"],settings["WebBinning"],settings["Category"],option=settings["Webpage"])
