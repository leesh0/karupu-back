from faker.factory import Factory


def get_faker():
    Faker = Factory.create
    faker = Faker(locale="ja-jp")
    faker.seed(0)
    return faker
