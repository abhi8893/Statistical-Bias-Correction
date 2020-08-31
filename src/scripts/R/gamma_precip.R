library(downscaleR)
library(loadeR)
library(loadeR.2nc)

obs <- loadGridData('/home/abhi/Documents/data/OBSERVATION/IMD/precip/imdCAL.nc', 'precip')
mod <- loadGridData('/home/abhi/Documents/data/PRECIS/base/precip/1971-2000_rm_ll25.nc', 'precip')

for (thresh in c(0.01)){
  setwd(paste0("/home/abhi/Documents/mygit/BC/output/precip/",thresh,"_mw30-15/base/mme"))

  mod.BC <- biasCorrection(obs, mod, mod, precipitation = TRUE, method="pqm",
			   fitdistr.args=list(densfun="gamma"),
                           window=c(30, 15), wet.threshold=thresh)
  grid2nc(mod.BC, 'gamma.nc', compression=NA)
  rm(mod.BC)
  gc()
}
