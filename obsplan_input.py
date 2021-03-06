'''
This file provides an example of how to interact and run obsplan.py

All position angles are defined +CCW from North towards East
'''
from __future__ import division
import numpy
import tools
import obsplan

###########################################################################
## USER INPUT
###########################################################################

## General inputs

#Prefix for all output files
prefix = '/Users/dawson/SkyDrive/Observing/Keck2013a/MACSJ1752/macs1752_Mask1_rev0'
# Hour angle of the target for the mask (float; unit:hours)
HA = -40/60.

## Star and Galaxy catalog inputs

catalog = '/Users/dawson/SkyDrive/Research/Clusters/MACS1752/catalog/macsj1752_sdsscat_shortobjid.txt'
objid_ttype = 'objID'
ra_ttype = 'ra'
dec_ttype = 'dec'
mag_ttype = 'dered_r'
passband = 'R'
equinox = '2000'

# Go ahead and read in the catalog since this will be needed to create the
# galaxy mask later in the user input section
cat = tools.readcatalog(catalog)
key = tools.readheader(catalog)

## Slitmask ds9 region input

# Path/Name of the ds9 region file defining the bound and orientation of the
# slit mask. Note region should be defined using Coordinate/WCS/Degrees and 
# Size/WCS/Arcmin options, with the Size 5 by 16.1 arcmin, Angle will then
# correspond to the slitmask's parallactic angle (i.e. +CCW from north towards
# east) with the guider camera in the North-east quadrent at Angle=0.
regfile = '/Users/dawson/SkyDrive/Observing/Keck2013a/MACSJ1752/mask1_rev0.reg'

## Slit size inputs

#The amount of sky on either side of the galaxy to include in slit (arcsec)
sky = (1.5,1.5)
# The ttype index of the galaxy size. If one value is entered then the galaxy
# will be assumed circular, of three values are entered the the galaxy will be
# assumed elliptical with major axis radius (a), and minor axis radius (b), and
# position angle (pa_gal) of the major axis measured +CCW from North towards
# east
A_gal_ttype = 'deVRad_r'
B_gal_ttype = None # if None then galaxy assumed circular
pa_ga_ttype = None # if None then galaxy assumed circular

## Guide and alignment star inputs

# Enter lists of the object ids for each type of star, these will be matched to
# the object ids in the catalog

# Guide star id's
gs_ids = (775311575)
# Alignment star id's
as_ids = (775311757, 775311662, 530933312, 530868425, 530868397)

## Exclusion list input

# ttype catalog of galaxies to exclude from mask (excludes matching ttype = objid). exobjid_ttype is ['string'] ttype name of the objid column in the exfile, the objid's should correspond to some of the objid's in the objid array

exfile = None
exobjid_ttype = None
#exfile = '/Users/dawson/SkyDrive/Observing/Keck2013a/MACSJ1752/macs1752_Mask1_rev0_maskcat.txt' #a string (e.g. 'exclusion.txt') or None
#exobjid_ttype = 'objID'

## Priority code (i.e. selection weight) input

# Currently obsplan is only setup to calculate an objects priority code based on
# its photo-z relative to the cluster redshift
z_cluster = 0.366
photo_z_ttype = 'z_phot'
photo_z_err_ttype = 'z_phot_Err'

## Create a sample definition

# Currently obsplan is only setup to break samples according to one object
# variable (e.g. magnitude).  The sampel_param_ttype is the ttype name of the 
# vairable in the catalog to be used to make the sample division (e.g. 
# magnitude). samplebounds defines the min and max of sample_param for each
# sample: e.g. (sample1 lowerbound, sample1 upperbound, sample2 lower bound,
# sample2 upper bound, etc., etc.).
sample_param_ttype = 'dered_r'
samplebounds = (0,22.5,22.5,23)

## Preselected list input

# ttype catalog of galaxies to preselect in dsim.
psfile = '/Users/dawson/SkyDrive/Observing/Keck2013a/MACSJ1752/preselect.txt' #a string (e.g. 'preselect.txt') or None
psobjid_ttype = 'objID'

## Create galaxy selection mask

# Some how the user at this point needs to create a boolean type mask for the
# catalog that will filter out all objects that are not galaxies
mask_galaxy = cat[:,key['type']] == 3

## Create a magnitude mask

# It is likely that the a faint end mask should be used
mask_mag = cat[:,key[mag_ttype]] <= 23




###########################################################################
## Automated Portion
###########################################################################

# create basic 1D arrays from catalog
objid = cat[:,key[objid_ttype]]
ra = cat[:,key[ra_ttype]]
dec = cat[:,key[dec_ttype]]
mag = cat[:,key[mag_ttype]]

# Create the slitmask mask
mask_slitmask = obsplan.createSlitmaskMask(regfile,ra,dec)

# Create the exclusion list mask
if exfile == None:
    # then make a numpy.array of just True's
    mask_ex = numpy.ones(numpy.size(objid)) == 1
elif exfile != None and exobjid_ttype != None:
    mask_ex = obsplan.createExclusionMask(objid,exfile,exobjid_ttype)

# Determine the priority_code (i.e. weight) for each galaxy
gal_photoz = cat[:,key[photo_z_ttype]]
photo_z_err = cat[:,key[photo_z_err_ttype]]
priority_code = obsplan.photoz_PriorityCode(z_cluster,gal_photoz,photo_z_err,plot_diag=False)

# Determine the sample for each galaxy (sample 1 objects selected first, then
# sample 2, etc.). This order of selection take priority over the priority_code
param_array = cat[:,key[sample_param_ttype]]
sample = obsplan.assignSample(param_array,samplebounds)

# Determine the selection flag for each galaxy. If non-zero then the object is
# preselected
selectflag = obsplan.assignSelectionFlag(objid,psfile,psobjid_ttype)

# determine object declination and the mask PA from the regfile
box = obsplan.readMaskRegion(regfile)
delta = box[1]
pa_mask = box[4]

# Determine the optimal slit PA
pa_slit = obsplan.optimalPA(pa_mask,HA,delta)

# Determine the slit size for each object
A_gal = cat[:,key[A_gal_ttype]]
if B_gal_ttype == None:
    B_gal = None
else:
    B_gal = cat[:,key[B_gal_ttype]]
if pa_ga_ttype == None:
    pa_gal = None
else:
    pa_gal = cat[:,key[pa_ga_ttype]]
len1, len2 = obsplan.slitsize(pa_slit,sky,A_gal,B_gal,pa_gal)

# Create the output dsim file
outcatname = prefix+'_maskcat.txt'
print 'started to write out to ', outcatname
F = open(outcatname,'w')

# Write the dsim header information to the output file
obsplan.write_dsim_header(F,regfile,prefix)

# Write the guide star info to the dsim output file
obsplan.write_guide_stars(F,gs_ids,objid,ra,dec,mag,equinox,passband)

# Write the alignment star info to the dsim output file
obsplan.write_align_stars(F,as_ids,objid,ra,dec,mag,equinox,passband)

# Filter the galaxy catalog before creating dsim input
mask_temp = mask_galaxy*mask_mag*mask_ex*mask_slitmask
# but need to include any preselected galaxies that might be excluded by the
# above masks
mask = numpy.logical_or(mask_temp,selectflag)

# Write the galaxy info to the desim output file
obsplan.write_galaxies_to_dsim(F,objid[mask],ra[mask],dec[mask],mag[mask],priority_code[mask],sample[mask],selectflag[mask],pa_slit,len1[mask],len2[mask],equinox='2000',passband='R')

# Close the output dsim file
F.close()

# Create the target galaxy slit region file
length = len1+len2
obsplan.makeSlitmaskRegion(prefix,ra[mask],dec[mask],pa_slit,length[mask],sample[mask],width=1)