import random
def rock_paper_scissors():
    game_result, choices = {"win": [("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")], "lose": [("rock", "paper"), ("paper", "scissors"), ("scissors", "rock")], "tied": [("rock", "rock"), ("paper", "paper"), ("scissors", "scissors")]}, {"0": "rock", "1": "paper", "2": "scissors"}; human_choice, cp_choice = choices[input("enter choice (0) Rock, (1) Paper, (2) Scissors: ")], random.choice(list(choices.values())); return "".join(key for key, values in game_result.items() if (human_choice, cp_choice) in values), human_choice, cp_choice
def rounds(total_round=3):
    score_table, score_results = {"win": 1, "lose": -1, "tied": 0}, list()
    for _ in range(0, total_round): result, human_choice, cp_choice = rock_paper_scissors(); print(f"you {result}. you chose {human_choice} & computer chose {cp_choice}.\n"); score_results.append(score_table[result])
    if sum(score_results) > 0: print(f"you win. you won {sum(score_results)} times!")
    elif sum(score_results) < 0: print(f"you lost. you lost {sum(score_results)} times.")
    else: print("it's a tie!")
rounds()
