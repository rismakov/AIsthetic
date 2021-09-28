from category_constants import OCCASION_TAGS, SEASON_TAGS

def filter_items_in_all_categories(
    filepaths: dict, season: list, occasions: list
) -> dict:
    return {
        cat: filter_items(filepaths[cat], seasons, occasions) 
        for cat in filepaths
    } 


def filter_items(
    filepaths: list, 
    seasons: list=list(SEASON_TAGS.keys()), 
    occasions: list=list(OCCASION_TAGS.keys())
) -> list:
    season_tags = [SEASON_TAGS[season] for season in seasons] 
    occasion_tags = [OCCASION_TAGS[occasion] for occasion in occasions]
    
    return [
        x for x in filepaths if (
            any(tag in x for tag in season_tags)
            and any(tag in x for tag in occasion_tags)
        )
    ]
