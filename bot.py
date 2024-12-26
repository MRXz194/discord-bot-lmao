# Author name: MRX
# Date and time: 12/26/2024 09:13 AM
# Day: Thursday
# Description: A simple Discord bot to play lo? game :))
# github: https://github.com/MRXz194   Discord: kz5198
import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()

# setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# data storage 
player_balances = {}

class TaiXiu:
    def __init__(self):
        self.minimum_bet = 1000
        self.maximum_bet = 100000

    def roll_dice(self):
        return [random.randint(1, 6) for _ in range(3)]

    def get_result(self, dice):
        total = sum(dice)
        if total >= 11:
            return "Tài", total  
        else:
            return "Xỉu", total  

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='balance')
async def balance(ctx):
    """Check your current balance"""
    user_id = str(ctx.author.id)
    if user_id not in player_balances:
        player_balances[user_id] = 10000  
    
    embed = discord.Embed(
        title="💰 Balance Information",
        color=discord.Color.gold()
    )
    embed.add_field(
        name=f"{ctx.author.display_name}'s Balance",
        value=f"```{player_balances[user_id]:,} coins```",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command(name='topup')
@commands.has_permissions(administrator=True)
async def topup(ctx, member: discord.Member, amount: int):
    """Add balance to a user's account (Admin only)"""
    if amount <= 0:
        await ctx.send("❌ Amount must be positive!")
        return

    user_id = str(member.id)
    if user_id not in player_balances:
        player_balances[user_id] = 0

    player_balances[user_id] += amount
    
    embed = discord.Embed(
        title="💎 Top Up Successful",
        color=discord.Color.green()
    )
    embed.add_field(
        name="Recipient",
        value=member.mention,
        inline=True
    )
    embed.add_field(
        name="Amount Added",
        value=f"{amount:,} coins",
        inline=True
    )
    embed.add_field(
        name="New Balance",
        value=f"{player_balances[user_id]:,} coins",
        inline=False
    )
    await ctx.send(embed=embed)

@topup.error
async def topup_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ ",
            description="Only administrators ",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command(name='delbalance')
@commands.has_permissions(administrator=True)
async def delbalance(ctx, member: discord.Member):
    """Reset a user's balance to 0 (Admin only)"""
    user_id = str(member.id)
    if user_id in player_balances:
        old_balance = player_balances[user_id]
        player_balances[user_id] = 0
        
        embed = discord.Embed(
            title="💰 Balance Reset",
            description=f"Reset balance for {member.mention}",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Old Balance",
            value=f"{old_balance:,} coins",
            inline=True
        )
        embed.add_field(
            name="New Balance",
            value="0 coins",
            inline=True
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"{member.mention} has no balance record.")

@delbalance.error
async def delbalance_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Only administrators can use this command!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command(name='taixiu')
async def taixiu(ctx, choice: str, bet: int):
    """Play Tài Xỉu. Usage: !taixiu <tai/xiu> <bet amount>"""
    user_id = str(ctx.author.id)
    
    if user_id not in player_balances:
        player_balances[user_id] = 10000

    # choice
    if choice.lower() not in ['tai', 'xiu']:
        embed = discord.Embed(
            title="❌ Invalid Choice",
            description="Use 'tai' for Tài (High) or 'xiu' for Xỉu (Low)",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    #bet
    if bet < 1000:
        embed = discord.Embed(
            title="❌ Invalid Bet",
            description="Minimum bet is 1,000 coins!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    if bet > player_balances[user_id]:
        embed = discord.Embed(
            title="❌ Insufficient Balance",
            description=f"You only have {player_balances[user_id]:,} coins!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # role dice :)))
    game = TaiXiu()
    dice = game.roll_dice()
    result, total = game.get_result(dice)
    
    # Convert to right format
    player_choice = "Tài" if choice.lower() == "tai" else "Xỉu"

    # Calculate win
    if player_choice == result:
        player_balances[user_id] += bet
        color = discord.Color.green()
        outcome = f"🎉 You won **{bet:,}** coins!"
    else:
        player_balances[user_id] -= bet
        color = discord.Color.red()
        outcome = f"💔 You lost **{bet:,}** coins!"

    
    dice_emojis = {
        1: "1️⃣",
        2: "2️⃣",
        3: "3️⃣",
        4: "4️⃣",
        5: "5️⃣",
        6: "6️⃣"
    }
    
    dice_display = " ".join(dice_emojis[d] for d in dice)
    
    embed = discord.Embed(
        title="🎲 Tài Xỉu Result",
        color=color
    )
    embed.add_field(
        name="Dice Roll",
        value=f"{dice_display} = {total}",
        inline=False
    )
    embed.add_field(
        name="Result",
        value=result,
        inline=True
    )
    embed.add_field(
        name="Your Choice",
        value=player_choice,
        inline=True
    )
    embed.add_field(
        name="Outcome",
        value=outcome,
        inline=False
    )
    embed.add_field(
        name="New Balance",
        value=f"```{player_balances[user_id]:,} coins```",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='help')
async def help_command(ctx):
    """Display beautiful help information"""
    embed = discord.Embed(
        title="🎲 Tài Xỉu Game Commands",
        description="Welcome to Tài Xỉu ",
        color=discord.Color.blue()
    )

    # Game Rules
    embed.add_field(
        name="📜 Game Rules",
        value="• **Tài (High)**: Total of dice is 11 or higher\n• **Xỉu (Low)**: Total of dice is 10 or lower",
        inline=False
    )

    # Commands
    embed.add_field(
        name="🎮 Game Commands",
        value="• `!taixiu <tai/xiu> <bet>` - Place your bet\n  Example: `!taixiu tai 1000`",
        inline=False
    )

    # Balance Comm
    embed.add_field(
        name="💰 Balance Commands",
        value="• `!balance` - Check your current balance",
        inline=False
    )

    # Admin 
    embed.add_field(
        name="👑 Admin Commands",
        value="• `!topup @user <amount>`\n• `!delbalance @user` - Reset user's balance to 0",
        inline=False
    )

    
    embed.set_footer(text="Good luck 🍀")
    
    await ctx.send(embed=embed)

bot.run(os.getenv('DISCORD_TOKEN'))
