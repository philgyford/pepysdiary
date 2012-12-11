from django.views.generic.detail import DetailView

from pepysdiary.encyclopedia.models import Topic


class TopicDetailView(DetailView):
    model = Topic
