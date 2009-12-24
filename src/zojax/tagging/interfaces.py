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
""" zojax.tagging.engine interfaces

$Id$
"""
from zope import schema, interface


class ITaggingEngine(interface.Interface):
    """Manangement and Querying of Tags.

    Tags are small stickers that are specific to an object to be tageed.
    """

    tagsCount = schema.Int(
        title = u'Tags count',
        description = u'The number of tags in the tagging engine',
        required = True)

    itemsCount = schema.Int(
        title = u'Items count',
        description = u'The number of items in the tagging engine',
        required = True)

    def update(oid, tags):
        """Update the tagging engine for an object id."""

    def remove(oid):
        """Remove all tag entries for object id."""

    def clear():
        """Remove all data."""

    def getItems(tags):
        """Get all items matching the specified items and users.

        The method returns a set of item ids.
        """

    def getUniqueItems(tags):
        """Get unique items for all tags."""

    def getTagCloud(reverse=False):
        """Get a set of tuples in the form of ('tag', weight).

        Limit is number of return tags, if no limit secified, return all.

        return values are sorted.
        """

    def getItemsTagCloud(items):
        """Get a set of tuples in the form of ('tag', weight) for all items."""

    def getFrequency(tags):
        """Get the frequency of all tags

        Returns iterator to ('tag', frequency)"""

    def __nonzero__():
        """ """

    def __contains__(tag):
        """Engine containes tag"""


class ITagIndex(interface.Interface):

    def apply(query):
        """Return None or an IFTreeSet of the doc ids that match the query.

        query is a dict with one of the following keys: and, or

        Any one of the keys may be used; using more than one is not allowed.

        'any_of' : docs containing at least one of the keys are returned. The
                   value is a list containing the tags.
        'all_of' : docs containing at all of the tags are returned. The value
                   is a list containing the tags.
        """
