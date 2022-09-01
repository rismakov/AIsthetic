import json
import os

from outfit_utils import is_statement_item
from utils import get_all_image_filenames, get_filenames_in_dir

from category_constants import TAGS
from utils_constants import CLOSET_PATH, NEW_ITEMS_PATH, OUTFIT_PATH


class Closet():

    def __init__(self):
        # open or create
        if os.path.isfile(OUTFIT_PATH):
            print('Loading `outfits`...')
            with open(OUTFIT_PATH, 'r') as f:
                self.outfits = json.load(f)
        else:
            print('Creating closet...')
            self.outfits = []
            self.create_outfits()

    def get_outfits(self):
        return self.outfits

    def save_outfits(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.outfits, f)

    @staticmethod
    def _get_tag_overlap(items, tags: dict) -> list:
        """
        Returns
        -------
        list
        """
        return [
            tag_key for tag_key, tag in tags.items() if all(
                tag in item for item in items
            )
        ]

    @staticmethod
    def _is_style_match(items):
        """Check if items are a style match.

        Considered a 'style match' if no more than one are 'Statement' pieces.

        Returns
        -------
        bool
        """
        return sum(is_statement_item(item) for item in items) <= 1

    @staticmethod
    def _is_statement_outfit(items):
        return sum(is_statement_item(item) for item in items) > 0

    def _item_match_info(self, items: list):
        """Check if items are a match together.

        Considered a match if they contain an overlapping season tag, contain
        an overlapping occasion tag, and are a style match.
        """
        season_tag_overlap = Closet._get_tag_overlap(items, TAGS['season'])
        occasion_tag_overlap = Closet._get_tag_overlap(items, TAGS['occasion'])
        return (
            season_tag_overlap
            and occasion_tag_overlap
            and Closet._is_style_match(items)
        ), season_tag_overlap, occasion_tag_overlap

    def _add_tags_info_to_outfit(self, outfit, season_tags, occasion_tags):
        tags = {
            'tags': {
                'season': season_tags,
                'occasion': occasion_tags,
                'is_statement': Closet._is_statement_outfit(outfit.values()),
            }
        }
        return {**outfit, **tags}

    @staticmethod
    def _check_if_in_dict(items: dict, cat: str) -> list:
        """Returns items in dict if exists in key `cat`, else opens from file.
        """
        if not items:
            return get_filenames_in_dir(f'{CLOSET_PATH}/{cat}')
        if not items[cat]:
            return get_filenames_in_dir(f'{CLOSET_PATH}/{cat}')
        return items[cat]

    def create_outfits(self, items_to_add: dict = None):
        outfits = []

        outerwear = Closet._check_if_in_dict(items_to_add, 'outerwear')

        # add 'one-piece' outfits
        dresses = Closet._check_if_in_dict(items_to_add, 'dresses')
        for dress in dresses:
            for outer in outerwear:
                items = [dress, outer]
                is_match, season_tag_overlap, occasion_tag_overlap = (
                    self._item_match_info(items)
                )
                if is_match:
                    outfit = {'dress': dress, 'outerwear': outer}
                    outfits.append(
                        self._add_tags_info_to_outfit(
                            outfit, season_tag_overlap, occasion_tag_overlap
                        )
                    )

        # add 'two-piece' outfits
        tops = Closet._check_if_in_dict(items_to_add, 'tops')
        bottoms = Closet._check_if_in_dict(items_to_add, 'bottoms')
        for top in tops:
            for bottom in bottoms:
                for outer in outerwear:
                    items = [top, bottom, outer]
                    is_match, season_tag_overlap, occasion_tag_overlap = (
                        self._item_match_info(items)
                    )
                    if is_match:
                        outfit = {
                            'top': top, 'bottom': bottom, 'outerwear': outer
                        }
                        outfits.append(
                            self._add_tags_info_to_outfit(
                                outfit, season_tag_overlap, occasion_tag_overlap
                            )
                        )
        self.outfits += outfits

    def remove_item(self, cat, item):
        # remove item
        os.remove(item)

        # remove outfits that include item
        self.outfits = [
            outfit for outfit in self.outfits if outfit.get(cat, '') != item
        ]
        self.save_outfits('outfits')

    def remove_outfit(self, outfit_to_remove):
        self.outfits = [outfit for outfit in self.outfits if not all(
            outfit.get(cat) == outfit_to_remove[cat] for cat in outfit_to_remove
        )]
        self.save_outfits(OUTFIT_PATH)

    def add_items(self):
        new_items = get_all_image_filenames(NEW_ITEMS_PATH)

        for cat in new_items:
            items_to_add = {cat: [] for cat in new_items}
            items_to_add[cat] = new_items[cat]
            print(f'Adding {len(new_items[cat])} new {cat} items to outfits...')
            self.create_outfits(items_to_add)

        print('Saving outfits...')
        self.save_outfits(OUTFIT_PATH)


if __name__ == "__main__":
    closet = Closet()
    # closet.add_items()
    closet.create_outfits()
    closet.save_outfits(OUTFIT_PATH)
    # item = 'closet/outerwear/91LO1uzkZ3L_bas_fa_sp_ca_wo_bar_f_._AC_SX342'
    # closet.remove_item('bottoms', item)
