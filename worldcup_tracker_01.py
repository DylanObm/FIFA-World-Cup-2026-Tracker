# Worked with Claude
# Project: FIFA World Cup 2026 Group Stage Tracker
# Description: A program to track the 2026 FIFA World Cup group stage and knockout stage
# Author: Dylan Obermayer
# How to run: python3 worldcup_tracker.py
# Requires: Python 3.9 or higher (check with: python3 --version)

# ==========================================
# 2026 FIFA WORLD CUP FORMAT RULES
# ==========================================
#
# GROUP STAGE:
# - 48 teams split into 12 groups of 4 teams each (Groups A to L)
# - Each team plays the other 3 teams in their group once (6 matches per group)
# - Win = 3 points, Draw = 1 point each, Loss = 0 points
# - Teams are ranked by points, then goal difference, then goals scored
#
# WHO QUALIFIES FOR THE KNOCKOUT STAGE:
# - The top 2 teams from each group qualify automatically (24 teams total)
# - The 8 best third-place teams from all 12 groups also qualify (8 teams total)
# - This gives 32 teams total advancing to the Round of 32
# - The bottom 4th place team in each group is eliminated
#
# HOW THE 8 BEST THIRD-PLACE TEAMS ARE SELECTED:
# - All 12 third-place teams are ranked together
# - Ranking is by: points, then goal difference, then goals scored
# - The top 8 of the 12 third-place teams advance
# - The bottom 4 third-place teams are eliminated
#
# KNOCKOUT STAGE:
# - Round of 32 (32 teams) -> Round of 16 (16 teams) -> Quarterfinals (8 teams)
#   -> Semifinals (4 teams) -> Final (2 teams) -> World Cup Winner!
# - In knockout matches there are no draws
# - If tied after 90 minutes: extra time is played
# - If still tied: penalty shootout decides the winner
# - NOTE: In this program the user simply picks the winner of each match
#   (simulating extra time and penalties if needed)
#
# ==========================================

import json
import os
import random

# ==========================================
# GROUP DATA - all 12 real 2026 World Cup groups with their teams
# ==========================================

groups = {
    "A": ["Mexico", "South Africa", "Korea Republic", "Czechia"],
    "B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["USA", "Paraguay", "Australia", "Turkiye"],
    "E": ["Germany", "Curacao", "Cote d'Ivoire", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "IR Iran", "New Zealand"],
    "H": ["Spain", "Cabo Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "Congo DR", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"]
}

# ==========================================
# PRE-PAIRED MATCHES - all 6 fixed matchups for each group
# matchday 1: team1 vs team2, team3 vs team4
# matchday 2: team1 vs team3, team2 vs team4
# matchday 3: team1 vs team4, team2 vs team3
# ==========================================

def get_group_matches(group):
    # get the 4 teams in the group
    teams = groups[group]
    t1 = teams[0]
    t2 = teams[1]
    t3 = teams[2]
    t4 = teams[3]

    # return all 6 fixed matchups as a list of pairs
    matches = [
        [t1, t2],
        [t3, t4],
        [t1, t3],
        [t2, t4],
        [t1, t4],
        [t2, t3]
    ]
    return matches

# ==========================================
# MATCH HISTORY - stores all group stage match results
# ==========================================

match_history = []

# ==========================================
# KNOCKOUT BRACKET - stores the knockout stage matches and results
# ==========================================

knockout_bracket = {
    "round_of_32": [],
    "round_of_16": [],
    "quarterfinals": [],
    "semifinals": [],
    "final": [],
    "winner": ""
}

# ==========================================
# STANDINGS - stores points, wins, draws, losses and goals for each team
# ==========================================

def create_standings():
    # create an empty standings table for all teams in all groups
    standings = {}
    for group in groups:
        standings[group] = {}
        for team in groups[group]:
            # each team starts with 0 points, wins, draws, losses and goals
            standings[group][team] = {
                "played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_for": 0,
                "goals_against": 0,
                "points": 0
            }
    return standings

# create the standings table when the program starts
standings = create_standings()

# ==========================================
# HELPER FUNCTION: CHECK IF ALL GROUP STAGE IS COMPLETE
# returns True only when all 12 groups have played all 6 matches
# ==========================================

def all_groups_complete():
    # check every group to see if all teams have played 3 games
    for group in groups:
        for team in groups[group]:
            if standings[group][team]["played"] < 3:
                return False
    return True

# ==========================================
# HELPER FUNCTION: SORT STANDINGS
# sorts teams by points then goal difference then goals scored
# ==========================================

def sort_standings(group):
    # get all teams and their stats as a list
    team_list = []
    for team in standings[group]:
        team_list.append([team, standings[group][team]])

    # simple bubble sort by points, then goal difference, then goals scored
    for i in range(len(team_list)):
        for j in range(i + 1, len(team_list)):
            # calculate goal difference for both teams
            gd_i = team_list[i][1]["goals_for"] - team_list[i][1]["goals_against"]
            gd_j = team_list[j][1]["goals_for"] - team_list[j][1]["goals_against"]

            # first compare points
            if team_list[j][1]["points"] > team_list[i][1]["points"]:
                team_list[i], team_list[j] = team_list[j], team_list[i]
            # if points equal compare goal difference
            elif team_list[j][1]["points"] == team_list[i][1]["points"] and gd_j > gd_i:
                team_list[i], team_list[j] = team_list[j], team_list[i]
            # if goal difference equal compare goals scored
            elif (team_list[j][1]["points"] == team_list[i][1]["points"] and
                  gd_j == gd_i and
                  team_list[j][1]["goals_for"] > team_list[i][1]["goals_for"]):
                team_list[i], team_list[j] = team_list[j], team_list[i]

    return team_list

# ==========================================
# HELPER FUNCTION: GET QUALIFIED TEAMS
# returns the 32 teams that qualify for the knockout stage
# - 12 group winners (position 1 in each group)
# - 12 group runners-up (position 2 in each group)
# - 8 best third-place teams (ranked across all groups)
# ==========================================

def get_qualified_teams():
    # lists to store group winners, runners-up and third place teams
    winners = []
    runners_up = []
    third_place_teams = []

    # go through each group and get the top 3 teams
    for group in groups:
        sorted_teams = sort_standings(group)
        winners.append([group, sorted_teams[0][0], sorted_teams[0][1]])
        runners_up.append([group, sorted_teams[1][0], sorted_teams[1][1]])
        third_place_teams.append([group, sorted_teams[2][0], sorted_teams[2][1]])

    # sort the third place teams by points, then goal difference, then goals scored
    for i in range(len(third_place_teams)):
        for j in range(i + 1, len(third_place_teams)):
            gd_i = third_place_teams[i][2]["goals_for"] - third_place_teams[i][2]["goals_against"]
            gd_j = third_place_teams[j][2]["goals_for"] - third_place_teams[j][2]["goals_against"]

            if third_place_teams[j][2]["points"] > third_place_teams[i][2]["points"]:
                third_place_teams[i], third_place_teams[j] = third_place_teams[j], third_place_teams[i]
            elif third_place_teams[j][2]["points"] == third_place_teams[i][2]["points"] and gd_j > gd_i:
                third_place_teams[i], third_place_teams[j] = third_place_teams[j], third_place_teams[i]
            elif (third_place_teams[j][2]["points"] == third_place_teams[i][2]["points"] and
                  gd_j == gd_i and
                  third_place_teams[j][2]["goals_for"] > third_place_teams[i][2]["goals_for"]):
                third_place_teams[i], third_place_teams[j] = third_place_teams[j], third_place_teams[i]

    # take only the top 8 third-place teams
    best_third = third_place_teams[:8]
    eliminated_third = third_place_teams[8:]

    return winners, runners_up, best_third, eliminated_third

# ==========================================
# HELPER FUNCTION: UPDATE STANDINGS
# calculates and updates points after a match result is entered
# ==========================================

def update_standings(group, home_team, away_team, home_goals, away_goals):
    # update goals for and goals against for both teams
    standings[group][home_team]["goals_for"] = standings[group][home_team]["goals_for"] + home_goals
    standings[group][home_team]["goals_against"] = standings[group][home_team]["goals_against"] + away_goals
    standings[group][away_team]["goals_for"] = standings[group][away_team]["goals_for"] + away_goals
    standings[group][away_team]["goals_against"] = standings[group][away_team]["goals_against"] + home_goals

    # update games played for both teams
    standings[group][home_team]["played"] = standings[group][home_team]["played"] + 1
    standings[group][away_team]["played"] = standings[group][away_team]["played"] + 1

    # check if home team won
    if home_goals > away_goals:
        standings[group][home_team]["wins"] = standings[group][home_team]["wins"] + 1
        standings[group][home_team]["points"] = standings[group][home_team]["points"] + 3
        standings[group][away_team]["losses"] = standings[group][away_team]["losses"] + 1

    # check if away team won
    elif away_goals > home_goals:
        standings[group][away_team]["wins"] = standings[group][away_team]["wins"] + 1
        standings[group][away_team]["points"] = standings[group][away_team]["points"] + 3
        standings[group][home_team]["losses"] = standings[group][home_team]["losses"] + 1

    # otherwise it is a draw
    else:
        standings[group][home_team]["draws"] = standings[group][home_team]["draws"] + 1
        standings[group][away_team]["draws"] = standings[group][away_team]["draws"] + 1
        standings[group][home_team]["points"] = standings[group][home_team]["points"] + 1
        standings[group][away_team]["points"] = standings[group][away_team]["points"] + 1

# ==========================================
# FEATURE 1: VIEW ALL GROUPS
# displays all 12 groups and their teams
# ==========================================

def view_groups():
    print("\n========================================")
    print("       FIFA WORLD CUP 2026 - GROUPS     ")
    print("========================================")

    # loop through each group and display the teams
    for group in groups:
        print("\n--- Group " + group + " ---")
        for team in groups[group]:
            print("  " + team)

    print("\n========================================")

# ==========================================
# FEATURE 2: ENTER MATCH RESULT
# shows the pre-paired matches for a group
# user only needs to enter the score
# stays in the function until all matches done or user goes back
# ==========================================

def enter_result():
    print("\n========================================")
    print("         ENTER MATCH RESULT             ")
    print("========================================")

    try:
        # show all groups as a numbered list
        print("\nSelect a group:")
        group_list = []
        number = 1
        for g in groups:
            print(str(number) + ". Group " + g)
            group_list.append(g)
            number = number + 1

        group_num = int(input("\nEnter group number: "))

        # check that the group number is valid
        if group_num < 1 or group_num > len(group_list):
            print("Error - please enter a number between 1 and " + str(len(group_list)))
            return

        # get the selected group letter
        group = group_list[group_num - 1]

        # keep entering results until all matches are done or user goes back
        while True:
            # get all 6 pre-paired matches for this group
            all_matches = get_group_matches(group)

            # show only the matches that have not been played yet
            remaining_matches = []
            for match in all_matches:
                home_team = match[0]
                away_team = match[1]
                already_played = False

                # check if this match has already been entered
                for played in match_history:
                    if played["group"] == group:
                        if played["home_team"] == home_team and played["away_team"] == away_team:
                            already_played = True
                        if played["home_team"] == away_team and played["away_team"] == home_team:
                            already_played = True

                if already_played == False:
                    remaining_matches.append(match)

            # check if all matches have already been played
            if len(remaining_matches) == 0:
                print("\nAll matches in Group " + group + " have been entered!")
                print("Use option 4 to view the final standings.")
                break

            # display the remaining matches for the user to choose from
            print("\nRemaining matches in Group " + group + ":")
            number = 1
            for match in remaining_matches:
                print(str(number) + ". " + match[0] + " vs " + match[1])
                number = number + 1
            print(str(number) + ". Go back to main menu")

            # ask the user to pick a match or go back
            match_num = int(input("\nEnter match number: "))

            # check if user wants to go back
            if match_num == len(remaining_matches) + 1:
                print("Going back to main menu...")
                break

            # check that the match number is valid
            if match_num < 1 or match_num > len(remaining_matches):
                print("Error - please enter a valid match number")
                continue

            # get the selected match
            selected_match = remaining_matches[match_num - 1]
            home_team = selected_match[0]
            away_team = selected_match[1]

            # ask the user to enter the score
            try:
                home_goals = int(input("Enter goals for " + home_team + ": "))
                away_goals = int(input("Enter goals for " + away_team + ": "))
            except ValueError:
                print("Error - please enter valid numbers for goals")
                continue

            # check that the goals are not negative
            if home_goals < 0 or away_goals < 0:
                print("Error - goals cannot be negative")
                continue

            # check that the goals are not unrealistically large
            if home_goals > 99 or away_goals > 99:
                print("Error - goals cannot be more than 99")
                continue

            # update the standings based on the result
            update_standings(group, home_team, away_team, home_goals, away_goals)

            # save the match to the history
            match_history.append({
                "group": group,
                "home_team": home_team,
                "away_team": away_team,
                "home_goals": home_goals,
                "away_goals": away_goals
            })

            print("\nResult saved: " + home_team + " " + str(home_goals) + " - " + str(away_goals) + " " + away_team)

    except ValueError:
        print("Error - please enter valid numbers only")

# ==========================================
# FEATURE 3: SIMULATE GROUP RESULTS
# randomly generates scores for all remaining matches in a group
# ==========================================

def simulate_one_group(group):
    # helper function to simulate all remaining matches in a single group
    all_matches = get_group_matches(group)

    # find the matches that have not been played yet
    remaining_matches = []
    for match in all_matches:
        home_team = match[0]
        away_team = match[1]
        already_played = False

        for played in match_history:
            if played["group"] == group:
                if played["home_team"] == home_team and played["away_team"] == away_team:
                    already_played = True
                if played["home_team"] == away_team and played["away_team"] == home_team:
                    already_played = True

        if already_played == False:
            remaining_matches.append(match)

    # if no matches left skip this group
    if len(remaining_matches) == 0:
        return 0

    # simulate each remaining match with random scores
    for match in remaining_matches:
        home_team = match[0]
        away_team = match[1]

        # generate random goals - weighted towards low scores like real football
        home_goals = random.choice([0, 0, 1, 1, 1, 2, 2, 3, 4])
        away_goals = random.choice([0, 0, 1, 1, 1, 2, 2, 3, 4])

        # update the standings with the simulated result
        update_standings(group, home_team, away_team, home_goals, away_goals)

        # save the match to the history
        match_history.append({
            "group": group,
            "home_team": home_team,
            "away_team": away_team,
            "home_goals": home_goals,
            "away_goals": away_goals
        })

        print(home_team + " " + str(home_goals) + " - " + str(away_goals) + " " + away_team)

    return len(remaining_matches)


def simulate_group():
    print("\n========================================")
    print("       SIMULATE GROUP RESULTS           ")
    print("========================================")

    try:
        # ask if user wants to simulate one group or all groups
        print("\nWhat would you like to simulate?")
        print("1. Simulate one group")
        print("2. Simulate ALL remaining groups at once")

        sim_choice = int(input("\nEnter choice: "))

        # simulate all groups at once
        if sim_choice == 2:
            print("\nSimulating all remaining group stage matches...\n")
            total_simulated = 0
            for group in groups:
                count = simulate_one_group(group)
                if count > 0:
                    print("--- Group " + group + " done (" + str(count) + " matches) ---")
                    total_simulated = total_simulated + count

            if total_simulated == 0:
                print("All group stage matches have already been entered!")
            else:
                print("\n" + str(total_simulated) + " matches simulated across all groups!")
                print("Use option 4 to view standings or option 8 to see qualified teams.")
            return

        # simulate one specific group
        elif sim_choice == 1:
            # show all groups as a numbered list
            print("\nSelect a group:")
            group_list = []
            number = 1
            for g in groups:
                print(str(number) + ". Group " + g)
                group_list.append(g)
                number = number + 1

            group_num = int(input("\nEnter group number: "))

            # check that the group number is valid
            if group_num < 1 or group_num > len(group_list):
                print("Error - please enter a number between 1 and " + str(len(group_list)))
                return

            # get the selected group letter
            group = group_list[group_num - 1]

            print("\nSimulating remaining matches for Group " + group + "...\n")
            count = simulate_one_group(group)

            if count == 0:
                print("All matches in Group " + group + " have already been entered!")
            else:
                print("\nAll remaining matches in Group " + group + " have been simulated!")
                print("Use option 4 to view the final standings.")

        else:
            print("Error - please enter 1 or 2")

    except ValueError:
        print("Error - invalid input")

# ==========================================
# FEATURE 4: VIEW GROUP STANDINGS
# displays the standings table for a selected group
# ==========================================

def view_standings():
    print("\n========================================")
    print("         VIEW GROUP STANDINGS           ")
    print("========================================")

    try:
        # show all groups as a numbered list
        print("\nSelect a group:")
        group_list = []
        number = 1
        for g in groups:
            print(str(number) + ". Group " + g)
            group_list.append(g)
            number = number + 1

        group_num = int(input("\nEnter group number: "))

        # check that the group number is valid
        if group_num < 1 or group_num > len(group_list):
            print("Error - please enter a number between 1 and " + str(len(group_list)))
            return

        # get the selected group letter
        group = group_list[group_num - 1]

        print("\n========================================")
        print("         GROUP " + group + " STANDINGS              ")
        print("========================================")

        # check if all 4 teams have played all 3 group stage games
        all_games_played = True
        for team in groups[group]:
            if standings[group][team]["played"] < 3:
                all_games_played = False

        # get sorted list of teams
        sorted_teams = sort_standings(group)

        # print the table header
        print("\nPos  Team                   P   W   D   L   GF  GA  GD   Pts")
        print("-" * 60)

        # print each team with position number
        position = 1
        for team_data in sorted_teams:
            team = team_data[0]
            stats = team_data[1]

            # calculate goal difference
            goal_diff = stats["goals_for"] - stats["goals_against"]

            # add + sign for positive goal difference
            if goal_diff > 0:
                goal_diff_str = "+" + str(goal_diff)
            else:
                goal_diff_str = str(goal_diff)

            # only show qualified if all group games have been played
            if all_games_played and position <= 2:
                qualified_str = " >> QUALIFIED (automatic)"
            else:
                qualified_str = ""

            # print the team row
            print(str(position) + ".   " +
                team.ljust(22) +
                str(stats["played"]).rjust(3) +
                str(stats["wins"]).rjust(4) +
                str(stats["draws"]).rjust(4) +
                str(stats["losses"]).rjust(4) +
                str(stats["goals_for"]).rjust(5) +
                str(stats["goals_against"]).rjust(4) +
                goal_diff_str.rjust(4) +
                str(stats["points"]).rjust(5) +
                qualified_str)

            position = position + 1

        # show message if not all games have been played yet
        if not all_games_played:
            # count matches played so far in this group
            matches_played = 0
            for team in groups[group]:
                matches_played = matches_played + standings[group][team]["played"]
            matches_played = matches_played // 2
            print("\n(" + str(matches_played) + " of 6 matches played - qualification markers will show once all 6 are done)")
        else:
            print("\nNote: 3rd place team may still qualify as one of the 8 best third-place teams.")
            print("Use option 7 to see all qualified teams after all groups are complete.")

        print("\nP=Played W=Won D=Draw L=Lost GF=Goals For GA=Goals Against GD=Goal Difference Pts=Points")

    except ValueError:
        print("Error - invalid input")

# ==========================================
# FEATURE 5: VIEW MATCH HISTORY
# displays all match results that have been entered
# ==========================================

def view_match_history():
    print("\n========================================")
    print("           MATCH HISTORY                ")
    print("========================================")

    # check if any results have been entered
    if len(match_history) == 0:
        print("No results have been entered yet")
        return

    # loop through all matches and display them
    match_number = 1
    for match in match_history:
        print("\nMatch " + str(match_number) + " - Group " + match["group"])
        print(match["home_team"] + " " + str(match["home_goals"]) + " - " + str(match["away_goals"]) + " " + match["away_team"])
        match_number = match_number + 1

    print("\nTotal matches entered: " + str(len(match_history)))

# ==========================================
# FEATURE 6: SAVE DATA TO FILE
# saves all standings, match history and knockout bracket to a json file
# ==========================================

def save_data():
    try:
        # check if a save file already exists and warn the user before overwriting
        if os.path.exists("worldcup_data.json"):
            print("\nA save file already exists. Overwriting will replace all previous data.")
            confirm = input("Are you sure you want to overwrite? (yes/no): ").lower()
            if confirm != "yes":
                print("Save cancelled.")
                return

        # combine all data into one dictionary
        data = {
            "standings": standings,
            "match_history": match_history,
            "knockout_bracket": knockout_bracket
        }

        # open the file for writing and save the data
        fh = open("worldcup_data.json", "w")
        json.dump(data, fh)
        fh.close()

        print("\nData saved successfully to worldcup_data.json")

    except IOError:
        print("Error - could not save data to file")

# ==========================================
# FEATURE 7: LOAD DATA FROM FILE
# loads previously saved data from a json file
# ==========================================

def load_data():
    global standings, knockout_bracket

    try:
        # check if the file exists before trying to open it
        if not os.path.exists("worldcup_data.json"):
            print("Error - no saved data file found")
            return

        # open the file and load the data
        fh = open("worldcup_data.json", "r")
        data = json.load(fh)
        fh.close()

        # update standings with loaded data
        standings = data["standings"]

        # clear the current match history and reload from file
        match_history.clear()
        for match in data["match_history"]:
            match_history.append(match)

        # load knockout bracket if it exists in the file
        if "knockout_bracket" in data:
            knockout_bracket["round_of_32"] = data["knockout_bracket"]["round_of_32"]
            knockout_bracket["round_of_16"] = data["knockout_bracket"]["round_of_16"]
            knockout_bracket["quarterfinals"] = data["knockout_bracket"]["quarterfinals"]
            knockout_bracket["semifinals"] = data["knockout_bracket"]["semifinals"]
            knockout_bracket["final"] = data["knockout_bracket"]["final"]
            knockout_bracket["winner"] = data["knockout_bracket"]["winner"]

        print("\nData loaded successfully from worldcup_data.json")

    except IOError:
        print("Error - could not load data from file")

    except (json.JSONDecodeError, KeyError):
        print("Error - saved file is corrupted or in wrong format")

# ==========================================
# FEATURE 8: VIEW QUALIFIED TEAMS
# shows all 32 teams that qualify for the knockout stage
# only available once all group stage matches are complete
# ==========================================

def view_qualified_teams():
    print("\n========================================")
    print("        QUALIFIED TEAMS                 ")
    print("========================================")

    # check that all group stage matches are complete first
    if not all_groups_complete():
        print("\nNot all group stage matches have been played yet.")
        print("Complete all groups first before viewing qualified teams.")
        return

    # get all qualified teams
    winners, runners_up, best_third, eliminated_third = get_qualified_teams()

    print("\n--- GROUP WINNERS (12 teams - automatic qualification) ---")
    number = 1
    for team_data in winners:
        print(str(number) + ". " + team_data[1] + " (Group " + team_data[0] + ")")
        number = number + 1

    print("\n--- GROUP RUNNERS-UP (12 teams - automatic qualification) ---")
    number = 1
    for team_data in runners_up:
        print(str(number) + ". " + team_data[1] + " (Group " + team_data[0] + ")")
        number = number + 1

    print("\n--- BEST THIRD-PLACE TEAMS (8 teams qualify out of 12) ---")
    number = 1
    for team_data in best_third:
        gd = team_data[2]["goals_for"] - team_data[2]["goals_against"]
        gd_str = "+" + str(gd) if gd > 0 else str(gd)
        print(str(number) + ". " + team_data[1] + " (Group " + team_data[0] + ") - Pts: " + str(team_data[2]["points"]) + " GD: " + gd_str)
        number = number + 1

    print("\n--- ELIMINATED THIRD-PLACE TEAMS (4 teams eliminated) ---")
    for team_data in eliminated_third:
        gd = team_data[2]["goals_for"] - team_data[2]["goals_against"]
        gd_str = "+" + str(gd) if gd > 0 else str(gd)
        print("  " + team_data[1] + " (Group " + team_data[0] + ") - Pts: " + str(team_data[2]["points"]) + " GD: " + gd_str)

    print("\nTotal qualified teams: 32")

# ==========================================
# FEATURE 9: KNOCKOUT STAGE
# allows user to play through the knockout rounds
# user picks the winner of each match (simulating extra time/penalties)
# ==========================================

def simulate_entire_knockout():
    # simulates all remaining knockout matches randomly from current state to final
    print("\nSimulating all remaining knockout matches...\n")

    round_order = ["round_of_32", "round_of_16", "quarterfinals", "semifinals"]
    round_names = {
        "round_of_32": "Round of 32",
        "round_of_16": "Round of 16",
        "quarterfinals": "Quarterfinals",
        "semifinals": "Semifinals",
        "final": "Final"
    }

    # simulate each round in order
    for rnd in round_order:
        # skip rounds not yet set up
        if len(knockout_bracket[rnd]) == 0:
            continue

        # simulate all undecided matches in this round
        for match in knockout_bracket[rnd]:
            if match["winner"] == "":
                winner = random.choice([match["team1"], match["team2"]])
                match["winner"] = winner
                print(round_names[rnd] + ": " + match["team1"] + " vs " + match["team2"] + " -> " + winner)

        # set up the next round if not already done
        next_rounds = {
            "round_of_32": "round_of_16",
            "round_of_16": "quarterfinals",
            "quarterfinals": "semifinals",
            "semifinals": "final"
        }
        next_rnd = next_rounds[rnd]
        if len(knockout_bracket[next_rnd]) == 0:
            next_teams = []
            for match in knockout_bracket[rnd]:
                next_teams.append(match["winner"])
            next_matches = []
            i = 0
            while i < len(next_teams) - 1:
                next_matches.append({"team1": next_teams[i], "team2": next_teams[i + 1], "winner": ""})
                i = i + 2
            knockout_bracket[next_rnd] = next_matches

    # simulate the final
    if len(knockout_bracket["final"]) > 0:
        final_match = knockout_bracket["final"][0]
        if final_match["winner"] == "":
            winner = random.choice([final_match["team1"], final_match["team2"]])
            final_match["winner"] = winner
            knockout_bracket["winner"] = winner
            print("Final: " + final_match["team1"] + " vs " + final_match["team2"] + " -> " + winner)


def play_knockout_stage():
    print("\n========================================")
    print("         KNOCKOUT STAGE                 ")
    print("========================================")

    # check that all group stage matches are complete first
    if not all_groups_complete():
        print("\nNot all group stage matches have been played yet.")
        print("Please complete all group stage matches first.")
        return

    # if tournament already complete just show the winner and summary
    if knockout_bracket["winner"] != "":
        print("\n========================================")
        print("  WORLD CUP WINNER: " + knockout_bracket["winner"] + "!")
        print("========================================")
        print("\nCongratulations! The tournament is complete.")
        show_tournament_summary()
        return

    # ask user if they want to simulate everything or play manually
    print("\nWhat would you like to do?")
    print("1. Play knockout stage match by match")
    print("2. Simulate ALL remaining knockout matches at once")

    try:
        ko_choice = int(input("\nEnter choice: "))
    except ValueError:
        print("Error - please enter 1 or 2")
        return

    # simulate entire remaining knockout at once
    if ko_choice == 2:
        # set up round of 32 first if not done yet
        if len(knockout_bracket["round_of_32"]) == 0:
            setup_round_of_32_silent()
        simulate_entire_knockout()
        if knockout_bracket["winner"] != "":
            print("\n========================================")
            print("  WORLD CUP WINNER: " + knockout_bracket["winner"] + "!")
            print("========================================")
            show_tournament_summary()
        return

    elif ko_choice != 1:
        print("Error - please enter 1 or 2")
        return

    # define all rounds in order with their display names
    round_order = [
        ("round_of_32",   "Round of 32"),
        ("round_of_16",   "Round of 16"),
        ("quarterfinals", "Quarterfinals"),
        ("semifinals",    "Semifinals"),
        ("final",         "THE FINAL")
    ]

    # set up round of 32 if not done yet
    if len(knockout_bracket["round_of_32"]) == 0:
        setup_round_of_32()

    # loop continuously through all rounds until tournament is complete or user stops
    while True:
        tournament_complete = True

        for round_name, round_display in round_order:
            # skip rounds not set up yet
            if len(knockout_bracket[round_name]) == 0:
                tournament_complete = False
                continue

            # if this round is not fully decided yet play it
            if not all_round_decided(round_name):
                tournament_complete = False
                # play this round - returns True if round complete, False if user stopped
                round_finished = play_knockout_round_matches(round_name, round_display)

                if not round_finished:
                    # user chose to stop - exit back to main menu
                    print("Returning to main menu. Come back to continue!")
                    return

                # round is now complete - continue loop to set up next round
                break

            # round is complete - set up the next round if not done yet
            if round_name == "round_of_32" and len(knockout_bracket["round_of_16"]) == 0:
                setup_next_round("round_of_32", "round_of_16", "Round of 16")
                tournament_complete = False
                break
            elif round_name == "round_of_16" and len(knockout_bracket["quarterfinals"]) == 0:
                setup_next_round("round_of_16", "quarterfinals", "Quarterfinals")
                tournament_complete = False
                break
            elif round_name == "quarterfinals" and len(knockout_bracket["semifinals"]) == 0:
                setup_next_round("quarterfinals", "semifinals", "Semifinals")
                tournament_complete = False
                break
            elif round_name == "semifinals" and len(knockout_bracket["final"]) == 0:
                setup_next_round("semifinals", "final", "The Final")
                tournament_complete = False
                break

        # check if tournament is fully complete
        if tournament_complete and all_round_decided("final"):
            knockout_bracket["winner"] = knockout_bracket["final"][0]["winner"]
            print("\n========================================")
            print("  WORLD CUP WINNER: " + knockout_bracket["winner"] + "!")
            print("========================================")
            show_tournament_summary()
            return

# ==========================================
# HELPER FUNCTION: SETUP ROUND OF 32
# creates the 32 matchups based on group results
# uses simplified bracket: winner of group vs runner up of next group
# ==========================================

def all_round_decided(round_name):
    # check if all matches in a round have a winner
    for match in knockout_bracket[round_name]:
        if match["winner"] == "":
            return False
    return True


def setup_next_round(current_round, next_round, next_round_name):
    # collect winners from current round and pair them for next round
    print("\n--- SETTING UP " + next_round_name.upper() + " ---")
    next_teams = []
    for match in knockout_bracket[current_round]:
        next_teams.append(match["winner"])
    next_matches = []
    i = 0
    while i < len(next_teams) - 1:
        next_matches.append({"team1": next_teams[i], "team2": next_teams[i + 1], "winner": ""})
        i = i + 2
    knockout_bracket[next_round] = next_matches
    print(next_round_name + " set up with " + str(len(next_matches)) + " matches!")


def setup_round_of_32_silent():
    # sets up round of 32 without printing anything - used for simulate all
    winners, runners_up, best_third, eliminated_third = get_qualified_teams()
    group_letters = list(groups.keys())
    matches = []
    for i in range(12):
        winner_group = group_letters[i]
        runner_group = group_letters[(i + 1) % 12]
        winner = ""
        runner = ""
        for team_data in winners:
            if team_data[0] == winner_group:
                winner = team_data[1]
        for team_data in runners_up:
            if team_data[0] == runner_group:
                runner = team_data[1]
        matches.append({"team1": winner, "team2": runner, "winner": ""})
    for i in range(0, 8, 2):
        matches.append({"team1": best_third[i][1], "team2": best_third[i + 1][1], "winner": ""})
    knockout_bracket["round_of_32"] = matches


def setup_round_of_32():
    print("\n--- SETTING UP ROUND OF 32 ---")

    # get all qualified teams
    winners, runners_up, best_third, eliminated_third = get_qualified_teams()

    # create 16 matchups for round of 32
    # simplified bracket: winner of group A vs runner-up of group B etc.
    # the 8 best third place teams fill the remaining 4 matches
    group_letters = list(groups.keys())
    matches = []

    # create matches between group winners and runners-up from adjacent groups
    for i in range(12):
        winner_group = group_letters[i]
        runner_group = group_letters[(i + 1) % 12]

        winner = ""
        runner = ""

        for team_data in winners:
            if team_data[0] == winner_group:
                winner = team_data[1]

        for team_data in runners_up:
            if team_data[0] == runner_group:
                runner = team_data[1]

        matches.append({"team1": winner, "team2": runner, "winner": ""})

    # add 4 matches involving the 8 best third place teams
    for i in range(0, 8, 2):
        matches.append({
            "team1": best_third[i][1],
            "team2": best_third[i + 1][1],
            "winner": ""
        })

    # save the round of 32 matches to the bracket
    knockout_bracket["round_of_32"] = matches

    print("\nRound of 32 has been set up with 16 matches!")

# ==========================================
# HELPER FUNCTION: PLAY A KNOCKOUT ROUND
# shows matches and asks user to pick winners
# then sets up the next round
# ==========================================

def play_knockout_round_matches(round_name, round_display_name):
    # shows all matches in a round and asks user to pick winners
    # returns True if all matches in the round are now decided, False otherwise
    print("\n========================================")
    print("  " + round_display_name.upper())
    print("========================================")
    print("Note: No draws. Tied after 90 mins = extra time then penalties.")
    print("Options: 1=team1 wins  2=team2 wins  3=simulate  4=simulate whole round  5=stop for now\n")

    # get the matches for this round
    matches = knockout_bracket[round_name]

    # check if all matches already decided
    if all_round_decided(round_name):
        print("All matches in this round already decided!")
        return True

    # go through each match and ask for the winner
    match_number = 1
    for match in matches:
        # show already decided matches
        if match["winner"] != "":
            print("Match " + str(match_number) + ": " + match["team1"] + " vs " + match["team2"] + " -> " + match["winner"])
            match_number = match_number + 1
            continue

        print("Match " + str(match_number) + ": " + match["team1"] + " vs " + match["team2"])
        print("  1. " + match["team1"] + " wins")
        print("  2. " + match["team2"] + " wins")
        print("  3. Simulate this match randomly")
        print("  4. Simulate ALL remaining matches in this round")
        print("  5. Stop here and go back to main menu")

        try:
            choice = int(input("  Choice: "))

            if choice == 1:
                match["winner"] = match["team1"]
                print("  " + match["team1"] + " advances!\n")

            elif choice == 2:
                match["winner"] = match["team2"]
                print("  " + match["team2"] + " advances!\n")

            elif choice == 3:
                # randomly simulate this single match
                winner = random.choice([match["team1"], match["team2"]])
                match["winner"] = winner
                print("  Simulated: " + winner + " advances!\n")

            elif choice == 4:
                # simulate all remaining matches in this round at once
                print("\n  Simulating all remaining matches in this round...\n")
                for remaining in matches:
                    if remaining["winner"] == "":
                        winner = random.choice([remaining["team1"], remaining["team2"]])
                        remaining["winner"] = winner
                        print("  " + remaining["team1"] + " vs " + remaining["team2"] + " -> " + winner)
                print("")
                # round is now fully decided
                return True

            elif choice == 5:
                # stop and go back to main menu
                print("\n  Stopping here. Come back to continue the knockout stage.\n")
                return False

            else:
                print("  Error - please enter 1, 2, 3, 4 or 5\n")
                # re-ask the same match by decrementing the counter
                match_number = match_number + 1
                continue

        except ValueError:
            print("  Error - please enter a valid number\n")
            match_number = match_number + 1
            continue

        match_number = match_number + 1

    return all_round_decided(round_name)



# ==========================================
# TOURNAMENT SUMMARY
# shows group rankings for all 12 groups after tournament is complete
# ==========================================

def show_tournament_summary():
    print("\n========================================")
    print("       FINAL GROUP STAGE RANKINGS       ")
    print("========================================")

    # loop through each group and show the final standings
    for group in groups:
        sorted_teams = sort_standings(group)
        print("\nGroup " + group + ":")
        position = 1
        for team_data in sorted_teams:
            team = team_data[0]
            stats = team_data[1]
            goal_diff = stats["goals_for"] - stats["goals_against"]
            goal_diff_str = "+" + str(goal_diff) if goal_diff > 0 else str(goal_diff)
            print("  " + str(position) + ". " + team.ljust(25) + " Pts:" + str(stats["points"]).rjust(2) + "  GD:" + goal_diff_str.rjust(3))
            position = position + 1

    print("\n========================================")
    print("       KNOCKOUT STAGE RESULTS           ")
    print("========================================")

    # show results of each knockout round
    round_names = {
        "round_of_32": "Round of 32",
        "round_of_16": "Round of 16",
        "quarterfinals": "Quarterfinals",
        "semifinals": "Semifinals",
        "final": "Final"
    }

    for rnd in ["round_of_32", "round_of_16", "quarterfinals", "semifinals", "final"]:
        if len(knockout_bracket[rnd]) > 0:
            print("\n--- " + round_names[rnd] + " ---")
            for match in knockout_bracket[rnd]:
                if match["winner"] != "":
                    print("  " + match["team1"] + " vs " + match["team2"] + " -> " + match["winner"])

    print("\n========================================")
    print("  WORLD CUP WINNER: " + knockout_bracket["winner"] + "!")
    print("========================================")


# ==========================================
# MAIN MENU
# ==========================================

def main():
    print("\n========================================")
    print("  FIFA WORLD CUP 2026 TRACKER           ")
    print("========================================")
    print("  Welcome! Track the full 2026 World Cup")
    print("========================================")

    while True:
        print("\n----------------------------------------")
        print("              MAIN MENU                 ")
        print("----------------------------------------")
        print("  --- GROUP STAGE ---")
        print("  1. View All Groups and Teams")
        print("  2. Enter Match Result")
        print("  3. Simulate Group Results")
        print("  4. View Group Standings")
        print("  5. View Match History")
        print("  --- SAVE / LOAD ---")
        print("  6. Save data to file")
        print("  7. Load previously saved data")
        print("  --- KNOCKOUT STAGE ---")
        print("  8. View Qualified Teams (32 teams)")
        print("  9. Play Knockout Stage")
        print("  --- ---")
        print("  10. Exit")
        print("----------------------------------------")

        try:
            choice = input("\n  Choice: ")

            if choice == "1":
                view_groups()
            elif choice == "2":
                enter_result()
            elif choice == "3":
                simulate_group()
            elif choice == "4":
                view_standings()
            elif choice == "5":
                view_match_history()
            elif choice == "6":
                save_data()
            elif choice == "7":
                load_data()
            elif choice == "8":
                view_qualified_teams()
            elif choice == "9":
                play_knockout_stage()
            elif choice == "10":
                print("\nGoodbye! Thanks for using the World Cup Tracker!")
                break
            else:
                print("Error - please enter a number between 1 and 10")

        except ValueError:
            print("Error - please enter a valid number")

# run the program
main()
