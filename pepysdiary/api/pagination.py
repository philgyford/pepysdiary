from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):

    def get_paginated_response(self, data):
        return Response({
            'totalResults': self.page.paginator.count,
            'totalPages': self.page.paginator.num_pages,
            'nextPageURL': self.get_next_link(),
            'previousPageURL': self.get_previous_link(),
            'results': data
        })
