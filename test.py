import unittest

from datetime import datetime
from streamlit.uploaded_file_manager import UploadedFile, UploadedFileRec

# methods
import outfit_selection_utils
import outfit_utils
import setup_tags
import utils

# constants
import test_constants

# classes
from outfit_calendar import OutfitCalendar
from closet_creater import Closet


CATS = ['tops', 'bottoms', 'dresses', 'outerwear', 'shoes', 'hats', 'bags']


class TestSetupTags(unittest.TestCase):

    def test_is_end_of_category(self):
        self.assertFalse(setup_tags.is_end_of_category(['x', 'y'], 0))

        self.assertFalse(setup_tags.is_end_of_category(['x', 'y'], 1))

        self.assertTrue(setup_tags.is_end_of_category(['x', 'y'], 2))

        self.assertTrue(setup_tags.is_end_of_category(['x', 'y'], 3))

    def test_get_next_cat_and_item_inds(self):
        items = test_constants.ONE_OF_EACH_ITEMS
        self.assertEqual(
            setup_tags.get_next_cat_and_item_inds(items, CATS, 0, 0), (1, 0)
        )
        self.assertEqual(
            setup_tags.get_next_cat_and_item_inds(items, CATS, 1, 0), (2, 0)
        )
        self.assertEqual(
            setup_tags.get_next_cat_and_item_inds(items, CATS, 2, 0), (3, 0)
        )
        self.assertEqual(
            setup_tags.get_next_cat_and_item_inds(items, CATS, 3, 0), (4, 0)
        )
        self.assertEqual(
            setup_tags.get_next_cat_and_item_inds(items, CATS, 4, 0), (5, 0)
        )
        self.assertEqual(
            setup_tags.get_next_cat_and_item_inds(items, CATS, 5, 0), (6, 0)
        )
        self.assertEqual(
            setup_tags.get_next_cat_and_item_inds(items, CATS, 6, 0),
            (None, None)
        )

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

        # Test empty `items_tags` case.
        self.assertEqual(
            setup_tags.get_inds_to_tag(
                test_constants.ITEMS, {}, CATS, 0, 0
            ), (1, 0)
        )

        self.assertEqual(
            setup_tags.get_inds_to_tag(
                test_constants.ONE_OF_EACH_ITEMS, {}, CATS, 0, 0
            ), (0, 0)
        )

        self.assertEqual(
            setup_tags.get_inds_to_tag(
                test_constants.ONE_OF_EACH_ITEMS, {}, CATS, 4, 0
            ), (4, 0)
        )


class TestOutfitUtils(unittest.TestCase):

    def test_are_tags_in_item(self):
        hats_tags = test_constants.ITEMS_TAGS['hats']
        self.assertTrue(
            outfit_utils.are_tags_in_item(
                hats_tags['basic_fall_casual_hat.jpeg'],
                ['Fall'],
                ['Casual'],
            )
        )
        # Should be True if at least one True in lists.
        self.assertTrue(
            outfit_utils.are_tags_in_item(
                hats_tags['basic_warm_casual_fall_hat.jpeg'],
                ['Fall'],
                ['Casual'],
            )
        )
        # Should be False if only one tag type is True.
        self.assertFalse(
            outfit_utils.are_tags_in_item(
                hats_tags['basic_fall_casual_hat.jpeg'],
                ['Summer'],
                ['Casual'],
            )
        )

    def test_is_item_of_type_style(self):
        cat_items_tags = test_constants.ITEMS_TAGS['hats']
        for item in [
            'basic_fall_casual_hat.jpeg', 'basic_warm_casual_fall_hat.jpeg'
        ]:
            self.assertTrue(
                outfit_utils.is_item_of_type_style(
                    cat_items_tags[item], 'Basic'
                )
            )
            self.assertFalse(
                outfit_utils.is_item_of_type_style(
                    cat_items_tags[item], 'Statement'
                )
            )

        item = 'statement_fall_causal_work_hat.jpeg'
        self.assertFalse(
            outfit_utils.is_item_of_type_style(cat_items_tags[item], 'Basic')
        )
        self.assertTrue(
            outfit_utils.is_item_of_type_style(cat_items_tags[item], 'Statement')
        )

    def test_filter_appropriate_items(self):
        # filter_appropriate_items
        pass


class TestClosetCreator(unittest.TestCase):

    def get_closet_1(self):
        return Closet(
            items=test_constants.ITEMS,
            items_tags=test_constants.ITEMS_TAGS,
            is_user_closet=True
        )

    def get_closet_2(self):
        return Closet(
            items=test_constants.ITEMS2,
            items_tags=test_constants.ITEMS_TAGS2,
            is_user_closet=True
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


class TestOutfitSelection(unittest.TestCase):

    def test_get_outfit_options(self):
        closet = Closet(
            items=test_constants.ITEMS,  # not used below
            items_tags=test_constants.ITEMS_TAGS,  # not used below
            is_user_closet=True,
            outfits=test_constants.TEST_OUTFITS_LIST
        )

        recently_worn = {
            'tops': [UploadedFile(UploadedFileRec(
                id=3, name='black_ruched_top.webp', type='image/webp', data=b""
            ))]
        }

        summer_dinner_response = outfit_selection_utils.get_outfit_options(
            closet, 'Summer', 'Bar/Dinner'
        )
        spring_work_response = outfit_selection_utils.get_outfit_options(
            closet, 'Spring', 'Work'
        )
        winter_casual_response = outfit_selection_utils.get_outfit_options(
            closet, 'Winter', 'Casual'
        )
        spring_work_response_2 = outfit_selection_utils.get_outfit_options(
            closet, 'Spring', 'Work', recently_worn
        )
        responses = {
            'summer_bar': (summer_dinner_response, test_constants.SUMMER_DINNER_OUTFITS),
            'spring_work': (spring_work_response, test_constants.SPRING_WORK_OUTFITS),
            'winter_casual': (winter_casual_response, test_constants.WINTER_CASUAL_OUTFITS),
            'spring_work_2': (spring_work_response_2, test_constants.SPRING_WORK_OUTFITS_2),
        }

        for x, y in responses.values():
            self.assertEqual(len(x), len(y))
            for i, v in enumerate(x):
                self.assertEqual(len(v), len(y[i]))
                for cat in CATS:
                    if v.get(cat):
                        self.assertEqual(v.get(cat).name, y[i].get(cat).name)

    def test_update_recently_worn_threshold(self):
        recently_worn = {
            'tops': [UploadedFile(UploadedFileRec(
                id=3, name='top_1.webp', type='image/webp', data=b""
            ))],
            'outerwear': [UploadedFile(UploadedFileRec(
                id=25, name='outerwear.jpg', type='image/jpeg', data=b""
            ))]
        }
        recently_worn_cats = [['tops', 'outerwear'], ['outerwear']]
        response = outfit_selection_utils.update_recently_worn_threshold(
            recently_worn, recently_worn_cats
        )
        answer = {
            'tops': [UploadedFile(UploadedFileRec(
                id=3, name='top_1.webp', type='image/webp', data=b""
            ))],
            'outerwear': [],
        }
        for cat in CATS:
            self.assertEqual(
                len(response.get(cat, [])), len(answer.get(cat, []))
            )
            if response.get(cat, []):
                for i, x in enumerate(response[cat]):
                    self.assertEqual(x.name, answer[cat][i].name)

    def test_get_non_recently_worn_options(self):
        recently_worn = {
            'tops': [test_constants.SUMMER_DINNER_OUTFITS[0]['tops']]
        }
        # should not remove anything because no other options available
        print('1')
        self.assertEqual(
            len(outfit_selection_utils.get_non_recently_worn_options(
                test_constants.SUMMER_DINNER_OUTFITS, recently_worn, True
            )),
            len(test_constants.SUMMER_DINNER_OUTFITS)
        )
        print('2')
        # should remove because in `recently_worn`
        recently_worn = {
            'tops': [test_constants.SPRING_WORK_OUTFITS[0]['tops']]
        }
        self.assertEqual(
            len(outfit_selection_utils.get_non_recently_worn_options(
                test_constants.SPRING_WORK_OUTFITS, recently_worn, True
            )),
            len(test_constants.SPRING_WORK_OUTFITS[1:])
        )
        # should remove only one, because both include one recently worn item,
        # but only one includes other recently worn item
        print('3')
        recently_worn = {
            'tops': [UploadedFile(UploadedFileRec(
                id=3, name='top_1.webp', type='image/webp', data=b""
            ))],
            'outerwear': [UploadedFile(UploadedFileRec(
                id=25, name='outerwear.jpg', type='image/jpeg', data=b""
            ))]
        }
        self.assertEqual(
            len(outfit_selection_utils.get_non_recently_worn_options(
                test_constants.TEST_OUTFITS_FOR_RECENTLY_WORN, recently_worn, True
            )),
            len(test_constants.TEST_OUTFITS_FOR_RECENTLY_WORN[1:])
        )

    def test_get_all_exclude_items_in_outfit(self):
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
        self.assertListEqual(
            outfit_selection_utils.get_all_exclude_items_in_outfit(
                test_constants.OUTFIT, test_exclude_items, is_user_closet=True
            ), ['bottoms']
        )
        test_exclude_items = {'bottoms': [], 'tops': []}
        self.assertListEqual(
            outfit_selection_utils.get_all_exclude_items_in_outfit(
                test_constants.OUTFIT, test_exclude_items, is_user_closet=True
            ), []
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
        self.assertListEqual(
            outfit_selection_utils.get_all_exclude_items_in_outfit(
                test_constants.OUTFIT, test_exclude_items, is_user_closet=True
            ), []
        )


class TestOutfitCalendar(unittest.TestCase):
    RECENTLY_WORN_INIT = {
        'tops': [],
        'bottoms': [],
        'dresses': [],
        'outerwear': [],
    }

    def test_init_most_recently_worn(self):
        self.assertEqual(
            OutfitCalendar._init_most_recently_worn(),
            TestOutfitCalendar.RECENTLY_WORN_INIT
        )

    def test_update_most_recently_worn(self):
        outfit = {
            **test_constants.OUTFIT,
            **{'tags': {
                'style': ['Basic'],
                'season': ['Summer'],
                'occasion': ['Casual']
            }}
        }
        calendar = OutfitCalendar(
            closet=Closet(
                items={cat: [v] for cat, v in test_constants.OUTFIT.items()},
                items_tags={},
                outfits=[outfit]
            ),
            start_date=datetime(2022, 10, 1),
            end_date=datetime(2022, 10, 2),
            weather_types=['Hot', 'Warm'],
            occasion='Casual',
            amount='entire closet',
            include_accessories=False
        )

        self.assertEqual(
            calendar._update_most_recently_worn(
                test_constants.OUTFIT, TestOutfitCalendar.RECENTLY_WORN_INIT
            ),
            {
                **{cat: [v] for cat, v in test_constants.OUTFIT.items()}, 
                **{'dresses': []}
            }
        )

    def test_get_seasons_set_from_weather_types(self):
        summers = ['Hot', 'Warm', 'Warm', 'Hot']
        summers_falls = ['Hot', 'Rainy', 'Warm', 'Chilly', 'Warm']
        all_seasons = ['Hot', 'Warm', 'Mild', 'Chilly', 'Cold']
        self.assertEqual(
            OutfitCalendar._get_seasons_set_from_weather_types(summers),
            {'Summer'}
        )
        self.assertEqual(
            OutfitCalendar._get_seasons_set_from_weather_types(summers_falls),
            {'Summer', 'Fall'}
        )
        self.assertEqual(
            OutfitCalendar._get_seasons_set_from_weather_types(all_seasons),
            {'Summer', 'Fall', 'Winter', 'Spring'}
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
