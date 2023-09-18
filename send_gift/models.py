from django.db import models


class TypeAccount(models.Model):
    type_name = models.CharField(unique=True, max_length=200)

    def __str__(self):
        return self.type_name


class Game(models.Model):
    name = models.CharField(unique=True, max_length=200)
    game_id = models.CharField(unique=True, max_length=200)
    type = models.ForeignKey(TypeAccount, on_delete=models.CASCADE)
    game_link = models.CharField(max_length=200)
    game_sub_id = models.CharField(max_length=200)
    amount = models.FloatField(default=0)

    def __str__(self):
        return self.name


class Account(models.Model):
    login = models.CharField(unique=True, max_length=200)
    password = models.CharField(max_length=200)
    type = models.ForeignKey(TypeAccount, on_delete=models.CASCADE)
    counter = models.PositiveIntegerField(default=0)
    status = models.BooleanField(default=True)
    balance = models.FloatField(default=0)

    def __str__(self):
        return self.login


class Code(models.Model):
    code = models.CharField(unique=True, max_length=200)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    status = models.CharField(max_length=200)
    link = models.CharField(max_length=200)
    error = models.TextField()
    counter = models.IntegerField(default=0)
    account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.code


class Interhub(models.Model):
    token = models.TextField(unique=True)
    balance = models.FloatField(default=0)


class Setting(models.Model):
    digi_code = models.TextField(unique=True)
    seller_id = models.IntegerField()
    course = models.FloatField(default=0)


class Log(models.Model):
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)


def get_key(key: str):
    try:
        return Code.objects.filter(code=key)[0]
    except IndexError:
        return False


def get_game(key: str):
    try:
        return Game.objects.filter(game_id=key)[0]
    except IndexError:
        return False


def get_account(account_type):
    try:
        return Account.objects.filter(type=account_type, counter__lt=10)[0]
    except IndexError:
        return False


def get_setting():
    return Setting.objects.all().last()
