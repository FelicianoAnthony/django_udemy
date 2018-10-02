from rest_framework import viewsets
from .models import Customer, Profession, DataSheet, Document
from .serializers import CustomerSerializer, ProfessionSerializer, DataSheetSerializer, DocumentSerializer
from rest_framework.response import Response
from django.http import HttpResponseNotAllowed
from rest_framework.status import HTTP_200_OK

from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter

# ViewSets define the view behavior.
class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    # in /customers/ adds a button called filter that filters like this http://localhost:8000/api/customers/?name=Billzzzz 
    # bascially the same thing we did in get_queryset except we dont have to code it all 
    # BUT YOU NEED TO MATCC FIELD EXACTLY -- CANT DO STRING CONTAINS ... 
    # filter_fields = ('name', )

    # search on specific fields ... less restrvve than DjangoBackendsFilter... 
    # http://www.django-rest-framework.org/api-guide/filtering/#searchfilter
    filter_backends = (SearchFilter,OrderingFilter)
    # can use foregin keys by appending name of table before field name ... 
    # http://localhost:8000/api/customers/?search=001 -- finds 001 in historical data field ... 
    # default search contains word but we can be more strict...
    search_fields = ('name', 'address', 'data_sheet__historical_data')
    # search_fields = ('=name') # is for an exact match on name ... 

    # http://localhost:8000/api/customers/?ordering=name -- order by name  
    # http://localhost:8000/api/customers/?ordering=-name -- not - before name -- descending order 
    ordering_fields = ('name', 'id',) # OrderingFilter 
    # ordering_fields = '__all__' # order by any field 
    # ordering = ('name',) # for defualt ordering if client doesnt pass an ordering 


    # can do stuff like this http://localhost:8000/api/customers/Jeff/ & return data 
    # but if lookup finds mroe than 1 object then an exception will be raised  
    lookup_field = 'name' # but field from class in models.py  should be unique ... 
    
    # override default queryset behavior
    def get_queryset(self):
        """
        this gets data from DB before it's even passed to HTTP verbs... 
        http://localhost:8000/api/customers/?id=3&active=False
        """


        # http://localhost:8000/api/customers/?address=num contains "num" inside address
        # search for all addresses that contain num & stauts=true
        # http://www.django-rest-framework.org/api-guide/filtering/#filtering-against-the-url
        address = self.request.query_params.get('address', None)
        # import pdb; pdb.set_trace()
        if self.request.query_params.get('active') == 'False':
            status=False
        else:
            status=True

        if address:
            customers = Customer.objects.filter(address__icontains=address, active=status)
        else:
            customers = Customer.objects.filter(active=status)
        return customers



        # mid level example 
        # # import pdb; pdb.set_trace()
        # _id = self.request.query_params.get('id', None)
        # status = True if self.request.query_params['active'] == 'True' else False

        # if _id:
        #     customers = Customer.objects.filter(id=_id, active=status)
        # else:
        #     customers = Customer.objects.filter(active=status)
        # return customers


        # simplest example of querying before passing to http verbs
        # active_customers = Customer.objects.filter(active=False)
        # return active_customers

    # override defualt list behavior -- works on this endpoint http://10.157.164.235:8000/api/customers/
    # def list(self, request, *args, **kwargs):
    #     """
    #     override GET ALL behavior
    #     list all resources in DB but you can apply your own filtering logic
    #     """
    #     # import pdb; pdb.set_trace() # n to go to next line then serializer.data 

    #     #this is to filter by ID of customer
    #     # customers = Customer.objects.filter(id=3)
    #     # serializer = CustomerSerializer(customers, many=True)
    #     # return Response(serializer.data)

    #     customers = self.get_queryset()
    #     serializer = CustomerSerializer(customers, many=True)
    #     return Response(serializer.data)


    # pdb works when you go to http://10.157.164.235:8000/api/customers/1 url -- make sure resource(pk) is there
    def retrieve(self, *args, **kwargs):
        """
        override GET BY PK behavior 
        look up a resource by pk & serialize it -- method it's overwriting abstracts this process
        """
        #import pdb; pdb.set_trace() # args kwargs

        obj  = self.get_object() # get_object is a django method to lookup object in db by pk 
        serializer = CustomerSerializer(obj)
        return Response(serializer.data) # dont use many cuz were getting only 1 object since pk 

        # return HttpResponseNotAllowed('not allowed')


    def create(self, request, *args, **kwargs):
        """
        POST method 
        1. retrieve data from request.data
        2. remove fields from request.data & map them correctly to obj
        3. need to lookup params in requests.data that have foreign relationships
        4. add this to the customer object & save 
        5. return serializers 

        -- validation would occur here but not written - 
        """

        data = request.data
        customer = Customer.objects.create(
            name=data['name'], 
            address=data['address'],
            data_sheet_id=data['data_sheet'],
        ) 
        prof = Profession.objects.get(id=data['profession'])

        customer.profession.add(prof)
        customer.save()

        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        note that when you update you may need to delete previous data depending on how you want the update to happen
        - which is why we loop over all professions associated with an ID & remove it before updating to the new one -- can have ...
        ... this behavior on any field 
        """

        # gets your customer object that corresponds to PK -- can also use kwargs -- see pdb trace in retrieve method 
        # or Customer.objects.get(pk=kwargs['id?'])
        customer = self.get_object()

        data=request.data
        customer.name = data['name']
        customer.address = data['address']
        customer.data_sheet_id = data['data_sheet']

        # if we didnt do this then object would have a list of profession if updated progession is different than progfession in DB already 
        for p in customer.profession.all():
            customer.profession.remove(p)

        prof = Profession.objects.get(id=data['profession'])
        customer.profession.add(prof)
        customer.save()

        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    #http://localhost:8000/api/customers/3/ patch   
    def partial_update(self, request, *args, **kwargs):
        """
        update one field in DB -- we dont know which arg we're gonna get so need to keep original entry if not received other fields   
        """

        customer = self.get_object()

        # if customer doesnt pass name then we keep the original name in DB 
        customer.name = request.data.get('name', customer.name)
        customer.address = request.data.get('address', customer.address) 
        customer.data_sheet_id = request.data.get('data_sheet_id', customer.data_sheet_id) 
        customer.save()

        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):

        customer = self.get_object()
        customer.delete()

        # this is how you'd add custom status codes 
        #return Response('removed', status=HTTP_200_OK)

    # ... but anything with @action is a GET request even tho we're doing a POST 
    # this is for custom actions/ functions I want that arent specific to HTTP verbs
    # no detail=True means it'd be applied to all resources at endpoint??
    @action(detail=True) # means this action wil be executed wehn looking into detail of a source ... customer/<pk>/deactivate
    def deactivate(self, request, **kwargs):
        # deactivat specific customer 

        customer = self.get_object()
        customer.active = False 
        customer.save()

        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    #http://localhost:8000/api/customers/deactivate_all/ -- GET request
    @action(detail=False)
    def deactivate_all(self, request, **kwargs):

        customers = self.get_queryset()
        customers.update(active=False)
        #customers.save() why save not neeeded?
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    #http://localhost:8000/api/customers/activate_all/ -- GET request
    @action(detail=False)
    def activate_all(self, request, **kwargs):

        customers = self.get_queryset()
        customers.update(active=True)
        #customers.save() why save not neeeded?
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)



    # http://localhost:8000/api/customers/change_status/
    # another way to do http://localhost:8000/api/customers/activate_all/  -- specify specific verbs to accept 
    # this turns active to opposite of whatever it is in DB 
    @action(detail=False, methods=['POST'])
    def change_status(self, request, **kwargs):
        # import pdb; pdb.set_trace()
        status = True if request.data['active'] == 'True' else False



        customers = self.get_queryset()
        customers.update(active=status)
        #customers.save() #why save not neeeded?
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)



    


    


class ProfessionViewSet(viewsets.ModelViewSet):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer


class DataSheetViewSet(viewsets.ModelViewSet):
    queryset = DataSheet.objects.all()
    serializer_class = DataSheetSerializer




class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer