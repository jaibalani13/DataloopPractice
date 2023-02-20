import dtlpy as dl
from datetime import datetime
if dl.token_expired():
    dl.login()
    # Get the project
project = dl.projects.get(project_name='Jai Sandbox')
# Get the dataset
dataset = project.datasets.get(dataset_name='architectural_buildings')

labels = [dl.Label(tag='class1', color=(0, 0, 0)), dl.Label(tag='class2', color=(100, 100, 100)), dl.Label(tag='key', color=(200, 200, 200))]

dataset.add_labels(labels)

# dataset.add_label(label_name='class1', color=(0, 0, 0))

# dataset.add_label(label_name='class2', color=(100, 100, 100))

# dataset.add_label(label_name='key', color=(200, 200, 200))


update_values = {'collected': str(datetime.now())}
pages = dataset.items.update(filters=dl.Filters(), update_values=update_values)
pages = dataset.items.list()

# first_item = items[0]
# first_item.metadata['collected'] = str(datetime.now())
# first_item.update()

index = 0
for item in pages.all():
    builder = item.annotations.builder()
    classification = dl.Classification(label='class1') if index<2 else dl.Classification(label='class2')
    builder.add(annotation_definition=classification)
    item.annotations.upload(builder)
    # adding 5 key point annotations to 1st item
    if index == 0:
        builder2 = item.annotations.builder()
        for j in range(5):
            builder2.add(annotation_definition=dl.Point(x=j*20,y=j*20,label='key'))
        item.annotations.upload(builder2)
    index += 1


filters = dl.Filters()
filters.add_join(field='label', values='class1')
pages = dataset.items.list(filters=filters)
for item in pages.all():
    print("Item name: %s, item id: %s " % (item.name, item.id))


filters = dl.Filters(resource=dl.FiltersResource.ANNOTATION)
filters.add(field='type', values='point')
pages = dataset.annotations.list(filters=filters)
for annotation in pages.all():
    print("Item name: %s, Item id: %s, Annotation id: %s, Annotation label: %s, Annotation point position: (%s, %s)" % (annotation.item.name, annotation.item.id, annotation.id, annotation.label, annotation.x, annotation.y))



# pages = dataset.items.list(filters=filters)
# for item in pages.all():
#     print("Item name: %s, item id: %s " % (item.name, item.id))
#     for annotation in item.annotations.list():
#         print("Annotation id: %s, Annotation label: %s, Annotation point position: (%s, %s)" % (annotation.id, annotation.label, annotation.x, annotation.y))
