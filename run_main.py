import asyncio
from api.gatherer import Gatherer
from api.fetcher import Fetcher
from bot.bot import BotRunner


def main():
    while True:
        print(
            "\nWhat do you want to run?"
            "\n1: Osu API data fetcher (menu)"
            "\n2: Discord bot"
            "\n3: Fetcher"
            "\nQ: Quit"
        )
        choice = input("> ").strip().lower()

        if choice == "1":
            # This itself has its own menu and loop
            asyncio.run(Gatherer().run())
        elif choice == "2":
            BotRunner().run()
        elif choice == "3":
            asyncio.run(Fetcher().run())
        elif choice == "q":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()