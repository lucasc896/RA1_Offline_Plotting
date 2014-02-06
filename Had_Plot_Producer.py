#!/usr/bin/env python
from ROOT import *
import ROOT as r
import logging,itertools
import os,fnmatch,sys
import glob, errno
from time import strftime, sleep
from optparse import OptionParser
import array, ast
import math as m
#from plottingUtils import *
from Btag_8TeV_Plots import *
from run_details import this_run


settings = {
  "dirs":["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"],
  "Plots":["MHTovMET_all", "MET_all", "MHTovMET_Full__all","MHT_all","AlphaT_all","JetMultiplicity_all","HT_all","Number_Btags_all","JetPt_all","JetEta_all","Number_verticies_all","Number_Good_verticies_all"],
  "Lumo" : this_run()["had_lumi"]*10.,
  "Webpage":"btag",
  "Category":"Had",
  "WebBinning":["200_275","275_325","325_375","375_upwards","200_upwards"],
  "Misc":[],
  "MHTMET":"True",
  "Trigger":{"175":1.0,"200":0.74,"275":0.85,"325":0.90,"375":0.99,"475":1.0,"575":1.0,"675":1.0,"775":1.0,"875":1.0,"975":1.0,"1075":1.0}
  }

print "\n>> Opening directory:", this_run()["path_name"]
sleep(2)

rootpath = "../" + this_run()["path_name"]
# njet_ext = "_NJet"
njet_ext = ""

muon_plots = {
     "nMuon":("./"+rootpath+"/Had_Data.root","","Data","","Inclusive"), 
     "mc2":("./"+rootpath+"/Had_WJets"+njet_ext+".root","","WJets","","Inclusive"),
     "mc3":("./"+rootpath+"/Had_TTbar.root","","TTbar","","Inclusive"),
     "mc4":("./"+rootpath+"/Had_Zinv.root","","Zinv","","Inclusive"),
     "mc5":("./"+rootpath+"/Had_DY"+njet_ext+".root","","DY","","Inclusive"),
     #"mc7":("./"+rootpath+"/Had_DiBoson.root","","Di-Boson","","Inclusive"),
     #"mc8":("./"+rootpath+"/Had_QCD.root","","QCD","","Inclusive"), 
     "mc9":("./"+rootpath+"/Had_SingleTop.root","","Single_Top","","Inclusive"),
    }

muon_one_btag_plots = {
     "nbMuon":("./"+rootpath+"/Had_Data.root","btag_one_","Data","","One"), 
     "mcb2":("./"+rootpath+"/Had_WJets"+njet_ext+".root","btag_one_","WJets","","One"),
     "mcb3":("./"+rootpath+"/Had_TTbar.root","btag_one_","TTbar","","One"),
     "mcb4":("./"+rootpath+"/Had_Zinv.root","btag_one_","Zinv","","One"),
     "mcb5":("./"+rootpath+"/Had_DY"+njet_ext+".root","btag_one_","DY","","One"),
     "mcb6":("./"+rootpath+"/Had_SingleTop.root","btag_one_","Single_Top","","One"),
     "mcb7":("./"+rootpath+"/Had_DiBoson.root","btag_one_","Di-Boson","","One"),
    # "mcb8":("./"+rootpath+"/Had_QCD.root","btag_one_","QCD","","One"),       
    }


muon_two_btag_plots = {
     "nbMuon":("./"+rootpath+"/Had_Data.root","btag_two_","Data","","Two"), 
     "mcb2":("./"+rootpath+"/Had_WJets"+njet_ext+".root","btag_two_","WJets","","Two"),
     "mcb3":("./"+rootpath+"/Had_TTbar.root","btag_two_","TTbar","","Two"),
     "mcb4":("./"+rootpath+"/Had_Zinv.root","btag_two_","Zinv","","Two"),
     "mcb5":("./"+rootpath+"/Had_DY"+njet_ext+".root","btag_two_","DY","","Two"),
     "mcb6":("./"+rootpath+"/Had_SingleTop.root","btag_two_","Single_Top","","Two"),
     "mcb7":("./"+rootpath+"/Had_DiBoson.root","btag_two_","Di-Boson","","Two"), 
     #"mcb8":("./"+rootpath+"/Had_QCD.root","btag_two_","QCD","","Two"),   
    }


muon_zero_btag_plots = {
     "nbMuon":("./"+rootpath+"/Had_Data.root","btag_zero_","Data","","Zero"), 
     "mcb2":("./"+rootpath+"/Had_WJets"+njet_ext+".root","btag_zero_","WJets","","Zero"),
     "mcb3":("./"+rootpath+"/Had_TTbar.root","btag_zero_","TTbar","","Zero"),
     "mcb4":("./"+rootpath+"/Had_Zinv.root","btag_zero_","Zinv","","Zero"),
     "mcb5":("./"+rootpath+"/Had_DY"+njet_ext+".root","btag_zero_","DY","","Zero"),
     "mcb6":("./"+rootpath+"/Had_SingleTop.root","btag_zero_","Single_Top","","Zero"),
     "mcb7":("./"+rootpath+"/Had_DiBoson.root","btag_zero_","Di-Boson","","Zero"),
     #"mcb8":("./"+rootpath+"/Had_QCD.root","btag_zero_","QCD","","Zero"),     
    }


muon_morethanzero_btag_plots = {
     "nbMuon":("./"+rootpath+"/Had_Data.root","btag_morethanzero_","Data","","Zero"), 
     "mcb2":("./"+rootpath+"/Had_WJets"+njet_ext+".root","btag_morethanzero_","WJets","","Zero"),
     "mcb3":("./"+rootpath+"/Had_TTbar.root","btag_morethanzero_","TTbar","","Zero"),
     "mcb4":("./"+rootpath+"/Had_Zinv.root","btag_morethanzero_","Zinv","","Zero"),
     "mcb5":("./"+rootpath+"/Had_DY"+njet_ext+".root","btag_morethanzero_","DY","","Zero"),
     "mcb7":("./"+rootpath+"/Had_DiBoson.root","btag_morethanzero_","Di-Boson","","Zero"),
     #"mcb8":("./"+rootpath+"/Had_QCD.root","btag_morethanzero_","QCD","","Zero"), 
     "mcb9":("./"+rootpath+"/Had_SingleTop.root","btag_morethanzero_","Single_Top","","Zero"),
    }

if __name__=="__main__":
  a = Plotter(settings,muon_plots,jet_multiplicity = "True",make_ratio= "True")
  b = Plotter(settings,muon_morethanzero_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  c = Plotter(settings,muon_two_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  d = Plotter(settings,muon_zero_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  e = Plotter(settings,muon_one_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  finish = Webpage_Maker(settings["Plots"],settings["WebBinning"],settings["Category"],option=settings["Webpage"])
