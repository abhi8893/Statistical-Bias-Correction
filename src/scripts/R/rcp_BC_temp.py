from cdo import Cdo
import xarray as xr
import numpy as np
import os
cdo = Cdo()
from collections import OrderedDict
from sys import argv
from pathlib import Path

variable = argv[1]

pwd = os.getcwd()
rscript_path = os.path.join(pwd, "src/R/rcp_BCtemp.R")

pyscript_path = "/home/abhi/Documents/mygit/misc_scripts/Python/convto360day.py"
junkDir = f"/home/abhi/Documents/mygit/BC/output/junk/{variable}/"

def getPath(var, variable):
    '''Function to return the data file path'''

    data_dir = "/home/abhi/Documents/data"
    if var is 'IMD':
        return os.path.join(data_dir, "OBSERVATION", "IMD", variable,
                            "1971-2000_rm_ll25_360day.nc")
    elif var is 'RAW':
        return os.path.join(data_dir, "PRECIS", "base", variable,
                            "1971-2000_rm_ll25.nc")
    elif var in ['rcp45', 'rcp85']:
        return os.path.join(data_dir, "PRECIS", var, variable, "2021-2090_rm_ll25_filled.nc")

varList = ['IMD', 'RAW', 'rcp45', 'rcp85']
distFileDict = OrderedDict()

# Distribute the grids into multiple parts
for var in varList:
    cdo.distgrid("3,3", input=getPath(var, variable),
                 output=f"/home/abhi/Documents/mygit/BC/output/junk/{variable}/{var}")


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

getOutFilePath = lambda scen, variable: f"/home/abhi/Documents/mygit/BC/output/{variable}"+\
                                      f"/mw30-15/{scen}"

for method in ["eqm", "variance",
               "scaling"]:
    for scen in ['rcp85']:

        if not Path(f'/home/abhi/Documents/mygit/BC/output/{variable}/mw30-15/{scen}/{method}').exists():
            zippedList = list(zip(distFileDict['IMD'],
                                  distFileDict['RAW'],
                                  distFileDict[scen],
                                  ))

            for imdfile, rawfile, rcpfile in zippedList:
                outfile = os.path.join(getOutFilePath(scen, variable),
                                       f"{scen}{imdfile[-8:-3]}")

                os.system(f"Rscript {rscript_path} {method} "+\
                          f"{imdfile} {rawfile} {rcpfile} {variable} {outfile}")

                outfile_dir = os.path.dirname(outfile)
                outfile_ext = os.path.splitext(outfile)[-1]
                outfile_name = os.path.basename(outfile).replace(outfile_ext, "")

                fixed_outfile = f"{outfile_dir}/{outfile_name}_fixed{outfile_ext}"
                cdo.setctomiss("inf",
                               input=f"-setctomiss,-inf {outfile}",
                               output=fixed_outfile)
                os.rename(fixed_outfile, outfile)


            outfile_parts = f"{getOutFilePath(scen, variable)}/{scen}*"
            outfile_merged = os.path.join(getOutFilePath(scen, variable), method)

            cdo.collgrid(input=outfile_parts,
                         output=outfile_merged)

            os.system(f"rm {outfile_parts}")

            os.system(f"python {pyscript_path} {outfile_merged} -o")
