import gradio

from util.champions import champions
from util.regions import regions


def output(*args):
    return f"inputs = {*args,}"


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
    gradio.Radio(
        ["Regular Season", "Playoffs", "Gauntlet", "International"],
        label="Tournament Type",
        interactive=True,
    ),

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
        ],
        outputs=text_output,
    )
    # text_button.click(flip_text, inputs=text_input, outputs=text_output)


demo.title = "Does Faker Win?"
demo.description = "TODO"
if __name__ == "__main__":
    demo.launch()
