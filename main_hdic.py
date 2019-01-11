from SeedSelection_HighDegree import *

if __name__ == "__main__":
    for pps in [1, 2, 3]:
        for wpiwp in [bool(0), bool(1)]:
            for data_setting in [1]:
                data_set_name = "email_directed" * (data_setting == 1) + "email_undirected" * (data_setting == 2) + "WikiVote_directed" * (data_setting == 3)
                for prod_setting in [1, 2]:
                    for prod_setting2 in [1, 2, 3]:
                        product_name = "r1p3n" + str(prod_setting) + "a" * (prod_setting2 == 2) + "b" * (prod_setting2 == 3)

                        total_budget = 10
                        sample_number, sample_output_number = 10, 10

                        iniG = IniGraph(data_set_name)
                        iniP = IniProduct(product_name)

                        seed_cost_dict = iniG.constructSeedCostDict()[1]
                        graph_dict = iniG.constructGraphDict()
                        product_list = iniP.getProductList()[0]
                        wallet_list = iniG.getWalletList(product_name)
                        num_node = len(seed_cost_dict)
                        num_product = len(product_list)

                        result_numseed_list = [[0 for _ in range(num_product)] for _ in range(int(sample_number / sample_output_number))]
                        result_numan_list = [[0 for _ in range(num_product)] for _ in range(int(sample_number / sample_output_number))]

                        for bud in range(1, total_budget + 1):
                            start_time = time.time()

                            sshd_main = SeedSelectionHD(graph_dict, seed_cost_dict, product_list, bud, pps, wpiwp)
                            dnic_main = DiffusionNormalIC(graph_dict, seed_cost_dict, product_list, pps, wpiwp)

                            degree_dict_o = sshd_main.constructDegreeDict(data_set_name)
                            mep_i_node, degree_dict_o = sshd_main.getHighDegreeNode(degree_dict_o)

                            result = []
                            avg_profit, avg_budget = 0.0, 0.0
                            pro_k_list, bud_k_list = [0.0 for _ in range(num_product)], [0.0 for _ in range(num_product)]
                            avg_num_k_seed, avg_num_k_an = [0 for _ in range(num_product)], [0 for _ in range(num_product)]
                            mrss_times, mrss_pro, mrss_set = [], [], []
                            mrss = [0, 0.0, ""]
                            an_promote_list = [[] for _ in range(sample_number)]

                            for sample_count in range(sample_number):
                                print("pp_strategy = " + str(pps) + ", wpiwp = " + str(wpiwp) + ", data_set_name = " + data_set_name +
                                      ", product_name = " + product_name + ", budget = " + str(bud) + ", sample_count = " + str(sample_count))
                                now_profit, now_budget = 0.0, 0.0
                                seed_set, activated_node_set = [set() for _ in range(num_product)], [set() for _ in range(num_product)]
                                activated_edge_set = [{} for _ in range(num_product)]
                                personal_prob_list = [[1.0 for _ in range(num_node)] for _ in range(num_product)]

                                current_wallet_list = copy.deepcopy(wallet_list)
                                degree_dict = copy.deepcopy(degree_dict_o)

                                while seed_cost_dict[mep_i_node] > total_budget or degree_dict == {}:
                                    mep_i_node, degree_dict = sshd_main.getHighDegreeNode(degree_dict)

                                # -- main --
                                while now_budget < bud and mep_i_node != '-1':
                                    mep_k_prod = choice([kk for kk in range(num_product)])
                                    seed_set, activated_node_set, activated_edge_set, an_number, current_profit, current_wallet_list, personal_prob_list = \
                                        dnic_main.insertSeedIntoSeedSet(mep_k_prod, mep_i_node, seed_set, activated_node_set, activated_edge_set, current_wallet_list, personal_prob_list)

                                    pro_k_list[mep_k_prod] += round(current_profit, 4)
                                    bud_k_list[mep_k_prod] += seed_cost_dict[mep_i_node]
                                    now_profit += round(current_profit, 4)
                                    now_budget += seed_cost_dict[mep_i_node]
                                    an_promote_list[sample_count].append([mep_k_prod, mep_i_node, an_number, round(current_profit, 4), seed_cost_dict[mep_i_node], iniG.getNodeOutDegree(mep_i_node)])

                                    mep_i_node, degree_dict = sshd_main.getHighDegreeNode(degree_dict)
                                    while seed_cost_dict[mep_i_node] > total_budget or degree_dict == {}:
                                        mep_i_node, degree_dict = sshd_main.getHighDegreeNode(degree_dict)

                                # -- result --
                                now_num_k_seed, now_num_k_an = [len(kk) for kk in seed_set], [len(kk) for kk in activated_node_set]
                                result.append([round(now_profit, 4), round(now_budget, 4), now_num_k_seed, now_num_k_an, seed_set])
                                avg_profit += now_profit
                                avg_budget += now_budget
                                for kk in range(num_product):
                                    avg_num_k_seed[kk] += now_num_k_seed[kk]
                                    avg_num_k_an[kk] += now_num_k_an[kk]
                                    pro_k_list[kk], bud_k_list[kk] = round(pro_k_list[kk], 4), round(bud_k_list[kk], 4)

                                if seed_set not in mrss_set:
                                    mrss_times.append(1)
                                    mrss_pro.append(now_profit)
                                    mrss_set.append(seed_set)
                                else:
                                    ii = mrss_set.index(seed_set)
                                    mrss_times[ii] += 1
                                    mrss_pro[ii] += now_profit
                                ii = mrss_set.index(seed_set)
                                if (mrss_times[ii] > mrss[0]) or ((mrss_times[ii] == mrss[0]) and (mrss_pro[ii] / mrss_times[ii]) > (mrss[1] / mrss[0])):
                                    mrss = [mrss_times[ii], mrss_pro[ii], seed_set]

                                how_long = round(time.time() - start_time, 2)
                                print("total_time: " + str(how_long) + "sec")
                                print(result[sample_count])
                                print("avg_profit = " + str(round(avg_profit / (sample_count + 1), 4)) + ", avg_budget = " + str(round(avg_budget / (sample_count + 1), 4)))
                                print("------------------------------------------")

                                if (sample_count + 1) % sample_output_number == 0:
                                    # print("output1")
                                    fw = open("result/mhdic_pps" + str(pps) + "_wpiwp" * wpiwp + "/" +
                                              data_set_name + "_" + product_name + "/" +
                                              "b" + str(bud) + "_i" + str(sample_count + 1) + ".txt", 'w')
                                    fw.write("mhdic, pp_strategy = " + str(pps) + ", total_budget = " + str(bud) + ", wpiwp = " + str(wpiwp) + "\n" +
                                             "data_set_name = " + data_set_name + ", product_name = " + product_name + "\n" +
                                             "total_budget = " + str(bud) + ", sample_count = " + str(sample_count + 1) + "\n" +
                                             "avg_profit = " + str(round(avg_profit / (sample_count + 1), 4)) +
                                             ", avg_budget = " + str(round(avg_budget / (sample_count + 1), 4)) + "\n" +
                                             "total_time = " + str(how_long) + ", avg_time = " + str(round(how_long / (sample_count + 1), 4)) + "\n")
                                    fw.write("\nprofit_ratio =")
                                    for kk in range(num_product):
                                        fw.write(" " + str(round(pro_k_list[kk] / (sample_count + 1), 4)))
                                    fw.write("\nbudget_ratio =")
                                    for kk in range(num_product):
                                        fw.write(" " + str(round(bud_k_list[kk] / (sample_count + 1), 4)))
                                    fw.write("\nseed_number =")
                                    for kk in range(num_product):
                                        fw.write(" " + str(round(avg_num_k_seed[kk] / (sample_count + 1), 4)))
                                    fw.write("\ncustomer_number =")
                                    for kk in range(num_product):
                                        fw.write(" " + str(round(avg_num_k_an[kk] / (sample_count + 1), 4)))
                                    fw.write("\n\n")
                                    mrss = [mrss[0], round(mrss[1] / mrss[0], 2), mrss[2]]
                                    fw.write(str(mrss[0]) + ", " + str(mrss[1]) + ", " + str(mrss[2]) + "\n")

                                    for t, r in enumerate(result):
                                        fw.write("\n" + str(t) + " " + str(round(r[0], 4)) + " " + str(round(r[1], 4)) + " " + str(r[2]) + " " + str(r[3]) + " " + str(r[4]))
                                        fw.write("\n" + str(t) + " " + str(an_promote_list[t]))
                                    fw.close()
