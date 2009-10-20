# utils.py
# Copyright (C) 2008, 2009 Michael Trier (mtrier@gmail.com) and contributors
#
# This module is part of GitPython and is released under
# the BSD License: http://www.opensource.org/licenses/bsd-license.php

import os

class LazyMixin(object):
	"""
	Base class providing an interface to lazily retrieve attribute values upon 
	first access. If slots are used, memory will only be reserved once the attribute
	is actually accessed and retrieved the first time. All future accesses will 
	return the cached value as stored in the Instance's dict or slot.
	"""
	__slots__ = tuple()
	
	def __getattr__(self, attr):
		"""
		Whenever an attribute is requested that we do not know, we allow it 
		to be created and set. Next time the same attribute is reqeusted, it is simply
		returned from our dict/slots.
		"""
		self._set_cache_(attr)
		# will raise in case the cache was not created
		return object.__getattribute__(self, attr)

	def _set_cache_(self, attr):
		""" This method should be overridden in the derived class. 
		It should check whether the attribute named by attr can be created
		and cached. Do nothing if you do not know the attribute or call your subclass
		
		The derived class may create as many additional attributes as it deems 
		necessary in case a git command returns more information than represented 
		in the single attribute."""
		pass


class IterableList(list):
	"""
	List of iterable objects allowing to query an object by id or by named index::
	 
	 heads = repo.heads
	 heads.master
	 heads['master']
	 heads[0]
	"""
	__slots__ = '_id_attr'
	
	def __new__(cls, id_attr):
		return super(IterableList,cls).__new__(cls)
		
	def __init__(self, id_attr):
		self._id_attr = id_attr
		
	def __getattr__(self, attr):
		for item in self:
			if getattr(item, self._id_attr) == attr:
				return item
		# END for each item
		return list.__getattribute__(self, attr)
		
	def __getitem__(self, index):
		if isinstance(index, int):
			return list.__getitem__(self,index)
		
		try:
			return getattr(self, index)
		except AttributeError:
			raise IndexError( "No item found with id %r" % index )

class Iterable(object):
	"""
	Defines an interface for iterable items which is to assure a uniform 
	way to retrieve and iterate items within the git repository
	"""
	__slots__ = tuple()
	_id_attribute_ = "attribute that most suitably identifies your instance"
	
	@classmethod
	def list_items(cls, repo, *args, **kwargs):
		"""
		Find all items of this type - subclasses can specify args and kwargs differently.
		If no args are given, subclasses are obliged to return all items if no additional 
		arguments arg given.
		
		Note: Favor the iter_items method as it will 
		
		Returns:
			list(Item,...) list of item instances 
		"""
		#return list(cls.iter_items(repo, *args, **kwargs))
		out_list = IterableList( cls._id_attribute_ )
		out_list.extend(cls.iter_items(repo, *args, **kwargs))
		return out_list
		
		
	@classmethod
	def iter_items(cls, repo, *args, **kwargs):
		"""
		For more information about the arguments, see list_items
		Return: 
			iterator yielding Items
		"""
		raise NotImplementedError("To be implemented by Subclass")
		
