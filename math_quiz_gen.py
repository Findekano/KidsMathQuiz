#-*-coding:utf-8-*-


def parseArgs():
    '''Parse ar测试guments from command line'''
    import argparse

    args_parser = argparse.ArgumentParser(description='Create math quiz for kids')
    args_parser.add_argument('-r', '--range',
                             dest='range',
                             default=100,
                             type=int,
                             help='range of numbers')

    args_parser.add_argument('-o', '--operator',
                             dest='ops',
                             default='+',
                             nargs='*',
                             choices=['+', '-'],
                             help='operator')

    args_parser.add_argument('-nc', '--no_carry',
                             dest='nc',
                             default=False,
                             const=True,
                             type=bool,
                             nargs='?',
                             help='not allow carry')

    args_parser.add_argument('count',
                             type=int,
                             nargs='?',
                             default=1,
                             help='how many quiz to generate')

    args = args_parser.parse_args()
    args.ops = list(set(args.ops))
    return args


def generateQuiz(args):
    from random import randint

    op = args.ops[randint(0, len(args.ops) - 1)]
    while True:
        lhs = randint(0, args.range - 1)
        rhs = randint(0, args.range - 1)
        if op == '-':
            if lhs == 0:
                continue

            rhs = randint(1, lhs)

        # fix carry issue
        carry_range_func = {'+': lambda i: 9 - i,
                            '-': lambda i: i}
        if args.nc == True:
            lhs_str = str(lhs)
            rhs_str = ''
            for c in lhs_str:
                rhs_str += str(randint(0, carry_range_func[op](int(c))))
            rhs = int(rhs_str)

        if rhs != 0:
            break

    op_func = {'+': lambda a, b: a + b,
               '-': lambda a, b: a - b}

    return {'quiz': '{0} {1} {2}'.format(lhs, op, rhs),
            'lhs': lhs,
            'rhs': rhs,
            'op': op,
            'answer': op_func[op](lhs, rhs)}


def generateHTML(quiz, args):
    import os.path
    import tempfile
    import webbrowser

    from django.template import Template, Context
    from django.conf import settings
    from django.utils.encoding import smart_str

    if settings.configured == False:
        settings.configure()

    path = os.path.dirname(os.path.realpath(__file__))
    fp = open(os.path.join(path, 'math_quiz_temp.html'))

    try:
        t = Template(fp.read())
    finally:
        fp.close()

    op_desc = {'+': '加',
               '-': '减'}

    html = smart_str(t.render(Context({'range': args.range,
                                       'operations': map(lambda i: op_desc[i], args.ops),
                                       'limitation': args.nc,
                                       'quiz': quiz})))
    fd, path = tempfile.mkstemp('.html', prefix='math_quiz_')
    os.write(fd, html)
    os.close(fd)

    browser = webbrowser.get()
    browser.open(path)


if __name__ == '__main__':
    args = parseArgs()
    quiz = []
    for i in range(args.count):
        quiz.append(generateQuiz(args))

    generateHTML(quiz, args)
