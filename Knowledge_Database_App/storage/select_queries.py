"""
Storage Selection Query API

Contains functions and classes for making selections from the Postgres 
database. Uses SQLAlchemy.

Exceptions:

    SelectError, InputError, MultipleValuesFound

Functions:

    get_content_piece, get_content_pieces, get_name, get_alternate_names,
    get_keywords, get_citations, get_keyword, get_citation,
    get_content_type, get_content_types, get_accepted_edits,
    get_rejected_edits, get_user_votes, get_accepted_votes,
    get_rejected_votes, get_user_encrypt_info, get_user, get_user_emails,
    get_user_reports

    Note that all functions take a common 'session' keyword argument,
    which defaults to None.
"""

from sqlalchemy.orm import subqueryload
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

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


def get_content_piece(content_id, session=None):
    """
    Args:
        content_id: Integer.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        ContentPiece: if content piece matching content_id is found.
    Raises:
        SelectError: if content_id does not match any row in the
            Content_Piece table.
    """
    if session is None:
        session = orm.start_session()
    try:
        content_piece = session.query(orm.ContentPiece).options(
            subqueryload(orm.ContentPiece.first_author),
            subqueryload(orm.ContentPiece.authors),
            subqueryload(orm.ContentPiece.content_type),
            subqueryload(orm.ContentPiece.name),
            subqueryload(orm.ContentPiece.alternate_names),
            subqueryload(orm.ContentPiece.text),
            subqueryload(orm.ContentPiece.keywords),
            subqueryload(orm.ContentPiece.citations)).filter(
            orm.ContentPiece.content_id == content_id).one()
    except (NoResultFound, MultipleResultsFound) as e:
        raise SelectError(str(e))
    else:
        return content_piece


def get_content_pieces(user_id, session=None):
    """
    Args:
        user_id: Integer.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        list of ContentPieces that user_id has authored.
    """
    if session is None:
        session = orm.start_session()
    content_pieces = session.query(orm.ContentPiece).options(
        subqueryload(orm.ContentPiece.first_author),
        subqueryload(orm.ContentPiece.authors),
        subqueryload(orm.ContentPiece.content_type),
        subqueryload(orm.ContentPiece.name),
        subqueryload(orm.ContentPiece.alternate_names),
        subqueryload(orm.ContentPiece.text),
        subqueryload(orm.ContentPiece.keywords),
        subqueryload(orm.ContentPiece.citations)).join(
        orm.User, orm.ContentPiece.authors).filter(
        orm.User.user_id == user_id).all()
    return content_pieces


def get_name(content_id, session=None):
    """
    Args:
        content_id: Integer.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        Name.
    """
    if session is None:
        session = orm.start_session()
    try:
        name = session.query(orm.ContentPiece.name).filter(
            orm.ContentPiece.content_id == content_id).one()
    except (NoResultFound, MultipleResultsFound) as e:
        raise SelectError(str(e))
    return name


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
    alternate_names = session.query(orm.ContentPiece.alternate_names).filter(
        orm.ContentPiece.content_id == content_id).all()
    return alternate_names


def get_keywords(content_id, session=None):
    """
    Args:
        content_id: Integer.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        list of Keywords.
    """
    if session is None:
        session = orm.start_session()
    keywords = session.query(orm.ContentPiece.keywords).filter(
        orm.ContentPiece.content_id == content_id).all()
    return keywords


def get_citations(content_id, session=None):
    """
    Args:
        content_id: Integer.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        list of Citations.
    """
    if session is None:
        session = orm.start_session()
    citations = session.query(orm.ContentPiece.citations).filter(
        orm.ContentPiece.content_id == content_id).all()
    return citations


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


def get_accepted_edits(content_id=None, edit_id=None, user_id=None,
                       text_id=None, name_id=None, citation_id=None,
                       keyword_id=None, ip_address=None, session=None):
    """
    Args:
        content_id: Integer. Defaults to None.
        edit_id: Integer. Defaults to None.
        user_id: Integer. Defaults to None.
        text_id: Integer. Defaults to None.
        name_id: Integer. Defaults to None.
        citation_id: Integer. Defaults to None.
        keyword_id: Integer. Defaults to None.
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
    if content_id is not None:
        accepted_edits = session.query(orm.AcceptedEdit).join(
            orm.ContentPiece).filter(orm.ContentPiece.content_id
            == content_id).order_by(orm.AcceptedEdit.acc_timestamp).all()
    elif user_id is not None:
        accepted_edits = session.query(orm.AcceptedEdit).join(
            orm.User).filter(orm.User.user_id == user_id).order_by(
            orm.AcceptedEdit.acc_timestamp).all()
    elif ip_address is not None:
        accepted_edits = session.query(orm.AcceptedEdit).filter(
            orm.AcceptedEdit.author_type == ip_address).all()
    elif text_id is not None:
        accepted_edits = session.query(orm.AcceptedEdit).join(
            orm.Text).filter(orm.Text.text_id == text_id).order_by(
            orm.AcceptedEdit.acc_timestamp).all()
    elif name_id is not None:
        accepted_edits = session.query(orm.AcceptedEdit).join(
            orm.Name).filter(orm.Name.name_id == name_id).order_by(
            orm.AcceptedEdit.acc_timestamp).all()
    elif citation_id is not None:
        accepted_edits = session.query(orm.AcceptedEdit).join(
            orm.Citation).filter(orm.Citation.citation_id
            == citation_id).order_by(orm.AcceptedEdit.acc_timestamp).all()
    elif keyword_id is not None:
        accepted_edits = session.query(orm.AcceptedEdit).join(
            orm.Keyword).filter(orm.Keyword.keyword_id == keyword_id).order_by(
            orm.AcceptedEdit.acc_timestamp).all()
    elif edit_id is not None:
        try:
            accepted_edit = session.query(orm.AcceptedEdit).options(
                subqueryload(orm.AcceptedEdit.author)).filter(
                orm.AcceptedEdit.edit_id == edit_id).one()
        except (NoResultFound, MultipleResultsFound) as e:
            raise SelectError(str(e))
        else:
            return accepted_edit
    else:
        InputError("No arguments!")

    return accepted_edits


def get_rejected_edits(content_id=None, edit_id=None, user_id=None,
                       text_id=None, name_id=None, citation_id=None,
                       keyword_id=None, ip_address=None, session=None):
    """
    Args:
        content_id: Integer. Defaults to None.
        edit_id: Integer. Defaults to None.
        user_id: Integer. Defaults to None.
        text_id: Integer. Defaults to None.
        name_id: Integer. Defaults to None.
        citation_id: Integer. Defaults to None.
        keyword_id: Integer. Defaults to None.
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
    if content_id is not None:
        rejected_edits = session.query(orm.RejectedEdit).join(
            orm.ContentPiece).filter(orm.ContentPiece.content_id
            == content_id).order_by(orm.RejectedEdit.rej_timestamp).all()
    elif user_id is not None:
        rejected_edits = session.query(orm.RejectedEdit).join(
            orm.User).filter(orm.User.user_id == user_id).order_by(
            orm.RejectedEdit.rej_timestamp).all()
    elif ip_address is not None:
        rejected_edits = session.query(orm.RejectedEdit).filter(
            orm.RejectedEdit.author_type == ip_address).all()
    elif text_id is not None:
        rejected_edits = session.query(orm.RejectedEdit).join(
            orm.Text).filter(orm.Text.text_id == text_id).order_by(
            orm.RejectedEdit.rej_timestamp).all()
    elif name_id is not None:
        rejected_edits = session.query(orm.RejectedEdit).join(
            orm.Name).filter(orm.Name.name_id == name_id).order_by(
            orm.RejectedEdit.rej_timestamp).all()
    elif citation_id is not None:
        rejected_edits = session.query(orm.RejectedEdit).join(
            orm.Citation).filter(orm.Citation.citation_id
            == citation_id).order_by(orm.RejectedEdit.rej_timestamp).all()
    elif keyword_id is not None:
        rejected_edits = session.query(orm.RejectedEdit).join(
            orm.Keyword).filter(orm.Keyword.keyword_id == keyword_id).order_by(
            orm.RejectedEdit.rej_timestamp).all()
    elif edit_id is not None:
        try:
            rejected_edit = session.query(orm.RejectedEdit).options(
                subqueryload(orm.RejectedEdit.author)).filter(
                orm.RejectedEdit.edit_id == edit_id).one()
        except (NoResultFound, MultipleResultsFound) as e:
            raise SelectError(str(e))
        else:
            return rejected_edit
    else:
        raise InputError("No arguments!")

    return rejected_edits


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
    votes = session.query(orm.Vote).join(orm.User).filter(
        orm.User.user_id == user_id).all()
    return votes


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
                                     == content_id).all()
    elif user_id is not None:
        votes = session.query(orm.Vote).join(orm.AcceptedEdit).join(
            orm.User).filter(orm.User.user_id == user_id).all()
    elif ip_address is not None:
        votes = session.query(orm.Vote).join(orm.AcceptedEdit).filter(
            orm.AcceptedEdit.author_type == ip_address).all()
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

    return votes


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
                                     == content_id).all()
    elif user_id is not None:
        votes = session.query(orm.Vote).join(orm.RejectedEdit).join(
            orm.User).filter(orm.User.user_id == user_id).all()
    elif ip_address is not None:
        votes = session.query(orm.Vote).join(orm.RejectedEdit).filter(
            orm.RejectedEdit.author_type == ip_address).all()
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

    return votes


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
    if session is None:
        session = orm.start_session()
    try:
        author_count = session.query(orm.ContentPiece.authors).filter(
            orm.ContentPiece.content_id == content_id).count()
    except Exception as e:
        raise SelectError(str(e))
    else:
        return author_count


def get_user(user_id=None, email=None, pass_hash=None, remember_id=None,
             remember_token_hash=None, session=None):
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
    if email is not None and pass_hash is not None:
        try:
            user = session.query(orm.User).filter(orm.User.email == email,
                orm.User.pass_hash == pass_hash).one()
        except MultipleResultsFound as e:
            raise SelectError(str(e))
        except NoResultFound:
            return None
    elif remember_id is not None and remember_token_hash is not None:
        try:
            user = session.query(orm.User).filter(
                orm.User.remember_id == remember_id,
                orm.User.remember_token_hash == remember_token_hash).one()
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


def get_user_emails(content_id=None, accepted_edit_id=None,
                    rejected_edit_id=None, session=None):
    """
    Args:
        contend_id: Integer. Defaults to None.
        accepted_edit_id: Integer. Defaults to None.
        rejected_edit_id: Integer. Defaults to None.
        session: SQLAlchemy session. Defaults to None.
    Returns:
        email or list of emails.
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
            emails = session.query(orm.User.email).join(
                orm.ContentPiece, orm.User.pieces).filter(
                orm.ContentPiece.content_id == content_id).values()
        except MultipleValuesFound as e:
            raise SelectError(str(e))
        else:
            return emails
    elif accepted_edit_id is not None:
        try:
            email = session.query(orm.User.email).join(
                orm.AcceptedEdit).filter(orm.AcceptedEdit.edit_id
                                         == accepted_edit_id).one()
        except (NoResultFound, MultipleResultsFound) as e:
            raise SelectError(str(e))
        else:
            return email
    elif rejected_edit_id is not None:
        try:
            email = session.query(orm.User.email).join(
                orm.RejectedEdit).filter(orm.RejectedEdit.edit_id
                                         == rejected_edit_id).one()
        except (NoResultFound, MultipleResultsFound) as e:
            raise SelectError(str(e))
        else:
            return email
    else:
        raise InputError("No arguments!")


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
            orm.ContentPiece.content_id == content_id).all()
    elif user_id is not None:
        reports = session.query(orm.UserReport).join(orm.User,
            orm.UserReport.author).filter(orm.User.user_id == user_id).all()
    elif admin_id is not None:
        reports = session.query(orm.UserReport).join(orm.User,
            orm.UserReport.admin).filter(orm.User.user_id == admin_id).all()
    elif ip_address is not None:
        reports = session.query(orm.UserReport).filter(
            orm.UserReport.author_type == ip_address).all()
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

    return reports
