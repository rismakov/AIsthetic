import json

from utils import get_filenames_in_dir

from category_constants import TAGS
from utils_constants import PATH_CLOSET


class Closet():

    def __init__(self):
        # open or create
        self.outfits = []

    def get_tag_overlap(items, tags: dict) -> list:
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

    def is_style_match(items):
        """Check if items are a style match.

        Considered a 'style match' if no more than one are 'Statement' pieces.

        Returns
        -------
        bool
        """
        return sum(TAGS['style']['Statement'] in item for item in items) <= 1
    
    def is_statement_outfit(items):
        return sum(TAGS['style']['Statement'] in item for item in items) > 0

    def item_match_info(items: list):
        """Check if items are a match together.

        Considered a match if they contain an overlapping season tag, contain
        an overlapping occasion tag, and are a style match.
        """
        season_tag_overlap = Closet.get_tag_overlap(items, TAGS['season'])
        occasion_tag_overlap = Closet.get_tag_overlap(items, TAGS['occasion'])
        return (
            season_tag_overlap 
            and occasion_tag_overlap 
            and Closet.is_style_match(items)
        ), season_tag_overlap, occasion_tag_overlap

    def create_outfits(self):
        outerwear = get_filenames_in_dir(f'{PATH_CLOSET}/outerwear')

        # add 'one-piece' outfits
        dresses = get_filenames_in_dir(f'{PATH_CLOSET}/dresses')
        for dress in dresses:
            for outer in outerwear:
                items = [dress, outer]
                is_match, season_tag_overlap, occasion_tag_overlap = (
                    Closet.item_match_info(items)
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
        tops = get_filenames_in_dir(f'{PATH_CLOSET}/tops')
        bottoms = get_filenames_in_dir(f'{PATH_CLOSET}/bottoms')
        for top in tops:
            for bottom in bottoms:
                for outer in outerwear:
                    items = [top, bottom, outer] 
                    is_match, season_tag_overlap, occasion_tag_overlap = (
                        Closet.item_match_info(items)
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
        
        with open('outfits', 'w') as f:
            json.dump(self.outfits, f)

    def remove_outfit():
        pass

if __name__ == "__main__":
    closet = Closet()
    closet.create_outfits()