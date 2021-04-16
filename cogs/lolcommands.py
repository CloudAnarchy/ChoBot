from discord.ext import commands
from riot_api.riot_api import RiotApi
import discord
import utils.utils as ut
from web_crawler.lol_crawlers.lol_crawler import LolCrawler


class LolCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.riot_api = RiotApi()
        self.lol_crawler = LolCrawler()

    @staticmethod
    def create_build_embed(build, position):
        em = discord.Embed(description=f"{build.win_ratio} {build.champ_tier}", color=0x7C45A1)
        em.set_author(name=build.champ_name, icon_url=build.champ_icon)
        em.set_thumbnail(url=build.champ_icon)

        # TODO Future Market
        primaries = "".join([f' {ut.fr(ut.rspaces(prune.replace(":", "").lower()))} ' for prune in build.runes.primaries])
        secondaries = "".join([f' {ut.fr(ut.rspaces(srune.replace(":", "").lower()))} ' for srune in build.runes.secondaries])
        stats = "".join([f" {ut.fr(ut.rspaces(stat.lower()))} " for stat in build.runes.stats])

        em.add_field(name=f"{build.runes.types[0]} {ut.fr(build.runes.types[0].lower())} ", value=f"{ut.fr(ut.rspaces(build.runes.keystone.lower()))}  ||  {primaries}", inline=True)
        em.add_field(name=f"{build.runes.types[1]} {ut.fr(build.runes.types[1].lower())} ", value=secondaries, inline=True)
        em.add_field(name="Skill Priotity", value="".join([spell + " -> " for spell in build.skills_priority]), inline=False)
        em.add_field(name="Stats", value=stats, inline=True)
        em.add_field(name="Summoners", value=ut.fr(build.runes.summoners[0][0].lower()) + " " + ut.fr(build.runes.summoners[1][0].lower()), inline=True)
        counters = ""
        for ctr in build.counters:
            tmp = ctr.split(" Win Ratio ")
            if len(tmp) > 1:
                counters += f"**{tmp[0]}** - {tmp[1]} Win Ratio\n"

        em.add_field(name="Main Counters", value=counters, inline=False)
        em.set_footer(text=f"This build is for {build.lane} {build.champ_name}")
        return em

    @commands.command(pass_context=True)
    async def build(self, ctx):
        msgs = ctx.message.content.split()

        # When not enough arguments were passed
        if len(msgs) <= 1:
            return

        if msgs[1].lower() in ["top", "jungle", "mid", "middle", "bot", "adc", "support", "supp"]:
            if msgs[1] in ["mid", "middle"]:
                lane = "middle"
            elif msgs[1] in ["bot", "adc"]:
                lane = "adc"
            elif msgs[1] in ["support", "supp"]:
                lane = "support"

            lane = msgs[1]
            offset = 2
        else:
            lane = ""
            offset = 1

        champion_name = "".join(msgs[offset:])
        champion = await self.lol_crawler.fetch_champion(champion_name, lane)
        embed = LolCommands.create_build_embed(champion, lane)
        # embed = LolCommands.create_build_embed(None, None)
        await ctx.send(embed=embed)
        # em = discord.Embed(title="Cho Gath", description="Mid-lane Build")
        # em.add_field(name="", value="", inline=True)
        # await ctx.send(embed=em)
        return

    @staticmethod
    def create_summoner_embed(summoner, n_champs=3):
        em = discord.Embed(
            title=summoner.elo, description=summoner.win_ratio, color=0xF3841B
        )
        em.set_author(name=summoner.name, icon_url=summoner.profile_icon)
        em.set_thumbnail(url=summoner.elo_icon)
        for champ in summoner.most_played_champs[0:n_champs]:
            em.add_field(
                name=champ.name + f" ({champ.games})",
                value=f"**CS:** {champ.cs}  **KDA:** {champ.kda}  **WR:** {champ.win_ratio}",
                inline=False,
            )
        em.set_footer(text=summoner.ladder_rank)
        return em

    @commands.command(pass_context=True)
    async def lol(self, ctx):
        msgs = ctx.message.content.split()

        # When not enough arguments were passed
        if len(msgs) <= 1:
            return

        summoner_name, region = ut.parse_summoner_name_and_region(
            msgs, self.lol_crawler.regions
        )
        # Once champion.gg api is back we may use this again.
        # try:
        #     summoner = await self.riot_api.fetch_summoner(summoner_name, region)
        # except Exception as e:
        #     print(e)
        #     print("Riot api fetch failed, try web-crawling from opgg.")

        summoner = await self.lol_crawler.fetch_summoner(summoner_name, region)
        # Format them into emded
        em = LolCommands.create_summoner_embed(summoner)

        # Send the embed to the region.
        await ctx.send(content=None, embed=em)


def setup(bot):
    bot.add_cog(LolCommands(bot))
