import MusicTags as MT

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