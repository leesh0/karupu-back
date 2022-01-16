from app.graphql.loaders import optloaders
from app.graphql.loaders.loaders import *
from strawberry.dataloader import DataLoader

from .base import OptDataLoader

contexts = {
    "project_tags_loader": DataLoader(load_fn=load_project_tags, cache=False),
    "team_tags_loader": DataLoader(load_fn=load_team_tags, cache=False),
    "user_loader": DataLoader(load_fn=load_user, cache=False),
    "user_projects_loader": DataLoader(load_fn=load_user_projects, cache=False),
    "project_loader": DataLoader(load_fn=load_project, cache=False),
    "project_member_loader": DataLoader(load_fn=load_project_members, cache=False),
    "feedback_loader": DataLoader(load_fn=load_feedback, cache=False),
    "child_feedback_loader": DataLoader(load_fn=load_child_feedback, cache=False),
    "team_loader": DataLoader(load_fn=load_team, cache=False),
    "part_member_loader": DataLoader(load_fn=load_part_member, cache=False),
    "team_part_loader": DataLoader(load_fn=load_team_part, cache=False),
    "part_loader": DataLoader(load_fn=load_part, cache=False),
    "team_member_loader": DataLoader(load_fn=load_team_member, cache=False),
    "project_feedbacks_count_loader": DataLoader(load_fn=load_feedbacks_count, cache=False),
}
