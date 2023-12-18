from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from blog.models import Post
from .permissions import IsAuthorOrReadOnly
from .serializers import PostSerializer
from rest_framework import filters


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['author']
    search_fields = ['body', 'author__username']
    ordering_fields = ['author_id', 'publish']
    def get(self, request, format=None):
        transformers = Post.objects.all()
        serializer = PostSerializer(transformers, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    # def get_queryset(self):
    #     user = self.request.user
    #     return Post.objects.filter(author=user)
    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        transformer = self.get_object(pk)
        serializer = PostSerializer(transformer)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        transformer = self.get_object(pk)
        serializer = PostSerializer(transformer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        transformer = self.get_object(pk)
        serializer = PostSerializer(transformer,
                                    data=request.data,
                                    partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        transformer = self.get_object(pk)
        transformer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserPostList(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.kwargs['username']
        return Post.objects.filter(author=user)
