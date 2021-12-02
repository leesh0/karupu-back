import io
import json
from typing import overload

from tests.client import get_client


class GqlTest:
    _cli = get_client()
    _ncli = get_client(admin=False)

    async def _post(self, query, variables):
        req = self._cli.build_request(
            method="POST", url="/graphql", json={"query": query, "variables": variables}
        )
        res = await self._cli.send(req)
        return res

    async def _npost(self, query, variables):
        req = self._ncli.build_request(
            method="POST", url="/graphql", json={"query": query, "variables": variables}
        )
        res = await self._ncli.send(req)
        return res

    async def _gqlpost(self, data, files):
        req = self._cli.build_request(method="POST", url="/graphql", data=data, files=files)
        try:
            res = await self._cli.send(req)
        except Exception as e:
            raise ValueError(message="Cannot send request")
        return res

    async def _ngqlpost(self, data, files):
        req = self._ncli.build_request(method="POST", url="/graphql", data=data, files=files)
        try:
            res = await self._ncli.send(req)
        except Exception as e:
            raise ValueError(message="Cannot send request")
        return res

    async def gql_execute(self, query, variables, admin=True):
        if admin:
            return await self._post(query, variables)
        else:
            return await self._npost(query, variables)

    async def gql_execute_with_file(self, query, variables: dict, admin=True):
        file_map = dict()
        file_obj = dict()
        attached = dict()
        for k, v in variables.items():
            if isinstance(v, list) and len(v) > 0:
                if isinstance(v[0], io.IOBase):
                    attached[k] = [f for f in v]
                    variables[k] = [None for _ in v]
            elif isinstance(v, io.IOBase):
                attached[k] = v
                variables[k] = None

        for v_name, objs in attached.items():
            if isinstance(objs, list):
                for i, obj in enumerate(objs):
                    file_map[f"file_{v_name}_{i}"] = [f"variables.{v_name}.{i}"]
                    file_obj[f"file_{v_name}_{i}"] = obj
            else:
                file_map[f"file_{v_name}"] = [f"variables.{v_name}"]
                file_obj[f"file_{v_name}"] = objs

        operations = json.dumps({"query": query, "variables": variables})

        if admin:
            cli_post = self._gqlpost
        else:
            cli_post = self._ngqlpost

        response = await cli_post(
            data={"operations": operations, "map": json.dumps(file_map)},
            files={**file_obj},
        )
        return response
