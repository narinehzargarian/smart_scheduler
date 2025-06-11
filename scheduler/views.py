from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from studies.models import Task, Course


class PlanAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Fetch user tasks and courses
        tasks = Task.objects.filter(owner=request.user)
        # Run the scheduler algorithm 
        # TODO: implement the actual scheduling logic
        # plan = generate_study_plan(tasks, request.user)
        plan = [
            {
                'title': t.name,
                'start': t.due_date,
                'end': t.due_date,
                'day': t.due_date.strftime('%A'),
            } for t in tasks
        ]

        return Response(plan) # Return the plan as JSON
        