# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from Trai.models import Problem
from Trai.submit_ac import get_problem_status
import time


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--vid', type=int)

        # Named (optional) arguments
        parser.add_argument('--all',
                            action='store_true',
                            dest='all',
                            default=False,
                            help="Update all problems' solved and submitted info in databases.")

    def handle(self, **options):
        def process(problem):
            vid = problem.vid
            try:
                res = get_problem_status(problem.oj, problem.pid)
                update = False
                if res['submitted'] and res['submitted'] != problem.submitted:
                    update = True
                    problem.submitted = int(res['submitted'])
                if res['accepted'] != problem.solved:
                    update = True
                    problem.solved = int(res['accepted'])
                if update and res['submitted']:
                    ac_rate = float(res['accepted']) / int(res['submitted'])
                    problem.ac_rate = ac_rate
                problem.save(update_fields=['submitted', 'solved', 'ac_rate'])
                self.stdout.write('Successfully update problem "%s"' % problem.__unicode__())
		return True
            except Problem.DoesNotExist:
                raise CommandError('Problem [pid:%s] does not exist' % vid)
            except Exception as e:
		self.stdout.write('Problem [pid:%s] error' % vid)
		return False
                # raise CommandError('Unknown error, please contact crazyX :"%s"' % e)

        if not options['all'] or not options['vid']:
            raise CommandError('too few arguments: --all and --vid at lease one.')
        # if options['all']:
        problems = Problem.objects.all().filter(vid__gte=options['vid'])
        for item in problems:
            flag = process(item)
            while not flag:
                time.sleep(3)
                flag = process(item)
        # else:
        #     for vid in options['vid']:
        #         item = Problem.objects.get(vid=vid)
        #         process(item)




