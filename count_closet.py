from outfit_utils import is_statement_item

from category_constants import ALL_CATEGORIES

def get_basics_and_statements(items):
    count = 0
    basics = []
    statements = []
    for cat in items:
        count += len(items[cat])
        for item in items[cat]:
            if not is_statement_item(item): 
                basics.append(item)
            elif is_statement_item(item): 
                statements.append(item)
    return count, basics, statements


def count_item_info(info_placeholder, items):
    count, basics, statements = get_basics_and_statements(items)

    info_placeholder.write(f"You have {count} items in your closet.")

    basic_count, statement_count = len(basics), len(statements)
    total = basic_count + statement_count
    info_placeholder.write(
        f'- This includes {basic_count} basic pieces '
        f'({basic_count * 100 / total:.1f}%) and {statement_count} statement '
        f'pieces ({statement_count * 100 / total:.1f}%).'
    )
    info = '- '
    for cat in ALL_CATEGORIES:
        info += f'{len(items[cat])} {cat}, '
    
    info_placeholder.write(f'{info[:-2]}.')


def count_outfits(info_placeholder, outfits, items=[]):
    outfit_count = len(outfits)
    # count non-statement outfits
    basic_outfit_count = sum(
        not outfit['tags']['is_statement'] for outfit in outfits
    )
    # count distinct statement pieces in statement outfits
    statement_outfits = [
        outfit for outfit in outfits if outfit['tags']['is_statement']
    ]
    unique_statement_pieces = [
        [
            item for item in outfit.values() if is_statement_item(item)
        ][0] for outfit in statement_outfits
    ]
    unique_statement_piece_count = len(set(unique_statement_pieces))
    outfit_count_2 = basic_outfit_count + unique_statement_piece_count

    if items:
        count_item_info(info_placeholder, items)
    
    info_placeholder.write(
        f"You have {outfit_count:,} unique outfit combinations ("
        f"{outfit_count_2:,} outfit combinations if only calculating distinct"
        " statement items once)."
    )
