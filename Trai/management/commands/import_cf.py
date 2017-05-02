# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from Trai.models import Problem
from Trai.importcf import get_cf_list
from Trai.vjudge import get_problem
import datetime


# error_list_file = '/home/TraiPro/list.log'
error_list_file = '/home/rhyme/Desktop/Team/TraiPro/list.log'
list_file = open(error_list_file, 'a')


class Command(BaseCommand):
    help = 'Import codeforces problem from online judge website.'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('min_page', type=int)
        parser.add_argument('max_page', type=int)
        parser.add_argument('--silent',
                            action='store_true',
                            dest='silent',
                            default=False,
                            help="Skip error when occurred.")

    def handle(self, **options):
        min_page = options['min_page']
        max_page = options['max_page']
        silent = options['silent']
        oj = 'codeforces'

        for page in range(min_page, max_page + 1):
            problems = get_cf_list(page)
            for item in problems:
                ac_num = int(problems[item])
                problem_info = get_problem('codeforces', item)
                if 'error' in problem_info:
                    self.stdout.write(
                        '{er} Failed import problem codeforces:{pid})'.format(pid=item, er=problem_info['error']))
                    list_file.write('{id}\n'.format(id=item))
                    if silent:
                        continue

                    confirm = raw_input('Something unexpected occurred,sure to continue?\n'
                                        "Type 'yes' to continue, or 'no' to cancel: ")
                    if confirm.lower() != 'yes':
                        raise CommandError("import problem cancelled.")
                else:
                    new_problem = Problem.objects.update_or_create(
                        vid=problem_info['vid'],
                        oj=oj,
                        pid=item,
                        title=problem_info['title'],
                        description=problem_info['html'],
                        solved=ac_num,
                    )
                    new_problem = new_problem[0]
                    new_problem.save()
                    self.stdout.write('Successfully import problem "%s"' % new_problem.__unicode__())