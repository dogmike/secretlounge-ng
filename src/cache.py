import logging
import itertools
from datetime import datetime, timedelta
from threading import RLock

from src.globals import *

class CachedMessage():
	__slots__ = ('user_id', 'time', 'warned', 'locked', 'upvoted')
	def __init__(self, user_id=None):
		self.user_id = user_id # who has sent this message
		self.time = datetime.now() # when was this message seen?
		self.warned = False # was the user warned for this message?
		self.locked = False # is this message bad for people to /exposeto?
		self.upvoted = set() # set of users that have given this message karma
	def isExpired(self):
		return datetime.now() >= self.time + timedelta(hours=36)
	def hasUpvoted(self, user):
		return user.id in self.upvoted
	def addUpvote(self, user):
		self.upvoted.add(user.id)

class Cache():
	def __init__(self):
		self.lock = RLock()
		self.counter = itertools.count()
		self.msgs = {} # dict(msid -> CachedMessage)
		self.idmap = {} # dict(uid -> dict(msid -> opaque))
	def _saveMapping(self, x, uid, msid, data):
		if uid not in x.keys():
			x[uid] = {}
		x[uid][msid] = data
	def _lookupMapping(self, x, uid, msid, data):
		if uid not in x.keys():
			return None
		if msid is not None:
			return x[uid].get(msid, None)
		# data is not None
		gen = ( msid for msid, _data in x[uid].items() if _data == data )
		return next(gen, None)
	def _allMappings(self, x, uid):
		gen = ( msid for msid, _cache in x.items() if _cache.user_id == uid)
		return gen

	def assignMessageId(self, cm: CachedMessage) -> int:
		with self.lock:
			ret = next(self.counter)
			self.msgs[ret] = cm
		return ret
	def getMessage(self, msid):
		with self.lock:
			return self.msgs.get(msid, None)
	def saveMapping(self, uid, msid, data):
		with self.lock:
			self._saveMapping(self.idmap, uid, msid, data)
	def lookupMapping(self, uid, msid=None, data=None):
		if msid is None and data is None:
			raise ValueError()
		with self.lock:
			return self._lookupMapping(self.idmap, uid, msid, data)
	def deleteMappings(self, msid):
		with self.lock:
			for d in self.idmap.values():
				d.pop(msid, None)
	def allMappings(self, uid):
		if uid is None:
			raise ValueError()
		with self.lock:
			return self._allMappings(self.msgs, uid)
	def expire(self):
		ids = set()
		with self.lock:
			for msid in list(self.msgs.keys()):
				if not self.msgs[msid].isExpired():
					continue
				ids.add(msid)
				# delete message itself and from mappings
				del self.msgs[msid]
				self.deleteMappings(msid)
		if len(ids) > 0:
			logging.debug("Expired %d entries from cache", len(ids))
		return ids
