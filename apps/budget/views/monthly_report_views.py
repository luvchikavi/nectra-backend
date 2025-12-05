# in backend/apps/budget/views/monthly_report_views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import MonthlyBudgetReport
from ..serializers import MonthlyBudgetReportSerializer
from ..services import MonthlyReportGenerator

class MonthlyBudgetReportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only viewset for retrieving Monthly Budget Reports.
    """
    serializer_class = MonthlyBudgetReportSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        """
        This view should return a list of all the reports
        for the project as determined by the project_id portion of the URL.
        """
        project_id = self.kwargs['project_pk']
        return MonthlyBudgetReport.objects.filter(project_id=project_id).order_by('-year', '-month')

    def retrieve(self, request, *args, **kwargs):
        """
        Allow retrieval by year and month, in addition to the default pk.
        """
        project_id = self.kwargs['project_pk']
        
        # Check if year and month are in the URL
        if 'year' in self.kwargs and 'month' in self.kwargs:
            year = self.kwargs['year']
            month = self.kwargs['month']
            try:
                report = MonthlyBudgetReport.objects.get(project_id=project_id, year=year, month=month)
                serializer = self.get_serializer(report)
                return Response(serializer.data)
            except MonthlyBudgetReport.DoesNotExist:
                return Response(
                    {"detail": f"No report found for {year}-{month}."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Fallback to default retrieve by pk
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['post'], url_path='generate-report')
    def generate_report(self, request, project_pk=None):
        """
        An action to manually trigger the generation of a report for a specific month.
        Expects 'year' and 'month' in the request body.
        This is useful for testing and back-filling old data.
        """
        year = request.data.get('year')
        month = request.data.get('month')

        if not year or not month:
            return Response(
                {"detail": "Both 'year' and 'month' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            project = self.get_queryset().model.project.field.related_model.objects.get(pk=project_pk)
            generator = MonthlyReportGenerator(project=project, year=int(year), month=int(month))
            report = generator.generate_report()
            serializer = self.get_serializer(report)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
