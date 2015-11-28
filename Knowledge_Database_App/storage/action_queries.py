"""

"""

import sys

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound, 
                               IntegrityError

from . import orm_core as orm
from .select_queries import InputError, get_user, get_content_piece


class ActionError(Exception):
    """General exception raised when a database action query fails."""


def store_content_piece(user_id, name, text, content_type, keywords, 
                        timestamp, citations=None, alternate_names=None):
    """
    Input: user_id, name, text, content_type, keywords, and timestamp. 
           Optionally, citations and alternate_names.
    """
    session = orm.start_session()
    content_piece = orm.ContentPiece(timestamp=timestamp)
    author = get_user(user_id=user_id)
    content_piece.first_author = author
    content_piece.authors.append(author)

    name = orm.Name(name=name, name_type="primary", timestamp=timestamp)
    content_piece.name = name
    if alternate_names is not None:
        alternate_names = [orm.Name(name=alt_name, name_type="alternate", 
                           timestamp=timestamp) for alt_name in alternate_names]
        content_piece.alternate_names = alternate_names

    text = orm.Text(text=text, timestamp=timestamp)
    content_type = orm.ContentType(content_type=content_type)
    keywords = [orm.Keyword(Keyword=Keyword, timestamp=timestamp) 
                for keyword in keywords]
    content_piece.text = text
    content_piece.content_type = content_type
    content_piece.keywords = keywords

    if citations is not None:
        citations = [orm.Citation(citation_text=citation, timestamp=timestamp) 
                     for citation in citations]
        content_piece.citations = citations

    session.add(content_piece)
    try:
        session.commit()
    except:
        session.rollback()
        raise ActionError(str(sys.exc_info()[0]))


def update_content_type(content_id, content_type):
    """Input: content_id and content_type."""

    session = orm.start_session()
    content_piece = get_content_piece(content_id)
    try:
        new_content_type = session.query(orm.ContentType).filter(
            orm.ContentType.content_type == content_type).one()
    except (NoResultFound, MultipleResultsFound) as e:
        raise InputError("Invalid argument!")
    else:
        content_piece.content_type = new_content_type
        try:
            session.commit()
        except:
            session.rollback()
            raise ActionError(str(sys.exc_info()[0]))


def store_content_part(content_part, part_text, content_id, timestamp):
    """
    Input: content_part ('name', 'keyword', or 'citation'), part_text, 
           content_id, and timestamp.
    """
    session = orm.start_session()
    content_piece = get_content_piece(content_id)
    if content_part == "name":
        alt_name = orm.Name(name=part_text, name_type="alternate", 
                            timestamp=timestamp)
        content_piece.alternate_names.append(alt_name)
    elif content_part == "keyword":
        keyword = orm.Keyword(keyword=part_text, timestamp=timestamp)
        content_piece.keywords.append(keyword)
    elif content_part == "citation":
        citation = orm.Citation(citation_text=part_text, timestamp=timestamp)
        content_piece.citations.append(citation)
    else:
        raise InputError("Invalid argument!")
    try:
        session.commit()
    except:
        session.rollback()
        raise ActionError(str(sys.exc_info()[0]))


def remove_content_part(content_id, part_id, content_part):
    """
    Input: content_id, part_id, and content_part 
           ('keyword', 'citation', or 'name').
    """
    


def update_content_part(part_id, content_part, part_text):
    """Input: part_id, content_part ('name' or 'text'), and part_text."""

    session = orm.start_session()
    if content_part == "name":
        name = session.query(orm.Name).filter(orm.Name.name_id == part_id).one()
        name.name = part_text
    elif content_part == "text":
        text = session.query(orm.Text).filter(orm.Text.text_id == part_id).one()
        text.text = part_text
    else:
        raise InputError("Invalid argument!")
    try:
        session.commit()
    except:
        session.rollback()
        raise ActionError(str(sys.exc_info()[0]))


def store_accepted_edit(edit_text, edit_rationale, content_part, part_id, 
                        content_id, vote, voter_ids, timestamp, acc_timestamp, 
                        author_type, user_id=None):
    """
    Input: edit_text, edit_rationale, content_part ('name', 'text', 'keyword',
           or 'citation'), part_id, content_id, vote, voter_ids, timestamp,
           acc_timestamp, and author_type. 
           Optionally, user_id.
    """
    session = orm.start_session()
    vote = orm.Vote(vote=vote, content_part=content_part, timestamp=timestamp,
                    close_timestamp=acc_timestamp)
    session.flush()     # To get vote.vote_id
    for user_id in voter_ids:
        session.execute(orm.user_votes.insert(), 
                        params={"vote_id": vote.vote_id, "user_id": user_id})

    content_piece = get_content_piece(content_id)
    edit = orm.AcceptedEdit(edit_text=edit_text, edit_rationale=edit_rationale,
                            content_part=content_part, timestamp=timestamp, 
                            acc_timestamp=acc_timestamp, content_id=content_id,
                            author_type=author_type)
    edit.vote = vote
    if author_type == "U" and user_id is not None:
        edit.author_id = user_id
    if content_part == "name":
        edit.name_id == part_id
    elif content_part == "text":
        edit.text_id == part_id
    elif content_part == "keyword":
        edit.keyword_id == part_id
    elif content_part == "citation":
        edit.citation_id == part_id
    else:
        raise InputError("Invalid argument!")

    try:
        session.commit()
    except:
        session.rollback()
        raise ActionError(str(sys.exc_info()[0]))


# store_rejected_edit...