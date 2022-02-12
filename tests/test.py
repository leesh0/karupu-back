from pydantic import PostgresDsn

$mt:
    read($$)




$mt(
    new_web
    db = PostgresDsn
)


$mt(
    add 1, 2
    mul 3
    ret x
)


def user():
    return 1

$mt[user].routes:
    user:{
        "yser"
    }
