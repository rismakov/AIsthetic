import pandas as pd
import streamlit as st

from typing import Dict

from count_closet import count_item_info, get_basics_and_statements
from outfit_utils import filter_appropriate_items, filter_items_by_style
from plotting_utils import stacked_bar_plot

from category_constants import MAIN_CATEGORIES, OCCASIONS, SEASONS

import matplotlib.pyplot as plt

plt.style.use('fivethirtyeight')

# should be 30-50% statement and 50-70% basic items for each season/occasion.


class ClosetAnalyzer():

    def __init__(self, closet):
        self.closet = closet

    def get_item_counts(self, filtered_items: dict, closet) -> dict:
        item_counts = {}
        for cat, cat_items in filtered_items.items():
            item_counts[cat] = {'Basic': [], 'Statement': []}
            for style in ['Basic', 'Statement']:
                item_counts[cat][style] = filter_items_by_style(
                    cat_items,
                    closet.items_tags[cat],
                    closet.is_user_closet,
                    style,
                )

        return item_counts

    def count_amounts(self):
        for season in SEASONS:
            st.header(season)
            fig, ax = plt.subplots(2, 2, figsize=(15, 12))
            for i, occasion in enumerate(OCCASIONS):
                items_filtered = filter_appropriate_items(
                    self.closet, [season], [occasion]
                )
                item_counts = self.get_item_counts(items_filtered, self.closet)

                cat_counts_by_style = {}
                for style in ['Basic', 'Statement']:
                    cat_counts_by_style[style] = [
                        len(
                            item_counts.get(cat, {}).get(style, [])
                        ) for cat in MAIN_CATEGORIES
                    ]

                fig, ax = stacked_bar_plot(
                    fig, ax,
                    MAIN_CATEGORIES,
                    cat_counts_by_style['Basic'],
                    cat_counts_by_style['Statement'],
                    ax_i=i,
                    title=occasion,
                )
            handles, _ = plt.gca().get_legend_handles_labels()
            fig.legend(handles, ['Basic', 'Statement'], loc='upper center')
            fig.suptitle(season)
            plt.tight_layout()
            st.pyplot(fig)
