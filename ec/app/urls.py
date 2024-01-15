from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_view
from . import views

urlpatterns = [
    path('', views.home, name='Homepage'),

#suppliers
    path('suppliers/', views.list_suppliers, name='SuppliersList'),
    path('suppliers/add', views.create_supplier, name='AddSupplier'),
    path('suppliers/edit/<int:id>', views.edit_supplier, name='EditSupplier'),
    path('suppliers/delete/<int:id>', views.delete_supplier, name='DeleteSupplier'),
    #warehouses
        path('warehouses/', views.list_warehouses, name='WarehousesList'),
        path('warehouses/add', views.create_warehouse, name='AddWarehouse'),
        path('warehouses/edit/<int:id>', views.edit_warehouse, name='EditWarehouse'),
        path('warehouses/delete/<int:id>', views.delete_warehouse, name='DeleteWarehouse'),

#components
    path('components/', views.list_components, name='ComponentsList'),
    path('components/add', views.create_component, name='AddComponent'),
    path('components/edit/<int:id>', views.edit_component, name='EditComponent'),
    path('components/delete/<int:id>', views.delete_component, name='DeleteComponent'),
    path('components/detail/<str:name>/<int:component_type_id>', views.components_detail, name='ComponentsDetail'),
    #component types
        path('component-types/', views.list_component_types, name='ComponentTypesList'),
        path('component-types/add', views.create_component_type, name='AddComponentType'),
        path('component-types/edit/<int:id>', views.edit_component_type, name='EditComponentType'),
        path('component-types/delete/<int:id>', views.delete_component_type, name='DeleteComponentType'),

#equipments
    path('equipments/', views.list_equipments, name='EquipmentsList'),
    path('equipments/add', views.create_equipment, name='AddEquipment'),
    path('equipments/edit/<int:id>', views.edit_equipment, name='EditEquipment'),
    path('equipments/edit-production/<int:id>', views.edit_production, name='EditProduction'),
    path('equipments/delete/<int:id>', views.delete_equipment, name='DeleteEquipment'),
    #equipment types
        path('equipment-types/', views.list_equipment_types, name='EquipmentTypesList'),
        path('equipment-types/add', views.create_equipment_type, name='AddEquipmentType'),
        path('equipment-types/edit/<int:id>', views.edit_equipment_type, name='EditEquipmentType'),
        path('equipment-types/delete/<int:id>', views.delete_equipment_type, name='DeleteEquipmentType'),

#Guides
    path('guides/', views.list_shipping_guides, name='ListShippingGuides'),
    path('guides/edit-guide/<int:id>', views.edit_shipping_guide, name='EditShippingGuides'),

#Orders
    path('order-equipment/<int:id>', views.order_equipment, name='OrderEquipment'),

#JSON importations and exportations
    path('export-to-json/', views.export_to_json, name='ExportToJSON'),
    path('import-from-json/', views.import_from_json, name='ImportFromJSON'),

    #authentication
    path('signup/', views.signup, name='Signup'),
    path('login/', views.login_view, name='Login'),
    path('logout/', views.logout_view, name='Logout'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)