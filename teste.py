import bcrypt
senha = '2702'
senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
print(senha_hash)