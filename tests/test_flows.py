from lithica_drive_sync.flows import connect_and_list


class FakeDrive:
    def list_projects(self, access_token):
        assert access_token == "access"
        return ["project"]


class FakeToken:
    access_token = "access"


def test_connect_and_list_finishes_as_one_operation():
    token, projects = connect_and_list(
        authorize=lambda config: FakeToken(),
        config=object(),
        drive=FakeDrive(),
    )

    assert token.access_token == "access"
    assert projects == ["project"]
