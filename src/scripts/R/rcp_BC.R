library(downscaleR)
library(loadeR)
library(loadeR.2nc)

args <- commandArgs()
args <- args[6:length(args)]

e <- list()
e[c("thresh" ,"method", "imdfile" ,"rawfile" ,"rcpfile" ,"outfile")] <- args
list2env(e, envir = parent.frame())

obs <- loadGridData(imdfile, 'precip')
mod <- loadGridData(rawfile, 'precip')
mod.rcp <- loadGridData(rcpfile, 'precip', years=2021:2090)

mod.bc <- biasCorrection(obs, mod, mod.rcp, method=method, 
                          wet.threshold = thresh,
                          precipitation = TRUE,
                          window = c(30, 15))

grid2nc(mod.bc, outfile, compression = NA)
