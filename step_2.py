# 原始的文件里，详细记录了每个电池在不同 SOC 
# 该脚本的目的是从这些数据中提取特征，以便后续的模型训练使用。
# 提取的特征包括：
# - 基本信息：文件名、材料类型、电池编号、ID、额定容量、实际容量、健康状态
# - 脉冲参数：脉冲时间、理论状态、实际状态
# - 电压特征：U1-U21，对应不同脉冲条件下的电压响应



import os
import pandas as pd


cap_mat = '10Ah LMO'
source_folder = '../PVRGdata/ProcessingData/step_1_extract workstep sheet/' + cap_mat + '/'
save_folder = '../PVRGdata/ProcessingData/step_2_feature extraction_adjustable/' + cap_mat + '/'

soc_to_extract = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50] # 使用 {5, 10, ..., 50}，因为 SOH 较低的电池可能不会在 55% 或更高 SOC 下测试。
pt_to_extract = [5]  # 在论文中：5s
U_to_extract = range(1, 21 + 1) # 在论文中：U1-U21
                                # U1：稳态开路电压（OCV），在静置 10 分钟后的电压
                                # U2-U9：0.5C 正脉冲开始/结束电压，静置，0.5C 负脉冲开始/结束电压，静置。
                                # U10-U17：1C；U18-U25：1.5C；U26-U33：2C；U34-U41：2.5C。

print(soc_to_extract, pt_to_extract, list(U_to_extract))

xlsx_files = [f for f in os.listdir(source_folder) if f.endswith('.xlsx') and not f.startswith('~$')]
xlsx_file_num = len(xlsx_files)

i = 0

item = ['File_Name','Mat','No.','ID','Qn','Q','SOH','Pt','SOC','SOCR'] + ['U' + str(i) for i in U_to_extract]
# filename: 文件名
# Mat: 电池材料
# No.: 电池编号
# ID: 电池ID
# Qn: 额定容量
# Q: 实际容量
# SOH: 健康状态
# Pt: 脉冲时间
# SOC: 理论状态
# SOCR: 实际状态
# U1-U21: 电压特征

for f in xlsx_files:
    i = i + 1
    print(str(i) + '/' + str(xlsx_file_num) + ' ' + f + ' processing')

    # 读取数据，转换为 numpy 数组
    df = pd.read_excel(source_folder + f).values

    # 初始化特征列表，长度与 item 相同，初始值为 None
    ft = [None] * len(item)

    # 提取基本信息
    ft[0] = f                                   # 文件名
    ft[1] = f.split('_')[0]                     # 材料 Mat
    ft[2] = int(f.split('_')[4])                # 编号 No.
    ft[3] = f.split('_')[10].split('.xlsx')[0]  # ID
    ft[4] = int(f.split('_')[2])                # 额定容量 Qn
    Q = - df[3][16]                             # 表格中为第一次CCCV充电量
    ft[5] = Q                                   # 实际容量 Q
    ft[6] = Q/ft[4]                             # 健康状态 SOH=Q/Qn

    # 初始化数据列表
    data = []

    # 特征提取
    for soc_num in soc_to_extract:
        soc_ith = int(soc_num/5 -1) # 将SOC值转换成索引

        ft[8] = soc_num 

        for pt_num in pt_to_extract:
            pt_ith = [0.03, 0.05, 0.07, 0.1, 0.3, 0.5, 0.7, 1, 3, 5].index(pt_num) # 将脉冲时间转换成索引

            ft[7] = pt_num  # Pt, i.e. pulse time or pulse width.

            soc_row_num = 5-1 + (10*5*4+2)*soc_ith + 2 + 5*4*pt_ith
            # 5-1: 5 steps SOH or Capacity measurement by CCCV charge - CC discharge, -1 due to start from 0 in python
                # rest, CCCV charge, rest, CC discharge, rest
            # 2: 2 steps to condition to assigned SOC
                # CC charge, rest
            # 10: 10 kinds of pulse time or pulse width
            # 5: 5 kinds of pulse current intensity
            # 4: 4 steps per pulse current intensity per pulse width
                # CC charge or positive pulse, rest, CC discharge or negative pulse, rest
            ft[9] = sum(df[5:(soc_row_num+1),18]) / ft[4]    # SOCR, state-of-charge in real at U1.
                # A more accurate value based on accumulated net charged capacity from statistics in the '工步层' or the workstep layer.
            
            ft[10:len(item)] = [None] * (len(item)-10)

            # Ensure that it will not read more than the actual number of rows or steps
            U_row_num_max = 5-1 + (10*5*4+2)*soc_ith + 2 + 5*4*pt_ith + max(U_to_extract) // 2
                # Due to security concern and voltage protection, some batteries failed to complete all planed pulse tests with different pulse current amplitude at same SOC level and with same pulse time.
                # If the experiemnt stop at step i corresponding to U(j) and U(j+1) with certain SOC, pulse time and pulse current amplitude:
                # In this version for adjustability:
                    # If all U(k) in U_to_extract satisfies k <= j+1, all required features in U_to_extract at this SOC, pulse time and pulse current amplitude will be recorded.
                    # If U_to_extract contains U(k) where j+1 < k, all required features in U_to_extract at this SOC, pulse time and pulse current amplitude will NOT be recorded.

            # Ensure that it will not read more than the actual number of rows or steps
            if U_row_num_max < df.shape[0]:
                for U_num in U_to_extract:
                    U_ith = U_to_extract.index(U_num) + 1

                    U_row_num = 5-1 + (10*5*4+2)*soc_ith + 2 + 5*4*pt_ith + U_num // 2
                    # 5-1: 5 steps SOH or Capacity measurement by CCCV charge - CC discharge, -1 due to start from 0 in python
                        # rest, CCCV charge, rest, CC discharge, rest
                    # 2: 2 steps to condition to assigned SOC
                        # CC charge, rest
                    # 10: 10 kinds of pulse time or pulse width
                    # 5: 5 kinds of pulse current intensity
                    # 4: 4 steps per pulse current intensity per pulse width
                        # CC charge or positive pulse, rest, CC discharge or negative pulse, rest
                    ft_ith = 9 + U_ith # ft[0]-ft[9]
                    
                    if U_num == 1:
                        ft[ft_ith] = df[U_row_num][12]  # U1.
                    elif U_num % 2 == 0:
                        ft[ft_ith] = df[U_row_num][10]  # Beginning point: U2, U4, ..., U40.
                    elif U_num % 2 == 1:
                        ft[ft_ith] = df[U_row_num][12]  # End point: U3, U5, ..., U41.
                    
                data.append(list(ft))

    # Save
    save_data = pd.DataFrame(data)
    save_data.to_excel(save_folder + f, index=False, header=item)

# Progress bar
print('Finished.')
