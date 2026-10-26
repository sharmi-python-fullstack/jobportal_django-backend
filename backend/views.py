from django.shortcuts import render
from rest_framework import generics, status 
from rest_framework.response import Response 
from .models import Application 
from .serializers import ApplicationSerializer, MyApplicationSerializer
# Create your views here.
from rest_framework.views import APIView 
from rest_framework.response import Response 
from rest_framework import status 
from rest_framework import generics, parsers 
from .serializers import UserSerializer 
from rest_framework.generics import ListCreateAPIView 
from rest_framework.generics import RetrieveAPIView 
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Job 
from .models import Resume 
from .filters import JobFilter 
from .serializers import JobSerializer
from .serializers import ResumeSerializer 
class RegisterView(APIView): 
    def post(self, request): 
        serializer = UserSerializer(data=request.data) 
        if serializer.is_valid(): 
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
class JobView(ListCreateAPIView): 
    queryset = Job.objects.all().order_by('-posted_at') 
    serializer_class = JobSerializer 
    permission_classes = [IsAuthenticatedOrReadOnly] 
    filterset_class = JobFilter# Allow read for all, create 
    def perform_create(self, serializer): 
        # Automatically set the recruiter to the current logged-in user 
        serializer.save(recruiter=self.request.user)
class JobDetailView(RetrieveAPIView): 
    queryset = Job.objects.all() 
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] 
class ResumeUploadView(generics.CreateAPIView): 
    queryset = Resume.objects.all() 
    serializer_class = ResumeSerializer 
    permission_classes = [IsAuthenticated] 
    parser_classes = [parsers.MultiPartParser, parsers.FormParser] 
    def perform_create(self, serializer): 
        # Link the resume to the current authenticated user 
        serializer.save(user=self.request.user)
class ApplyView(generics.CreateAPIView): 
    queryset = Application.objects.all() 
    serializer_class = ApplicationSerializer 
    permission_classes = [IsAuthenticated] 
    def create(self, request, *args, **kwargs): 
        job_id = request.data.get('job_id') 
        try:
         # Check if user has uploaded a resume 
            resume = Resume.objects.get(user=request.user) 
            # Prevent multiple applications for the same job 
            if Application.objects.filter(applicant=request.user, job_id=job_id).exists(): 
                return Response({'detail': 'You have already applied for this job.'}, 
status=status.HTTP_400_BAD_REQUEST) 
            serializer = self.get_serializer(data={'job': job_id}) 
            serializer.is_valid(raise_exception=True) 
            serializer.save(applicant=request.user, resume=resume) 
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        except Resume.DoesNotExist: 
            return Response({'detail': 'Please upload your resume first.'}, 
status=status.HTTP_400_BAD_REQUEST) 
class AppliedJobsView(generics.ListAPIView): 
    serializer_class = MyApplicationSerializer
    permission_classes = [IsAuthenticated] 
    def get_queryset(self): 
        # Return only the applications of the current user 
        return Application.objects.filter(applicant=self.request.user).order_by('applied_at')