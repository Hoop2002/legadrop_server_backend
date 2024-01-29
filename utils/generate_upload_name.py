def generate_upload_path(instance, filename):
    model_name = instance._meta.model.__name__.lower()
    return f'{model_name}_{instance.id}/{filename}'
