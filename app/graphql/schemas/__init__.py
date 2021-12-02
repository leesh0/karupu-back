from app.graphql.schemas import projects, user

queries = (projects.Query, user.Query)

mutations = (projects.Mutation, user.Mutation)
