#!/usr/bin/env python
import ROOT as r
import logging,itertools
import os,fnmatch,sys
import glob, errno
from time import strftime, time
from optparse import OptionParser
import array
import math as m
from array import array
from run_details import this_run
from sys import exit

r.gROOT.SetBatch(r.kTRUE)

class Plotter(object):

  def __init__(self,settings,sample_list,jet_multiplicity = "",make_ratio = "False",draw_data = "True"):
    #================================== Preamble
    self.baseTime = time()
    print " Selecting tdr style"
    r.gROOT.ProcessLine(".L tdrstyle.C")
    r.setstyle()
    r.gROOT.SetBatch(True)
    r.gStyle.SetOptStat(0)
    r.gStyle.SetPaintTextFormat("5.2f")

    #==================================
    self.settings = settings
    if "Profile" in self.settings["Misc"]: r.gStyle.SetOptStat(1)
    self.jet_multi = jet_multiplicity
    self.DoRatios = make_ratio
    self.Draw_Data = draw_data
    self.sample_list = sample_list
    self.MHTMETcorrections = settings["MHTMET"]
    print "DoRatio : %s" %self.DoRatios
    self.splash_screen()
    self.jet_cats = settings["jet_categories"]

    """
    Hist getting simply loops through your specified data file and then appends to a list the path
    to the histogram you specified in your settings

    e.g It will append to Path_List,  OneMuon_375_475/Number_Btags_all
    
    We later loop through this list in Plotting_Option and produce all the relevant histograms 
    """
    self.Hist_Getter(settings,sample_list)
    self.Plotting_Option(settings,sample_list)    

  def splash_screen(self):
    print "\n|============================================================================|"
    print "| XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX |"
    print "|==================  STARTING  BINNED ALPHA T PLOTTING ======================|"
    print "| XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX |"
    print "|============================================================================|"

  def ensure_dir(self,dir):
    try:
      os.makedirs(dir)
    except OSError as exc:
      pass

  def Hist_Getter(self,settings,sample_list):
    for key,sample in sorted(sample_list.iteritems()):
      if "n" == key[0]:
        self.DATA_FILE = sample[0]
        self.Directory_Name = sample[1]
        temp =  r.TFile.Open(self.DATA_FILE)
        DirKeys = temp.GetListOfKeys()
        self.Path_List =[]
        self.Hist_List = []
        for key in DirKeys:
          subdirect = temp.FindObjectAny(key.GetName())
          for bin in settings["dirs"]:
            dir = sample[1]+bin
            if dir ==  subdirect.GetName():
              for subkey in subdirect.GetListOfKeys() :
                if subkey.GetName() in settings["Plots"]:
                  if self.jet_multi == "True":
                    base = subkey.GetName().strip('all')
                    for entry in self.jet_cats:
                      self.Path_List.append("%s/%s" % (subdirect.GetName(),base+entry))
                      self.Hist_List.append(base+entry)
                  else: 
                    self.Path_List.append("%s/%s" % (subdirect.GetName(),subkey.GetName()))
                    self.Hist_List.append(subkey.GetName())
        temp.Close()
  
  def Directory_Maker(self):
    htBins = self.settings["dirs"]
    self.Dir_Binning = []
    print "\n Making Directory ::: Plots :::" 
    self.ensure_dir("Plots")
    self.base = os.getcwd()
    os.chdir("Plots")
    owd = os.getcwd()
    for bin in htBins: self.Dir_Binning.append(bin)
    for path in self.Dir_Binning: 
      self.ensure_dir(path)
      os.chdir(path)
      for h in self.Hist_List: self.ensure_dir(str(h))
      os.chdir(owd)


  """
  We loop through Path_List which contains the path to every histogram we want to make.
  If this path is then within our Webbinning folder, eg. ones we want to show on the website we then pass this onto MakePlots
  """
  def Plotting_Option(self,settings,sample_list):
        self.Directory_Maker()
        for num,histpath in enumerate(self.Path_List):
          name = self.Hist_List[num]
          ht = (histpath.split('/')[0])[len(self.Directory_Name):]
          if ht in settings["WebBinning"] : self.Make_Plots(ht,name,histpath)

          # These two plots here are when we want to make combined HT bins plots 375,200 upwards. the split is to strip the
          # 375_475 from the hist name. I seem to have some problems if I used the .strip method hence why it looks a bit
          # weird with the -7 there.
          if ht in ["375_475"]: self.Make_Plots(ht,name,histpath,combine = "True",histpath= (histpath.split('/')[0][:-7]))
          if ht in ["200_275"]: self.Make_Plots(ht,name,histpath,combine = "True",histpath= (histpath.split('/')[0][:-7]))

        os.chdir(self.base)
 
  def MakePad(self,plot):
      if type(plot) != type(r.TH2D()):
        # Make 2 pads for the Data/MC ratio plot fit.
          self.up = r.TPad("u","u",0.01,0.25,0.99,0.99)
          self.dp = r.TPad("d","d",0.01,0.01,0.99,0.25)
          self.up.SetNumber(1)
          self.dp.SetNumber(2)
          self.up.Draw()
          self.dp.Draw()

  """
  This is used if we want to make the Data/MC ratio plots below the histograms. If make_ratio = false this is not used
  """
  
  def MakeMCRatio(self,histname,data,mc):
        if type(data) != type(r.TH2D()):
          self.c1.cd(2)
          self.ratio = data.Clone()
          #self.ratio.Add(mc,-1)
          self.ratio.Divide(mc)
          self.ratio.GetYaxis().SetRangeUser(0.5,1.5)
          self.ratio.GetYaxis().SetTitle("Data/MC")
          self.ratio.GetYaxis().SetTitleOffset(0.5)
          self.ratio.GetYaxis().SetLabelSize(0.11)
          self.ratio.GetYaxis().SetNdivisions(505)
          self.ratio.GetXaxis().SetTitle("")
          self.ratio.GetXaxis().SetLabelSize(0.12)
          self.ratio.SetTitleSize(0.1,"Y")
          for i in range(0,self.ratio.GetNbinsX()):
              try:self.ratio.SetBinError(i+1,self.ratio.GetBinContent(i+1)*(data.GetBinError(i+1)/data.GetBinContent(i+1)))
              except ZeroDivisionError: self.ratio.SetBinError(i+1,0)
          self.ratio = self.Hist_Options(histname,self.ratio,norebin=True)
          if self.max_min[1] != 0: 
            self.lv = r.TLine(self.max_min[0],1,self.max_min[1],1)
            fit = r.TF1("fit","pol0", self.max_min[0], self.max_min[1])
          else:
            fit = r.TF1("fit","pol0", data.GetXaxis().GetBinLowEdge(1), data.GetXaxis().GetBinUpEdge(data.GetNbinsX()))
            self.lv = r.TLine(data.GetXaxis().GetBinLowEdge(1),1,data.GetXaxis().GetBinUpEdge(data.GetNbinsX()),1)
          error_changer = self.ratio.Clone()
          for i in range(0,error_changer.GetNbinsX()):
            error_changer.SetBinContent(i,1)
            try: error_changer.SetBinError(i+1,mc.GetBinError(i+1)/mc.GetBinContent(i+1))
            except ZeroDivisionError: error_changer.SetBinError(i+1,0)
          r.gStyle.SetOptFit(1)
          self.ratio_error = r.TGraphErrors(error_changer)
          self.ratio.Fit(fit)
          self.ratio_error.SetFillStyle(3244)
          self.ratio_error.SetFillColor(17)
          #self.bv.SetFillColor(39)
          #self.bv.SetFillStyle(3002)
          self.lv.SetLineWidth(3)
          self.ratio.Draw("p")
          self.ratio_error.Draw("SAME2")
          #self.bv.Draw("SAME")
          self.lv.Draw("SAME")
          self.ratio.Draw("PSAME")

         
  def Poission(self,plot):
    poisson_eh = [ 1.15, 1.36, 1.53, 1.73, 1.98, 2.21, 2.42, 2.61, 2.80, 3.00, 3.16 ]
    poisson_el = [ 0.00, 1.00, 2.00, 2.14, 2.30, 2.49, 2.68, 2.86, 3.03, 3.19, 3.16 ]

    for i in range(1,plot.GetNbinsX()):
      x = plot.GetBinContent(i)
      if x<10:
        n = int(x)
        plot.SetBinError(i,poisson_el[n])
    return plot 

  def Make_Plots(self,htbin,histname,rootpath,combine = "",histpath=""):

      """ 
      This is where the plot is made.
      Initially we open the data file only.
      Any options are added in Hist_Options  
      The same is then done for all MC files in MC_Draw
      A bunch of other lists are filled for producing different stacked, simplified plots and also drawing on the Total EWK band


      """
      print "At Histogram %s %s" %(rootpath,histname)
      self.DataFile =  r.TFile.Open("../%s" %self.DATA_FILE)
      self.Plot_Closer = [self.DataFile]
      plot  = self.DataFile.Get("%s" %rootpath)
      self.c1 = r.TCanvas("canvas"+str(rootpath),"canname"+str(histname),1200,1000)
      
      if combine == "True":
        #If we are producing _upwards plots we Add additional htbins onto our original plot
        self.dir_num = int( self.settings["dirs"].index(htbin)) + 1
        for bin in self.settings["dirs"][self.dir_num:]:
          add_plot = self.DataFile.Get(("%s%s/%s" %(histpath,bin,histname) if histpath !="" else "%s%s/%s" %(histpath,bin,histname) ))
          plot.Add(add_plot,1)
 
      if self.DoRatios == "True": self.MakePad(plot)
      self.currenthtbin = htbin.split('_')
      if combine == "True": self.currenthtbin[1] = "upwards"
      self.max_min = [0,0]
      self.c1.cd(1)
      plot.GetSumw2()
      self.iflog = 0
      self.reversed = 0
      self.simple_draw_zinv = None
      self.simple_draw_sms = None
      self.histclone_keeper = []
      self.total_mc_maker = []
      self.ewk_mc_maker = []
      self.qcd_only = []
      self.draw_error = []
      self.draw_error_simple = []
      plot.SetMarkerStyle(20)
      plot.SetMarkerSize(1.5)
      plot.SetLineWidth(2)
      
      # If Draw_Data is false then all data points are set to 0
      if self.Draw_Data == "False" : self.Floor_Data(plot) 
  
      # Hist Options are applied such as axis range, logY settings and rebinning
      plot = self.Hist_Options(histname,plot,canvas = self.up if self.DoRatios == "True" else self.c1,word=True)

      self.max_maker = [plot]
      self.Legend_Maker()
      if self.Draw_Data == "False" : self.leg.AddEntry(plot,"Data","P")
      self.Poission(plot)

      # All MC files are looped through here and their plots are also drawn on the canvas
      self.MC_Draw(rootpath,histname,htbin, histpath = histpath,combine = combine)
      self.stackleg = self.leg.Clone()

      if type(plot) != type(r.TH2D()) and "Profile" not in self.settings["Misc"]:
        # This draws the total MC band for Total MC, EWK MC only, EWK+QCD used in data/MC ratio
        self.Draw_Total_MC(self.total_mc_maker)
        self.Draw_Total_MC(self.ewk_mc_maker, NoDraw = "EWK")
        self.Draw_Total_MC(self.total_mc_maker, NoDraw = "EWKQCD")

      self.yaxis_maximiser(plot)
      self.Drawer(self.max_maker)
      if type(plot) != type(r.TH2D()) and "Profile" not in self.settings["Misc"]:
        self.Drawer(self.draw_error,error="True")
        self.leg.Draw("SAME")
      
      self.TextBox(plot,(rootpath.split("/")[0] if not combine else (rootpath.split("/")[0]).rstrip("475")),histname)
      if "NoLegend" not in self.settings["Misc"]: self.TagBox()
      if type(plot) != type(r.TH2D()): 
          # Redraw data to make it easier to see
          plot.Draw("PSAME")
      if self.DoRatios == "True" and type(plot) != type(r.TH2D()): self.MakeMCRatio(histname,plot,self.total_background)

      # Save files in png,pdf and .C formats
      for ext in ['png','pdf','C']: self.c1.SaveAs("%s/%s/%s_%s%s.%s" %(htbin,histname,histname,(rootpath.split("/")[0]).rsplit('_',1)[0]+"_upwards" if combine == "True" else  rootpath.split("/")[0],"_reversed" if "Reversed" in self.settings["Misc"] else "_profile" if "Profile" in self.settings["Misc"] else "",ext)) 
      
      # Make Stacked plots and also Simplified plots here
      if type(plot) != type(r.TH2D()) and "Profile" not in self.settings["Misc"]:
        self.Stack_Draw(plot,self.total_mc_maker,htbin,histname,rootpath,combine = combine)
        if "Normalise" in self.settings["Misc"]: self.Normalise_Plots(plot,self.ewk_mc_maker,self.qcd_only,htbin,histname,rootpath,combine = combine)
        # else: self.Simple_Draw(plot,self.ewk_background,self.qcd_only,self.total_background,htbin,histname,rootpath,combine = combine)

      for file in self.Plot_Closer: file.Close()

  def Floor_Data(self,plot):

      if type(plot) == type(r.TH2D()):
         for xbin in range(0, plot.GetNbinsX()+1):
            for ybin in range(0, plot.GetNbinsY()+1):
                plot.SetBinContent(xbin,ybin,0)
                plot.SetBinError(xbin,ybin,0)

      else:
        for bin in range(0, plot.GetNbinsX()+1): 
           plot.SetBinContent(bin,0)
           plot.SetBinError(bin,0)

  def Normalise_Plots(self,plot,mc_array,qcd_array,htbin,histname,rootpath,combine=""):

    self.c1.cd(1)
    #self.c1.SetLogy(0)
    for num,mc_hist in enumerate(mc_array):
      if num == 0: mc_plot = mc_hist
      else: mc_plot.Add(mc_hist)
    if qcd_array: qcd_plot = qcd_array[0]

    mc_plot.GetSumw2()  
    mc_int = mc_plot.Integral()
    plot_int = plot.Integral()
    if qcd_array: qcd_int = qcd_plot.Integral()

    if "Reversed" in self.settings["Misc"]:
       mc_int = mc_plot.GetBinContent(1)
       plot_int = plot.GetBinContent(1)
       if qcd_array: qcd_int = qcd_plot.GetBinContent(1)

    for i in range (plot.GetNbinsX()):

      try:plot.SetBinContent(i+1,plot.GetBinContent(i+1)/plot_int)
      except ZeroDivisionError: plot.SetBinContent(i+1,0)
      try:mc_plot.SetBinContent(i+1,mc_plot.GetBinContent(i+1)/mc_int)
      except ZeroDivisionError: mc_plot.SetBinContent(i+1,0)
      if qcd_array:
        try:qcd_plot.SetBinContent(i+1,qcd_plot.GetBinContent(i+1)/qcd_int)
        except ZeroDivisionError: qcd_plot.SetBinContent(i+1,0)

    leg = r.TLegend(0.68,0.53,0.90,0.75) 
    leg.SetTextSize(0.02)
    leg.SetShadowColor(0)
    leg.SetBorderSize(0)
    leg.SetFillColor(0)
    leg.SetLineColor(0)
    #leg.AddEntry(plot,"8TeV Data","L")
    leg.AddEntry(mc_plot,"EWK MC","L")
    mc_plot.SetLineColor(3)
    mc_plot.SetFillColor(0)
    mc_plot.GetYaxis().SetRangeUser(0.005,1.5)
    mc_plot.Draw("HIST")
    if qcd_array: 
       leg.AddEntry(qcd_plot,"QCD MC","L")
       qcd_plot.SetFillColor(0)
       qcd_plot.Draw("HISTSAME")
    #plot.SetLineColor(2)
    #plot.Draw("HISTSAME")
    leg.Draw("SAME")
    self.TextBox(plot,(rootpath.split("/")[0] if not combine else (rootpath.split("/")[0]).rstrip("475")),histname)
    self.TagBox()
    if self.DoRatios == "True": self.MakeMCRatio(histname,plot,mc_plot)
    for ext in ['png','pdf','C']: self.c1.SaveAs("%s/%s/Simplified_%s_%s_normalised_%s.%s" %(htbin,histname,histname,(rootpath.split("/")[0]).rsplit('_',1)[0]+"_upwards" if combine == "True" else  rootpath.split("/")[0],"reversed" if "Reversed" in self.settings["Misc"] else "",ext))  

  def Stack_Draw(self,data,mc_array,htbin,histname,rootpath,combine=""):
    self.c1.cd(1)
    mc_stack = r.THStack()
    self.Stack_Sorter(mc_array)
    for plot in mc_array:
      plot.SetFillColor(plot.GetLineColor())
      mc_stack.Add(plot)
    data.Draw()
    mc_stack.Draw("HISTSAME")
    self.stackleg.Draw("SAME")
    data.Draw("PSAME")
    self.TextBox(data,(rootpath.split("/")[0] if not combine else (rootpath.split("/")[0]).rstrip("475")),histname)
    self.TagBox()
    if self.DoRatios == "True": self.MakeMCRatio(histname,data,self.total_background)
    for ext in ['png','pdf','C']: self.c1.SaveAs("%s/%s/Stacked_%s_%s%s.%s" %(htbin,histname,histname,(rootpath.split("/")[0]).rsplit('_',1)[0]+"_upwards" if combine == "True" else  rootpath.split("/")[0],"reversed" if "Reversed" in self.settings["Misc"] else "" ,ext))  

  # Sorted stacked files with Lowest yield on the bottom to highest on top
  def Stack_Sorter(self,mc_array):
    temp = []
    for num,plot in enumerate(mc_array):
        temp.append(plot.Integral())
    swapped = True  
    while swapped:  
       swapped = False  
       for i in range(len(temp)-1):  
          if temp[i] > temp[i+1]:  
             temp[i], temp[i+1] = temp[i+1], temp[i]
             mc_array[i+1], mc_array[i] = mc_array[i], mc_array[i+1]
             swapped = True 
    return mc_array
  
  def Simple_Draw(self,data,mc_combined,qcd_only,total_mc,htbin,histname,rootpath,combine = ''):
    self.c1.cd(1)
    self.Legend_Maker()
    self.leg.AddEntry(data,"Data","P")
    mc_stacker = r.THStack()
    if self.simple_draw_zinv: self.leg.AddEntry(self.simple_draw_zinv,"Z Jets","L")
    if self.simple_draw_sms: self.leg.AddEntry(self.simple_draw_sms,"SMS","L")
    self.leg.AddEntry(mc_combined,"EWK","L")
    if qcd_only: self.leg.AddEntry(qcd_only[0],"QCD","L")
    #self.leg.AddEntry(total_mc,"EWK + QCD","L")
    data.Draw()
    mc_combined.SetMarkerColor(4)
    mc_combined.SetMarkerStyle(20)
    mc_stacker = r.THStack()
    #mc_stacker.Add(mc_combined)
    if qcd_only: 
      qcd_only[0].SetFillColor(0)
      #mc_stacker.Add(qcd_only[0])
      qcd_only[0].Draw("SAMEHIST")
    
    mc_stacker.Add(mc_combined)
    mc_stacker.Draw("SAMEHIST")
    if self.simple_draw_sms: 
    #    self.simple_draw_sms.SetMarkerStyle(20)
        #mc_stacker.Add(self.simple_draw_sms)
        self.simple_draw_sms.Draw("SAMEHIST")
    mc_combined.Draw("SAMEHIST")

    if self.simple_draw_zinv: 
        self.simple_draw_zinv.SetMarkerStyle(20)
        self.simple_draw_zinv.Draw("SAMEHIST")
    
    self.Drawer(self.draw_error_simple,error="True")
    self.leg.Draw("SAME")
    self.TextBox(data,(rootpath.split("/")[0] if not combine else (rootpath.split("/")[0]).rstrip("475")),histname)
    self.TagBox()
    data.Draw("PSAME")
    if self.DoRatios == "True": self.MakeMCRatio(histname,data,total_mc)
    for ext in ['png']: # ['png','pdf','C']:
      self.c1.SaveAs("%s/%s/Simplified_%s_%s%s.%s" %(htbin,histname,histname,(rootpath.split("/")[0]).rsplit('_',1)[0]+"_upwards" if combine == "True" else  rootpath.split("/")[0],"reversed" if "Reversed" in self.settings["Misc"] else "", ext))
    
  
  def Draw_Total_MC(self,mc_list,NoDraw = ""):
    
    if NoDraw == "EWK":
      for num,hist in enumerate(mc_list):
        if num == 0:self.ewk_background = hist.Clone()
        else: self.ewk_background.Add(hist)
      self.ewk_background.SetLineColor(3)
      self.ewk_background.SetLineWidth(3)

    elif NoDraw == "EWKQCD":
      for num,hist in enumerate(mc_list):
        if num == 0:self.total_background = hist.Clone()
        else: self.total_background.Add(hist)
      self.total_background.SetLineColor(3)
      self.total_background.SetLineWidth(3)

    else:
      for num,hist in enumerate(mc_list):
        if num == 0:self.totmcplot = hist.Clone()
        else: self.totmcplot.Add(hist)
      errorbarplot = r.TGraphErrors(self.totmcplot)
      errorbarplot.SetFillColor(3)
      errorbarplot.SetFillStyle(3008)
      self.draw_error.append(errorbarplot)
      self.draw_error_simple.append(errorbarplot)
      self.totmcplot.SetLineColor(3)
      self.leg.AddEntry(self.totmcplot,"Combined SM","L")
      self.totmcplot.SetLineWidth(3)
      self.max_maker.append(self.totmcplot)

  def Drawer(self,hist_collection,error=''):
    for num,plot in enumerate(hist_collection):
      if error:
        # Draw Error bands
        plot.Draw("SAME2")
      else:
        if type(plot) == type(r.TH2D()): 
          plot.Draw("COLZ")
        else:
          if num == 0: plot.Draw("PE0")
          else: plot.Draw("HISTSAME")

  def ReversedDrawer(self,histname,canvas,hist_collection,rootpath):
    for num,plot in enumerate(hist_collection):
      if num == 0 :plot = self.Hist_Options(histname,plot,canvas = canvas,norebin=true)
      else: plot = self.Hist_Options(histname,plot,norebin=true)
      self.yaxis_maximiser(hist_collection[0])
      self.Drawer(hist_collection)
      self.leg.Draw("SAME")
      self.TextBox(hist_collection[0],rootpath.split("/")[0],histname)
      self.TagBox()
 
  #Ensured that y-axis is set to accomodate the yields in MC and display everything on canvas 
  def yaxis_maximiser(self,plot):
      highest = 0
      if type(plot) != type(r.TH2D()):
        for max in self.max_maker:
          temp = max.GetMaximum()
          if temp > highest: highest = temp
        if self.iflog : self.ymax = highest * 10
        else: self.ymax = highest * 1.5
        self.max_maker[0].GetYaxis().SetRangeUser(self.iflog,self.ymax)

  def TextBox(self,plot,htbin,histname):

    hist_multi = histname.split('_')[-1]
    # multi_txt = ""
    # if hist_multi == '3':
    #   multi_txt += '>'
    #   multi_txt += str(hist_multi)
    # else:
    #   multi_txt += '='
    #   if hist_multi == 'all':
    #     multi_txt += 'all'
    #   else:
    #     multi_txt += str(int(hist_multi)+1)

    jet_txt = {
      "1":"=2",
      "2":"=3",
      "3":"=4",
      "4":">=5",
      "all":"all",
    }

    Textbox = r.TLatex()
    Textbox.SetNDC()
    Textbox.SetTextAlign(12)
    Textbox.SetTextSize(0.04)
    Textbox.DrawLatex(0.1,0.95, htbin+'    Jet Multiplicity ' + jet_txt[hist_multi])

  def TagBox(self):
    Textbox = r.TLatex()
    title = "CMS 2012, 8TeV"
    lumi= "\int L dt = %s fb^{-1}" % (self.settings['Lumo']/10)
    Textbox.SetNDC()
    Textbox.SetTextAlign(12)
    Textbox.SetTextSize(0.03)
    Textbox.DrawLatex(0.7,0.85,title )
    Textbox.DrawLatex(0.7,0.79,lumi)


  def Sideband_Corrections(self,plot,legend):

      if legend in ["Single Top","t\\bar{t}","WW/ZZ/WZ"] : scalefactor = this_run()["tt_corr"]
      elif legend in ["W + Jets"]: scalefactor = this_run()["wj_corr"]
      elif legend in ["Z\\rightarrow \\nu\\bar{\\nu}"]: scalefactor = this_run()["dy_corr"]
      elif legend in ["DY + Jets"]: scalefactor = this_run()["dy_corr"]
      elif legend in ["\gamma + Jets"] : scalefactor = this_run()["dy_corr"]
      else: scalefactor = 1.

      plot.Scale(scalefactor)
      return plot

  def Plot_Combiner(self,passed_plot,htbins,histpath,histname,File,leg_entry,add_jet_mult = ''):
    
    for bin in htbins:
      
      another_plot = File.Get(("%s%s/%s" %(histpath,bin,histname) if histpath !="" else "%s%s/%s" %(histpath,bin,histname) ) ) 
    
      # apply trigger eff scaling
      another_plot.Scale(self.settings["Trigger"][bin.split('_')[0]+"_"+self.jetcategory])
      
      htsplit = bin.split('_')

      try : midht = (float(htsplit[0])+float(htsplit[1]))/2
      except IndexError:  midht = float(htsplit[0])
     
      """ 
      Sideband corrections are added here
      """ 

      if self.MHTMETcorrections == "True":  self.Sideband_Corrections(another_plot,leg_entry)

      passed_plot.Add(another_plot,1)

  def MC_Draw(self,rootpath,histname,htbin,histpath,combine = ""):

      """
      MC files are added in here, sample type is defined in config file and used her to match to a string
      """
      for key,sample in sorted(self.sample_list.iteritems()):
        if "n" != key[0]:
          if sample[2] == "EWK": 
            self.EWKFile = r.TFile.Open("../%s" %sample[0])
            self.Add_MCplot("ewk_plot",rootpath,histname,htbin,4,"EWK MC",self.EWKFile,histpath,combine=combine)
          if sample[2] == "WJets": 
            self.WJetsFile = r.TFile.Open("../%s" %sample[0])
            self.Add_MCplot("wjet_plot",rootpath,histname,htbin,4,"W + Jets",self.WJetsFile,histpath,combine=combine) 
          if sample[2] == "Zinv":
            self.ZinvFile = r.TFile.Open("../%s" %sample[0]) 
            self.Add_MCplot("zinv_plot",rootpath,histname,htbin,5,"Z\\rightarrow \\nu\\bar{\\nu}",self.ZinvFile,histpath,combine=combine) 
          if sample[2] == "TTbar": 
            self.TTbarFile = r.TFile.Open("../%s" %sample[0])
            self.Add_MCplot("ttbar_plot",rootpath,histname,htbin,2,"t\\bar{t}",self.TTbarFile,histpath,combine=combine)           
          if sample[2] == "Top": 
            self.TopFile = r.TFile.Open("../%s" %sample[0])
            self.Add_MCplot("top_plot",rootpath,histname,htbin,2,"t\\bar{t}/ Single t",self.TopFile,histpath,combine=combine)  
          if sample[2] == "Di-Boson": 
            self.Di_Boson = r.TFile.Open("../%s" %sample[0])
            self.Add_MCplot("di_boson_plot",rootpath,histname,htbin,44,"WW/ZZ/WZ",self.Di_Boson,histpath,combine=combine)#,style="9")
          if sample[2] == "DY": 
            self.DiMuonFile = r.TFile.Open("../%s" %sample[0])
            self.Add_MCplot("dimuon_plot",rootpath,histname,htbin,6,"DY + Jets",self.DiMuonFile,histpath,combine=combine)
          if sample[2] == "Single_Top": 
            self.SingleTopFile = r.TFile.Open("../%s" %sample[0]) 
            self.Add_MCplot("sing_top_plot",rootpath,histname,htbin,40,"Single Top",self.SingleTopFile,histpath,combine=combine)#,style="9")
          if sample[2] == "Photon": 
            self.PhotonFile = r.TFile.Open("../%s" %sample[0])
            self.Add_MCplot("photon_plot",rootpath,histname,htbin,8,"\gamma + Jets",self.PhotonFile,histpath,combine=combine)
          if sample[2] == "Z0": 
            self.Z0File = r.TFile.Open("../%s" %sample[0])
            self.Add_MCplot("z0_plot",rootpath,histname,htbin,2,"Z0 Template",self.Z0File,histpath,combine=combine)
          if sample[2] == "Z2": 
            self.Z2File = r.TFile.Open("../%s" %sample[0])
            self.Add_MCplot("z2_plot",rootpath,histname,htbin,5,"Z2 Template",self.Z2File,histpath,combine=combine)
          if sample[2] == "QCD": 
            self.QCDFile = r.TFile.Open("../%s" %sample[0])
            self.Add_MCplot("qcd_plot",rootpath,histname,htbin,7,"QCD",self.QCDFile,histpath,combine=combine,style="10")
          if sample[2] == "SMS": 
            self.SMSFile = r.TFile.Open("../%s" %sample[0])
            self.Add_MCplot("sms_plot",rootpath,histname,htbin,2,"SMS",self.SMSFile,histpath,combine=combine)

          
  def Add_MCplot(self,mcplot,rootpath,histname,htbin,color,leg_entry,File,histpath,combine = "",style=""):
       
      mcplot  = File.Get("%s" %rootpath)
      self.jetcategory = histname.split('_')[-1]

      # apply trigger eff scaling      
      mcplot.Scale(self.settings["Trigger"][htbin.split('_')[0]+"_"+self.jetcategory])

      """
      MHT/MET sideband plots added here. Comment out to ignore
      """ 
      htsplit = htbin.split('_')
      try : midht = (float(htsplit[0])+float(htsplit[1]))/2
      except IndexError:  midht = float(htsplit[0])

      if self.MHTMETcorrections == "True":  self.Sideband_Corrections(mcplot,leg_entry)
        
      #Used when combining over all HT bins 200_upwards, 375_upwards
      if combine:
        self.Plot_Combiner(mcplot,self.settings["dirs"][self.dir_num:],histpath,histname,File,leg_entry,add_jet_mult = ("True" if histname.split('_')[-1] == '3' else "False"))

      mcplot.GetSumw2()

      if "SMS" not in leg_entry:
        mcplot.Scale(float(self.settings["Lumo"]))
      else:
        ##@@ need to account for the factor of 10 in self.settings["Lumo"]!!
        # mcplot.Scale(float(self.settings["Lumo"])*0.00028) # scale factor for 128059 evts of 400GeV stop production (xs = 0.0356pb)
        # mcplot.Scale(float(self.settings["Lumo"])*0.000957) # (250,230), T2cc 582301 evts, xs = 5.57596
        mcplot.Scale(float(self.settings["Lumo"])*0.002046) # (250,240), T2_4body 272495 evts, xs = 5.57596
        # mcplot.Scale(float(self.settings["Lumo"])*0.000959) # (250,170), T2cc 581438 evts, xs = 5.57596
        # mcplot.Scale(float(self.settings["Lumo"])*0.05256) # (225,125) T2bw 0p75, 18853 evts, xs = 9.90959
        mcplot.SetLineStyle(2)

      mcplot.SetLineColor(int(color))
      self.leg.AddEntry(mcplot,str(leg_entry),"L")
      mcplot.SetLineWidth(3)
      
      if style: mcplot.SetLineStyle(int(style))
      mcplot = self.Hist_Options(histname,mcplot)
      

      if leg_entry =="Z\\rightarrow \\nu\\bar{\\nu}":
        self.simple_draw_zinv = mcplot.Clone()
        errorbarplot = r.TGraphErrors(mcplot)
        errorbarplot.SetFillColor(int(color))
        errorbarplot.SetFillStyle(3008)
        self.draw_error_simple.append(errorbarplot)

      if leg_entry =="SMS":
        self.simple_draw_sms = mcplot.Clone()
        errorbarplot = r.TGraphErrors(mcplot)
        errorbarplot.SetFillColor(int(color))
        errorbarplot.SetFillStyle(3008)
        self.draw_error_simple.append(errorbarplot)

      if leg_entry =="t\\bar{t}":
        self.simple_draw_ttbar = mcplot.Clone()
        errorbarplot = r.TGraphErrors(mcplot)
        errorbarplot.SetFillColor(int(color))
        errorbarplot.SetFillStyle(3008)

      if leg_entry == "QCD": 
        errorbarplot = r.TGraphErrors(mcplot)
        errorbarplot.SetFillColor(int(color))
        errorbarplot.SetFillStyle(3008)
        self.qcd_only.append(mcplot)
        if style: 
          errorbarplot.SetLineStyle(int(style))
          self.draw_error.append(errorbarplot)
          self.draw_error_simple.append(errorbarplot)

      #All plots added here to be drawn later
      self.max_maker.append(mcplot)
      if leg_entry != "SMS" : self.total_mc_maker.append(mcplot)
      if leg_entry != "QCD" and leg_entry != "SMS": self.ewk_mc_maker.append(mcplot)
      self.Plot_Closer.append(File)

  def Legend_Maker(self): 
      self.leg = r.TLegend(0.72,0.54,0.90,0.76) 
      self.leg.SetTextSize(0.02)
      self.leg.SetShadowColor(0)
      self.leg.SetBorderSize(0)
      self.leg.SetFillColor(0)
      self.leg.SetLineColor(0)

  def make_plot_name_list(self, hist_names = []):
    """ returns a list of all combinations of arg and jetcats"""

    out = []

    for i in itertools.product(hist_names, self.jet_cats):
      out.append( i[0] + "_" + i[1] )

    return out

  def Hist_Options(self,histogram,plot,canvas="",word = "",norebin=""):


        """
        Hist options added in here
 
        word : first time hist_option is called for data root file. Sets titles for both axes. 
        norebin : true when making data/MC ratio. Plot is already rebinned, don't want to apply it again

        Global changes should be done in the norebin section.

        """ 
        if word: print "Applying %s Options" % histogram
       
        if histogram in self.make_plot_name_list(["EffectiveMass"]):
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 50 GeV")
          if not norebin:
            plot.Rebin(50)
            self.OverFlow_Bin(plot,0,2500,1600)

        if histogram in self.make_plot_name_list(["MHT", "MHT_FixedThreshold"]):
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 50 GeV")
          if not norebin:
            plot.Rebin(5)
            self.OverFlow_Bin(plot,0,600,800)
       
        if histogram in self.make_plot_name_list(["MET", "MET_Corrected"]):
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 25 GeV")
          if not norebin:
            plot.Rebin(5)
            self.OverFlow_Bin(plot,0,2500,800)

        if histogram in self.make_plot_name_list(["MT"]):
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 50 GeV")
          if not norebin:
            plot.Rebin(50)
            self.OverFlow_Bin(plot,0,2000,800)

        if histogram in self.make_plot_name_list(["pfCandsPt"]):
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 50 GeV")
          if not norebin:
            plot.Rebin(5)
            self.OverFlow_Bin(plot,0,200,500)

        if histogram in self.make_plot_name_list(["pfCandsDzPV"]):
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 50 GeV")
          if not norebin:
            plot.Rebin(5)
            self.OverFlow_Bin(plot,0,0.1,500)

        if histogram in self.make_plot_name_list(["pfCandsDunno"]):
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 50 GeV")
          if not norebin:
            plot.Rebin(5)
            self.OverFlow_Bin(plot,0,0.1,500)            

        if "MuPFIso_" in histogram:
          if canvas: self.Log_Setter(plot,canvas,0.1)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 0.02")
          if not norebin:
            plot.Rebin(20)
            self.OverFlow_Bin(plot,0,2.,0.16)

        if "MuHIso_" in histogram:
          if canvas: self.Log_Setter(plot,canvas,0.1)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 0.02")
          if not norebin:
            plot.Rebin(20)
            self.OverFlow_Bin(plot,0,2.,0.14)

        if "MuEIso_" in histogram:
          if canvas: self.Log_Setter(plot,canvas,0.1)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 0.02")
          if not norebin:
            plot.Rebin(20)
            self.OverFlow_Bin(plot,0,2.,0.14)

        if "MuTrIso_" in histogram:
          if canvas: self.Log_Setter(plot,canvas,0.1)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 0.02")
          if not norebin:
            plot.Rebin(20)
            self.OverFlow_Bin(plot,0,2.,0.2)

        if "MuPt_" in histogram:
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 25 GeV")
          if not norebin:
            plot.Rebin(20)
          self.OverFlow_Bin(plot,10,2010,1000)

        if "PartonHT" in histogram :
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 25 GeV")
          if not norebin:
            plot.Rebin(20)  
            self.OverFlow_Bin(plot,0,2000,1500)
            if "Reversed" in self.settings["Misc"]: self.Reversed_Integrator(plot)


        if histogram in self.make_plot_name_list(["HT"]): # note: this should eventually be done for all histos
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 25 GeV")
          if not norebin:
            plot.Rebin(5)  
            self.OverFlow_Bin(plot,0,2000,1500)
            if "Reversed" in self.settings["Misc"]: self.Reversed_Integrator(plot)

        if "HT_after_alphaT" in histogram:
          if canvas:self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 50 GeV")
          if not norebin:
            plot.Rebin(50)
            self.OverFlow_Bin(plot,0,2000,1250)
      
        if "HT_vs_SecondJetPt" in histogram:
          if word:
            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("JetPt_{T}")
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitle("H_{T}")
            
          if not norebin:
            ptbins = {"200":26.0,"275":36.68,"325":43.34}
            setjetpt = 50
            if self.currenthtbin[0] in ptbins.keys() : setjetpt = ptbins[self.currenthtbin[0]]
            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.SetAxisRange(float(self.currenthtbin[0]),(float(self.currenthtbin[0]) if self.currenthtbin[1] != "upwards" else 874),"X")
            plot.SetAxisRange(setjetpt,150,"Y")
            if "Scale" in self.settings["Misc"]: self.EfficiencyCalculator(plot,normalise = "false",integral = "single")

        if "Resolution_LeadingJet_Pt" in histogram:
          if word:
            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("(Reco - Gen)/Gen")
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitle("LeadingJet P_{T}")
            
          if not norebin:

            ptbins = {"200":53.33,"225":60.,"250":66.66,"275":73.33,"325":86.66}
            setjetpt = 100.
            if self.currenthtbin[0] in ptbins.keys() : setjetpt = ptbins[self.currenthtbin[0]]

            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("(Reco - Gen)/Gen")
            plot.SetAxisRange(float(setjetpt)-5.0,3*float(setjetpt),"X")
            #plot.SetAxisRange(-1.5,1.5,"Y")
            if "Profile" in self.settings["Misc"] : 
                 a = plot.ProjectionY("_py",0,-1,"d")
                 return a

        if "Resolution_SecondJet_Pt" in histogram:
          if word:
            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("(Reco - Gen)/Gen")
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitle("LeadingJet P_{T}")
            
          if not norebin:

            ptbins = {"200":0.5*53.33,"225":0.5*60.,"250":0.5*66.66,"275":0.5*73.33,"325":0.5*86.66}
            setjetpt = 50.
            if self.currenthtbin[0] in ptbins.keys() : setjetpt = ptbins[self.currenthtbin[0]]

            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("(Reco - Gen)/Gen")
            plot.SetAxisRange(float(setjetpt)-5.0,3*float(setjetpt),"X")
            #plot.SetAxisRange(-1.5,1.5,"Y")
            if "Profile" in self.settings["Misc"] : 
                 a = plot.ProjectionY("_py",0,-1,"d")
                 return a

        if "Resolution_HT" in histogram:
          if word:
            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("(Reco - Gen)/Gen")
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitle("H_{T}")
            
          if not norebin:
            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("(Reco - Gen)/Gen")
            plot.SetAxisRange(float(self.currenthtbin[0])-10.0,(float(self.currenthtbin[1]) if self.currenthtbin[1] != "upwards" else 975),"X")
            #plot.SetAxisRange(-1.5,1.5,"Y")
            if "Profile" in self.settings["Misc"] : 
                 a = plot.ProjectionY("_py",0,-1,"d")
                 return a

        if "Resolution_MHT" in histogram:
          if word:
            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("(Reco - Gen)/Gen")
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitle("MH_{T}")
            
          if not norebin:
            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("(Reco - Gen)/Gen")
            plot.SetAxisRange(float(self.currenthtbin[0])*0.4,(float(self.currenthtbin[1]) if self.currenthtbin[1] != "upwards" else 975),"X")
            #plot.SetAxisRange(-1.5,1.5,"Y")
            if "Profile" in self.settings["Misc"] : 
                 a = plot.ProjectionY("_py",0,-1,"d")
                 return a

        if "LeadJet_vs_SecondJet" in histogram:
          if word:
            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("#LeadJet P_{T}")
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitle("SecondJet P_{T}")
            
          if not norebin:
            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.SetAxisRange(50.0,150.0,"Y")
            plot.SetAxisRange(50.0,150.0,"X")
            if "Scale" in self.settings["Misc"]: self.EfficiencyCalculator(plot,normalise = "false")

        if "HT_vs_AlphaT" in histogram:

          if canvas: self.Log_Setter(plot,canvas,0.55)

          if word:
            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("#alpha_{T}")
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitle("H_{T}")
            
          if not norebin:
            #plot.RebinX(25)
            plot.RebinY(1)
            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("#alpha_{T}")
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitle("H_{T}")
            plot.SetAxisRange(float(self.currenthtbin[0]),(float(self.currenthtbin[0]) if self.currenthtbin[1] != "upwards" else 874),"X")
            plot.SetAxisRange(0.55,1.5,"Y")
            plot.SetAxisRange(0.0,3.0,"Z")

        if histogram in self.make_plot_name_list(["MHTovMET", "MHTovMET_Scaled"]):
          if canvas: self.Log_Setter(plot,canvas,0.1)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 0.1")
          if not norebin:
            plot.Rebin(5)
            self.OverFlow_Bin(plot,0,10.,5.0)

        if "MHT_vs_MET" in histogram:
       
          #if canvas: self.Log_Setter(plot,canvas,0.1)

          if word: 
            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("MET")
            plot.GetXaxis().SetTitle("MHT")
            #plot.GetZaxis().SetRangeUser(0.8,1.2) 
          if not norebin:

            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("MET")
            plot.GetXaxis().SetTitle("MHT")
            plot.RebinY(10)
            plot.RebinX(10)
            plot.SetAxisRange(0.,500.,"Y")
            plot.SetAxisRange(0.,500.,"X")

        if "MET_vs_MHTovMET" in histogram:
       
          #if canvas: self.Log_Setter(plot,canvas,0.1)
          if word: 
            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("MHT/MET")
            plot.GetXaxis().SetTitle("MET")
            #plot.GetZaxis().SetRangeUser(0.8,1.2) 
          if not norebin:
            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("MHTovMET")
            plot.GetXaxis().SetTitle("MET")
            plot.RebinY(1)
            plot.RebinX(10)
            plot.SetAxisRange(0.,5.,"Y")
            plot.SetAxisRange(0.,500.,"X")

        if "MHTovMET_vs_AlphaT" in histogram:
       
          if canvas: self.Log_Setter(plot,canvas,0.1)

          if word: 
            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("#alpha_{T}")
            plot.GetXaxis().SetTitle("MHTovMET")

          if not norebin:
            plot.SetTitle("")
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("#alpha_{T}")
            plot.GetXaxis().SetTitle("MHTovMET")
            plot.RebinY(1)
            plot.RebinX(10)
            plot.SetAxisRange(1.0,3.0,"Y")

        if histogram in self.make_plot_name_list(["AlphaT"]): 

          axis_rebin = array('d',[0.00,0.10,0.15,0.25,0.30,0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.90,1.00,1.25,1.50,1.75,2.0,2.50,3.00,3.10,10.0])
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events")
          
          if not norebin:
            a = plot.Rebin(len(axis_rebin)-1,"plot",axis_rebin )
            self.OverFlow_Bin(a,0.0,10.00,3.0)
            self.BinNormalise(a,0.05)
            if "Reversed" in self.settings["Misc"]:self.Reversed_Integrator(a)
            return a
          
        if histogram in self.make_plot_name_list(["AlphaT_Zoomed"]):
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 0.08")
          if not norebin:
            plot.Rebin(5)

        if "JetMultiplicity_" in histogram: 
          if canvas: self.Log_Setter(plot,canvas,0.5)
        
        if "Number_Btags" in histogram : 
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetXaxis().SetTitleOffset(1.3)
            plot.GetXaxis().SetTitle("N_{b-tag}")
 
        if "Number_Good_verticies_" in histogram:
          if canvas: self.Log_Setter(plot,canvas,0.5)

        if "Number_verticies_" in histogram:
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if not norebin:
            pass

        if histogram in self.make_plot_name_list(["LeadJetPt","SecondJetPt","CommonJetPt"]):
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if not norebin:
            plot.Rebin(2)
            self.OverFlow_Bin(plot,0.,1500.,500.)

        if histogram in self.make_plot_name_list(["LeadJetEta","SecondJetEta","CommonJetEta"]):
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if not norebin:
            plot.Rebin(2)
            plot.SetAxisRange(-3.0,3.0,"X")

        if histogram in self.make_plot_name_list(["MuEta"]):
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if not norebin:
            plot.Rebin(5)
            plot.SetAxisRange(-3.0,3.0,"X")


        if histogram in ["ComMinBiasDPhi_all","ComMinBiasDPhi_1","ComMinBiasDPhi_2","ComMinBiasDPhi_3","ComMinBiasDPhi_4", "ComMinBiasDPhi_acceptedJets_all","ComMinBiasDPhi_acceptedJets_1","ComMinBiasDPhi_acceptedJets_2","ComMinBiasDPhi_acceptedJets_3","ComMinBiasDPhi_acceptedJets_4"]:
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word:
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events")
          if not norebin:
            plot.Rebin(10)
            self.OverFlow_Bin(plot,0,3.15,3.15)

        if histogram in ["MinBiasJetLeadJetDPhi_all","MinBiasJetLeadJetDPhi_1","MinBiasJetLeadJetDPhi_2","MinBiasJetLeadJetDPhi_3","MinBiasJetLeadJetDPhi_4"]:
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word:
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events")
          if not norebin:
            plot.Rebin(5)
            self.OverFlow_Bin(plot,0,3.15,3.15)

        if histogram in self.make_plot_name_list(["Thrust_pjetDphi"]):
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word:
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events")
          if not norebin:
            plot.Rebin(5)
            self.OverFlow_Bin(plot,0,3.15,3.15)

        if histogram in self.make_plot_name_list(["Thrust_HTFmax", "Thrust_HTFmin"]):
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word:
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events")
          if not norebin:
            plot.Rebin(2)
            self.OverFlow_Bin(plot,0,1000., 1000.)

        if histogram in self.make_plot_name_list(["Thrust_MHTFmax", "Thrust_MHTFmin"]):
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word:
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events")
          if not norebin:
            plot.Rebin(2)
            self.OverFlow_Bin(plot,0,1000., 1000.)

        if "PhotonPt_" in histogram:
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 25 GeV")
          if not norebin:
            plot.Rebin(25)
          self.OverFlow_Bin(plot,0,1500,650)

        if "Photonrho25_" in histogram:
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events")
          if not norebin:
            plot.Rebin(4)
          self.OverFlow_Bin(plot,0,40,32)

        if "PhotonPFIso_" in histogram:
    
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events")
          if not norebin:
            plot.Rebin(20)
          self.OverFlow_Bin(plot,0,10.,4.)

        if "PhotonChargedIso_" in histogram:
    
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events")
          if not norebin:
            plot.Rebin(10)
          self.OverFlow_Bin(plot,0,10.,1.)

        if "PhotonNeutralIso_" in histogram:
    
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events")
          if not norebin:
            plot.Rebin(20)
          self.OverFlow_Bin(plot,0,10.,6.)

        if "Muon_Iso_PU_Interactions_" in histogram:
          #if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events")
          #if not norebin:
          #  plot.Rebin(2)
          self.OverFlow_Bin(plot,0,80,45)

        if "PU_Interactions_" in histogram:
          #if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events")
          #if not norebin:
          #  plot.Rebin(2)
          self.OverFlow_Bin(plot,0,80,45)


        if "DiMuon_Mass_" in histogram:
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 5 GeV")
          if not norebin:
            plot.Rebin(5)
          self.OverFlow_Bin(plot,0,1500,150)

        if "DiLepton_Mass_" in histogram:
          if canvas: self.Log_Setter(plot,canvas,0.5)
          if word: 
            plot.GetYaxis().SetTitleOffset(1.3)
            plot.GetYaxis().SetTitle("Events / 5 GeV")
          if not norebin:
            plot.Rebin(5)
          self.OverFlow_Bin(plot,0,1500,150)

        return plot

  def Log_Setter(self,plot,canvas,min):
    self.iflog = min
    plot.SetMinimum(float(min))
    if type(plot) == type(r.TH2D()):
      #canvas.SetLogz(1)
      canvas.SetLogy(1)

    else:
      canvas.SetLogy(1)

  def BinNormalise(self,hist,width):
    for bin in range(1,hist.GetNbinsX()+1):
       hist.SetBinContent(bin,hist.GetBinContent(bin)*(width/hist.GetBinWidth(bin)))
       hist.SetBinError(bin,hist.GetBinError(bin)*(width/hist.GetBinWidth(bin)))


  """
  Set overflow bin by passing x-value you want histogram to be displayed until and filling the last bin with the intergral over all remaining bins.
  """
  def OverFlow_Bin(self,hist,xmin,xmax,overflow,*args ):
     
    if args: 
      ymin = args[0]
      ymax = args[1]
      overflow_y = args[2]

      for y in range(0,hist.GetNbinsY()): 
          set_overflowx = float(hist.Integral(hist.GetXaxis().FindBin(overflow),hist.GetNbinsX(),y+1,y+1))
          hist.SetBinContent(hist.GetXaxis().FindBin(overflow),y+1,set_overflowx)
          hist.SetBinContent(hist.GetXaxis().FindBin(overflow),y+1,m.sqrt(set_overflowx))

      for x in range(0,hist.GetNbinsX()): 
          set_overflowy = float(hist.Integral(x+1,x+1,hist.GetYaxis().FindBin(overflow_y),hist.GetNbinsY()))
          hist.SetBinContent(x+1,hist.GetYaxis().FindBin(overflow),set_overflowy)
          hist.SetBinError(x+1,hist.GetYaxis().FindBin(overflow),m.sqrt(set_overflowy))

      hist.SetAxisRange(xmin,overflow,"X")
      hist.SetAxisRange(ymin,overflow_y,"Y")

    else:
      overflow_bin = hist.FindBin(overflow)
      set_overflow = float(hist.Integral(overflow_bin,hist.GetNbinsX()))

      hist.SetBinContent(overflow_bin,set_overflow)
      hist.SetBinError(overflow_bin,m.sqrt(set_overflow))
      hist.SetAxisRange(xmin,overflow,"X")
      additional_bin = (0.1)
      self.max_min = [xmin,overflow+additional_bin]

  def Reversed_Integrator(self,hist):
      
      self.histclone = hist.Clone()
      integral_keeper = []
      self.reversed = 1
      for i in range(self.histclone.GetNbinsX()): 
          integral_keeper.append(self.histclone.Integral(self.histclone.GetNbinsX()-i,self.histclone.GetNbinsX()))
      for k in range(self.histclone.GetNbinsX()):
        hist.SetBinContent(self.histclone.GetNbinsX()-k,integral_keeper[k])  
        hist.SetBinError(self.histclone.GetNbinsX()-k,m.sqrt(integral_keeper[k]))
      self.histclone_keeper.append(self.histclone) 

class Webpage_Maker(object):



      """
      This is where the webpage is made. This is all automated however you wil need to change
       
      self.ensure_dir("/home/hep/db1110/public_html/Website_Plots/"+self.webdir)
      -------
      if simplified:htF = open('/home/hep/db1110/public_html/Website_Plots/'+self.webdir+'/Simplified_'+j+'_'+i+'.html','w')
            elif stacked: htF = open('/home/hep/db1110/public_html/Website_Plots/'+self.webdir+'/Stacked_'+j+'_'+i+'.html','w')
            else: htF = open('/home/hep/db1110/public_html/Website_Plots/'+self.webdir+'/'+j+'_'+i+'.html','w')
      to a path that you have write access too.

      Webpage is made by first using os.walk into you Plots directory where all plots you make are dumped. The files are then copied across to where you specified.

      HTbins/Btag_Multiplicities vs plot names are then loops through to create a bunch of websites which are then filled with the .png files from doing a fnmatch.

      The loops can be a bit confusing. I wrote them a long time ago and it was a mind fuck at the time to follow what I was doing. If you want to make your own just take all the individual steps I've done as a basis and rewrite the whole thing in a less convoluted way!
      
        
      """

      # def __init__(self,plotnames,self.binning,category,option="",extra=""):
      def __init__(self,settings):
        self.extra = "" # dummy variable - can probably remove. left over from old __init__ definition
        print settings["Category"]
        if "Had" in settings["Category"]:
          self.category = ""
          self.title = settings["Category"]
        else: 
          self.category = settings["Category"]
          if self.extra: self.category = settings["Category"].rstrip(self.extra)
          self.title = settings["Category"]
        self.binning = settings["WebBinning"]
        self.jet_cats = settings["jet_categories"]
        self.Make_Page(settings["Plots"],settings["Webpage"])

      def ensure_dir(self,dir):
        try: os.makedirs(dir)
        except OSError as exc: pass
      
      def Make_Page(self,plotnames,option=""): 
        print "\n       ================================" 
        print "       ======== Making Webpage ========"
        print "       ********************************\n\n"
        self.webdir = self.title+"_plots_"+strftime("%d_%b_%H")
        self.ensure_dir("/Users/chrislucas/SUSY/AnalysisCode/Website_Plots/"+self.webdir)
        for root,dirs,files in os.walk('./Plots'):
          for filename in fnmatch.filter(files,'*'):
              name = os.path.join(root,filename)
              os.system('cp ' +name+ ' /Users/chrislucas/SUSY/AnalysisCode/Website_Plots/'+self.webdir+'/')
        
        if option == "Normal":
          for i in plotnames:
              counter = 0
              htF = open('/Users/chrislucas/SUSY/AnalysisCode/Website_Plots/'+self.webdir+'/'+i+'.html','w')
              htF.write('Author: Darren Burton <br> \n')
              htF.write('<script language="Javascript"> \n document.write("Last Modified: " + document.lastModified + ""); \n </script> <br> \n ')
              htF.write('<center>\n <p> \n <font size="5"> Binned Muon Control Sample </font>\n </p>\n') 
              htF.write('<font size="3">Results for :  '+i+' </font><br> \n')
              htF.write('Hist Name: ') 
              for k in plotnames:
                counter += 1
                htF.write('<a href=\"'+k+'.html\">'+k+'</a>')
                htF.write('   |    ')
                if counter == 5:
                  htF.write('<br> \n')
                  counter = 0
              htF.write('<br> \n')

              for root,dirs,files in os.walk('./'+self.webdir):
                sorter = []
                for filenames in fnmatch.filter(files,i+'_*.png'): 
                  sorter.append(filenames)
                  sorter.sort()
                for plot in sorter: htF.write('<a href='+plot+'><img height=\"400\" src=\"'+plot+'\"></a> \n') 

        if option == "btag":
          if self.extra == "OS":
            self.btag_slices = {"Inclusive":"Inclusive","OS_Di":"DiMuon_Pairs"}
            self.btag_names = {"Inclusive":self.category,"OS_Di":"_DiMuon"+self.category }

          else: 
            self.btag_slices = {'Zero':"0-btag",'One':"1-btag",'Two':"2-btag",'Three':"3-btag","Inclusive":"Inclusive",'More_Than_Zero':"A btag",'More_Than_Two':"More Than Two",'More_Than_Three':"More Than Three"}
            self.btag_names = {'More_Than_Three':"_btag_morethanthree_"+self.category,'More_Than_Two':"_btag_morethantwo_"+self.category,'More_Than_Zero':"_btag_morethanzero_"+self.category,'Zero':"_btag_zero_"+self.category,'One':"_btag_one_"+self.category,'Three':"_btag_three_"+self.category,'Two':"_btag_two_"+self.category,"Inclusive":'_'+self.category }

          self.Alpha_Webpage(self.binning,plotnames,link="Zero",outertitle="HT Bins:  ")
          self.Alpha_Webpage(self.btag_slices,plotnames,link=self.binning[0],outertitle="Btag Multiplicities:  ",slice="True")
          
          #Simplified plots
          self.Alpha_Webpage(self.binning,plotnames,link="Zero",outertitle="HT Bins:  ",simplified = "True")
          self.Alpha_Webpage(self.btag_slices,plotnames,link=self.binning[0],outertitle="Btag Multiplicities:  ",slice="True",simplified = "True")

          #Stacked plots
          self.Alpha_Webpage(self.binning,plotnames,link="Zero",outertitle="HT Bins:  ",stacked = "True")
          self.Alpha_Webpage(self.btag_slices,plotnames,link=self.binning[0],outertitle="Btag Multiplicities:  ",slice="True",stacked = "True")

      def Alpha_Webpage(self,outer,inner,link="",outertitle="",slice="",simplified="",stacked=""):
 
        for i in outer:
          for j in inner:
            counter = 0
            if simplified:htF = open('/Users/chrislucas/SUSY/AnalysisCode/Website_Plots/'+self.webdir+'/Simplified_'+j+'_'+i+'.html','w')
            elif stacked: htF = open('/Users/chrislucas/SUSY/AnalysisCode/Website_Plots/'+self.webdir+'/Stacked_'+j+'_'+i+'.html','w')
            else: htF = open('/Users/chrislucas/SUSY/AnalysisCode/Website_Plots/'+self.webdir+'/'+j+'_'+i+'.html','w')
            htF.write('Author: Darren Burton <br> \n')
            htF.write('<script language="Javascript"> \n document.write("Last Modified: " + document.lastModified + ""); \n </script> <br> \n ')
            htF.write('<center>\n <p> \n <font size="5"> '+self.title+' Plots </font>\n </p>\n') 
            htF.write('<font size="3">Results for '+j+'_'+i+' </font><br> \n')
            htF.write('Hist Name: ')
            for k in inner:
              counter += 1
              if simplified: htF.write('<a href=\"Simplified_'+k+'_'+i+'.html\">'+k+'</a>   ')
              elif stacked: htF.write('<a href=\"Stacked_'+k+'_'+i+'.html\">'+k+'</a>   ')
              else: htF.write('<a href=\"'+k+'_'+i+'.html\">'+k+'</a>   ')
              htF.write('    |     ')
              if counter == 4:
                htF.write('<br> \n')
                counter = 0
            htF.write('<br> \n')
            htF.write('<br> \n')
            htF.write(outertitle)
            for k in outer: 
              if simplified:htF.write('<a href=\"Simplified_'+j+'_'+k+'.html\">'+(self.btag_slices[k] if slice else k)+'</a>     /    ')
              elif stacked:htF.write('<a href=\"Stacked_'+j+'_'+k+'.html\">'+(self.btag_slices[k] if slice else k)+'</a>     /    ')
              else:htF.write('<a href=\"'+j+'_'+k+'.html\">'+(self.btag_slices[k] if slice else k)+'</a>     /    ')
            htF.write('<br> \n')
            htF.write('<br> \n')
            if simplified:htF.write('Change Evolution Type: <a href=\"Simplified_'+j+'_'+link+'.html\">'+ ('HT Evolution' if slice else 'Btag Evolution')+'</a>')
            elif stacked:htF.write('Change Evolution Type: <a href=\"Stacked_'+j+'_'+link+'.html\">'+ ('HT Evolution' if slice else 'Btag Evolution')+'</a>')
            else:htF.write('Change Evolution Type: <a href=\"'+j+'_'+link+'.html\">'+ ('HT Evolution' if slice else 'Btag Evolution')+'</a>')
            htF.write('<br> \n')
            htF.write('<br> \n')
            htF.write(' Toggle Full/Basic/Stacked Plots:')
            if simplified:
              htF.write('<a href=\"'+j+'_'+i+'.html\">' + '  Full </a>')
              htF.write('     |     ')
              htF.write('<a href=\"Stacked_'+j+'_'+i+'.html\">' + '   Stacked </a>')
            elif stacked:
              htF.write('<a href=\"'+j+'_'+i+'.html\">' + '   Full </a>')
              htF.write('     |     ')
              htF.write('<a href=\"Simplified_'+j+'_'+i+'.html\">' + '   Simplified </a>')
            else:
              htF.write('<a href=\"Stacked_'+j+'_'+i+'.html\">' + '   Stacked </a>')
              htF.write('     |     ')
              htF.write('<a href=\"Simplified_'+j+'_'+i+'.html\">' + '   Simplified </a>')
            
            htF.write('<br> \n')
            htF.write('<br> \n')
            htF.write(' Return to Home Page:')
            htF.write('<a href=\"../RA1_Website_Plots.html\"> Go </a>')
            htF.write('<br><br>')
            
            btag_array = ['_','_btag_morethanzero_','_btag_morethanone_','_btag_morethantwo_','_btag_morethanthree_','_btag_zero_','_btag_one_','_btag_two_','_btag_three_']
            if "Had" in self.title: 
              for num,entry in enumerate(btag_array): btag_array[num] = (entry.rstrip('_'))
              for num,entry in enumerate(self.btag_names): 
                self.btag_names[entry] = self.btag_names[entry].rstrip('_')
                if num == 0: self.btag_names[entry] = ""
            for root,dirs,files in os.walk('/Users/chrislucas/SUSY/AnalysisCode/Website_Plots/'+self.webdir):
              sorter = []
              test_sorter = []
              if not slice:
                for multi in btag_array:
                  for label in self.jet_cats:
                    if not stacked:
                      for filenames in fnmatch.filter(files,('Simplified_'+j.strip('all')+label+multi+self.category+'_'+i+'*.png' if simplified == "True" else j.strip('all')+label+multi+self.category+'_'+i+'*.png')):
                        sorter.append(filenames)
                    else:
                      for filenames in fnmatch.filter(files,'Stacked_'+j.strip('all')+label+multi+self.category+'_'+i+'*.png'):
                        sorter.append(filenames)
              else:
                for bin in self.binning:
                  for label in self.jet_cats:
                    if not stacked:
                      # print j,label
                      # print j.strip('all')+label+self.btag_names[i]+'_'+bin+'*.png' 
                      for filenames in fnmatch.filter(files,('Simplified_'+j.strip('all')+label+self.btag_names[i]+'_'+bin+'*.png' if simplified == "True" else j.strip('all')+label+self.btag_names[i]+'_'+bin+'*.png')):
                        sorter.append(filenames)
                    else:
                      for filenames in fnmatch.filter(files,'Stacked_'+j.strip('all')+label+self.btag_names[i]+'_'+bin+'.png'):
                        sorter.append(filenames)
              for plot in sorter:
                htF.write('<a href='+plot+'><img width=\"30%\" src=\"'+plot+'\"></a> \n')
                if "_all" in plot:
                  htF.write("<br />")


