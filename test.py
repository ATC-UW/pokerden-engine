import eval7

deck = eval7.Deck()

# Create a board with 5 cards
# board = deck.draw(5)

# print(deck)
# hand = deck.deal(5)

# s = eval7.evaluate(hand)
# print(hand[0])

# card = eval7.Card("3c")
# hand.append(card)
# print(hand)

# s= eval7.evaluate(hand)

# created = eval7.Card("Ts")
# deck.cards.remove(created)
# print(deck.cards)

ITERATION = 1000000
equal_count = 0
for i in range(ITERATION):
    print(str(i) + "th iteration")
    deck = eval7.Deck()
    # Draw two hands of 5 cards each
    hand1 = deck.deal(5)
    hand2 = deck.deal(5)

    # Evaluate both hands
    score1 = eval7.evaluate(hand1)
    score2 = eval7.evaluate(hand2)

    # Print the hands and their scores
    # print("Hand 1:", hand1, "Score:", score1)
    # print("Hand 2:", hand2, "Score:", score2)

    # Check if the hands are the same
    if hand1 == hand2:
        print("The hands are the same.")
        equal_count += 1

print("Done")
print(equal_count)
print(equal_count / ITERATION)