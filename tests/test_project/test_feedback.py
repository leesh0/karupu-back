from app.db.table.karupu import Project, User
from app.main import get_application
from app.resources import strings
from tests.graphql.generator import GqlTest
from tests.graphql.queries.feedbacks import *
from tests.graphql.queries.projects import query_add_project
from tests.utils import get_random_image
from tortoise.contrib import test

app = get_application()

gt = GqlTest()


class TestProject(test.TestCase):
    async def test_add_feedback(self):
        test_project = Project(user_id=1, title="test p")
        await test_project.save()

        variables = {"id": test_project.id, "rateScore": 5, "body": "test Body!"}

        try:
            r = await gt.gql_execute(query=query_add_feedback, variables=variables)
        except:
            assert False, "Fail to Request"

        data = r.json().get("data", {}).get("addFeedback")
        feedback_id = data.get("id")

        assert feedback_id is not None, "fail to add feedback"

        # ------- test add feedback

        variables = {"id": feedback_id, "body": "test#edit"}

        try:
            r = await gt.gql_execute(query=query_edit_feedback, variables=variables)
        except:
            assert False, "Fail to Request"

        data = r.json().get("data", {}).get("editFeedback", {})

        assert data.get("body") == "test#edit", "fail to edit feedback"

        # -------- test edit feedback

        variables = {"id": feedback_id}

        try:
            r = await gt.gql_execute(query=query_delete_feedback, variables=variables)
        except:
            assert False, "Fail to Request"

        data = r.json().get("data", {}).get("deleteFeedback", {})

        assert data, "fail to edit feedback"

        # ---------- test delete feedback
