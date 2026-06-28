def connect_and_list(authorize, config, drive):
    token = authorize(config)
    projects = drive.list_projects(token.access_token)
    return token, projects
