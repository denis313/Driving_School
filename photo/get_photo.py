from aiogram.types import FSInputFile

def get_photo(name):
    photo = FSInputFile(f'photo/{name}.png', filename=f'photo_{name}')
    return photo