import uuid


def generate_upload_name(instance, filename):
    model_name = instance._meta.model.__name__.lower()
    _filename = filename if filename else f"{model_name}_{uuid.uuid4()}"
    return f"{model_name}/{_filename}"
