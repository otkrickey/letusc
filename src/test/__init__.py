def test():
    # test_v2_CheckAccount()
    # test_v2_LetusPage_Manager_pull()
    # test_v2_LetusPage_Manager_push()
    # test_v2_LetusContent_Manager_push()
    pass


def test_v2_CheckAccount():
    from src.Letus.v2.LetusAccount import LetusAccount
    from src.service.v2.checkAccount import checkAccount

    LA = LetusAccount("601235188571176961")
    checkAccount(LA)


def test_v2_LetusPage_Manager_pull():
    from src.Letus.v2.LetusPage import LetusPage
    from src.database.v2.PageManager import PageManager

    LP = LetusPage("2023:course:126936")
    PM = PageManager(LP)
    PM.pull()


def test_v2_LetusPage_Manager_push():
    from src.Letus.v2.LetusPage import LetusPage
    from src.database.v2.PageManager import PageManager

    LP = LetusPage(
        "2023:course:126936:1060750704626643034:1074363874112983092:601235188571176961"
    )
    PM = PageManager(LP)
    PM.push()


def test_v2_LetusContent_Manager_push():
    from src.Letus.v2.LetusPage import LetusPage
    from src.Letus.v2.LetusContent import LetusContentV2
    from src.database.v2.ContentManager import ContentManagerV2

    LP = LetusPage(
        "2023:course:126936:1060750704626643034:1074363874112983092:601235188571176961"
    )
    LC = LetusContentV2(LP)
    CM = ContentManagerV2(LC)
    CM.push()

    # DEBUG
    print(LP.__dict__)
    print(LP.LA.__dict__)
    print(CM.LC.__dict__ | {"document": None})
    print(CM.LCp.__dict__ | {"document": None})
    for section in LC.sections:
        print(section.__dict__)
        for module in section.modules:
            print(module.__dict__)
