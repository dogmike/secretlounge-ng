from src.util import Enum

# a few utility functions
def escape_html(s):
	ret = ""
	if s is None:
		return ""
	for c in s:
		if c in ("<", ">", "&"):
			c = "&#" + str(ord(c)) + ";"
		ret += c
	return ret

def format_datetime(t):
	tzinfo = __import__("datetime").timezone.utc
	return t.replace(tzinfo=tzinfo).strftime("%Y-%m-%d %H:%M UTC")

def format_timedelta(d):
	timedelta = __import__("datetime").timedelta
	l = [
		(timedelta(weeks=1), "w"), (timedelta(days=1), "d"),
		(timedelta(hours=1), "h"), (timedelta(minutes=1), "m"),
	]
	for cmp, char in l:
		if d >= cmp:
			return "%d%c" % (d // cmp, char)
	return "%ds" % d.total_seconds()

## for debugging ##
def dump(obj, name=None, r=False):
	name = "" if name is None else (name + ".")
	for e, ev in ((e, getattr(obj, e)) for e in dir(obj)):
		if e.startswith("_") or ev is None:
			continue
		if r and ev.__class__.__name__[0].isupper():
			print("%s%s (%s)" % (name, e, ev.__class__.__name__))
			dump(ev, name + e, r)
		else:
			print("%s%s = %r" % (name, e, ev))

# Program version
VERSION = "1.8"

# Ranks
RANKS = Enum({
	"owner": 100,
	"admin": 50,
	"mod": 10,
	"user": 0,
	"banned": -10
})

# Types of media
MEDIA = Enum({
		"videos":2,
		"photos":1,
		"stickers":0
})

# Cooldown related
COOLDOWN_TIME_BEGIN = [1, 5, 25, 60*2, 60*12, 60*24*3] # begins with 1m, 5m, 25m, 2h, 12h, 3d
COOLDOWN_TIME_LINEAR_M = 60*24*3 # continues 7d, 10d, 13d, 16d, ... (linear)
COOLDOWN_TIME_LINEAR_B = 60*24*7
WARN_EXPIRE_HOURS = 24*7

# Karma related
KARMA_PLUS_ONE = 1
KARMA_WARN_PENALTY = 7

# Spam limits
SPAM_LIMIT = 6
SPAM_LIMIT_HIT = 6
SPAM_INTERVAL_SECONDS = 5

# Spam score calculation
SCORE_STICKER = 1.5
SCORE_BASE_MESSAGE = 0.75
SCORE_BASE_FORWARD = 1.25
SCORE_TEXT_CHARACTER = 0.002
SCORE_TEXT_LINEBREAK = 0.1
