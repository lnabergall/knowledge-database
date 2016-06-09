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
    change_user_type, delete_user, store_user_report

    Note that all functions take a common 'session' keyword argument,
    with default value None.
"""
from sqlalchemy.orm.exc import (NoResultFound, ObjectDeletedError,
                                StaleDataError)
from sqlalchemy.exc import IntegrityError

from . import orm_core as orm
from .orm_core import ActionError
from .select_queries import InputError, get_user, get_content_piece


UNIQUE_CONSTRAINT_VIOLATION = "23505"


class MissingDataError(Exception):
    """Exception raised when a query unexpectedly returns no results."""


class UniquenessViolationError(Exception):
    """Exception raised when a query violates a unique constraint."""


def store_content_piece(user_id, name, text, content_type, keywords, timestamp,
                        citations=None, alternate_names=None, session=None):
    """
    Args:
        user_id: Integer.
        name: Name.
        text: Text.
        content_type: ContentType.
        keywords: list of Keywords.
        timestamp: Datetime.
        citations: list of Citations. Defaults to None.
        alternate_names: list of Names of type 'alternate'. Defaults to None.
        session: SQLAlchemy session. Defaults to None.
    Raises:
        ActionError: if session is provided and committing changes fails.
    """
    try:
        if session is None:
            session = orm.start_session()
        content_piece = orm.ContentPiece(timestamp=timestamp, 
                                         last_edited_timestamp=timestamp)
        author = get_user(user_id=user_id, session=session)
        content_piece.first_author = author
        content_piece.authors.append(author)

        content_piece.name = name
        if alternate_names is not None:
            content_piece.alternate_names = alternate_names

        content_piece.text = text
        content_piece.content_type = content_type
        content_piece.keywords = keywords

        if citations is not None:
            content_piece.citations = citations

        session.add(content_piece)
        session.flush()
    except Exception as e:
        raise ActionError(str(e))
    else:
        return content_piece.content_id


def delete_content_piece(content_id, deleted_timestamp, session=None):
    """
    Args:
        content_id: Integer.
        deleted_timestamp: datetime.
        session: SQLAlchemy session. Defaults to None.
    Raises:
        ActionError: if session is provided and committing changes fails.
    """
    try:
        if session is None:
            session = orm.start_session()
        session.query(orm.ContentPiece).filter(
            orm.ContentPiece.content_id == content_id).update(
            {orm.ContentPiece.deleted_timestamp: deleted_timestamp},
            synchronize_session=False)
        session.flush()
    except Exception as e:
        raise ActionError(str(e))


def update_content_type(content_id, content_type, session=None):
    """
    Args:
        content_id: Integer.
        content_type: ContentType.
        session: SQLAlchemy session. Defaults to None.
    Raises:
        ActionError: if session is provided and committing changes fails.
    """
    try:
        if session is None:
            session = orm.start_session()
        content_piece = get_content_piece(content_id, session=session)
        content_piece.content_type = content_type
        session.flush()
    except Exception as e:
        raise ActionError(str(e))


def store_content_part(content_part, content_id,
                       edited_citations=None, session=None):
    """
    Args:
        content_part: Name, Keyword, or Citation.
        content_id: Integer.
        edited_citations: List of Citation objects.
        session: SQLAlchemy session. Defaults to None.
    Raises:
        InputError: if content_part is not a Name, Keyword, or Citation.
        ActionError: if session is provided and committing changes fails.
    """
    try:
        if session is None:
            session = orm.start_session()
        content_piece = get_content_piece(content_id, session=session)
        if isinstance(content_part, orm.Name):
            content_piece.alternate_names.append(content_part)
        elif isinstance(content_part, orm.Keyword):
            content_piece.keywords.append(content_part)
        elif isinstance(content_part, orm.Citation):
            if edited_citations is not None:
                content_part.edited_citations = edited_citations
            content_piece.citations.append(content_part)
        else:
            raise InputError("Invalid argument!")
        session.flush()
    except Exception as e:
        raise ActionError(str(e))


def remove_content_part(content_id, part_id, content_part, session=None):
    """
    Deletes name or removes association between content piece and
    keyword/citation.

    Args:
        content_id: Integer.
        part_id: Integer.
        content_part: String, accepts 'keyword', 'citation', or 'name'.
        session: SQLAlchemy session. Defaults to None.
    Raises:
        InputError: if content_part != 'keyword', 'citation', or 'name'.
        ActionError: if session is provided and committing changes fails.
    """
    try:
        if session is None:
            session = orm.start_session()
        if content_part == "keyword":
            session.execute(orm.content_keywords.delete(),
                params={"keyword_id": part_id, "content_id": content_id})
        elif content_part == "citation":
            session.query(orm.ContentPieceCitation).filter(
                orm.ContentPieceCitation.content_id == content_id).filter(
                orm.ContentPieceCitation.citation_id == part_id).delete(
                synchronize_session=False)
        elif content_part == "name":
            session.query(orm.Name).filter(orm.Name.name_id == part_id).delete(
                synchronize_session=False)
        else:
            raise InputError("Invalid argument!")
        session.flush()
    except (NoResultFound, StaleDataError, ObjectDeletedError) as e:
        raise MissingDataError(str(e))
    except Exception as e:
        raise ActionError(str(e))


def update_content_part(part_id, content_part, part_text, session=None):
    """
    Args:
        part_id: Integer.
        content_part: String, accepts 'name' or 'text'.
        part_text: String.
        session: SQLAlchemy session. Defaults to None.
    Raises:
        InputError: if content_part != 'name' or 'text'.
        ActionError: if session is provided and committing changes fails.
    """
    try:
        if session is None:
            session = orm.start_session()
        if content_part == "name":
            session.query(orm.Name).filter(orm.Name.name_id == part_id).update(
                {orm.Name.name: part_text}, synchronize_session=False)
        elif content_part == "text":
            session.query(orm.Text).filter(orm.Text.text_id == part_id).update(
                {orm.Text.text: part_text}, synchronize_session=False)
        else:
            raise InputError("Invalid argument!")
        session.flush()
    except Exception as e:
        raise ActionError(str(e))


def store_accepted_edit(redis_edit_id, edit_text, applied_edit_text,
                        edit_rationale, content_part, part_id, content_id,
                        vote_string, voter_ids, start_timestamp, timestamp,
                        acc_timestamp, author_type, user_id=None, session=None):
    """
    Args:
        redis_edit_id: Integer.
        edit_text: String.
        applied_edit_text: String.
        edit_rationale: String.
        content_part: String, accepts 'name', 'text', 'content_type',
            'keyword' or 'citation'.
        part_id: Integer.
        content_id: Integer.
        vote_string: String.
        voter_ids: list of Integers.
        start_timestamp: Datetime.
        timestamp: Datetime.
        acc_timestamp: Datetime.
        author_type: String, expects 'U' or an IP address.
        user_id: Integer. Defaults to None.
        session: SQLAlchemy session. Defaults to None.
    Raises:
        InputError: if content_part != 'name', 'text', 'keyword',
            or 'citation'.
        ActionError: if session is provided and committing changes fails.
    """
    try:
        if session is None:
            session = orm.start_session()
        vote = orm.Vote(vote=vote_string, content_part=content_part,
                        timestamp=timestamp, close_timestamp=acc_timestamp)
        session.add(vote)
        session.flush()     # To get vote.vote_id
        for user_id in voter_ids:
            session.begin_nested()
            try:
                session.execute(orm.user_votes.insert(),
                    params={"vote_id": vote.vote_id, "user_id": user_id})
            except IntegrityError as e:
                if e.orig.pgcode != UNIQUE_CONSTRAINT_VIOLATION:
                    raise
                else:
                    session.rollback()
            else:
                session.commit()
        edit = orm.AcceptedEdit(redis_edit_id=redis_edit_id, edit_text=edit_text,
                                applied_edit_text=applied_edit_text,
                                edit_rationale=edit_rationale,
                                content_part=content_part,
                                start_timestamp=start_timestamp,
                                timestamp=timestamp, acc_timestamp=acc_timestamp,
                                content_id=content_id, author_type=author_type)
        edit.vote = vote
        if author_type == "U" and user_id is not None:
            edit.author_id = user_id
            session.begin_nested()
            try:
                session.execute(orm.content_authors.insert(),
                    params={"content_id": content_id, "user_id": user_id})
            except IntegrityError as e:
                if e.orig.pgcode != UNIQUE_CONSTRAINT_VIOLATION:
                    raise
                else:
                    session.rollback()
            else:
                session.commit()
        if content_part == "name":
            session.query(orm.Name).filter(orm.Name.name_id == part_id).update(
                {orm.Name.last_edited_timestamp: acc_timestamp}, 
                synchronize_session=False)
            edit.name_id = part_id
        elif content_part == "text":
            session.query(orm.Text).filter(orm.Text.text_id == part_id).update(
                {orm.Text.last_edited_timestamp: acc_timestamp}, 
                synchronize_session=False)
            edit.text_id = part_id
        elif content_part == "content_type":
            edit.content_type_id = part_id
        elif content_part == "keyword":
            edit.keyword_id = part_id
        elif content_part == "citation":
            edit.citation_id = part_id
        else:
            raise InputError("Invalid argument!")
        session.query(orm.ContentPiece).filter(
            orm.ContentPiece.content_id == content_id).update(
            {orm.ContentPiece.last_edited_timestamp: acc_timestamp}, 
            synchronize_session=False)
        session.add(edit)
        session.flush()
    except Exception as e:
        raise ActionError(str(e))
    else:
        return edit.edit_id


def store_rejected_edit(redis_edit_id, edit_text, edit_rationale, content_part,
                        part_id, content_id, vote_string, voter_ids, timestamp,
                        rej_timestamp, author_type, user_id=None, session=None):
    """
    Args:
        redis_edit_id: Integer.
        edit_text: String.
        edit_rationale: String.
        content_part: String, accepts 'name', 'text', 'content_type',
            'keyword' or 'citation'.
        part_id: Integer.
        content_id: Integer.
        vote_string: String.
        voter_ids: list of Integers.
        timestamp: Datetime.
        rej_timestamp: Datetime.
        author_type: String, expects 'U' or an IP address.
        user_id: Integer. Defaults to None.
        session: SQLAlchemy session. Defaults to None.
    Raises:
        InputError: if content_part != 'name', 'text', 'keyword',
            or 'citation'.
        ActionError: if session is provided and committing changes fails.
    """
    try:
        if session is None:
            session = orm.start_session()
        vote = orm.Vote(vote=vote_string, content_part=content_part,
                        timestamp=timestamp, close_timestamp=rej_timestamp)
        session.add(vote)
        session.flush()     # To get vote.vote_id
        for user_id in voter_ids:
            session.begin_nested()
            try:
                session.execute(orm.user_votes.insert(),
                    params={"vote_id": vote.vote_id, "user_id": user_id})
            except IntegrityError as e:
                if e.orig.pgcode != UNIQUE_CONSTRAINT_VIOLATION:
                    raise
                else:
                    session.rollback()
            else:
                session.commit()
        edit = orm.RejectedEdit(redis_edit_id=redis_edit_id, edit_text=edit_text,
                                edit_rationale=edit_rationale,
                                content_part=content_part, timestamp=timestamp,
                                rej_timestamp=rej_timestamp, content_id=content_id,
                                author_type=author_type)
        edit.vote = vote
        if author_type == "U" and user_id is not None:
            edit.author_id = user_id
        if content_part == "name":
            edit.name_id = part_id
        elif content_part == "text":
            edit.text_id = part_id
        elif content_part == "content_type":
            edit.content_type_id = part_id
        elif content_part == "keyword":
            edit.keyword_id = part_id
        elif content_part == "citation":
            edit.citation_id = part_id
        else:
            raise InputError("Invalid argument!")

        session.add(edit)
        session.flush()
    except Exception as e:
        raise ActionError(str(e))
    else:
        return edit.edit_id


def store_new_user(user_type, user_name, email, pass_hash,
                   pass_hash_type, pass_salt, remember_id, timestamp,
                   session=None):
    """
    Args:
        user_type: String, expects 'standard' or 'admin'.
        user_name: String.
        email: String.
        pass_hash: String.
        pass_hash_type: String.
        pass_salt: String.
        timestamp: Datetime.
        session: SQLAlchemy session. Defaults to None.
    Raises:
        ActionError: if session is provided and committing changes fails.
    """
    try:
        if session is None:
            session = orm.start_session()
        user = orm.User(user_type=user_type, user_name=user_name, email=email,
                        pass_hash=pass_hash, pass_hash_type=pass_hash_type,
                        pass_salt=pass_salt, remember_id=remember_id,
                        timestamp=timestamp)
        session.add(user)
        session.flush()
    except IntegrityError as e:
        if e.orig.pgcode == UNIQUE_CONSTRAINT_VIOLATION:
            raise UniquenessViolationError(str(e))
        else:
            raise
    except Exception as e:
        raise ActionError(str(e))
    else:
        return user.user_id


def update_user(user_id, new_user_name=None, new_email=None,
                confirmed_timestamp=None, new_pass_hash=None,
                new_pass_hash_type=None, new_pass_salt=None,
                new_remember_token_hash=None,
                new_remember_hash_type=None, session=None):
    """
    Args:
        user_id: Integer.
        new_user_name: String. Defaults to None.
        new_email: String. Defaults to None.
        confirmed_timestamp: datetime. Defaults to None.
        new_pass_hash: String. Defaults to None.
        new_pass_hash_type: String. Defaults to None.
        new_pass_salt: String. Defaults to None.
        new_remember_token_hash: String. Defaults to None.
        new_remember_hash_type: String. Defaults to None.
        session: SQLAlchemy session. Defaults to None.
    Raises:
        InputError: if new_user_name is None, new_email is None,
            confirmed_timestamp is None, new_pass_hash or new_pass_hash_type
            or new_pass_salt is None, and new_remember_token_hash or
            new_remember_hash_type is None.
        ActionError: if session is provided and committing changes fails.
    """
    try:
        if session is None:
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
        session.flush()
    except Exception as e:
        raise ActionError(str(e))


def change_user_type(user_id, user_type, session=None):
    """
    Args:
        user_id: Integer.
        user_type: String, expects 'standard' or 'admin'.
        session: SQLAlchemy session. Defaults to None.
    Raises:
        ActionError: if session is provided and committing changes fails.
    """
    try:
        if session is None:
            session = orm.start_session()
        session.query(orm.User).filter(orm.User.user_id == user_id).update(
            {orm.User.user_type: user_type}, synchronize_session=False)
        session.flush()
    except Exception as e:
        raise ActionError(str(e))


def delete_user(user_id, deleted_timestamp=None, permanently=False, session=None):
    """
    Args:
        user_id: Integer.
        deleted_timestamp: Datetime. Defaults to None.
        permanently: Boolean, if True, the user's data is permanently
            deleted from the database. Defaults to False.
        session: SQLAlchemy session. Defaults to None.
    Raises:
        ActionError: if session is provided and committing changes fails.
    """
    try:
        if session is None:
            session = orm.start_session()
        if permanently:
            session.query(orm.User).filter(orm.User.user_id == user_id).delete()
        else:
            session.query(orm.User).filter(orm.User.user_id == user_id).update(
                {orm.User.deleted_timestamp: deleted_timestamp},
                synchronize_session=False)
        session.flush()
    except Exception as e:
        raise ActionError(str(e))


def store_user_report(content_id, report_text, report_type, admin_report,
                      timestamp, res_timestamp, admin_id, author_type,
                      user_id=None, session=None):
    """
    Args:
        content_id: Integer.
        report_text: String.
        report_type: String, expects 'content' or 'authors'.
        admin_report: String.
        timestamp: Datetime.
        res_timestamp: Datetime.
        admin_id: Integer.
        author_type: String, expects 'U' or an IP address.
        user_id: Integer. Defaults to None.
        session: SQLAlchemy session. Defaults to None.
    Raises:
        ActionError: if session is provided and committing changes fails.
    """
    try:
        if session is None:
            session = orm.start_session()
        user_report = orm.UserReport(report_text=report_text,
            report_type=report_type, author_type=author_type,
            admin_report=admin_report, timestamp=timestamp, admin_id=admin_id,
            res_timestamp=res_timestamp, content_id=content_id)
        if author_type == "U" and user_id is not None:
            user_report.author_id = user_id
        session.add(user_report)
        session.flush()
    except Exception as e:
        raise ActionError(str(e))
    else:
        return user_report.report_id
