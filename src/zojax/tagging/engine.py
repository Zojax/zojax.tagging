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
""" Tagging Engine implementation

$Id$
"""
import struct

from BTrees.OOBTree import OOSet
from BTrees.IFBTree import IFBucket
from BTrees.LOBTree import LOBTree
from BTrees.LLBTree import LLSet, multiunion
from BTrees.LFBTree import LFBTree, LFSet, weightedUnion, weightedIntersection

from zope import interface
from persistent import Persistent
from interfaces import ITaggingEngine



def c_mul(a, b):
    return eval(hex((long(a) * b) & 0xFFFFFFFFL)[:-1])


class TaggingEngine(Persistent):
    interface.implements(ITaggingEngine)

    def __init__(self):
        self.clear()

    @property
    def tagsCount(self):
        return len(self.tag_oids)

    @property
    def itemsCount(self):
        return len(self.oid_tags)

    def clear(self):
        self.tagsmap = LOBTree()

        # index
        self.tag_oids = LOBTree()
        self.oid_tags = LOBTree()

        # tag weight
        self.weights = OOSet()
        self.tag_weight = LFBTree()

    def getHash(self, str):
        if not str:
            return 0 # empty

        res = hash(str)

        # NOTE: workaround for 64bit
        if struct.calcsize("P") * 8 == 64:
            res = ord(str[0]) << 7
            for char in str:
                res = c_mul(1000003, res) ^ ord(char)
            res = res ^ len(str)
            if res == -1:
                res = -2
            if res >= 2**31:
                res -= 2**32

        return res

    def update(self, oid, tags):
        self.remove(oid)

        for tag in tags:
            htag = self.getHash(tag)
            self.tagsmap[htag] = tag

            # add oid -> tag
            oids = self.tag_oids.get(htag)
            if oids is None:
                oids = LFSet()
                self.tag_oids[htag] = oids

            if oid not in oids:
                oids.insert(oid)

            # add tag -> oid
            oid_tags = self.oid_tags.get(oid)
            if oid_tags is None:
                oid_tags = LLSet()
                self.oid_tags[oid] = oid_tags

            if htag not in oid_tags:
                oid_tags.insert(htag)

            # culculate weight
            weight = self.tag_weight.get(htag)
            if weight is not None:
                key = (weight, htag)
                if key in self.weights:
                    self.weights.remove(key)

            weight = float(len(oids))
            self.tag_weight[htag] = weight
            self.weights.insert((weight, htag))

    def remove(self, oid):
        for tag in self.oid_tags.get(oid, ()):
            # remove oid from tag -> oids reference
            oids = self.tag_oids.get(tag)

            if oid in oids:
                oids.remove(oid)

            oids_len = float(len(oids))

            # reculculate weight
            weight = self.tag_weight.get(tag)
            if weight is not None:
                key = (weight, tag)
                if key in self.weights:
                    self.weights.remove(key)

            if oids_len:
                self.tag_weight[tag] = oids_len
                self.weights.insert((oids_len, tag))

            # remove tag
            if not oids_len:
                del self.tag_oids[tag]
                del self.tagsmap[tag]

        if oid in self.oid_tags:
            del self.oid_tags[oid]

    def getItems(self, tags):
        oids = self.tag_oids
        weights = self.tag_weight

        weight, result = 0, LFBTree()
        for tag in tags:
            htag = self.getHash(tag)
            if htag in oids:
                weight, result = weightedUnion(
                    oids.get(htag), result, weights.get(htag), weight)

        return IFBucket(result)

    def getUniqueItems(self, tags):
        oids = self.tag_oids
        weights = self.tag_weight

        weight, result = 1.0, None
        for tag in tags:
            htag = self.getHash(tag)
            if htag in oids:
                if result is None:
                    weight, result = weightedUnion(
                        oids.get(htag), LFBTree(), weights.get(htag), weight)
                else:
                    weight, result = weightedIntersection(
                        result, oids.get(htag), weight, weights.get(htag))

        return IFBucket(result)

    def getTagCloud(self, reverse=False):
        total = len(self.oid_tags)
        if not total:
            return

        tags = self.tagsmap
        data = self.weights.keys()

        percent = total / 100.0

        if reverse:
            first = len(data)-1

            for idx in xrange(first, -1, -1):
                weight, htag = data[idx]
                yield weight / percent, tags.get(htag)
        else:
            for weight, htag in data:
                yield weight / percent, tags.get(htag)

    def getItemsTagCloud(self, items):
        oid_tags = self.oid_tags

        tags = [oid_tags[oid] for oid in items if oid in oid_tags]
        if tags:
            tags = multiunion(tags)
        else:
            return

        total = len(oid_tags)
        data = self.weights.keys()
        weights = self.tag_weight

        percent = total / 100.0

        for tag in tags:
            yield weights[tag] / percent, self.tagsmap.get(tag)

    def getFrequency(self, tags):
        tagsmap = self.tagsmap
        tag_weight = self.tag_weight

        for tag in tags:
            yield (tag, tag_weight.get(self.getHash(tag), 0))

    def __nonzero__(self):
        return bool(self.tag_oids)

    def __contains__(self, tag):
        return self.getHash(tag) in self.tagsmap
