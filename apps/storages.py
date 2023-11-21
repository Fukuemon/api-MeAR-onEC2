from storages.backends.s3boto3 import S3Boto3Storage

class CustomS3Boto3Storage(S3Boto3Storage):
    def _save(self, name, content):
        if name.startswith('models/') and name.endswith('.glb'):
            content.content_type = 'model/gltf-binary'
        return super()._save(name, content)
