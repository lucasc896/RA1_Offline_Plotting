#!/usr/bin/env python
import ROOT as r
import logging,itertools
import os,fnmatch,sys
import glob, errno
from time import strftime, time
from optparse import OptionParser
import array, ast
import math as m
#from plottingUtils import *
from Btag_8TeV_Plots import *
import shutil

r.gROOT.SetBatch(r.kTRUE)

"""
Input dirs in file
Plots you want to make
Luminosity 
Webbinning - Plots you want displayed on website
Trigger - Trigger efficiencies


Misc - Is just a collection of options I pass sometimes to implement a bunch of hacks, because sometimes people have come up with annoying little studies and this was the quickest way to implement the information without rewriting the code. These include Normalising histograms to just compare shapes of distributions etc
"""

baseTime = time()

settings = {
  "dirs":["150_200","200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"],
  "Plots":["MHTovMET_all","MHT_all","AlphaT_all","JetPt_all","HT_all","Number_Btags_all","JetMultiplicity_all","JetEta_all","MuPt_all","MuEta_all","MuPFIso_all","MT__all","Number_Good_verticies_all"],
  "Lumo" : 192.55,
  "Webpage":"btag",
  "Category":"OneMuon",
  "WebBinning":["150_200","200_upwards","375_upwards"],
  "Misc":[],
  "MHTMET":"True",
  "Trigger":{"150":0.88,"200":0.88,"275":0.88,"325":0.88,"375":0.88,"475":0.88,"575":0.88,"675":0.88,"775":0.88,"875":0.88,"975":0.88,"1075":0.88}
  }

rootpath = "FullDataset_Root_Files_Correct_PU"
njet_ext = ""
"""
rootpath = "NewConfig_RootFiles"
njet_ext = "_NJet"
"""
muon_2d = {
     "nMuon":("./"+rootpath+"/Muon_EWK"+njet_ext+".root","OneMuon_","Data","Muon","Inclusive"), 
     "mc2":("./"+rootpath+"/Muon_EWK"+njet_ext+".root","OneMuon_","SMS","Muon","Inclusive"),
    }

muon_2d_data = {
     "nMuon":("./"+rootpath+"/Muon_Data.root","OneMuon_","Data","Muon","Inclusive"), 
    }

muon_2d_ratios = {
     "nMuon":("./"+rootpath+"/MHTMET_ratio.root","OneMuon_","Data","Muon","Inclusive"), 
     #"mc2":("./"+rootpath+"/Muon_Data.root","OneMuon_","SMS","Muon","Inclusive"),

    }


muon_plots = {
     "nMuon":("./"+rootpath+"/Muon_Data.root","OneMuon_","Data","Muon","Inclusive"), 
     "mc2":("./"+rootpath+"/Muon_WJets"+njet_ext+".root","OneMuon_","WJets","Muon","Inclusive"),
     "mc3":("./"+rootpath+"/Muon_TTbar.root","OneMuon_","TTbar","Muon","Inclusive"),
     "mc4":("./"+rootpath+"/Muon_Zinv.root","OneMuon_","Zinv","Muon","Inclusive"),
     "mc5":("./"+rootpath+"/Muon_DY"+njet_ext+".root","OneMuon_","DY","Muon","Inclusive"),
     "mc7":("./"+rootpath+"/Muon_DiBoson.root","OneMuon_","Di-Boson","Muon","Inclusive"),
     #"mc8":("./"+rootpath+"/Muon_QCD.root","OneMuon_","QCD","Muon","Inclusive"), 
     "mc9":("./"+rootpath+"/Muon_SingleTop.root","OneMuon_","Single_Top","Muon","Inclusive"),
    }

muon_one_btag_plots = {
     "nbMuon":("./"+rootpath+"/Muon_Data.root","btag_one_OneMuon_","Data","Muon","One"), 
     #"mcb1":("./"+rootpath+"/Muon_MC.root","btag_one_OneMuon_","MC Combined","Muon","One"),
     "mcb2":("./"+rootpath+"/Muon_WJets"+njet_ext+".root","btag_one_OneMuon_","WJets","Muon","One"),
     "mcb3":("./"+rootpath+"/Muon_TTbar.root","btag_one_OneMuon_","TTbar","Muon","One"),
     "mcb4":("./"+rootpath+"/Muon_Zinv.root","btag_one_OneMuon_","Zinv","Muon","One"),
     "mcb5":("./"+rootpath+"/Muon_DY"+njet_ext+".root","btag_one_OneMuon_","DY","Muon","One"),
     "mcb6":("./"+rootpath+"/Muon_SingleTop.root","btag_one_OneMuon_","Single_Top","Muon","One"),
     "mcb7":("./"+rootpath+"/Muon_DiBoson.root","btag_one_OneMuon_","Di-Boson","Muon","One"),
    # "mcb8":("./"+rootpath+"/Muon_QCD.root","btag_one_OneMuon_","QCD","Muon","One"), 
    }


muon_two_btag_plots = {
     "nbMuon":("./"+rootpath+"/Muon_Data.root","btag_two_OneMuon_","Data","Muon","Two"), 
     "mcb2":("./"+rootpath+"/Muon_WJets"+njet_ext+".root","btag_two_OneMuon_","WJets","Muon","Two"),
     "mcb3":("./"+rootpath+"/Muon_TTbar.root","btag_two_OneMuon_","TTbar","Muon","Two"),
     "mcb4":("./"+rootpath+"/Muon_Zinv.root","btag_two_OneMuon_","Zinv","Muon","Two"),
     "mcb5":("./"+rootpath+"/Muon_DY"+njet_ext+".root","btag_two_OneMuon_","DY","Muon","Two"),
     "mcb6":("./"+rootpath+"/Muon_SingleTop.root","btag_two_OneMuon_","Single_Top","Muon","Two"),
     "mcb7":("./"+rootpath+"/Muon_DiBoson.root","btag_two_OneMuon_","Di-Boson","Muon","Two"), 
     #"mcb8":("./"+rootpath+"/Muon_QCD.root","btag_two_OneMuon_","QCD","Muon","Two"),   
    }


muon_zero_btag_plots = {
     "nbMuon":("./"+rootpath+"/Muon_Data.root","btag_zero_OneMuon_","Data","Muon","Zero"), 
     "mcb2":("./"+rootpath+"/Muon_WJets"+njet_ext+".root","btag_zero_OneMuon_","WJets","Muon","Zero"),
     "mcb3":("./"+rootpath+"/Muon_TTbar.root","btag_zero_OneMuon_","TTbar","Muon","Zero"),
     "mcb4":("./"+rootpath+"/Muon_Zinv.root","btag_zero_OneMuon_","Zinv","Muon","Zero"),
     "mcb5":("./"+rootpath+"/Muon_DY"+njet_ext+".root","btag_zero_OneMuon_","DY","Muon","Zero"),
     "mcb6":("./"+rootpath+"/Muon_SingleTop.root","btag_zero_OneMuon_","Single_Top","Muon","Zero"),
     "mcb7":("./"+rootpath+"/Muon_DiBoson.root","btag_zero_OneMuon_","Di-Boson","Muon","Zero"),
     #"mcb8":("./"+rootpath+"/Muon_QCD.root","btag_zero_OneMuon_","QCD","Muon","Zero"),
    }


muon_morethanzero_btag_plots = {
     "nbMuon":("./"+rootpath+"/Muon_Data.root","btag_morethanzero_OneMuon_","Data","Muon","Zero"), 
     "mcb2":("./"+rootpath+"/Muon_WJets"+njet_ext+".root","btag_morethanzero_OneMuon_","WJets","Muon","Zero"),
     "mcb3":("./"+rootpath+"/Muon_TTbar.root","btag_morethanzero_OneMuon_","TTbar","Muon","Zero"),
     "mcb4":("./"+rootpath+"/Muon_Zinv.root","btag_morethanzero_OneMuon_","Zinv","Muon","Zero"),
     "mcb5":("./"+rootpath+"/Muon_DY"+njet_ext+".root","btag_morethanzero_OneMuon_","DY","Muon","Zero"),
     "mcb7":("./"+rootpath+"/Muon_DiBoson.root","btag_morethanzero_OneMuon_","Di-Boson","Muon","Zero"),
     #"mcb8":("./"+rootpath+"/Muon_QCD.root","btag_morethanzero_OneMuon_","QCD","Muon","Zero"), 
     "mcb9":("./"+rootpath+"/Muon_SingleTop.root","btag_morethanzero_OneMuon_","Single_Top","Muon","Zero"),
    }


if __name__=="__main__":
  a = Plotter(settings,muon_plots,jet_multiplicity = "True",make_ratio= "True")
  #b = Plotter(settings,muon_morethanzero_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  #c = Plotter(settings,muon_two_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  #d = Plotter(settings,muon_zero_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  #e = Plotter(settings,muon_one_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  
  #settings["Misc"] = ["NoLegend"]
  #settings["Lumo"] = 1.0
  #settings["Plots"] = ["MHT_vs_MET_all","MET_vs_MHTovMET_all"]
  #Plotter(settings,muon_2d_ratios,jet_multiplicity = "True",draw_data="True")
  #settings["Plots"] = ["MET_vs_MHTovMET_all","MHT_vs_MET_all"]#,"MHTovMET_all","MHTovMET_Scaled_all","MET_all","MET_Corrected_all","MHT_all","MHT_FixedThreshold_all","JetMultiplicity_all","HT_all", "JetPt_all","JetEta_all"]
  
  finish = Webpage_Maker(settings["Plots"],settings["WebBinning"],settings["Category"],option=settings["Webpage"])

  try :shutil.rmtree('./Plots')
  except OSError as exc: pass

  print "\n", "*"*52
  print "\tTotal Analysis time: ", time()-baseTime
  print "*"*52
