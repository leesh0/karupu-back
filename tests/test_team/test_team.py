from app.db.table import karupu as models
from app.main import get_application
from app.resources import strings
from tests.db.factories import TeamFactory
from tests.graphql.generator import GqlTest
from tests.graphql.queries.feedbacks import *
from tests.graphql.queries.projects import query_add_project
from tests.graphql.queries.teams import *
from tests.utils import get_random_image
from tortoise.contrib import test

app = get_application()

gt = GqlTest()


class TestTeam(test.TestCase):
    async def test_team(self):

        # testing add team
        variables = {
            "name": "test team",
            "open": True,
            "readme": "test readme",
            "tags": ["test1", "test2"],
            "thumbnail": get_random_image(n=1)[0],
            "title": "test team wanted",
        }

        try:
            r = await gt.gql_execute_with_file(query=query_add_team, variables=variables)
        except:
            assert False, "request error"

        resp = r.json()["data"]
        assert resp and resp["addTeam"], "test add team failed"

        # test edit team

        team_id = resp["addTeam"]["id"]
        edit_variables = {"teamId": team_id, "name": "test team edit", "tags": ["test3", "test2"]}

        try:
            r = await gt.gql_execute(query=query_edit_team, variables=edit_variables)
        except:
            assert False, "request error"

        resp = r.json()["data"]

        assert resp and resp["editTeam"], "test edit team failed"

        # test app part
        part_variables = {
            "desc": "test decs 1",
            "maxCount": 1,
            "name": "test backend",
            "teamId": team_id,
        }

        try:
            r = await gt.gql_execute(query=query_add_part, variables=part_variables)
        except:
            assert False, "request error"

        resp = r.json()["data"]

        assert resp and resp["addPart"], "test add part failed"

        # test edit part
        part_id = resp["addPart"]["id"]
        part_edit_variables = {
            "desc": "test edit desc 1",
            "maxCount": 3,
            "name": "test edit backend",
            "partId": part_id,
        }

        try:
            r = await gt.gql_execute(query=query_edit_part, variables=part_edit_variables)
        except:
            assert False, "request error"

        resp = r.json()["data"]
        assert resp and resp["editPart"], "test edit part failed"

        # test entry member
        entry_member_variables = {"partId": part_id}

        try:
            r = await gt.gql_execute(
                query=query_entry_member, variables=entry_member_variables, admin=False
            )
        except:
            assert False, "request error"

        resp = r.json()["data"]
        assert resp and resp["entryMember"], "test entry member failed"

        # test accept member

        member_id = str((await models.TeamMember.filter(part_id=part_id).first()).id)
        accpet_member_variables = {"memberId": member_id}

        try:
            r = await gt.gql_execute(query=query_accept_member, variables=accpet_member_variables)
        except:
            assert False, "request error"

        resp = r.json()["data"]

        assert resp and resp["acceptMember"], "test accept member failed"

        # test delete member
        delete_member_variables = {"memberId": member_id}

        try:
            r = await gt.gql_execute(query=query_delete_member, variables=delete_member_variables)
        except:
            assert False, "request error"

        resp = r.json()["data"]
        assert resp and resp["deleteMember"], "test delete member failed"

        # test delete part
        delete_part_variables = {"partId": part_id}
        try:
            r = await gt.gql_execute(query=query_delete_part, variables=delete_part_variables)
        except:
            assert False, "request error"

        resp = r.json()["data"]
        assert resp and resp["deletePart"], "test delete part failed"

        # test delete team
        delete_team_variables = {"teamId": team_id}
        try:
            r = await gt.gql_execute(query=query_delete_team, variables=delete_team_variables)
        except:
            assert False, "request error"

        resp = r.json()["data"]

        assert resp and resp["deleteTeam"], "test delete team failed"
