import os
import pandas as pd

cap_mat = '10Ah LMO'
mat_inf = 'LMO_10Ah_W_'

source_folder = '../PVRGdata/ProcessingData/step_2_feature extraction_adjustable/' + cap_mat + '/'
save_folder = '../PVRGdata/ProcessedData/' + cap_mat + '/'

soc_to_extract = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
pt_to_extract = [5]
U_to_extract = range(1, 21+1)
    # U1：十分钟静置后的稳态开路电压（OCV）
    # U2-U9：0.5C正脉冲、静置、0.5C负脉冲、静置的起始和结束电压
    # U10-U17：1C。 # U18-U21：1.5C正脉冲和静置

xlsx_files = [f for f in os.listdir(source_folder) if f.endswith('.xlsx') and not f.startswith('~$')]
xlsx_files_num = len(xlsx_files)

item = ['File_Name', 'Mat', 'No.', 'ID', 'Qn', 'Q', 'SOH', 'Pt', 'SOC', 'SOCR'] + ['U' + str(i) for i in U_to_extract]

sheet_num = len(soc_to_extract) + 1

for pt_num in pt_to_extract:
    pt_ith = pt_to_extract.index(pt_num)
    print(str(pt_ith + 1) + '/' + str(len(pt_to_extract)) + ' pulse time ' + str(pt_num) + 's proccessing...')
    data = [[] for _ in range(sheet_num)]
    i = 0

    for f in xlsx_files:
        i += 1
        print(str(pt_ith+1) + '/' + str(len(pt_to_extract)) + ' pulse time ' + str(pt_num) + 's ' + str(i) + '/' + str(xlsx_files_num) + ' ' + f + ' processing')
        df = pd.read_excel(source_folder + f).values

        for row_ith in range(0, df.shape[0]):
            if float(df[row_ith][7] == float(pt_num)):
                data[0].append(list(df[row_ith]))
                data[soc_to_extract.index(df[row_ith][8]) + 1].append(list(df[row_ith]))

    save_file_name = mat_inf + str(int(pt_num * 1000)) + '.xlsx'

    with pd.ExcelWriter(save_folder + save_file_name) as writer:
        save_data = pd.DataFrame(data[0])
        save_data.to_excel(writer, sheet_name='All_SOC', index=False, header=item)

        for soc_num in soc_to_extract:
            soc_ith = soc_to_extract.index(soc_num)

            if not data[soc_ith+1]:
                data[soc_ith+1].append([None]*len(item))
            save_data = pd.DataFrame(data[soc_ith+1])
            save_data.to_excel(writer, sheet_name='SOC'+str(soc_num), index=False, header=item)

print('Finished.')