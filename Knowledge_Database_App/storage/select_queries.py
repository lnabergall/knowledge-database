"""

"""

from sqlalchemy.orm import joinedload, aliased
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from . import orm_core as orm


class SelectError(Exception):
	pass


class InputError(Exception):
	pass


def get_content_piece(content_id):
	"""
	Input: content_id.
	Returns: ContentPiece instance.
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
	Returns: list of Name instances.
	"""
	session = orm.start_session()
	alternate_names = session.query(orm.ContentPiece.alternate_names).filter(
		orm.ContentPiece.content_id == content_id).all()
	return alternate_names


def get_accepted_edits(content_id=None, edit_id=None, user_id=None, 
					   text_id=None, name_id=None, citation_id=None, 
					   keyword_id=None):
	"""
	Input: content_id, edit_id, user_id, text_id, name_id, citation_id,
		   or keyword_id.
	Returns: AcceptedEdit instance or list of AcceptedEdit instances.
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
		except NoResultFound, MultipleResultsFound:
			raise SelectError()
		else:
			return accepted_edit

	return accepted_edits


def get_rejected_edits(content_id=None, edit_id=None, user_id=None, 
					   text_id=None, name_id=None, citation_id=None, 
					   keyword_id=None):
	"""
	Input: content_id, edit_id, user_id, text_id, name_id, citation_id,
		   or keyword_id.
	Returns: RejectedEdit instance or list of RejectedEdit instances.
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
		except NoResultFound, MultipleResultsFound:
			raise SelectError()
		else:
			return rejected_edit
	else:
		raise InputError("No arguments!")

	return rejected_edits


def get_user_votes(user_id):
	"""
	Input: user_id.
	Returns: list of Vote instances.
	"""
	session = orm.start_session()
	votes = session.query(orm.Vote).join(orm.User).filter(
			orm.User.user_id == user_id).all()
	return votes


def get_accepted_votes(content_id=None, edit_id=None, 
					   vote_id=None, user_id=None):
	"""
	Input: content_id, edit_id, vote_id, or user_id.
	Returns: Vote instance or list of Vote instances.
	"""
	session = orm.start_session()
	if content_id is not None:
		votes = session.query(orm.Vote).join(orm.AcceptedEdit).join(
			orm.ContentPiece).filter(orm.ContentPiece.content_id 
			== content_id).all()
	elif user_id is not None:
		votes = session.query(orm.Vote).join(orm.AcceptedEdit).join(
			orm.User).filter(orm.User.user_id == user_id).all()
	elif edit_id is not None:
		try:
			vote = session.query(orm.Vote).join(orm.AcceptedEdit).filter(
				orm.AcceptedEdit.edit_id == edit_id).one()
		except NoResultFound, MultipleResultsFound:
			raise SelectError()
		else:
			return vote
	elif vote_id is not None:
		try:
			vote = session.query(orm.Vote).filter(
				orm.Vote.vote_id == vote_id).one()
		except NoResultFound, MultipleResultsFound:
			raise SelectError()
		else:
			return vote
	else:
		raise InputError("No arguments!")

	return votes


def get_rejected_votes(content_id=None, edit_id=None, 
					   vote_id=None, user_id=None):
	"""
	Input: content_id, edit_id, vote_id, or user_id.
	Returns: Vote instance or list of Vote instances.
	"""
	session = orm.start_session()
	if content_id is not None:
		votes = session.query(orm.Vote).join(orm.RejectedEdit).join(
			orm.ContentPiece).filter(orm.ContentPiece.content_id 
			== content_id).all()
	elif user_id is not None:
		votes = session.query(orm.Vote).join(orm.RejectedEdit).join(
			orm.User).filter(orm.User.user_id == user_id).all()
	elif edit_id is not None:
		try:
			vote = session.query(orm.Vote).join(orm.RejectedEdit).filter(
				orm.RejectedEdit.edit_id == edit_id).one()
		except NoResultFound, MultipleResultsFound:
			raise SelectError()
		else:
			return vote
	elif vote_id is not None:
		try:
			vote = session.query(orm.Vote).filter(
				orm.Vote.vote_id == vote_id).one()
		except NoResultFound, MultipleResultsFound:
			raise SelectError()
		else:
			return vote
	else:
		raise InputError("No arguments!")

	return votes


def get_user_encrypt_info(email=None):
	

def get_user(user_id=None, email=None, pass_hash=None, remember_id=None, 
			 remember_token_hash=None):
	