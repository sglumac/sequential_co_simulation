import constraint
import networkx as nx

from operator import itemgetter


def calculate(connections):
    g = nx.DiGraph(name='Connections')
    edges = [(src[0], dst[0]) for (dst, src) in connections.items()]
    g.add_edges_from(edges)

    def other_bigger(this, *others):
        return all(this < other for other in others)
    def other_bigger_or_smaller(this, *others):
        otherSmaller = all(this > other for other in others)
        return otherSmaller or other_bigger(this, *others)

    problem = constraint.Problem()
    variables = g.nodes()
    problem.addVariables(variables, range(len(variables)))
    problem.addConstraint(constraint.AllDifferentConstraint())

    others = [this for this in variables if g.in_edges(this)]
    for this in variables:
        if not g.in_edges(this):
            problem.addConstraint(other_bigger, [this] + others)

    for this in variables:
        others = [other for other, _ in g.in_edges(this)]
        problem.addConstraint(other_bigger_or_smaller, [this] + others)

    solutions = problem.getSolutions()
    def feedback(solution):
        return tuple((src,dst) for src, dst in g.edges() if solution[src] > solution[dst])

    feedbacks = map(feedback, solutions)
    minFeedback = min(map(len, feedbacks))
    uniqueFeedbacks = set(feedback for feedback in feedbacks if len(feedback) == minFeedback)
    filteredSolutions = []
    for feedback in uniqueFeedbacks:
        idx = feedbacks.index(feedback)
        solution = sorted(solutions[idx].items(), key=itemgetter(1))
        filteredSolutions.append(tuple(map(itemgetter(0), solution)))

    return filteredSolutions

