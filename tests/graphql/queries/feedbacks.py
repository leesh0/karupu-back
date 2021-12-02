query_add_feedback = """
mutation AddFeedback($id: Int!, $rateScore: Int!, $body: String!, $anon: Boolean) {
  addFeedback(feedback: {rateScore: $rateScore, body: $body, anon: $anon}, projectId: $id) {
    id
    body
  }
}
"""


query_edit_feedback = """
mutation EditFeedback($id: UUID!, $rateScore: Int, $body: String, $anon: Boolean) {
  editFeedback(feedback: {body: $body, rateScore:$rateScore, anon:$anon}, feedbackId: $id) {
    body
  }
}
"""

query_delete_feedback = """
mutation DeleteFeedback($id: UUID!) {
  deleteFeedback(feedbackId: $id)
}
"""
