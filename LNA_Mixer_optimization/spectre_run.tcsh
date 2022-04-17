#tcsh
source ~/.cshrc
cd /home/ee18b064/cadence_project/LNA_Mixer/non_ideal/hb_single_pin_diff
spectre circ.scs =log display.log +diagnose
exit