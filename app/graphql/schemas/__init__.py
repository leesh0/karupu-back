from . import project


def get_queries(services: list):
    return tuple(serv.queries.Query for serv in services)


def get_mutations(services: list):
    return tuple(serv.mutations.Mutation for serv in services)


servs = [
    project,
]


queries = get_queries(servs)

mutations = get_mutations(servs)
