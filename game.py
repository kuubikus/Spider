"""
Solitaire clone
"""
import arcade
import cards
import settings
import random


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, settings.SCREEN_TITLE)
        
        #  list of cards
        self.card_list = None
        arcade.set_background_color(arcade.color.AMAZON)
        #  cards being dragged
        self.held_cards = None
        #  og location
        self.held_cards_og_pos = None
        #  mats
        self.pile_mat_list = None
        #  a list of lists for each pile
        self.piles = None

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """
        #  cards being dragged
        self.held_cards = []
        self.held_cards_og_pos = []

        # ---  Create the mats the cards go on.

        # Sprite list with all the mats tha cards lay on.
        self.pile_mat_list: arcade.SpriteList = arcade.SpriteList()

        # Create the mats for the bottom face down and face up piles
        pile = arcade.SpriteSolidColor(settings.MAT_WIDTH, settings.MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = settings.START_X, settings.BOTTOM_Y
        self.pile_mat_list.append(pile)

        pile = arcade.SpriteSolidColor(settings.MAT_WIDTH, settings.MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = settings.START_X + settings.X_SPACING, settings.BOTTOM_Y
        self.pile_mat_list.append(pile)

        # Create the seven middle piles
        for i in range(7):
            pile = arcade.SpriteSolidColor(settings.MAT_WIDTH, settings.MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
            pile.position = settings.START_X + i * settings.X_SPACING, settings.MIDDLE_Y
            self.pile_mat_list.append(pile)

        # Create the top "play" piles
        for i in range(4):
            pile = arcade.SpriteSolidColor(settings.MAT_WIDTH, settings.MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
            pile.position = settings.START_X + i * settings.X_SPACING, settings.TOP_Y
            self.pile_mat_list.append(pile)

        # Sprite list with all the cards, no matter what pile they are in.
        self.card_list = arcade.SpriteList()

        # Create every card
        for card_suit in settings.CARD_SUITS:
            for card_value in settings.CARD_VALUES:
                card = cards.Card(card_suit, card_value, settings.CARD_SCALE)
                card.position = settings.START_X, settings.BOTTOM_Y
                self.card_list.append(card)
        
        # Shuffle the cards
        for pos1 in range(len(self.card_list)):
            pos2 = random.randrange(len(self.card_list))
            self.card_list.swap(pos1, pos2)

        self.piles = [[] for x in range(settings.PILE_COUNT)]
        # Put all the cards in the bottom face-down pile
        for card in self.card_list:
            self.piles[settings.BOTTOM_FACE_DOWN_PILE].append(card)

    def pull_to_top(self, card: arcade.Sprite):
        """ Pull card to top of rendering order (last to render, looks on-top) """
        # Remove, and append to the end
        self.card_list.remove(card)
        self.card_list.append(card)

    def on_draw(self):
        """ Render the screen. """
        #  Clear the screen
        self.clear()
        #  draw mats
        self.pile_mat_list.draw()
        #  draw cards
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

    def get_last_cards(self, card_in_hand):
        """ get a SpriteList of all last cards in a pile """
        pile_last_card_list: arcade.SpriteList = arcade.SpriteList()
        for pile in self.piles:
                #  if there is a last card
                if len(pile) > 0:
                    #  not the same as the one in hand
                    if pile[-1] != card_in_hand:
                        pile_last_card_list.append(pile[-1])
        return pile_last_card_list

    def get_closest_sprite(self, card_in_hand):
        pile_from_mat, distance_from_mat = arcade.get_closest_sprite(card_in_hand, self.pile_mat_list)
        print("pile_from_mat  ",pile_from_mat)
        last_cards = self.get_last_cards(card_in_hand)
        print("last cards  ", len(last_cards))
        if last_cards:
            pile_from_card, distance_from_card = arcade.get_closest_sprite(card_in_hand, last_cards)   # returns the nearest card but not the corresponding pile
            print('distance_from_mat: ', distance_from_mat)
            print('distance_from_card: ', distance_from_card)
            if distance_from_mat > distance_from_card:
                print("the pile from card  ", pile_from_card)
                #  get the pile correspdonding to that card
                return pile_from_card, self.get_pile_for_card(pile_from_card)
        return pile_from_mat, self.pile_mat_list.index(pile_from_mat)

        
    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """ Called when the user presses a mouse button. """
        # If we don't have any cards, who cares
        if len(self.held_cards) == 0:
            return
        
        # Find the closest pile, in case we are in contact with more than one
        pile, pile_index = self.get_closest_sprite(self.held_cards[0])
        print("pile: ", pile)
        reset_position = True

        # See if we are in contact with the closest pile or the last card in the pile
        if arcade.check_for_collision(self.held_cards[0], pile):

            #  Is it the same pile we came from?
            if pile_index == self.get_pile_for_card(self.held_cards[0]):
                # If so, who cares. We'll just reset our position.
                pass

            # Is it on a middle play pile?
            elif settings.PLAY_PILE_1 <= pile_index <= settings.PLAY_PILE_7:
                # Are there already cards there?
                if len(self.piles[pile_index]) > 0:
                    # Move cards to proper position
                    top_card = self.piles[pile_index][-1]
                    for i, dropped_card in enumerate(self.held_cards):
                        dropped_card.position = top_card.center_x, \
                                                top_card.center_y - settings.CARD_VERTICAL_OFFSET * (i + 1)
                else:
                    # Are there no cards in the middle play pile?
                    for i, dropped_card in enumerate(self.held_cards):
                        # Move cards to proper position
                        dropped_card.position = pile.center_x, \
                                                pile.center_y - settings.CARD_VERTICAL_OFFSET * i

                for card in self.held_cards:
                    # Cards are in the right position, but we need to move them to the right list
                    self.move_card_to_new_pile(card, pile_index)

                # Success, don't reset position of cards
                reset_position = False

            # Release on top play pile? And only one card held?
            elif settings.TOP_PILE_1 <= pile_index <= settings.TOP_PILE_4 and len(self.held_cards) == 1:
                # Move position of card to pile
                self.held_cards[0].position = pile.position
                # Move card to card list
                for card in self.held_cards:
                    self.move_card_to_new_pile(card, pile_index)

                reset_position = False

        if reset_position:
            # Where-ever we were dropped, it wasn't valid. Reset the each card's position
            # to its original spot.
            for pile_index, card in enumerate(self.held_cards):
                card.position = self.held_cards_original_position[pile_index]

        # We are no longer holding cards
        self.held_cards = []

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ User moves mouse """

        # If we are holding cards, move them with the mouse
        for card in self.held_cards:
            card.center_x += dx
            card.center_y += dy

    def get_pile_for_card(self, card):
        """ What pile is this card in? """
        for index, pile in enumerate(self.piles):
            if card in pile:
                return index
    
    def remove_card_from_pile(self, card):
        """ Remove card from whatever pile it was in. """
        for pile in self.piles:
            if card in pile:
                pile.remove(card)
                break

    def move_card_to_new_pile(self, card, pile_index):
        """ Move the card to a new pile """
        self.remove_card_from_pile(card)
        self.piles[pile_index].append(card)


def main():
    """ Main function """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()