from django.db import models


class EmailInbox(models.Model):
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    imap_host = models.CharField(max_length=255)
    smtp_host = models.CharField(max_length=255)
    settings = models.JSONField(null=True, default=None)

    @property
    def user(self):
        return self.username.split("@")[0]

    @property
    def domain(self):
        return self.username.split("@")[1]


class GarminConversations(models.Model):
    inbox = models.ForeignKey(EmailInbox, on_delete=models.PROTECT)
    selector = models.CharField(max_length=255, null=True, default=None)
    reply_url = models.CharField(max_length=255, null=True, default=None)

    @property
    def user(self):
        if self.selector:
            return f"{self.inbox.user}+{self.selector}"
        return self.inbox.user

    @property
    def address(self):
        return f"{self.user}@{self.inbox.domain}"


class Request(models.Model):
    conversation = models.ForeignKey(GarminConversations, on_delete=models.PROTECT)
    created = models.DateField(auto_created=True, auto_now=True)
    status = models.IntegerField(choices=((0, "New"), (1, "Pending"), (2, "Done"), (3, "Failed")), default=0)
    action = models.IntegerField(choices=((0, "Ping"), (1, "SailDocs - GRIB"), (2, "SailDocs - Spot Forecast")))
    input = models.JSONField()


class Response(models.Model):
    conversation = models.ForeignKey(GarminConversations, on_delete=models.PROTECT)
    request = models.ForeignKey(Request, on_delete=models.PROTECT, null=True)
    created = models.DateField(auto_created=True, auto_now=True)
    status = models.IntegerField(choices=((0, "Pending"), (1, "Sent"), (2, "Failed")), default=0)
    message = models.CharField(max_length=160)


class ScheduledRequest(models.Model):
    conversation = models.ForeignKey(GarminConversations, on_delete=models.PROTECT)
    group = models.IntegerField(choices=((0, "Daily"), (1, "12 hours"), (2, "6 hours")), default=0)
    action = models.IntegerField(choices=((0, "Ping"), (1, "SailDocs - GRIB")))
    input = models.JSONField()
