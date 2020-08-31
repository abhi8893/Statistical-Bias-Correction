library(downscaleR)
library(loadeR)
library(loadeR.2nc)

# files <- vector(mode="list", length=3)
# names(files) <- c("tmean", "tmax", "tmin")
#
# for (i in c(1, 2, 3)){
# 	files[[i]] <-  vector(mode="list", length=2)
# 	names(files[[i]]) <- c("name", "varname")
#
# 	files[[i]]$name <- vector(mod="list", length=2)
# 	names(file[[i]]$name) <- c("obs", "mod")
#
# 	files[[i]]$varname <- vector(mod="list", length=2)
# 	names(file[[i]]$varname) <- c("obs", "mod")
#
# }
#
# files$tmean$name$obs <- "1971-2000_rm_ll25.nc"
# files$tmean$name$mod <- "tmean_base_rm25.nc"
#
# files$tmax$name$obs <- "1971-2000_rm_ll25.nc"
# files$tmax$name$mod <- "tmax_base_rm25.nc"
#
# files$tmin$name$obs <- "1971-2000_rm_ll25.nc"
# files$tmin$name$mod <- "tmin_base_rm25.nc"
#
# files$tmean$varname$obs <- "t"
# files$tmean$varname$mod <- "temp"
#
# files$tmax$varname$obs <- "t"
# files$tmax$varname$mod <- "temp"
#
# files$tmin$varname$obs <- "t"
# files$tmin$varname$mod <- "temp"


for (var in c("tmean", "tmax", "tmin")){
    obs_path <- paste0("/home/abhi/Documents/data/OBSERVATION/IMD/",var,
	                   "/","1971-2000_rm_ll25.nc")

	mod_path <- paste0("/home/abhi/Documents/data/PRECIS/base/",
	                   var,"/",var,"_base_rm25.nc")

	obs <- loadGridData(obs_path, var="t", years = 1971:2000)
	mod <- loadGridData(mod_path, var="temp", years = 1971:2000)

	setwd(paste0("/home/abhi/Documents/mygit/BC/output/",var,"/mw30-15"))

	for (type in c("delta", "scaling", "variance", "eqm")){

		if (type == "scaling"){

			for (scaltype in c("additive", "multiplicative")){

				mod.BC <- biasCorrection(obs, mod, mod,
										 window=c(30, 15),
										 method=type, scaling.type=scaltype,
										 precipitation=FALSE)

				grid2nc(mod.BC, paste0(type,"-",scaltype, ".nc"), compression=NA)
				rm(mod.BC)
				gc()
			}

		} else {

			mod.BC <- biasCorrection(obs, mod, mod,
				                     window=c(30, 15), method=type,
									 precipitation=FALSE)

			grid2nc(mod.BC, paste0(type,".nc"), compression=NA)
			rm(mod.BC)
			gc()

				}
		}

rm(obs, mod)
gc()
}
