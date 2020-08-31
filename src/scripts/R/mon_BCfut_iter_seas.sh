#!/bin/bash

mod_file="mod_data/Precip_base_rm25.nc"
obs_file="obs_data/imdCAL.nc"
mask_file="maskfile/mask_25.nc"

thresh=1

mkdir -p BC
mkdir -p bias_corrected/future/seasonal/thresh/${thresh}

declare -A dict=( ["eqm"]="BCmethod <- biasCorrection(y = obsData, x = modData, newdata = modData_fut, method = 'eqm', wet.threshold = 1, precipitation = TRUE)"
			  ["gqm"]='BCmethod <- biasCorrection(y = obsData, x = modData, newdata = modData_fut, method = "pqm", fitdistr.args = list(densfun="gamma"), wet.threshold = 1, precipitation = TRUE)'
			  )


mkdir -p bias_corrected/base/seasonal/thresh/${thresh}/

scen_list=("rcp45" "rcp85")


for scen in ${scen_list[@]}; do

	fut_file="fut_data/precip_${scen}_rm25.nc"

	for method in ${!dict[@]}; do

		if [[ "$method" =~ ^("eqm"|"loci"|"ptr"|"scalmul") ]]; then

			sed -i "8s/.*.*/${dict[$method]}/" mon_BCfut.R
			sed -n "8p" mon_BCfut.R

			for seas in {DJF,MAM,JJAS,ON}; do

				cdo -s -O -selseas,${seas} -delete,day=29,30,month=2 ${mod_file} infile_mod.nc
				cdo -s -O -selseas,${seas} -delete,day=29,30,month=2 ${obs_file} infile_obs.nc
				cdo -s -O -selseas,${seas} -delete,day=29,30,month=2 ${fut_file} infile_fut.nc

				Rscript mon_BCfut.R

				echo "Season $seas done!" >> progress.txt

				mv BC/outfile.nc BC/${seas}.nc

				rm infile_mod.nc infile_obs.nc infile_fut.nc

			done

			cdo -s -O -mergetime BC/* bias_corrected/future/seasonal/thresh/${thresh}/${method}_unmasked.nc
			cdo -s -O -add bias_corrected/future/seasonal/thresh/${thresh}/${method}_unmasked.nc ${mask_file} bias_corrected/future/seasonal/thresh/${thresh}/${method}.nc
			rm bias_corrected/future/seasonal/thresh/${thresh}/${method}_unmasked.nc
			rm BC/*

		fi

	done

done
