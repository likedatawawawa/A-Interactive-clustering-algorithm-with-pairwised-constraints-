import copy
import csv
import heapq
import math
import os
import threading
import time

from sklearn.metrics import adjusted_rand_score
from sklearn.neighbors import NearestNeighbors

from a_DMCons import graph_initialization
from b_ranking_allocation import order_allocation
from c_neighborhood_initialization import neighborhood_initialization
from d_influence_model_propagation import influence_model_propagation
from ensemble.b_construct_query_list import construct_query_list_for_max_uncertain_xi_list
from ensemble.c_iteration_stage_user_vote import iteration_stage_user_vote_thread
from ensemble.c_iteration_stage_user_vote_asy import iteration_stage_user_vote_thread_asy, neighbourhoods_lock

stop_event = threading.Event()

def k_nearest_neighbor_cal(data,k):

    neighbors = NearestNeighbors(n_neighbors=k).fit(data)
    k_nearest_neighbors = neighbors.kneighbors(data, return_distance=False)
    return k_nearest_neighbors

def uncertainty_oneNode(predict_labels, k_nearest_neighbor, k, skeleton, node_id):
    label_dict = {}
    for point in k_nearest_neighbor:
        if predict_labels[point] not in label_dict:
            label_dict[predict_labels[point]] = [point]
        else:
            label_dict[predict_labels[point]].append(point)

    entropy = 0
    for m in label_dict:
        proportion = len(label_dict[m]) / k
        if proportion != 0:
            entropy += proportion * math.log2(proportion)
    entropy = -entropy
    if entropy == -0.0:
        entropy = 0.0

    graph_degree = skeleton.degree[node_id]
    coefficient = min(graph_degree, k) / k

    adjusted_uncertainty = entropy * coefficient
    return adjusted_uncertainty

def uncertainty_cal(predict_labels, k_nearest_neighbors, candidates, k, skeleton):
    uncertainty_dict = dict()
    for candidate in candidates:
        k_nearest_neighbor = k_nearest_neighbors[candidate]
        uncertainty = uncertainty_oneNode(predict_labels, k_nearest_neighbor, k, skeleton, candidate)
        uncertainty_dict[candidate] = uncertainty
    return uncertainty_dict

def first_n_nodes_cal(my_dict,n):
    if n>len(my_dict):
        n=len(my_dict)
    sliced_list=[]

    heap = [(-value, key) for key, value in my_dict.items()]
    heapq.heapify(heap)
    count=0
    for _ in range(n):
        if heap:
            neg_value, key = heapq.heappop(heap)
            value = -neg_value
            if value==0.0:
                break
            sliced_list.append(key)
            del my_dict[key]
            count=count+1
        else:
            break
    remaining_count = n - count
    if remaining_count > 0:
        for i in range(remaining_count):
            first_key, first_value = next(iter(my_dict.items()))
            del my_dict[first_key]
            sliced_list.append(first_key)
            count = count + 1
    return sliced_list, my_dict

def result_to_csv_ACDM_thread(ARI_record, title,output_path):
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



def neighborhood_learning(skeleton, data, predict_labels, neighborhood, k_nearest_neighbors, count, order,real_labels, record, k,users_list,user_locks,min_users_num, max_users_num,max_uncertainty_num,constraints_num,isUpdate):

    candidates = dict()
    for i in range(len(order)):
        candidates[order[i]] = 0
    flag = False
    iter=2

    while True:
        candidates = uncertainty_cal(predict_labels, k_nearest_neighbors, candidates, k, skeleton)
        sliced_list,candidates = first_n_nodes_cal(candidates, max_uncertainty_num)
        query_list_dict = construct_query_list_for_max_uncertain_xi_list(sliced_list, neighborhood,data)
        neighborhood, users_list, count, max_uncertain_xi_list_label_dict,constraints_num = iteration_stage_user_vote_thread(
            sliced_list, query_list_dict, users_list, real_labels, count, neighborhood, min_users_num, max_users_num,user_locks,constraints_num,isUpdate)

        if candidates == dict():
            flag = True

        predict_labels = influence_model_propagation(skeleton,neighborhood)
        ari = adjusted_rand_score(real_labels, predict_labels)
        record.append([{"iter": iter, "interaction": count,"constraints_num":constraints_num, "ari": ari}])
        print("iteration: %d, interaction: %d, queries: %d, ari: %s" % (iter, count, constraints_num, ari))
        iter=iter+1

        if flag == True:
            break
        if ari ==1:
            break

    return record

def neighborhood_learning_asy(skeleton, data, predict_labels, neighborhood, k_nearest_neighbors, count, order,real_labels, record, k,users_list,user_locks,min_users_num, max_users_num,max_uncertainty_num,constraints_num,isUpdate):

    candidates = dict()
    for i in range(len(order)):
        candidates[order[i]] = 0
    flag = False
    iter=2

    def periodic_propagation(interval):
        while not stop_event.is_set():
            time.sleep(interval)

            with neighbourhoods_lock:
                nei_snapshot = copy.deepcopy(neighborhood)

            if len(nei_snapshot) == 0:
                continue

            periodic_predict_labels = influence_model_propagation(skeleton, nei_snapshot)
            periodic_ari = adjusted_rand_score(real_labels, periodic_predict_labels)
            record.append([{"interaction": count, "constraints_num": constraints_num, "ari": periodic_ari}])
            print("[Time Trigger] interaction: %d, constraints_num：%d, ari: %s" % (count, constraints_num, periodic_ari))

            if periodic_ari == 1:
                stop_event.set()

    while True:
        candidates = uncertainty_cal(predict_labels, k_nearest_neighbors, candidates, k, skeleton)
        sliced_list,candidates = first_n_nodes_cal(candidates, max_uncertainty_num)
        query_list_dict = construct_query_list_for_max_uncertain_xi_list(sliced_list, neighborhood,data)

        if candidates == dict():
            flag = True

        prop_thread = threading.Thread(
            target=periodic_propagation,
            args=(0.01,),
            daemon=True
        )
        prop_thread.start()

        neighborhood, users_list, count, label_dict, constraints_num = iteration_stage_user_vote_thread_asy(
            sliced_list,
            query_list_dict,
            users_list,
            real_labels,
            count,
            neighborhood,
            min_users_num,
            max_users_num,
            user_locks,
            constraints_num,
            isUpdate,
            neighbourhoods_lock,
            stop_event=stop_event
        )

        stop_event.set()
        prop_thread.join()

        predict_labels = influence_model_propagation(skeleton, neighborhood)
        ari = adjusted_rand_score(real_labels, predict_labels)

        record.append([{"iter": iter, "interaction": count,"constraints_num":constraints_num, "ari": ari}])
        print("iteration: %d, queries: %d, ari: %s" % (iter, count, ari))
        iter=iter+1

        if flag == True:
            break
        if ari ==1:
            break

        stop_event.clear()

    return record

def ACMC(data, real_labels,k,users_list,user_locks,min_users_num, max_users_num,max_uncertainty_num,isUpdate=True, use_asy=False):

    k_nearest_neighbors = k_nearest_neighbor_cal(data, k)
    skeleton, representative = graph_initialization(data)

    record = [[{"iter": 0, "interaction": 0,"constraints_num":0, "ari": 0}]]
    skeleton, order = order_allocation(skeleton, representative)
    neighborhood,neighborhood_r,neighborhood_r_behind,count,order,users_list,constraints_num=neighborhood_initialization(data, order, representative, real_labels,users_list,user_locks,min_users_num, max_users_num,max_uncertainty_num,isUpdate)
    predict_labels = influence_model_propagation(
        skeleton,
        neighborhood,
    )
    ari=adjusted_rand_score(real_labels, predict_labels)
    record.append([{"iter": 1, "interaction": count,"constraints_num":constraints_num, "ari": ari}])
    print("iteration: %d, queries: %d, ari: %s" % (1, count, ari))

    if use_asy:
        stop_event.clear()
        record = neighborhood_learning_asy(
            skeleton, data, predict_labels, neighborhood, k_nearest_neighbors, count, order,
            real_labels, record, k, users_list, user_locks, min_users_num, max_users_num,
            max_uncertainty_num, constraints_num, isUpdate
        )
    else:
        record = neighborhood_learning(
            skeleton, data, predict_labels, neighborhood, k_nearest_neighbors, count, order,
            real_labels, record, k, users_list, user_locks, min_users_num, max_users_num,
            max_uncertainty_num, constraints_num, isUpdate
        )
    return record
