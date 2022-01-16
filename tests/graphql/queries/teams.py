query_add_team = """
mutation AddTeam($name: String!, $title: String!, $open: Boolean, $readme: String!, $tags: [String!], $thumbnail: Upload) {
  addTeam(team: {title: $title, name: $name, readme: $readme, open: $open, tags: $tags, thumbnail: $thumbnail}) {
    user {
      bio
    }
    id
    slug
    tags
    name
  }
}

"""


query_edit_team = """
mutation AddTeam($teamId:UUID!, $name: String, $title: String, $open: Boolean, $readme: String, $tags: [String!], $thumbnail: Upload) {
  editTeam(team: {name: $name, open: $open, readme: $readme, tags: $tags, thumbnail: $thumbnail, title: $title}, teamId: $teamId) {
    id
    slug
    title
    thumbnail
    tags
    readme
    open
    name
    createdAt
    user {
      id
    }
  }
}
"""

query_delete_team = """
mutation MyMutation($teamId:UUID!) {
  deleteTeam(teamId: $teamId)
}
"""


query_add_part = """
mutation MyMutation($name:String!, $desc:String, $maxCount:Int, $teamId:UUID!){
  addPart(part: {name: $name, desc: $desc, maxCount: $maxCount}, teamId: $teamId) {
    desc
    id
    maxCount
    name
  }
}
"""

query_edit_part = """
mutation MyMutation($name: String, $desc: String, $maxCount: Int, $partId: UUID!) {
  editPart(part: {desc: $desc, maxCount: $maxCount, name: $name}, partId: $partId) {
    desc
    id
    maxCount
    name
  }
}
"""

query_delete_part = """
mutation MyMutation($partId:UUID!) {
  deletePart(partId: $partId)
}
"""


query_entry_member = """
mutation MyMutation($partId:UUID!) {
  entryMember(partId: $partId)
}
"""

query_accept_member = """
mutation MyMutation($memberId:UUID!) {
  acceptMember(memberId: $memberId)
}
"""

query_delete_member = """
mutation MyMutation($memberId: UUID!) {
  deleteMember(memberId: $memberId)
}
"""
