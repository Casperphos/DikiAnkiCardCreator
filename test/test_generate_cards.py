from create_cards_and_export_csv import *


def test_generate_cards_01():
    generate_cards("./test/_dk_test01.txt")

    with open("anki_cards.csv", 'r', encoding="utf-8") as f:
        lines = f.read().splitlines()

    lines = '\n'.join(lines)
    excepted_output = 'Expression;Meaning;Reading\n'\
        'get flak | get the flak | flak | flack | flack | flak;"1. zostać ostro skrytykowanym\n'\
        '2. ogień krytyki\n'\
        '3. ostra krytyka\n'\
        '4. ogień przeciwlotniczy\n'\
        '5. dezaprobata\n'\
        '6. reklamować produkt lub usługę";<img src="flak.png"> <img src="flack.png"> <img src="flack.png"> <img src="flak.png">'

    assert lines == excepted_output
