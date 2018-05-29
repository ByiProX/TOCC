import unittest

__all__ = ['_get_tag', '_get_tags', '_put_tag', '_put_tags', '_delete_tag', '_delete_tags']


def _get_tag(bitmap, _tag_id):
    """Test whether a tag exists."""
    if bitmap & pow(2, _tag_id):
        return True
    return False


def _get_tags(bitmap):
    """Return a list containing the index of the tags in the bitmap."""
    bitmap_as_bin = bin(bitmap)[::-1]
    _tag_list = []
    for index, value in enumerate(bitmap_as_bin):
        if value == '1':
            _tag_list.append(index)
    return _tag_list


def _put_tag(bitmap, _tag_id):
    """Add a tag to this bitmap."""
    return bitmap | pow(2, _tag_id)


def _put_tags(bitmap, _tag_list):
    """Add a list of tags to this bitmap."""
    _bitmap = 0
    for i in set(_tag_list):
        _bitmap += pow(2, i)
    return bitmap | _bitmap


def _delete_tag(bitmap, _tag_id):
    """Delete a tag in this bitmap."""
    return ~(~bitmap | pow(2, _tag_id))


def _delete_tags(bitmap, _tag_list):
    """Delete a list of tags in this bitmap."""
    _delete_map = 0
    for i in set(_tag_list):
        _delete_map += pow(2, i)
    return bitmap & ~_delete_map


class TestTagMethods(unittest.TestCase):

    def test_get_tag(self):
        bitmap = _put_tags(0, [1, 2, 3, 4, 5])
        # get tag 0,1,9999
        self.assertEqual(_get_tag(bitmap, 0), False)
        self.assertEqual(_get_tag(bitmap, 1), True)
        self.assertEqual(_get_tag(bitmap, 9999), False)

    def test_get_tags(self):
        tag_list = [1, 2, 3, 4]
        self.assertEqual(_get_tags(_put_tags(0, tag_list)), tag_list)

    def test_put_tag(self):
        # add bit tag 1, 00  -> 01
        self.assertEqual(_put_tag(0, 1), 2)
        # add bit tag 1, 01  -> 01
        self.assertEqual(_put_tag(2, 1), 2)
        # add bit tag 2, 010 -> 011
        self.assertEqual(_put_tag(2, 2), 6)

    def test_put_tags(self):
        # add nothing.
        self.assertEqual(_put_tags(0, []), 0)
        # add bit tag [1,2,3,4], 00000 -> 01111
        self.assertEqual(_put_tags(0, [1, 2, 3, 4, ]), 30)
        # add bit tag [1,2,3,4], 01111 -> 01111
        self.assertEqual(_put_tags(30, [1, 2, 3, 4, ]), 30)
        # add bit tag [1,2,3,4,5], 011110 -> 011111
        self.assertEqual(_put_tags(30, [1, 2, 3, 4, 5]), 62)
        # add bit tag [1,1,2,3,4,5], 00000 -> 01111
        self.assertEqual(_put_tags(0, [1, 1, 2, 3, 4, ]), 30)

    def test_delete_tag(self):
        tag_list = [1, 2, 3, 9]
        self.assertEqual(_get_tags(_delete_tag(_put_tags(0, tag_list), 1)), _get_tags(_put_tags(0, tag_list[1:])))
        # Delete an item not exist.
        self.assertEqual(_get_tags(_delete_tag(_put_tags(0, tag_list), 0)), _get_tags(_put_tags(0, tag_list)))

    def test_delete_tags(self):
        tag_list = [1, 2, 3, 9]
        self.assertEqual(_delete_tags(_put_tags(0, tag_list), tag_list), 0)
        self.assertEqual(_delete_tags(_put_tags(0, tag_list), [2, 3, 9]), 2)
        # Delete an item not exist.
        self.assertEqual(_delete_tags(_put_tags(0, tag_list), tag_list + [99]), 0)


if __name__ == '__main__':
    unittest.main()
