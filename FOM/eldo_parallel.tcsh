#!/bin/tcsh -f
cd /home/ee18b064/Eldo_files
source sour
setenv LANG en_US
cd /home/ee18b064/Eldo_files/CGA_CurrentMirror_1_With_parasitics-parallel/default
eldo -silent CGA_CurrentMirror_1_With_parasitics-parallel_default_default.cir
exit
