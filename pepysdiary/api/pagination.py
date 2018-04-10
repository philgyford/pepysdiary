from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):

    def get_paginated_response(self, data):
        return Response({
            'pageCount': self.page.paginator.count,
            'nextPageURL': self.get_next_link(),
            'previousPageURL': self.get_previous_link(),
            'results': data
        })
