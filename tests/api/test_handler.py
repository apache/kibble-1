import os
import requests
import pytest


class TestKibbleAPI:
    base_url = "https://0.0.0.0:8080"

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_account_delete(self):
        """
        Delete: /api/account
        """
        url = os.path.join(self.base_url, "/api/account")
        response = requests.delete(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_account_patch(self):
        """
        Patch: /api/account
        """
        url = os.path.join(self.base_url, "/api/account")
        response = requests.patch(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_account_put(self):
        """
        Put: /api/account
        """
        url = os.path.join(self.base_url, "/api/account")
        response = requests.put(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_bio_bio_get(self):
        """
        Get: /api/bio/bio
        """
        url = os.path.join(self.base_url, "/api/bio/bio")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_bio_bio_post(self):
        """
        Post: /api/bio/bio
        """
        url = os.path.join(self.base_url, "/api/bio/bio")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_bio_newtimers_get(self):
        """
        Get: /api/bio/newtimers
        """
        url = os.path.join(self.base_url, "/api/bio/newtimers")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_bio_newtimers_post(self):
        """
        Post: /api/bio/newtimers
        """
        url = os.path.join(self.base_url, "/api/bio/newtimers")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_bio_trends_get(self):
        """
        Get: /api/bio/trends
        """
        url = os.path.join(self.base_url, "/api/bio/trends")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_bio_trends_post(self):
        """
        Post: /api/bio/trends
        """
        url = os.path.join(self.base_url, "/api/bio/trends")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_ci_queue_get(self):
        """
        Get: /api/ci/queue
        """
        url = os.path.join(self.base_url, "/api/ci/queue")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_ci_queue_post(self):
        """
        Post: /api/ci/queue
        """
        url = os.path.join(self.base_url, "/api/ci/queue")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_ci_status_get(self):
        """
        Get: /api/ci/status
        """
        url = os.path.join(self.base_url, "/api/ci/status")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_ci_status_post(self):
        """
        Post: /api/ci/status
        """
        url = os.path.join(self.base_url, "/api/ci/status")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_ci_top_buildcount_get(self):
        """
        Get: /api/ci/top-buildcount
        """
        url = os.path.join(self.base_url, "/api/ci/top-buildcount")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_ci_top_buildcount_post(self):
        """
        Post: /api/ci/top-buildcount
        """
        url = os.path.join(self.base_url, "/api/ci/top-buildcount")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_ci_top_buildtime_get(self):
        """
        Get: /api/ci/top-buildtime
        """
        url = os.path.join(self.base_url, "/api/ci/top-buildtime")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_ci_top_buildtime_post(self):
        """
        Post: /api/ci/top-buildtime
        """
        url = os.path.join(self.base_url, "/api/ci/top-buildtime")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_changes_get(self):
        """
        Get: /api/code/changes
        """
        url = os.path.join(self.base_url, "/api/code/changes")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_changes_post(self):
        """
        Post: /api/code/changes
        """
        url = os.path.join(self.base_url, "/api/code/changes")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_commits_get(self):
        """
        Get: /api/code/commits
        """
        url = os.path.join(self.base_url, "/api/code/commits")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_commits_post(self):
        """
        Post: /api/code/commits
        """
        url = os.path.join(self.base_url, "/api/code/commits")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_committers_get(self):
        """
        Get: /api/code/committers
        """
        url = os.path.join(self.base_url, "/api/code/committers")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_committers_post(self):
        """
        Post: /api/code/committers
        """
        url = os.path.join(self.base_url, "/api/code/committers")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_evolution_get(self):
        """
        Get: /api/code/evolution
        """
        url = os.path.join(self.base_url, "/api/code/evolution")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_evolution_post(self):
        """
        Post: /api/code/evolution
        """
        url = os.path.join(self.base_url, "/api/code/evolution")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_pony_get(self):
        """
        Get: /api/code/pony
        """
        url = os.path.join(self.base_url, "/api/code/pony")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_pony_post(self):
        """
        Post: /api/code/pony
        """
        url = os.path.join(self.base_url, "/api/code/pony")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_pony_timeseries_get(self):
        """
        Get: /api/code/pony-timeseries
        """
        url = os.path.join(self.base_url, "/api/code/pony-timeseries")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_pony_timeseries_post(self):
        """
        Post: /api/code/pony-timeseries
        """
        url = os.path.join(self.base_url, "/api/code/pony-timeseries")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_punchcard_get(self):
        """
        Get: /api/code/punchcard
        """
        url = os.path.join(self.base_url, "/api/code/punchcard")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_punchcard_post(self):
        """
        Post: /api/code/punchcard
        """
        url = os.path.join(self.base_url, "/api/code/punchcard")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_relationships_get(self):
        """
        Get: /api/code/relationships
        """
        url = os.path.join(self.base_url, "/api/code/relationships")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_relationships_post(self):
        """
        Post: /api/code/relationships
        """
        url = os.path.join(self.base_url, "/api/code/relationships")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_retention_get(self):
        """
        Get: /api/code/retention
        """
        url = os.path.join(self.base_url, "/api/code/retention")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_retention_post(self):
        """
        Post: /api/code/retention
        """
        url = os.path.join(self.base_url, "/api/code/retention")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_sloc_get(self):
        """
        Get: /api/code/sloc
        """
        url = os.path.join(self.base_url, "/api/code/sloc")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_sloc_post(self):
        """
        Post: /api/code/sloc
        """
        url = os.path.join(self.base_url, "/api/code/sloc")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_top_commits_get(self):
        """
        Get: /api/code/top-commits
        """
        url = os.path.join(self.base_url, "/api/code/top-commits")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_top_commits_post(self):
        """
        Post: /api/code/top-commits
        """
        url = os.path.join(self.base_url, "/api/code/top-commits")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_top_sloc_get(self):
        """
        Get: /api/code/top-sloc
        """
        url = os.path.join(self.base_url, "/api/code/top-sloc")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_top_sloc_post(self):
        """
        Post: /api/code/top-sloc
        """
        url = os.path.join(self.base_url, "/api/code/top-sloc")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_trends_get(self):
        """
        Get: /api/code/trends
        """
        url = os.path.join(self.base_url, "/api/code/trends")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_code_trends_post(self):
        """
        Post: /api/code/trends
        """
        url = os.path.join(self.base_url, "/api/code/trends")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_forum_actors_get(self):
        """
        Get: /api/forum/actors
        """
        url = os.path.join(self.base_url, "/api/forum/actors")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_forum_actors_post(self):
        """
        Post: /api/forum/actors
        """
        url = os.path.join(self.base_url, "/api/forum/actors")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_forum_creators_get(self):
        """
        Get: /api/forum/creators
        """
        url = os.path.join(self.base_url, "/api/forum/creators")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_forum_creators_post(self):
        """
        Post: /api/forum/creators
        """
        url = os.path.join(self.base_url, "/api/forum/creators")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_forum_issues_get(self):
        """
        Get: /api/forum/issues
        """
        url = os.path.join(self.base_url, "/api/forum/issues")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_forum_issues_post(self):
        """
        Post: /api/forum/issues
        """
        url = os.path.join(self.base_url, "/api/forum/issues")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_forum_responders_get(self):
        """
        Get: /api/forum/responders
        """
        url = os.path.join(self.base_url, "/api/forum/responders")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_forum_responders_post(self):
        """
        Post: /api/forum/responders
        """
        url = os.path.join(self.base_url, "/api/forum/responders")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_forum_top_get(self):
        """
        Get: /api/forum/top
        """
        url = os.path.join(self.base_url, "/api/forum/top")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_forum_top_post(self):
        """
        Post: /api/forum/top
        """
        url = os.path.join(self.base_url, "/api/forum/top")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_forum_top_count_get(self):
        """
        Get: /api/forum/top-count
        """
        url = os.path.join(self.base_url, "/api/forum/top-count")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_forum_top_count_post(self):
        """
        Post: /api/forum/top-count
        """
        url = os.path.join(self.base_url, "/api/forum/top-count")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_forum_trends_get(self):
        """
        Get: /api/forum/trends
        """
        url = os.path.join(self.base_url, "/api/forum/trends")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_forum_trends_post(self):
        """
        Post: /api/forum/trends
        """
        url = os.path.join(self.base_url, "/api/forum/trends")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_actors_get(self):
        """
        Get: /api/issue/actors
        """
        url = os.path.join(self.base_url, "/api/issue/actors")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_actors_post(self):
        """
        Post: /api/issue/actors
        """
        url = os.path.join(self.base_url, "/api/issue/actors")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_age_get(self):
        """
        Get: /api/issue/age
        """
        url = os.path.join(self.base_url, "/api/issue/age")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_age_post(self):
        """
        Post: /api/issue/age
        """
        url = os.path.join(self.base_url, "/api/issue/age")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_closers_get(self):
        """
        Get: /api/issue/closers
        """
        url = os.path.join(self.base_url, "/api/issue/closers")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_closers_post(self):
        """
        Post: /api/issue/closers
        """
        url = os.path.join(self.base_url, "/api/issue/closers")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_issues_get(self):
        """
        Get: /api/issue/issues
        """
        url = os.path.join(self.base_url, "/api/issue/issues")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_issues_post(self):
        """
        Post: /api/issue/issues
        """
        url = os.path.join(self.base_url, "/api/issue/issues")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_openers_get(self):
        """
        Get: /api/issue/openers
        """
        url = os.path.join(self.base_url, "/api/issue/openers")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_openers_post(self):
        """
        Post: /api/issue/openers
        """
        url = os.path.join(self.base_url, "/api/issue/openers")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_pony_timeseries_get(self):
        """
        Get: /api/issue/pony-timeseries
        """
        url = os.path.join(self.base_url, "/api/issue/pony-timeseries")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_pony_timeseries_post(self):
        """
        Post: /api/issue/pony-timeseries
        """
        url = os.path.join(self.base_url, "/api/issue/pony-timeseries")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_relationships_get(self):
        """
        Get: /api/issue/relationships
        """
        url = os.path.join(self.base_url, "/api/issue/relationships")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_relationships_post(self):
        """
        Post: /api/issue/relationships
        """
        url = os.path.join(self.base_url, "/api/issue/relationships")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_retention_get(self):
        """
        Get: /api/issue/retention
        """
        url = os.path.join(self.base_url, "/api/issue/retention")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_retention_post(self):
        """
        Post: /api/issue/retention
        """
        url = os.path.join(self.base_url, "/api/issue/retention")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_top_get(self):
        """
        Get: /api/issue/top
        """
        url = os.path.join(self.base_url, "/api/issue/top")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_top_post(self):
        """
        Post: /api/issue/top
        """
        url = os.path.join(self.base_url, "/api/issue/top")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_top_count_get(self):
        """
        Get: /api/issue/top-count
        """
        url = os.path.join(self.base_url, "/api/issue/top-count")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_top_count_post(self):
        """
        Post: /api/issue/top-count
        """
        url = os.path.join(self.base_url, "/api/issue/top-count")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_trends_get(self):
        """
        Get: /api/issue/trends
        """
        url = os.path.join(self.base_url, "/api/issue/trends")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_issue_trends_post(self):
        """
        Post: /api/issue/trends
        """
        url = os.path.join(self.base_url, "/api/issue/trends")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_keyphrases_get(self):
        """
        Get: /api/mail/keyphrases
        """
        url = os.path.join(self.base_url, "/api/mail/keyphrases")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_keyphrases_post(self):
        """
        Post: /api/mail/keyphrases
        """
        url = os.path.join(self.base_url, "/api/mail/keyphrases")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_map_get(self):
        """
        Get: /api/mail/map
        """
        url = os.path.join(self.base_url, "/api/mail/map")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_map_post(self):
        """
        Post: /api/mail/map
        """
        url = os.path.join(self.base_url, "/api/mail/map")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_mood_get(self):
        """
        Get: /api/mail/mood
        """
        url = os.path.join(self.base_url, "/api/mail/mood")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_mood_post(self):
        """
        Post: /api/mail/mood
        """
        url = os.path.join(self.base_url, "/api/mail/mood")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_mood_timeseries_get(self):
        """
        Get: /api/mail/mood-timeseries
        """
        url = os.path.join(self.base_url, "/api/mail/mood-timeseries")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_mood_timeseries_post(self):
        """
        Post: /api/mail/mood-timeseries
        """
        url = os.path.join(self.base_url, "/api/mail/mood-timeseries")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_pony_timeseries_get(self):
        """
        Get: /api/mail/pony-timeseries
        """
        url = os.path.join(self.base_url, "/api/mail/pony-timeseries")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_pony_timeseries_post(self):
        """
        Post: /api/mail/pony-timeseries
        """
        url = os.path.join(self.base_url, "/api/mail/pony-timeseries")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_relationships_get(self):
        """
        Get: /api/mail/relationships
        """
        url = os.path.join(self.base_url, "/api/mail/relationships")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_relationships_post(self):
        """
        Post: /api/mail/relationships
        """
        url = os.path.join(self.base_url, "/api/mail/relationships")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_retention_get(self):
        """
        Get: /api/mail/retention
        """
        url = os.path.join(self.base_url, "/api/mail/retention")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_retention_post(self):
        """
        Post: /api/mail/retention
        """
        url = os.path.join(self.base_url, "/api/mail/retention")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_timeseries_get(self):
        """
        Get: /api/mail/timeseries
        """
        url = os.path.join(self.base_url, "/api/mail/timeseries")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_timeseries_post(self):
        """
        Post: /api/mail/timeseries
        """
        url = os.path.join(self.base_url, "/api/mail/timeseries")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_timeseries_single_get(self):
        """
        Get: /api/mail/timeseries-single
        """
        url = os.path.join(self.base_url, "/api/mail/timeseries-single")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_timeseries_single_post(self):
        """
        Post: /api/mail/timeseries-single
        """
        url = os.path.join(self.base_url, "/api/mail/timeseries-single")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_top_authors_get(self):
        """
        Get: /api/mail/top-authors
        """
        url = os.path.join(self.base_url, "/api/mail/top-authors")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_top_authors_post(self):
        """
        Post: /api/mail/top-authors
        """
        url = os.path.join(self.base_url, "/api/mail/top-authors")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_top_topics_get(self):
        """
        Get: /api/mail/top-topics
        """
        url = os.path.join(self.base_url, "/api/mail/top-topics")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_top_topics_post(self):
        """
        Post: /api/mail/top-topics
        """
        url = os.path.join(self.base_url, "/api/mail/top-topics")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_trends_get(self):
        """
        Get: /api/mail/trends
        """
        url = os.path.join(self.base_url, "/api/mail/trends")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_mail_trends_post(self):
        """
        Post: /api/mail/trends
        """
        url = os.path.join(self.base_url, "/api/mail/trends")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_org_contributors_post(self):
        """
        Post: /api/org/contributors
        """
        url = os.path.join(self.base_url, "/api/org/contributors")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_org_list_get(self):
        """
        Get: /api/org/list
        """
        url = os.path.join(self.base_url, "/api/org/list")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_org_list_post(self):
        """
        Post: /api/org/list
        """
        url = os.path.join(self.base_url, "/api/org/list")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_org_list_put(self):
        """
        Put: /api/org/list
        """
        url = os.path.join(self.base_url, "/api/org/list")
        response = requests.put(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_org_members_delete(self):
        """
        Delete: /api/org/members
        """
        url = os.path.join(self.base_url, "/api/org/members")
        response = requests.delete(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_org_members_get(self):
        """
        Get: /api/org/members
        """
        url = os.path.join(self.base_url, "/api/org/members")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_org_members_post(self):
        """
        Post: /api/org/members
        """
        url = os.path.join(self.base_url, "/api/org/members")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_org_members_put(self):
        """
        Put: /api/org/members
        """
        url = os.path.join(self.base_url, "/api/org/members")
        response = requests.put(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_org_sourcetypes_get(self):
        """
        Get: /api/org/sourcetypes
        """
        url = os.path.join(self.base_url, "/api/org/sourcetypes")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_org_sourcetypes_post(self):
        """
        Post: /api/org/sourcetypes
        """
        url = os.path.join(self.base_url, "/api/org/sourcetypes")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_org_trends_get(self):
        """
        Get: /api/org/trends
        """
        url = os.path.join(self.base_url, "/api/org/trends")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_org_trends_post(self):
        """
        Post: /api/org/trends
        """
        url = os.path.join(self.base_url, "/api/org/trends")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_session_delete(self):
        """
        Delete: /api/session
        """
        url = os.path.join(self.base_url, "/api/session")
        response = requests.delete(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_session_get(self):
        """
        Get: /api/session
        """
        url = os.path.join(self.base_url, "/api/session")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_session_put(self):
        """
        Put: /api/session
        """
        url = os.path.join(self.base_url, "/api/session")
        response = requests.put(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_sources_delete(self):
        """
        Delete: /api/sources
        """
        url = os.path.join(self.base_url, "/api/sources")
        response = requests.delete(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_sources_get(self):
        """
        Get: /api/sources
        """
        url = os.path.join(self.base_url, "/api/sources")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_sources_patch(self):
        """
        Patch: /api/sources
        """
        url = os.path.join(self.base_url, "/api/sources")
        response = requests.patch(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_sources_post(self):
        """
        Post: /api/sources
        """
        url = os.path.join(self.base_url, "/api/sources")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_sources_put(self):
        """
        Put: /api/sources
        """
        url = os.path.join(self.base_url, "/api/sources")
        response = requests.put(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_verify_email_vcode_get(self):
        """
        Get: /api/verify/{email}/{vcode}
        """
        url = os.path.join(self.base_url, "/api/verify/{email}/{vcode}")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_views_delete(self):
        """
        Delete: /api/views
        """
        url = os.path.join(self.base_url, "/api/views")
        response = requests.delete(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_views_get(self):
        """
        Get: /api/views
        """
        url = os.path.join(self.base_url, "/api/views")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_views_patch(self):
        """
        Patch: /api/views
        """
        url = os.path.join(self.base_url, "/api/views")
        response = requests.patch(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_views_post(self):
        """
        Post: /api/views
        """
        url = os.path.join(self.base_url, "/api/views")
        response = requests.post(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_views_put(self):
        """
        Put: /api/views
        """
        url = os.path.join(self.base_url, "/api/views")
        response = requests.put(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body

    @pytest.mark.xfail(reason="Not implemented :<")
    def test_widgets_pageid_get(self):
        """
        Get: /api/widgets/{pageid}
        """
        url = os.path.join(self.base_url, "/api/widgets/{pageid}")
        response = requests.get(url)
        assert response.status_code == requests.codes.ok

        body = response.json()
        expected_body = {}
        assert body == expected_body
