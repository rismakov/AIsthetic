import json
import os

from streamlit.uploaded_file_manager import UploadedFile
from typing import Dict, List, Optional, Union

from outfit_utils import is_statement_item
from utils import get_all_image_filenames, get_filenames_in_dir

from utils_constants import NEW_ITEMS_PATH


class Closet():

    def __init__(
        self,
        items: Dict[str, List[Union[str, UploadedFile]]],
        items_tags: [Dict[str, dict]] = {},
        outfits: Optional[list] = [],
        is_user_closet: bool = False
    ):
        """Initializes `items`, `outfits`, and `item_tags`.

        If `outfits` isn't passed in, creates it from `items`.
        """
        self.items = items
        self.outfits = outfits
        self.items_tags = items_tags
        self.is_user_closet = is_user_closet

        if not self.outfits:
            print('Creating closet...')
            self.create_outfits(self.items)

    def _get_item_name(self, item):
        if self.is_user_closet:
            return item.name
        return item

    def save_outfits(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.outfits, f)

    def get_tag_overlap(
        self,
        outfit_option: Dict[str, UploadedFile],
        tag_type: str = None
    ) -> set:
        """Get intersection of `tags` in `group_items`.

        Parameters
        ----------
        outfit_option : list
            A group of items, including either 'top', 'bottom' and 'outer', or
            'dress' and 'outer'.
        tag_markers : Dict[str, str]
            The key is the tag (e.g. 'Summer', 'Work', etc) and the value is
            the tag flag that can be found in the item name (e.g. 'su_' for
            'Summer'). This must be passed in if `self.items_tags` is None.
        tag_type : str
            The type of tags. Must be either `season` or `occasion`. This is
            only necessary to pass in if using `self.item_tags`.

        Returns
        -------
        list
        """
        tags = []
        for cat, item in outfit_option.items():
            item_name = self._get_item_name(item)
            tags.append(self.items_tags[cat][item_name][tag_type])
        return set(tags[0]).intersection(*tags[1:])

    def get_number_of_statement_pieces(self, outfit):
        return sum(
            is_statement_item(
                item, self.items_tags[cat][self._get_item_name(item)]
            ) for cat, item in outfit.items()
        )

    def _is_style_match(self, outfit):
        """Check if items are a style match.

        Considered a 'style match' if no more than one are 'Statement' pieces.

        Returns
        -------
        bool
        """
        return self.get_number_of_statement_pieces(outfit) <= 1

    def _item_match_info(self, outfit: Dict[str, UploadedFile]) -> bool:
        """Check if items are a match together.

        Considered a match if they contain an overlapping season tag, contain
        an overlapping occasion tag, and are a style match.

        Parameters
        ----------
        outfit : Dict[str, UploadedFile]
            Either list of a top, bottom, outerwear item group, or dress and
            outerwear item group.

        Returns
        -------
        bool
            True if items in `item_group` fit together.
        """
        season_tag_overlap = self.get_tag_overlap(outfit, 'season')
        occasion_tag_overlap = self.get_tag_overlap(outfit, 'occasion')
        return (
            season_tag_overlap
            and occasion_tag_overlap
            and self._is_style_match(outfit)
        ), season_tag_overlap, occasion_tag_overlap

    def _add_tags_info_to_outfit(self, outfit, season_tags, occasion_tags):
        tags = {
            'tags': {
                'season': season_tags,
                'occasion': occasion_tags,
                'is_statement': self.get_number_of_statement_pieces(outfit) > 0,
            }
        }
        return {**outfit, **tags}

    def create_outfits(self, items):
        # add 'one-piece' outfits
        dresses = items['dresses']
        for dress in dresses:
            for outer in items['outerwear']:
                outfit_option = {'dresses': dress, 'outerwear': outer}
                is_match, season_tag_overlap, occasion_tag_overlap = (
                    self._item_match_info(outfit_option)
                )
                if is_match:
                    self.outfits.append(
                        self._add_tags_info_to_outfit(
                            outfit_option, season_tag_overlap, occasion_tag_overlap
                        )
                    )
        print(f'Created {len(self.outfits)} one-piece outfits')

        # add 'two-piece' outfits
        for top in items['tops']:
            for bottom in items['bottoms']:
                for outer in items['outerwear']:
                    outfit_option = {
                        'tops': top, 'bottoms': bottom, 'outerwear': outer
                    }
                    is_match, season_tag_overlap, occasion_tag_overlap = (
                        self._item_match_info(outfit_option)
                    )
                    if is_match:
                        self.outfits.append(
                            self._add_tags_info_to_outfit(
                                outfit_option, season_tag_overlap, occasion_tag_overlap
                            )
                        )
        print(f'Created {len(self.outfits)} one-pieces and two-piece outfits')

    def remove_item(self, cat, item):
        # remove item
        os.remove(item)

        # remove outfits that include item
        self.outfits = [
            outfit for outfit in self.outfits if outfit.get(cat, '') != item
        ]
        self.save_outfits('outfits')

    def remove_outfit(self, outfit_to_remove, outfit_path):
        self.outfits = [outfit for outfit in self.outfits if not all(
            outfit.get(cat) == outfit_to_remove[cat] for cat in outfit_to_remove
        )]
        self.save_outfits(outfit_path)

    def add_items(self, outfit_path):
        new_items = get_all_image_filenames(NEW_ITEMS_PATH)

        for cat in new_items:
            items_to_add = {cat: [] for cat in new_items}
            items_to_add[cat] = new_items[cat]
            print(f'Adding {len(new_items[cat])} new {cat} items to outfits...')
            self.create_outfits(items_to_add)

        print('Saving outfits...')
        self.save_outfits(outfit_path)


if __name__ == "__main__":
    closet = Closet()
    # closet.add_items()
    closet.create_outfits()
    closet.save_outfits(OUTFIT_PATH)
    # item = 'closet/outerwear/91LO1uzkZ3L_bas_fa_sp_ca_wo_bar_f_._AC_SX342'
    # closet.remove_item('bottoms', item)
