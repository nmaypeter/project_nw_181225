from SeedSelection_NaiveGreedy import *

if __name__ == "__main__":
    for pps in [1, 2, 3]:
        for wpiwp in [bool(0), bool(1)]:
            data_set_name, product_name = "", ""
            for data_setting in [2]:
                if data_setting == 1:
                    data_set_name = "email_directed"
                elif data_setting == 2:
                    data_set_name = "email_undirected"
                elif data_setting == 3:
                    data_set_name = "WikiVote_directed"
                for prod_setting in [1, 2, 3]:
                    for prod_setting2 in [1, 2, 3, 4]:
                        if prod_setting == 1:
                            if prod_setting2 == 1:
                                product_name = "r1p3n1"
                            elif prod_setting2 == 2:
                                product_name = "r1p3n1a"
                            elif prod_setting2 == 3:
                                product_name = "r1p3n1b"
                        elif prod_setting == 2:
                            if prod_setting2 == 1:
                                product_name = "r1p3n2"
                            elif prod_setting2 == 2:
                                product_name = "r1p3n2a"
                            elif prod_setting2 == 3:
                                product_name = "r1p3n2b"
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

                            an_promote_list = []
                            class_count, class_accumulate_num_node_list, class_accumulate_wallet = [], [[] for _ in range(10)], [[] for _ in range(10)]

                            mep_k_prod, mep_i_node = ssng_sample.getMostValuableSeed(exp_profit_list, nban_seed_set)

                            # -- main --
                            while now_budget < bud and mep_i_node != '-1':
                                class_count.append([mep_k_prod, mep_i_node, current_wallet_list[int(mep_i_node)]])

                                for kk in range(num_product):
                                    if mep_i_node in nban_seed_set[kk]:
                                        nban_seed_set[kk].remove(mep_i_node)
                                seed_set, activated_node_set, activated_edge_set, an_number, current_profit, current_wallet_list, personal_prob_list = \
                                    dnic_sample.insertSeedIntoSeedSet(mep_k_prod, mep_i_node, seed_set, activated_node_set, activated_edge_set, current_wallet_list, personal_prob_list)

                                for num in range(10):
                                    class_accumulate_num_node_list[num].append(len(iniG.getNodeClassList(iniP.getProductList()[1], current_wallet_list)[0][num]))
                                    class_accumulate_wallet[num].append(iniG.getNodeClassList(iniP.getProductList()[1], current_wallet_list)[1][num])
                                now_profit += round(current_profit, 4)
                                now_budget += seed_cost_dict[mep_i_node]
                                an_promote_list.append([mep_k_prod, mep_i_node, an_number, round(current_profit, 4), seed_cost_dict[mep_i_node], iniG.getNodeOutDegree(mep_i_node)])

                                exp_profit_list, nban_seed_set = ssng_sample.updateExpectProfitList(seed_set, nban_seed_set, exp_profit_list, now_budget, activated_node_set, activated_edge_set, current_wallet_list, personal_prob_list)
                                mep_k_prod, mep_i_node = ssng_sample.getMostValuableSeed(exp_profit_list, nban_seed_set)

                            # -- result --
                            how_long = round(time.time() - start_time, 2)
                            fw = open("result/temp/mngic_pps" + str(pps) + "_wpiwp" * wpiwp + "_" + data_set_name + "_" + product_name + "_b" + str(bud) + ".txt", 'w')
                            # -- no. of product, no. of seed, degree, wallet of seed --
                            cc1, cc2, cc3, cc4 = "", "", "", ""
                            for cc in class_count:
                                cc1 = cc1 + str(cc[0] + 1) + "\t"
                                cc2 = cc2 + str(cc[1]) + "\t"
                                cc3 = cc3 + str(iniG.getNodeOutDegree(cc[1])) + "\t"
                                cc4 = cc4 + str(round(cc[2], 2)) + "\t"
                            fw.write(str(cc1) + "\n")
                            fw.write(str(cc2) + "\n")
                            fw.write(str(cc3) + "\n")
                            fw.write(str(cc4) + "\n")
                            fw.write("\n" * 3)

                            # -- accumulative nodes --
                            for num in range(10):
                                ca_list = ""
                                for t, ca in enumerate(class_accumulate_num_node_list[num]):
                                    if num == 0:
                                        ca -= (t + 1)
                                    ca_list = ca_list + str(ca) + "\t"
                                fw.write(str(ca_list) + "\n")
                            fw.write("\n" * 5)

                            # -- accumulative wallet --
                            for num in range(10):
                                ca_list = ""
                                for ca in class_accumulate_wallet[num]:
                                    ca_list = ca_list + str(ca) + "\t"
                                fw.write(str(ca_list) + "\n")
                            fw.write("\n" * 5)

                            ap1, ap2 = ["" for _ in range(num_product)], ["" for _ in range(num_product)]
                            for ap in an_promote_list:
                                for kk in range(num_product):
                                    if ap[0] == kk:
                                        ap1[kk] = ap1[kk] + str(ap[2]) + "\t"
                                        ap2[kk] = ap2[kk] + str(round(ap[3], 2)) + "\t"
                                    else:
                                        ap1[kk] = ap1[kk] + str(0) + "\t"
                                        ap2[kk] = ap2[kk] + str(0) + "\t"
                            # -- nodes for products --
                            for kk in range(num_product):
                                fw.write(str(ap1[kk]) + "\n")
                            fw.write("\n" * 12)
                            # -- profit for products --
                            for kk in range(num_product):
                                fw.write(str(ap2[kk]) + "\n")

                            print("total time: " + str(how_long) + "sec")
                            fw.close()
