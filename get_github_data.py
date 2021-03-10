import pandas as pd
import requests
import sys
from progress.bar import IncrementalBar
import os

auth_token = os.getenv('AUTH_TOKEN')

auth_headers = {'Authorization': f'token {auth_token}','User-Agent': 'request'}

def get_reactions(comments_ids):
    '''Get all reactions data'''
    reaction_dfs = []
    processing_reactions = IncrementalBar('get all reactions', max=len(comments_ids))
    for comment_id in comments_ids:
        processing_reactions.next()
        response = requests.get(f"https://api.github.com/repos/programminghistorian/jekyll/issues/comments/{comment_id}/reactions", headers={'Accept': 'application/vnd.github.squirrel-girl-preview', **auth_headers})
        df = pd.DataFrame.from_dict(response.json())
        reaction_dfs.append(df)
    processing_reactions.finish()
    return pd.concat(reaction_dfs)

def get_comments(comments_urls):
    '''Get all comments data'''
    comments_dfs = []
    processing_comments = IncrementalBar('get all comments', max=len(comments_urls))
    for url in comments_urls:
        processing_comments.next()
        response = requests.get(url, headers=auth_headers)
        df = pd.DataFrame.from_dict(response.json())
        comments_dfs.append(df)
    processing_comments.finish()
    return pd.concat(comments_dfs)

def fresh_data_scrape(output_filename):
    '''This function does a fresh scrape of the Github API to get all issue, comments, and reactions data for the Jekyll repo. It will probably need to be run over at least two hours because of rate limiting.'''
    dfs = []
    # Using requests get all Github issues data (have to hard code in the range currently but giving a very wide range)
    processing_issues = IncrementalBar('get all issues', max=100)
    for i in range(0, 100):
        processing_issues.next()
        response = requests.get(f"https://api.github.com/repos/programminghistorian/jekyll/issues?state=all&page={i}&per_page=100", headers=auth_headers)
        print(response)
        df = pd.DataFrame.from_dict(response.json())
        df['request_page'] = i
        if len(df) == 0:
            processing_issues.finish()
            break
        else:
            dfs.append(df)
    initial_df = pd.concat(dfs)
    df = initial_df.drop_duplicates(subset=['id'])
    df.to_csv(output_filename + '_isssues.csv', index=False)
        
    comment_urls = df.comments_url.tolist()
    comments_df = get_comments(comment_urls)
    comments_df.to_csv(output_filename+ '_comments.csv', index=False)

    comment_ids = comments_df.id.tolist()
    reactions_df = get_reactions(comment_ids)
    reactions_df.to_csv(output_filename+ '_reactions.csv', index=False)

def scrape_all_data(output_filename):
    '''This function scrapes Github API to get all issue, comments, and reactions data'''
    issues_df = pd.read_csv(output_filename + '_issues.csv')
    comments_df = pd.read_csv(output_filename + '_comments.csv')
    reactions_df = pd.read_csv(output_filename+ '_reactions.csv')

    if len(issues_df) == 0:
        return fresh_data_scrape(output_filename)
    
    print('reading existing and new issues')
    response = requests.get('https://api.github.com/repos/programminghistorian/jekyll/issues?sort=updated&direction=desc&per_page=100')
    repo_latest_issues = pd.DataFrame.from_dict(response.json())
    new_issues = list(set(repo_latest_issues.id.tolist()) - set(issues_df.id.tolist()))

    if len(new_issues) > 0:
        print('joining new issues with existing ones')
        concat_issues = pd.concat([repo_latest_issues, issues_df])
        total_issues = concat_issues[concat_issues.id.duplicated() == False]

        total_issues.to_csv(output_filename + '_issues.csv', index=False)

    print('reading existing and new comments')
    response = requests.get('https://api.github.com/repos/programminghistorian/jekyll/issues/comments?sort=updated&direction=desc&per_page=100')
    repo_latest_comments = pd.DataFrame.from_dict(response.json())
    new_comments = list(set(repo_latest_comments.id.tolist()) - set(comments_df.id.tolist()))

    if len(new_comments) > 0:
        print('joining new comments with existing ones')
        concat_comments = pd.concat([repo_latest_comments, comments_df])
        total_comments = concat_comments[concat_comments.id.duplicated() == False]
        total_comments.to_csv(output_filename + '_comments.csv', index=False)

        print('joining new reactions with existing ones')
        comment_ids = repo_latest_comments.id.tolist()
        repo_latest_reactions = get_reactions(comment_ids)
        concat_reactions = pd.concat([repo_latest_reactions, reactions_df])
        total_reactions = concat_reactions[concat_reactions.id.duplicated() == False]
        total_reactions.to_csv(output_filename+ '_reactions.csv', index=False)


if __name__ ==  "__main__" :
    output_filename = sys.argv[1] if len(sys.argv) > 1 else './datasets/programming_historian_github_data'
    scrape_all_data(output_filename)
