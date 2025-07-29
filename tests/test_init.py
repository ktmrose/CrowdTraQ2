from init import generate_room_code

def test_generate_room_code_length():
    code = generate_room_code(6)
    assert len(code) == 6
    assert code.isupper()