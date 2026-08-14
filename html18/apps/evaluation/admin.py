from django.contrib import admin
from .models import Machine, Evaluation, AHPMatrix, EntropyWeight, ComprehensiveWeightResult, UserEvaluationResult, DataOperationLog


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'model', 'machine_type', 'created_by', 'created_at']
    list_filter = ['machine_type', 'created_at']
    search_fields = ['name', 'model', 'report_number']
    readonly_fields = ['created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            user_profile = request.user.userprofile
            if user_profile.is_admin():
                return qs
            else:
                return qs.filter(created_by=request.user)
        except:
            return qs.filter(created_by=request.user)


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['id', 'machine', 'evaluator', 'total_score', 'grade', 'evaluation_date']
    list_filter = ['grade', 'evaluation_date']
    search_fields = ['machine__name', 'evaluator__username']
    readonly_fields = ['evaluation_date']


@admin.register(AHPMatrix)
class AHPMatrixAdmin(admin.ModelAdmin):
    list_display = ['id', 'path', 'evaluator', 'is_consistent', 'submitted_at']
    list_filter = ['is_consistent', 'submitted_at']
    search_fields = ['path', 'evaluator__username']
    readonly_fields = ['submitted_at']


@admin.register(EntropyWeight)
class EntropyWeightAdmin(admin.ModelAdmin):
    list_display = ['id', 'machine', 'evaluator', 'precision_type', 'calculated_at']
    list_filter = ['precision_type', 'calculated_at']
    search_fields = ['machine__name', 'evaluator__username', 'total_id']
    readonly_fields = ['calculated_at', 'updated_at', 'version']


@admin.register(ComprehensiveWeightResult)
class ComprehensiveWeightResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'machine', 'evaluator', 'total_score', 'grade', 'calculated_at']
    list_filter = ['grade', 'calculated_at']
    search_fields = ['machine__name', 'evaluator__username']
    readonly_fields = ['calculated_at']


@admin.register(UserEvaluationResult)
class UserEvaluationResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'machine', 'evaluator', 'total_score', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['machine__name', 'evaluator__username']
    readonly_fields = ['created_at', 'updated_at']


# @admin.register(DataOperationLog)
# class DataOperationLogAdmin(admin.ModelAdmin):
#     list_display = ['id', 'action', 'table_name', 'record_id', 'machine_id', 'operation_time']
#     list_filter = ['action', 'operation_time']
#     search_fields = ['table_name', 'record_id', 'machine_id']
#     readonly_fields = ['operation_time']
#     
#     def has_add_permission(self, request):
#         return False
#     
#     def has_change_permission(self, request, obj=None):
#         return False
