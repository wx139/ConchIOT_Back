from django.shortcuts import render
from rest_framework.views import APIView
from .models import *
from rest_framework.pagination import PageNumberPagination
from .serializers import *
from rest_framework.response import Response

# Create your views here.

class LogList(APIView):
    # 获取用户下日志列表
    def get(self,request,format="JSON"):
        user=request.user
        try:
            query_params=list(request.query_params.keys())
            kwargs={

            }
            if 'start' in query_params and request.query_params['start'] != '':
                kwargs['addtime__date__gte'] = request.query_params['start']
            if 'end' in query_params and request.query_params['end'] != '':
                kwargs['addtime__date__lte'] = request.query_params['end']
            kwargs['user__id']=user.id
            log_list=Logs.objects.filter(**kwargs).order_by('-addtime')
            page = PageNumberPagination()  # 生成分页器对象
            page.page_size = 2  # 设置每页的条数
            page.page_query_param = 'page'  # url中查询第几页的key默认为'page
            page.page_size_query_param = 'limit'  # url中这一页数据的条数的key, 默认为None
            # page.max_page_size = 5  # 每页的最大数据条数

            page_list = page.paginate_queryset(log_list, request, self) # 生成这一页的数据列表
            # page_list.
            # 将这一页的数据列表序列化
            # return Response(ret.data)  # 返回查到的数据列表
            ret = LogsSerialiser(page_list, many=True)
            jsondata={
            }
            jsondata['code']=20000
            jsondata['total'] = page.page.paginator.count
            jsondata['items']=ret.data
            return Response(jsondata)
        except:
            return Response({
                'code': 0,
                'msg': '日志列表获取失败'
            })