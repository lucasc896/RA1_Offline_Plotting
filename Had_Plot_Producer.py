#!/usr/bin/env python
import ROOT as r
import logging,itertools
import os,fnmatch,sys
import glob, errno
import shutil
from time import strftime, sleep
from optparse import OptionParser
import array, ast
import math as m
#from plottingUtils import *
from Btag_8TeV_Plots import *
from run_details import this_run

r.gROOT.SetBatch(r.kTRUE)

trigger_effs = {"200_Low":0.818,"200_High":0.789,"200_5":0.32,
                "275_Low":0.952,"275_High":0.900,"275_5":0.39,
                "325_Low":0.978,"325_High":0.959,"325_5":0.96,
                "375_Low":0.992,"375_High":0.987,"375_5":0.97,
                "475_Low":0.998,"475_High":0.996, "475_5":0.96,
                "575_Low":1.,"575_High":1.,"575_5":1.,
                "675_Low":1.,"675_High":1.,"675_5":1.,
                "775_Low":1.,"775_High":1.,"775_5":1.,
                "875_Low":1.,"875_High":1.,"875_5":1.,
                "975_Low":1.,"975_High":1.,"975_5":1.,
                "1075_Low":1.,"1075_High":1.,"1075_5":1.,}

settings = {
  "dirs":["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"],
  # "Plots":["MHTovMET_all", "MET_all","MHT_all","AlphaT_all","JetMultiplicity_all","HT_all","Number_Btags_all","CommonJetPt_all","CommonJetEta_all","Number_Good_verticies_all","LeadJetPt_all","SecondJetPt_all",][1:3],
  "Plots":["AlphaT_all", "HT_all", "ComMinBiasDPhi_acceptedJets_all", "ComMinBiasDPhi_all", "MET_all","MHT_all","LeadJetEta_all", "Number_Good_verticies_all"][:1],
  # "Plots":["HT_all",],
  "Lumo" : this_run()["had_lumi"]*10.,
  "Webpage":"btag",
  "Category":"Had",
  # "WebBinning":["200_275","275_325","325_375","375_475","375_upwards","200_upwards"][-2:-1],
  "WebBinning":["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075", "375_upwards", "200_upwards"][-2:-1],
  "Misc":[],
  "MHTMET":"True",
  "Trigger":trigger_effs,
  "SITV_plots":[False, True][0],
  "SMS_plots":[False, True][0],
  }

data_run_suf = ["", "_2012A", "_2012B", "_2012C", "_2012D", "_2012ABC", "_2012BC"][0]

if settings["SITV_plots"]:
  for p in ['pfCandsPt_0', 'pfCandsDzPV_0', 'pfCandsDunno_0', 'pfCandsCharge_0']:
    settings["Plots"].append(p)

print "\n>> Opening directory:", this_run()["path_name"]
sleep(2)

rootpath = "../" + this_run()["path_name"]
# njet_ext = "_NJet"
njet_ext = ""

muon_plots = {
     "nMuon":("./"+rootpath+"/Had_Data%s.root" % data_run_suf,"","Data","","Inclusive"), 
     "mc2":("./"+rootpath+"/Had_WJets"+njet_ext+".root","","WJets","","Inclusive"),
     "mc3":("./"+rootpath+"/Had_TTbar.root","","TTbar","","Inclusive"),
     "mc4":("./"+rootpath+"/Had_Zinv.root","","Zinv","","Inclusive"),
     "mc5":("./"+rootpath+"/Had_DY"+njet_ext+".root","","DY","","Inclusive"),
     "mc7":("./"+rootpath+"/Had_DiBoson.root","","Di-Boson","","Inclusive"),
     "mc8":("./"+rootpath+"/Had_QCD.root","","QCD","","Inclusive"), 
     "mc9":("./"+rootpath+"/Had_SingleTop.root","","Single_Top","","Inclusive"),
     # "mc10":("./"+rootpath+"/Had_SMS.root","","SMS","","Inclusive"),
    }

muon_one_btag_plots = {
     "nbMuon":("./"+rootpath+"/Had_Data%s.root" % data_run_suf,"btag_one_","Data","","One"), 
     "mcb2":("./"+rootpath+"/Had_WJets"+njet_ext+".root","btag_one_","WJets","","One"),
     "mcb3":("./"+rootpath+"/Had_TTbar.root","btag_one_","TTbar","","One"),
     "mcb4":("./"+rootpath+"/Had_Zinv.root","btag_one_","Zinv","","One"),
     "mcb5":("./"+rootpath+"/Had_DY"+njet_ext+".root","btag_one_","DY","","One"),
     "mcb6":("./"+rootpath+"/Had_SingleTop.root","btag_one_","Single_Top","","One"),
     "mcb7":("./"+rootpath+"/Had_DiBoson.root","btag_one_","Di-Boson","","One"),
    "mcb8":("./"+rootpath+"/Had_QCD.root","btag_one_","QCD","","One"),       
      # "mcb10":("./"+rootpath+"/Had_SMS.root","btag_one_","SMS","","One"),
    }


muon_two_btag_plots = {
     "nbMuon":("./"+rootpath+"/Had_Data%s.root" % data_run_suf,"btag_two_","Data","","Two"), 
     "mcb2":("./"+rootpath+"/Had_WJets"+njet_ext+".root","btag_two_","WJets","","Two"),
     "mcb3":("./"+rootpath+"/Had_TTbar.root","btag_two_","TTbar","","Two"),
     "mcb4":("./"+rootpath+"/Had_Zinv.root","btag_two_","Zinv","","Two"),
     "mcb5":("./"+rootpath+"/Had_DY"+njet_ext+".root","btag_two_","DY","","Two"),
     "mcb6":("./"+rootpath+"/Had_SingleTop.root","btag_two_","Single_Top","","Two"),
     "mcb7":("./"+rootpath+"/Had_DiBoson.root","btag_two_","Di-Boson","","Two"), 
     "mcb8":("./"+rootpath+"/Had_QCD.root","btag_two_","QCD","","Two"),
     # "mcb10":("./"+rootpath+"/Had_SMS.root","btag_two_","SMS","","Two"),
    }


muon_zero_btag_plots = {
     "nbMuon":("./"+rootpath+"/Had_Data%s.root" % data_run_suf,"btag_zero_","Data","","Zero"), 
     "mcb2":("./"+rootpath+"/Had_WJets"+njet_ext+".root","btag_zero_","WJets","","Zero"),
     "mcb3":("./"+rootpath+"/Had_TTbar.root","btag_zero_","TTbar","","Zero"),
     "mcb4":("./"+rootpath+"/Had_Zinv.root","btag_zero_","Zinv","","Zero"),
     "mcb5":("./"+rootpath+"/Had_DY"+njet_ext+".root","btag_zero_","DY","","Zero"),
     "mcb6":("./"+rootpath+"/Had_SingleTop.root","btag_zero_","Single_Top","","Zero"),
     "mcb7":("./"+rootpath+"/Had_DiBoson.root","btag_zero_","Di-Boson","","Zero"),
     "mcb8":("./"+rootpath+"/Had_QCD.root","btag_zero_","QCD","","Zero"),     
      # "mcb10":("./"+rootpath+"/Had_SMS.root","btag_zero_","SMS","","Zero"),
    }


muon_morethanzero_btag_plots = {
     "nbMuon":("./"+rootpath+"/Had_Data%s.root" % data_run_suf,"btag_morethanzero_","Data","","Zero"), 
     "mcb2":("./"+rootpath+"/Had_WJets"+njet_ext+".root","btag_morethanzero_","WJets","","Zero"),
     "mcb3":("./"+rootpath+"/Had_TTbar.root","btag_morethanzero_","TTbar","","Zero"),
     "mcb4":("./"+rootpath+"/Had_Zinv.root","btag_morethanzero_","Zinv","","Zero"),
     "mcb5":("./"+rootpath+"/Had_DY"+njet_ext+".root","btag_morethanzero_","DY","","Zero"),
     "mcb7":("./"+rootpath+"/Had_DiBoson.root","btag_morethanzero_","Di-Boson","","Zero"),
     "mcb8":("./"+rootpath+"/Had_QCD.root","btag_morethanzero_","QCD","","Zero"), 
     "mcb9":("./"+rootpath+"/Had_SingleTop.root","btag_morethanzero_","Single_Top","","Zero"),
     # "mcb10":("./"+rootpath+"/Had_SMS.root","btag_morethanzero_","SMS","","Zero"),
    }


if __name__=="__main__":

  if settings["SMS_plots"]:
    for this_dict in [muon_plots, muon_one_btag_plots, muon_two_btag_plots, muon_zero_btag_plots, muon_morethanzero_btag_plots]:
      poppers = []
      for key in this_dict:
        if "n" in key: continue
        if "SMS" not in this_dict[key][0]:
          poppers.append(key)
      for p in poppers:
        this_dict.pop(p)
        
  a = Plotter(settings,muon_plots,jet_multiplicity = "True",make_ratio= "True")
  # b = Plotter(settings,muon_morethanzero_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  # c = Plotter(settings,muon_two_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  # d = Plotter(settings,muon_zero_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  # e = Plotter(settings,muon_one_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  finish = Webpage_Maker(settings["Plots"],settings["WebBinning"],settings["Category"],option=settings["Webpage"], bg_predict=True)

  # try :shutil.rmtree('./Plots')
  # except OSError as exc: pass
