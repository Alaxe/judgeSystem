from django.contrib.contenttypes.models import ContentType

from tags.models import Tag, TagInstance

def tags_by_category():
    tags = {}
    for tag in Tag.objects.all():
        if tag.category in tags:
            tags[tag.category].append(tag)
        else:
            tags[tag.category] = [tag]


    awns = []
    for key in tags:
        awns.append((key, tags[key],))
        
    return awns

def filter_category(objectSet, tags):
    tagInst = TagInstance.objects.filter(tag__in = tags)

    # O( len( tagInst ) )
    objects = { inst.content for inst in tagInst }

    return objects & objectSet

def filter_by_tags(querySet, tags):
    curCatTags = []
    curCategory = ''

    objects = set(querySet)

    for tag in tags:
        if curCategory == tag.category:
            curCatTags.append(tag)
        else:
            if curCatTags:
                objects = filter_category(objects, curCatTags)

            curCatTags = [tag]
            curCategory = tag.category

    if curCatTags:
        objects = filter_category(objects, curCatTags)

    print(objects)

    return list(objects)
