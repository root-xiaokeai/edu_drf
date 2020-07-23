from rest_framework.pagination import PageNumberPagination


class CoursePageNumber(PageNumberPagination):
    """课程列表分页器"""
    # 获取第几页的对象
    page_query_param = "page"
    # 指定前端修改每页分页数量的 key
    page_size_query_param = "size"
    # 指定每页分页的数量
    page_size = 2
    # 可以通过此参数指定分页最大数量
    max_page_size = 10