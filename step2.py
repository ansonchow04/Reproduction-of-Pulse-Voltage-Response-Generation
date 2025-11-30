import os
import pandas as pd

cap_mat = '10Ah LMO'
source_folder = '../RPVGdata/ProcessingData/step_1_extract workstep sheet/' + cap_mat + '/'
save_folder = '../RPVGdata/ProcessingData/step_2_feature extraction_adjustable/' + cap_mat + '/'

soc_to_extract = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
pt_to_extract = [5]
U_to_extract = range(1, 21+1)