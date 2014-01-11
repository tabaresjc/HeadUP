from unittest import defaultTestLoader

from storm.properties import Int
from storm.info import get_obj_info
from storm.cache import Cache, GenerationalCache

from tests.helper import TestHelper


class StubObjectInfo(object):

    def __init__(self, id):
        self.id = id
        self.hashed = False

    def get_obj(self):
        return str(self.id)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.id)

    def __hash__(self):
        self.hashed = True
        return self.id

    def __lt__(self, other):
        return self.id < other.id


class StubClass(object):

    __storm_table__ = "stub_class"

    id = Int(primary=True)


class BaseCacheTest(TestHelper):

    Cache = Cache

    def setUp(self):
        super(BaseCacheTest, self).setUp()
        self.obj_infos = [StubObjectInfo(i) for i in range(10)]
        for i in range(len(self.obj_infos)):
            setattr(self, "obj%d" % (i+1), self.obj_infos[i])

    def clear_hashed(self):
        for obj_info in self.obj_infos:
            obj_info.hashed = False

    def test_initially_empty(self):
        cache = self.Cache()
        self.assertEqual(cache.get_cached(), [])

    def test_add(self):
        cache = self.Cache(5)
        cache.add(self.obj1)
        cache.add(self.obj2)
        cache.add(self.obj3)
        self.assertEquals(sorted(cache.get_cached()),
                          [self.obj1, self.obj2, self.obj3])

    def test_adding_similar_obj_infos(self):
        """If __eq__ is broken, this fails."""
        obj_info1 = get_obj_info(StubClass())
        obj_info2 = get_obj_info(StubClass())
        cache = self.Cache(5)
        cache.add(obj_info1)
        cache.add(obj_info2)
        cache.add(obj_info2)
        cache.add(obj_info1)
        self.assertEquals(sorted([hash(obj_info)
                                  for obj_info in cache.get_cached()]),
                          sorted([hash(obj_info1), hash(obj_info2)]))

    def test_remove(self):
        cache = self.Cache(5)
        cache.add(self.obj1)
        cache.add(self.obj2)
        cache.add(self.obj3)
        cache.remove(self.obj2)
        self.assertEquals(sorted(cache.get_cached()),
                          [self.obj1, self.obj3])

    def test_add_existing(self):
        cache = self.Cache(5)
        cache.add(self.obj1)
        cache.add(self.obj2)
        cache.add(self.obj3)
        cache.add(self.obj2)
        self.assertEquals(sorted(cache.get_cached()),
                          [self.obj1, self.obj2, self.obj3])

    def test_add_with_size_zero(self):
        """Cache is disabled entirely on add() if size is 0."""
        cache = self.Cache(0)
        cache.add(self.obj1)
        # Ensure that we don't even check if obj_info is in the
        # cache, by testing if it was hashed.  Hopefully, that means
        # we got a faster path.
        self.assertEquals(self.obj1.hashed, False)

    def test_remove_with_size_zero(self):
        """Cache is disabled entirely on remove() if size is 0."""
        cache = self.Cache(0)
        cache.remove(self.obj1)

    def test_clear(self):
        """The clear method empties the cache."""
        cache = self.Cache(5)
        for obj_info in self.obj_infos:
            cache.add(obj_info)
        cache.clear()
        self.assertEquals(cache.get_cached(), [])

        # Just an additional check ensuring that any additional structures
        # which may be used were cleaned properly as well.
        for obj_info in self.obj_infos:
            self.assertEquals(cache.remove(obj_info), False)

    def test_set_zero_size(self):
        """
        Setting a cache's size to zero clears the cache.
        """
        cache = self.Cache()
        cache.add(self.obj1)
        cache.add(self.obj2)
        cache.set_size(0)
        self.assertEquals(cache.get_cached(), [])

    def test_fit_size(self):
        """
        A cache of size n can hold at least n objects.
        """
        size = 10
        cache = self.Cache(size)
        for value in xrange(size):
            cache.add(StubObjectInfo(value))
        self.assertEqual(len(cache.get_cached()), size)


class CacheTest(BaseCacheTest):

    def test_size_and_fifo_behaviour(self):
        cache = Cache(5)
        for obj_info in self.obj_infos:
            cache.add(obj_info)
        self.assertEquals([obj_info.id for obj_info in cache.get_cached()],
                          [9, 8, 7, 6, 5])

    def test_reduce_max_size_to_zero(self):
        """When setting the size to zero, there's an optimization."""
        cache = Cache(5)
        obj_info = self.obj_infos[0]
        cache.add(obj_info)
        obj_info.hashed = False
        cache.set_size(0)
        self.assertEquals(cache.get_cached(), [])
        # Ensure that we don't even check if obj_info is in the
        # cache, by testing if it was hashed.  Hopefully, that means
        # we got a faster path.
        self.assertEquals(obj_info.hashed, False)

    def test_reduce_max_size(self):
        cache = Cache(5)
        for obj_info in self.obj_infos:
            cache.add(obj_info)
        cache.set_size(3)
        self.assertEquals([obj_info.id for obj_info in cache.get_cached()],
                          [9, 8, 7])

        # Adding items past the new maximum size should drop older ones.
        for obj_info in self.obj_infos[:2]:
            cache.add(obj_info)
        self.assertEquals([obj_info.id for obj_info in cache.get_cached()],
                          [1, 0, 9])

    def test_increase_max_size(self):
        cache = Cache(5)
        for obj_info in self.obj_infos:
            cache.add(obj_info)
        cache.set_size(10)
        self.assertEquals([obj_info.id for obj_info in cache.get_cached()],
                          [9, 8, 7, 6, 5])

        # Adding items past the new maximum size should drop older ones.
        for obj_info in self.obj_infos[:6]:
            cache.add(obj_info)
        self.assertEquals([obj_info.id for obj_info in cache.get_cached()],
                          [5, 4, 3, 2, 1, 0, 9, 8, 7, 6])


class TestGenerationalCache(BaseCacheTest):

    Cache = GenerationalCache

    def setUp(self):
        super(TestGenerationalCache, self).setUp()
        self.obj1 = StubObjectInfo(1)
        self.obj2 = StubObjectInfo(2)
        self.obj3 = StubObjectInfo(3)
        self.obj4 = StubObjectInfo(4)

    def test_initially_empty(self):
        cache = GenerationalCache()
        self.assertEqual(cache.get_cached(), [])

    def test_cache_one_object(self):
        cache = GenerationalCache()
        cache.add(self.obj1)
        self.assertEqual(cache.get_cached(), [self.obj1])

    def test_cache_multiple_objects(self):
        cache = GenerationalCache()
        cache.add(self.obj1)
        cache.add(self.obj2)
        self.assertEqual(sorted(cache.get_cached()), [self.obj1, self.obj2])

    def test_clear_cache(self):
        cache = GenerationalCache()
        cache.add(self.obj1)
        cache.clear()
        self.assertEqual(cache.get_cached(), [])

    def test_clear_cache_clears_the_second_generation(self):
        cache = GenerationalCache(1)
        cache.add(self.obj1)
        cache.add(self.obj2)
        cache.clear()
        self.assertEqual(cache.get_cached(), [])

    def test_remove_object(self):
        cache = GenerationalCache()
        cache.add(self.obj1)
        cache.add(self.obj2)
        cache.add(self.obj3)

        present = cache.remove(self.obj2)
        self.assertTrue(present)
        self.assertEqual(sorted(cache.get_cached()), [self.obj1, self.obj3])

    def test_remove_nothing(self):
        cache = GenerationalCache()
        cache.add(self.obj1)

        present = cache.remove(self.obj2)
        self.assertFalse(present)
        self.assertEqual(cache.get_cached(), [self.obj1])

    def test_size_limit(self):
        """
        A cache will never hold more than twice its size in objects.  The
        generational system is what prevents it from holding exactly the
        requested number of objects.
        """
        size = 10
        cache = GenerationalCache(size)
        for value in xrange(5 * size):
            cache.add(StubObjectInfo(value))
        self.assertEquals(len(cache.get_cached()), size * 2)

    def test_set_size_smaller_than_current_size(self):
        """
        Setting the size to a smaller size than the number of objects
        currently cached will drop some of the extra content.  Note that
        because of the generation system, it can actually hold two times
        the size requested in edge cases.
        """
        cache = GenerationalCache(150)
        for i in range(250):
            cache.add(StubObjectInfo(i))
        cache.set_size(100)
        cached = cache.get_cached()
        self.assertEquals(len(cached), 100)
        for obj_info in cache.get_cached():
            self.assertTrue(obj_info.id >= 100)

    def test_set_size_larger_than_current_size(self):
        """
        Setting the cache size to something more than the number of
        objects in the cache does not affect its current contents,
        and will merge any elements from the second generation into
        the first one.
        """
        cache = GenerationalCache(1)
        cache.add(self.obj1) # new=[1]    old=[]
        cache.add(self.obj2) # new=[2]    old=[1]
        cache.set_size(2)    # new=[1, 2] old=[]
        cache.add(self.obj3) # new=[3]    old=[1, 2]
        self.assertEqual(sorted(cache.get_cached()),
                         [self.obj1, self.obj2, self.obj3])

    def test_set_size_limit(self):
        """
        Setting the size limits the cache's size just like passing an
        initial size would.
        """
        size = 10
        cache = GenerationalCache(size * 100)
        cache.set_size(size)
        for value in xrange(size * 10):
            cache.add(StubObjectInfo(value))
        self.assertEquals(len(cache.get_cached()), size * 2)

    def test_two_generations(self):
        """
        Inserting more objects than the cache's size causes the cache
        to contain two generations, each holding up to <size> objects.
        """
        cache = GenerationalCache(1)
        cache.add(self.obj1)
        cache.add(self.obj2)

        self.assertEqual(sorted(cache.get_cached()), [self.obj1, self.obj2])

    def test_three_generations(self):
        """
        If more than 2*<size> objects come along, only 2*<size>
        objects are retained.
        """
        cache = GenerationalCache(1)
        cache.add(self.obj1)
        cache.add(self.obj2)
        cache.add(self.obj3)

        self.assertEqual(sorted(cache.get_cached()), [self.obj2, self.obj3])

    def test_generational_overlap(self):
        """
        An object that is both in the primary and the secondary
        generation is listed only once in the cache's contents.
        """
        cache = GenerationalCache(2)
        cache.add(self.obj1) # new=[1]    old=[]
        cache.add(self.obj2) # new=[1, 2] old=[]
        cache.add(self.obj3) # new=[3]    old=[1, 2]
        cache.add(self.obj1) # new=[3, 1] old=[1, 2]

        self.assertEqual(sorted(cache.get_cached()),
                         [self.obj1, self.obj2, self.obj3])

    def test_remove_from_overlap(self):
        """
        Removing an object from the cache removes it from both its
        primary and secondary generations.
        """
        cache = GenerationalCache(2)
        cache.add(self.obj1) # new=[1]    old=[]
        cache.add(self.obj2) # new=[1, 2] old=[]
        cache.add(self.obj3) # new=[3]    old=[1, 2]
        cache.add(self.obj1) # new=[3, 1] old=[1, 2]

        present = cache.remove(self.obj1)
        self.assertTrue(present)
        self.assertEqual(sorted(cache.get_cached()), [self.obj2, self.obj3])

    def test_evict_oldest(self):
        """The "oldest" object is the first to be evicted."""
        cache = GenerationalCache(1)
        cache.add(self.obj1)
        cache.add(self.obj2)
        cache.add(self.obj3)

        self.assertEqual(sorted(cache.get_cached()), [self.obj2, self.obj3])

    def test_evict_LRU(self):
        """
        Actually, it's not the oldest but the LRU object that is first
        to be evicted.  Re-adding the oldest object makes it not be
        the LRU.
        """
        cache = GenerationalCache(1)
        cache.add(self.obj1)
        cache.add(self.obj2)

        # This "refreshes" the oldest object in the cache.
        cache.add(self.obj1)

        cache.add(self.obj3)

        self.assertEqual(sorted(cache.get_cached()), [self.obj1, self.obj3])


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)
