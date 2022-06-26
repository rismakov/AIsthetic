import json
import os

from outfit_utils import is_statement_item
from utils import get_filenames_in_dir

from category_constants import TAGS
from utils_constants import OUTFIT_PATH, CLOSET_PATH


class Closet():

    def __init__(self):
        # open or create
        if os.path.isfile(OUTFIT_PATH):
            with open(OUTFIT_PATH, 'r') as f:
                self.outfits = json.load(f)
        else:
            self.create_outfits()

    def get_outfits(self):
        return self.outfits

    def save_outfits(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.outfits, f)

    def _get_tag_overlap(self, items, tags: dict) -> list:
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

    def _is_style_match(self, items):
        """Check if items are a style match.

        Considered a 'style match' if no more than one are 'Statement' pieces.

        Returns
        -------
        bool
        """
        return sum(is_statement_item(item) for item in items) <= 1

    @staticmethod
    def is_statement_outfit(items):
        return sum(is_statement_item(item) for item in items) > 0

    def _item_match_info(self, items: list):
        """Check if items are a match together.

        Considered a match if they contain an overlapping season tag, contain
        an overlapping occasion tag, and are a style match.
        """
        season_tag_overlap = self._get_tag_overlap(items, TAGS['season'])
        occasion_tag_overlap = self._get_tag_overlap(items, TAGS['occasion'])
        return (
            season_tag_overlap
            and occasion_tag_overlap
            and self._is_style_match(items)
        ), season_tag_overlap, occasion_tag_overlap

    def create_outfits(self):
        outerwear = get_filenames_in_dir(f'{CLOSET_PATH}/outerwear')

        # add 'one-piece' outfits
        dresses = get_filenames_in_dir(f'{CLOSET_PATH}/dresses')
        for dress in dresses:
            for outer in outerwear:
                items = [dress, outer]
                is_match, season_tag_overlap, occasion_tag_overlap = (
                    self._item_match_info(items)
                )
                if is_match:
                    self.outfits.append({
                        'dress': dress,
                        'outerwear': outer,
                        'tags': {
                            'season': season_tag_overlap,
                            'occasion': occasion_tag_overlap,
                            'is_statement': Closet.is_statement_outfit(items),
                        }
                    })

        # add 'two-piece' outfits
        tops = get_filenames_in_dir(f'{CLOSET_PATH}/tops')
        bottoms = get_filenames_in_dir(f'{CLOSET_PATH}/bottoms')
        for top in tops:
            for bottom in bottoms:
                for outer in outerwear:
                    items = [top, bottom, outer] 
                    is_match, season_tag_overlap, occasion_tag_overlap = (
                        self._item_match_info(items)
                    )
                    if is_match:
                        self.outfits.append({
                            'top': top,
                            'bottom': bottom,
                            'outerwear': outer,
                            'tags': {
                                'season': season_tag_overlap,
                                'occasion': occasion_tag_overlap,
                                'is_statement': (
                                    Closet.is_statement_outfit(items)
                                ),
                            }
                        })

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


if __name__ == "__main__":
    closet = Closet()
    closet.create_outfits()
    closet.save_outfits(OUTFIT_PATH)