##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""A catalog index wich uses the tagging engine.

$Id$
"""
from BTrees.IFBTree import IFTreeSet

from zope import interface
from zope.index.interfaces import IIndexSearch
from zojax.tagging.interfaces import ITagIndex


class TagIndex(object):
    interface.implements(IIndexSearch, ITagIndex)

    def __init__(self, engine):
        self.engine = engine

    def apply(self, query):
        if 'any_of' in query:
            tags = query['any_of']
            return self.engine.getItems(tags)
        elif 'all_of' in query:
            tags = query['all_of']
            return self.engine.getUniqueItems(tags)
