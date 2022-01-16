from app.db.table import karupu as model

print(model.User._meta.backward_fk_fields)
