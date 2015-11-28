"""

"""

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm.query import Query as _Query

from . import orm_core as orm


class Query(_Query):
	"""Custom SQLAlchemy query class."""

	def values(self):
		"""
		Return an iterable of all scalar element values from rows 
		matched by this query.

		:raise MultipleValuesFound: If result rows have more than 
									one element.
		"""
		try:
			return [x for (x,) in self.all()]
		except ValueError as e:
			raise MultipleValuesFound(str(e))


class MultipleValuesFound(ValueError, MultipleResultsFound):
	"""
	Exception raised by :meth:'Query.values' when multiple value were
	found in a single result row.
	"""


class SelectError(Exception):
	"""
	General exception raised when a database query returns an invalid 
	result.
	"""


class InputError(Exception):
	"""
	General exception raised when function is called with invalid argument 
	values.
	"""


def get_content_piece(content_id):
	"""
	Input: content_id.
	Returns: 'ContentPiece' instance.
	"""
	session = orm.start_session()
	try:
		content_piece = session.query(orm.ContentPiece).filter(
			orm.ContentPiece.content_id == content_id).one()
	except NoResultFound, MultipleResultsFound:
		raise SelectError()
	else:
		return content_piece


def get_alternate_names(content_id):
	"""
	Input: content_id.
	Returns: list of 'Name' instances.
	"""
	session = orm.start_session()
	alternate_names = session.query(orm.ContentPiece.alternate_names).filter(
		orm.ContentPiece.content_id == content_id).all()
	return alternate_names


def get_accepted_edits(content_id=None, edit_id=None, user_id=None, 
					   text_id=None, name_id=None, citation_id=None, 
					   keyword_id=None, ip_address=None):
	"""
	Input: content_id, edit_id, user_id, text_id, name_id, citation_id,
		   keyword_id, or ip_address.
	Returns: 'AcceptedEdit' instance or list of 'AcceptedEdit' instances.
	"""
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
			accepted_edit = session.query(orm.AcceptedEdit).filter(
				orm.AcceptedEdit.edit_id == edit_id).one()
		except (NoResultFound, MultipleResultsFound) as e:
			raise SelectError(str(e))
		else:
			return accepted_edit

	return accepted_edits


def get_rejected_edits(content_id=None, edit_id=None, user_id=None, 
					   text_id=None, name_id=None, citation_id=None, 
					   keyword_id=None, ip_address=None):
	"""
	Input: content_id, edit_id, user_id, text_id, name_id, citation_id,
		   keyword_id, or ip_address.
	Returns: 'RejectedEdit' instance or list of 'RejectedEdit' instances.
	"""
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
			rejected_edit = session.query(orm.RejectedEdit).filter(
				orm.RejectedEdit.edit_id == edit_id).one()
		except (NoResultFound, MultipleResultsFound) as e:
			raise SelectError(str(e))
		else:
			return rejected_edit
	else:
		raise InputError("No arguments!")

	return rejected_edits


def get_user_votes(user_id):
	"""
	Input: user_id.
	Returns: list of 'Vote' instances.
	"""
	session = orm.start_session()
	votes = session.query(orm.Vote).join(orm.User).filter(
			orm.User.user_id == user_id).all()
	return votes


def get_accepted_votes(content_id=None, edit_id=None, 
					   vote_id=None, user_id=None, ip_address=None):
	"""
	Input: content_id, edit_id, vote_id, user_id, or ip_address.
	Returns: 'Vote' instance or list of 'Vote' instances.
	"""
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
		raise InputError("Invalid arguments!")

	return votes


def get_rejected_votes(content_id=None, edit_id=None, 
					   vote_id=None, user_id=None, ip_address=None):
	"""
	Input: content_id, edit_id, vote_id, user_id, or ip_address.
	Returns: 'Vote' instance or list of 'Vote' instances.
	"""
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
		raise InputError("Invalid arguments!")

	return votes


def get_user_encrypt_info(email):
	"""
	Input: email.
	Returns: tuple (pass_hash_type, pass_salt, remember_token_hash).
	"""
	session = orm.start_session()
	try:
		encrypt_info = session.query(orm.User.pass_hash_type, 
			orm.User.pass_salt, orm.User.remember_token_hash).filter(
			orm.User.email == email).one()
	except (NoResultFound, MultipleResultsFound) as e:
		raise SelectError(str(e))
	else:
		return encrypt_info


def get_user(email=None, pass_hash=None, remember_id=None, 
			 remember_token_hash=None):
	"""
	Input: email and pass_hash or remember_id and remember_token_hash.
	Returns: 'User' instance.
	"""
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
	else:
		raise InputError("Invalid arguments!")

	return user


def get_user_emails(content_id=None, accepted_edit_id=None, 
					rejected_edit_id=None):
	"""
	Input: content_id or edit_id.
	Returns: email or list of emails.
	"""
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
	else:
		raise InputError("Invalid arguments!")


def get_user_reports(content_id=None, report_id=None, 
					 user_id=None, admin_id=None, ip_address=None):
	"""
	Input: content_id, report_id, user_id, admin_id, or ip_address.
	Returns: 'UserReport' instance or list of 'UserReport' instances.
	"""
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
		raise InputError("Invalid arguments!")

	return reports
