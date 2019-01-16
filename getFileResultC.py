profit = []

for data_setting in [2]:
    data_set_name = "email_directed" * (data_setting == 1) + "email_undirected" * (data_setting == 2) + "WikiVote_directed" * (data_setting == 3)
    for prod_setting in [1, 2]:
        for prod_setting2 in [1, 2, 3]:
            product_name = "r1p3n" + str(prod_setting) + "a" * (prod_setting2 == 2) + "b" * (prod_setting2 == 3)
            for wpiwp in [bool(0), bool(1)]:
                for m in [1, 2, 3]:
                    model_name = "mngic" * (m == 1) + "mhdic" * (m == 2) + "mric" * (m == 3) + "_pps"
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

fw = open("result/comparison_profit.txt", 'w')
for lnum, line in enumerate(profit):
    if lnum % 9 == 0 and lnum != 0:
        fw.write("\n")
    if lnum % 18 == 0 and lnum != 0:
        fw.write("\n")
    fw.write(str(line) + "\n")
fw.close()