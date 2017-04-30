# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from Trai.models import Problem
from Trai.vjudge import get_problem


class Command(BaseCommand):
    help = 'Import problem from online judge website.'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('OJ', type=str)
        parser.add_argument('min_PID', type=int)
        parser.add_argument('max_PID', type=int)
        parser.add_argument('--silent',
                            action='store_true',
                            dest='silent',
                            default=False,
                            help="Skip error when occurred.")

    def handle(self, **options):
        min_id = options['min_PID']
        max_id = options['max_PID']
        oj = options['OJ']
        silent = options['silent']
        for pid in range(min_id, max_id + 1):
            data = get_problem(oj, pid)
            if 'error' not in data:
                new_problem = Problem.objects.update_or_create(
                    vid=data['vid'],
                    oj=str(oj).upper(),
                    pid=pid,
                    title=data['title'],
                    description=data['html'],
                )
                new_problem = new_problem[0]
                new_problem.save()

                self.stdout.write('Successfully import problem "%s"' % new_problem.__unicode__())
            else:
                self.stdout.write('{er} Failed import problem ({oj}:{pid})'.format(oj=oj, pid=pid, er=data['error']))
                if silent:
                    continue

                confirm = raw_input('Something unexpected occurred,sure to continue?\n'
                                    "Type 'yes' to continue, or 'no' to cancel: ")
                if confirm.lower() != 'yes':
                    raise CommandError("import problem cancelled.")
