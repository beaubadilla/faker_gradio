import gradio
from joblib import load

from util.champions import champions
from util.champions_dmg_profile import champions_dmg_profile
from util.champions_role import roles
from util.regions import regions
import pandas
import numpy as np


def warn(*args, **kwargs):
    pass


import warnings

warnings.warn = warn

MODEL = load("./models/rf_5.pkl")


def output(
    blue_is_t1,
    blue_top_champion,
    blue_jungle_champion,
    blue_mid_champion,
    blue_bot_champion,
    blue_support_champion,
    blue_region,
    red_is_t1,
    red_top_champion,
    red_jungle_champion,
    red_mid_champion,
    red_bot_champion,
    red_support_champion,
    red_region,
    tournament_type,
    tournament_curr_win,
    tournament_curr_loss,
):
    # ['Side','tournament_curr_win_percentage','teams_region',
    #  'teammate_role_top','teammate_role_jungle','teammate_role_mid','teammate_role_adc','teammate_role_support',
    #  'enemy_role_top','enemy_role_jungle','enemy_role_mid','enemy_role_adc','enemy_role_support',
    #  'tournament_type',
    #  'blue_physical_damage_perc','blue_magic_damage_perc','blue_true_damage_perc','red_physical_damage_perc','red_magic_damage_perc','red_true_damage_perc']
    # model.predict

    blue_picks = [
        blue_top_champion,
        blue_jungle_champion,
        blue_mid_champion,
        blue_bot_champion,
        blue_support_champion,
    ]
    red_picks = [
        red_top_champion,
        red_jungle_champion,
        red_mid_champion,
        red_bot_champion,
        red_support_champion,
    ]

    # feature engineer
    # 'Side'
    side = "Blue" if blue_is_t1 else "Red"

    # 'tournament_curr_win_percentage'
    tournament_curr_win_percentage = calculate_tcwp(
        tournament_curr_win, tournament_curr_loss
    )

    # teams_region
    # teams_region does not require any engineering
    teams_region = red_region if blue_is_t1 else blue_region

    # teammate_role_* and enemy_role_*
    fakers_teams_champions, enemy_teams_champions = (
        (blue_picks, red_picks) if blue_is_t1 else (red_picks, blue_picks)
    )

    teammates_role = [
        get_champion_role(fakers_teams_champions[0], "top"),
        get_champion_role(fakers_teams_champions[1], "jungle"),
        get_champion_role(fakers_teams_champions[2], "mid"),
        get_champion_role(fakers_teams_champions[3], "bot"),
        get_champion_role(fakers_teams_champions[4], "support"),
    ]
    enemy_role = [
        get_champion_role(enemy_teams_champions[0], "top"),
        get_champion_role(enemy_teams_champions[1], "jungle"),
        get_champion_role(enemy_teams_champions[2], "mid"),
        get_champion_role(enemy_teams_champions[3], "bot"),
        get_champion_role(enemy_teams_champions[4], "support"),
    ]

    # 'tournament type'
    # tournament_type does not require any engineering

    # blue_*_damage_perc and red_*_damage_perc
    (
        blue_physical_damage_perc,
        blue_magic_damage_perc,
        blue_true_damage_perc,
        red_physical_damage_perc,
        red_magic_damage_perc,
        red_true_damage_perc,
    ) = get_damage_profile_composition(blue_picks, red_picks)

    headers = [
        "Side",
        "tournament_curr_win_percentage",
        "teams_region",
        "teammate_role_top",
        "teammate_role_jungle",
        "teammate_role_mid",
        "teammate_role_adc",
        "teammate_role_support",
        "enemy_role_top",
        "enemy_role_jungle",
        "enemy_role_mid",
        "enemy_role_adc",
        "enemy_role_support",
        "tournament_type",
        "blue_physical_damage_perc",
        "blue_magic_damage_perc",
        "blue_true_damage_perc",
        "red_physical_damage_perc",
        "red_magic_damage_perc",
        "red_true_damage_perc",
    ]

    sample = [
        # *headers,
        [
            side,
            tournament_curr_win_percentage,
            teams_region,
            *teammates_role,
            *enemy_role,
            tournament_type,
            blue_physical_damage_perc,
            blue_magic_damage_perc,
            blue_true_damage_perc,
            red_physical_damage_perc,
            red_magic_damage_perc,
            red_true_damage_perc,
        ],
    ]
    sample = pandas.DataFrame(
        data=sample, index=np.arange(len(sample)), columns=headers
    )
    prediction = MODEL.predict(sample)

    return f"inputs = {sample}, prediction = {prediction}"


def calculate_tcwp(wins, losses):
    if wins == 0 and losses == 0:
        return 0.5

    return round(wins / (wins + losses), 4)


def get_damage_profile_composition(blue_side_picks, red_side_picks):
    # get blue picks info with comprehension
    blue_team_info = {champ: champions_dmg_profile[champ] for champ in blue_side_picks}
    # get red picks info with comprehension
    red_team_info = {champ: champions_dmg_profile[champ] for champ in red_side_picks}

    # calculate weights
    # sum DPM
    sum_blue_dpm = sum((info["DPM"] for info in blue_team_info.values()))
    for info in blue_team_info.values():
        curr_champ_dpm = info["DPM"]
        info["weight"] = curr_champ_dpm / sum_blue_dpm
    sum_red_dpm = sum((info["DPM"] for info in red_team_info.values()))
    for info in red_team_info.values():
        curr_champ_dpm = info["DPM"]
        info["weight"] = curr_champ_dpm / sum_red_dpm

    blue_physical_damage_perc = sum(
        info["weight"] * info["physical_damage"] for info in blue_team_info.values()
    )
    blue_magic_damage_perc = sum(
        info["weight"] * info["magic_damage"] for info in blue_team_info.values()
    )
    blue_true_damage_perc = sum(
        info["weight"] * info["true_damage"] for info in blue_team_info.values()
    )
    red_physical_damage_perc = sum(
        info["weight"] * info["physical_damage"] for info in red_team_info.values()
    )
    red_magic_damage_perc = sum(
        info["weight"] * info["magic_damage"] for info in red_team_info.values()
    )
    red_true_damage_perc = sum(
        info["weight"] * info["true_damage"] for info in red_team_info.values()
    )

    return (
        blue_physical_damage_perc,
        blue_magic_damage_perc,
        blue_true_damage_perc,
        red_physical_damage_perc,
        red_magic_damage_perc,
        red_true_damage_perc,
    )


# def feature_engineer():
#     # champions -> dmg profiles
#     # champions -> role
#     # is_t1 -> blue / red side
#     return (side,)
#     ...


def get_champion_role(champion, lane):
    if champion == "Nunu":
        champion = "Nunu & Willump"
    classes = roles[champion].split()

    if champion == "Varus":
        if lane == "bot":
            subcls = classes[1]
        else:
            subcls = classes[3]
    else:
        subcls = classes[1]

    return subcls


with gradio.Blocks() as demo:
    demo.title = "Faker Classifier"
    gradio.Markdown("""# Does Faker Win?""")
    with gradio.Row():
        # Blue Side
        with gradio.Column():
            gradio.Markdown("""## Blue Side""")
            blue_region = gradio.Dropdown(
                choices=regions,
                label="Team's Region",
                value="Korea",
                interactive=True,
            )
            blue_is_t1 = gradio.Checkbox(label="T1?", value=True)
            blue_top_champion = gradio.Dropdown(
                choices=champions,
                label="Top",
                value="Teemo",
                interactive=True,
            )
            blue_jungle_champion = gradio.Dropdown(
                choices=champions,
                label="Jungle",
                value="Teemo",
                interactive=True,
            )
            blue_mid_champion = gradio.Dropdown(
                choices=champions,
                label="Mid",
                value="Teemo",
                interactive=True,
            )
            blue_bot_champion = gradio.Dropdown(
                choices=champions,
                label="Bot",
                value="Teemo",
                interactive=True,
            )
            blue_support_champion = gradio.Dropdown(
                choices=champions,
                label="Support",
                value="Teemo",
                interactive=True,
            )

        # Red Side
        with gradio.Column():
            gradio.Markdown("""## Red Side""")
            red_region = gradio.Dropdown(
                choices=regions,
                label="Team's Region",
                value="Korea",
                interactive=True,
            )
            red_is_t1 = gradio.Checkbox(label="T1?")
            red_top_champion = gradio.Dropdown(
                choices=champions,
                label="Top",
                value="Teemo",
                interactive=True,
            )
            red_jungle_champion = gradio.Dropdown(
                choices=champions,
                label="Jungle",
                value="Teemo",
                interactive=True,
            )
            red_mid_champion = gradio.Dropdown(
                choices=champions,
                label="Mid",
                value="Teemo",
                interactive=True,
            )
            red_bot_champion = gradio.Dropdown(
                choices=champions,
                label="Bot",
                value="Teemo",
                interactive=True,
            )
            red_support_champion = gradio.Dropdown(
                choices=champions,
                label="Support",
                value="Teemo",
                interactive=True,
            )

        # Listeners
        red_is_t1.change(
            fn=lambda is_t1: not is_t1, inputs=red_is_t1, outputs=blue_is_t1
        )
        blue_is_t1.change(
            fn=lambda is_t1: not is_t1, inputs=blue_is_t1, outputs=red_is_t1
        )
        red_is_t1.change(
            fn=lambda is_t1: "Korea" if is_t1 else None,
            inputs=red_is_t1,
            outputs=red_region,
        )
        blue_is_t1.change(
            fn=lambda is_t1: "Korea" if is_t1 else None,
            inputs=blue_is_t1,
            outputs=blue_region,
        )
    tournament_type = gradio.Radio(
        ["Regular Season", "Playoffs", "Gauntlet", "International"],
        label="Tournament Type",
        interactive=True,
    )
    tournament_curr_win = gradio.Number(
        label="Number of wins in current tournament",
        interactive=True,
    )
    tournament_curr_loss = gradio.Number(
        label="Number of losses in current tournament",
        interactive=True,
    )

    # Output
    text_output = gradio.Textbox()
    output_btn = gradio.Button(value="Simulate match")
    output_btn.click(
        fn=output,
        inputs=[
            blue_is_t1,
            blue_top_champion,
            blue_jungle_champion,
            blue_mid_champion,
            blue_bot_champion,
            blue_support_champion,
            blue_region,
            red_is_t1,
            red_top_champion,
            red_jungle_champion,
            red_mid_champion,
            red_bot_champion,
            red_support_champion,
            red_region,
            tournament_type,
            tournament_curr_win,
            tournament_curr_loss,
        ],
        outputs=text_output,
    )

if __name__ == "__main__":
    demo.launch()
