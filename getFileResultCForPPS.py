for m in [1, 2, 3]:
    model_name = "mngic" * (m == 1) + "mhdic" * (m == 2) + "mric" * (m == 3) + "_pps"
    profit = []
    for data_setting in [2, 4]:
        data_set_name = "email_directed" * (data_setting == 1) + "email_undirected" * (data_setting == 2) + \
                        "WikiVote_directed" * (data_setting == 3) + "NetPHY_undirected" * (data_setting == 4)
        for prod_setting in [1, 2]:
            for prod_setting2 in [1, 2, 3]:
                product_name = "r1p3n" + str(prod_setting) + "a" * (prod_setting2 == 2) + "b" * (prod_setting2 == 3)
                for wpiwp in [bool(0), bool(1)]:
                    for pps in [1, 2, 3]:

                        try:
                            result_name = "result/r/" + model_name + str(pps) + "_wpiwp" * wpiwp + "/" + \
                                          model_name + str(pps) + "_wpiwp" * wpiwp + "_" + data_set_name + "_" + product_name + "/profit.txt"
                            print(result_name)

                            with open(result_name) as f:
                                for lnum, line in enumerate(f):
                                    if lnum == 0:
                                        profit.append(line)
                                    else:
                                        break
                            f.close()
                        except FileNotFoundError:
                            profit.append("")
                            continue

    fw = open("result/" + model_name + "_comparison_profit.txt", 'w')
    for lnum, line in enumerate(profit):
        if lnum % 6 == 0 and lnum != 0:
            fw.write("\n" * 9)
        fw.write(str(line) + "\n")
    fw.close()