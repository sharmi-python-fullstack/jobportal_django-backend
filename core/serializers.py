from rest_framework import serializers 
from .models import Application, Resume
from django.contrib.auth.models import User 
class UserSerializer(serializers.ModelSerializer): 
    password = serializers.CharField(write_only=True) 
    class Meta: 
        model = User 
        fields = ('username', 'password', 'email') 
    def create(self, validated_data): 
        user = User.objects.create_user( 
            username=validated_data['username'], 
            email=validated_data['email'], 
            password=validated_data['password'] 
        ) 
        return user
from rest_framework import serializers 
from .models import Job 
class JobSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Job 
        fields = '__all__' # Expose all fields 
        read_only_fields = ('recruiter',) 
class ResumeSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Resume 
        fields = ('id', 'file', 'uploaded_at', 'user')
        read_only_fields = ('user',)  
class ApplicationSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Application 
        fields = '__all__' 
        read_only_fields = ('applicant', 'resume') 
class MyApplicationSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)

    class Meta:
        model = Application
        fields = ('id', 'job', 'applied_at')
# Recruiter is automatically set in the view