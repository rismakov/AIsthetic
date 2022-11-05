import json
import random
import streamlit as st

from datetime import date
from typing import Dict, List

from count_closet import count_outfits
from get_weather import get_projected_weather
from outfit_selection_utils import choose_outfit
from webapp_error_messages import weather_info_not_found_message
from utils import daterange, get_filenames_in_dir, increment_i

from category_constants import (
    CADENCES,
    DOWS,
    OUTFIT_AMOUNT,
    WEATHER_ICON_MAPPING,
    WEATHER_TO_SEASON_MAPPINGS,
)
from utils_constants import CLOSET_PATH

# References:
# https://daleonai.com/social-media-fashion-ai


class OutfitCalendar():

    def __init__(
        self,
        closet,
        start_date,
        end_date,
        weather_types,
        occasion: str,
        amount: str,
        include_accessories: bool,
        work_dow: List[str] = DOWS[1:-1],
    ):
        """Initialize `OutfitCalendar`.

        Parameters
        ----------
        closet : create_closet.Closet
        start_date : datetime.datetime
            The start date of the outfit plan.
        end_date : datetime.datetime
            The end date of the outfit plan.
        weather_types : List[str]
            The weather type (e.g. 'Hot', 'Chilly', etc.) from `start_date` to
            `end_date`.
        occasion : str
            The occasion type (i.e, 'Casual', 'Dinner/Bar').
        amount : str
            The amount to pack for (i.e. 'small carry-on suitcase', 'medium
            suitcase').
        include_accessories : bool
            Whether to include accessories in the outfit plan.
        work_dow : List[str]
            Default is Monday through Friday.
        """
        if len(weather_types) != (end_date - start_date).days + 1:
            raise Exception(
                "`weather_types` must be the same length as `start_date` to "
                "`end_date`"
            )

        self.closet = closet
        self.start_date = start_date
        self.end_date = end_date
        self.occasion = occasion
        self.amount = amount
        self.include_accessories = include_accessories
        self.work_dow = work_dow

        self.outfit_plan = self._create_outfit_plan(weather_types)

    @staticmethod
    def _get_seasons_set_from_weather_types(weather_types: List[str]):
        """Return season types based on scraped weather.

        Parameters
        ----------
        weather_info : List[str]
            Example: ['Hot', 'Rainy', 'Mild', ...]

        Returns
        -------
        set
        """
        weather_type_set = set(weather_types)
        season_types = set(
            WEATHER_TO_SEASON_MAPPINGS[weather_type]
            for weather_type in weather_type_set
        )

        st.write(
            "This trip requires planning for the following season types:"
            f"{', '.join(season_types)}."
        )

        return season_types

    @staticmethod
    def _init_most_recently_worn():
        return {cat: [] for cat in ['tops', 'bottoms', 'dresses', 'outerwear']}

    def _update_most_recently_worn(
        self, outfit: dict, recently_worn: dict
    ) -> dict:
        """Add outfit to `recently_worn` list based on `self.amount`.

        For example, if amount allows for a top to be worn once every 5 days,
        `recently_worn` should be tracking all tops that were worn within the
        last 5 days.

        Parameters
        ----------
        outfit : dict
        recently_worn : dict

        Returns
        -------
        dict
        """
        for cat, cadence in CADENCES[self.amount].items():
            if outfit.get(cat):
                recently_worn[cat] = (
                    [outfit[cat]] + recently_worn[cat]
                )[:cadence]
        return recently_worn

    def save_outfit_plan(self, outfits, city):
        path = f'outfit_plans/{city}_{self.start_date}_{self.end_date}.json'
        with open(path, 'w') as f:
            json.dump(outfits, f)

    def _create_outfit_plan(self, weather_types: List[str]):
        """Get outfit plan from `start_date` to `end_date`.

        Parameters
        ----------
        weather_types : List[str]
            The weather types (i.e. 'Hot', 'Warm', 'Chilly') of the specified
            days.

        Returns
        -------
        list
            List of outfits from `start_date` to `end_date`.
        """
        occasion_outfit_plan = {'dates': [], 'outfits': []}

        recently_worn = OutfitCalendar._init_most_recently_worn()
        for weather_type, outfit_date in zip(
            weather_types, daterange(self.start_date, self.end_date)
        ):
            # Don't add outfit for `occasion`='Work' if its a non-work day
            work_dow_ints = [
                i for i, day in enumerate(DOWS) if day in self.work_dow
            ]
            if (
                outfit_date.weekday() not in work_dow_ints
                and self.occasion == 'Work'
            ):
                continue

            occasion_outfit_plan['dates'].append(outfit_date)
            outfit = choose_outfit(
                self.closet,
                weather_type,
                self.occasion,
                self.include_accessories,
                recently_worn=recently_worn,
            )

            occasion_outfit_plan['outfits'].append(outfit)
            recently_worn = self._update_most_recently_worn(outfit, recently_worn)

        return occasion_outfit_plan


class OutfitCalendars():
    """Creates plans for all specified occasions (e.g. 'Casual', 'Work', etc)."""

    def __init__(
        self,
        closet,
        start_date,
        end_date,
        city: str,
        country: str,
        occasions: List[str],
        amount: str,
        include_accessories: bool,
        work_dow: List[str] = DOWS[1:-1],
    ):
        self.weather_info = get_projected_weather(
            start_date, end_date, city, country,
        )
        if not self.weather_info['temps']:
            weather_info_not_found_message()

        self.plans = [
            OutfitCalendar(
                closet,
                start_date,
                end_date,
                self.weather_info['weather_types'],
                occasion,
                amount,
                include_accessories,
                work_dow
            ) for occasion in occasions
        ]
