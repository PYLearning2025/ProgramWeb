from django.urls import path
from . import views

urlpatterns = [
    path("", views.material_list, name="MaterialList"),
    path("unit/<int:unit_id>/", views.unit_detail, name="UnitDetail"),
    path("material/<int:material_id>/", views.material_detail, name="MaterialDetail"),
    path("download/<int:material_id>/", views.material_download, name="MaterialDownload"),
    path("search/", views.search_materials, name="SearchMaterials"),
    path("manage/", views.manage_materials, name="ManageMaterials"),
    path("add-unit/", views.add_unit, name="AddUnit"),
    path("add-material/", views.add_material, name="AddMaterial"),
    path("add-category/", views.add_category, name="AddCategory"),
    path("delete-material/<int:material_id>/", views.delete_material, name="DeleteMaterial"),
    path("delete-unit/<int:unit_id>/", views.delete_unit, name="DeleteUnit"),
    path("delete-category/<int:category_id>/", views.delete_category, name="DeleteCategory"),
    path("edit-unit/<int:unit_id>/", views.edit_unit, name="EditUnit"),
    path("edit-material/<int:material_id>/", views.edit_material, name="EditMaterial"),
    path("edit-category/<int:category_id>/", views.edit_category, name="EditCategory"),
]