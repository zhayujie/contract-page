# -*- coding:utf-8 -*-
#import queue
#import pygraphviz as pgv

import json
import generateGo
import generateSol

class Commitment:
    def __init__(self, pre, res, tc):
        self.pre = pre
        self.res = res
        self.tc = tc
    def print_content(self):
        print(self.pre)
        print(self.res + ' ' + self.tc)

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

                # 再次遍历承诺的集合，如果有承诺j 的前提 是承诺i sat或vio，则承诺j变为 bas (且该承诺必须本身为1)
                for j in range(0, len(stats)):
                    if stats[j] != 1:
                        continue
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
                transfers.append([stats, new_stats2, 'vio-'+cs[i].tc]) 
                queue.insert(0, new_stats1)
                queue.insert(0, new_stats2)

            # 如果承诺i 状态为1(act)，则可能转移为2 (bas) 或 5 (exp)
            elif c_stat == 1:
                # 转移为5的情况只需要 满足tc，可以直接写
                new_stats1 = list(stats)
                new_stats1[i] = 5        # Ci: act -> exp

                # 如果某个承诺变为5，则所有当前为1，且以它为5作为前提的承诺变为2，以它3/4为前提的承诺变为5
                # 且新变成5的承诺会递归 进行判断
                exp_queue = []
                exp_queue.append(i)
                while len(exp_queue):
                    t = exp_queue.pop(0)
                    for j in range(0, len(stats)):
                        connect = cs[j].pre[0]
                        if stats[j] == 1 and connect:
                            con_id = int(connect[0])              # 前提条件指定的承诺id
                            con_stat = int(connect[1])
                            if t == con_id and con_stat == 5:
                                new_stats1[j] = 2
                            elif t == con_id and (con_stat == 3 or con_stat == 4):
                                new_stats1[j] = 5
                                exp_queue.insert(0, j)

                            

                transfers.append([stats, new_stats1, 'exp-'+cs[i].tc])
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
    G.draw('/Users/zyj/Desktop/contract0.png')



def create_fsm(contract, contract_id):
    cs = []
    stat = {'满足':'3', '违约':'4', '延期':'5'}
    num = {'一':'0', '二':'1', '三':'2', '四':'3','五':'4', '六':'5','七':'6', '八':'7',
        '九':'8', '十':'9'}
    
    for c in contract:
        plist = []
        pr = ''
        premise = c['premise']
        res = c['res']
        p_event = 0
        time = c['time']
        if premise:
            for pre in premise:
                if '条款' in pre:
                    pr = pr + num[pre[2]] + stat[pre[-2:]]
                else:
                    p_event = pre
        if pr:
            plist.append(pr)
        else:
            plist.append(0)

        plist.append(p_event)

        cs.append(Commitment(plist, res, time))
    '''
    c0 = Commitment([0, 'buy'], 'res0', '2017')
    c1 = Commitment(['03', 0], 'res1', '2018')
    c2 = Commitment(['13', 0], 'res2', '2019')
    cs = [c0, c1, c2]
    
    for c in cs:
        c.print_content()
    transfers = create_state_transfers(cs)
    print(transfers)

    '''
    transfers = create_state_transfers(cs)
    size = len(cs)
    root = size * [1]

    transfer_file = {'InitStatus':str(root), "FsmArray":[]}
    
    for i in range(0, len(transfers)):
        current_status = transfers[i][0]
        new_status = transfers[i][1]
        action = transfers[i][2]
        t = {'CurrentStatus': str(current_status), 'Action': action, 'NewStatus': str(new_status)}
        transfer_file['FsmArray'].append(t)
    
    with open('./fsm/' + contract_id, 'w') as fs:
        fs.write(json.dumps(transfer_file, indent=2))
       # print(123)
    generateGo.transferGo('./fsm/'+contract_id, './code/'+contract_id)
    generateSol.transferSolidity('./fsm/'+contract_id, './code/'+contract_id)

# /anaconda/bin/python 
if __name__ == '__main__':
    c0 = Commitment([0, 'buy'], 'res0', '2017')
    c1 = Commitment(['03', 0], 'res1', '2018')
    c2 = Commitment(['13', 0], 'res2', '2019')
    c3 = Commitment(['23', 0], 'res3', '2020')
    c4 = Commitment(['33', 0], 'res3', '2020')
    c5 = Commitment(['33', 0], 'res3', '2020')
    c6 = Commitment(['44', 0], 'res3', '2020')
    c7 = Commitment(['54', 0], 'res3', '2020')
    c8 = Commitment(['63', 0], 'res3', '2020')


    cs = [c0, c1, c2]

    transfers = create_state_transfers(cs)
    
    for line in transfers:
       print(line)
    
    #print(len(transfers))
    #painting(transfers)
    #create_fsm('134', '123')


    