from django.db import models


class Profession(models.Model):
    description = models.CharField(max_length=50)

    def __str__(self):
        return self.description


class DataSheet(models.Model):
    description = models.CharField(max_length=50)
    historical_data = models.TextField()

    def __str__(self):
        return self.description

class Customer(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    profession = models.ManyToManyField(Profession)
    data_sheet = models.OneToOneField(DataSheet, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    # http://localhost:8000/api/customers/?active=False -- status_message key 
    @property # dont need to do migrations if adding propertieies 
    # this add a new key depending on customers state 
    def status_message(self): 

        if self.active:
            return "Customer active"
        return "Customer not active"

    def num_professions(self):
        """
        return the number of professions associated with a specific customer 
        although we cannot return this as a field 
        this works closely with customerserializer in serializer.py
        """
        return self.profession.all().count()


    def __str__(self):
        return self.name


# dont think I need this part ... 
class Document(models.Model):
    PP = 'PP'
    ID = 'ID'
    OT = 'OT'

    DOC_TYPES = (
        (PP, 'Passport'),
        (ID, 'Identity Card'),
        (OT, 'Others')   
    )

    dtype = models.CharField(choices=DOC_TYPES, max_length=2)
    doc_number = models.CharField(max_length=50)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return self.doc_number