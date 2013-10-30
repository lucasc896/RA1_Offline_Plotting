#!/usr/bin/env python
from ROOT import *
import ROOT as r
import array


def normalise_plot(plot):

  int = plot.Integral()
  for xbin in range(1,plot.GetNbinsX()+1):
    for ybin in range(1,plot.GetNbinsY()+1):
        plot.SetBinContent(xbin,ybin,plot.GetBinContent(xbin,ybin)/int) 

  return plot

def make_ratio(data,mc):

  ratio_plot = data.Clone()
  for xbin in range(1,data.GetNbinsX()+1):
    for ybin in range(1,data.GetNbinsY()+1):
       #print data.GetBinContent(xbin,ybin), mc.GetBinContent(xbin,ybin)
       try :ratio_plot.SetBinContent(xbin,ybin,data.GetBinContent(xbin,ybin)/mc.GetBinContent(xbin,ybin))
       except ZeroDivisionError : ratio_plot.SetBinContent(xbin,ybin,0)

  return ratio_plot     


hists = ["MET_vs_MHTovMET_","MHT_vs_MET_"]

jetmult = ["2","3","all"]

dirs = ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"]

prefix = "OneMuon_"
EWK = ["./Oct_11_MHTMET/Muon_EWK.root"][0]
Data = ["./Oct_11_MHTMET/Muon_Data.root"][0]


file = r.TFile("./MHTMET_ratio.root","RECREATE")

for dir in dirs:
  file.cd("/")
  file.mkdir(prefix+str(dir))


mc_model = r.TFile.Open("./"+EWK)
data_model = r.TFile.Open("./"+Data)

for dir in dirs:

  file.cd(prefix+dir)
  for plot in hists: 
     for jet in jetmult:
         mc_plot = mc_model.Get(prefix+dir+"/"+plot+jet)
         data_plot = data_model.Get(prefix+dir+"/"+plot+jet)
        
         if plot == "MET_vs_MHTovMET_":
            mc_plot.RebinX(10)
            data_plot.RebinX(10)
            mc_plot.RebinY(1)
            data_plot.RebinY(1)

         if plot == "MHT_vs_MET_":
            mc_plot.RebinY(10)
            mc_plot.RebinX(10)
            data_plot.RebinY(10)
            data_plot.RebinX(10)

         normalise_plot(mc_plot)
         normalise_plot(data_plot)

         final_ratio = make_ratio(data_plot,mc_plot)
         final_ratio.Write("",r.TObject.kOverwrite)
         #print final_ratio
  file.cd("../")        

file.Close()

