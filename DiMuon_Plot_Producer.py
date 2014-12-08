#!/usr/bin/env python
import ROOT as r
import logging,itertools
import os,fnmatch,sys
import glob, errno
from time import strftime, sleep
from optparse import OptionParser
import array, ast
import math as m
from Btag_8TeV_Plots import *
import shutil
from run_details import this_run


trigger_effs =  {"150_Low": 0.984,"150_High": 0.984,
                  "200_Low": 0.985,"200_High": 0.984,
                  "275_Low": 0.985,"275_High": 0.984,
                  "325_Low": 0.986,"325_High": 0.986,
                  "375_Low": 0.986,"375_High": 0.985,
                  "475_Low": 0.986,"475_High": 0.986,
                  "575_Low": 0.986,"575_High": 0.986,
                  "675_Low": 0.987,"675_High": 0.986,
                  "775_Low": 0.986,"775_High": 0.986,
                  "875_Low": 0.987,"875_High": 0.986,
                  "975_Low": 0.987,"975_High": 0.988,
                  "1075_Low":0.987,"1075_High":0.987,}

settings = {
  "dirs":["150_200","200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"][4:],
  # "Plots":["MHTovMET_all","MET_Corrected_all", "MET_all", "MHT_all","HT_all","DiMuon_Mass_all", "AlphaT_all","JetMultiplicity_all","Number_Btags_all","CommonJetPt_all","CommonJetEta_all","MuPt_all","MuEta_all","SecondMuPt_all","SecondMuEta_all","MuPFIso_all","Number_Good_verticies_all","LeadJetPt_all","SecondJetPt_all"][1:2],
  "Plots":["ComMinBiasDPhi_all", "ComMinBiasDPhi_acceptedJets_all"],
  "Lumo" : this_run()["mu_lumi"]*10.,
  "Webpage":"btag",
  "Category":"DiMuon",
  "WebBinning":["150_200","200_275","275_325","325_375","200_upwards","375_upwards"][-1:],
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
"""
rootpath = "NewConfig_RootFiles"
njet_ext = "_NJet"
"""
# dimuon_2d = {
#      "nMuon":("./"+rootpath+"/Muon_EWK"+njet_ext+".root","DiMuon_","Data","Muon","Inclusive"), 
#      "mc2":("./"+rootpath+"/Muon_EWK"+njet_ext+".root","DiMuon_","SMS","Muon","Inclusive"),
#     }
# dimuon_2d_data = {
#      "nMuon":("./"+rootpath+"/Muon_Data.root","DiMuon_","Data","Muon","Inclusive"), 
#     }

muon_plots = {
     "nMuon":("./"+rootpath+"/Muon_Data.root","DiMuon_","Data","Muon","Inclusive"), 
     "mc2":("./"+rootpath+"/Muon_WJets"+njet_ext+".root","DiMuon_","WJets","Muon","Inclusive"),
     "mc3":("./"+rootpath+"/Muon_TTbar.root","DiMuon_","TTbar","Muon","Inclusive"),
     "mc4":("./"+rootpath+"/Muon_Zinv.root","DiMuon_","Zinv","Muon","Inclusive"),
     "mc5":("./"+rootpath+"/Muon_DY"+njet_ext+".root","DiMuon_","DY","Muon","Inclusive"),
     "mc7":("./"+rootpath+"/Muon_DiBoson.root","DiMuon_","Di-Boson","Muon","Inclusive"),
     # "mc8":("./"+rootpath+"/Muon_QCD.root","DiMuon_","QCD","Muon","Inclusive"), 
     "mc9":("./"+rootpath+"/Muon_SingleTop.root","DiMuon_","Single_Top","Muon","Inclusive"),
     # "mc10":("./"+rootpath+"/Muon_SMS.root","DMuon_","SMS","Muon","Inclusive"),
    }

muon_one_btag_plots = {
     "nbMuon":("./"+rootpath+"/Muon_Data.root","btag_one_DiMuon_","Data","Muon","One"), 
     "mcb2":("./"+rootpath+"/Muon_WJets"+njet_ext+".root","btag_one_DiMuon_","WJets","Muon","One"),
     "mcb3":("./"+rootpath+"/Muon_TTbar.root","btag_one_DiMuon_","TTbar","Muon","One"),
     "mcb4":("./"+rootpath+"/Muon_Zinv.root","btag_one_DiMuon_","Zinv","Muon","One"),
     "mcb5":("./"+rootpath+"/Muon_DY"+njet_ext+".root","btag_one_DiMuon_","DY","Muon","One"),
     "mcb6":("./"+rootpath+"/Muon_SingleTop.root","btag_one_DiMuon_","Single_Top","Muon","One"),
     "mcb7":("./"+rootpath+"/Muon_DiBoson.root","btag_one_DiMuon_","Di-Boson","Muon","One"),
     # "mcb9":("./"+rootpath+"/Muon_SMS.root","btag_one_DiMuon_","SMS","Muon","One"),
    }

muon_two_btag_plots = {

     "nbMuon":("./"+rootpath+"/Muon_Data.root","btag_two_DiMuon_","Data","Muon","Two"), 
     "mcb2":("./"+rootpath+"/Muon_WJets"+njet_ext+".root","btag_two_DiMuon_","WJets","Muon","Two"),
     "mcb3":("./"+rootpath+"/Muon_TTbar.root","btag_two_DiMuon_","TTbar","Muon","Two"),
     "mcb4":("./"+rootpath+"/Muon_Zinv.root","btag_two_DiMuon_","Zinv","Muon","Two"),
     "mcb5":("./"+rootpath+"/Muon_DY"+njet_ext+".root","btag_two_DiMuon_","DY","Muon","Two"),
     "mcb6":("./"+rootpath+"/Muon_SingleTop.root","btag_two_DiMuon_","Single_Top","Muon","Two"),
     "mcb7":("./"+rootpath+"/Muon_DiBoson.root","btag_two_DiMuon_","Di-Boson","Muon","Two"), 
     # "mcb9":("./"+rootpath+"/Muon_SMS.root","btag_two_DiMuon_","SMS","Muon","Two"),
    }

muon_zero_btag_plots = {
     "nbMuon":("./"+rootpath+"/Muon_Data.root","btag_zero_DiMuon_","Data","Muon","Zero"), 
     "mcb2":("./"+rootpath+"/Muon_WJets"+njet_ext+".root","btag_zero_DiMuon_","WJets","Muon","Zero"),
     "mcb3":("./"+rootpath+"/Muon_TTbar.root","btag_zero_DiMuon_","TTbar","Muon","Zero"),
     "mcb4":("./"+rootpath+"/Muon_Zinv.root","btag_zero_DiMuon_","Zinv","Muon","Zero"),
     "mcb5":("./"+rootpath+"/Muon_DY"+njet_ext+".root","btag_zero_DiMuon_","DY","Muon","Zero"),
     "mcb6":("./"+rootpath+"/Muon_SingleTop.root","btag_zero_DiMuon_","Single_Top","Muon","Zero"),
     "mcb7":("./"+rootpath+"/Muon_DiBoson.root","btag_zero_DiMuon_","Di-Boson","Muon","Zero"),
     # "mcb9":("./"+rootpath+"/Muon_SMS.root","btag_zero_DiMuon_","SMS","Muon","Zero"),
    }

muon_morethanzero_btag_plots = {
     "nbMuon":("./"+rootpath+"/Muon_Data.root","btag_morethanzero_DiMuon_","Data","Muon","Zero"), 
     "mcb2":("./"+rootpath+"/Muon_WJets"+njet_ext+".root","btag_morethanzero_DiMuon_","WJets","Muon","Zero"),
     "mcb3":("./"+rootpath+"/Muon_TTbar.root","btag_morethanzero_DiMuon_","TTbar","Muon","Zero"),
     "mcb4":("./"+rootpath+"/Muon_Zinv.root","btag_morethanzero_DiMuon_","Zinv","Muon","Zero"),
     "mcb5":("./"+rootpath+"/Muon_DY"+njet_ext+".root","btag_morethanzero_DiMuon_","DY","Muon","Zero"),
     "mcb7":("./"+rootpath+"/Muon_DiBoson.root","btag_morethanzero_DiMuon_","Di-Boson","Muon","Zero"),
     "mcb9":("./"+rootpath+"/Muon_SingleTop.root","btag_morethanzero_DiMuon_","Single_Top","Muon","Zero"),
     # "mcb9":("./"+rootpath+"/Muon_SMS.root","btag_morethanzero_DiMuon_","SMS","Muon","Zero"),
    }

if __name__=="__main__":
  a = Plotter(settings,muon_plots,jet_multiplicity = "True",make_ratio= "True")
  # b = Plotter(settings,muon_morethanzero_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  # c = Plotter(settings,muon_two_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  d = Plotter(settings,muon_zero_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  e = Plotter(settings,muon_one_btag_plots,jet_multiplicity = "True",make_ratio= "True")

  finish = Webpage_Maker(settings["Plots"],settings["WebBinning"],settings["Category"],option=settings["Webpage"])

  try :shutil.rmtree('./Plots')
  except OSError as exc: pass
