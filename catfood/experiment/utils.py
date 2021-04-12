import datetime


def generate_response(data, isSuccess):
    return {
        "isSuccess": isSuccess,
        "data": data
    }


def dict_filter(old_dict, keys):
    ans = {}
    for key in keys:
        ans[key] = old_dict[key]
    return ans


def student_assignments_filter(assignments_list):
    key_white_list = ['course_case_id',
                      'submission_uploader', 'submission_case_id']
    for index, assignment in enumerate(assignments_list):
        if not assignment['submission_is_public']:
            assignments_list[index] = dict_filter(assignment, key_white_list)
    return assignments_list


def is_submission_valid(submission):
    valid_keys_set = {'course_case_id',
                      'submission_file_name', 'course_id'}
    return set(submission.keys()) == valid_keys_set


def is_submission_retrieve_valid(old_submission, new_submission):
    if old_submission['submission_is_public']:
        return False
    key_white_list = ['course_case_id',
                      'submission_uploader', 'submission_file_name', 'submission_case_id']
    for key in new_submission.keys():
        if key not in key_white_list:
            return False
    return True


def is_submission_delete_valid(old_submission):
    if old_submission['submission_is_public']:
        return False
    return True


def check_ddl(end_time):
    ddl = datetime.datetime.strptime(end_time.split('+')[0], '%Y-%m-%dT%H:%M:%S')
    return datetime.datetime.now() < ddl
