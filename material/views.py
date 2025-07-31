from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Unit, Material, MaterialCategory
import hashlib
import os

#教材區
def material_list(request):
    units = Unit.objects.prefetch_related('materials').all()
    page_title = '教材區'
    return render(request, 'material/material_list.html', locals())

# 單元詳細頁面
def unit_detail(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)
    all_materials = unit.materials.all()
    
    # 分頁處理
    paginator = Paginator(all_materials, 10)
    page_number = request.GET.get('page')
    materials = paginator.get_page(page_number)
    page_title = f'{unit.title} - 教材列表'
    
    return render(request, 'material/unit_detail.html', locals())

#教材詳細頁面
def material_detail(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    
    # 獲取同單元的其他教材
    related_materials = Material.objects.filter(
        unit=material.unit
    ).exclude(id=material.id).order_by('order')
    
    page_title = material.title
    return render(request, 'material/material_detail.html', locals())

#教材下載功能(限制需要登入)
@login_required
def material_download(request, material_id):
    from django.http import FileResponse, Http404
    import os
    
    material = get_object_or_404(Material, id=material_id)
    
    if not material.pdf_file:
        raise Http404("PDF檔案不存在")
    
    # 取得檔案路徑
    file_path = material.pdf_file.path
    
    if not os.path.exists(file_path):
        raise Http404("PDF檔案不存在")
    
    # 讀取檔案內容
    with open(file_path, 'rb') as pdf_file:
        response = FileResponse(pdf_file.read(), content_type='application/pdf')
        
    # 設定下載檔名
    filename = f"{material.title}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

# 教材搜尋功能
def search_materials(request):
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # Combine search conditions using Q objects
        materials = Material.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query) | Q(unit__title__icontains=query)
        ).distinct().order_by('unit__order', 'order')
        
        # 建立分頁
        paginator = Paginator(materials, 15)
        page_number = request.GET.get('page')
        results = paginator.get_page(page_number)
    
    page_title = f'搜尋結果: {query}' if query else '教材搜尋'
    return render(request, 'material/search_results.html', locals())

# 檢查是否已存在相同內容的PDF檔案
def check_duplicate_pdf(uploaded_file):
    if not uploaded_file:
        return None
    uploaded_file.seek(0)
    uploaded_hasher = hashlib.sha256()
    for chunk in iter(lambda: uploaded_file.read(4096), b""):
        uploaded_hasher.update(chunk)
    uploaded_file.seek(0)
    uploaded_hash = uploaded_hasher.hexdigest()
    all_materials = Material.objects.filter(pdf_file__isnull=False)

    for material in all_materials:
        try:
            if material.pdf_file and os.path.exists(material.pdf_file.path):
                with open(material.pdf_file.path, 'rb') as existing_file:
                    existing_hasher = hashlib.sha256()
                    for chunk in iter(lambda: existing_file.read(4096), b""):
                        existing_hasher.update(chunk)
                    existing_hash = existing_hasher.hexdigest()
                    if uploaded_hash == existing_hash:
                        return material
        except (OSError, IOError):
            continue
    return None

# 管理功能 - 需要管理員權限
@staff_member_required
def manage_materials(request):
    units = Unit.objects.all().order_by('order')
    latest_materials = Material.objects.all().order_by('-created_at')
    total_materials = Material.objects.all() 
    categories = MaterialCategory.objects.all().order_by('name')
    
    page_title = '教材管理'
    return render(request, 'material/manage_materials.html', locals())

# 新增單元
@staff_member_required
def add_unit(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        order = request.POST.get('order')
        
        if title:
            # 如果沒有指定順序，自動設定為最後一個
            if not order:
                last_unit = Unit.objects.order_by('-order').first()
                order = (last_unit.order + 1) if last_unit else 1
            
            # 檢查是否已存在同名單元
            if Unit.objects.filter(title=title).exists():
                messages.error(request, f'單元「{title}」已存在！')
            else:
                unit = Unit.objects.create(
                    title=title,
                    description=description,
                    order=int(order)
                )
                messages.success(request, f'單元「{unit.title}」新增成功！')
                return redirect('ManageMaterials')
        else:
            messages.error(request, '單元標題不能為空！')
    
    # 取得下一個建議的順序
    last_unit = Unit.objects.order_by('-order').first()
    suggested_order = (last_unit.order + 1) if last_unit else 1
    
    page_title = '新增單元'
    return render(request, 'material/add_unit.html', locals())

# 新增教材
@staff_member_required
def add_material(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        unit_id = request.POST.get('unit')
        category_id = request.POST.get('category')
        pdf_file = request.FILES.get('pdf_file')
        order = request.POST.get('order')
        
        if title and unit_id and pdf_file:
            unit = get_object_or_404(Unit, id=unit_id)
            category = MaterialCategory.objects.get(id=category_id) if category_id else None
            
            # 如果沒有指定順序，自動設定為該單元的最後一個
            if not order:
                last_material = Material.objects.filter(unit=unit).order_by('-order').first()
                order = (last_material.order + 1) if last_material else 1
            
            # 檢查是否已存在同名教材
            if Material.objects.filter(title=title, unit=unit).exists():
                messages.error(request, f'教材「{title}」在此單元中已存在！')
            else:
                # 檢查是否已存在相同內容的PDF檔案
                duplicate_material = check_duplicate_pdf(pdf_file)
                
                # 建立新教材
                material = Material.objects.create(
                    title=title,
                    content=content,
                    unit=unit,
                    category=category,
                    order=int(order),
                    pdf_file=pdf_file,
                    creator=request.user
                )
                
                # 根據是否有重複檔案顯示不同的成功訊息
                if duplicate_material:
                    messages.warning(request, 
                        f'教材「{title}」新增成功！但偵測到此PDF檔案與現有教材「{duplicate_material.title}」（{duplicate_material.unit.title}）內容相同。')
                else:
                    messages.success(request, f'教材「{title}」新增成功！')
                
                return redirect('ManageMaterials')
        else:
            if not title:
                messages.error(request, '教材標題不能為空！')
            elif not unit_id:
                messages.error(request, '請選擇所屬單元！')
            elif not pdf_file:
                messages.error(request, '請上傳PDF檔案！')
            else:
                messages.error(request, '教材標題、單元和PDF檔案都是必填項目！')
    
    units = Unit.objects.all().order_by('order')
    categories = MaterialCategory.objects.all().order_by('name')
    page_title = '新增教材'
    return render(request, 'material/add_material.html', locals())

# 新增教材類型
@staff_member_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            # 檢查是否已存在同名類型
            if MaterialCategory.objects.filter(name=name).exists():
                messages.error(request, f'類型「{name}」已存在！')
            else:
                category = MaterialCategory.objects.create(
                    name=name,
                    description=description
                )
                messages.success(request, f'類型「{category.name}」新增成功！')
                return redirect('ManageMaterials')
        else:
            messages.error(request, '類型名稱不能為空！')
    
    page_title = '新增類型'
    return render(request, 'material/add_category.html', locals())

# 刪除教材
@staff_member_required
def delete_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    
    if request.method == 'POST':
        material_title = material.title
        material.delete()
        messages.success(request, f'教材「{material_title}」已成功刪除！')
        return redirect('ManageMaterials')
    
    page_title = f'刪除教材 - {material.title}'
    return render(request, 'material/delete_confirm.html', locals())

# 刪除單元
@staff_member_required  
def delete_unit(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)
    
    if request.method == 'POST':
        unit_title = unit.title
        if unit.materials.exists():
            messages.error(request, f'無法刪除單元「{unit_title}」，因為其下還有教材！請先刪除所有教材。')
        else:
            unit.delete()
            messages.success(request, f'單元「{unit_title}」已成功刪除！')
        return redirect('ManageMaterials')
    
    page_title = f'刪除單元 - {unit.title}'
    return render(request, 'material/delete_confirm.html', locals())

# 刪除教材類型
@staff_member_required
def delete_category(request, category_id):
    category = get_object_or_404(MaterialCategory, id=category_id)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'類型「{category_name}」已成功刪除！')
        return redirect('ManageMaterials')
    
    page_title = f'刪除類型 - {category.name}'
    return render(request, 'material/delete_confirm.html', locals())

# 編輯單元
@staff_member_required
def edit_unit(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        order = request.POST.get('order')
        
        if title:
            # 檢查是否已存在同名單元
            if Unit.objects.filter(title=title).exclude(id=unit.id).exists():
                messages.error(request, f'單元「{title}」已存在！')
            else:
                unit.title = title
                unit.description = description
                if order:
                    unit.order = int(order)
                unit.save()
                messages.success(request, f'單元「{unit.title}」編輯成功！')
                return redirect('ManageMaterials')
        else:
            messages.error(request, '單元標題不能為空！')
    
    page_title = f'編輯單元 - {unit.title}'
    return render(request, 'material/edit_unit.html', locals())

# 編輯教材
@staff_member_required
def edit_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        unit_id = request.POST.get('unit')
        category_id = request.POST.get('category')
        pdf_file = request.FILES.get('pdf_file')
        order = request.POST.get('order')
        
        if title and unit_id:
            unit = get_object_or_404(Unit, id=unit_id)
            category = MaterialCategory.objects.get(id=category_id) if category_id else None

            # 檢查是否已存在同名教材
            if Material.objects.filter(title=title, unit=unit).exclude(id=material.id).exists():
                messages.error(request, f'教材「{title}」在此單元中已存在！')
            else:
                material.title = title
                material.content = content
                material.unit = unit
                material.category = category
                material.order = int(order) if order else material.order
                if pdf_file:
                    if material.pdf_file and os.path.isfile(material.pdf_file.path):
                        os.remove(material.pdf_file.path)
                    material.pdf_file = pdf_file
                material.save()
                messages.success(request, f'教材「{material.title}」編輯成功！')
                return redirect('ManageMaterials')
        else:
            messages.error(request, '教材標題和單元不能為空！')
    
    units = Unit.objects.all().order_by('order')
    categories = MaterialCategory.objects.all().order_by('name')
    page_title = f'編輯教材 - {material.title}'
    return render(request, 'material/edit_material.html', locals())

# 編輯教材類型
@staff_member_required
def edit_category(request, category_id):
    category = get_object_or_404(MaterialCategory, id=category_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            # 檢查是否已存在同名類型
            if MaterialCategory.objects.filter(name=name).exclude(id=category.id).exists():
                messages.error(request, f'類型「{name}」已存在！')
            else:
                category.name = name
                category.description = description
                category.save()
                messages.success(request, f'類型「{category.name}」編輯成功！')
                return redirect('ManageMaterials')
        else:
            messages.error(request, '類型名稱不能為空！')
    
    categories = MaterialCategory.objects.all()
    page_title = f'編輯類型 - {category.name}'
    return render(request, 'material/edit_category.html', locals())


