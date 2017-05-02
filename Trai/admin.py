# -*- coding: utf-8 -*-
from django.contrib import admin
from django.db.models import Count, Case, When, IntegerField, Q
from django import forms
from django_summernote.admin import SummernoteModelAdmin
from Trai.models import Member, History, Problem, Team, Group, Assignment
from django.contrib import messages
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.helpers import ActionForm
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.db.models.functions import Length
# http://awesome-django.com/#awesome-django-admin-interface


class MemberAdmin(admin.ModelAdmin):
    list_display = ('nick_name', 'real_name', 'solved', 'related')

    # http://stackoverflow.com/questions/2168475/
    # django-admin-how-to-sort-by-one-of-the-custom-list-display-fields-that-has-no-d

    # http://stackoverflow.com/questions/33775011/how-to-annotate-count-with-a-condition-in-a-django-queryset
    def get_queryset(self, request):
        qs = super(MemberAdmin, self).get_queryset(request)
        qs = qs.annotate(related_cnt=Count('history'),
                         solved_cnt=Count(Case(
                             When(history__is_assignment=True, then=1), output_field=IntegerField(),)
                             )
                         )
        return qs

    def solved(self, obj):
        return obj.solved_cnt

    solved.admin_order_field = 'solved_cnt'

    def related(self, obj):
        return obj.related_cnt

    related.admin_order_field = 'related_cnt'


# https://djangosnippets.org/snippets/2885/
class ProblemFilter(SimpleListFilter):
    title = 'Assignment Group Filter' # or use _('country') for translated title
    parameter_name = 'group'

    def lookups(self, request, model_admin):
        groups = Group.objects.all()
        return [(c.id, c.name) for c in groups]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.exclude(assignments__groups__id__exact=self.value())
        else:
            return queryset


class ProblemFilter2(SimpleListFilter):
    title = 'History Group Filter' # or use _('country') for translated title
    parameter_name = 'his_group'

    def lookups(self, request, model_admin):
        groups = Group.objects.all()
        return [(c.id, c.name) for c in groups]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.exclude(history__member__teams__groups__id__exact=self.value())
        else:
            return queryset


class AssignmentForm(forms.Form):
    contest_name = forms.CharField(max_length=256)
    date = forms.DateTimeField(widget=forms.SelectDateWidget())
    groups = Group.objects.all()
    # options = ()
    # for group in groups:
    #     options.__add__((group.id, group.name))

    group_form = forms.ModelMultipleChoiceField(groups, required=False, widget=
                                                forms.SelectMultiple(
                                                    attrs={'size': '5', 'style': 'color:blue;width:250px'}))
    # price = IntegerField(required=False)


class ProblemAdmin(SummernoteModelAdmin):
    model = Problem
    list_display = ('vid', 'oj', 'pid', 'title', 'submitted', 'solved', 'ac_rate', 'difficulty', 'valid', 'info_date')
    list_filter = ('oj', 'valid', ProblemFilter, ProblemFilter2)
    actions = ['make_problem_assignment']

    def get_queryset(self, request):
        qs = super(ProblemAdmin, self).get_queryset(request)
        return qs.annotate(pid_len=Length('pid')).order_by('oj', 'pid_len', 'pid')

    class AssignmentForm(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
        contest_name = forms.CharField(max_length=256, label=u'Contest Name')
        date = forms.DateField(widget=forms.SelectDateWidget())
        groups = Group.objects.all()
        group_form = forms.ModelMultipleChoiceField(groups, required=False,
                                                    widget=forms.SelectMultiple(
                                                        attrs={'size': '5', 'style': 'color:blue;width:250px'}),
                                                    label=u'Group')

    def make_problem_assignment(self, request, queryset):
        form = None
        if 'apply' in request.POST:
            form = self.AssignmentForm(request.POST)
            if form.is_valid():
                contest_name = form.cleaned_data['contest_name']
                selected_problem_ids = form.cleaned_data['_selected_action']
                date = form.cleaned_data['date']
                groups = form.cleaned_data['group_form']
                try:
                    Assignment.objects.get(contest=contest_name)
                    self.message_user(request, 'Contest name existed, rename please.', messages.ERROR)
                    return render(request, 'Trai/action.html', {'title': u'Add Problem(s) on Assignment',
                                                                'queryset': queryset, 'form': form})
                except Assignment.DoesNotExist:
                    new_assignment = Assignment.objects.create(contest=contest_name, date=date)
                    lists = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
                    for problem_id in lists:
                        problem = Problem.objects.get(vid=int(problem_id))
                        new_assignment.problems.add(problem)
                    for group in groups:
                        new_assignment.groups.add(group)
                    self.message_user(request,
                                      u'Add Assignment(contest name:{name}) success!'.format(name=contest_name))
                    return HttpResponseRedirect(request.get_full_path())

        if not form:
            form = self.AssignmentForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME),
                                                'date': timezone.localtime(timezone.now())})

        print request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return render(request, 'Trai/action.html', {'title': u'Add Problem(s) on Assignment',
                                                    'queryset': queryset, 'form': form})

    make_problem_assignment.short_description = 'add problem(s) to assignment'


class HistoryAdmin(admin.ModelAdmin):
    list_display = ('member', 'problem', 'solve_date', 'is_assignment')
    list_filter = ('is_assignment', )


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', )
    filter_horizontal = ('members', )


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', )
    filter_horizontal = ('teams',)


class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('_contest', 'date')
    filter_horizontal = ('problems', 'groups')
    # filter_vertical = ('groups', )

    def _contest(self, obj):
        # html = '<a href="%s%s">%s</a>' % ('http://url-to-prepend.com/', obj.url_field, obj.url_field)
        return obj.contest

    _contest.short_description = 'Contest Name'
    _contest.admin_order_field = 'contest'

admin.site.register(Member, MemberAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(History, HistoryAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Assignment, AssignmentAdmin)


from django_summernote.admin import Attachment
admin.site.unregister(Attachment)

