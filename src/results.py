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


PERSONALITY_CARDS = {
    "INTJ": {
        "name": "The Architect",
        "color": discord.Color.dark_teal(),
        "traits": [
            "Strategic thinker",
            "Independent",
            "Future-focused",
            "Enjoys solving complex problems",
        ],
        "strengths": [
            "Planning",
            "Logical reasoning",
            "Learning quickly",
        ],
        "growth": [
            "Can overanalyse",
            "May overlook emotions",
        ],
    },
    "INTP": {
        "name": "The Logician",
        "color": discord.Color.blurple(),
        "traits": ["Analytical", "Curious", "Open-minded", "Independent"],
        "strengths": ["Problem solving", "Innovation", "Pattern recognition"],
        "growth": ["May delay action", "Can get stuck in thought"],
    },
    "ENTJ": {
        "name": "The Commander",
        "color": discord.Color.red(),
        "traits": ["Decisive", "Driven", "Confident", "Goal-oriented"],
        "strengths": ["Leadership", "Strategy", "Execution"],
        "growth": ["Can be impatient", "May seem overly direct"],
    },
    "ENTP": {
        "name": "The Debater",
        "color": discord.Color.orange(),
        "traits": ["Inventive", "Quick-witted", "Energetic", "Curious"],
        "strengths": ["Idea generation", "Adaptability", "Communication"],
        "growth": ["May lose focus", "Can debate for too long"],
    },
    "INFJ": {
        "name": "The Advocate",
        "color": discord.Color.green(),
        "traits": ["Insightful", "Idealistic", "Empathetic", "Private"],
        "strengths": ["Vision", "Understanding others", "Purpose-driven work"],
        "growth": ["Can take on too much", "May set very high standards"],
    },
    "INFP": {
        "name": "The Mediator",
        "color": discord.Color.purple(),
        "traits": ["Imaginative", "Values-driven", "Gentle", "Reflective"],
        "strengths": ["Creativity", "Empathy", "Authenticity"],
        "growth": ["Can idealise outcomes", "May avoid conflict"],
    },
    "ENFJ": {
        "name": "The Protagonist",
        "color": discord.Color.gold(),
        "traits": ["Encouraging", "Outgoing", "Organised", "People-focused"],
        "strengths": ["Motivating others", "Communication", "Collaboration"],
        "growth": ["Can overextend", "May prioritise others too much"],
    },
    "ENFP": {
        "name": "The Campaigner",
        "color": discord.Color.fuchsia(),
        "traits": ["Enthusiastic", "Creative", "Warm", "Spontaneous"],
        "strengths": ["Inspiration", "Connection", "Fresh ideas"],
        "growth": ["Can get distracted", "May struggle with routine"],
    },
    "ISTJ": {
        "name": "The Logistician",
        "color": discord.Color.dark_gold(),
        "traits": ["Reliable", "Structured", "Responsible", "Practical"],
        "strengths": ["Consistency", "Organisation", "Follow-through"],
        "growth": ["Can resist change", "May be overly rigid"],
    },
    "ISFJ": {
        "name": "The Protector",
        "color": discord.Color.dark_green(),
        "traits": ["Caring", "Dependable", "Quiet", "Observant"],
        "strengths": ["Support", "Detail awareness", "Loyalty"],
        "growth": ["May avoid attention", "Can put others first too often"],
    },
    "ESTJ": {
        "name": "The Executive",
        "color": discord.Color.dark_red(),
        "traits": ["Efficient", "Direct", "Organised", "Responsible"],
        "strengths": ["Leadership", "Decision making", "Reliability"],
        "growth": ["Can be inflexible", "May push too hard"],
    },
    "ESFJ": {
        "name": "The Consul",
        "color": discord.Color.dark_magenta(),
        "traits": ["Friendly", "Supportive", "Social", "Practical"],
        "strengths": ["Community building", "Care", "Coordination"],
        "growth": ["Can seek approval", "May worry about harmony too much"],
    },
    "ISTP": {
        "name": "The Virtuoso",
        "color": discord.Color.teal(),
        "traits": ["Adaptable", "Observant", "Calm", "Hands-on"],
        "strengths": ["Troubleshooting", "Practical fixes", "Independence"],
        "growth": ["Can be reserved", "May avoid long-term planning"],
    },
    "ISFP": {
        "name": "The Adventurer",
        "color": discord.Color.dark_purple(),
        "traits": ["Artistic", "Kind", "Flexible", "Present-focused"],
        "strengths": ["Creativity", "Sensitivity", "Adaptability"],
        "growth": ["Can avoid structure", "May keep feelings private"],
    },
    "ESTP": {
        "name": "The Entrepreneur",
        "color": discord.Color.orange(),
        "traits": ["Bold", "Practical", "Action-oriented", "Energetic"],
        "strengths": ["Quick decisions", "Problem solving", "Confidence"],
        "growth": ["Can act impulsively", "May dislike routines"],
    },
    "ESFP": {
        "name": "The Entertainer",
        "color": discord.Color.blurple(),
        "traits": ["Playful", "Warm", "Spontaneous", "Expressive"],
        "strengths": ["Energy", "Connection", "Adaptability"],
        "growth": ["Can seek excitement", "May avoid boring tasks"],
    },
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


def build_personality_card_embed(mbti):
    card = PERSONALITY_CARDS.get(mbti.upper())

    if card is None:
        return discord.Embed(
            title="Personality Card",
            description=f"I do not have a card for **{mbti}**.",
            color=discord.Color.red()
        )

    traits = "\n".join(f"🔹 {trait}" for trait in card["traits"])
    strengths = "\n".join(f"✓ {strength}" for strength in card["strengths"])
    growth = "\n".join(f"• {area}" for area in card["growth"])

    embed = discord.Embed(
        title=f"Your MBTI: {mbti.upper()}",
        description=f'"{card["name"]}"',
        color=card["color"]
    )
    embed.add_field(name="Your traits", value=traits, inline=False)
    embed.add_field(name="Strengths", value=strengths, inline=False)
    embed.add_field(name="Growth areas", value=growth, inline=False)
    embed.set_footer(text="MBTI personality card")
    return embed