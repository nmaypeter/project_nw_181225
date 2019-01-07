import copy
import time
from random import choice
from Initialization import *


class DiffusionNormalIC:
    def __init__(self, g_dict, s_c_dict, prod_list, pps, wpiwp):
        ### g_dict: (dict) the graph
        ### g_dict[node1(str)]: (dict) the set of node1's receivers
        ### g_dict[node1(str)][node2(str)]: (float2) the weight one the edge of node1 to node2
        ### s_c_dict: (dict) the set of cost for seeds
        ### s_c_dict[ii(str)]: (dict) the degree of ii's seed
        ### prod_list: (list) the set to record products
        ### prod_list[kk(int)]: (list) [kk's profit, kk's cost, kk's price]
        ### prod_list[kk(int)][]: (float2)
        ### num_node: (int) the number of nodes
        ### num_product: (int) the kinds of products
        ### pp_strategy: (int) the strategy to update personal prob.
        ### wpiwp: (bool) whether passing the information without purchasing
        self.graph_dict = g_dict
        self.seed_cost_dict = s_c_dict
        self.product_list = prod_list
        self.num_node = len(s_c_dict)
        self.num_product = len(prod_list)
        self.pps = pps
        self.wpiwp = wpiwp

    def getPersonalProbList(self, w_list):
        ### pp_list: (list) the list of personal prob. for all combinations of nodes and products
        ### pp_list[k]: (list) the list of personal prob. for k-product
        ### pp_list[k][i]: (float2) the personal prob. for i-node for k-product
        pp_list = [[1.0 for _ in range(self.num_node)] for _ in range(self.num_product)]

        for k in range(self.num_product):
            prod_price = self.product_list[k][2]
            for i in self.seed_cost_dict:
                if w_list[int(i)] == 0:
                    pp_list[k][int(i)] = 0
                else:
                    if self.pps == 1:
                        # -- after buying a product, the prob. to buy another product will decrease randomly --
                        pp_list[k][int(i)] = round(random.uniform(0, pp_list[k][int(i)]), 4)
                    elif self.pps == 2:
                        # -- choose as expensive as possible --
                        pp_list[k][int(i)] *= round((prod_price / w_list[int(i)]), 4)
                    elif self.pps == 3:
                        # -- choose as cheap as possible --
                        pp_list[k][int(i)] *= round(1 - (prod_price / w_list[int(i)]), 4)

        for k in range(self.num_product):
            for i in range(self.num_node):
                if w_list[i] < self.product_list[k][2]:
                    pp_list[k][i] = 0.0

        return pp_list

    def updatePersonalProbList(self, k_prod, i_node, w_list, pp_list):
        prod_price = self.product_list[k_prod][2]
        if self.pps == 1:
            # -- after buying a product, the prob. to buy another product will decrease randomly --
            for k in range(self.num_product):
                if k == k_prod or w_list[int(i_node)] == 0:
                    pp_list[k][int(i_node)] = 0
                else:
                    pp_list[k][int(i_node)] = round(random.uniform(0, pp_list[k][int(i_node)]), 4)
        elif self.pps == 2:
            # -- choose as expensive as possible --
            for k in range(self.num_product):
                if k == k_prod or w_list[int(i_node)] == 0:
                    pp_list[k][int(i_node)] = 0
                else:
                    pp_list[k][int(i_node)] *= round((prod_price / w_list[int(i_node)]), 4)
        elif self.pps == 3:
            # -- choose as cheap as possible --
            for k in range(self.num_product):
                if k == k_prod or w_list[int(i_node)] == 0:
                    pp_list[k][int(i_node)] = 0
                else:
                    pp_list[k][int(i_node)] *= round(1 - (prod_price / w_list[int(i_node)]), 4)

        for k in range(self.num_product):
            for i in range(self.num_node):
                if w_list[i] < self.product_list[k][2]:
                    pp_list[k][i] = 0.0

        return pp_list

    def getSeedExpectProfit(self, k_prod, i_node, s_set, a_n_set_k, a_e_set_k, w_list, pp_list_k):
        # -- calculate the expected profit for single node when it's chosen as a seed --
        ### try_a_n_list: (list) the set to store the nodes may be activated for kk-products
        ### try_a_n_list[][0]: (str) the receiver when ii is ancestor
        ### try_a_n_list[][1]: (float4) the probability to activate the receiver from ii
        ### try_a_n_list[][2]: (float2) the personal probability to activate own self
        ### ep: (float2) the expected profit
        a_n_set_k = copy.deepcopy(a_n_set_k)
        a_n_set_k.add(i_node)
        a_e_set_k = copy.deepcopy(a_e_set_k)
        try_a_n_list = []
        s_total_set = set()
        for k in range(self.num_product):
            s_total_set = s_total_set.union(s_set[k])
        ep = -1 * self.seed_cost_dict[i_node]

        # -- add the receivers of nnode into try_a_n_list --
        # -- notice: prevent the node from owing no receiver --
        if i_node not in self.graph_dict:
            return ep

        outdict = self.graph_dict[i_node]
        for out in outdict:
            if not (out not in a_n_set_k):
                continue
            if not (out not in s_total_set):
                continue
            if not (i_node not in a_e_set_k or out not in a_e_set_k[i_node]):
                continue
            if not (w_list[int(out)] > self.product_list[k_prod][2]):
                continue
            if not (pp_list_k[int(out)] > 0):
                continue
            # -- add the value calculated by activated probability * profit of this product --
            i_prob = float(outdict[out])
            temp_ep = i_prob * pp_list_k[int(out)] * self.product_list[k_prod][0]
            ep += temp_ep
            # -- activate the receivers temporally --
            # -- add the receiver of node into try_a_n_list --
            # -- notice: prevent the node from owing no receiver --
            a_n_set_k.add(out)
            try_a_n_list.append([out, i_prob, i_prob])

        while len(try_a_n_list) > 0:
            ### try_node: (list) the nodes may be activated for kk-products
            try_node = choice(try_a_n_list)
            try_a_n_list.remove(try_node)
            i_nodet, i_probt, i_acc_probt = try_node[0], try_node[1], try_node[2]

            if i_nodet not in self.graph_dict:
                continue

            outdictw = self.graph_dict[i_nodet]
            for outw in outdictw:
                if not (outw not in a_n_set_k):
                    continue
                if not (outw not in s_total_set):
                    continue
                if not (i_node not in a_e_set_k or outw not in a_e_set_k[i_node]):
                    continue
                if not (w_list[int(outw)] > self.product_list[k_prod][2]):
                    continue
                if not (pp_list_k[int(outw)] > 0):
                    continue
                # -- add the value calculated by activated probability * profit of this product --
                i_probw = float(outdictw[outw])
                temp_ep = i_acc_probt * pp_list_k[int(outw)] * self.product_list[k_prod][0]
                ep += temp_ep
                # -- activate the receivers temporally --
                # -- add the receiver of node into try_a_n_list --
                # -- notice: prevent the node from owing no receiver --
                a_n_set_k.add(outw)
                try_a_n_list.append([outw, i_probw, round(i_probt * i_probw, 4)])

        return round(ep, 4)

    def insertSeedIntoSeedSet(self, k_prod, i_nodet, s_set, a_n_set, a_e_set, w_list, pp_list):
        # -- insert the seed with maximum expected profit into seed set --
        # -- insert the seed into seed set --
        # -- insert the seed into a_n_set --
        # -- i_nodet's wallet is 0 --
        # -- i_nodet's pp to all product is 0 --
        s_set[k_prod].add(i_nodet)
        a_n_set[k_prod].add(i_nodet)
        w_list[int(i_nodet)] = 0
        for k in range(self.num_product):
            pp_list[k][int(i_nodet)] = 0
        cur_profit = 0.0
        s_total_set = set()
        for k in range(self.num_product):
            s_total_set = s_total_set.union(s_set[k])

        ### try_a_n_list: (list) the set to store the nodes may be activated for some products
        ### try_a_n_list[][0]: (str) the receiver when seed is ancestor
        ### try_a_n_list[][1]: (float4) the probability to activate the receiver from seed
        ### an_number: (int) the number of costumers activated bt this seed
        try_a_n_list = []
        an_number = 1

        # -- add the receivers of seed into try_a_n_list --
        # -- notice: prevent the seed from owing no receiver --
        if i_nodet not in self.graph_dict:
            return s_set, a_n_set, a_e_set, an_number, cur_profit, w_list, pp_list

        outdict = self.graph_dict[i_nodet]
        for out in outdict:
            if not (out not in a_n_set[k_prod]):
                continue
            if not (out not in s_total_set):
                continue
            if not (i_nodet not in a_e_set[k_prod] or out not in a_e_set[k_prod][i_nodet]):
                continue
            if not (w_list[int(out)] > self.product_list[k_prod][2]):
                continue
            if not (pp_list[k_prod][int(out)] > 0):
                continue
            if random.random() <= float(outdict[out]):
                try_a_n_list.append(out)
                if i_nodet in a_e_set[k_prod]:
                    a_e_set[k_prod][i_nodet].add(out)
                else:
                    a_e_set[k_prod][i_nodet] = {out}

        # -- activate the candidate nodes actually --
        dnic_d = DiffusionNormalIC(self.graph_dict, self.seed_cost_dict, self.product_list, self.pps, self.wpiwp)

        while len(try_a_n_list) > 0:
            ### try_node: (list) the nodes may be activated for kk-products (receiving the information)
            ### dp: (bool) the definition of purchasing
            try_node = choice(try_a_n_list)
            try_a_n_list.remove(try_node)
            dp = bool(0)

            ### -- whether purchasing or not --
            if random.random() <= pp_list[k_prod][int(try_node)]:
                a_n_set[k_prod].add(try_node)
                w_list[int(try_node)] -= self.product_list[k_prod][2]
                pp_list = dnic_d.updatePersonalProbList(k_prod, try_node, w_list, pp_list)
                cur_profit += self.product_list[k_prod][0]
                dp = bool(1)

                an_number += 1

                if try_node not in self.graph_dict:
                    continue

            ### -- whether passing the information or not --
            if self.wpiwp or dp:
                outdictw = self.graph_dict[try_node]
                for outw in outdictw:
                    if not (outw not in a_n_set[k_prod]):
                        continue
                    if not (outw not in s_total_set):
                        continue
                    if not (i_nodet not in a_e_set[k_prod] or outw not in a_e_set[k_prod][i_nodet]):
                        continue
                    if not (w_list[int(outw)] > self.product_list[k_prod][2]):
                        continue
                    if not (pp_list[k_prod][int(outw)] > 0):
                        continue
                    if random.random() <= float(outdictw[outw]):
                        try_a_n_list.append(outw)
                        if i_nodet in a_e_set[k_prod]:
                            a_e_set[k_prod][i_nodet].add(outw)
                        else:
                            a_e_set[k_prod][i_nodet] = {outw}

        return s_set, a_n_set, a_e_set, an_number, cur_profit, w_list, pp_list


class Evaluation:
    def __init__(self, g_dict, s_c_dict, prod_list, pps, wpiwp):
        ### g_dict: (dict) the graph
        ### g_dict[node1(str)]: (dict) the set of node1's receivers
        ### g_dict[node1(str)][node2(str)]: (float2) the weight one the edge of node1 to node2
        ### s_c_dict: (dict) the set of cost for seeds
        ### s_c_dict[ii(str)]: (dict) the degree of ii's seed
        ### prod_list: (list) the set to record products
        ### prod_list[kk(int)]: (list) [kk's profit, kk's cost, kk's price]
        ### prod_list[kk(int)][]: (float2)
        ### num_node: (int) the number of nodes
        ### num_product: (int) the kinds of products
        ### pp_strategy: (int) the strategy to update personal prob.
        ### wpiwp: (bool) whether passing the information without purchasing
        self.graph_dict = g_dict
        self.seed_cost_dict = s_c_dict
        self.product_list = prod_list
        self.num_node = len(s_c_dict)
        self.num_product = len(prod_list)
        self.pps = pps
        self.wpiwp = wpiwp

    def getSeedSetProfitSimultaneously(self, s_set, w_list, pp_list):
        ### -- calculate the  profit for seed set simultaneously --
        a_n_set = copy.deepcopy(s_set)
        seed_set_list, try_a_n_list = [], []
        seed_set_profit = 0.0
        for k in range(self.num_product):
            for i in s_set[k]:
                seed_set_list.append([k, i])
        s_total_set = set()
        for k in range(self.num_product):
            s_total_set = s_total_set.union(s_set[k])

        pro_k_list = [0.0 for _ in range(self.num_product)]

        # -- insert the children of seeds into try_a_n_set --
        while len(seed_set_list) > 0:
            seed = choice(seed_set_list)
            seed_set_list.remove(seed)
            k_prod, i_node = seed[0], seed[1]
            outdict = self.graph_dict[i_node]
            for out in outdict:
                if not (out not in a_n_set[k_prod]):
                    continue
                if not (out not in s_total_set):
                    continue
                if not (w_list[int(out)] > self.product_list[k_prod][2]):
                    continue
                if not (pp_list[k_prod][int(out)] > 0):
                    continue
                if random.random() <= float(outdict[out]):
                    try_a_n_list.append([k_prod, out])

        # -- activate the nodes --
        dnic_e = DiffusionNormalIC(self.graph_dict, self.seed_cost_dict, self.product_list, self.pps, self.wpiwp)

        while len(try_a_n_list) > 0:
            ### try_node: (list) the nodes may be activated for kk-products (receiving the information)
            ### dp: (bool) the definition of purchasing
            try_node = choice(try_a_n_list)
            try_a_n_list.remove(try_node)
            k_prod, i_node = try_node[0], try_node[1]
            dp = bool(0)

            ### -- whether purchasing or not --
            if random.random() <= pp_list[k_prod][int(i_node)]:
                a_n_set[k_prod].add(i_node)
                w_list[int(i_node)] -= self.product_list[k_prod][2]
                pp_list = dnic_e.updatePersonalProbList(k_prod, i_node, w_list, pp_list)
                seed_set_profit += self.product_list[k_prod][0]
                dp = bool(1)

                pro_k_list[k_prod] += self.product_list[k_prod][0]

                if i_node not in self.graph_dict:
                    continue

            ### -- whether passing the information or not --
            if self.wpiwp or dp:
                outdictw = self.graph_dict[i_node]
                for outw in outdictw:
                    if not (outw not in a_n_set[k_prod]):
                        continue
                    if not (outw not in s_total_set):
                        continue
                    if not (w_list[int(outw)] > self.product_list[k_prod][2]):
                        continue
                    if not (pp_list[k_prod][int(outw)] > 0):
                        continue
                    if random.random() <= float(outdictw[outw]):
                        try_a_n_list.append([k_prod, outw])

        an_num_list = [0 for _ in range(self.num_product)]
        for k in range(self.num_product):
            an_num_list[k] += len(a_n_set[k])
            pro_k_list[k] = round(pro_k_list[k], 2)

        return seed_set_profit, pro_k_list, an_num_list


if __name__ == "__main__":
    data_set_name = "email_directed"
    product_name = "r1p3n1"
    pp_strategy = 2
    whether_passing_information_without_purchasing = bool(0)

    iniG = IniGraph(data_set_name)
    iniP = IniProduct(product_name)

    seed_cost_dict = iniG.constructSeedCostDict()[1]
    graph_dict = iniG.constructGraphDict()
    product_list = iniP.getProductList()[0]
    wallet_list = iniG.getWalletList(product_name)
    num_node = len(seed_cost_dict)
    num_product = len(product_list)

    start_time = time.time()

    dnic = DiffusionNormalIC(graph_dict, seed_cost_dict, product_list, pp_strategy, whether_passing_information_without_purchasing)
    eva = Evaluation(graph_dict, seed_cost_dict, product_list, pp_strategy, whether_passing_information_without_purchasing)

    seed_set = [set(), set(), {'196', '54', '380'}]
    current_wallet_list = copy.deepcopy(wallet_list)
    personal_prob_list = [[1.0 for _ in range(num_node)] for _ in range(num_product)]
    for ii in range(num_node):
        personal_prob_list = dnic.updatePersonalProbList(-1, str(ii), current_wallet_list, personal_prob_list)

    profit, profit_k_list, an_number_list = eva.getSeedSetProfitSimultaneously(seed_set, current_wallet_list, personal_prob_list)
    print(round(profit, 2))
    print(profit_k_list)
    print(an_number_list)

    how_long = round(time.time() - start_time, 4)
    print("total time: " + str(how_long) + "sec")
