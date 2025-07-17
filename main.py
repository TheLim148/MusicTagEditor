import MusicTags as MT
import JSONParse as JSParse

while True:
    choose = int(input("\n1 - да\n~$ "))

    match(choose):
        case 1:
            dir_from = input("Введите исходную директорию: ")
            dir_to = input("Введите конечную директорию: ")
            MT.fromRawMp3ToClean(dir_from, dir_to)
        case 2:
            print("Поки!")
            break
        case 3:
            JSParse.printData("data.json")
            break