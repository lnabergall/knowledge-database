"""
Storage Selection Query API

Contains functions and classes for making selections from the Postgres 
database. Uses SQLAlchemy.

Exceptions:

    SelectError, InputError, MultipleValuesFound

Functions:

    get_content_piece, get_content_pieces, get_part_string, get_names,
    get_alternate_names, get_keyword, get_keywords, get_citation,
    get_citations, get_content_type, get_content_types, get_accepted_edits,
    get_rejected_edits, get_user_votes, get_accepted_votes,
    get_rejected_votes, get_user_encrypt_info, get_author_count, get_user,
    get_user_info, get_admin_ids, get_user_reports

    Note that all functions take a common 'session' keyword argument,
    which defaults to None.
"""

from sqlalchemy.orm import subqueryload
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.sql.expression import desc

from . import orm_core as orm
from .orm_core import Query


class MultipleValuesFound(ValueError, MultipleResultsFound):
    """
    Exception raised by :meth:'Query.values' when multiple value were
    found in a single result row.
    """


class SelectError(Exception):
    """
    General exception raised when a database select query returns an
    invalid result.
    """


class InputError(Exception):
    """
    General exception raised when a function is called with invalid
    argument values.
    """


def get_content_piece(content_id=None, accepted_edit_id=None,
                      rejected_edit_id=None, session=None):
    """
    Args:
        content_id: Integer. Defaults to None.
        accepted_edit_id: Integer. Defaults to None.
        rejected_edit_id: Integer. Defaults to None.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        ContentPiece: if content piece matching content_id or associated
            with accepted_edit_id or rejected_edit_id is found.
    Raises:
        SelectError: if content_id does not match any row in the
            Content_Piece table or accepted_edit_id or rejected_edit_id
            are not associated with any content piece.
    """
    if session is None:
        session = orm.start_session()
    try:
        if content_id is not None:
            content_piece = session.query(orm.ContentPiece).options(
                subqueryload(orm.ContentPiece.first_author),
                subqueryload(orm.ContentPiece.authors),
                subqueryload(orm.ContentPiece.content_type),
                subqueryload(orm.ContentPiece.name),
                subqueryload(orm.ContentPiece.alternate_names),
                subqueryload(orm.ContentPiece.text),
                subqueryload(orm.ContentPiece.keywords)).filter(
                orm.ContentPiece.content_id == content_id).one()
        elif accepted_edit_id is not None:
            content_piece = session.query(orm.ContentPiece).join(
                orm.AcceptedEdit).options(
                subqueryload(orm.ContentPiece.first_author),
                subqueryload(orm.ContentPiece.authors),
                subqueryload(orm.ContentPiece.content_type),
                subqueryload(orm.ContentPiece.name),
                subqueryload(orm.ContentPiece.alternate_names),
                subqueryload(orm.ContentPiece.text),
                subqueryload(orm.ContentPiece.keywords)).filter(
                orm.AcceptedEdit.edit_id == accepted_edit_id).one()
        elif rejected_edit_id is not None:
            content_piece = session.query(orm.ContentPiece).join(
                orm.RejectedEdit).options(
                subqueryload(orm.ContentPiece.first_author),
                subqueryload(orm.ContentPiece.authors),
                subqueryload(orm.ContentPiece.content_type),
                subqueryload(orm.ContentPiece.name),
                subqueryload(orm.ContentPiece.alternate_names),
                subqueryload(orm.ContentPiece.text),
                subqueryload(orm.ContentPiece.keywords)).filter(
                orm.RejectedEdit.edit_id == rejected_edit_id).one()
        else:
            raise InputError("Missing argument!")
    except (NoResultFound, MultipleResultsFound) as e:
        raise SelectError(str(e))
    else:
        return content_piece


def get_content_pieces(sort="created_at", content_part=None, user_id=None,
                       page_num=None, per_page=10, session=None):
    """
    Args:
        sort: String, accepts 'created_at' or 'last_edited_at'.
            Defaults to 'created_at'.
        content_part: String, accepts 'keyword', 'content_type', 'name',
            or 'citation'. Defaults to None.
        user_id: Integer. Defaults to None.
        page_num: Integer. Defaults to None.
        per_page: Integer. Defaults to 10.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        list of ContentPieces that user_id has authored.
    """
    if session is None:
        session = orm.start_session()
    if user_id:
        content_pieces = session.query(orm.ContentPiece).options(
            subqueryload("*")).join(orm.User, orm.ContentPiece.authors).filter(
            orm.User.user_id == user_id)
    elif content_part:
        if content_part == "keyword":
            content_pieces = session.query(orm.ContentPiece).join(orm.Keyword,
                orm.ContentPiece.keywords).options(subqueryload("*")).filter(
                orm.Keyword.keyword == content_part)
        elif content_part == "content_type":
            content_pieces = session.query(orm.ContentPiece).join(orm.ContentType,
                orm.ContentPiece.content_type).options(subqueryload("*")).filter(
                orm.ContentType.content_type == content_part)
        elif content_part == "name":
            content_pieces = session.query(orm.ContentPiece).join(orm.Name,
                orm.ContentPiece.name).options(subqueryload("*")).filter(
                orm.Name.name == content_part)
        elif content_part == "citation":
            content_pieces = session.query(orm.ContentPiece).join(
                orm.ContentPieceCitation).join(orm.Citation,
                orm.ContentPieceCitation.citation).options(subqueryload("*")).filter(
                orm.Citation.citation_text == content_part)
        else:
            raise InputError("Invalid argument!")
    else:
        content_pieces = session.query(orm.ContentPiece).options(
            subqueryload("*"))

    if sort == "created_at":
        content_pieces = content_pieces.order_by(orm.ContentPiece.timestamp).offset(
            (page_num-1)*per_page).limit(per_page)
    elif sort == "last_edited_at":
        content_pieces = content_pieces.order_by(
            orm.ContentPiece.last_edited_timestamp).offset(
            (page_num-1)*per_page).limit(per_page)
    else:
        raise InputError("Invalid argument!")

    return content_pieces.all()


def get_part_string(part_id, content_part, session=None):
    """
    Args:
        part_id: Integer.
        content_part: String, accepts 'text', 'name', 'alternate_name',
            'content_type', 'keyword', or 'citation'.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        String of the content part of type content_part with
        primary key part_id.
    """
    if session is None:
        session = orm.start_session()
    try:
        if content_part == "text":
            part_string = session.query(orm.Text.text).filter(
                orm.Text.text_id == part_id).one()
        elif content_part == "name" or content_part == "alternate_name":
            part_string = session.query(orm.Name.name).filter(
                orm.Name.name_id == part_id).one()
        elif content_part == "citation":
            part_string = session.query(orm.Citation.citation_text).filter(
                orm.Citation.citation_id == part_id).one()
        elif content_part == "content_type":
            part_string = session.query(orm.ContentType.content_type).filter(
                orm.ContentType.content_type_id == part_id).one()
        elif content_part == "keyword":
            part_string = session.query(orm.Keyword.keyword).filter(
                orm.Keyword.keyword_id == part_id).one()
        else:
            raise InputError("Invalid argument!")
    except (NoResultFound, MultipleResultsFound) as e:
        raise SelectError(str(e))
    else:
        return part_string


def get_names(content_id=None, content_ids=None, session=None):
    """
    Args:
        content_id: Integer. Defaults to None.
        content_ids: Integer. Defaults to None.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        Name or list of tuples of the form (content_id, Name).
    """
    if session is None:
        session = orm.start_session()
    if content_id is not None:
        try:
            name = session.query(orm.Name).join(
                orm.ContentPiece, orm.Name.piece_).filter(
                orm.ContentPiece.content_id == content_id).one()
        except (NoResultFound, MultipleResultsFound) as e:
            raise SelectError(str(e))
        return name
    elif content_ids is not None:
        if content_ids:
            names = session.query(orm.Name).join(
                orm.ContentPiece, orm.Name.piece_).filter(
                orm.ContentPiece.content_id.in_(content_ids)).all()
        else:
            names = []
        return names
    else:
        raise InputError("Missing argument!")


def get_alternate_names(content_id, session=None):
    """
    Args:
        content_id: Integer.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        list of Names.
    """
    if session is None:
        session = orm.start_session()
    alternate_names = session.query(orm.Name).join(
        orm.ContentPiece, orm.Name.piece).filter(
        orm.ContentPiece.content_id == content_id)
    return alternate_names.all()


def get_keyword(keyword_string, session=None):
    """
    Args:
        keyword_string: String.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        Keyword: if keyword matching keyword_string is found.
    Raises:
        SelectError: if keyword_string does not match any row in the
            Keyword table.
    """
    if session is None:
        session = orm.start_session()
    try:
        keyword = session.query(orm.Keyword).filter(
            orm.Keyword.keyword == keyword_string).one()
    except (NoResultFound, MultipleResultsFound) as e:
        raise SelectError(str(e))
    else:
        return keyword


def get_keywords(content_id=None, page_num=None, per_page=None, session=None):
    """
    Args:
        content_id: Integer. Defaults to None.
        page_num: Integer. Defaults to None.
        per_page: Integer. Defaults to None.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        list of Keywords.
    """
    if session is None:
        session = orm.start_session()
    if content_id:
        keywords = session.query(orm.Keyword).join(
            orm.ContentPiece, orm.Keyword.pieces).filter(
            orm.ContentPiece.content_id == content_id)
    elif page_num and per_page:
        keywords = session.query(orm.Keyword).order_by(
            orm.Keyword.keyword).offset((page_num-1)*per_page).limit(per_page)
    else:
        raise InputError("Invalid arguments!")

    return keywords.all()


def get_citation(citation_string, session=None):
    """
    Args:
        citation_string: String.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        Citation: if citation matching citation_string is found.
    Raises:
        SelectError: if citation_string does not match any row in the
            Citation table.
    """
    if session is None:
        session = orm.start_session()
    try:
        citation = session.query(orm.Citation).filter(
            orm.Citation.citation_text == citation_string).one()
    except (NoResultFound, MultipleResultsFound) as e:
        raise SelectError(str(e))
    else:
        return citation


def get_citations(content_id=None, citation_id=None, edited_citation_id=None,
                  page_num=None, per_page=None, session=None):
    """
    Args:
        content_id: Integer. Defaults to None.
        citation_id: Integer. Defaults to None.
        edited_citation_id: Integer. Defaults to None.
        page_num: Integer. Defaults to None.
        per_page: Integer. Defaults to None.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        list of Citations.
    """
    if session is None:
        session = orm.start_session()
    if citation_id is not None and content_id is not None:
        citations = session.query(orm.Citation).join(
            orm.ContentPieceCitation, orm.Citation.edited_citation).filter(
            orm.ContentPieceCitation.citation_id == citation_id).filter(
            orm.ContentPieceCitation.content_id == content_id)
    elif edited_citation_id is not None and content_id is not None:
        citations = session.query(orm.Citation).join(
            orm.ContentPieceCitation, orm.Citation.editing_citations).filter(
            orm.ContentPieceCitation.edited_citation_id == edited_citation_id).filter(
            orm.ContentPieceCitation.content_id == content_id)
    elif content_id is not None:
        citations = session.query(orm.Citation).join(
            orm.ContentPieceCitation, orm.Citation.citation_content_pieces).filter(
            orm.ContentPieceCitation.content_id == content_id)
    elif page_num and per_page:
        citations = session.query(orm.Citation).offset(
            (page_num-1)*per_page).limit(per_page)
    else:
        raise InputError("Invalid arguments!")

    return citations.all()


def get_content_type(content_type_string, session=None):
    """
    Args:
        content_type_string: String.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        ContentType: if content type matching content_type_string is found.
    Raises:
        SelectError: if content_type_string does not match any row in the
            Content_Type table.
    """
    if session is None:
        session = orm.start_session()
    try:
        content_type = session.query(orm.ContentType).filter(
            orm.ContentType.content_type == content_type_string).one()
    except (NoResultFound, MultipleResultsFound) as e:
        raise SelectError(str(e))
    else:
        return content_type


def get_content_types(session=None):
    """
    Args:
        session: SQLAlchemy session. Defaults to None.
    Returns:
        list of ContentTypes.
    """
    if session is None:
        session = orm.start_session()
    content_types = session.query(orm.ContentType).all()
    return content_types


def get_accepted_edits(content_id=None, edit_id=None, redis_edit_id=None,
                       user_id=None, text_id=None, name_id=None,
                       citation_id=None, keyword_id=None, content_type_id=None,
                       content_ids=None, ip_address=None, session=None):
    """
    Args:
        content_id: Integer. Defaults to None.
        edit_id: Integer. Defaults to None.
        redis_edit_id: Integer. Defaults to None.
        user_id: Integer. Defaults to None.
        text_id: Integer. Defaults to None.
        name_id: Integer. Defaults to None.
        citation_id: Integer. Defaults to None.
        keyword_id: Integer. Defaults to None.
        content_type_id: Integer. Defaults to None.
        content_ids: List of Integers. Defaults to None.
        ip_address: String. Defaults to None.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        AcceptedEdit or list of AcceptedEdits.
    Raises:
        SelectError: if edit_id does not match any row in the
            Accepted_Edit table.
        InputError: if all arguments are None.
    """
    if session is None:
        session = orm.start_session()
    if user_id is not None:
        accepted_edits = session.query(orm.AcceptedEdit).join(
            orm.User).filter(orm.User.user_id == user_id)
    elif ip_address is not None:
        accepted_edits = session.query(orm.AcceptedEdit).filter(
            orm.AcceptedEdit.author_type == ip_address)
    elif text_id is not None:
        accepted_edits = session.query(orm.AcceptedEdit).join(
            orm.Text).filter(orm.Text.text_id == text_id)
    elif name_id is not None:
        accepted_edits = session.query(orm.AcceptedEdit).join(
            orm.Name).filter(orm.Name.name_id == name_id)
    elif citation_id is not None and content_id is not None:
        accepted_edits = session.query(orm.AcceptedEdit).join(
            orm.Citation).join(orm.ContentPiece).filter(
            orm.Citation.citation_id == citation_id).filter(
            orm.ContentPiece.content_id == content_id)
    elif citation_id is not None:
        accepted_edits = session.query(orm.AcceptedEdit).join(
            orm.Citation).filter(orm.Citation.citation_id == citation_id)
    elif keyword_id is not None and content_id is not None:
        accepted_edits = session.query(orm.AcceptedEdit).join(
            orm.Keyword).join(orm.ContentPiece).filter(
            orm.Keyword.keyword_id == keyword_id).filter(
            orm.ContentPiece.content_id == content_id)
    elif keyword_id is not None:
        accepted_edits = session.query(orm.AcceptedEdit).join(
            orm.Keyword).filter(orm.Keyword.keyword_id == keyword_id)
    elif content_type_id is not None and content_id is not None:
        accepted_edits = session.query(orm.AcceptedEdit).join(
            orm.ContentType).join(orm.ContentPiece).filter(
            orm.ContentType.content_type_id == content_type_id).filter(
            orm.ContentPiece.content_id == content_id)
    elif content_type_id is not None:
        accepted_edits = session.query(orm.AcceptedEdit).join(
            orm.ContentType).filter(orm.ContentType.content_type_id
            == content_type_id)
    elif content_id is not None:
        accepted_edits = session.query(orm.AcceptedEdit).join(
            orm.ContentPiece).filter(
            orm.ContentPiece.content_id == content_id)
    elif content_ids is not None:
        if content_ids:
            accepted_edits = session.query(orm.AcceptedEdit).join(
                orm.ContentPiece).filter(
                orm.ContentPiece.content_id.in_(content_ids))
        else:
            accepted_edits = []
    elif edit_id is not None:
        try:
            accepted_edit = session.query(orm.AcceptedEdit).options(
                subqueryload(orm.AcceptedEdit.author)).filter(
                orm.AcceptedEdit.edit_id == edit_id).one()
        except (NoResultFound, MultipleResultsFound) as e:
            raise SelectError(str(e))
        else:
            return accepted_edit
    elif redis_edit_id is not None:
        try:
            accepted_edit = session.query(orm.AcceptedEdit).options(
                subqueryload(orm.AcceptedEdit.author)).filter(
                orm.AcceptedEdit.redis_edit_id == redis_edit_id).one()
        except (NoResultFound, MultipleResultsFound) as e:
            raise SelectError(str(e))
        else:
            return accepted_edit
    else:
        raise InputError("No arguments!")

    try:
        return accepted_edits.all()
    except:
        return []


def get_rejected_edits(content_id=None, edit_id=None, redis_edit_id=None,
                       user_id=None, text_id=None, name_id=None,
                       citation_id=None, keyword_id=None, content_type_id=None,
                       content_ids=None, ip_address=None, session=None):
    """
    Args:
        content_id: Integer. Defaults to None.
        edit_id: Integer. Defaults to None.
        redis_edit_id: Integer. Defaults to None.
        user_id: Integer. Defaults to None.
        text_id: Integer. Defaults to None.
        name_id: Integer. Defaults to None.
        citation_id: Integer. Defaults to None.
        keyword_id: Integer. Defaults to None.
        content_type_id: Integer. Defaults to None.
        content_ids: List of Integers. Defaults to None.
        ip_address: String. Defaults to None.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        RejectedEdit or list of RejectedEdits.
    Raises:
        SelectError: if edit_id does not match any row in the
            Rejected_Edit table.
        InputError: if all arguments are None.
    """
    if session is None:
        session = orm.start_session()
    if user_id is not None:
        rejected_edits = session.query(orm.RejectedEdit).join(
            orm.User).filter(orm.User.user_id == user_id)
    elif ip_address is not None:
        rejected_edits = session.query(orm.RejectedEdit).filter(
            orm.RejectedEdit.author_type == ip_address)
    elif text_id is not None:
        rejected_edits = session.query(orm.RejectedEdit).join(
            orm.Text).filter(orm.Text.text_id == text_id)
    elif name_id is not None:
        rejected_edits = session.query(orm.RejectedEdit).join(
            orm.Name).filter(orm.Name.name_id == name_id)
    elif citation_id is not None and content_id is not None:
        rejected_edits = session.query(orm.RejectedEdit).join(
            orm.Citation).join(orm.ContentPiece).filter(
            orm.Citation.citation_id == citation_id).filter(
            orm.ContentPiece.content_id == content_id)
    elif citation_id is not None:
        rejected_edits = session.query(orm.RejectedEdit).join(
            orm.Citation).filter(orm.Citation.citation_id == citation_id)
    elif keyword_id is not None and content_id is not None:
        rejected_edits = session.query(orm.RejectedEdit).join(
            orm.Keyword).join(orm.ContentPiece).filter(
            orm.Keyword.keyword_id == keyword_id).filter(
            orm.ContentPiece.content_id == content_id)
    elif keyword_id is not None:
        rejected_edits = session.query(orm.RejectedEdit).join(
            orm.Keyword).filter(orm.Keyword.keyword_id == keyword_id)
    elif content_type_id is not None and content_id is not None:
        rejected_edits = session.query(orm.RejectedEdit).join(
            orm.ContentType).join(orm.ContentPiece).filter(
            orm.ContentType.content_type_id == content_type_id).filter(
            orm.ContentPiece.content_id == content_id)
    elif content_type_id is not None:
        rejected_edits = session.query(orm.RejectedEdit).join(
            orm.ContentType).filter(orm.ContentType.content_type_id
            == content_type_id).order_by(desc(
            orm.RejectedEdit.rej_timestamp))
    elif content_id is not None:
        rejected_edits = session.query(orm.RejectedEdit).join(
            orm.ContentPiece).filter(
            orm.ContentPiece.content_id == content_id)
    elif content_ids is not None:
        if content_ids:
            rejected_edits = session.query(orm.RejectedEdit).join(
                orm.ContentPiece).filter(
                orm.ContentPiece.content_id.in_(content_ids))
        else:
            rejected_edits = []
    elif edit_id is not None:
        try:
            rejected_edit = session.query(orm.RejectedEdit).options(
                subqueryload(orm.RejectedEdit.author)).filter(
                orm.RejectedEdit.edit_id == edit_id).one()
        except (NoResultFound, MultipleResultsFound) as e:
            raise SelectError(str(e))
        else:
            return rejected_edit
    elif redis_edit_id is not None:
        try:
            rejected_edit = session.query(orm.RejectedEdit).options(
                subqueryload(orm.RejectedEdit.author)).filter(
                orm.RejectedEdit.redis_edit_id == redis_edit_id).one()
        except (NoResultFound, MultipleResultsFound) as e:
            raise SelectError(str(e))
        else:
            return rejected_edit
    else:
        raise InputError("No arguments!")

    try:
        return rejected_edits.all()
    except:
        return []


def get_user_votes(user_id, session=None):
    """
    Args:
        user_id: Integer.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        list of Votes.
    """
    if session is None:
        session = orm.start_session()
    votes = session.query(orm.Vote).join(orm.User, orm.Vote.voters).filter(
        orm.User.user_id == user_id)
    return votes.all()


def get_accepted_votes(content_id=None, edit_id=None, vote_id=None,
                       user_id=None, ip_address=None, session=None):
    """
    Args:
        content_id: Integer. Defaults to None.
        edit_id: Integer. Defaults to None.
        vote_id: Integer. Defaults to None.
        user_id: Integer. Defaults to None.
        ip_address: String. Defaults to None.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        Vote or list of Votes.
    Raises:
        SelectError: if edit_id does not match any row in the
            AcceptedEdit table or vote_id does not match any row
            in the Vote table.
        InputError: if all arguments are None.
    """
    if session is None:
        session = orm.start_session()
    if content_id is not None:
        votes = session.query(orm.Vote).join(orm.AcceptedEdit).join(
            orm.ContentPiece).filter(orm.ContentPiece.content_id
                                     == content_id)
    elif user_id is not None:
        votes = session.query(orm.Vote).join(orm.AcceptedEdit).join(
            orm.User).filter(orm.User.user_id == user_id)
    elif ip_address is not None:
        votes = session.query(orm.Vote).join(orm.AcceptedEdit).filter(
            orm.AcceptedEdit.author_type == ip_address)
    elif edit_id is not None:
        try:
            vote = session.query(orm.Vote).join(orm.AcceptedEdit).filter(
                orm.AcceptedEdit.edit_id == edit_id).one()
        except (NoResultFound, MultipleResultsFound) as e:
            raise SelectError(str(e))
        else:
            return vote
    elif vote_id is not None:
        try:
            vote = session.query(orm.Vote).filter(
                orm.Vote.vote_id == vote_id).one()
        except (NoResultFound, MultipleResultsFound) as e:
            raise SelectError(str(e))
        else:
            return vote
    else:
        raise InputError("No arguments!")

    return votes.all()


def get_rejected_votes(content_id=None, edit_id=None, vote_id=None,
                       user_id=None, ip_address=None, session=None):
    """
    Args:
        content_id: Integer. Defaults to None.
        edit_id: Integer. Defaults to None.
        vote_id: Integer. Defaults to None.
        user_id: Integer. Defaults to None.
        ip_address: String. Defaults to None.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        Vote or list of Votes.
    Raises:
        SelectError: if edit_id does not match any row in the
            RejectedEdit table or vote_id does not match any row
            in the Vote table.
        InputError: if all arguments are None.
    """
    if session is None:
        session = orm.start_session()
    if content_id is not None:
        votes = session.query(orm.Vote).join(orm.RejectedEdit).join(
            orm.ContentPiece).filter(orm.ContentPiece.content_id
                                     == content_id)
    elif user_id is not None:
        votes = session.query(orm.Vote).join(orm.RejectedEdit).join(
            orm.User).filter(orm.User.user_id == user_id)
    elif ip_address is not None:
        votes = session.query(orm.Vote).join(orm.RejectedEdit).filter(
            orm.RejectedEdit.author_type == ip_address)
    elif edit_id is not None:
        try:
            vote = session.query(orm.Vote).join(orm.RejectedEdit).filter(
                orm.RejectedEdit.edit_id == edit_id).one()
        except (NoResultFound, MultipleResultsFound) as e:
            raise SelectError(str(e))
        else:
            return vote
    elif vote_id is not None:
        try:
            vote = session.query(orm.Vote).filter(
                orm.Vote.vote_id == vote_id).one()
        except (NoResultFound, MultipleResultsFound) as e:
            raise SelectError(str(e))
        else:
            return vote
    else:
        raise InputError("No arguments!")

    return votes.all()


def get_user_encrypt_info(email=None, remember_id=None, session=None):
    """
    Args:
        email: String. Defaults to None.
        remember_id: Integer. Defaults to None.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        tuple (pass_hash_type, pass_salt, remember_hash_type).
    Raises:
        InputError: if all arguments are None.
        SelectError: if email or remember_id does not match any row in
            the User table.
    """
    if session is None:
        session = orm.start_session()
    try:
        if email is not None:
            encrypt_info = session.query(orm.User.pass_hash_type,
                orm.User.pass_salt, orm.User.remember_hash_type).filter(
                orm.User.email == email).one()
        elif remember_id is not None:
            encrypt_info = session.query(orm.User.pass_hash_type,
                orm.User.pass_salt, orm.User.remember_hash_type).filter(
                orm.User.remember_id == remember_id).one()
        else:
            raise InputError("No arguments!")
    except (NoResultFound, MultipleResultsFound) as e:
        raise SelectError(str(e))
    else:
        return encrypt_info


def get_author_count(content_id, session=None):
    """
    Args:
        content_id: Integer.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        The number of authors of the content piece matching content_id.
    """
    if session is None:
        session = orm.start_session()
    try:
        author_count = session.query(orm.ContentPiece.authors).filter(
            orm.ContentPiece.content_id == content_id).count()
    except Exception as e:
        raise SelectError(str(e))
    else:
        return author_count


def get_user(user_id=None, email=None, remember_id=None, session=None):
    """
    Args:
        user_id: Integer. Defaults to None.
        email: String. Defaults to None.
        pass_hash: String. Defaults to None.
        remember_id: Integer. Defaults to None.
        remember_token_hash: String. Defaults to None.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        User.
    Raises:
        SelectError: if email and pass_hash do not match any row in the
            User table, or remember_id and remember_token_hash do not
            match any row in the User table, or user_id does not match any
            row in the User table.
        InputError: if email or pass_hash is None, and remember_id or
            remember_token_hash is None, and user_id is None. Indicates
            insufficient information was provided to identify a user.
    """
    if session is None:
        session = orm.start_session()
    if email is not None:
        try:
            user = session.query(orm.User).filter(
                orm.User.email == email).one()
        except MultipleResultsFound as e:
            raise SelectError(str(e))
        except NoResultFound:
            return None
    elif remember_id is not None:
        try:
            user = session.query(orm.User).filter(
                orm.User.remember_id == remember_id).one()
        except MultipleResultsFound as e:
            raise SelectError(str(e))
        except NoResultFound:
            return None
    elif user_id is not None:
        try:
            user = session.query(orm.User).filter(
                orm.User.user_id == user_id).one()
        except (NoResultFound, MultipleResultsFound) as e:
            raise SelectError(str(e))
    else:
        raise InputError("Invalid arguments!")

    return user


def get_user_info(content_id=None, user_id=None, accepted_edit_id=None,
                  rejected_edit_id=None, user_ids=None, session=None):
    """
    Args:
        contend_id: Integer. Defaults to None.
        user_id: Integer. Defaults to None.
        accepted_edit_id: Integer. Defaults to None.
        rejected_edit_id: Integer. Defaults to None.
        user_ids: List of Integers. Defaults to None.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        Tuple or List of Tuples of the form (user_id, user_name, email).
    Raises:
        SelectError: if content_id matches multiple values in one row,
            or accepted_edit_id does not match any row in the
            Accepted_Edit table, or rejected_edit_id does not match
            any row in the Rejected_Edit table.
        InputError: if all arguments are None.
    """
    if session is None:
        session = orm.start_session()
    if content_id is not None:
        try:
            info_tuples = session.query(orm.User.user_id,
                orm.User.user_name, orm.User.email).join(
                orm.ContentPiece, orm.User.pieces).filter(
                orm.ContentPiece.content_id == content_id).all()
        except MultipleValuesFound as e:
            raise SelectError(str(e))
        else:
            return info_tuples
    elif user_ids is not None:
        try:
            if user_ids:
                info_tuples = session.query(orm.User.user_id,
                    orm.User.user_name, orm.User.email).filter(
                    orm.User.user_id.in_(user_ids)).all()
            else:
                info_tuples = []
        except MultipleValuesFound as e:
            raise SelectError(str(e))
        else:
            return info_tuples
    elif user_id is not None:
        try:
            info = session.query(orm.User.user_id,
                orm.User.user_name, orm.User.email).filter(
                orm.User.user_id == user_id).one()
        except (NoResultFound, MultipleResultsFound) as e:
            raise SelectError(str(e))
        else:
            return info
    elif accepted_edit_id is not None:
        try:
            info = session.query(orm.User.user_id,
                orm.User.user_name, orm.User.email).join(
                orm.AcceptedEdit).filter(orm.AcceptedEdit.edit_id
                                         == accepted_edit_id).one()
        except (NoResultFound, MultipleResultsFound) as e:
            raise SelectError(str(e))
        else:
            return info
    elif rejected_edit_id is not None:
        try:
            info = session.query(orm.User.user_id,
                orm.User.user_name, orm.User.email).join(
                orm.RejectedEdit).filter(orm.RejectedEdit.edit_id
                                         == rejected_edit_id).one()
        except (NoResultFound, MultipleResultsFound) as e:
            raise SelectError(str(e))
        else:
            return info
    else:
        raise InputError("No arguments!")


def get_admin_ids(session=None):
    """
    Args:
        session: SQLAlchemy session. Defaults to None.
    Returns:
        List of integers.
    """
    if session is None:
        session = orm.start_session()
    admin_ids = session.query(orm.User.user_id).filter(
        orm.User.user_type == "admin").values()
    return admin_ids


def get_user_reports(content_id=None, report_id=None, user_id=None,
                     admin_id=None, ip_address=None, session=None):
    """
    Args:
        content_id: Integer. Defaults to None.
        report_id: Integer. Defaults to None.
        user_id: Integer. Defaults to None.
        admin_id: Integer. Defaults to None.
        ip_address: String. Defaults to None.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        UserReport or list of UserReports.
    Raises:
        SelectError: if report_id does not match any row in the
            User_Report table.
        InputError: if all arguments are None.
    """
    if session is None:
        session = orm.start_session()
    if content_id is not None:
        reports = session.query(orm.UserReport).join(orm.ContentPiece).filter(
            orm.ContentPiece.content_id == content_id)
    elif user_id is not None:
        reports = session.query(orm.UserReport).join(orm.User,
            orm.UserReport.author).filter(orm.User.user_id == user_id)
    elif admin_id is not None:
        reports = session.query(orm.UserReport).join(orm.User,
            orm.UserReport.admin).filter(orm.User.user_id == admin_id)
    elif ip_address is not None:
        reports = session.query(orm.UserReport).filter(
            orm.UserReport.author_type == ip_address)
    elif report_id is not None:
        try:
            report = session.query(orm.UserReport).filter(
                orm.UserReport.report_id == report_id).one()
        except (NoResultFound, MultipleResultsFound) as e:
            raise SelectError(str(e))
        else:
            return report
    else:
        raise InputError("No arguments!")

    return reports.order_by(orm.UserReport.timestamp).all()
