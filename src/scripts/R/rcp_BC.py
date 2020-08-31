from cdo import Cdo
import xarray as xr
import numpy as np
import os
cdo = Cdo()
from collections import OrderedDict

pwd = os.getcwd()
rscript_path = os.path.join(pwd, "src/R/rcp_BC.R")
rscriptpqm_path = os.path.join(pwd, "src/R/rcp_BCpqm.R")
pyscript_path = "/home/abhi/Documents/mygit/misc_scripts/Python/convto360day.py"
junkDir = "/home/abhi/Documents/mygit/BC/output/junk/"

def getPath(var, ):
    '''Function to return the data file path'''

    data_dir = "/home/abhi/Documents/data"
    if var is 'IMD':
        return os.path.join(data_dir, "OBSERVATION", "IMD", "precip", "imdCAL.nc")
    elif var is 'RAW':
        return os.path.join(data_dir, "PRECIS", "base", "precip", "1971-2000_rm_ll25.nc")
    elif var in ['rcp45', 'rcp85']:
        return os.path.join(data_dir, "PRECIS", var, "precip", f"precip_{var}_rm25_filled.nc")

varList = ['IMD', 'RAW', 'rcp45', 'rcp85']
distFileDict = OrderedDict()

# Distribute the grids into multiple parts
# for var in varList:
#     cdo.distgrid("3,3", input=getPath(var),
#                  output=f"/home/abhi/Documents/mygit/BC/output/junk/{var}")


for file in os.listdir(junkDir):
    for var in varList:
        if file.startswith(var):
            try:
                distFileDict[var].append(os.path.join(junkDir, file))
            except KeyError:
                distFileDict[var] = []
                distFileDict[var].append(os.path.join(junkDir, file))


for var, paths in distFileDict.items():
    distFileDict[var].sort(key=lambda x: int(x[-8:-3]))

getOutFilePath = lambda scen, thresh: f"/home/abhi/Documents/mygit/BC/output/precip"+\
                                      f"/mw30-15/{scen}/{thresh}"

for method in ["gamma"]:
    for thresh in [0, 0.01]:
        for scen in ['rcp45', 'rcp85']:
            zippedList = list(zip(distFileDict['IMD'],
                                  distFileDict['RAW'],
                                  distFileDict[scen],
                                  ))

            for imdfile, rawfile, rcpfile in zippedList:
                outfile = os.path.join(getOutFilePath(scen, thresh),
                                       f"{scen}{imdfile[-8:-3]}")
                if method in ["gamma"]:
                    rscript = rscriptpqm_path
                else:
                    rscript = rscript_path

                os.system(f"Rscript {rscript} {thresh} {method} "+\
                          f"{imdfile} {rawfile} {rcpfile} {outfile}")

                outfile_dir = os.path.dirname(outfile)
                outfile_ext = os.path.splitext(outfile)[-1]
                outfile_name = os.path.basename(outfile).replace(outfile_ext, "")

                fixed_outfile = f"{outfile_dir}/{outfile_name}_fixed{outfile_ext}"
                cdo.setctomiss("inf",
                               input=f"-setctomiss,-inf {outfile}",
                               output=fixed_outfile)
                os.rename(fixed_outfile, outfile)


            outfile_parts = f"{getOutFilePath(scen, thresh)}/{scen}*"
            outfile_merged = os.path.join(getOutFilePath(scen, thresh), method)

            cdo.collgrid(input=outfile_parts,
                         output=outfile_merged)

            os.system(f"rm {outfile_parts}")

            os.system(f"python {pyscript_path} {outfile_merged} -o")
