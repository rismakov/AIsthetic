from typing import Tuple

from outfit_utils import get_item_name, is_item_of_type_style, filter_items_by_style

from category_constants import ALL_CATEGORIES


def get_basics_and_statements(closet) -> Tuple[int, dict, dict]:
    """
    Parameters
    ----------
    closet : create_closet.Closet
        The closet, including `items` and `items_tags`.

    Returns
    -------
        Tuple[int, dict, dict]
    """
    count = 0
    basics = {}
    statements = {}
    for cat, cat_items in closet.items.items():
        count += len(closet.items[cat])
        basics[cat] = filter_items_by_style(cat_items, closet.items_tags[cat], 'Basic')
        statements[cat] = filter_items_by_style(cat_items, closet.items_tags[cat], 'Statement')

    return count, basics, statements


def count_item_info(info_placeholder, closet):
    count, basics, statements = get_basics_and_statements(closet)

    info_placeholder.write(f"You have {count} items in your closet.")

    basic_count, statement_count = (
        sum(len(x) for x in basics.values()),
        sum(len(x) for x in statements.values()),
    )
    total = basic_count + statement_count
    info_placeholder.write(
        f'- This includes {basic_count} basic pieces '
        f'({basic_count * 100 / total:.1f}%) and {statement_count} statement '
        f'pieces ({statement_count * 100 / total:.1f}%).'
    )
    info = '- '
    for cat in ALL_CATEGORIES:
        info += f'{len(closet.items[cat])} {cat}, '

    info_placeholder.write(f'{info[:-2]}.')


def count_outfits(info_placeholder, closet):
    outfit_count = len(closet.outfits)
    # count non-statement outfits
    basic_outfit_count = sum(
        not outfit['tags']['is_statement'] for outfit in closet.outfits
    )
    # count distinct statement pieces in statement outfits
    statement_outfits = [
        outfit for outfit in closet.outfits if outfit['tags']['is_statement']
    ]
    unique_statement_pieces = []
    for outfit in statement_outfits:
        for cat, item in outfit.items():
            if is_item_of_type_style(
                closet.items_tags[cat][
                    get_item_name(item, closet.is_user_closet)
                ], 'Statement'
            ):
                unique_statement_pieces.append(item)

    unique_statement_piece_count = len(set(unique_statement_pieces))
    outfit_count_2 = basic_outfit_count + unique_statement_piece_count

    count_item_info(info_placeholder, closet)

    info_placeholder.write(
        f"You have {outfit_count:,} unique outfit combinations ("
        f"{outfit_count_2:,} outfit combinations if only calculating distinct"
        " statement items once)."
    )
