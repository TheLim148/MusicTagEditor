import MusicTagsEditor as MT
import Parse
import asyncio

while True:
    choose = int(input("\n1 - да\n~$ "))

    match(choose):
        case 1:
            asyncio.run(MT.main())
            break
        case 2:
            print("Поки!")
            break
        case 3:
            Parse.printData("data.json")
            break