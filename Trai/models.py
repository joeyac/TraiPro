# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Member(models.Model):
    nick_name = models.CharField(max_length=100)
    real_name = models.CharField(max_length=100)
    user = models.OneToOneField(User, blank=True, null=True)

    def __unicode__(self):
        return u'{v1}({v2})'.format(v1=self.nick_name, v2=self.real_name)
    # @property
    # def solved(self):
    #     return History.objects.filter(member=self).count()

    # @property
    # def related(self):
    #     # teams = Team.objects.filter()
    #     return 0


class Problem(models.Model):
    vid = models.IntegerField(primary_key=True)
    oj = models.CharField(max_length=40)
    pid = models.CharField(max_length=50)

    title = models.CharField(max_length=256)
    description = models.TextField()

    submitted = models.IntegerField(blank=True, null=True)
    solved = models.IntegerField(blank=True, null=True)
    ac_rate = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        return u'{v1}-{v2}'.format(v1=self.oj, v2=self.pid)

    @property
    def difficulty(self):
        return 0

    valid = models.BooleanField(default=True)
    why_invalid = models.CharField(default="", blank=True, max_length=500)

    info_date = models.DateTimeField(auto_now=True)  # 添加或者修改的时间




class History(models.Model):
    solve_date = models.DateTimeField(auto_created=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)  # 级联删除
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    is_assignment = models.BooleanField(verbose_name='是否比赛记录', default=True)

    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'{v1}:[{v2}]'.format(v1=self.member.nick_name, v2=self.problem)

    class Meta:
        verbose_name = 'History'
        verbose_name_plural = 'Histories'


class Team(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(Member, related_name='teams')

    def __unicode__(self):
        return u'{v}'.format(v=self.name)


class Group(models.Model):
    name = models.CharField(max_length=100)
    teams = models.ManyToManyField(Team, related_name='groups')

    def __unicode__(self):
        return u'{v}'.format(v=self.name)


class Assignment(models.Model):
    contest = models.CharField(max_length=256, verbose_name='Contest Name')
    problems = models.ManyToManyField(Problem, related_name='assignments')
    groups = models.ManyToManyField(Group, related_name='assignments')
    date = models.DateField()

    # end_date_time = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return u'{v}'.format(v=self.contest)
