import sqlite3
import json
import shutil
import tarfile
import io
import os.path as path

def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def retrieve_test_results(path):
    connection = sqlite3.connect(path)
    connection.row_factory = dict_factory
    cursor = connection.cursor()
    results = cursor.execute("SELECT * from TestResult").fetchall()
    connection.close()
    return {row['name']: row for row in results}


def compare_test_results():
    new_tests = []
    failed_tests = []
    passed_tests = []
    newly_failed_tests = []
    newly_passed_tests = []

    old_results_rows = retrieve_test_results("testament.db")
    new_results_rows = retrieve_test_results("build/testament.db")

    for new_result in new_results_rows.values():
        old_result = old_results_rows.get(new_result['name'])

        comparison_flags = []
        new_result['comparison_flags'] = comparison_flags

        if old_result is None:
            comparison_flags.append('new')

        if new_result['result'] == 'reSuccess':
            if old_result and old_result['result'] != 'reSuccess':
                comparison_flags.append('newly passed')
            else:
                comparison_flags.append('passed')
        else:
            if old_result and old_result['result'] == 'reSuccess':
                comparison_flags.append('newly failed')
            else:
                comparison_flags.append('failed')

    return json.dumps(new_results_rows)


def main():
    # If we have two tests to compare, compare them and get the results:
    comparison_output = ""
    if path.exists("testament.db") and path.exists("build/testament.db"):
        with open('compresults.json', 'w') as fh:
            fh.write(compare_test_results().replace('\n', '\r'))

    # Next, add the comparison results and test database to a tar file.
    # with tarfile.open("testfiles.tar.bz2", "w:bz2", compresslevel=9) as tar:
    #     tar.add('build/testament.db', 'testament.db')
    #     tar.add('build/testresults.html', 'testresults.html')
    #     tar.add('compresults.json')

    # Then update the 'last database' file.
    if path.exists("build/testament.db"):
        shutil.copyfile("build/testament.db", "testament.db")

if __name__ == "__main__":
    main()
