import dtlpy as dl
import io
import re
from datetime import datetime
from PIL import Image
if dl.token_expired():
    dl.login()
    # Get the project
project = dl.projects.get(project_name='Dataloop Jai')
# Get the dataset
dataset = project.datasets.get(dataset_name='architectural_buildings')

item = dataset.items.get(filepath='/faces.jpg')


# PART 1: Save cropped images
def crop(item):
    filters = dl.Filters(resource=dl.FiltersResource.ANNOTATION)
    filters.add(field='type', values='box')
    pages = dataset.annotations.list(filters=filters)
    remote_path = "/%s" % item.name.split(".")[0]
    for annotation in pages.all():
        print(annotation.left, annotation.top, annotation.right, annotation.bottom)
        buffer = item.download(save_locally=False)
        image = Image.open(buffer)
        cropped_image = image.crop((annotation.left, annotation.top, annotation.right, annotation.bottom))
        cropped_file_name = "%s-%s.%s" % (item.name.split(".")[0], annotation.id, item.name.split(".")[1])
        buf = io.BytesIO()
        cropped_image.save(buf, format='JPEG')
        cropped_image_buffer = buf.getvalue()
        dataset.items.upload(local_path=cropped_image_buffer, remote_path=remote_path, remote_name=cropped_file_name)

crop(item)

# PART 2: Merge cropped images annotations with original image

def merge(item: dl.repositories.Items):
    item_name_without_extension = item.name.split(".")[0]
    annotations = item.annotations.list()
    annotations_dict = {annotation.id: annotation for annotation in annotations}

    filter = dl.Filters()
    filter.add(field='dir', values='/%s' % item_name_without_extension)
    pages = dataset.items.list( filters = filter )
    builder = item.annotations.builder()
    for page in pages:
        for cropped_image in page:
            point_filters = dl.Filters(resource=dl.FiltersResource.ANNOTATION)
            point_filters.add(field='type', values='point')
            point_annotations_pages = cropped_image.annotations.list(filters=point_filters)
            cropped_image_name = cropped_image.name
            annotation_id = re.search("-(.*)\.", cropped_image_name).group(1)
            box_annotation = annotations_dict[annotation_id]
            for point_annotation in point_annotations_pages:
                builder.add(
                    annotation_definition=dl.Point(
                    x=box_annotation.left+point_annotation.x,
                    y=box_annotation.top+point_annotation.y,
                    label=point_annotation.label),
                    parent_id=box_annotation.id
                )

    item.annotations.upload(builder)

merge(item)
