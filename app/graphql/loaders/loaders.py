from typing import Dict, List

from app.db.table import karupu as models
from app.graphql.types import (
    ChildProjectFeedback,
    Project,
    ProjectFeedback,
    Team,
    TeamMember,
    TeamPart,
    User,
)


async def load_project(project_ids) -> List[Project]:
    objs = await models.Project.in_bulk(id_list=project_ids)
    return [Project(**objs[pid].serialize()) for pid in project_ids]


async def load_project_tags(project_ids) -> List[List[str]]:
    objs = await models.ProjectTagManager.gql.select_related("tag").list_in_bulk(
        project_ids, field_name="project_id"
    )
    return [[obj.tag.text for obj in objs[pid]] for pid in project_ids]


async def load_team_tags(tids):
    objs = (
        await models.TeamTagManager.gql.select_related("tag")
        .only("team_id")
        .list_in_bulk(tids, field_name="team_id")
    )
    return [[obj.tag.text for obj in objs[tid]] for tid in tids]


async def load_project_members(project_ids) -> List[User]:
    objs = (
        await models.ProjectMember.gql.select_related("user")
        .only("id", "project_id")
        .list_in_bulk(project_ids, field_name="project_id")
    )
    return [[User(**obj.user.serialize()) for obj in objs[pid]] for pid in project_ids]


async def load_user(user_ids):
    objs = await models.User.in_bulk(user_ids, field_name="id")
    return [User(**objs[uid].serialize()) for uid in user_ids]


async def load_user_projects(user_ids):
    objs = await models.Project.list_in_bulk(user_ids, field_name="user_id")
    return [[Project(**obj.serialize()) for obj in objs[uid]] for uid in user_ids]


async def load_feedback(pids):
    objs = await models.ProjectFeedback.filter(parent__isnull=True).list_in_bulk(
        pids, "project_id"
    )
    return [[ProjectFeedback(**obj.serialize()) for obj in objs[pid]] for pid in pids]


async def load_child_feedback(fids):
    objs = await models.ProjectFeedback.list_in_bulk(fids, field_name="parent_id")
    return [[ChildProjectFeedback(**obj.serialize()) for obj in objs[fid]] for fid in fids]


async def load_team(tids):
    objs = await models.Team.in_bulk(tids, field_name="id")
    return [Team(**objs[tid].serialize()) for tid in tids]


async def load_part_member(pids):
    objs = await models.TeamMember.list_in_bulk(pids, field_name="part_id")
    return [[TeamMember(**obj.serialize()) for obj in objs[pid]] for pid in pids]


async def load_team_part(tids):
    objs = await models.TeamPart.list_in_bulk(tids, field_name="team_id")
    return [[TeamPart(**obj.serialize()) for obj in objs[tid]] for tid in tids]


async def load_part(pids):
    objs = await models.TeamPart.in_bulk(pids, field_name="id")
    return [TeamPart(**objs[pid].serialize()) for pid in pids]
