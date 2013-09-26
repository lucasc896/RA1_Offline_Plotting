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
from Btag_8TeV_Plots import *

settings = {
  "dirs":["150_200","200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"],
  "Plots":["MHTovMET_all","DiMuon_Mass_all", "MHT_all","AlphaT_all","JetMultiplicity_all","HT_all","Number_Btags_all","JetPt_all","JetEta_all","MuPt_all","MuEta_all","MuPFIso_all","Number_Good_verticies_all"],
  "Lumo" : 192.55,
  "Webpage":"btag",
  "Category":"DiMuon",
  "WebBinning":["200_upwards","375_upwards"],
  "Misc":[],
  "MHTMET":"True",
  "Trigger":{"150":0.95,"200":0.95,"275":0.96,"325":0.96,"375":0.96,"475":0.96,"575":0.97,"675":0.97,"775":0.98,"875":0.98,"975":0.98,"1075":0.98}
  }

muon_plots = {
     "nMuon":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data.root","DiMuon_","Data","Muon","Inclusive"), 
     #"mc1":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_MC.root","DiMuon_","MC Combined","Muon","Inclusive"),
     "mc2":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets.root","DiMuon_","WJets","Muon","Inclusive"),
     "mc3":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar.root","DiMuon_","TTbar","Muon","Inclusive"),
     "mc4":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv.root","DiMuon_","Zinv","Muon","Inclusive"),
     "mc5":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY.root","DiMuon_","DY","Muon","Inclusive"),
     "mc7":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson.root","DiMuon_","Di-Boson","Muon","Inclusive"),
     #"mc8":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_QCD.root","DiMuon_","QCD","Muon","Inclusive"), 
     "mc9":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop.root","DiMuon_","Single_Top","Muon","Inclusive"),

    }

muon_one_btag_plots = {
     "nbMuon":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data.root","btag_one_DiMuon_","Data","Muon","One"), 
     #"mcb1":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_MC.root","btag_one_DiMuon_","MC Combined","Muon","One"),
     "mcb2":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets.root","btag_one_DiMuon_","WJets","Muon","One"),
     "mcb3":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar.root","btag_one_DiMuon_","TTbar","Muon","One"),
     "mcb4":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv.root","btag_one_DiMuon_","Zinv","Muon","One"),
     "mcb5":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY.root","btag_one_DiMuon_","DY","Muon","One"),
     "mcb6":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop.root","btag_one_DiMuon_","Single_Top","Muon","One"),
     "mcb7":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson.root","btag_one_DiMuon_","Di-Boson","Muon","One"),
        
    }


muon_two_btag_plots = {
     "nbMuon":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data.root","btag_two_DiMuon_","Data","Muon","Two"), 
     #"mcb1":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_MC.root","btag_two_DiMuon_","MC Combined","Muon","Two"),
     "mcb2":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets.root","btag_two_DiMuon_","WJets","Muon","Two"),
     "mcb3":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar.root","btag_two_DiMuon_","TTbar","Muon","Two"),
     "mcb4":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv.root","btag_two_DiMuon_","Zinv","Muon","Two"),
     "mcb5":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY.root","btag_two_DiMuon_","DY","Muon","Two"),
     "mcb6":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop.root","btag_two_DiMuon_","Single_Top","Muon","Two"),
     "mcb7":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson.root","btag_two_DiMuon_","Di-Boson","Muon","Two"), 
    }

muon_zero_btag_plots = {
     "nbMuon":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data.root","btag_zero_DiMuon_","Data","Muon","Zero"), 
     #"mcb1":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_MC.root","btag_zero_DiMuon_","MC Combined","Muon","Zero"),
     "mcb2":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets.root","btag_zero_DiMuon_","WJets","Muon","Zero"),
     "mcb3":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar.root","btag_zero_DiMuon_","TTbar","Muon","Zero"),
     "mcb4":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv.root","btag_zero_DiMuon_","Zinv","Muon","Zero"),
     "mcb5":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY.root","btag_zero_DiMuon_","DY","Muon","Zero"),
     "mcb6":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop.root","btag_zero_DiMuon_","Single_Top","Muon","Zero"),
     "mcb7":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson.root","btag_zero_DiMuon_","Di-Boson","Muon","Zero"),
        
    }

muon_morethanzero_btag_plots = {
     "nbMuon":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data.root","btag_morethanzero_DiMuon_","Data","Muon","Zero"), 
     #"mcb1":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_MC.root","btag_morethanzero_DiMuon_","MC Combined","Muon","Zero"),
     "mcb2":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets.root","btag_morethanzero_DiMuon_","WJets","Muon","Zero"),
     "mcb3":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar.root","btag_morethanzero_DiMuon_","TTbar","Muon","Zero"),
     "mcb4":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv.root","btag_morethanzero_DiMuon_","Zinv","Muon","Zero"),
     "mcb5":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY.root","btag_morethanzero_DiMuon_","DY","Muon","Zero"),
     "mcb7":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson.root","btag_morethanzero_DiMuon_","Di-Boson","Muon","Zero"),
     "mcb9":("./MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop.root","btag_morethanzero_DiMuon_","Single_Top","Muon","Zero"),
    }

if __name__=="__main__":
  a = Plotter(settings,muon_plots,jet_multiplicity = "True",make_ratio= "True")
  b = Plotter(settings,muon_morethanzero_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  c = Plotter(settings,muon_two_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  d = Plotter(settings,muon_zero_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  e = Plotter(settings,muon_one_btag_plots,jet_multiplicity = "True",make_ratio= "True")
  finish = Webpage_Maker(settings["Plots"],settings["WebBinning"],settings["Category"],option=settings["Webpage"])
