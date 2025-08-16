from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def build_reaction_buttons(post_id):
    reactions = ["😢", "😂", "🤯", "🤬", "❤️"]
    buttons = [
        InlineKeyboardButton(r, callback_data=f"react:{post_id}:{r}") for r in reactions  # noqa: E501
    ]
    return InlineKeyboardMarkup.from_row(buttons)


def build_pagination_buttons(current_page):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⬅️", callback_data=f"page:{current_page-1}"),  # noqa: E501
                InlineKeyboardButton(
                    f"{current_page}", callback_data=f"page:{current_page}"
                ),
                InlineKeyboardButton("➡️", callback_data=f"page:{current_page+1}"),  # noqa: E501
            ]
        ]
    )
