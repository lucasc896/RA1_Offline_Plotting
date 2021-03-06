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
from run_details import this_run

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

trigger_effs = {"200_Low":1.0,"200_High":1.0,
                "275_Low":1.0,"275_High":1.0,
                "325_Low":1.0,"325_High":1.0,
                "375_Low":1.0,"375_High":1.0,
                "475_Low":1.0,"475_High":1.0,
                "575_Low":1.0,"575_High":1.0,
                "675_Low":1.0,"675_High":1.0,
                "775_Low":1.0,"775_High":1.0,
                "875_Low":1.0,"875_High":1.0,
                "975_Low":1.0,"975_High":1.0,
                "1075_Low":1.0,"1075_High":1.0}

settings = {
  "dirs":["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"][3:],
  # "Plots":[ "PhotonPt_all", "AlphaT_all","HT_all","PhotonPFIso_all","PhotonNeutralIso_all","PhotonChargedIso_all","JetMultiplicity_all","Number_Btags_all","CommonJetPt_all","CommonJetEta_all","Number_Good_verticies_all" ] ,
  "Plots":["MET_Corrected_all"],
  "Lumo" : this_run()["ph_lumi"]*10.,
  "Webpage":"btag",
  "Category":"Photon",
  "WebBinning":["375_upwards"],
  "Misc":[],
  "MHTMET":"True",
  "Trigger":trigger_effs
      }

rootDirectory = "../" + this_run()["path_name"]

'''
Sample Instructions

1st argument - Path to root File
2nd argument - Prefix to ht bin, "Photon_","OneMuon_","DiMuon_"
3rd argument - MC Type, ( WJets,TTbar,Zinv,DY,Di-Boson,QCD,Single_Top)
4th argument - Sample Type, "Photon","Muon","DiMuon"
5th argument - Btag type, "Inclusive"(Baseline),"One","Two" etc

'''
rootpath = rootDirectory

#rootpath = "Oct_11_MHTMET"

photon_plots = {
     "nMuon":("./"+rootpath+"/Photon_Data.root","Photon_","Data","Photon","Inclusive"), 
     "mc9":("./"+rootpath+"/Photon_MC.root","Photon_","Photon","Photon","Inclusive"),
    }

photon_one_btag_plots = {
     "nbMuon":("./"+rootpath+"/Photon_Data.root","btag_one_Photon_","Data","Photon","One"), 
     "mcb7":("./"+rootpath+"/Photon_MC.root","btag_one_Photon_","Photon","Photon","One"),     
    }


photon_two_btag_plots = {
     "nbMuon":("./"+rootpath+"/Photon_Data.root","btag_two_Photon_","Data","Photon","Two"), 
     "mcb7":("./"+rootpath+"/Photon_MC.root","btag_two_Photon_","Photon","Photon","Two"), 
    }


photon_zero_btag_plots = {
     "nbMuon":("./"+rootpath+"/Photon_Data.root","btag_zero_Photon_","Data","Photon","Zero"), 
     "mcb7":("./"+rootpath+"/Photon_MC.root","btag_zero_Photon_","Photon","Photon","Zero"), 
    }

photon_morethanzero_btag_plots = {
     "nbMuon":("./"+rootpath+"/Photon_Data.root","btag_morethanzero_Photon_","Data","Photon","Zero"), 
     "mcb2":("./"+rootpath+"/Photon_MC.root","btag_morethanzero_Photon_","Photon","Photon","Zero"),
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
  b = Plotter(settings,photon_morethanzero_btag_plots,jet_multiplicity = "True",make_ratio="True")
  c = Plotter(settings,photon_two_btag_plots,jet_multiplicity = "True",make_ratio="True")
  d = Plotter(settings,photon_zero_btag_plots,jet_multiplicity = "True",make_ratio="True")
  e = Plotter(settings,photon_one_btag_plots,jet_multiplicity = "True",make_ratio="True")

  finish = Webpage_Maker(settings["Plots"],settings["WebBinning"],settings["Category"],option=settings["Webpage"])
