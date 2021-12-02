from app.db.table.karupu import Categories, Project, User
from tortoise import run_async

from faker.factory import Factory

Faker = Factory.create
faker = Faker(locale="ja-jp")
faker.seed(0)


def create_user():
    profile = faker.profile()
    new_user = User(
        username=profile["username"],
        nickname=profile["name"],
        email=profile["mail"],
        avatar=None,
        bio=None,
        onboarded=True,
        is_staff=True,
        is_admin=False,
    )
    run_async(new_user.save())
    return new_user


def create_users(n=3):
    new_users = []
    for i in range(0, n):
        profile = faker.profile()
        new_users.append(
            User(
                username=profile["username"],
                nickname=profile["name"],
                email=profile["mail"],
                avatar=None,
                bio=None,
                onboarded=True,
                is_staff=True,
                is_admin=False,
            )
        )
    run_async(User.bulk_create(new_users))
    return new_users


def create_admin():
    profile = faker.profile()
    new_admin = User(
        username=profile["username"],
        nickname=profile["name"],
        email=profile["mail"],
        avatar=None,
        bio=None,
        onboarded=True,
        is_staff=True,
        is_admin=True,
    )
    run_async(new_admin.save())
    return new_admin


def create_projects(user, n=3):
    datas = [
        (faker.sentence(), faker.sentence(), faker.paragraph(nb_sentences=5), Categories.WEB)
        for i in range(0, n)
    ]
    creation = [
        Project(user=user, icon="https://naver.com", category=c, title=s, desc=d, readme=p)
        for (s, d, p, c) in datas
    ]
    run_async(Project.bulk_create(creation))
    return creation


def init_db_datas():
    admin = create_admin()
    user = create_user()
    example_users = create_users(5)
    create_projects(admin, 5)
    create_projects(user, 5)
