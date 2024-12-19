import bcrypt

def gerar_hash_senha(senha):
    # Gera um salt aleatório
    salt = bcrypt.gensalt()
    # Gera o hash da senha com o salt
    hash_senha = bcrypt.hashpw(senha.encode('utf-8'), salt)
    return hash_senha


senha = "Aec91a427r02j03b"
hash_senha = gerar_hash_senha(senha)
hash_senha = hash_senha.decode('utf-8')
print("Hash gerado:", hash_senha)