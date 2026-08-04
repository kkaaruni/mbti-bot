import discord


DIMENSION_LABELS = {
    "E": "extroverted",
    "I": "introverted",
    "N": "intuitive",
    "S": "sensing",
    "T": "thinking",
    "F": "feeling",
    "J": "judging",
    "P": "perceiving",
}


def build_result_embed(mbti, scores):
    personality_lines = []

    for first, second in [("E", "I"), ("N", "S"), ("T", "F"), ("J", "P")]:
        first_score = scores[first]
        second_score = scores[second]
        total = first_score + second_score

        if total == 0:
            first_percent = 50
        else:
            first_percent = round((first_score / total) * 100)

        second_percent = 100 - first_percent

        if first_score >= second_score:
            lead_label = DIMENSION_LABELS[first]
            follow_label = DIMENSION_LABELS[second]
        else:
            lead_label = DIMENSION_LABELS[second]
            follow_label = DIMENSION_LABELS[first]
            first_percent, second_percent = second_percent, first_percent

        personality_lines.append(
            f"You are about {first_percent}% {lead_label} and {second_percent}% {follow_label}."
        )

    embed = discord.Embed(
        title="Your MBTI Results",
        description="Here’s a breakdown of your personality profile.",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="Personality Breakdown",
        value="\n".join(personality_lines),
        inline=False
    )
    embed.add_field(
        name="Your MBTI Type",
        value=f"**{mbti}**",
        inline=False
    )
    return embed