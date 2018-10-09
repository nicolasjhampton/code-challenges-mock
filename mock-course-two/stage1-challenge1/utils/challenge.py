from contextlib import redirect_stdout
import io
import inspect
import unittest
import sys


# A set of tuples of filename to output
execution_log = set()

def source_of(filename, strip=True):
    with open(filename) as f:
        src = f.read()
    if strip:
        src = src.strip()
    return src


def execute_source(filename):
    global execution_log
    src = source_of(filename)
    out = io.StringIO()
    with redirect_stdout(out):
        exec(src)
    context = locals().copy()
    output = out.getvalue().strip()
    if output:
        execution_log.add((filename, output))
    context['__output'] = output
    return context


def write_preview(module, text):
    # TODO: Expose this file name in top level runner as a Python variable
    output_file_name = 'output.html'
    # NOTE: All tasks are run, so `write_preview` is called multiple times
    if module.test_number == 1:
        with open(output_file_name, 'w') as file:
            file.write('''
            <html>
                <head>
                    <title>Test Results</title>
                    <link rel="stylesheet" href="https://teamtreehouse.com/_assets/application.css" />
                </head>
                <body id="challenge-preview">
                ''')
            # Output standard out for any code that was executed
            if execution_log:
                for filename, output in execution_log:
                    file.write('''
                        <div class="mixed-box">
                            <div class="box-header">
                                <h2>Output for {}</h2>
                            </div>
                            <div class="secondary box">
                                <pre>{}</pre>
                            </div>
                        </div>
                    '''.format(filename, output))

    with open(output_file_name, 'a') as file:
        file.write('''
            <div class="mixed-box">
                <div class="box-header">
                    <h2>Task #{}</h2>
                </div>
                <div class="secondary box">
                    <pre><code class="python">{}</code></pre>
                </div>
            </div>
        '''.format(module.test_number, text))
    # TODO: How do you know you are on the last test?


def message_from_problem(problem):
    """Pulls a bummer message from a problem (error/failure).

    This could use some work, and only exists because of the TextTestRunner.

    :param problem: A tuple of test to error
    :returns message: A student facing bummer message
    """
    # Very last line (expecting trailing new line)
    return problem[1].split('\n')[-2]


def depends_on(*classes):

    def wrap(cls):
        cls._dependencies = classes
        return cls

    return wrap


def test_cases_from_module(module):
    return [obj for _, obj in inspect.getmembers(module)
            if inspect.isclass(obj) and issubclass(obj, unittest.TestCase)]


def results_from_test_cases(test_cases):
    output_stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=output_stream)
    # TestCase => unittest.Result (or None if unmet dependencies)
    results = dict()

    def check(test_case):
        if test_case not in results:
            dependencies = getattr(test_case, '_dependencies', ())
            # Head's up...recursion
            all_met = all(check(dependency) for dependency in dependencies)
            if all_met:
                result = runner.run(unittest.defaultTestLoader.loadTestsFromTestCase(test_case))
                results[test_case] = result
            else:
                # We didn't run it because dependencies were not met
                results[test_case] = None
        res = results[test_case]
        return res.wasSuccessful() if res is not None else None

    for case in test_cases:
        check(case)
    return (output_stream.getvalue(),
            [r for r in results.values() if r is not None])


def run_task_tests_in_module(module_name):
    """Run Unit Tests with intimate knowledge of challenge engine.

    Output is written to preview pane using `output.html`.

    :param module_name: The module that represents the PythonRunner script.
                            It should contain things like the `success` and `failure` method.
    """
    mod = sys.modules[module_name]
    test_cases = test_cases_from_module(mod)
    output, results = results_from_test_cases(test_cases)
    unsuccessful_results = [result for result in results if not result.wasSuccessful()]
    if unsuccessful_results:
        # Collapse all errors and failures into a list of lists
        problems_nested = [result.errors + result.failures for result in unsuccessful_results]
        # Flatten
        problems = [problem for sub in problems_nested for problem in sub]
        if len(problems) == 1:
            custom_msg = message_from_problem(problems[0])
            mod.failure(custom_msg)
        else:
            mod.failure(
                "Oh no, there were {} problems with your code, check the preview pane for more information".format(
                    len(problems)))

    else:
        mod.success()
    write_preview(mod, output)
