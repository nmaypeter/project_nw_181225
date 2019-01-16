from Diffusion_NormalIC import *


class SeedSelectionR:
    def __init__(self, g_dict, s_c_dict, prod_list, total_bud, pps, wpiwp):
        ### g_dict: (dict) the graph
        ### g_dict[node1]: (dict) the set of node1's receivers
        ### g_dict[node1][node2]: (float2) the weight one the edge of node1 to node2
        ### s_c_dict: (dict) the set of cost for seeds
        ### s_c_dict[ii]: (dict) the degree of ii's seed
        ### prod_list: (list) the set to record products
        ### prod_list[kk]: (list) [kk's profit, kk's cost, kk's price]
        ### prod_list[kk][]: (float2)
        ### total_bud: (int) the budget to select seed
        ### num_node: (int) the number of nodes
        ### num_product: (int) the kinds of products
        ### pps: (int) the strategy to update personal prob.
        ### wpiwp: (bool) whether passing the information without purchasing
        self.graph_dict = g_dict
        self.seed_cost_dict = s_c_dict
        self.product_list = prod_list
        self.total_budget = total_bud
        self.num_node = len(s_c_dict)
        self.num_product = len(prod_list)
        self.pps = pps
        self.wpiwp = wpiwp

    def selectRandomSeed(self, nb_set):
        # -- select a seed for a random product randomly
        ### product_num: (list) record the product number with possible seeds
        product_num = [k for k in range(self.num_product)]
        k_prod, i_node = -1, '-1'
        while k_prod == -1:
            k_prod = choice(product_num)
            if len(nb_set[k_prod]) == 0:
                product_num.remove(k_prod)
                k_prod = -1
            if len(product_num) == 0:
                return k_prod, i_node
        i_node = choice(list(nb_set[k_prod]))

        return k_prod, i_node

    def updateNotbanSet(self, nb_set, cur_bud):
        # -- remove the impossible seeds --
        b_set = [set() for _ in range(self.num_product)]
        for k in range(self.num_product):
            for i in nb_set[k]:
                # -- the cost of seed cannot exceed the budget --
                if self.seed_cost_dict[i] + cur_bud > self.total_budget:
                    b_set[k].add(i)

        # -- remove the impossible seeds fom nban_set
        for k in range(self.num_product):
            for i in b_set[k]:
                if i in nb_set[k]:
                    nb_set[k].remove(i)
        return nb_set


if __name__ == "__main__":
    ### whether_passing_information_without_purchasing: (bool) whether passing the information without purchasing
    data_set_name = "email_undirected"
    product_name = "r1p3n1"
    total_budget = 1
    pp_strategy = 2
    whether_passing_information_without_purchasing = bool(0)

    iniG = IniGraph(data_set_name)
    iniP = IniProduct(product_name)

    seed_cost_dict = iniG.constructSeedCostDict()[1]
    graph_dict = iniG.constructGraphDict()
    ### product_list: (list) [profit, cost, price]
    product_list = iniP.getProductList()[0]
    ### wallet_list: (list) the list of node's personal budget (wallet)
    ### wallet_list[ii]: (float2) the ii's wallet
    wallet_list = iniG.getWalletList(product_name)
    num_node = len(seed_cost_dict)
    num_product = len(product_list)

    # -- initialization for each budget --
    start_time = time.time()

    ssr = SeedSelectionR(graph_dict, seed_cost_dict, product_list, total_budget, pp_strategy, whether_passing_information_without_purchasing)
    dnic = DiffusionNormalIC(graph_dict, seed_cost_dict, product_list, pp_strategy, whether_passing_information_without_purchasing)

    notban_set = [{ii for ii in graph_dict} for _ in range(num_product)]
    notban_set = ssr.updateNotbanSet(notban_set, 0)

    ### result: (list) [profit, budget, seed number per product, customer number per product, seed set] in this execution_time
    result = []
    ### avg_profit, avg_budget: (float) the average profit and budget per execution_time
    ### avg_num_k_seed: (list) the list to record the average number of seed for products per execution_time
    ### avg_num_k_seed[kk]: (int) the average number of seed for kk-product per execution_time
    ### avg_num_k_an: (list) the list to record the average number of activated node for products per execution_time
    ### avg_num_k_an[kk]: (int) the average number of activated node for kk-product per execution_time
    avg_profit, avg_budget = 0.0, 0.0
    avg_num_k_seed, avg_num_k_an = [0 for _ in range(num_product)], [0 for _ in range(num_product)]
    ### pro_k_list, bud_k_list: (list) the list to record profit and budget for products
    ### pro_k_list[kk], bud_k_list[kk]: (float) the list to record profit and budget for kk-product
    pro_k_list, bud_k_list = [0.0 for _ in range(num_product)], [0.0 for _ in range(num_product)]

    # -- initialization for each sample_number --
    ### now_profit, now_budget: (float) the profit and budget in this execution_time
    now_profit, now_budget = 0.0, 0.0
    ### seed_set: (list) the seed set
    ### seed_set[kk]: (set) the seed set for kk-product
    ### activated_node_set: (list) the activated node set
    ### activated_node_set[kk]: (set) the activated node set for kk-product
    seed_set, activated_node_set = [set() for _ in range(num_product)], [set() for _ in range(num_product)]
    ### activated_edge_set: (list) the activated edge set
    ### activated_edge_set[kk]: (dict) the activated edge set for kk-product
    ### activated_edge_set[kk][node1]: (set) the activated edge set of node1 for kk-product
    activated_edge_set = [{} for _ in range(num_product)]
    ### personal_prob_list: (list) the list of personal prob. for all combinations of nodes and products
    ### personal_prob_list[kk]: (list) the list of personal prob. for kk-product
    ### personal_prob_list[kk][ii]: (float2) the personal prob. for ii-node for kk-product
    personal_prob_list = [[1.0 for _ in range(num_node)] for _ in range(num_product)]

    current_wallet_list = copy.deepcopy(wallet_list)
    nban_set = copy.deepcopy(notban_set)
    for ii in range(num_node):
        personal_prob_list = dnic.updatePersonalProbList(-1, str(ii), current_wallet_list, personal_prob_list)

    ### an_promote_list: (list) to record the seed activate customer event for a product
    an_promote_list = []

    mep_k_prod, mep_i_node = ssr.selectRandomSeed(nban_set)

    # -- main --
    while now_budget < total_budget and mep_i_node != '-1':
        for kk in range(num_product):
            if mep_i_node in nban_set[kk]:
                nban_set[kk].remove(mep_i_node)
        seed_set, activated_node_set, activated_edge_set, an_number, current_profit, current_wallet_list, personal_prob_list = \
            dnic.insertSeedIntoSeedSet(mep_k_prod, mep_i_node, seed_set, activated_node_set, activated_edge_set, current_wallet_list, personal_prob_list)

        pro_k_list[mep_k_prod] += round(current_profit, 4)
        bud_k_list[mep_k_prod] += seed_cost_dict[mep_i_node]
        now_profit += round(current_profit, 4)
        now_budget += seed_cost_dict[mep_i_node]
        an_promote_list.append([mep_k_prod, mep_i_node, an_number, round(current_profit, 4), seed_cost_dict[mep_i_node], iniG.getNodeOutDegree(mep_i_node)])

        nban_set = ssr.updateNotbanSet(nban_set, now_budget)
        mep_k_prod, mep_i_node = ssr.selectRandomSeed(nban_set)

    # -- result --
    now_num_k_seed, now_num_k_an = [len(kk) for kk in seed_set], [len(kk) for kk in activated_node_set]
    result.append([round(now_profit, 4), round(now_budget, 4), now_num_k_seed, now_num_k_an, seed_set])
    avg_profit += now_profit
    avg_budget += now_budget
    for kk in range(num_product):
        avg_num_k_seed[kk] += now_num_k_seed[kk]
        avg_num_k_an[kk] += now_num_k_an[kk]
        pro_k_list[kk], bud_k_list[kk] = round(pro_k_list[kk], 4), round(bud_k_list[kk], 4)
    how_long = round(time.time() - start_time, 2)
    print("result")
    print(result)
    print("\nan_promote_list (#product, #node, num_an, profit, cost, degree)")
    print(an_promote_list)
    print("\npro_k_list, bud_k_list")
    print(pro_k_list, bud_k_list)
    print("total time: " + str(how_long) + "sec")
