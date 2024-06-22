"""
Solitaire clone.
"""
import arcade
import cards

# Screen title and size
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Drag and Drop Cards"


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        #  list of cards
        self.card_list = None
        arcade.set_background_color(arcade.color.AMAZON)

        #  cards being dragged
        self.held_cards = None
        #  og location
        self.held_cards_og_pos = None

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """
        #  cards being dragged
        self.held_cards = []
        self.held_cards_og_pos = []

        # Sprite list with all the cards, no matter what pile they are in.
        self.card_list = arcade.SpriteList()

        # Create every card
        for card_suit in cards.CARD_SUITS:
            for card_value in cards.CARD_VALUES:
                card = cards.Card(card_suit, card_value, cards.CARD_SCALE)
                card.position = cards.START_X, cards.BOTTOM_Y
                self.card_list.append(card)

    def pull_to_top(self, card: arcade.Sprite):
        """ Pull card to top of rendering order (last to render, looks on-top) """
        # Remove, and append to the end
        self.card_list.remove(card)
        self.card_list.append(card)

    def on_draw(self):
        """ Render the screen. """
        # Clear the screen
        self.clear()
        #draw cards
        self.card_list.draw()

    def on_mouse_press(self, x, y, button, key_modifiers):
        """ Called when the user presses a mouse button. """
        # Get list of cards we've clicked on
        cards = arcade.get_sprites_at_point((x, y), self.card_list)

        # Have we clicked on a card?
        if len(cards) > 0:
            # Might be a stack of cards, get the top one
            primary_card = cards[-1]
            # All other cases, grab the face-up card we are clicking on
            self.held_cards = [primary_card]
            # Save the position
            self.held_cards_original_position = [self.held_cards[0].position]
            # Put on top in drawing order
            self.pull_to_top(self.held_cards[0])

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """ Called when the user presses a mouse button. """
        # If we don't have any cards, who cares
        if len(self.held_cards) == 0:
            return
        # We are no longer holding cards
        self.held_cards = []

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ User moves mouse """

        # If we are holding cards, move them with the mouse
        for card in self.held_cards:
            card.center_x += dx
            card.center_y += dy


def main():
    """ Main function """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()