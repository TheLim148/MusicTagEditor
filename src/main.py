import tags_editor
import asyncio

while True:
    choose = int(input("\n1 - да\n~$ "))

    match(choose):
        case 1:
            asyncio.run(tags_editor.main())
            break
        case 2:
            print("Поки!")
            break