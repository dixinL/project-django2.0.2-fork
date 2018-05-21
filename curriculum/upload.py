from django.shortcuts import render, redirect
from .forms import AddCurriculumForm, AddSeriesForm
from .models import Series
from django.contrib.auth.decorators import permission_required
import os
# Create your views here.


UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'upload_dir')


# 分块写入文件 return 文件存储的位置
def handle_uploaded_file(f, file_name, series):
    path = os.path.join(UPLOAD_DIR, series)
    if not os.path.exists(path):  # 判断是否存在文件或目录path
        os.makedirs(path)
    with open(os.path.join(path, file_name), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    print(path)
    return path


# 检测用户是否有上传文件的权限，如果没有返回主页
@permission_required('curriculum.upload_file', login_url='/')
# 往系列添加视频界面
def add_curriculum_view(request, series):
    series = Series.objects.get(pk=series)
    if series.owner != request.user:
        return redirect('my_series_list')
    if request.method == 'POST':
        form = AddCurriculumForm(request.POST, request.FILES)
        if form.is_valid():
            new_curriculum = form.save(commit=False)
            new_curriculum.owner = request.user
            new_curriculum.series = series
            new_curriculum.path = handle_uploaded_file(request.FILES['post_file'],
                                                       file_name=form.cleaned_data['name'],
                                                       series=series.name)
            if request.FILES['post_attachment'] != "" or request.FILES['post_attachment'] is not None:
                new_curriculum.attachment = handle_uploaded_file(
                    request.FILES['post_attachment'],
                    file_name=form.cleaned_data['name']+"-attachment",
                    series=series.name)
            new_curriculum.save()
            print("saved!")
            return redirect('my_series',series.id)
        print(form)
        return redirect('add_curriculum',series.id)
    else:
        form = AddCurriculumForm()

    return render(request, 'curriculum/add_curriculum.html', {'form': form, 'series': series})


# 添加系列课程
@permission_required('curriculum.upload_file',login_url='/')
def add_series_view(request):
    if request.method == 'POST':
        form = AddSeriesForm(request.POST)
        if form.is_valid():
            new_series = form.save(commit=False)
            new_series.owner = request.user
            new_series.save()
            return redirect('my_series', new_series.id)
        return redirect('my_series_list')
    else:
        form = AddSeriesForm()
    return render(request, 'curriculum/add_series.html', {'form': form})
