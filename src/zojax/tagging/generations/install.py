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
"""

$Id$
"""
from BTrees.LLBTree import LLSet
from BTrees.LOBTree import LOBTree
from BTrees.LFBTree import LFBTree, LFSet
from zope import interface, component
from zope.location.interfaces import ILocation
from zope.app.component.interfaces import ISite
from zope.app.zopeappgenerations import getRootFolder

from zojax.tagging.interfaces import ITaggingEngine


def evolve(context):
    root = getRootFolder(context)

    for engine in findObjectsMatching(root, ITaggingEngine.providedBy):
        fixEngine(engine)

    for site in findObjectsMatching(root, ISite.providedBy):
        for engine in findObjectsMatching(
            site.getSiteManager(), ITaggingEngine.providedBy):
            fixEngine(engine)

    for loc in findObjectsMatching(root, ILocation.providedBy):
        loc._p_activate()
        for attr in loc.__dict__.values():
            if ITaggingEngine.providedBy(attr):
                fixEngine(attr)


def fixEngine(engine):
    if not isinstance(engine.tagsmap, LOBTree):
        engine.tagsmap = LOBTree(engine.tagsmap)
        engine.tag_weight = LFBTree(engine.tag_weight)

        tag_oids = LOBTree()
        for tag, oids in engine.tag_oids.items():
            tag_oids[tag] = LFSet(oids)

        engine.tag_oids = tag_oids

        oid_tags = LOBTree()
        for oid, tags in engine.oid_tags.items():
            oid_tags[oid] = LLSet(tags)

        engine.oid_tags = oid_tags


def findObjectsMatching(root, condition):
    if condition(root):
        yield root

    if hasattr(root, 'values') and callable(root.values):
        for subobj in root.values():
            for match in findObjectsMatching(subobj, condition):
                yield match
