import heapq



alpha = 0.5


def centrality_ranking(G,start_node):

    degrees = dict(G.degree())
    max_degree = max(degrees.values()) if degrees else 1

    traversed_nodes = [start_node]
    candidate_edges = []


    for u, v, data in G.edges(start_node, data=True):
        combined_weight = data['weight'] + (degrees[v] / max_degree)
        heapq.heappush(candidate_edges, (-combined_weight, u, v))
    while candidate_edges:
        neg_weight, current_node, new_node = heapq.heappop(candidate_edges)
        if new_node not in traversed_nodes:
            traversed_nodes.append(new_node)

            for _, neighbor, data in G.edges(new_node, data=True):
                if neighbor != current_node:
                    neighbor_degree = degrees[neighbor]
                    new_combined_weight = alpha * data['weight'] + (1 - alpha) * (neighbor_degree / max_degree)
                    heapq.heappush(candidate_edges, (-new_combined_weight, new_node, neighbor))

    return traversed_nodes

def order_allocation(skeleton, representative):
    decision_list = centrality_ranking(skeleton, start_node=representative)
    for i in range(len(decision_list)):
        skeleton.nodes[decision_list[i]]['ranking'] = i
    return skeleton, decision_list
