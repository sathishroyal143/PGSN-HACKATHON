"""Admin API for gateway configuration and audit visibility."""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsGatewayAdmin
from .repositories import RateLimitRepository
from .selectors import APIKeySelectors, AuditLogSelectors, RateLimitSelectors
from .serializers import (
    APIKeySerializer,
    AuditLogSerializer,
    CreateAPIKeySerializer,
    RateLimitSerializer,
)
from .services import APIKeyService


class APIKeyListView(APIView):
    permission_classes = [IsGatewayAdmin]

    def get(self, request):
        return Response({
            'data': APIKeySerializer(APIKeySelectors.list(), many=True).data,
        })

    def post(self, request):
        serializer = CreateAPIKeySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        owner_id = data.pop('owner_id', request.user.id)
        api_key, raw_key = APIKeyService.create(owner_id=owner_id, **data)
        response_data = APIKeySerializer(api_key).data
        response_data['key'] = raw_key
        return Response({'data': response_data}, status=status.HTTP_201_CREATED)


class RevokeAPIKeyView(APIView):
    permission_classes = [IsGatewayAdmin]

    def post(self, request, pk):
        api_key = APIKeySelectors.get(pk)
        if not api_key:
            return Response(
                {'error': {'message': 'API key not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        APIKeyService.revoke(api_key)
        return Response({'data': APIKeySerializer(api_key).data})


class RateLimitListView(APIView):
    permission_classes = [IsGatewayAdmin]

    def get(self, request):
        return Response({
            'data': RateLimitSerializer(RateLimitSelectors.list(), many=True).data,
        })

    def post(self, request):
        serializer = RateLimitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        policy = RateLimitRepository.create(
            created_by_id=request.user.id, **serializer.validated_data,
        )
        return Response(
            {'data': RateLimitSerializer(policy).data},
            status=status.HTTP_201_CREATED,
        )


class RateLimitDetailView(APIView):
    permission_classes = [IsGatewayAdmin]

    def patch(self, request, pk):
        policy = RateLimitSelectors.get(pk)
        if not policy:
            return Response(
                {'error': {'message': 'Rate-limit policy not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = RateLimitSerializer(policy, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        policy = RateLimitRepository.update(policy, **serializer.validated_data)
        return Response({'data': RateLimitSerializer(policy).data})


class AuditLogListView(APIView):
    permission_classes = [IsGatewayAdmin]

    def get(self, request):
        logs = AuditLogSelectors.list(
            path=request.query_params.get('path'),
            status_code=request.query_params.get('status_code'),
            method=request.query_params.get('method'),
        )
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', 50)), 200)
        start = (page - 1) * page_size
        total = logs.count()
        return Response({
            'data': AuditLogSerializer(logs[start:start + page_size], many=True).data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': max(1, (total + page_size - 1) // page_size),
            },
        })


class GatewayStatisticsView(APIView):
    permission_classes = [IsGatewayAdmin]

    def get(self, request):
        return Response({'data': AuditLogSelectors.statistics()})
