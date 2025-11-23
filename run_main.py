import asyncio
from api.gatherer import OsuDataFetcher
from bot.bot import BotRunner


def main():
    while True:
        print(
            "\nWhat do you want to run?"
            "\n1: Osu API data fetcher (menu)"
            "\n2: Discord bot"
            "\nQ: Quit"
        )
        choice = input("> ").strip().lower()

        if choice == "1":
            # This itself has its own menu and loop
            asyncio.run(OsuDataFetcher().run())
        elif choice == "2":
            BotRunner().run()
        elif choice == "q":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()