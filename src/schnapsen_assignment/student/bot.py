
from schnapsen.game import Bot, Move, PlayerPerspective, TrumpExchange, SchnapsenTrickScorer
# other needed imports here. Most likely you need:
from schnapsen.deck import Card, Suit, Rank


class AssignmentBot(Bot):
    """Your suit order is [HEARTS, SPADES, CLUBS, DIAMONDS], from lower suit to higher suit."""
    # Define suit order
    order = [Suit.HEARTS, Suit.SPADES, Suit.CLUBS, Suit.DIAMONDS]

    def get_move(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """Get the move for the Bot.
        The basic structure for your bot is already implemented and must not be modified.
        To implement your bot, only modify the condition and action methods below.
        """
        if self.condition1(perspective, leader_move):
            return self.action1(perspective, leader_move)
        elif self.condition2(perspective, leader_move):
            if self.condition3(perspective, leader_move):
                return self.action2(perspective, leader_move)
            else:
                return self.action3(perspective, leader_move)
        else:
            return self.action4(perspective, leader_move)

    def condition1(self, perspective: PlayerPerspective, leader_move: Move | None) -> bool:
        """1. if the bot can play a trump exchange [1 point]"""
        # Get the valid moves from the current hand
        hand = perspective.valid_moves()
        # Check if there is any trump exchange moves
        if any(move.is_trump_exchange() for move in hand):
            return True
        else:
            return False


    def condition2(self, perspective: PlayerPerspective, leader_move: Move | None) -> bool:
        """2. otherwise, if the bot is follower and the opponent played a DIAMONDS card [1 point]"""
        # Check if the bot is the follower
        if leader_move is not None:
            # Check if the opponent played a diamond
            return leader_move.cards[0].suit == Suit.DIAMONDS
        else:
            return False
        
    def condition3(self, perspective: PlayerPerspective, leader_move: Move | None) -> bool:
        """                  a. if the bot has at least 2 cards and the sum of their points are higher than 15 [1.5 points]"""
        # Get the current hand
        hand = perspective.get_hand().get_cards()
        # Check if the bot has at least 2 cards
        if len(hand) >= 2:
            # Calculate the sum of points in the current hand
            points = sum(SchnapsenTrickScorer.SCORES[card.rank] for card in hand)
            return points > 15
        else: 
            return False

    def action1(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """   then play a trump exchange  [1.5 point]"""
        # Get trump suit
        trump_suit = perspective.get_trump_suit()
        # Perform trump exchange
        return TrumpExchange(Card.get_card(Rank.JACK, trump_suit))

    def action2(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """                     then play the valid regular move where the card has the highest suit according
                          to the suit order above. If multiple cards have the highest suit,
                          prioritize according to highest points. [1.5 points]"""
        # Retrieve valid regular moves
        valid_regular_moves = [move for move in perspective.valid_moves() if move.is_regular_move()]
        # Sort the list first by suit order then by points (low to high)
        valid_regular_moves.sort(key=lambda move: (self.order.index(move.cards[0].suit), SchnapsenTrickScorer.SCORES[move.cards[0].rank]))

        return valid_regular_moves[-1]
        


    def action3(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """                  b. otherwise find the most frequent suit among the cards in valid regular moves.
                               If multiple suits have the same most frequency, prioritize according
                               to the suit order above. Among these cards, play the one with the
                               highest points. [2.0 points]"""
        # Get valid moves
        valid_moves = perspective.valid_moves()
        # Get suit frequencies
        suit_frequencies = {}
        for move in valid_moves:
            if move.is_regular_move():
                suit = move.cards[0].suit
                suit_frequencies[suit] = suit_frequencies.get(suit, 0) + 1
        # Define initial comparison value
        highest_frequency = 0
        for frequency in suit_frequencies.values():
            if frequency > highest_frequency:
                highest_frequency = frequency
        # Gather the most frequent suits
        most_frequent_suits = []
        for suit, frequency in suit_frequencies.items():
            if frequency == highest_frequency:
                most_frequent_suits.append(suit)

        # Return most frequent suit if only one exists
        if len(most_frequent_suits) == 1:
            most_frequent_suit = most_frequent_suits[0]
        # Sort the suits if more than one most frequent suit exists
        else:
            most_frequent_suits.sort(key=lambda suit: self.order.index(suit))
            most_frequent_suit = most_frequent_suits[-1]
        # Get the moves with the most frequent suit
        moves_with_most_fequent_suit = []
        for move in valid_moves:
            if move.is_regular_move():
                if move.cards[0].suit == most_frequent_suit:
                    moves_with_most_fequent_suit.append(move)
        # Sort the moves according to their rank
        moves_with_most_fequent_suit.sort(key=lambda move:SchnapsenTrickScorer.SCORES[move.cards[0].rank])
        return moves_with_most_fequent_suit[-1]



    def action4(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """3. otherwise take the cards in valid regular moves and order them by points (low to high); in this
             ordering, if two cards have the same points, sort these according to the suit order.
             Now, play the card in the middle of the sequence. If the number of cards is even, play
             the card right above the middle. [1.5 points]"""
        # Retrieve valid regular moves
        valid_regular_moves = [move for move in perspective.valid_moves() if move.is_regular_move()]
        # Sort the list first by points then suit order (low to high)
        valid_regular_moves.sort(key=lambda move: (SchnapsenTrickScorer.SCORES[move.cards[0].rank], self.order.index(move.cards[0].suit)))
        # Find the middle card
        middle_card_index = len(valid_regular_moves) // 2
        
        return  valid_regular_moves[middle_card_index]