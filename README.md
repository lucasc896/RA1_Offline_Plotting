Included here is the code I use to produce plots for the RA1 Analysis.

The Photon/Had/Muon/DiMuon Plot_Producer.py contain the config file which is passed to Btag_8TeV_Plots.py

Btag_8TeV_Plots.py contains both the plot maker and the webpage maker class. See comments in file to see what is going on.


Setup:

git clone <repo url>
mkdir Website_Plots
cp RA1_Offline_Plotting/*png Website_Plots/.
cp RA1_Offline_Plotting/*gif Website_Plots/.
cp RA1_Offline_Plotting/WebsiteMaker.py Website_Plots/.
cd RA1_Offline_Plotting
ln -s ../RA1_Offline_Analysis/run_details.py
