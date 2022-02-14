query_add_project = """
mutation testAddProject($category: String!, $title: String!, $icon: Upload, $desc: String, $homeUrl: String, $repoUrl: String, $readme: String, $tags: [String!], $status: String, $members: [String!]) {
  addProject(project: {category: $category, title: $title, icon: $icon, desc: $desc, homeUrl: $homeUrl, repoUrl: $repoUrl, readme: $readme, members: $members, status: $status, tags: $tags}) {
    id
    tags {
      id
      text
      slug
    }
    homeUrl
    members {
      username
    }
    category
    title
  }
}
"""

query_edit_project = """
mutation testEditProject(
  $id:Int!,
  $category:String,
  $title:String,
  $icon:Upload,
  $desc:String,
  $homeUrl:String,
  $repoUrl:String,
  $readme:String,
  $tags:[String!],
  $members: [String!],
  $status:String
) {
  editProject(id:$id,body: {
    category: $category, 
    title: $title, 
    icon: $icon, 
    desc: $desc, 
    homeUrl: $homeUrl, 
    repoUrl: $repoUrl, 
    readme: $readme, 
    members: $members,
    status:$status,
    tags: $tags}) {
    id
    icon
    tags{
      id
      text
      slug
    }
    homeUrl
    repoUrl
    status
    members {
        username
    }
  }
}
"""

query_delete_project = """
mutation testDeleteProject($id:Int!){
  deleteProject(id:$id)
}
"""
