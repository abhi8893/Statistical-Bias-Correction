library(downscaleR)
library(loadeR)
library(loadeR.2nc)

args <- commandArgs()
args <- args[6:length(args)]

e <- list()
e[c( "method", "imdfile" ,"rawfile" ,"rcpfile" ,"variable" ,"outfile")] <- args
list2env(e, envir = parent.frame())

obs <- loadGridData(imdfile, variable)
mod <- loadGridData(rawfile, variable)
mod.rcp <- loadGridData(rcpfile, variable, years=2021:2090)

if (method != "scaling"){
  mod.bc <- biasCorrection(obs, mod, mod.rcp, method=method, 
                          precipitation = FALSE,
                          window = c(30, 15))
} else {
  mod.bc <- biasCorrection(obs, mod, mod.rcp, method=method,
                           scaling.type = "additive",
                           precipitation = FALSE,
                           window = c(30, 15))
}
  

grid2nc(mod.bc, outfile, compression = NA)
