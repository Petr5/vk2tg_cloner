def get_token_from_url(url: str) -> str:
    """get url like this https://oauth.vk.com/blank.html#access_token=vk1.a.2Y6SAaTg9dZUipXtWcGtCToXxA452AVIWPsz0EEtNSC3ePRvVP6qcxwjh1cEIImcAtM_RKMPoDyX8Ma5Q5_2ke9ztWbyWBSAFdE0GBP3VhrUd5qvxutG1igvbFHdIbkwWV9DDgTGqDNS9qkITeT3ouGEqju9ZQe_NlqszVVnQhxy6anJtQhvYOmSZfO6TUag&expires_in=0&user_id=536270471 and convert it to access token"""
    return url.split("access_token=")[1].split("&")[0]


def list_of_dict_to_list(list_of_dict: list[dict], key) -> list:
    """Convert list of dict to list of values by key"""
    return [d[key] for d in list_of_dict]