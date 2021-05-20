from pepysdiary.encyclopedia import views
from tests import ViewTestCase


class EncyclopediaViewTestCase(ViewTestCase):
    def test_response_200(self):
        "If the Entry exists, it returns 200"
        response = views.EncyclopediaView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = views.EncyclopediaView.as_view()(self.request)
        self.assertEqual(response.template_name[0], "category_list.html")

    # Need to finish this
