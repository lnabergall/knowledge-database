"""
Content Piece View API
"""

from .content import Content
from .edit import Edit
from .vote import AuthorVote


class ContentView:

    def __init__(self, content_id=None, first_author_name=None, 
                 first_author_id=None, content_type=None, name=None,
                 alternate_names=None, text=None, keywords=None, 
                 citations=None):
        """
        Args:
            content_id: Integer.
            first_author_name: String.
            first_author_id: Integer.
            content_type: String.
            name: String.
            alternate_names: List of Strings.
            text: String.
            keywords: List of Strings.
            citations: List of Strings.
        """
        if content_id is not None:
            try:
                content = Content(content_id=content_id)
            except:
                raise
            else:
                self.content = content.json_ready
        else:
            try:
                content = Content(first_author_name=first_author_name,
                                  first_author_id=first_author_id, 
                                  content_type=content_type, name=name,
                                  alternate_names=alternate_names, text=text,
                                  keywords=keywords, citations=citations)
            except:
                raise
            else:
                self.content = content.json_ready

    @classmethod
    def user_content(cls, user_id, page_num=0):
        try:
            content = Content.bulk_retrieve(user_id=user_id, page_num=page_num)
            content_ids = [piece.content_id for piece in content]
            edit_existence_dict = Edit.edits_validating(content_ids)
            votes_needed = AuthorVote.votes_needed(
                user_id, content_ids=content_ids)
        except:
            raise
        else:
            content = [piece.json_ready for piece in content]
            for i in range(len(content)):
                content_id = content[i]["content_id"]
                content[i]["edits_validating"] = edit_existence_dict[content_id]
                content[i]["votes_needed"] = votes_needed[content_id]
            return content

    @classmethod
    def get_content_types(cls):
        try:
            content_types = Content.get_content_types()
        except:
            raise
        else:
            return content_types

    @classmethod
    def search(cls, query, page_num=1):
        try:
            results = Content.search(query, page_num=page_num)
        except:
            raise
        else:
            return results

    @classmethod
    def filter_by(cls, content_part, part_string, page_num=1):
        try:
            results = Content.filter_by(content_part, part_string, 
                                        page_num=page_num)
        except:
            raise
        else:
            return results

    @classmethod
    def autocomplete(cls, content_part, query):
        try:
            completions = Content.autocomplete(content_part, query)
        except:
            raise
        else:
            return completions

    @classmethod
    def recent_activity(cls):
        pass

    @classmethod
    def validation_data(cls):
        pass
