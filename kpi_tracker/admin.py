from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db import connection
from .models import (
    BreastKPI, 
    KPIActivityLog, 
    Physicians, 
    User
)

class CustomUserForm(forms.ModelForm):
    groups_field = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple('groups', False)
    )

    class Meta:
        model = User
        fields = '__all__'
        exclude = ('groups',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            group_ids = [getattr(result, 'group_id', None) for result in self.instance.get_group_ids()]
            self.fields['groups_field'].initial = [gid for gid in group_ids if gid is not None]

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM [datahub].[KPI_Users_Groups] WHERE [user_id] = ?", 
                    [user.pk]
                )
                for group in self.cleaned_data['groups_field']:
                    cursor.execute("""
                        INSERT INTO [datahub].[KPI_Users_Groups] 
                        ([user_id], [group_id]) 
                        VALUES (?, ?)
                    """, [user.pk, group.pk])
        return user

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = CustomUserForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    
    fieldsets = (
        (None, {'fields': ('username',)}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'azure_id')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups_field'),
            'classes': ('collapse',),
            'description': 'User permissions and group memberships'
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'is_staff', 'is_superuser', 'groups_field'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')

    def save_model(self, request, obj, form, change):
        if change:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE [datahub].[KPI_Users]
                    SET [username] = ?, 
                        [email] = ?, 
                        [first_name] = ?, 
                        [last_name] = ?,
                        [is_staff] = ?, 
                        [is_superuser] = ?, 
                        [is_active] = ?
                    WHERE [id] = ?
                """, [
                    obj.username, 
                    obj.email, 
                    obj.first_name, 
                    obj.last_name,
                    1 if obj.is_staff else 0, 
                    1 if obj.is_superuser else 0, 
                    1 if obj.is_active else 0,
                    obj.id
                ])
        else:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO [datahub].[KPI_Users] (
                        [username], [email], [first_name], [last_name],
                        [is_staff], [is_superuser], [is_active],
                        [date_joined]
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, GETDATE()
                    );
                    SELECT SCOPE_IDENTITY();
                """, [
                    obj.username, 
                    obj.email, 
                    obj.first_name, 
                    obj.last_name,
                    1 if obj.is_staff else 0, 
                    1 if obj.is_superuser else 0, 
                    1 if obj.is_active else 0
                ])
                obj.id = cursor.fetchone()[0]

@admin.register(BreastKPI)
class BreastKPIAdmin(admin.ModelAdmin):
    list_display = ('MRN', 'Gender', 'Age', 'Nationality', 'Patient_on_CPG', 'Pending')
    list_filter = ('Pending', 'Patient_on_CPG', 'Treatment_NotFitForThisKPI', 'Surgery_NotFitForThisKPI', 'Radio_NotFitForThisKPI')
    search_fields = ('MRN', 'CNC_name', 'Oncologist_name', 'Surgeon_name')
    date_hierarchy = 'entry_ts'

@admin.register(KPIActivityLog)
class KPIActivityLogAdmin(admin.ModelAdmin):
    list_display = ('MRN', 'UserName', 'Type', 'ts', 'Pending_Status')
    list_filter = ('SourcePage', 'Type', 'Pending_Status')
    search_fields = ('MRN', 'UserName', 'UserEmail')
    date_hierarchy = 'ts'

@admin.register(Physicians)
class PhysiciansAdmin(admin.ModelAdmin):
    list_display = ('Disease', 'Physician_type', 'Physician_name')
    list_filter = ('Disease', 'Physician_type')
    search_fields = ('Physician_name',)

    
