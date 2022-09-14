import pandas as pd
import streamlit as st

from typing import Dict

from closet_creater import Closet
from count_closet import count_item_info, get_basics_and_statements
from outfit_utils import filter_appropriate_outfits, 
from utils import get_all_image_filenames, stacked_bar_plot

from category_constants import MAIN_CATEGORIES, OCCASIONS, SEASONS
from utils_constants import CLOSET_PATH

import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')

DAYS_PER_SEASON = 90

OUTFITS_PER_SEASON = {
    'Casual': int(DAYS_PER_SEASON * (4/7)),
    'Work': int(DAYS_PER_SEASON * (4/7)),
    'Dinner/Bar': int(DAYS_PER_SEASON * (4/7)),
    'Club/Fancy': int(DAYS_PER_SEASON * (2/7)),
}


class ClosetAnalyzer():

    def __init__(self, items, outfits):
        self.outfits = outfits
        self.items = items

    def count_amounts(self):
        for occasion in OCCASIONS:
            st.header(occasion)
            for season in SEASONS:
                st.subheader(season)

                items_filtered = (
                    self.items, [season], [occasion]
                )
                count_item_info(st.container(), items_filtered)

                _, basics, statements = (
                    get_basics_and_statements(items_filtered)
                )
                fig = stacked_bar_plot(
                    MAIN_CATEGORIES,
                    [len(basics[cat]) for cat in MAIN_CATEGORIES],
                    [len(statements[cat]) for cat in MAIN_CATEGORIES],
                    ['Basic', 'Statement'],
                    ylabel='count',
                )
                st.pyplot(fig)

    def calculate_outfit_count(self, items: Dict[str, str], outfit_max_count):
        _, basics, statements = get_basics_and_statements(items)

        statement_count = 0
        for cat in statements:
            statement_count_cat = len(statements[cat])
            print(
                f'There are {statement_count_cat} {cat} statement pieces and '
                f'{len(basics[cat])} {cat} basic pieces.'
            )
            statement_count += statement_count_cat

        print(f'Ideal number of statement outfits: {int(outfit_max_count * 0.3)}')
        print(f'True number of statement outfits: {statement_count}')
        outfits_left = outfit_max_count - statement_count

        print(f'Number of items left: {outfits_left}')

    def calculate_outfit_count_per_season(self):
        for season in ['Spring']:  # SEASONS:
            print('season:', season)
            for occasion in ['Dinner/Bar']:
                print('occasion:', occasion)

                items_filtered = (
                    self.items, [season], [occasion]
                )

                self.calculate_outfit_count(
                    items_filtered, OUTFITS_PER_SEASON[occasion]
                )

    @staticmethod
    def _get_all_outfits_including_item(outfits, cat, item):
        return [outfit for outfit in outfits if outfit[cat] == item]

    def remove_similar_outfits(self, outfits):
        bottoms = set([outfit['bottom'] for outfit in outfits])
        for bottom in bottoms:
            outfits_tops = set(
                [outfit['tops'] for outfit in (
                    ClosetAnalyzer._get_all_outfits_including_item(
                        outfits, 'bottom', bottom
                    )
                )]
            )

    def analyze_wardrobe():
        pass

if __name__ == "__main__":
    closet_analyzer = ClosetAnalyzer()
    closet_analyzer.calculate_outfit_count_per_season()
