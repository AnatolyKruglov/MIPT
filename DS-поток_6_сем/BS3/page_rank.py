def create_page_rank_markov_chain(links, damping_factor=0.15):
    links = np.array(links)
    N = links.max() + 1  # Число веб-страниц
    prob_matrix = np.zeros((N,N))
    for v in range(N):
        to = links[links[:,0]==v, 1]
        uniq_to, cnt = np.unique(to, return_counts=True)
        prob_matrix[v, uniq_to] = (1-damping_factor)*cnt/len(to) if len(to)>0 else 0
        prob_matrix[v] += damping_factor / N
    return prob_matrix

def page_rank(links, start_distribution, damping_factor=0.15, tolerance=10 ** (-7), return_trace=False):
    prob_matrix = create_page_rank_markov_chain(links, damping_factor=damping_factor)
    distribution = np.matrix(start_distribution)
    prev = np.eye(np.max(links) + 1)
    trace = [distribution]
    while np.linalg.norm(prob_matrix - prev, ord='fro') > tolerance:
        prev = np.copy(prob_matrix)
        prob_matrix = prob_matrix @ prob_matrix
        distribution = distribution @ prob_matrix
        trace.append(distribution)
    if return_trace:
        return np.array(distribution).ravel(),np.array(trace)
    else:
        return np.array(distribution).ravel()