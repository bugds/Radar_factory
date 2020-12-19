import pandas as pd

df = pd.read_csv('NHANES_full.csv')

#############################
# FINDING COLUMNS W/STRINGS #
#############################

for c in df.columns:
    df[c] = pd.to_numeric(df[c], errors='coerce')
    print(c + ': ' + str(df[c].isna().sum()))

# Results:
# Respondent: 0
# Gender: 0
# Age_years: 0
# Age_months: 28074
# Pregnancy: 51439
# WBC: 4124
# LymN: 4288
# MonN: 4288
# NeuN: 4288
# EosN: 4288
# BasN: 4288
# RBC: 4123
# HGB: 4123
# HCT: 4123
# MCV: 4123
# MCH: 4123
# MCHC: 4103
# RDW: 4123
# PltN: 4124
# MPV: 4124
# RetN: 63079
# Albumin_SI: 5158
# ALT_SI: 5261
# AST_SI: 5286
# UreaNitr_SI: 5166
# Ca_SI: 5207
# Chol_SI: 5167
# Bicarbon: 5250
# GGT_SI: 5169
# Gluc_SI: 5161
# Fe_SI: 5215
# P_SI: 5170
# Bilirub_SI: 5192
# Protein_SI: 5222
# Triglyc_SI: 5189
# UricAcid_SI: 5174
# Creatinine_SI: 5162
# Na_SI: 5163
# K_SI: 5172
# Cl_SI: 5170
# Osm_SI: 5169
# Globulin_SI: 5223

# Remove Age in months;
# Pregnancy - to 2 - not pregnant. Others: 1 - pregnancy; 3 - not sure (remove);
# Remove RetN.

###################
# DATA REFINEMENT #
###################

df = df.drop(columns='Age_months')
df = df.drop(columns='RetN')
df['Pregnancy'] = df['Pregnancy'].fillna(2)
df = df[df['Pregnancy'] != 3]
df = df.dropna()
df.to_csv('NHANES_refined.csv')

######################
# PAIRWISE DISTANCES #
######################

from scipy.spatial.distance import pdist
from scipy.spatial.distance import squareform
pairwise = pd.DataFrame(
    squareform(pdist(df)),
    columns = df.index,
    index = df.index
)
