import csv
import math
import os
import time
import threading

import numpy as np
import random

from ensemble.user import get_error_rate_list, create_some_users
from e_neighborhood_learning import ACMC

from sklearn.preprocessing import LabelEncoder
def get_data_from_datasets(file_path):
    true_label = []
    data_matrix = []

    with open(file_path, 'r') as file:
        for line in file:
            line_data = line.strip().split(',')
            row_data = np.array([float(x) for x in line_data[:-1]])
            data_matrix.append(row_data)
            label = line_data[-1].strip()
            true_label.append(label)

    data_matrix = np.array(data_matrix)
    encoder = LabelEncoder()
    true_label = encoder.fit_transform(true_label)

    return data_matrix, true_label





def data_preprocess(data):
    size=np.shape(data)
    random_matrix=np.random.rand(size[0],size[1]) * 0.000001
    data=data+random_matrix
    return data


def record_run_time(time, dataset_name, output_path):
    wirte_path=os.path.join(output_path,'time')
    os.makedirs(wirte_path, exist_ok=True)
    output_file=os.path.join(wirte_path, f'{dataset_name}_runtime.csv')
    with open(output_file,'a') as file:
        file.write(f"{time}\n")
    return 0

def result_to_csv_ACMC(ARI_record, title,output_path):
    os.makedirs(output_path, exist_ok=True)
    
    fullpath = os.path.join(output_path, f'{title}_result.csv')
    with open(fullpath, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        writer.writerow(['interaction','constraints_num', 'ari'])
        
        for record_group in ARI_record:
            for record in record_group:
                interaction = record.get('interaction', None)
                constraints_num=record.get('constraints_num', None)
                ari = record.get('ari', None)
                writer.writerow([interaction,constraints_num, ari])
    return 0

def cul_uncertainty_num(value,base,alpha):
    num=math.ceil(alpha*math.log(value, base))
    return num

def run_ACMC(output_path, algo_name, dataset_source, repetitions_times, error_span, min_users_n, max_users_n, isUpdate=True, use_asy=False):
    print('----------ACMC------')


    datasets_root = os.path.join("datasets", dataset_source)
    datasets = [
        (os.path.splitext(f)[0], f)
        for f in os.listdir(datasets_root)
        if f.endswith(".csv") or f.endswith(".data") or f.endswith(".txt")
    ]
    print(f"共检测到 {len(datasets)} 个数据集： {[d[0] for d in datasets]}")


    output_path = os.path.join(output_path, '26_07_02', dataset_source)
    os.makedirs(output_path, exist_ok=True)


    for dataset_name, file_name in datasets:
        datasets_path = os.path.join(datasets_root, file_name)
        title = dataset_name
        print(f"\n========== 开始运行数据集：{title} ==========")
        print(f"路径：{datasets_path}")
        data, real_labels = get_data_from_datasets(datasets_path)
        data = data_preprocess(data)
        k = 24
        beta = cul_uncertainty_num(data.shape[0], 2, 1)
        usernum = beta

        print(f'k={k}, isUpdate={isUpdate}, max_uncertainty_num={beta}, usernum={usernum}, min_users_n={min_users_n}, max_users_n={max_users_n}')

        error_rate_list = get_error_rate_list(usernum, error_span)
        min_users_num, max_users_num = min_users_n, max_users_n

        temp_output_path = os.path.join(
            output_path,
            f'{title}_error={error_rate_list[0]}_{error_rate_list[-1]}_users={min_users_num}_{max_users_num}'
        )

        users_list = create_some_users(usernum, error_rate_list, 1)
        user_locks = {user: threading.Lock() for user in users_list}

        for re_times in range(repetitions_times):
            print(f'\n第 {re_times + 1} 次运行 {title}')
            final_path = os.path.join(temp_output_path, f'{re_times + 1}')
            os.makedirs(final_path, exist_ok=True)

            start_time = time.time()

            seed = 20 + re_times
            np.random.seed(seed)
            random.seed(seed)


            ARI_record = ACMC(
                data, real_labels, k, users_list, user_locks, min_users_num, max_users_num, beta,
                isUpdate=isUpdate, use_asy=use_asy
            )


            end_time = time.time()

            print(f'耗时：{end_time - start_time:.3f}s')
            print(f'最终 ARI = {ARI_record[-1]}')

            record_run_time(end_time - start_time, title, temp_output_path)
            result_to_csv_ACMC(ARI_record, title, final_path)

        print(f'数据集 {title} 完成')


    print('\n全部数据集运行完成')
    return 0

if __name__ == '__main__':
    output_path= 'result/'

    start_time = time.time()
    dataset_source, repetitions_times='banknote',1

    run_ACMC(output_path, 'ACMC', dataset_source, repetitions_times
                    , error_span=0.00, min_users_n=1, max_users_n=1, isUpdate=True, use_asy=False)
