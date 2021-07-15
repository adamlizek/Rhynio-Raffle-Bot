class Email:
    def __init__(self, email, firstname=None, lastname=None):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname

        self.isNameEnabled = False

        if self.firstname is not None and self.lastname is not None:
            self.isNameEnabled = True

    def nameEnabled(self):
        return self.isNameEnabled

    def get_email(self):
        return self.email

    def get_first_name(self):
        return self.firstname

    def get_last_name(self):
        return self.lastname
