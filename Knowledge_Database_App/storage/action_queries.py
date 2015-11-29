"""
Storage Action Query API

Contains functions and exceptions for making actions (adds, updates, deletes)
on the Postgres database. Uses SQLAlchemy.

Exceptions:

    ActionError

Functions:

    store_content_piece, delete_content_piece, update_content_type, 
    store_content_part, remove_content_part, update_content_part, 
    store_accepted_edit, store_rejected_edit, store_new_user, update_user, 
    store_user_report
"""

import sys

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import (MultipleResultsFound, NoResultFound, 
                                IntegrityError)

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


def delete_content_piece(content_id, deleted_timestamp):
    """Input: content_id and deleted_timestamp."""

    session = orm.start_session()
    session.query(orm.ContentPiece).filter(
        orm.ContentPiece.content_id == content_id).update(
        {orm.ContentPiece.deleted_timestamp: deleted_timestamp},
         synchronize_session=False)
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
    Deletes name or removes association between content piece and 
    keyword/citation. 
    """
    session = orm.start_session()
    if content_part == "keyword":
        session.execute(orm.content_keywords.delete(), 
            params={"keyword_id": part_id, "content_id": content_id})
    elif content_part == "citation":
        session.execute(orm.content_citations.delete(), 
            params={"citation_id": part_id, "content_id": content_id})
    elif content_part == "name":
        session.query(orm.Name).filter(orm.Name.name_id == part_id).delete(
            synchronize_session=False)
    else:
        raise InputError("Invalid argument!")
    try:
        session.commit()
    except:
        session.rollback()
        raise ActionError(str(sys.exc_info()[0]))


def update_content_part(part_id, content_part, part_text):
    """Input: part_id, content_part ('name' or 'text'), and part_text."""

    session = orm.start_session()
    if content_part == "name":
        session.query(orm.Name).filter(orm.Name.name_id == part_id).update(
            {orm.Name.name: part_text}, synchronize_session=False)
    elif content_part == "text":
        session.query(orm.Text).filter(orm.Text.text_id = part_id).update(
            {orm.Text.text: part_text}, synchronize_session=False)
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

    edit = orm.AcceptedEdit(edit_text=edit_text, edit_rationale=edit_rationale,
                            content_part=content_part, timestamp=timestamp, 
                            acc_timestamp=acc_timestamp, content_id=content_id,
                            author_type=author_type)
    edit.vote = vote
    if author_type == "U" and user_id is not None:
        edit.author_id = user_id
        session.execute(orm.content_authors.insert(),
            params={"content_id": content_id, "user_id": user_id})
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


def store_rejected_edit(edit_text, edit_rationale, content_part, part_id, 
                        content_id, vote, voter_ids, timestamp, rej_timestamp, 
                        author_type, user_id=None):
    """
    Input: edit_text, edit_rationale, content_part ('name', 'text', 'keyword',
           or 'citation'), part_id, content_id, vote, voter_ids, timestamp,
           rej_timestamp, and author_type. 
           Optionally, user_id.
    """
    session = orm.start_session()
    vote = orm.Vote(vote=vote, content_part=content_part, timestamp=timestamp,
                    close_timestamp=rej_timestamp)
    session.flush()     # To get vote.vote_id
    for user_id in voter_ids:
        session.execute(orm.user_votes.insert(), 
            params={"vote_id": vote.vote_id, "user_id": user_id})

    edit = orm.RejectedEdit(edit_text=edit_text, edit_rationale=edit_rationale,
                            content_part=content_part, timestamp=timestamp, 
                            rej_timestamp=rej_timestamp, content_id=content_id,
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


def store_new_user(user_type, user_name, email, pass_hash, 
                   pass_hash_type, pass_salt, timestamp):
    """
    Input: user_type, user_name, email, pass_hash, pass_hash_type, 
           pass_salt, and timestamp.
    """
    session = orm.start_session()
    user = orm.User(user_type=user_type, user_name=user_name, email=email, 
                    pass_hash=pass_hash, pass_hash_type=pass_hash_type, 
                    pass_salt=pass_salt, timestamp=timestamp)
    try:
        session.commit()
    except:
        session.rollback()
        raise ActionError(str(sys.exc_info()[0]))


def update_user(user_id, new_user_name=None, new_email=None,
                confirmed_timestamp=None, new_pass_hash=None,
                new_pass_hash_type=None, new_pass_salt=None,
                new_remember_token_hash=None, 
                new_remember_hash_type=None):
    """
    Input: user_id. 
           Optionally, new_user_name, new_email, confirmed_timestamp,
           new_pass_hash and new_pass_hash_type and new_pass_salt, or
           new_remember_token_hash and new_remember_hash_type. 
    """
    session = orm.start_session()
    if new_user_name is not None:
        session.query(orm.User).filter(orm.User.user_id == user_id).update(
            {orm.User.user_name: new_user_name}, synchronize_session=False)
    elif new_email is not None:
        session.query(orm.User).filter(orm.User.user_id == user_id).update(
            {orm.User.email: new_email}, synchronize_session=False)
    elif confirmed_timestamp is not None:
        session.query(orm.User).filter(orm.User.user_id == user_id).update(
            {orm.User.confirmed_timestamp: confirmed_timestamp}, 
            synchronize_session=False)
    elif (new_pass_hash is not None and new_pass_hash_type is not None
            and new_pass_salt is not None):
        session.query(orm.User).filter(orm.User.user_id == user_id).update(
            {orm.User.pass_hash: new_pass_hash, orm.User.pass_hash_type: 
             new_pass_hash_type, orm.User.pass_salt: new_pass_salt}, 
            synchronize_session=False)
    elif (new_remember_token_hash is not None 
            and new_remember_hash_type is not None):
        session.query(orm.User).filter(orm.User.user_id == user_id).update(
            {orm.User.remember_token_hash: new_remember_token_hash, 
             orm.User.remember_hash_type: new_remember_hash_type}, 
            synchronize_session=False)
    else:
        raise InputError("Invalid arguments!")
    try:
        session.commit()
    except:
        session.rollback()
        raise ActionError(str(sys.exc_info()[0]))


def store_user_report(content_id, report_text, report_type, admin_report,
                      timestamp, res_timestamp, admin_id, author_type, 
                      user_id=None):
    """
    Input: content_id, report_text, report_type, admin_report, timestamp, 
           res_timestamp, admin_id, and author_type.
           Optionally, user_id.
    """
    session = orm.start_session()
    user_report = orm.UserReport(report_text=report_text, 
        report_type=report_type, author_type=author_type, 
        admin_report=admin_report, timestamp=timestamp, admin_id=admin_id, 
        res_timestamp=res_timestamp, content_id=content_id)
    if author_type == "U" and user_id is not None:
        user_report.author_id = user_id

    session.add(user_report)
    try:
        session.commit()
    except:
        session.rollback()
        raise ActionError(str(sys.exc_info()[0]))