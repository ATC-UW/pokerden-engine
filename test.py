import eval7

deck = eval7.Deck()

# Create a board with 5 cards
# board = deck.draw(5)

print(deck)
hand = deck.deal(5)

s = eval7.evaluate(hand)
print(hand[0])

card = eval7.Card("3c")
hand.append(card)
print(hand)

s= eval7.evaluate(hand)

created = eval7.Card("Ts")
deck.cards.remove(created)
print(deck.cards)