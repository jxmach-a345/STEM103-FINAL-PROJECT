# =========================
# PART 1: GLOBALS & HELPERS
# =========================

import random

# --- Game constants ---
STARTING_MONEY = 200

# Tournament tracking
tournament_number = 0
tournament_records = []  # {number, winner, prize, day}

# Flags
player_robot_upgraded_today = False

# --- Base robot template ---
def make_base_robot(name):
    return {
        "name": name,
        "money": STARTING_MONEY,

        # Ingredients
        "dough": 0,
        "cheese": 0,
        "sauce": 0,
        "toppings": 0,
        "topping_quality": 0,

        # Side items
        "side_items": {
            "garlic_knots": 0,
            "soda": 0,
            "desserts": 0,
            "breadsticks": 0,
            "salad": 0
        },

        # Robot stats
        "speed": 0,
        "efficiency": 0,
        "quality": 0,

        # Performance tracking
        "duel_wins": 0,
        "duel_losses": 0,
        "tournaments_won": 0,
        "tournaments_entered": 0,

        # Losing streak (NEW)
        "losing_streak": 0
    }

# Player placeholder (real name set in intro)
player = make_base_robot("TEMP")

# Competitor names
competitor_names = [
    "MegaMelt-9000",
    "SliceBot-X",
    "CheezoTron",
    "Dough Master 3000",
    "Pepperoni Prime",
    "CrustCrusher-67",
    "OvenLord",
    "CheddarCore-V2",
    "Marinara Monk",
    "ToppingTitan-RX",
    "YeastBeast-404",
    "SauceSerpent",
    "The Rolling Pin",
    "DeepDish Dominator"
]

competitors = [make_base_robot(name) for name in competitor_names]

# Side item topping bonuses
SIDE_ITEM_TOPPING_BONUS = {
    "garlic_knots": 1,
    "soda": 1,
    "desserts": 2,
    "breadsticks": 1,
    "salad": 1
}

# Horse racing system
horses = [
    "Big Apple",
    "Dusty Hooves",
    "Old Reliable",
    "Midnight Shadow",
    "Unicronus",
    "Lucky Clover",
    "Mudrunner",
    "Infernal Mud"
]

horse_odds = {
    "Big Apple": 0.25,
    "Dusty Hooves": 0.20,
    "Old Reliable": 0.15,
    "Midnight Shadow": 0.12,
    "Unicronus": 0.10,
    "Lucky Clover": 0.08,
    "Mudrunner": 0.06,
    "Infernal Mud": 0.04
}

horse_payouts = {
    "Big Apple": 2,
    "Dusty Hooves": 3,
    "Old Reliable": 4,
    "Midnight Shadow": 5,
    "Unicronus": 6,
    "Lucky Clover": 8,
    "Mudrunner": 10,
    "Infernal Mud": 15
}

# Slots symbols
SLOT_SYMBOLS = ["Cherry", "Lemon", "Bell", "Star", "Seven"]

def spin_slots():
    return [random.choice(SLOT_SYMBOLS) for _ in range(3)]

def evaluate_slots(reels, bet):
    a, b, c = reels
    if a == b == c == "Seven":
        return bet * 50
    if a == b == c:
        return bet * 10
    if a == b or a == c or b == c:
        return bet * 3
    return -bet

# ---------- SCORING SYSTEM ----------

def side_item_topping_bonus(entity):
    total = 0
    for item, count in entity["side_items"].items():
        total += SIDE_ITEM_TOPPING_BONUS.get(item, 0) * count
    return total

def ingredient_score(entity):
    return (
        entity["dough"] * 2 +
        entity["cheese"] * 1 +
        entity["sauce"] * 1 +
        entity["toppings"] * 3
    )

def total_topping_bonus(entity):
    return entity["topping_quality"] + side_item_topping_bonus(entity)

def pizza_score(entity):
    return ingredient_score(entity) + total_topping_bonus(entity)

def duel_score(entity):
    return pizza_score(entity) + entity["quality"] * 3

# ----------> LOSING STREAK PENALTY (DOUBLING) don't lose I guess :( <----------

def losing_penalty(entity):
    # 15 * (2^losing_streak)
    return 15 * (2 ** entity["losing_streak"])

# ---------- DUEL RESOLUTION ----------

def sudden_death_duel_entities(a, b):
    while True:
        a_score = duel_score(a)
        b_score = duel_score(b)

        if a_score > b_score:
            a["duel_wins"] += 1
            b["duel_losses"] += 1

            # Reset winner streak, increase loser streak
            a["losing_streak"] = 0
            b["losing_streak"] += 1

            # Apply doubling penalty
            penalty = losing_penalty(b)
            b["money"] = max(0, b["money"] - penalty)

            return a

        elif b_score > a_score:
            b["duel_wins"] += 1
            a["duel_losses"] += 1

            b["losing_streak"] = 0
            a["losing_streak"] += 1

            penalty = losing_penalty(a)
            a["money"] = max(0, a["money"] - penalty)

            return b

        # Tie → repeat

# ----------> SURVIVAL SYSTEM <----------

def duel_win_rate(entity):
    total = entity["duel_wins"] + entity["duel_losses"]
    if total == 0:
        return 0.0
    return entity["duel_wins"] / total

def tournament_performance_score(entity):
    if entity["tournaments_entered"] == 0:
        return 0.0
    return entity["tournaments_won"] / entity["tournaments_entered"]

def ingredient_power(entity):
    return ingredient_score(entity) + total_topping_bonus(entity)

def survival_score(entity):
    return (
        entity["speed"] * 1.5 +
        entity["efficiency"] * 1.2 +
        entity["quality"] * 2.0 +
        duel_win_rate(entity) * 10 +
        tournament_performance_score(entity) * 5 +
        entity["money"] / 50 +
        ingredient_power(entity) / 20 -
        (entity["losing_streak"] * 5)
    )

def compute_survival_percentages(include_player=True):
    all_entities = competitors[:]
    if include_player:
        all_entities = [player] + all_entities

    scores = [max(0.1, survival_score(e)) for e in all_entities]
    total = sum(scores)

    return {e["name"]: (s / total) * 100 for e, s in zip(all_entities, scores)}


# <==========================>
# PART 2 — GAMEPLAY SYSTEMS
# <==========================>

# ----------> GROCERY STORE SYSTEM <----------

def grocery_store(entity):
    print("\n=== GROCERY STORE ===")
    print("1. Buy Dough ($5)")
    print("2. Buy Cheese ($3)")
    print("3. Buy Sauce ($2)")
    print("4. Buy Toppings ($4)")
    print("5. Upgrade Topping Quality ($10)")
    print("6. Buy Side Items")
    print("7. Leave Store")

    while True:
        choice = input("Choose an option: ")

        if choice == "1":
            if entity["money"] >= 5:
                entity["dough"] += 1
                entity["money"] -= 5
                print("Bought 1 Dough.")
            else:
                print("Not enough money.")

        elif choice == "2":
            if entity["money"] >= 3:
                entity["cheese"] += 1
                entity["money"] -= 3
                print("Bought 1 Cheese.")
            else:
                print("Not enough money.")

        elif choice == "3":
            if entity["money"] >= 2:
                entity["sauce"] += 1
                entity["money"] -= 2
                print("Bought 1 Sauce.")
            else:
                print("Not enough money.")

        elif choice == "4":
            if entity["money"] >= 4:
                entity["toppings"] += 1
                entity["money"] -= 4
                print("Bought 1 Topping.")
            else:
                print("Not enough money.")

        elif choice == "5":
            if entity["money"] >= 10:
                entity["topping_quality"] += 1
                entity["money"] -= 10
                print("Topping Quality increased!")
            else:
                print("Not enough money.")

        elif choice == "6":
            buy_side_items(entity)

        elif choice == "7":
            print("Leaving store...")
            break

        else:
            print("Invalid choice.")


def buy_side_items(entity):
    print("\n--- SIDE ITEMS ---")
    print("1. Garlic Knots ($3)")
    print("2. Soda ($2)")
    print("3. Desserts ($5)")
    print("4. Breadsticks ($3)")
    print("5. Salad ($4)")
    print("6. Back")

    prices = {
        "1": ("garlic_knots", 3),
        "2": ("soda", 2),
        "3": ("desserts", 5),
        "4": ("breadsticks", 3),
        "5": ("salad", 4)
    }

    while True:
        choice = input("Choose an item: ")

        if choice in prices:
            item, cost = prices[choice]
            if entity["money"] >= cost:
                entity["side_items"][item] += 1
                entity["money"] -= cost
                print(f"Bought 1 {item.replace('_', ' ').title()}.")
            else:
                print("Not enough money.")

        elif choice == "6":
            break

        else:
            print("Invalid choice.")


# ----------> CASINO SYSTEM 

def casino(entity):
    print("\n=== CASINO ===")
    print("1. Horse Racing")
    print("2. Slot Machine")
    print("3. Leave Casino")

    while True:
        choice = input("Choose an option: ")

        if choice == "1":
            horse_racing(entity)
        elif choice == "2":
            slot_machine(entity)
        elif choice == "3":
            print("Leaving casino...")
            break
        else:
            print("Invalid choice.")


def horse_racing(entity):
    print("\n--- HORSE RACING ---")
    print("Available Horses:")
    for h in horses:
        print(f"- {h} (Odds: {horse_odds[h]})")

    bet = int(input("Enter bet amount: "))
    if bet > entity["money"]:
        print("Not enough money.")
        return

    horse_choice = input("Choose a horse: ")
    if horse_choice not in horses:
        print("Invalid horse.")
        return

    print("The race is starting...")
    winner = random.choices(horses, weights=[horse_odds[h] for h in horses])[0]
    print(f"The winner is: {winner}")

    if horse_choice == winner:
        winnings = bet * horse_payouts[winner]
        entity["money"] += winnings
        print(f"You won ${winnings}!")
    else:
        entity["money"] -= bet
        print("You lost the bet.")


def slot_machine(entity):
    print("\n--- SLOT MACHINE ---")
    bet = int(input("Enter bet amount: "))
    if bet > entity["money"]:
        print("Not enough money.")
        return

    reels = spin_slots()
    print(" | ".join(reels))

    result = evaluate_slots(reels, bet)
    entity["money"] += result

    if result > 0:
        print(f"You won ${result}!")
    else:
        print("You lost the bet.")


# ----------> COMPETITOR DAILY ACTIONS 

def competitor_daily_actions():
    for c in competitors:
        action = random.choice(["buy", "upgrade", "nothing"])

        if action == "buy":
            c["toppings"] += 1
        elif action == "upgrade":
            c["quality"] += 1


# ====================================
# PART 3 — TOURNAMENTS & WIKI SYSTEMS
# ====================================

import random

# ---------- TOURNAMENT SYSTEM ----------

def run_tournament(player, day):
    global tournament_number
    tournament_number += 1

    print(f"\n=== TOURNAMENT #{tournament_number} ===")

    entry_fee = 25
    if player["money"] < entry_fee:
        print("You cannot afford the entry fee.")
        return

    player["money"] -= entry_fee
    player["tournaments_entered"] += 1

    opponents = random.sample(competitors, 3)

    print("Your opponents:")
    for o in opponents:
        print(f"- {o['name']}")

    wins = 0
    for o in opponents:
        winner = sudden_death_duel_entities(player, o)
        if winner == player:
            wins += 1
            print(f"You defeated {o['name']}!")
        else:
            print(f"You lost to {o['name']}.")

    if wins >= 2:
        prize = 100 + (wins * 20)
        player["money"] += prize
        player["tournaments_won"] += 1
        print(f"\nYou WON the tournament! Prize: ${prize}")
        record_tournament_result(tournament_number, player["name"], prize, day)
    else:
        print("\nYou did not win the tournament.")
        record_tournament_result(tournament_number, "No Winner", 0, day)


def record_tournament_result(number, winner, prize, day):
    tournament_records.append({
        "number": number,
        "winner": winner,
        "prize": prize,
        "day": day
    })


def show_tournament_history():
    print("\n=== TOURNAMENT HISTORY ===")
    if not tournament_records:
        print("No tournaments have been held yet.")
        return

    for r in tournament_records:
        print(f"#{r['number']} | Winner: {r['winner']} | Prize: ${r['prize']} | Day {r['day']}")


# ---------- WIKI SYSTEM ----------

def wiki_menu():
    print("\n=== ROBOT WIKI ===")
    print("1. View Player Stats")
    print("2. View Competitor Stats")
    print("3. View Survival Percentages")
    print("4. View Tournament History")
    print("5. Back")

    while True:
        choice = input("Choose an option: ")

        if choice == "1":
            show_robot_stats(player)
        elif choice == "2":
            show_all_competitors()
        elif choice == "3":
            show_survival_percentages()
        elif choice == "4":
            show_tournament_history()
        elif choice == "5":
            break
        else:
            print("Invalid choice.")


def show_robot_stats(entity):
    print(f"\n=== {entity['name']} STATS ===")
    print(f"Money: ${entity['money']}")
    print(f"Duel Wins: {entity['duel_wins']}")
    print(f"Duel Losses: {entity['duel_losses']}")
    print(f"Tournaments Won: {entity['tournaments_won']}")
    print(f"Tournaments Entered: {entity['tournaments_entered']}")
    print(f"Losing Streak: {entity['losing_streak']}")
    print(f"Ingredients: Dough {entity['dough']}, Cheese {entity['cheese']}, Sauce {entity['sauce']}, Toppings {entity['toppings']}")
    print(f"Topping Quality: {entity['topping_quality']}")
    print(f"Side Items: {entity['side_items']}")
    print(f"Speed: {entity['speed']} | Efficiency: {entity['efficiency']} | Quality: {entity['quality']}")


def show_all_competitors():
    print("\n=== COMPETITOR STATS ===")
    for c in competitors:
        print(f"- {c['name']}: Wins {c['duel_wins']}, Losses {c['duel_losses']}, Money ${c['money']}")


def show_survival_percentages():
    print("\n=== SURVIVAL PERCENTAGES ===")
    percentages = compute_survival_percentages(include_player=True)
    for name, pct in percentages.items():
        print(f"{name}: {pct:.2f}%")
# ================================
# PART 4 — MENUS & GAMEPLAY LOOP
# ================================

def intro_sequence():
    print("Welcome to the Robot Pizza Competition.")
    name = input("Name your robot: ")
    return name


def show_daily_header(day, entity):
    print("\n==============================")
    print(f"DAY {day} REPORT")
    print("==============================")
    print(f"Money: ${entity['money']}")
    print(f"Duel Wins: {entity['duel_wins']}")
    print(f"Duel Losses: {entity['duel_losses']}")
    print(f"Losing Streak: {entity['losing_streak']}")
    print("==============================")


def player_action_menu():
    print("\n=== DAILY ACTIONS ===")
    print("1. Grocery Store")
    print("2. Casino")
    print("3. Duel a Competitor")
    print("4. Enter Tournament")
    print("5. Robot Wiki")
    print("6. End Day")

    choice = input("Choose an action: ")
    return choice


def choose_competitor():
    print("\nChoose a competitor to duel:")
    for i, c in enumerate(competitors):
        print(f"{i+1}. {c['name']} (Wins: {c['duel_wins']}, Losses: {c['duel_losses']})")

    while True:
        try:
            idx = int(input("Enter number: ")) - 1
            if 0 <= idx < len(competitors):
                return competitors[idx]
        except ValueError:
            pass
        print("Invalid choice.")


def main(player):
    day = 1
    global player_robot_upgraded_today

    while True:
        player_robot_upgraded_today = False

        show_daily_header(day, player)

        competitor_daily_actions()

        while True:
            action = player_action_menu()

            if action == "1":
                grocery_store(player)

            elif action == "2":
                casino(player)

            elif action == "3":
                opponent = choose_competitor()
                winner = sudden_death_duel_entities(player, opponent)
                if winner == player:
                    print(f"You defeated {opponent['name']} in a duel.")
                else:
                    print(f"You lost to {opponent['name']}.")

            elif action == "4":
                run_tournament(player, day)

            elif action == "5":
                wiki_menu()

            elif action == "6":
                print("Ending day...")
                break

            else:
                print("Invalid choice.")

        day += 1

# WRAPPER FUNCTIONS FOR main.py

def initialize_player(name):
    """Creates the player's robot using the base robot builder."""
    return make_base_robot(name)

def run_game_loop(player):
    """Starts the main game loop."""
    main(player)
