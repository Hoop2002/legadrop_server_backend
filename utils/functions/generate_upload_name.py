def generate_upload_name(instance, filename):
    model_name = instance._meta.model.__name__.lower()
    _filename = filename if filename else f"{model_name}_{instance.id}_photo"
    return f"{model_name}_{instance.id}/{_filename}"
