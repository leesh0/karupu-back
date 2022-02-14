from tortoise.contrib import test

from app.db.table.karupu import Project, User
from app.main import get_application
from app.resources import strings
from tests.graphql.generator import GqlTest
from tests.graphql.queries.projects import *
from tests.utils import get_random_image

app = get_application()

gt = GqlTest()


class TestProject(test.TestCase):
    async def test_add_project(self):
        example_users = await User.all()
        member_users = [user.username for user in example_users[:3]]
        variables = {
            "category": "Webサービス",
            "title": "test-edit",
            "icon": get_random_image(1)[0],
            "desc": "test",
            "homeUrl": "https://naver.com",
            "readme": "zzzzzzzz",
            "tags": ["test1", "test2", "test3"],
            "members": member_users,
            "status": "released",
        }
        try:
            r = await gt.gql_execute_with_file(query_add_project, variables)
        except Exception:
            assert False, "fail to create project"

        data = r.json()["data"]

        self.assertEqual(
            bool(data and data["addProject"]["id"]), len(data["addProject"]["tags"]) == 3
        ), "fail to test add project"

    async def test_edit_project(self):
        example_users = await User.all()
        member_users = [user.username for user in example_users[:4]]
        plist = await Project.all().select_related("user")
        admin_user = await User.get(is_admin=True)
        project = [p for p in plist if p.user.id == admin_user.id][0]
        variables = {
            "id": project.id,
            "icon": get_random_image(1)[0],
            "category": "Webサービス",
            "title": "test-post-#1",
            "desc": "test project post!",
            "homeUrl": "https://naver.com",
            "readme": "test_readme",
            "tags": ["test1", "test2", "test3"],
            "members": member_users,
            "status": "wanted",
        }
        try:
            r = await gt.gql_execute_with_file(query_edit_project, variables)
        except Exception:
            assert False, "fail to edit project"
        data = r.json()["data"]
        print(">>>>", r.json())
        assert [t["text"] for t in data["editProject"].get("tags")] == [
            "test1",
            "test2",
            "test3",
        ], "edit failed"
        assert data["editProject"].get("status") == "wanted", "edit project failed"

    async def test_edit_project_one_field(self):
        plist = await Project.all().select_related("user")
        admin_user = await User.get(is_admin=True)
        project = [p for p in plist if p.user.id == admin_user.id][1]
        variables = {
            "id": project.id,
            "tags": ["test#1", "test#2", "test#3"],
        }
        try:
            r = await gt.gql_execute(query_edit_project, variables)
        except Exception:
            assert False, "fail to edit project"
        data = r.json()["data"]
        assert [t["text"] for t in data["editProject"].get("tags")] == [
            "test#1",
            "test#2",
            "test#3",
        ], "edit failed"

    async def test_another_user_can_edit_project(self):
        project = await Project.filter(user__is_admin=False).first().select_related("user")
        variables = {
            "id": project.id,
            "tags": ["test#1", "test#2", "test#3"],
        }
        try:
            r = await gt.gql_execute(query_edit_project, variables)
        except Exception:
            assert False, "fail to edit project"
        data = r.json()["errors"]
        assert any(
            strings.PROJECT_YOUR_NOT_AUTHOR == err["message"] for err in data
        ), "fail to not non-permission user can edit project"

    async def test_delete_project(self):
        project = await Project.filter(user__is_admin=True).first()
        variables = {"id": project.id}
        try:
            r = await gt.gql_execute(query_delete_project, variables)
        except Exception:
            assert False, "faile to delete project"

        data = r.json()["data"]
        assert data["deleteProject"] == True, "fail to delete project"
