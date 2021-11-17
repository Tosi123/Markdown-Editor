# -*- coding: utf-8 -*-

import os
import re
import shutil
import string
import random
import datetime
import platform
import logging

from django.contrib import messages
from django.conf import settings
from django.shortcuts import redirect, render

from .models import Document, MediaFile, History, Category
from .forms import DocumentForm, DocumentModifyForm, MediaForm, CategoryForm

logger = logging.getLogger(__name__)
DOCUMENT_ROOT = getattr(settings, 'DOCUMENT_ROOT', '.')


def _get_os():
    return {
        'linux': 'linux',
        'darwin': 'mac',
        'windows': 'windows',
    }.get(platform.system().lower(), 'unknown')


# Os Version Check
if _get_os() == 'linux':
    SEPARTOR = "/"
elif _get_os() == 'windows':
    SEPARTOR = "\\"


def _random(length=10):
    string_list = string.ascii_letters + string.digits
    result = ""

    for i in range(length):
        result += random.choice(string_list)
    return result


def _write_file(data):
    try:
        now = datetime.datetime.now()
        date = now.strftime('%Y-%m-%d')
        category_key = data['category']
        # file = re.sub(r' |\(|\)|@|;|\^|\\', '', str(data['title']))
        file_name = "{}-{}.md".format(date, _random(12))

        if category_key.lower() == 'none':
            category_key = ''
            path = DOCUMENT_ROOT + SEPARTOR + file_name
            parent = []
        else:
            category = Category.objects.get(key=category_key)
            if category.parent_key == '':
                path = DOCUMENT_ROOT + SEPARTOR + category.real_path + SEPARTOR + file_name
                parent = [category.title]
            else:
                path = DOCUMENT_ROOT + SEPARTOR + category.parent_path + \
                    SEPARTOR + category.real_path + SEPARTOR + file_name
                parent = [category.title, category.parent_title]

        # Head select
        if len(parent) == 1:
            head = """---
layout: default
title: {}
parent: {}
---\n""".format(data['title'], parent[0])
        elif len(parent) == 2:
            head = """---
layout: default
title: {}
parent: {}
grand_parent: {}
---\n""".format(data['title'], parent[0], parent[1])
        else:
            head = """---
layout: default
title: {}
---\n""".format(data['title'])

        if not os.path.isdir(DOCUMENT_ROOT):
            os.mkdir(DOCUMENT_ROOT)

        if not os.path.isfile(path):
            # File Create
            f = open(path, 'w', encoding="UTF8")
            f.write(head)
            f.write(data['text'].replace('\r', ''))
            f.close()
        else:
            return None
        return {'title': data['title'], 'file_name': file_name, 'category_key': category_key, 'real_path': path, 'writer': data['writer']}
    except Exception as e:
        logger.exception(e)
        return False


def _update_file(data):
    try:
        document = Document.objects.get(key=data['old_key'])

        if data['category'].lower() == 'none':
            new_path = DOCUMENT_ROOT + SEPARTOR + document.file_name
            head = """---
layout: default
title: {}
---\n""".format(data['title'])
        else:
            category = Category.objects.get(key=data['category'])
            if category.parent_key == '':
                new_path = DOCUMENT_ROOT + SEPARTOR + \
                    category.real_path + SEPARTOR + document.file_name
                head = """---
layout: default
title: {}
parent: {}
---\n""".format(data['title'], category.title)
            else:
                new_path = DOCUMENT_ROOT + SEPARTOR + category.parent_path + \
                    SEPARTOR + category.real_path + SEPARTOR + document.file_name
                head = """---
layout: default
title: {}
parent: {}
grand_parent: {}
---\n""".format(data['title'], category.title, category.parent_title)

        if not os.path.isdir(DOCUMENT_ROOT):
            os.mkdir(DOCUMENT_ROOT)

        if document.real_path != new_path:
            shutil.move(document.real_path, new_path)

        # File Create
        f = open(new_path, 'w', encoding="UTF8")
        f.write(head)
        f.write(data['text'].replace('\r', ''))
        f.close()
        return {'title': data['title'], 'file_name': document.file_name, 'real_path': new_path, 'writer': data['writer'], 'key': data['old_key'], 'category_key': data['category']}
    except Exception as e:
        logger.exception(e)
        return False


def _make_dir(data):
    try:
        title = data['title']
        parent_key = data['parent']
        real_path = data['real_path']
        file_name = "category.md"

        if parent_key.lower() == 'none':
            parent_key = ''
            parent_title = ''
            parent_path = ''
            path = DOCUMENT_ROOT + SEPARTOR + real_path
            head = """---
layout: default
title: {}
has_children: true
---""".format(title)
        else:
            category = Category.objects.get(key=parent_key)
            parent_title = category.title
            parent_path = category.real_path
            path = DOCUMENT_ROOT + SEPARTOR + category.real_path + SEPARTOR + real_path
            head = """---
layout: default
title: {}
parent: {}
nav_order: 1
has_children: true
---""".format(title, category.title)

        if not os.path.isdir(path):
            os.mkdir(path)
            # File Create
            f = open(path + SEPARTOR + file_name, 'w', encoding="UTF8")
            f.write(head)
            f.close()
        return {'title': title, 'real_path': real_path, 'parent_key': parent_key, 'parent_title': parent_title, 'parent_path': parent_path}
    except Exception as e:
        logger.exception(e)
        return False


def main(request):
    message = '원하는 만큼 파일을 업로드하세요!'
    form = DocumentForm()
    media_form = MediaForm()
    category_from = CategoryForm()
    categorys = Category.objects.exclude(
        title__isnull=True).order_by('parent_title')
    media = MediaFile.objects.exclude(
        file_name__isnull=True).order_by('-create_dttm')
    documents = Document.objects.exclude(
        file_name__isnull=True).order_by('-create_dttm')
    context = {'documents': documents, 'form': form, 'categorys': categorys,
               'media_form': media_form, 'cat_form': category_from, 'message': message, 'medias': media}
    return render(request, 'main.html', context)


def show(request):
    try:
        key = request.GET.get('key', None)
        if key is not None:
            documents = Document.objects.get(key=key)
            categorys = Category.objects.exclude(
                title__isnull=True).order_by('-parent_title')
            form = DocumentModifyForm()
            with open(documents.real_path, mode="r", encoding="UTF8") as file:
                contents = ""
                cnt = 0

                while True:
                    line = file.readline()
                    if line:
                        if cnt < 2:
                            diff = line.replace(' ', '').replace('\n', '')
                            if re.match(r'^---$', diff):
                                cnt += 1
                            # elif re.match(r'^title:.*$', diff):
                            #     split = line.strip().split(':')
                            #     title = split[1]
                        else:
                            contents += line.replace('\n',
                                                     '\\n').replace('"', '\\"')
                    else:
                        break
                file.close()

        context = {'form': form, 'categorys': categorys,
                   'data': contents, 'documents': documents}
        return render(request, 'modify.html', context)
    except Exception as e:
        logger.exception(e)
        messages.error(request, "System error: {}".format(e))
        return redirect(main)


def category_create(request):
    try:
        if request.method == 'POST':
            result = _make_dir(request.POST)
            if result:
                category = Category(
                    title=result['title'], real_path=result['real_path'], parent_key=result['parent_key'], parent_title=result['parent_title'], parent_path=result['parent_path'])
                category.save()
                messages.info(request, "카테고리 생성 완료")
            else:
                messages.error(request, "카테고리 생성 실패")
        else:
            messages.error(request, "Method POST를 사용해 주세요")
        return redirect(main)
    except Exception as e:
        logger.exception(e)
        messages.error(request, "System error: {}".format(e))
        return redirect(main)


def category_delete(request):
    try:
        if request.method == 'GET':
            key = request.GET.get('key', None)
            if key is not None:
                category = Category.objects.get(key=key)
                if category.parent_key == '':
                    delete_path = DOCUMENT_ROOT + SEPARTOR + category.real_path
                else:
                    delete_path = DOCUMENT_ROOT + SEPARTOR + \
                        category.parent_path + SEPARTOR + category.real_path
                if os.path.isdir(delete_path):
                    os.rmdir(delete_path)
                    messages.info(request, "디렉터리 삭제 완료")
                else:
                    messages.info(request, "디렉터리가 존재하지 않아 삭제하지 않았습니다.")
                category.delete()
                messages.info(request, "DB 데이터 삭제 완료")
            else:
                messages.error(request, "삭제 KEY를 입력해 주세요")
        else:
            messages.error(request, "Method GET을 사용해 주세요")
        return redirect(main)
    except OSError:
        messages.error(request, "매뉴얼 및 하위 카테고리를 삭제 후 진행 바랍니다.")
        return redirect(main)
    except Exception as e:
        logger.exception(e)
        messages.error(request, "System error: {}".format(e))
        return redirect(main)


def document_create(request):
    try:
        if request.method == 'POST':
            result = _write_file(request.POST)
            print(request.POST)
            if result:
                document = Document(title=result['title'],
                                    file_name=result['file_name'], category_key=result['category_key'], real_path=result['real_path'], writer=result['writer'])
                document.save()
                messages.info(request, "게시물 작성 완료")
            elif result == None:
                messages.error(request, "게시물이 이미 등록되어 있습니다.")
            else:
                messages.error(request, "게시물 작성 실패")
        else:
            messages.error(request, "Method POST를 사용해 주세요")
        return redirect(main)
    except Exception as e:
        logger.exception(e)
        messages.error(request, "System error: {}".format(e))
        return redirect(main)


def document_modifiy(request):
    try:
        if request.method == 'POST':
            result = _update_file(request.POST)
            if result:
                document = Document.objects.get(key=result['key'])
                history = History(title=document.title,
                                  file_name=document.file_name, real_path=document.real_path, modifier=document.writer, method='UPDATE', category_key=document.category_key)
                history.save()
                document.title = result['title']
                document.real_path = result['real_path']
                document.modifier = result['writer']
                document.category_key = result['category_key']
                document.save()
                messages.info(request, "게시물 수정 완료")
            else:
                messages.error(request, "게시물 수정 실패")
        else:
            messages.error(request, "Method POST를 사용해 주세요")
        return redirect(main)
    except Exception as e:
        logger.exception(e)
        messages.error(request, "System error: {}".format(e))
        return redirect(main)


def document_delete(request):
    try:
        if request.method == 'GET':
            key = request.GET.get('key', None)
            if key is not None:
                document = Document.objects.get(key=key)
                file_name = document.real_path
                if os.path.isfile(file_name):
                    os.remove(file_name)
                    messages.info(request, "파일 삭제 완료")
                else:
                    messages.info(request, "파일이 존재하지 않아 삭제하지 않았습니다.")
                # 이력 DB에 저장
                history = History(
                    file_name=document.file_name, real_path=document.real_path, modifier='None', method='DELETE')
                history.save()
                # 문서 DB에서 삭제
                document.delete()
                messages.info(request, "DB 데이터 삭제 완료")
            else:
                messages.error(request, "삭제 KEY를 입력해 주세요")
        else:
            messages.error(request, "Method GET을 사용해 주세요")
        return redirect(main)
    except Exception as e:
        logger.exception(e)
        messages.error(request, "System error: {}".format(e))
        return redirect(main)


def media_upload(request):
    try:
        if request.method == 'POST':
            files = request.FILES.getlist('docfile')
            for file in files:
                media = MediaFile(
                    file_name=file, real_path=file, size=file.size, extension=file.content_type)
                media.save()
                messages.info(request, "{} 업로드 성공".format(file))
        else:
            messages.error(request, "Method POST를 사용해 주세요")
        return redirect(main)
    except Exception as e:
        logger.exception(e)
        messages.error(request, "System error: {}".format(e))
        return redirect(main)


def media_delete(request):
    try:
        if request.method == 'GET':
            key = request.GET.get('key', None)
            if key is not None:
                media = MediaFile.objects.get(key=key)
                file_name = media.real_path.path
                if os.path.isfile(file_name):
                    os.remove(file_name)
                    messages.info(request, "파일 삭제 완료")
                else:
                    messages.info(request, "파일이 존재하지 않아 삭제하지 않았습니다.")
                media.delete()
                messages.info(request, "DB 데이터 삭제 완료")
            else:
                messages.error(request, "삭제 KEY를 입력해 주세요")
        else:
            messages.error(request, "Method GET을 사용해 주세요")
        return redirect(main)
    except Exception as e:
        logger.exception(e)
        messages.error(request, "System error: {}".format(e))
        return redirect(main)

