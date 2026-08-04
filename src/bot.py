import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from questions import questions
from scoring import calculate_mbti
from results import build_result_embed

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

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

# MBTI command to start the test
@bot.command()
async def mbti(ctx):
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

#MBTI command to view server MBTI statistics

#MBTI command to compare MBTI types of two users (and compatibility)

#MBTI command to view personality card
bot.run(TOKEN)