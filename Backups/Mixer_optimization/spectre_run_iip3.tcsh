#tcsh
source ~/.cshrc
cd /home/ee18b064/cadence_project/Double_Balanced_Mixer/non_ideal/hb_manual_sweep_diff
spectre circ_iip3.scs =log display_iip3.log +diagnose
exit