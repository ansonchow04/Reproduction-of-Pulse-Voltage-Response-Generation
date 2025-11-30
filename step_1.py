# step one, 将冗长的原始数据文件中的工步层提取出来，节省后续处理时间

import os
import pandas as pd

# 根据不同的电池型号
cap_mat = '10Ah LMO'
# 文件路径
source_folder = '../RPVGdata/RawData/' + cap_mat + '/'
# 目标路径（需要提前创建！）
save_folder = '../RPVGdata/ProcessingData/step_1_extract workstep sheet/' + cap_mat + '/'
sheet_name = '工步层' # 所有工步层都在1-1文件，不会出现在1-2
xlsx_files = [f for f in os.listdir(source_folder) if f.endswith('.xlsx') and not f.startswith('~$')] # list of all xlsx files in the source folder
xlsx_files_num = len(xlsx_files)

i = 0

for f in xlsx_files:
    i += 1
    print(str(i) + '/' + str(xlsx_files_num) + ' ' + f + ' processing')
    if f.split('_')[8].split('-')[0] == '1':
        # read in and extract
        data = pd.read_excel(source_folder + f, sheet_name=sheet_name)
        # save
        data.to_excel(save_folder + f, index=False)

print('Finished.')
