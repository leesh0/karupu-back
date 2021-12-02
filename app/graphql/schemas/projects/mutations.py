from uuid import UUID

import strawberry
from app.db.repositories.projects import ProjectRepository
from app.db.table import karupu as models
from app.graphql.permissions.authentication import IsAuthenticated
from app.graphql.permissions.feedbacks import IsFeedbackAuthor
from app.graphql.permissions.projects import IsProjectAuthor
from app.graphql.schemas.projects.inputs import (
    ProjectFeedbackInput,
    ProjectFeedbackUpdateInput,
    ProjectsInput,
    ProjectsUpdateInput,
)
from app.graphql.types import Project, ProjectFeedback
from app.graphql.utils import input_dict
from app.models.feedbacks import CreateFeedbackModel, UpdateFeedbackModel
from app.models.projects import ProjectCreateModel, ProjectUpdateModel
from strawberry.types import Info


@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def add_project(self, project: ProjectsInput, info: Info) -> Project:
        auth = info.context["auth"]
        req_user = await auth.get_current_user()

        project_data = input_dict(project)
        arg_model = ProjectCreateModel(user=req_user, **project_data)

        created = await ProjectRepository.create(arg_model)
        return Project(**created.serialize())

    @strawberry.mutation(permission_classes=[IsAuthenticated, IsProjectAuthor])
    async def edit_project(self, id: int, body: ProjectsUpdateInput, info: Info) -> Project:
        project_data = input_dict(body)

        arg_model = ProjectUpdateModel(id=id, **project_data)
        updated = await ProjectRepository.update(arg_model)

        return Project(**updated.serialize())

    @strawberry.mutation(permission_classes=[IsAuthenticated, IsProjectAuthor])
    async def delete_project(self, id: int, info: Info) -> bool:
        return await ProjectRepository.delete(id)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def add_feedback(
        self, project_id: int, feedback: ProjectFeedbackInput, info: Info
    ) -> ProjectFeedback:
        auth = info.context["auth"]
        req_user = await auth.get_current_user()

        feedback_data = input_dict(feedback)
        project = await models.Project.get(id=project_id)

        arg_model = CreateFeedbackModel(project=project, user=req_user, **feedback_data)
        created = await ProjectRepository.add_feedback(arg_model)

        return ProjectFeedback(**created.serialize())

    @strawberry.mutation(permission_classes=[IsAuthenticated, IsFeedbackAuthor])
    async def edit_feedback(
        self, feedback_id: UUID, feedback: ProjectFeedbackUpdateInput, info: Info
    ) -> ProjectFeedback:
        feedback_data = input_dict(feedback)

        arg_model = UpdateFeedbackModel(id=feedback_id, **feedback_data)
        updated = await ProjectRepository.edit_feedback(arg_model)

        return ProjectFeedback(**updated.serialize())

    @strawberry.mutation(permission_classes=[IsAuthenticated, IsFeedbackAuthor])
    async def delete_feedback(self, feedback_id: UUID) -> bool:
        return await ProjectRepository.delete_feedback(id=feedback_id)
