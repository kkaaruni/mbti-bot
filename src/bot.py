import json
import os
from collections import Counter
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from questions import questions
from scoring import calculate_mbti
from results import build_personality_card_embed, build_result_embed

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
STATS_FILE = Path(__file__).resolve().parent.parent / "data" / "server_mbti_stats.json"
MBTI_TYPES = {"INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


def load_server_stats():
    if not STATS_FILE.exists():
        return {}

    try:
        with STATS_FILE.open("r", encoding="utf-8") as file_handle:
            return json.load(file_handle)
    except (json.JSONDecodeError, OSError):
        return {}


def save_server_stats(stats):
    STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with STATS_FILE.open("w", encoding="utf-8") as file_handle:
        json.dump(stats, file_handle, indent=2, sort_keys=True)


def record_server_mbti(guild_id, user_id, mbti):
    stats = load_server_stats()
    guild_stats = stats.setdefault(str(guild_id), {})
    guild_stats[str(user_id)] = mbti
    save_server_stats(stats)


def get_server_member_mbti(guild_id, user_id):
    stats = load_server_stats()
    guild_stats = stats.get(str(guild_id), {})
    return guild_stats.get(str(user_id))

#Assign MBTI role to user in server
async def assign_mbti_role(guild, member, mbti):
    role_name = mbti.upper()
    existing_role = discord.utils.get(guild.roles, name=role_name)

    if existing_role is None:
        if not guild.me.guild_permissions.manage_roles:
            return False
        existing_role = await guild.create_role(name=role_name, colour=discord.Colour.blurple())

    for role in member.roles:
        if role.name.upper() in MBTI_TYPES:
            try:
                await member.remove_roles(role)
            except discord.Forbidden:
                pass

    if existing_role not in member.roles:
        try:
            await member.add_roles(existing_role)
            return True
        except discord.Forbidden:
            return False

    return True


def build_server_stats_embed(guild_name, results):
    counts = Counter(results.values())
    total = sum(counts.values())

    embed = discord.Embed(
        title=f"{guild_name} MBTI Statistics",
        color=discord.Color.blurple()
    )

    if total == 0:
        embed.description = "No MBTI results have been recorded for this server yet."
        return embed

    distribution_lines = []
    for mbti, count in counts.most_common():
        percent = round((count / total) * 100)
        distribution_lines.append(f"{mbti}: {count} ({percent}%)")

    top_count = counts.most_common(1)[0][1]
    top_types = [mbti for mbti, count in counts.items() if count == top_count]

    embed.description = f"Based on {total} recorded result{'s' if total != 1 else ''}."
    embed.add_field(
        name="Distribution",
        value="\n".join(distribution_lines),
        inline=False
    )
    embed.add_field(
        name="Most Common Type",
        value=", ".join(f"**{mbti}**" for mbti in sorted(top_types)),
        inline=False
    )

    return embed


def build_compatibility_embed(author_name, author_mbti, target_name, target_mbti):
    matches = sum(1 for first, second in zip(author_mbti, target_mbti) if first == second)
    compatibility_percent = round((matches / len(author_mbti)) * 100)

    if compatibility_percent >= 75:
        compatibility_label = "high"
    elif compatibility_percent >= 50:
        compatibility_label = "moderate"
    else:
        compatibility_label = "low"

    embed = discord.Embed(
        title="MBTI Compatibility",
        description=f"{author_name} and {target_name} have {compatibility_label} compatibility.",
        color=discord.Color.green() if compatibility_percent >= 75 else discord.Color.gold() if compatibility_percent >= 50 else discord.Color.red()
    )
    embed.add_field(name=author_name, value=f"**{author_mbti}**", inline=True)
    embed.add_field(name=target_name, value=f"**{target_mbti}**", inline=True)
    embed.add_field(name="Compatibility", value=f"**{compatibility_percent}%**", inline=False)
    return embed

class StartView(discord.ui.View):
    def __init__(self, author, question_list, answers, ctx):
        super().__init__(timeout=180)
        self.author = author
        self.question_list = question_list
        self.answers = answers
        self.ctx = ctx

        start_button = discord.ui.Button(
            label="Start Quiz",
            style=discord.ButtonStyle.success
        )
        start_button.callback = self._start_callback
        self.add_item(start_button)

    async def interaction_check(self, interaction):
        if interaction.user != self.author:
            await interaction.response.send_message(
                "Only the person taking the test can start it.",
                ephemeral=True
            )
            return False
        return True

    async def _start_callback(self, interaction):
        view = QuestionView(
            self.author,
            self.question_list,
            self.answers,
            0,
            self.ctx
        )
        embed = view._build_embed(0)
        await interaction.response.edit_message(
            content=f"Question 1 of {len(self.question_list)}",
            embed=embed,
            view=view
        )


class QuestionView(discord.ui.View):
    def __init__(self, author, question_list, answers, index, ctx):
        super().__init__(timeout=180)
        self.author = author
        self.question_list = question_list
        self.answers = answers
        self.index = index
        self.ctx = ctx
        self._build_buttons()

    def _build_buttons(self):
        for value in range(1, 11):
            if value <= 3:
                style = discord.ButtonStyle.primary
            elif value <= 7:
                style = discord.ButtonStyle.primary
            else:
                style = discord.ButtonStyle.primary

            button = discord.ui.Button(
                label=str(value),
                style=style
            )
            button.callback = self._make_callback(value)
            self.add_item(button)

    def _make_callback(self, value):
        async def callback(interaction):
            await self._handle_answer(interaction, value)

        return callback

    async def interaction_check(self, interaction):
        if interaction.user != self.author:
            await interaction.response.send_message(
                "Only the person taking the test can answer.",
                ephemeral=True
            )
            return False
        return True

    async def _handle_answer(self, interaction, value):
        self.answers.append(value)

        if self.index + 1 < len(self.question_list):
            next_index = self.index + 1
            embed = self._build_embed(next_index)
            next_view = QuestionView(
                self.author,
                self.question_list,
                self.answers,
                next_index,
                self.ctx
            )
            await interaction.response.edit_message(
                content=f"Question {next_index + 1} of {len(self.question_list)}",
                embed=embed,
                view=next_view
            )
            return

        mbti, scores = calculate_mbti(self.answers, self.question_list)
        if self.ctx.guild is not None:
            record_server_mbti(self.ctx.guild.id, interaction.user.id, mbti)
            await assign_mbti_role(self.ctx.guild, interaction.user, mbti)
        embed = build_result_embed(mbti, scores)

        await interaction.response.edit_message(
            content="Test complete!",
            embed=embed,
            view=None
        )

    def _build_embed(self, index):
        question = self.question_list[index]
        embed = discord.Embed(
            title=f"MBTI Question {index + 1}/{len(self.question_list)}",
            description=question["question"],
            color=discord.Color.blurple()
        )
        embed.add_field(
            name="How to answer",
            value="Choose a number from 1 to 10.\n1 = strongly disagree, 10 = strongly agree.",
            inline=False
        )
        return embed

@bot.group(invoke_without_command=True)
async def mbti(ctx):
    await ctx.send("Use `!mbti test` to start the MBTI quiz.")
    

#MBTI command to start the quiz
@mbti.command(name="test")
async def mbti_test(ctx):
    answers = []

    initial_embed = discord.Embed(
        title="MBTI Personality Test",
        description="Answer each question by choosing a number from 1 to 10.",
        color=discord.Color.blurple()
    )
    initial_embed.add_field(
        name="How to answer",
        value="1 = strongly disagree\n10 = strongly agree",
        inline=False
    )

    view = StartView(ctx.author, questions, answers, ctx)

    await ctx.send(
        "Ready to begin?",
        embed=initial_embed,
        view=view
    )


#MBTI command to compare MBTI types of two users (and compatibility)
@mbti.command(name="compare")
async def mbti_compare(ctx, member: discord.Member):
    if ctx.guild is None:
        await ctx.send("MBTI comparisons are only available in a server.")
        return

    author_mbti = get_server_member_mbti(ctx.guild.id, ctx.author.id)
    target_mbti = get_server_member_mbti(ctx.guild.id, member.id)

    if author_mbti is None:
        await ctx.send("You need to finish `!mbti test` first so I can compare your type.")
        return

    if target_mbti is None:
        await ctx.send(f"{member.display_name} has not completed `!mbti test` yet.")
        return

    embed = build_compatibility_embed(
        ctx.author.display_name,
        author_mbti,
        member.display_name,
        target_mbti
    )

    await ctx.send(embed=embed)


#MBTI command to view server's MBTI statistics
@mbti.command(name="stats")
async def mbti_stats(ctx):
    if ctx.guild is None:
        await ctx.send("Server MBTI statistics are only available in a server.")
        return

    stats = load_server_stats()
    guild_results = stats.get(str(ctx.guild.id), {})
    embed = build_server_stats_embed(ctx.guild.name, guild_results)

    await ctx.send(embed=embed)


#MBTI command to view personality card
@mbti.command(name="card")
async def mbti_card(ctx, mbti_type: str = None):
    if mbti_type is None:
        if ctx.guild is None:
            await ctx.send("MBTI cards are only available in a server unless you pass a type like `!mbti card INTJ`.")
            return

        mbti_type = get_server_member_mbti(ctx.guild.id, ctx.author.id)

        if mbti_type is None:
            await ctx.send("You need to finish `!mbti test` first so I can build your personality card.")
            return

    embed = build_personality_card_embed(mbti_type)
    await ctx.send(embed=embed)

bot.run(TOKEN)