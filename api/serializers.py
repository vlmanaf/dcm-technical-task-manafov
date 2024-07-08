import os

from django.core.exceptions import SuspiciousFileOperation
from django.core.files.storage import default_storage
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import TestEnvironment, TestFilePath, TestRunRequest


class TestRunRequestSerializer(serializers.ModelSerializer):
    env_name = serializers.ReadOnlyField(source='env.name')

    class Meta:
        model = TestRunRequest
        fields = (
            'id',
            'requested_by',
            'env',
            'path',
            'status',
            'created_at',
            'env_name'
        )
        read_only_fields = (
            'id',
            'created_at',
            'status',
            'logs',
            'env_name'
        )


class TestRunRequestItemSerializer(serializers.ModelSerializer):
    env_name = serializers.ReadOnlyField(source='env.name')

    class Meta:
        model = TestRunRequest
        fields = (
            'id',
            'requested_by',
            'env',
            'path',
            'status',
            'created_at',
            'env_name',
            'logs'
        )


class TestFilePathSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestFilePath
        fields = ('id', 'path')


class TestEnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestEnvironment
        fields = ('id', 'name')


class UploadTestFileSerializer(serializers.ModelSerializer):
    test_file = serializers.FileField(write_only=True)
    upload_dir = serializers.CharField(
        max_length=1024,
        min_length=None,
        allow_blank=True,
        trim_whitespace=False,
        write_only=True,
        validators=[],
    )

    def create(self, validated_data):
        file = validated_data['test_file']
        upload_dir = validated_data['upload_dir']
        path = os.path.join(upload_dir, file.name)
        try:
            default_storage.exists(path)
        except SuspiciousFileOperation:
            raise ValidationError(f'Access denied for destination {path!r}')
        final_path = default_storage.save(path, file)
        test_file_path = TestFilePath.objects.create(path=final_path)
        return test_file_path

    class Meta:
        model = TestFilePath
        fields = ['path', 'test_file', 'upload_dir']
        read_only_fields = ['path']
