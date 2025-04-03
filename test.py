import jwt
print(jwt.encode({'user': 'test'}, 'secret', algorithm='HS256'))