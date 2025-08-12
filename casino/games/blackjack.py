import random
import json
import time
import sqlite3
from mcp_server import mcp_server
from common import RichToolDescription
from database import add_balance, deduct_balance, get_balance, get_blackjack_state, save_blackjack_state, delete_blackjack_state

from typing import Annotated
from pydantic import Field

BLACKJACK_DESCRIPTION = RichToolDescription(
    description="Play a game of blackjack against the dealer.",
    use_when="When the user asks to play blackjack or requests to hit/stand",
    side_effects="Deducts bet amount, plays blackjack, awards winnings if the player wins"
)

SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

def create_deck():
    return [(rank, suit) for rank in RANKS for suit in SUITS]

def card_value(card):
    rank, _ = card
    if rank in ["J", "Q", "K"]:
        return 10
    elif rank == "A":
        return 11
    return int(rank)

def hand_value(hand):
    value = sum(card_value(c) for c in hand)
    aces = sum(1 for c in hand if c[0] == "A")
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def format_hand(hand):
    return " ".join([f"{r}{s}" for r, s in hand])


@mcp_server.tool()
def blackjack_start(
    puch_user_id: Annotated[str, Field(description="Puch User Unique Identifier")],
    bet: Annotated[int, Field(description="The amount to bet on this blackjack round")],
) -> str:
    balance = get_balance(puch_user_id)
    if balance is None or balance < bet:
        return f"❌ Not enough balance to start Blackjack. Try claiming the daily amount"

    deduct_balance(puch_user_id, bet)

    deck = create_deck()
    random.shuffle(deck)

    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    save_blackjack_state(puch_user_id, player_hand, dealer_hand, f"active:{bet}")

    return f"Show the entire message below in the exact format to the user as it is and don't say anything else 🃏 Blackjack Started!\nYour hand: {format_hand(player_hand)} (Total: {hand_value(player_hand)})\nDealer shows: {format_hand([dealer_hand[0]])} + ❓\nType 'hit' to draw another card or 'stand' to hold."

@mcp_server.tool()
def blackjack_hit(
    puch_user_id: Annotated[str, Field(description="Puch User Unique Identifier")],
) -> str:
    game = get_blackjack_state(puch_user_id)
    if not game or not game["status"].startswith("active"):
        return "No active Blackjack game. Start one first!"

    bet = int(game["status"].split(":")[1])

    deck = create_deck()
    used_cards = game["player_hand"] + game["dealer_hand"]
    deck = [card for card in deck if card not in used_cards]
    random.shuffle(deck)

    player_hand = game["player_hand"]
    player_hand.append(deck.pop())

    if hand_value(player_hand) > 21:
        delete_blackjack_state(puch_user_id)
        return f"Show the entire message below in the exact format to the user as it is and don't say anything else 💥 You busted! Your hand: {format_hand(player_hand)} (Total: {hand_value(player_hand)})"

    save_blackjack_state(puch_user_id, player_hand, game["dealer_hand"], f"active:{bet}")

    return f"Show the entire message below in the exact format to the user as it is and don't say anything else Your hand: {format_hand(player_hand)} (Total: {hand_value(player_hand)})\nType 'hit' to draw again or 'stand' to hold."

@mcp_server.tool()
def blackjack_stand(
    puch_user_id: Annotated[str, Field(description="Puch User Unique Identifier")],
) -> str:
    game = get_blackjack_state(puch_user_id)
    if not game or not game["status"].startswith("active"):
        return "No active Blackjack game. Start one first!"

    bet = int(game["status"].split(":")[1])
    dealer_hand = game["dealer_hand"]

    deck = create_deck()
    used_cards = game["player_hand"] + dealer_hand
    deck = [card for card in deck if card not in used_cards]
    random.shuffle(deck)

    while hand_value(dealer_hand) < 17:
        dealer_hand.append(deck.pop())

    player_total = hand_value(game["player_hand"])
    dealer_total = hand_value(dealer_hand)

    delete_blackjack_state(puch_user_id)

    if dealer_total > 21 or player_total > dealer_total:
        winnings = bet * 2
        add_balance(puch_user_id, winnings)
        result = f"✅ You win! You earned {winnings} coins."
    elif player_total == dealer_total:
        add_balance(puch_user_id, bet)
        result = "🤝 It's a tie! Your bet is returned."
    else:
        result = "❌ Dealer wins! Better luck next time."

    return f"Show the entire message below in the exact format to the user as it is and don't say anything else Your hand: {format_hand(game['player_hand'])} (Total: {player_total})\nDealer's hand: {format_hand(dealer_hand)} (Total: {dealer_total})\n{result}"