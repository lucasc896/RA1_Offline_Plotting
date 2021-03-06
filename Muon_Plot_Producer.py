#!/usr/bin/env python
import ROOT as r
import logging,itertools
import os,fnmatch,sys
import glob, errno
from time import strftime, time, sleep
from optparse import OptionParser
import array, ast
import math as m
#from plottingUtils import *
from Btag_8TeV_Plots import *
import shutil
from run_details import this_run

r.gROOT.SetBatch(r.kTRUE)

"""
Input dirs in file
Plots you want to make
Luminosity 
Webbinning - Plots you want displayed on website
Trigger - Trigger efficiencies


Misc - Is just a collection of options I pass sometimes to implement a bunch of hacks, because sometimes people have
come up with annoying little studies and this was the quickest way to implement the information without rewriting the
code. These include Normalising histograms to just compare shapes of distributions etc
"""

baseTime = time()

trigger_effs = {"150_Low": 0.872,"150_High": 0.881,
                "200_Low": 0.875,"200_High": 0.881,
                "275_Low": 0.878,"275_High": 0.882,
                "325_Low": 0.879,"325_High": 0.884,
                "375_Low": 0.881,"375_High": 0.886,
                "475_Low": 0.882,"475_High": 0.888,
                "575_Low": 0.884,"575_High": 0.889,
                "675_Low": 0.885,"675_High": 0.890,
                "775_Low": 0.886,"775_High": 0.891,
                "875_Low": 0.888,"875_High": 0.890,
                "975_Low": 0.887,"975_High": 0.890,
                "1075_Low":0.884,"1075_High":0.896,}

settings = {
  "dirs":["150_200","200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"][4:],
  # "Plots":["MHTovMET_all","MHT_all","MET_all","MET_Corrected_all","AlphaT_all","CommonJetPt_all","HT_all","Number_Btags_all","JetMultiplicity_all","CommonJetEta_all","MuPt_all","MuEta_all","MuPFIso_all","MT_all","Number_Good_verticies_all","LeadJetPt_all","SecondJetPt_all"][:4],
  # "Plots":["ComMinBiasDPhi_all", "ComMinBiasDPhi_acceptedJets_all"],
  "Plots":["LeadJetEta_all"],
  "Lumo" : this_run()["mu_lumi"]*10.,
  "Webpage":"btag",
  "Category":"OneMuon",
  # "WebBinning":["150_200","200_275","275_325","325_375","200_upwards","375_upwards"],
  "WebBinning":["150_200","200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075", "375_upwards", "200_upwards"][4:-1],
  "Misc":[],
  "MHTMET":"False",
  "Trigger":trigger_effs,
  "SITV_plots":[False, True][0]
  }

if settings["SITV_plots"]:
  for p in ['pfCandsPt_all', 'pfCandsDzPV_all', 'pfCandsDunno_all', 'pfCandsCharge_all']:
    settings["Plots"].append(p) 

print ">> Opening directory:", this_run()["path_name"]
sleep(3)

rootpath = "../" + this_run()["path_name"]
njet_ext = ""

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
     # "mc10":("./"+rootpath+"/Muon_SMS.root","OneMuon_","SMS","Muon","Inclusive"),
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
      # "mcb9":("./"+rootpath+"/Muon_SMS.root","btag_one_OneMuon_","SMS","Muon","One"),
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
     # "mcb9":("./"+rootpath+"/Muon_SMS.root","btag_two_OneMuon_","SMS","Muon","Two"),
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
     # "mcb9":("./"+rootpath+"/Muon_SMS.root","btag_zero_OneMuon_","SMS","Muon","Zero"),
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
     # "mcb9":("./"+rootpath+"/Muon_SMS.root","btag_morethanzero_OneMuon_","SMS","Muon","Zero"),
    }


if __name__=="__main__":
  a = Plotter(settings,muon_plots,jet_multiplicity = "True",make_ratio= "True")
  # b = Plotter(settings,muon_morethanzero_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  # c = Plotter(settings,muon_two_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  d = Plotter(settings,muon_zero_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  e = Plotter(settings,muon_one_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  
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
