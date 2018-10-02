
from rest_framework import serializers
from .models import Customer, Profession, DataSheet, Document

class DataSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSheet
        fields = ('id', 'description', 'historical_data')


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ('id', 'description')



# Serializers define the API representation.
class CustomerSerializer(serializers.ModelSerializer):

    # connects to num_professions in models.py 
    # when you cann serializerMethodField()... django expect you to define a method with same name prepended with get_
    # and add to fields ...
    num_professions = serializers.SerializerMethodField()

    # for foreign key relationships -- we get string that represents that field -- changes the id to the actual text 
    # data_sheet = serializers.StringRelatedField()

    # this is a manytomany relationships -- needs to be included in fields in meta class 
    # variable name here needs to match model column name in fields 
    profession = serializers.StringRelatedField(many=True)
    document_set = serializers.StringRelatedField(many=True) # for foreign key relatipnship 

    # this is for if we EXPLICITLY want primary key field of data ... 
    #data_sheet = serializers.PrimaryKeyRelatedField(read_only=True) # need to pass many=True if mulitple objects 

    # nested serializer -- avoid doing 1 extra request but have much bigger json 
    data_sheet  =  DataSheetSerializer()
    #profession = ProfessionSerializer(many=True)

    class Meta:
        model = Customer
        fields = ('id', 'name', 'address', 'profession', 'data_sheet', 'active', 'status_message', 'num_professions', 'document_set')

    def get_num_professions(self, obj):
        """
        how we access a method inside a model when it IS NOT  a @property
        """
        return obj.num_professions()

    # def get_data_sheet(self, obj):
    #     return obj.data_sheet.description







class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ('id', 'description')









class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('id', 'dtype', 'doc_number', 'customer')



