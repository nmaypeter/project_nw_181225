from shutil import copyfile


for m in [1]:
    model_name = "mngic" * (m == 1) + "mhdic" * (m == 2) + "mric" * (m == 3) + "_pps"
    for pps in [1, 2, 3]:
        for wpiwp in [bool(0), bool(1)]:
            for data_setting in [1]:
                data_set_name = "email_directed" * (data_setting == 1) + "email_undirected" * (data_setting == 2) + "WikiVote_directed" * (data_setting == 3)
                for prod_setting in [1, 2]:
                    for prod_setting2 in [1, 2, 3]:
                        product_name = "r1p3n" + str(prod_setting) + "a" * (prod_setting2 == 2) + "b" * (prod_setting2 == 3)
                        for bud in range(1, 11):
                            result_name = "result/" + model_name + str(pps) + "_wpiwp" * wpiwp + "/" + \
                                          data_set_name + "_" + product_name + "/" + \
                                          "b" + str(bud) + "_i10.txt"
                            print(result_name)
                            try:
                                fw = open("temp.txt", 'w')
                                with open(result_name) as f:
                                    for lnum, line in enumerate(f):
                                        if lnum == 3:
                                            (l) = line.split()
                                            (ll) = list(l[2])
                                            ll.insert(ll.index('a'), ", ")
                                            lnum3 = ""
                                            for ln in ll:
                                                lnum3 += ln
                                            l[2] = lnum3
                                            lnum3 = ""
                                            for ln in l:
                                                lnum3 = lnum3 + " " + ln
                                            lnum3 = lnum3[1:]
                                            fw.write(lnum3 + "\n")
                                        else:
                                            fw.write(line)
                                f.close()
                                fw.close()
                            except FileNotFoundError:
                                print(result_name)
                                continue

                            try:
                                copyfile("temp.txt", result_name)
                            except FileNotFoundError:
                                print(result_name + ", copy")
                                continue