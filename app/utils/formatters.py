def money_br(value):
    if value is None:
        return ''
    return f'R$ {float(value):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
