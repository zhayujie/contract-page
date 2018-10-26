# -*- coding:utf-8 -*-
#import queue
import pygraphviz as pgv

class Commitment:
    def __init__(self, pre, res, tc):
        self.pre = pre
        self.res = res
        self.tc = tc

# 生产状态转移列表
def create_state_transfers(commitments):
    queue = []
    transfers = []
    cs = commitments

    nums = len(cs)       # 承诺数量
    root = nums * [1]    # 初始状态 [1, 1, 1, ..., 1, 1]
    queue.append(root)

    # 以bfs顺序建立图结构，图的每个结点是一个承诺状态列表
    while len(queue):
        stats = queue.pop(0)
        # 遍历当前状态中的所有承诺
        for i in range(0, len(stats)):
            c_stat = stats[i]
           
            # 如果该承诺i状态为2（bas），则可能转移为3（边为res） 和 4（边为tc）
            if c_stat == 2:
                new_stats1 = list(stats)
                new_stats1[i] = 3        # Ci : bas -> sat
                new_stats2 = list(stats)
                new_stats2[i] = 4        # Ci : bas -> vio

                # 再次遍历承诺的集合，如果有承诺j 的前提 是承诺i sat或vio，则承诺j变为 bas
                for j in range(0, len(stats)):
                    connect = cs[j].pre[0]
                    if connect:
                        con_id = int(connect[0])              # 前提条件指定的承诺id
                        con_stat = int(connect[1])            # 前提条件指定的承诺状态
                        if i == con_id and con_stat == 3:
                            new_stats1[j] = 2
                        elif i == con_id and con_stat == 4:
                            new_stats2[j] = 2
                    
                # 保存状态转移，将新状态加入queue
                transfers.append([stats, new_stats1, cs[i].res]) 
                transfers.append([stats, new_stats2, cs[i].tc]) 
                queue.insert(0, new_stats1)
                queue.insert(0, new_stats2)

            # 如果承诺i 状态为1(act)，则可能转移为2 (bas) 或 5 (exp)
            elif c_stat == 1:
                # 转移为5的情况只需要 满足tc，可以直接写
                new_stats1 = list(stats)
                new_stats1[i] = 5        # Ci: act -> exp
                transfers.append([stats, new_stats1, cs[i].tc])
                queue.insert(0, new_stats1)

                # 判断承诺i的前提条件中是否有与之前条件有依赖关系，有的话则检查是否满足，满足则转移为bas
                # 其实以下代码只对根结点有效，因为对于其他节点，只要状态转移到3或4就会自动将 以他为前提的承诺设置为bas
                pre = cs[i].pre
                connect = pre[0]
            
                if not pre[1]:
                    event = ''
                else:
                    event = pre[1]

                if connect:
                    pre_id = int(connect[0])
                    pre_stat = int(connect[1])
                    if stats[pre_id] == pre_stat:
                        new_stats2 = list(stats)
                        new_stats2[i] = 2   # Ci: act -> bas
                        transfers.append([stats, new_stats1, event])
                        queue.insert(0, new_stats2)
                    else:
                        continue
                else:
                    new_stats2 = list(stats)
                    new_stats2[i] = 2
                    transfers.append([stats, new_stats2, event])
                    queue.insert(0, new_stats2)
            
            # 对于承诺状态为3，4，5的则不做处理直接跳过

    return transfers


def painting(transfers):
    G = pgv.AGraph(directed=True, strict=True, encoding='UTF-8')
    G.graph_attr['epsilon']='0.001'
    s = set({})
    for transfer in transfers:
        s.add(str(transfer[0]))
        s.add(str(transfer[1]))

    for node in list(s):
        G.add_node(node)

    for transfer in transfers:
        G.add_edge(str(transfer[0]), str(transfer[1]))

    G.layout('dot')
    G.draw('/Users/zyj/Desktop/contract1.png')


if __name__ == '__main__':

    c0 = Commitment([0, 'buy'], 'res0', '2017')
    c1 = Commitment(['03', 0], 'res1', '2018')
    c2 = Commitment(['04', 0], 'res2', '2019')
    c3 = Commitment(['13', 0], 'res3', '2020')

    cs = [c0, c1, c2, c3]
    transfers = create_state_transfers(cs)
    '''
    for line in transfers:
       print(line)
    '''
    print(len(transfers))
    painting(transfers)
    