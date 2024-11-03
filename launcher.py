from src.lib.bot import SCUFFBOT
import argparse

parser = argparse.ArgumentParser(description='Runs ScuffBot.')
parser.add_argument('--dev', action='store_true', help='Enable development mode.')
args = parser.parse_args()

bot = SCUFFBOT(args.dev)
bot.run()
