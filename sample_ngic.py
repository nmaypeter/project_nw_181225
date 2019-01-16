from SeedSelection_NaiveGreedy import *

if __name__ == "__main__":
    for pps in [1, 2, 3]:
        for wpiwp in [bool(0), bool(1)]:
            for data_setting in [2, 4]:
                data_set_name = "email_directed" * (data_setting == 1) + "email_undirected" * (data_setting == 2) + \
                                "WikiVote_directed" * (data_setting == 3) + "NetPHY_undirected" * (data_setting == 4)
                for prod_setting in [1, 2]:
                    for prod_setting2 in [1, 2, 3]:
                        product_name = "r1p3n" + str(prod_setting) + "a" * (prod_setting2 == 2) + "b" * (prod_setting2 == 3)

                        for bud in [1, 5, 10]:
                            print("pp_strategy = " + str(pps) + ", wpiwp = " + str(wpiwp) + ", data_set_name = " + data_set_name +
                                  ", product_name = " + product_name + ", budget = " + str(bud))
                            iniG = IniGraph(data_set_name)
                            iniP = IniProduct(product_name)

                            seed_cost_dict = iniG.constructSeedCostDict()[1]
                            graph_dict = iniG.constructGraphDict()
                            product_list = iniP.getProductList()[0]
                            wallet_list = iniG.getWalletList(product_name)
                            num_node = len(seed_cost_dict)
                            num_product = len(product_list)

                            # -- initialization for each budget --
                            start_time = time.time()

                            ssng_sample = SeedSelectionNG(graph_dict, seed_cost_dict, product_list, bud, pps, wpiwp)
                            dnic_sample = DiffusionNormalIC(graph_dict, seed_cost_dict, product_list, pps, wpiwp)

                            exp_profit_list = [[0 for _ in range(num_node)] for _ in range(num_product)]
                            for kk in range(num_product):
                                for i in seed_cost_dict:
                                    if i not in graph_dict:
                                        exp_profit_list[kk][int(i)] -= seed_cost_dict[i]
                            notban_seed_set = [set(graph_dict.keys()) for _ in range(num_product)]
                            exp_profit_list, notban_seed_set = ssng_sample.updateExpectProfitList([set() for _ in range(num_product)], notban_seed_set, exp_profit_list, 0.0,
                                                                                                  [set() for _ in range(num_product)], [{} for _ in range(num_product)], wallet_list,
                                                                                                  [[1.0 for _ in range(num_node)] for _ in range(num_product)])

                            # -- initialization for each sample_number --
                            now_profit, now_budget = 0.0, 0.0
                            seed_set, activated_node_set = [set() for _ in range(num_product)], [set() for _ in range(num_product)]
                            activated_edge_set = [{} for _ in range(num_product)]
                            personal_prob_list = [[1.0 for _ in range(num_node)] for _ in range(num_product)]

                            current_wallet_list = copy.deepcopy(wallet_list)
                            exp_profit_list = copy.deepcopy(exp_profit_list)
                            nban_seed_set = copy.deepcopy(notban_seed_set)
                            for ii in range(num_node):
                                personal_prob_list = dnic_sample.updatePersonalProbList(-1, str(ii), current_wallet_list, personal_prob_list)

                            an_promote_list = []
                            class_count, class_accumulate_num_node_list, class_accumulate_wallet = [], [[] for _ in range(10)], [[] for _ in range(10)]
                            remaining_affordable_number = []

                            mep_k_prod, mep_i_node = ssng_sample.getMostValuableSeed(exp_profit_list, nban_seed_set)

                            # -- main --
                            while now_budget < bud and mep_i_node != '-1':
                                cc4_local = 0
                                if mep_i_node in graph_dict:
                                    for ad in graph_dict[mep_i_node]:
                                        if current_wallet_list[int(ad)] >= product_list[mep_k_prod][2]:
                                            cc4_local += 1
                                class_count.append([mep_k_prod, mep_i_node, cc4_local, current_wallet_list[int(mep_i_node)]])
                                affordable_number = [0 for _ in range(num_product)]
                                for ii in range(num_node):
                                    for kk in range(num_product):
                                        if current_wallet_list[ii] >= product_list[kk][2]:
                                            affordable_number[kk] += 1
                                remaining_affordable_number.append(affordable_number)

                                for kk in range(num_product):
                                    if mep_i_node in nban_seed_set[kk]:
                                        nban_seed_set[kk].remove(mep_i_node)
                                seed_set, activated_node_set, activated_edge_set, an_number, current_profit, current_wallet_list, personal_prob_list = \
                                    dnic_sample.insertSeedIntoSeedSet(mep_k_prod, mep_i_node, seed_set, activated_node_set, activated_edge_set, current_wallet_list, personal_prob_list)

                                for num in range(10):
                                    class_accumulate_num_node_list[num].append(len(iniG.getNodeClassList(IniProduct("r1p3n" + str(prod_setting)).getProductList()[1], current_wallet_list)[0][num]))
                                    class_accumulate_wallet[num].append(iniG.getNodeClassList(IniProduct("r1p3n" + str(prod_setting)).getProductList()[1], current_wallet_list)[1][num])

                                now_profit += round(current_profit, 4)
                                now_budget += seed_cost_dict[mep_i_node]
                                an_promote_list.append([mep_k_prod, mep_i_node, an_number, round(current_profit, 4), seed_cost_dict[mep_i_node], iniG.getNodeOutDegree(mep_i_node)])

                                exp_profit_list, nban_seed_set = ssng_sample.updateExpectProfitList(seed_set, nban_seed_set, exp_profit_list, now_budget, activated_node_set, activated_edge_set, current_wallet_list, personal_prob_list)
                                mep_k_prod, mep_i_node = ssng_sample.getMostValuableSeed(exp_profit_list, nban_seed_set)

                            # -- result --
                            how_long = round(time.time() - start_time, 2)

                            path1 = "result/samples/mngic_pps" + str(pps) + "_wpiwp" * wpiwp
                            if not os.path.isdir(path1):
                                os.mkdir(path1)
                            path = "result/samples/mngic_pps" + str(pps) + "_wpiwp" * wpiwp + "/" + \
                                   data_set_name
                            if not os.path.isdir(path):
                                os.mkdir(path)

                            fw = open(path + "/" + product_name + "_b" + str(bud) + ".txt", 'w')
                            # -- no. of product, no. of seed, degree, wallet of seed --
                            cc1, cc2, cc3, cc4, cc5 = "", "", "", "", ""
                            for cc in class_count:
                                cc1 = cc1 + str(cc[0] + 1) + "\t"
                                cc2 = cc2 + str(cc[1]) + "\t"
                                cc3 = cc3 + str(iniG.getNodeOutDegree(cc[1])) + "\t"
                                cc4 = cc4 + str(cc[2]) + "\t"
                                cc5 = cc5 + str(round(cc[3], 2)) + "\t"
                            fw.write(str(cc1) + "\n")
                            fw.write(str(cc2) + "\n")
                            fw.write(str(cc3) + "\n")
                            fw.write(str(cc4) + "\n")
                            fw.write(str(cc5) + "\n")
                            fw.write("\n" * 3)

                            # -- accumulative nodes --
                            cannl_list = [0 for _ in range(len(class_accumulate_num_node_list[0]))]
                            for num in range(10):
                                ca_list = ""
                                for t, ca in enumerate(class_accumulate_num_node_list[num]):
                                    if num == 0:
                                        ca -= (t + 1)
                                    ca_list = ca_list + str(ca) + "\t"
                                    cannl_list[t] += ca
                                fw.write(str(ca_list) + "\n")
                            cannl_str = ""
                            for cannl in cannl_list:
                                cannl_str += str(cannl) + "\t"
                            fw.write(cannl_str + "\n")
                            fw.write("\n" * 4)

                            # -- accumulative wallet --
                            aw_list = [0 for _ in range(len(class_accumulate_wallet[0]))]
                            for num in range(10):
                                ca_list = ""
                                for t, ca in enumerate(class_accumulate_wallet[num]):
                                    ca_list = ca_list + str(ca) + "\t"
                                    aw_list[t] += ca
                                fw.write(str(ca_list) + "\n")
                            aw_str = ""
                            for aw in aw_list:
                                aw_str += str(round(aw, 2)) + "\t"
                            fw.write(aw_str + "\n")
                            fw.write("\n" * 4)

                            ap1_list, ap2_list = [0], [0.0]
                            ap1, ap2 = ["" for _ in range(num_product)], ["" for _ in range(num_product)]
                            apn1, apn2 = [[0 for _ in range(num_product)]], [[0.0 for _ in range(num_product)]]

                            for t, ap in enumerate(an_promote_list):
                                if t != 0:
                                    ap1_list.append(ap1_list[t-1])
                                    ap2_list.append(ap2_list[t-1])
                                    apn1.append(copy.deepcopy(apn1[t-1]))
                                    apn2.append(copy.deepcopy(apn2[t-1]))
                                ap1_list[t] += ap[2]
                                ap2_list[t] += round(ap[3], 2)
                                for kk in range(num_product):
                                    if ap[0] == kk:
                                        apn1[t][kk] += ap[2]
                                        apn2[t][kk] += round(ap[3])
                                        ap1[kk] = ap1[kk] + str(ap[2]) + "\t"
                                        ap2[kk] = ap2[kk] + str(round(ap[3], 2)) + "\t"
                                    else:
                                        ap1[kk] = ap1[kk] + str(0) + "\t"
                                        ap2[kk] = ap2[kk] + str(0) + "\t"
                            # -- nodes for products --
                            for kk in range(num_product):
                                fw.write(str(ap1[kk]) + "\n")
                            ap1_str = ""
                            for ap1_local in ap1_list:
                                ap1_str += str(ap1_local) + "\t"
                            fw.write(ap1_str + "\n")
                            fw.write("\n")
                            apn1_str = ["" for _ in range(num_product)]
                            for apn1_local in apn1:
                                for kk, apn1_l in enumerate(apn1_local):
                                    apn1_str[kk] += str(apn1_l) + "\t"
                            for kk in range(num_product):
                                fw.write(str(apn1_str[kk]) + "\n")
                            fw.write("\n" * 7)
                            # -- profit for products --
                            for kk in range(num_product):
                                fw.write(str(ap2[kk]) + "\n")
                            ap2_str = ""
                            for ap2_local in ap2_list:
                                ap2_str += str(round(ap2_local, 2)) + "\t"
                            fw.write(ap2_str + "\n")
                            fw.write("\n")
                            apn2_str = ["" for _ in range(num_product)]
                            for apn2_local in apn2:
                                for kk, apn2_l in enumerate(apn2_local):
                                    apn2_str[kk] += str(apn2_l) + "\t"
                            for kk in range(num_product):
                                fw.write(str(apn2_str[kk]) + "\n")
                            fw.write("\n" * 7)

                            # -- affordable nodes --
                            aff_num = ["" for _ in range(num_product)]
                            for aff in remaining_affordable_number:
                                for kk in range(num_product):
                                    aff_num[kk] += str(aff[kk]) + "\t"
                            for kk in range(num_product):
                                fw.write(aff_num[kk] + "\n")

                            print("total time: " + str(how_long) + "sec")
                            fw.close()
