from flask import Flask, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

game_state = {
    "player_cards": [],
    "dealer_cards": [],
    "deck": [],
    "status": "",
    "game_over": False,
    "player_value": 0,
    "dealer_value": 0
}

statistics = {
    "wins": 0,
    "losses": 0,
    "ties": 0
}

def create_deck():
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    return [f"{rank} of {suit}" for suit in suits for rank in ranks]

def shuffle_deck():
    deck = create_deck()
    random.shuffle(deck)
    return deck

def deal_card():
    return game_state["deck"].pop()

def calculate_hand_value(hand):
    values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11}
    total = sum(values[card.split()[0]] for card in hand)
    aces = sum(card.startswith('Ace') for card in hand)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def determine_winner():
    player_value = game_state["player_value"]
    dealer_value = game_state["dealer_value"]
    
    if player_value > 21:
        statistics["losses"] += 1
        return "Player busts. Dealer wins."
    elif dealer_value > 21:
        statistics["wins"] += 1
        return "Dealer busts. Player wins!"
    elif player_value > dealer_value:
        statistics["wins"] += 1
        return "Player wins!"
    elif dealer_value > player_value:
        statistics["losses"] += 1
        return "Dealer wins."
    else:
        statistics["ties"] += 1
        return "It's a tie!"

def reset_game_state():
    game_state["player_cards"] = []
    game_state["dealer_cards"] = []
    game_state["deck"] = shuffle_deck()
    game_state["status"] = ""
    game_state["game_over"] = False
    game_state["player_value"] = 0
    game_state["dealer_value"] = 0

@app.route('/start', methods=['GET'])
def start_game():
    reset_game_state()
    game_state["player_cards"] = [deal_card(), deal_card()]
    game_state["dealer_cards"] = [deal_card()]
    game_state["player_value"] = calculate_hand_value(game_state["player_cards"])
    game_state["dealer_value"] = calculate_hand_value(game_state["dealer_cards"])
    return jsonify(game_state)

@app.route('/hit', methods=['GET'])
def hit():
    if not game_state["game_over"]:
        game_state["player_cards"].append(deal_card())
        game_state["player_value"] = calculate_hand_value(game_state["player_cards"])
        if game_state["player_value"] > 21:
            game_state["status"] = determine_winner()
            game_state["game_over"] = True
    return jsonify(game_state)

@app.route('/stand', methods=['GET'])
def stand():
    if not game_state["game_over"]:
        while game_state["dealer_value"] < 17:
            game_state["dealer_cards"].append(deal_card())
            game_state["dealer_value"] = calculate_hand_value(game_state["dealer_cards"])
        game_state["status"] = determine_winner()
        game_state["game_over"] = True
    return jsonify(game_state)

@app.route('/double-down', methods=['GET'])
def double_down():
    if not game_state["game_over"] and len(game_state["player_cards"]) == 2:
        game_state["player_cards"].append(deal_card())
        game_state["player_value"] = calculate_hand_value(game_state["player_cards"])
        if game_state["player_value"] <= 21:
            while game_state["dealer_value"] < 17:
                game_state["dealer_cards"].append(deal_card())
                game_state["dealer_value"] = calculate_hand_value(game_state["dealer_cards"])
        game_state["status"] = determine_winner()
        game_state["game_over"] = True
    return jsonify(game_state)

@app.route('/get-stats', methods=['GET'])
def get_stats():
    return jsonify(statistics)

if __name__ == '__main__':
    app.run(debug=True)