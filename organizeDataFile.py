edge_dict = {}
with open("data/email.txt") as f:
    for line in f:
        (node1, node2) = line.split()
        if node1 in edge_dict:
            edge_dict[node1].add(int(node2))
        else:
            edge_dict[node1] = {int(node2)}
        if node2 in edge_dict:
            edge_dict[node2].add(int(node1))
        else:
            edge_dict[node2] = {int(node1)}
f.close()

fw = open("data/email_directed/data.txt", 'w')
node_order_list = []
for n1 in list(edge_dict.keys()):
    node_order_list.append(int(n1))
node_order_list = sorted(node_order_list)
print(node_order_list)
for n1 in node_order_list:
    edge_dict[str(n1)] = sorted(list(edge_dict[str(n1)]))
    for n2 in edge_dict[str(n1)]:
        fw.write(str(n1) + "\t" + str(n2) + "\n")
fw.close()

