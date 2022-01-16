from app.graphql.schemas import projects, teams, user

queries = (projects.Query, user.Query)

mutations = (projects.Mutation, user.Mutation, teams.Mutation)
