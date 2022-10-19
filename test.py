import unittest

from streamlit.uploaded_file_manager import UploadedFile, UploadedFileRec

import outfit_utils
import outfit_calendar
import setup_tags
import test_constants
import utils

from closet_creater import Closet

CATS = ['tops', 'bottoms', 'dresses', 'outerwear', 'shoes', 'hats', 'bags']


class TestSetupTags(unittest.TestCase):

    def test_is_item_untagged(self):
        self.assertTrue(setup_tags.is_item_untagged(
            test_constants.ITEMS_TAGS,
            'bottoms',
            test_constants.ITEMS['bottoms'][0]
        ))
        self.assertFalse(setup_tags.is_item_untagged(
            test_constants.ITEMS_TAGS,
            'bottoms',
            test_constants.ITEMS['bottoms'][1]
        ))

    def test_is_end_of_category(self):
        self.assertFalse(setup_tags.is_end_of_category(['x', 'y'], 0))

        self.assertFalse(setup_tags.is_end_of_category(['x', 'y'], 1))

        self.assertTrue(setup_tags.is_end_of_category(['x', 'y'], 2))

        self.assertTrue(setup_tags.is_end_of_category(['x', 'y'], 3))

    def test_get_inds_to_tag(self):
        # This is empty. Should return next untagged item.
        self.assertEqual(
            setup_tags.get_inds_to_tag(
                test_constants.ITEMS, test_constants.ITEMS_TAGS, CATS, 0, 0
            ), (1, 0)
        )
        # This is untagged. Should return same values.
        self.assertEqual(
            setup_tags.get_inds_to_tag(
                test_constants.ITEMS, test_constants.ITEMS_TAGS, CATS, 1, 0
            ), (1, 0)
        )
        # This is tagged with nothing after it to tag. Should return None.
        self.assertEqual(
            setup_tags.get_inds_to_tag(
                test_constants.ITEMS, test_constants.ITEMS_TAGS, CATS, 1, 1
            ), (None, None)
        )


class TestOutfitUtils(unittest.TestCase):

    def test_are_tags_in_item(self):
        hats_tags = test_constants.ITEMS_TAGS['hats']
        self.assertTrue(
            outfit_utils.are_tags_in_item(
                hats_tags['beret_bas_ca_wo_bar_fa_wi_.jpeg'],
                ['Fall'],
                ['Casual'],
            )
        )
        # Should be True if at least one True in lists.
        self.assertTrue(
            outfit_utils.are_tags_in_item(
                hats_tags['hat_st_fa_ca_wo_.jpeg'],
                ['Fall'],
                ['Casual'],
            )
        )
        # Should be False if only one tag type is True.
        self.assertFalse(
            outfit_utils.are_tags_in_item(
                hats_tags['beret_bas_ca_wo_bar_fa_wi_.jpeg'],
                ['Summer'],
                ['Casual'],
            )
        )

    def test_filter_appropriate_items(self):
        # filter_appropriate_items
        pass


class TestClosetCreator(unittest.TestCase):

    def get_closet_1(self):
        return Closet(
            items=test_constants.ITEMS,
            items_tags=test_constants.ITEMS_TAGS,
            is_item_upload=True
        )

    def get_closet_2(self):
        return Closet(
            items=test_constants.ITEMS2,
            items_tags=test_constants.ITEMS_TAGS2,
            is_item_upload=True
        )

    def test_get_number_of_statement_pieces(self):
        closet = self.get_closet_1()
        self.assertEqual(
            closet.get_number_of_statement_pieces(test_constants.OUTFIT),
            1
        )

    def test_get_tag_overlap(self):
        closet1 = self.get_closet_1()
        self.assertEqual(
            closet1.get_tag_overlap(test_constants.OUTFIT, 'season'),
            set()
        )
        self.assertEqual(
            closet1.get_tag_overlap(test_constants.OUTFIT, 'occasion'),
            {'Casual'}
        )

        closet2 = self.get_closet_2()
        top1 = test_constants.ITEMS2['tops'][0]
        bottom1 = test_constants.ITEMS2['bottoms'][0]
        bottom2 = test_constants.ITEMS2['bottoms'][1]
        outer1 = test_constants.ITEMS2['outerwear'][0]
        outer2 = test_constants.ITEMS2['outerwear'][1]
        self.assertEqual(
            closet2.get_tag_overlap(
                {'tops': top1, 'bottoms': bottom1, 'outerwear': outer1}, 
                'season'
            ),
            {'Summer', 'Fall'}
        )
        self.assertEqual(
            closet2.get_tag_overlap(
                {'tops': top1, 'bottoms': bottom1, 'outerwear': outer2},
                'season'

            ),
            {'Fall'}
        )
        self.assertEqual(
            closet2.get_tag_overlap(
                {'tops': top1, 'bottoms': bottom2, 'outerwear': outer1},
                'season'
            ),
            {'Summer'}
        )
        self.assertEqual(
            closet2.get_tag_overlap(
                {'tops': top1, 'bottoms': bottom2, 'outerwear': outer2},
                'season'
            ),
            set()
        )

        self.assertEqual(
            closet2.get_tag_overlap(
                {'tops': top1, 'bottoms': bottom1, 'outerwear': outer1}, 
                'occasion'
            ),
            set()
        )
        self.assertEqual(
            closet2.get_tag_overlap(
                {'tops': top1, 'bottoms': bottom1, 'outerwear': outer2},
                'occasion'

            ),
            {'Casual'}
        )
        self.assertEqual(
            closet2.get_tag_overlap(
                {'tops': top1, 'bottoms': bottom2, 'outerwear': outer1},
                'occasion'
            ),
            {'Bar/Dinner'}
        )
        self.assertEqual(
            closet2.get_tag_overlap(
                {'tops': top1, 'bottoms': bottom2, 'outerwear': outer2},
                'occasion'
            ),
            {'Casual', 'Bar/Dinner'}
        )

    def test_is_style_match(self):
        closet1 = self.get_closet_1()
        self.assertTrue(closet1._is_style_match(test_constants.OUTFIT))

        closet2 = self.get_closet_2()
        top1 = test_constants.ITEMS2['tops'][0]
        bottom1 = test_constants.ITEMS2['bottoms'][0]
        bottom2 = test_constants.ITEMS2['bottoms'][1]
        outer1 = test_constants.ITEMS2['outerwear'][0]
        outer2 = test_constants.ITEMS2['outerwear'][1]
        self.assertTrue(closet2._is_style_match(
            {'tops': top1, 'bottoms': bottom1, 'outerwear': outer1}
        ))
        self.assertTrue(closet2._is_style_match(
            {'tops': top1, 'bottoms': bottom1, 'outerwear': outer2}
        ))
        self.assertTrue(closet2._is_style_match(
            {'tops': top1, 'bottoms': bottom2, 'outerwear': outer1}
        ))
        self.assertFalse(closet2._is_style_match(
            {'tops': top1, 'bottoms': bottom2, 'outerwear': outer2}
        ))

    def test_item_match_info(self):
        closet1 = self.get_closet_1()
        self.assertFalse(
            closet1._item_match_info(test_constants.OUTFIT)[0],
            False
        )
        self.assertEqual(
            closet1._item_match_info(test_constants.OUTFIT)[1],
            set()
        )
        self.assertEqual(
            closet1._item_match_info(test_constants.OUTFIT)[2],
            {'Casual'}
        )

        closet2 = self.get_closet_2()
        top1 = test_constants.ITEMS2['tops'][0]
        bottom1 = test_constants.ITEMS2['bottoms'][0]
        bottom2 = test_constants.ITEMS2['bottoms'][1]
        outer1 = test_constants.ITEMS2['outerwear'][0]
        outer2 = test_constants.ITEMS2['outerwear'][1]
        self.assertFalse(
            closet2._item_match_info(
                {'tops': top1, 'bottoms': bottom1, 'outerwear': outer1}
            )[0]
        )
        self.assertTrue(
            closet2._item_match_info(
                {'tops': top1, 'bottoms': bottom1, 'outerwear': outer2}
            )[0]
        )
        self.assertTrue(
            closet2._item_match_info(
                {'tops': top1, 'bottoms': bottom2, 'outerwear': outer1}
            )[0]
        )
        self.assertFalse(
            closet2._item_match_info(
                {'tops': top1, 'bottoms': bottom2, 'outerwear': outer2}
            )[0]
        )

    def test_create_outfits(self):
        closet2 = self.get_closet_2()
        top1 = test_constants.ITEMS2['tops'][0]
        bottom1 = test_constants.ITEMS2['bottoms'][0]
        bottom2 = test_constants.ITEMS2['bottoms'][1]
        outer1 = test_constants.ITEMS2['outerwear'][0]
        outer2 = test_constants.ITEMS2['outerwear'][1]

        self.assertEqual(
            closet2.outfits,
            [
                {
                    **{'tops': top1, 'bottoms': bottom1, 'outerwear': outer2},
                    **{'tags': {
                        'is_statement': True,
                        'season': {'Fall'},
                        'occasion': {'Casual'}
                    }},
                },
                {
                    **{'tops': top1, 'bottoms': bottom2, 'outerwear': outer1},
                    **{'tags': {
                        'is_statement': True,
                        'season': {'Summer'},
                        'occasion': {'Bar/Dinner'}
                    }},
                },
            ],
        )


class TestOutfitCalendar(unittest.TestCase):

    def test_is_any_exclude_item_in_outfit(self):
        test_exclude_items = {
            'bottoms': [
                UploadedFile(UploadedFileRec(
                    id=114,
                    name='91_bas_su_ca_.jpg',
                    type='image/jpeg',
                    data=b""
                    )
                ),
                UploadedFile(UploadedFileRec(
                    id=114,
                    name='not_in_outfit.jpg',
                    type='image/jpeg',
                    data=b""
                    )
                )
            ],
        }
        self.assertTrue(
            outfit_calendar.is_any_exclude_item_in_outfit(
                test_constants.OUTFIT, test_exclude_items, is_item_upload=True
            )
        )
        test_exclude_items = {'bottoms': [], 'tops': []}
        self.assertFalse(
            outfit_calendar.is_any_exclude_item_in_outfit(
                test_constants.OUTFIT, test_exclude_items, is_item_upload=True
            )
        )
        test_exclude_items = {
            'bottoms': [
                UploadedFile(UploadedFileRec(
                    id=114,
                    name='not_in_outfit.jpg',
                    type='image/jpeg',
                    data=b""
                    )
                )
            ],
        }
        self.assertFalse(
            outfit_calendar.is_any_exclude_item_in_outfit(
                test_constants.OUTFIT, test_exclude_items, is_item_upload=True
            )
        )


class TestUtils(unittest.TestCase):

    def test_update_keys(self):
        mapping = {
            'old_1': 'new_1',
            'old_2': 'new_2',
        }
        self.assertEqual(
            utils.update_keys(
                {
                    'old_1': 'value_1', 
                    'old_2': 'value_2',
                    'same_1': 'value_3', 
                    'same_2': 'value_4',
                },
                mapping
            ),
            {
                'new_1': 'value_1', 
                'new_2': 'value_2',
                'same_1': 'value_3', 
                'same_2': 'value_4',
            }
        )



if __name__ == '__main__':
    unittest.main()
