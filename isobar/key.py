from scale import *
from note import *
from util import *

import random

class Key:
	""" Represents a harmonic structure, containing a tonic and scale.
	"""

	def __init__(self, tonic = 0, scale = Scale.major):
		if type(tonic) == str:
			tonic = nametomidi(tonic)
		if type(scale) == str:
			scale = Scale.byname(scale)
			
		self.tonic = tonic
		self.scale = scale

	def __eq__(self, other):
		return self.tonic == other.tonic and self.scale == other.scale

	def __str__(self):
		return "key: %s %s" % (miditopitch(self.tonic), self.scale.name)

	def __repr__(self):
		return 'Key(%s, "%s")' % (self.tonic, self.scale.name)

	def get(self, degree):
		""" Returns the <degree>th semitone within this key. """
		if degree is None:
			return None

		semitone = self.scale[degree]
		return semitone + self.tonic

	def __getitem__(self, degree):
		return self.get(degree)

	@property
	def semitones(self):
		semitones = map(lambda n: (n + self.tonic) % 12, self.scale.semitones)
		semitones.sort()
		return semitones

	def voiceleading(self, other):
		""" Returns the most parsimonious voice leading between this key
			and <other>, as a list of N tuples (semiA, semiB) where N is the
			maximal length of (this, other), and semiA and semiB are members
			of each. May not be bijective. """

		if len(self.semitones()) > len(other.semitones()):
			semisA = self.semitones()
			semisB = other.semitones()
		else:
			semisA = other.semitones()
			semisB = self.semitones()
		semisB = list(reversed(semisB))

		leading = []
		for semiA in semisA:
			distances = []
			for semiB in semisB:
				distance = abs(semiA - semiB)
				if distance > self.scale.octave_size / 2:
					distance = self.scale.octave_size - distance
				distances.append(distance)
			index = distances.index(min(distances))
			leading.append((semiA, semisB[index]))

		return leading

	def distance(self, other):
		leading = self.voiceleading(other)
		distance = sum(map(lambda (a, b): abs(a - b), leading))
		return distance

	def fadeto(self, other, level):
		""" level between 0..1 """
		semitones_a = self.semitones()
		semitones_b = other.semitones()
		semitones_shared = filter(lambda n: n in semitones_a, semitones_b)
		semitones_a_only = filter(lambda n: n not in semitones_b, semitones_a)
		semitones_b_only = filter(lambda n: n not in semitones_a, semitones_b)

		if level < 0.5:
			# scale from 1..0
			level = 1.0 - (level * 2)
			count_from_a = int(round(level * len(semitones_a_only)))
			return semitones_shared + semitones_a_only[0:count_from_a]
		else:
			# scale from 0..1
			level = 2 * (level - 0.5)
			count_from_b = int(round(level * len(semitones_b_only)))
			return semitones_shared + semitones_b_only[0:count_from_b]

	@staticmethod
	def random():
		t = random.randint(0, 11)
		s = Scale.random()
		return key(t, s)

	@staticmethod
	def all():
		return [ Key(note, scale) for note in Note.all() for scale in Scale.all() ]
