import sqlite3


def retrieve_test_results(path):
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    results = cursor.execute("SELECT * from TestResult").fetchall()
    connection.close()
    return {row['name']: row for row in results}


def main():
    new_tests = []
    failed_tests = []
    passed_tests = []
    newly_failed_tests = []
    newly_passed_tests = []

    old_results_rows = retrieve_test_results("testament.db")
    new_results_rows = retrieve_test_results("build/testament.db")

    for new_result in new_results_rows.values():
        old_result = old_results_rows.get(new_result['name'])
        if old_result is None:
            new_tests.append(new_result)

        if new_result['result'] == 'reSuccess':
            passed_tests.append(new_result)
            if old_result and old_result['result'] != 'reSuccess':
                newly_passed_tests.append(new_result)
        else:
            failed_tests.append(new_result)
            if old_result and old_result['result'] == 'reSuccess':
                newly_failed_tests.append(new_result)

    print(json.dumps(
        dict(
            new_tests=new_tests,
            failed_tests=failed_tests,
            passed_tests=passed_tests,
            newly_failed_tests=newly_failed_tests,
            newly_passed_tests=newly_passed_tests,
        )
    ))

if __name__ == "__main__":
    main()