from scipy import sparse
import numpy as np


class MarkovChainsMaker(object):
    def __init__(self, agents, pd):
        self.agents = agents
        self.pd = pd
        self.chains = {}
        self.prob_dic = {}
        self.max_path = 0
        self.update_max_path(self.agents.values())
        self.add_chains(self.agents, self.prob_dic)

    def update_max_path(self, paths):
        for path in paths:
            if len(path) > self.max_path:
                self.max_path = len(path)

    def add_chains(self, agents, prob_dic):
        for agent, path in agents.items():
            chain = np.identity(len(path)) * self.pd
            for i in range(len(path) - 1):
                chain[i][i+1] = 1 - self.pd
            chain[len(path)-1][len(path)-1] = 1
            self.chains[agent] = sparse.csr_matrix(chain)
            s = np.zeros([1, chain.shape[0]])
            s[0][0] = 1
            i = 0
            while s[0][-1] < 0.99:
                i += 1
                if i not in prob_dic:
                    prob_dic[i] = {}
                s = np.matmul(s, chain)
                for j in range(len(s[0])):
                    if s[0][j] > 10e-6:
                        if tuple(path[j]) not in prob_dic[i]:
                            prob_dic[i][tuple(path[j])] = []
                        prob_dic[i][tuple(path[j])].append(s[0][j])

    def get_chains(self):
        return self.chains

    def get_conflict_prob_given_path(self, path):
        self.update_max_path([path])
        # Calculate probability distribution at time t for path
        dist_dic = {}
        self.add_chains({'last': path}, dist_dic)
        # Calculate conflict probability at time t for path
        conf_prob_t_dic = {}
        max_conf_prob_at_t = 0
        t_max_conf_prob = 0
        pos_conf_prob_at_t = {}
        for t in dist_dic:
            prob = 0
            tmp = {}
            if t in self.prob_dic:
                for pos in dist_dic[t]:
                    if pos in self.prob_dic[t]:
                        prob_agents_same_pos_same_t = self.prob_dic[t][pos]
                        prob_agents_not_same_pos_same_t = [1 - x for x in prob_agents_same_pos_same_t]
                        prob_no_agent_at_pos = np.product(prob_agents_not_same_pos_same_t)
                        prob_at_least_one_agent_at_pos = 1 - prob_no_agent_at_pos
                        prob_at_least_one_conf_at_pos = prob_at_least_one_agent_at_pos * dist_dic[t][pos][0]
                        prob = prob + prob_at_least_one_conf_at_pos
                        tmp[pos] = prob_at_least_one_conf_at_pos
            conf_prob_t_dic[t] = prob
            if prob > max_conf_prob_at_t:
                max_conf_prob_at_t = prob
                t_max_conf_prob = t
                pos_conf_prob_at_t = tmp
        # Calculate probability of at least one conflict in path
        prob_no_conf_at_t = [1 - x for x in conf_prob_t_dic.values()]
        prob_no_conf = np.product(prob_no_conf_at_t)
        prob_at_least_one_conf = 1 - prob_no_conf
        max = 0
        pos_tmp = 0
        for pos, prob in pos_conf_prob_at_t.items():
            if prob > max:
                max = prob
                pos_tmp = pos
        res = {'prob': prob_at_least_one_conf, 't_max_conf': t_max_conf_prob, 'pos_max_conf': pos_tmp}
        return res



if __name__ == '__main__':
    agents = {'a1': [[0, 0], [0, 1], [0, 2]], 'a2': [[1, 0], [1, 1], [1, 2], [1, 3], [1, 4]]}
    pd = 0.05
    mk = MarkovChainsMaker(agents, pd)
    for chain in mk.get_chains().values():
        chain = chain.toarray()
        s = np.zeros([1, chain.shape[0]])
        s[0][0] = 1
        for i in range(19):
            s = np.matmul(s, chain)
        #print(s)
    print(mk.get_conflict_prob_given_path([[5, 0], [0, 0], [0, 2]]))
