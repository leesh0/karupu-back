from app.graphql.loaders.loaders import *
from strawberry.dataloader import DataLoader

contexts = {
    "project_tags_loader": DataLoader(load_fn=load_project_tags),
    "team_tags_loader": DataLoader(load_fn=load_team_tags),
    "user_loader": DataLoader(load_fn=load_user),
    "user_projects_loader": DataLoader(load_fn=load_user_projects),
    "project_loader": DataLoader(load_fn=load_project),
    "project_member_loader": DataLoader(load_fn=load_project_members),
    "feedback_loader": DataLoader(load_fn=load_feedback),
    "child_feedback_loader": DataLoader(load_fn=load_child_feedback),
    "team_loader": DataLoader(load_fn=load_team),
    "part_member_loader": DataLoader(load_fn=load_part_member),
    "team_part_loader": DataLoader(load_fn=load_team_part),
    "part_loader": DataLoader(load_fn=load_part),
}
