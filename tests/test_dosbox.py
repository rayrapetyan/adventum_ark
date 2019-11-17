from runners.dosbox import DosBox

def test_run():
    db = DosBox("fable")
    db.run()
